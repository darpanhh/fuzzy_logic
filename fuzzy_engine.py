"""
fuzzy_engine.py
---------------
All fuzzy-logic computation lives here.
No Streamlit, no matplotlib — pure data in, pure data out.

Public API
----------
build_system()          -> FuzzySystem (call once, cache the result)
run_inference(sys, t, h) -> InferenceResult
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Dict

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


# ── Universe of discourse ────────────────────────────────────────────────────
T_UNIVERSE = np.arange(0, 41, 1)    # Temperature: 0–40 °C
H_UNIVERSE = np.arange(0, 101, 1)   # Humidity:    0–100 %
F_UNIVERSE = np.arange(0, 101, 1)   # Fan speed:   0–100 %

# ── Membership-function parameters (triangular) ──────────────────────────────
TEMP_MF_PARAMS = {
    "cold": [0,  0,  20],
    "warm": [0,  20, 40],
    "hot":  [20, 40, 40],
}

HUM_MF_PARAMS = {
    "low":    [0,   0,   50],
    "medium": [0,   50,  100],
    "high":   [50,  100, 100],
}

FAN_MF_PARAMS = {
    "slow":   [0,   0,   50],
    "medium": [0,   50,  100],
    "fast":   [50,  100, 100],
}

# ── Rule table (human-readable) ───────────────────────────────────────────────
# Each tuple: (Temperature term, Humidity term, Fan-speed consequent)
RULE_META: List[Tuple[str, str, str]] = [
    ("Cold", "Low",    "Slow"),
    ("Cold", "Medium", "Slow"),
    ("Cold", "High",   "Medium"),
    ("Warm", "Low",    "Slow"),
    ("Warm", "Medium", "Medium"),
    ("Warm", "High",   "Fast"),
    ("Hot",  "Low",    "Medium"),
    ("Hot",  "Medium", "Fast"),
    ("Hot",  "High",   "Fast"),
]


# ── Data containers ──────────────────────────────────────────────────────────

@dataclass
class FuzzySystem:
    """Holds the built skfuzzy control system and pre-computed MF arrays."""
    ctrl_system: ctrl.ControlSystem
    # Pre-computed MF arrays (numpy) keyed by term name
    temp_mfs: Dict[str, np.ndarray]
    hum_mfs:  Dict[str, np.ndarray]
    fan_mfs:  Dict[str, np.ndarray]


@dataclass
class InferenceResult:
    """Everything produced by one forward pass of the FIS."""
    # crisp inputs
    temperature: float
    humidity: float

    # fuzzified membership degrees
    temp_degrees: Dict[str, float]   # {"cold": 0.0, "warm": 0.5, "hot": 0.5}
    hum_degrees:  Dict[str, float]   # {"low": 0.0, "medium": 0.8, "high": 0.2}

    # rule firing strengths (list aligned to RULE_META)
    rule_strengths: List[float]

    # output MF arrays after implication (clipping)
    # keyed by fan-speed term
    clipped_mfs: Dict[str, np.ndarray]

    # aggregated output (pointwise max of all clipped mfs)
    aggregate: np.ndarray

    # crisp output after centroid defuzzification
    fan_speed: float


# ── Factory & inference ──────────────────────────────────────────────────────

def build_system() -> FuzzySystem:
    """
    Construct and wire the Mamdani FIS.
    Call once and cache the returned FuzzySystem object (e.g. with
    @st.cache_resource in Streamlit or simply as a module-level singleton).
    """
    temp = ctrl.Antecedent(T_UNIVERSE, "temperature")
    hum  = ctrl.Antecedent(H_UNIVERSE, "humidity")
    fan  = ctrl.Consequent(F_UNIVERSE, "fan_speed")

    for term, params in TEMP_MF_PARAMS.items():
        temp[term] = fuzz.trimf(T_UNIVERSE, params)
    for term, params in HUM_MF_PARAMS.items():
        hum[term] = fuzz.trimf(H_UNIVERSE, params)
    for term, params in FAN_MF_PARAMS.items():
        fan[term] = fuzz.trimf(F_UNIVERSE, params)

    rules = [
        ctrl.Rule(temp["cold"] & hum["low"],    fan["slow"]),
        ctrl.Rule(temp["cold"] & hum["medium"], fan["slow"]),
        ctrl.Rule(temp["cold"] & hum["high"],   fan["medium"]),
        ctrl.Rule(temp["warm"] & hum["low"],    fan["slow"]),
        ctrl.Rule(temp["warm"] & hum["medium"], fan["medium"]),
        ctrl.Rule(temp["warm"] & hum["high"],   fan["fast"]),
        ctrl.Rule(temp["hot"]  & hum["low"],    fan["medium"]),
        ctrl.Rule(temp["hot"]  & hum["medium"], fan["fast"]),
        ctrl.Rule(temp["hot"]  & hum["high"],   fan["fast"]),
    ]

    system = ctrl.ControlSystem(rules)

    # Pre-compute MF numpy arrays once (reused in every chart)
    temp_mfs = {t: fuzz.trimf(T_UNIVERSE, p) for t, p in TEMP_MF_PARAMS.items()}
    hum_mfs  = {t: fuzz.trimf(H_UNIVERSE, p) for t, p in HUM_MF_PARAMS.items()}
    fan_mfs  = {t: fuzz.trimf(F_UNIVERSE, p) for t, p in FAN_MF_PARAMS.items()}

    return FuzzySystem(
        ctrl_system=system,
        temp_mfs=temp_mfs,
        hum_mfs=hum_mfs,
        fan_mfs=fan_mfs,
    )


def run_inference(system: FuzzySystem, temperature: float, humidity: float) -> InferenceResult:
    """
    Run one forward pass of the Mamdani FIS for the given crisp inputs.

    Parameters
    ----------
    system      : FuzzySystem returned by build_system()
    temperature : crisp temperature value in [0, 40]
    humidity    : crisp humidity value    in [0, 100]

    Returns
    -------
    InferenceResult with every intermediate quantity needed for visualisation.
    """
    # ── Step 1: skfuzzy computation (handles defuzzification) ──
    sim = ctrl.ControlSystemSimulation(system.ctrl_system)
    sim.input["temperature"] = temperature
    sim.input["humidity"]    = humidity
    sim.compute()
    fan_speed = sim.output["fan_speed"]

    # ── Step 2: fuzzification ──
    temp_degrees = {
        term: float(fuzz.interp_membership(T_UNIVERSE, mf_arr, temperature))
        for term, mf_arr in system.temp_mfs.items()
    }
    hum_degrees = {
        term: float(fuzz.interp_membership(H_UNIVERSE, mf_arr, humidity))
        for term, mf_arr in system.hum_mfs.items()
    }

    # ── Step 3: rule evaluation (AND = min) ──
    rule_strengths = []
    for t_lbl, h_lbl, _ in RULE_META:
        alpha = min(
            temp_degrees[t_lbl.lower()],
            hum_degrees[h_lbl.lower()],
        )
        rule_strengths.append(alpha)

    # ── Step 4: implication (clip each consequent MF at its rule strength) ──
    clipped_mfs: Dict[str, np.ndarray] = {
        term: np.zeros_like(F_UNIVERSE, dtype=float)
        for term in system.fan_mfs
    }
    for idx, (_, _, f_lbl) in enumerate(RULE_META):
        alpha   = rule_strengths[idx]
        f_key   = f_lbl.lower()
        clipped = np.fmin(alpha, system.fan_mfs[f_key])
        clipped_mfs[f_key] = np.fmax(clipped_mfs[f_key], clipped)

    # ── Step 5: aggregation (OR = max across all terms) ──
    aggregate = np.zeros_like(F_UNIVERSE, dtype=float)
    for arr in clipped_mfs.values():
        aggregate = np.fmax(aggregate, arr)

    return InferenceResult(
        temperature=temperature,
        humidity=humidity,
        temp_degrees=temp_degrees,
        hum_degrees=hum_degrees,
        rule_strengths=rule_strengths,
        clipped_mfs=clipped_mfs,
        aggregate=aggregate,
        fan_speed=fan_speed,
    )
