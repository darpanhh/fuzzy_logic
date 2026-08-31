"""
charts.py
---------
All matplotlib figure-building functions.
Imports from theme.py for colours; imports from fuzzy_engine.py for
type hints.  No Streamlit calls — just returns Figure objects.
"""

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

import theme
from fuzzy_engine import (
    F_UNIVERSE, T_UNIVERSE, H_UNIVERSE,
    RULE_META, FuzzySystem, InferenceResult,
)

matplotlib.use("Agg")


# ── Figure factory ────────────────────────────────────────────────────────────

def _base_fig(w: float = 8, h: float = 3.2):
    """Return a (fig, ax) pair with the standard light chart style."""
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor(theme.CHART_FIG_BG)
    ax.set_facecolor(theme.CHART_AXES_BG)
    ax.tick_params(colors=theme.CHART_TICK, labelsize=9)
    for spine in ax.spines.values():
        spine.set_color(theme.CHART_SPINE)
        spine.set_linewidth(0.8)
    ax.grid(True, color=theme.CHART_GRID, linewidth=0.5)
    return fig, ax


def _style_ax(ax, title: str, xlabel: str, ylabel: str = "μ"):
    ax.set_title(title, fontsize=10, fontweight="600",
                 color=theme.CHART_TITLE, pad=8)
    ax.set_xlabel(xlabel, fontsize=8, color=theme.CHART_LABEL)
    ax.set_ylabel(ylabel, fontsize=9, color=theme.CHART_LABEL)


# ── Step 1 — Membership functions ────────────────────────────────────────────

def plot_membership_functions(system: FuzzySystem, input_temp: float, input_hum: float):
    """
    Returns three figures: temperature MFs, humidity MFs, fan-speed MFs.
    A dashed vertical line marks the current crisp input on the input charts.
    """
    def _mf_fig(univ, mf_dict, colors, title, xlabel, input_val=None):
        fig, ax = _base_fig(5, 3)
        for term, arr in mf_dict.items():
            color = colors[term]
            ax.plot(univ, arr, color=color, lw=2, label=term.title())
            ax.fill_between(univ, arr, alpha=0.07, color=color)
        if input_val is not None:
            ax.axvline(input_val, color=theme.CHART_INPUT,
                       lw=1.4, ls="--", alpha=0.5)
        ax.set_ylim(-0.04, 1.1)
        ax.legend(fontsize=8, framealpha=0.9, edgecolor=theme.CHART_SPINE)
        _style_ax(ax, title, xlabel)
        fig.tight_layout()
        return fig

    fig_t = _mf_fig(T_UNIVERSE, system.temp_mfs, theme.TEMP_COLORS,
                    "Temperature", "°C", input_temp)
    fig_h = _mf_fig(H_UNIVERSE, system.hum_mfs,  theme.HUM_COLORS,
                    "Humidity", "%", input_hum)

    # Fan-speed colour map uses the FAN_COLORS keys
    fan_colors_mapped = {
        "slow":   theme.FAN_COLORS["slow"],
        "medium": theme.FAN_COLORS["medium_f"],
        "fast":   theme.FAN_COLORS["fast"],
    }
    fig_f = _mf_fig(F_UNIVERSE, system.fan_mfs, fan_colors_mapped,
                    "Fan Speed (output)", "%")
    return fig_t, fig_h, fig_f


# ── Step 2 — Fuzzification ───────────────────────────────────────────────────

def plot_fuzzification(result: InferenceResult, system: FuzzySystem):
    """
    Returns two figures (temperature, humidity) showing the membership
    degrees at the crisp input values, with dotted projection lines.
    """
    def _fuzz_fig(univ, mf_dict, degrees, colors, input_val, title, xlabel):
        fig, ax = _base_fig(6, 3.4)
        for term, arr in mf_dict.items():
            mu    = degrees[term]
            color = colors[term]
            ax.plot(univ, arr, color=color, lw=2,
                    label=f"{term.title()}  μ = {mu:.3f}")
            if mu > 0:
                ax.hlines(mu, 0, input_val,
                          colors=color, linestyles="dotted", lw=1.2, alpha=0.7)
                ax.plot(input_val, mu, "o", color=color, markersize=7, zorder=5)
        ax.axvline(input_val, color=theme.CHART_INPUT,
                   lw=1.4, ls="--", alpha=0.5, label=f"Input = {input_val}")
        ax.set_ylim(-0.04, 1.12)
        ax.legend(fontsize=8, framealpha=0.9, edgecolor=theme.CHART_SPINE)
        _style_ax(ax, title, xlabel)
        fig.tight_layout()
        return fig

    fig_t = _fuzz_fig(
        T_UNIVERSE, system.temp_mfs, result.temp_degrees,
        theme.TEMP_COLORS, result.temperature,
        "Temperature Fuzzification", "°C",
    )
    fig_h = _fuzz_fig(
        H_UNIVERSE, system.hum_mfs, result.hum_degrees,
        theme.HUM_COLORS, result.humidity,
        "Humidity Fuzzification", "%",
    )
    return fig_t, fig_h


