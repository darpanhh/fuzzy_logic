"""
app.py
------
Streamlit entry point.  This file only:
  • configures the page
  • renders the sidebar
  • calls fuzzy_engine.run_inference()
  • calls charts.*() to get figures
  • renders those figures with st.pyplot()

No business logic, no colours, no matplotlib construction here.
"""

import streamlit as st
import matplotlib.pyplot as plt

import theme
import charts
from fuzzy_engine import build_system, run_inference, RULE_META


# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="Fan Speed — Fuzzy Logic",
    page_icon="🌀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject CSS from theme ─────────────────────────────────────────────────────
st.markdown(theme.STREAMLIT_CSS, unsafe_allow_html=True)


# ── Build (and cache) the fuzzy system ───────────────────────────────────────
@st.cache_resource
def get_system():
    return build_system()

system = get_system()


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Fan Speed Controller")
    st.caption("Mamdani Fuzzy Inference System")
    st.divider()

    input_temp = st.slider("Temperature (°C)", 0, 40, 25)
    input_hum  = st.slider("Humidity (%)",     0, 100, 60)
    st.divider()
    run = st.button("Run inference →", type="primary", use_container_width=True)
    st.divider()
    st.caption(
        "**About**  \nThis tool steps through the full Mamdani "
        "fuzzy pipeline: fuzzification → rule evaluation → "
        "implication → aggregation → defuzzification."
    )


# ── Main area — header ────────────────────────────────────────────────────────
st.markdown("## 🌀 Automatic Fan Speed Control")
st.markdown(
    "Inputs: **Temperature** (0–40 °C) and **Humidity** (0–100 %).  "
    "Output: **Fan Speed** (0–100 %).  "
    "Mamdani FIS — AND = min, OR = max, defuzzification = centroid."
)
st.divider()

if not (run or st.session_state.get("ran")):
    st.info("Set the inputs in the sidebar and click **Run inference →**.")
    st.stop()

st.session_state["ran"] = True


# ── Run inference ─────────────────────────────────────────────────────────────
result = run_inference(system, input_temp, input_hum)


# ── Result summary ────────────────────────────────────────────────────────────
col_inp, col_res = st.columns([2, 1])
with col_inp:
    st.markdown("**Inputs**")
    c1, c2 = st.columns(2)
    c1.metric("Temperature", f"{input_temp} °C")
    c2.metric("Humidity",    f"{input_hum} %")

