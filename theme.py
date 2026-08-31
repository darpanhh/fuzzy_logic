"""
theme.py
--------
Single source of truth for every colour, font, and chart style used
across the application.  Import this module wherever you need a colour
or a styled matplotlib figure — never hard-code hex strings elsewhere.
"""

# ── Linguistic-term colours ───────────────────────────────────────────────────
# One accent per term, reused on every chart so the palette stays consistent.

TEMP_COLORS = {
    "cold": "#4a90d9",
    "warm": "#e8852b",
    "hot":  "#d94444",
}

HUM_COLORS = {
    "low":    "#3aab6f",
    "medium": "#c8a020",
    "high":   "#b0459a",
}

# Fan speed uses its own keys to avoid collision with humidity "medium"
FAN_COLORS = {
    "slow":     "#3aab6f",
    "medium_f": "#c8a020",
    "fast":     "#d94444",
}

# Convenience lookup for rule-table badge colours (Title-cased keys)
RULE_TEMP_COLORS = {k.title(): v for k, v in TEMP_COLORS.items()}
RULE_HUM_COLORS  = {k.title(): v for k, v in HUM_COLORS.items()}
RULE_FAN_COLORS  = {
    "Slow":   FAN_COLORS["slow"],
    "Medium": FAN_COLORS["medium_f"],
    "Fast":   FAN_COLORS["fast"],
}

# ── UI chrome colours ─────────────────────────────────────────────────────────
PAGE_BG        = "#f7f8fa"   # app background
CARD_BG        = "#ffffff"   # step card background
CARD_BORDER    = "#3b6fd4"   # left accent stripe on cards
LABEL_BG       = "#3b6fd4"   # "STEP N" badge background
RESULT_BG      = "#1a1f2e"   # dark result box
RESULT_NUM     = "#7aadff"   # large result number

# ── Chart colours ─────────────────────────────────────────────────────────────
CHART_FIG_BG   = "#ffffff"
CHART_AXES_BG  = "#f9fafc"
CHART_SPINE    = "#d0d6e0"
CHART_GRID     = "#e4e8f0"
CHART_TICK     = "#444444"
CHART_TITLE    = "#1a1f2e"
CHART_LABEL    = "#5a6478"
CHART_INPUT    = "#1a1f2e"   # vertical dashed line for crisp input

AGG_COLOR      = "#3b6fd4"   # aggregated set line
CENTROID_COLOR = "#d94444"   # centroid marker
CENTROID_FILL  = "#3aab6f"   # area left of centroid

# ── Table colours ─────────────────────────────────────────────────────────────
TABLE_HEADER_BG   = "#1a1f2e"
TABLE_HEADER_TEXT = "#c8d4f0"
TABLE_ROW_ODD     = "#f7f8fa"
TABLE_ROW_EVEN    = "#ffffff"
TABLE_SEP         = "#e0e4ea"
TABLE_ACTIVE_CLR  = "#3aab6f"   # ✓ tick
TABLE_INACTIVE    = "#b0b8cc"   # — dash / greyed text
TABLE_BAR_TRACK   = "#f0f2f8"
TABLE_BAR_TRACK_BORDER = "#d0d6e0"
TABLE_BAR_FILL    = "#3b6fd4"
TABLE_STRENGTH_CLR = "#3b6fd4"

# ── CSS injected into Streamlit ───────────────────────────────────────────────
STREAMLIT_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

html, body, [class*="css"] {{
    font-family: 'IBM Plex Sans', sans-serif;
}}
code, .mono {{ font-family: 'IBM Plex Mono', monospace; }}

.stApp {{ background: {PAGE_BG}; }}

.card {{
    background: {CARD_BG};
    border: 1px solid #e0e4ea;
    border-left: 4px solid {CARD_BORDER};
    border-radius: 4px;
    padding: 1rem 1.25rem;
    margin-bottom: 1.2rem;
}}
.card-title {{
    font-size: 1rem;
    font-weight: 600;
    color: {CHART_TITLE};
    margin-bottom: 0.25rem;
}}
.card-desc {{
    font-size: 0.875rem;
    color: {CHART_LABEL};
    line-height: 1.5;
}}

.step-label {{
    display: inline-block;
    background: {LABEL_BG};
    color: white;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    padding: 2px 10px;
    border-radius: 3px;
    margin-bottom: 6px;
    font-family: 'IBM Plex Mono', monospace;
}}

.result-box {{
    background: {RESULT_BG};
    color: #f0f4ff;
    border-radius: 6px;
    padding: 1.5rem 2rem;
    text-align: center;
}}
.result-number {{
    font-size: 3rem;
    font-weight: 600;
    color: {RESULT_NUM};
    font-family: 'IBM Plex Mono', monospace;
    line-height: 1;
}}
.result-sub {{
    font-size: 0.85rem;
    color: #8a9bb8;
    margin-top: 0.4rem;
}}

.mem-pill {{
    display: inline-block;
    background: #eef2ff;
    border: 1px solid #c7d4f5;
    border-radius: 4px;
    padding: 3px 10px;
    font-size: 0.82rem;
    color: #2c4a9e;
    font-family: 'IBM Plex Mono', monospace;
    margin: 3px 4px;
}}
</style>
"""