# ── Step 3 — Rule evaluation table ───────────────────────────────────────────

def plot_rule_table(result: InferenceResult):
    """
    Returns a matplotlib figure rendering the 9-rule evaluation table
    with coloured term badges and a firing-strength progress bar.
    (Rendered in matplotlib so Streamlit HTML sanitisation is irrelevant.)
    """
    fig, ax = plt.subplots(figsize=(13, 4.2))
    fig.patch.set_facecolor(theme.CHART_FIG_BG)
    ax.set_facecolor(theme.CHART_FIG_BG)
    ax.axis("off")

    COL_X    = [0.03, 0.12, 0.26, 0.40, 0.54, 0.64, 0.94]
    HDRS     = ["Rule", "Temperature", "Humidity", "Fan Speed",
                "Strength", "Firing bar", "Active"]
    ROW_H    = 0.90
    HEADER_Y = 9.2

    # Header row
    ax.add_patch(mpatches.FancyBboxPatch(
        (0, HEADER_Y - 0.40), 1.0, 0.58,
        boxstyle="square,pad=0", linewidth=0,
        facecolor=theme.TABLE_HEADER_BG,
    ))
    for cx, hdr in zip(COL_X, HDRS):
        ax.text(cx, HEADER_Y, hdr, ha="left", va="center",
                color=theme.TABLE_HEADER_TEXT,
                fontsize=8.5, fontweight="bold", fontfamily="monospace")

    for i, (t_lbl, h_lbl, f_lbl) in enumerate(RULE_META):
        s     = result.rule_strengths[i]
        row_y = HEADER_Y - (i + 1) * ROW_H
        bg    = theme.TABLE_ROW_ODD if i % 2 == 0 else theme.TABLE_ROW_EVEN

        ax.add_patch(mpatches.FancyBboxPatch(
            (0, row_y - 0.38), 1.0, 0.72,
            boxstyle="square,pad=0", linewidth=0, facecolor=bg,
        ))
        ax.axhline(row_y - 0.38, color=theme.TABLE_SEP, lw=0.5, zorder=5)

        dim = theme.TABLE_INACTIVE
        lit = "#1a1f2e"

        # Rule number
        ax.text(COL_X[0], row_y, f"R{i+1}", ha="left", va="center",
                color=lit if s > 0 else dim,
                fontsize=9, fontweight="600", fontfamily="monospace")

        # Temperature badge
        tc = theme.RULE_TEMP_COLORS[t_lbl]
        ax.add_patch(mpatches.FancyBboxPatch(
            (COL_X[1], row_y - 0.20), 0.10, 0.38,
            boxstyle="round,pad=0.01", linewidth=1,
            edgecolor=tc, facecolor=tc + "18", zorder=3,
        ))
        ax.text(COL_X[1] + 0.050, row_y, t_lbl, ha="center", va="center",
                color=tc, fontsize=8, fontweight="600")

        # Humidity badge
        hc = theme.RULE_HUM_COLORS[h_lbl]
        ax.add_patch(mpatches.FancyBboxPatch(
            (COL_X[2], row_y - 0.20), 0.11, 0.38,
            boxstyle="round,pad=0.01", linewidth=1,
            edgecolor=hc, facecolor=hc + "18", zorder=3,
        ))
        ax.text(COL_X[2] + 0.055, row_y, h_lbl, ha="center", va="center",
                color=hc, fontsize=8, fontweight="600")

        # Fan Speed badge
        fc = theme.RULE_FAN_COLORS[f_lbl]
        ax.add_patch(mpatches.FancyBboxPatch(
            (COL_X[3], row_y - 0.20), 0.10, 0.38,
            boxstyle="round,pad=0.01", linewidth=1,
            edgecolor=fc, facecolor=fc + "18", zorder=3,
        ))
        ax.text(COL_X[3] + 0.050, row_y, f_lbl, ha="center", va="center",
                color=fc, fontsize=8, fontweight="600")

        # Strength value
        ax.text(COL_X[4], row_y, f"{s:.3f}", ha="left", va="center",
                color=theme.TABLE_STRENGTH_CLR if s > 0 else dim,
                fontsize=9, fontweight="600", fontfamily="monospace")

        # Progress bar (track + fill)
        bx, bw, bh = COL_X[5], 0.28, 0.22
        ax.add_patch(mpatches.FancyBboxPatch(
            (bx, row_y - bh / 2), bw, bh,
            boxstyle="round,pad=0.003", linewidth=0.8,
            edgecolor=theme.TABLE_BAR_TRACK_BORDER,
            facecolor=theme.TABLE_BAR_TRACK, zorder=3,
        ))
        if s > 0:
            ax.add_patch(mpatches.FancyBboxPatch(
                (bx, row_y - bh / 2), bw * s, bh,
                boxstyle="round,pad=0.003", linewidth=0,
                facecolor=theme.TABLE_BAR_FILL, zorder=4,
            ))

        # Active indicator
        if s > 0:
            ax.text(COL_X[6], row_y, "✓", ha="center", va="center",
                    color=theme.TABLE_ACTIVE_CLR, fontsize=12, fontweight="bold")
        else:
            ax.text(COL_X[6], row_y, "—", ha="center", va="center",
                    color=dim, fontsize=10)

    ax.set_xlim(0, 1)
    ax.set_ylim(HEADER_Y - 9 * ROW_H - 0.5, HEADER_Y + 0.5)
    fig.tight_layout(pad=0.3)
    return fig