with col_res:
    st.markdown(f"""
    <div class="result-box">
        <div style="font-size:0.78rem; color:#8a9bb8; margin-bottom:6px; letter-spacing:0.05em;">FAN SPEED</div>
        <div class="result-number">{result.fan_speed:.1f}%</div>
        <div class="result-sub">centroid defuzzification</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()


# ── STEP 1 — Membership functions ────────────────────────────────────────────
st.markdown("""
<div class="card">
  <div class="step-label">STEP 1</div>
  <div class="card-title">Membership Functions</div>
  <div class="card-desc">
    Each input and output variable is partitioned into three triangular fuzzy sets.
    These define how crisp values map to linguistic terms.
    The dashed line marks the current input.
  </div>
</div>
""", unsafe_allow_html=True)

fig_t, fig_h, fig_f = charts.plot_membership_functions(system, input_temp, input_hum)
col1, col2, col3 = st.columns(3)
with col1:
    st.pyplot(fig_t, use_container_width=True); plt.close(fig_t)
with col2:
    st.pyplot(fig_h, use_container_width=True); plt.close(fig_h)
with col3:
    st.pyplot(fig_f, use_container_width=True); plt.close(fig_f)


# ── STEP 2 — Fuzzification ───────────────────────────────────────────────────
st.markdown("""
<div class="card">
  <div class="step-label">STEP 2</div>
  <div class="card-title">Fuzzification</div>
  <div class="card-desc">
    Read off the membership degree of each input value in every linguistic term.
    Dotted projection lines show the evaluated μ at the input.
  </div>
</div>
""", unsafe_allow_html=True)

fig_ft, fig_fh = charts.plot_fuzzification(result, system)
fc1, fc2 = st.columns(2)
with fc1:
    st.pyplot(fig_ft, use_container_width=True); plt.close(fig_ft)
with fc2:
    st.pyplot(fig_fh, use_container_width=True); plt.close(fig_fh)

# Membership degree summary pills
td = result.temp_degrees
hd = result.hum_degrees
st.markdown(
    f'<span class="mem-pill">T: Cold = {td["cold"]:.3f}</span>'
    f'<span class="mem-pill">T: Warm = {td["warm"]:.3f}</span>'
    f'<span class="mem-pill">T: Hot = {td["hot"]:.3f}</span>'
    f'&nbsp;&nbsp;'
    f'<span class="mem-pill">H: Low = {hd["low"]:.3f}</span>'
    f'<span class="mem-pill">H: Medium = {hd["medium"]:.3f}</span>'
    f'<span class="mem-pill">H: High = {hd["high"]:.3f}</span>',
    unsafe_allow_html=True,
)
st.markdown("")


# ── STEP 3 — Rule evaluation ─────────────────────────────────────────────────
st.markdown("""
<div class="card">
  <div class="step-label">STEP 3</div>
  <div class="card-title">Rule Evaluation  —  AND = min</div>
  <div class="card-desc">
    Each rule fires at strength = min(μ_temperature, μ_humidity).
    Rules with strength 0 have no effect on the output.
  </div>
</div>
""", unsafe_allow_html=True)

fig_tbl = charts.plot_rule_table(result)
st.pyplot(fig_tbl, use_container_width=True)
plt.close(fig_tbl)


# ── STEP 4 — Implication ─────────────────────────────────────────────────────
st.markdown("""
<div class="card">
  <div class="step-label">STEP 4</div>
  <div class="card-title">Implication  —  clip at α</div>
  <div class="card-desc">
    Each active rule clips its output membership function at the firing strength α.
    Inactive rules (α = 0) are skipped.
  </div>
</div>
""", unsafe_allow_html=True)

impl_figs = charts.plot_implication(result, system)
if not impl_figs:
    st.warning("No rules fired. Adjust the inputs.")
else:
    cols = st.columns(min(len(impl_figs), 4))
    for j, (idx, t_lbl, h_lbl, f_lbl, fig) in enumerate(impl_figs):
        with cols[j % 4]:
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)


# ── STEP 5 — Aggregation ─────────────────────────────────────────────────────
st.markdown("""
<div class="card">
  <div class="step-label">STEP 5</div>
  <div class="card-title">Aggregation  —  OR = max</div>
  <div class="card-desc">
    All clipped consequent sets are combined by taking the pointwise maximum,
    forming a single aggregate fuzzy set.
  </div>
</div>
""", unsafe_allow_html=True)

fig_agg = charts.plot_aggregation(result)
st.pyplot(fig_agg, use_container_width=True)
plt.close(fig_agg)


# ── STEP 6 — Defuzzification ─────────────────────────────────────────────────
st.markdown(f"""
<div class="card">
  <div class="step-label">STEP 6</div>
  <div class="card-title">Defuzzification  —  centroid</div>
  <div class="card-desc">
    The centroid (centre of gravity) of the aggregate set gives the crisp output:
    <strong>{result.fan_speed:.2f}%</strong> fan speed.
  </div>
</div>
""", unsafe_allow_html=True)

fig_defuzz = charts.plot_defuzzification(result)
st.pyplot(fig_defuzz, use_container_width=True)
plt.close(fig_defuzz)


# ── Final result ──────────────────────────────────────────────────────────────
st.divider()
_, col_mid, _ = st.columns([1, 2, 1])
with col_mid:
    st.markdown(f"""
    <div class="result-box">
        <div style="font-size:0.78rem; color:#8a9bb8; margin-bottom:6px; letter-spacing:0.05em;">COMPUTED FAN SPEED</div>
        <div class="result-number">{result.fan_speed:.1f}%</div>
        <div class="result-sub">T = {input_temp} °C &nbsp;·&nbsp; H = {input_hum} %</div>
    </div>
    """, unsafe_allow_html=True)