# ── Step 4 — Implication (individual clipped MFs) ────────────────────────────

def plot_implication(result: InferenceResult, system: FuzzySystem):
    """
    Returns one small figure per active rule showing the clipped output MF.
    """
    fan_colors = {
        "slow":   theme.FAN_COLORS["slow"],
        "medium": theme.FAN_COLORS["medium_f"],
        "fast":   theme.FAN_COLORS["fast"],
    }

    figures = []
    for idx, (t_lbl, h_lbl, f_lbl) in enumerate(RULE_META):
        alpha = result.rule_strengths[idx]
        if alpha == 0:
            continue

        f_key  = f_lbl.lower()
        color  = fan_colors[f_key]
        base   = system.fan_mfs[f_key]
        clipped = np.fmin(alpha, base)

        fig, ax = _base_fig(3.5, 2.8)
        ax.plot(F_UNIVERSE, base, color=color, lw=1.5, ls="--", alpha=0.35)
        ax.fill_between(F_UNIVERSE, clipped, alpha=0.30, color=color)
        ax.plot(F_UNIVERSE, clipped, color=color, lw=2)
        ax.axhline(alpha, color="#777", lw=0.9, ls=":", alpha=0.7)
        ax.text(2, alpha + 0.03, f"α={alpha:.3f}", fontsize=7.5, color="#555")
        ax.set_ylim(-0.04, 1.1)
        _style_ax(ax, f"R{idx+1}: {t_lbl} ∧ {h_lbl} → {f_lbl}",
                  "Fan Speed %")
        fig.tight_layout()
        figures.append((idx, t_lbl, h_lbl, f_lbl, fig))

    return figures


# ── Step 5 — Aggregation ─────────────────────────────────────────────────────

def plot_aggregation(result: InferenceResult):
    """
    Returns a single figure of the aggregated output fuzzy set
    with individual term contributions shown as dashed fills.
    """
    fan_colors = {
        "slow":   theme.FAN_COLORS["slow"],
        "medium": theme.FAN_COLORS["medium_f"],
        "fast":   theme.FAN_COLORS["fast"],
    }

    fig, ax = _base_fig(10, 3.6)
    for term, arr in result.clipped_mfs.items():
        if np.max(arr) > 0:
            color = fan_colors[term]
            ax.fill_between(F_UNIVERSE, arr, alpha=0.18, color=color)
            ax.plot(F_UNIVERSE, arr, color=color, lw=1.2, ls="--",
                    alpha=0.5, label=f"{term.title()} (clipped)")

    ax.fill_between(F_UNIVERSE, result.aggregate, alpha=0.25, color=theme.AGG_COLOR)
    ax.plot(F_UNIVERSE, result.aggregate, color=theme.AGG_COLOR,
            lw=2.2, label="Aggregate (max)")
    ax.legend(fontsize=8.5, framealpha=0.9, edgecolor=theme.CHART_SPINE)
    _style_ax(ax, "Aggregated Output Fuzzy Set", "Fan Speed %")
    fig.tight_layout()
    return fig


# ── Step 6 — Defuzzification ─────────────────────────────────────────────────

def plot_defuzzification(result: InferenceResult):
    """
    Returns a figure showing the aggregate set with the centroid marked.
    """
    fig, ax = _base_fig(10, 3.8)
    agg = result.aggregate
    cv  = result.fan_speed

    ax.fill_between(F_UNIVERSE, agg, alpha=0.20, color=theme.AGG_COLOR)
    ax.plot(F_UNIVERSE, agg, color=theme.AGG_COLOR, lw=2.2, label="Aggregate set")
    ax.fill_between(F_UNIVERSE, agg, where=(F_UNIVERSE <= cv),
                    alpha=0.18, color=theme.CENTROID_FILL, label="Left of centroid")
    ax.axvline(cv, color=theme.CENTROID_COLOR, lw=2,
               label=f"Centroid = {cv:.2f}%")
    ax.plot(cv, 0, marker="^", color=theme.CENTROID_COLOR,
            markersize=11, zorder=6)
    ax.legend(fontsize=8.5, framealpha=0.9, edgecolor=theme.CHART_SPINE)
    _style_ax(ax, "Defuzzification — Centroid Method", "Fan Speed %")
    fig.tight_layout()
    return fig
