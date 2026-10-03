"""
theme.py
---------
Shared visual theme for the Streamlit app.
Modern dark academic / placement-cell dashboard theme.
"""

import streamlit as st

# ---------- COLORS ----------
PRIMARY = "#0F172A"          # Dark navy
PRIMARY_LIGHT = "#1E293B"    # Slate navy
ACCENT = "#38BDF8"           # Sky blue
ACCENT_2 = "#F59E0B"         # Amber

SUCCESS = "#22C55E"
WARNING = "#F59E0B"
DANGER = "#EF4444"

BG = "#0B1120"               # Main dark background
CARD_BG = "#111827"          # Card background
CARD_BG_LIGHT = "#172033"

TEXT = "#F8FAFC"             # Main text
TEXT_SECONDARY = "#CBD5E1"   # Secondary text
MUTED = "#94A3B8"

BORDER = "#263449"


def inject_css():
    st.markdown(
        f"""
        <style>

        /* ---------- GLOBAL ---------- */

        html, body, [class*="css"] {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}

        .stApp {{
    background: {BG} !important;
    color: {TEXT} !important;
}}

[data-testid="stAppViewContainer"] {{
    background: {BG} !important;
}}

[data-testid="stMain"] {{
    background: {BG} !important;
}}

[data-testid="stMainBlockContainer"] {{
    background: {BG} !important;
}}

[data-testid="stHeader"] {{
    background: {BG} !important;
}}

[data-testid="stToolbar"] {{
    background: transparent !important;
}}
        /* ---------- MAIN CONTENT ---------- */

        .main {{
            background: {BG};
        }}

        section[data-testid="stMain"] {{
            background: {BG};
        }}

        /* ---------- HEADINGS ---------- */

        h1, h2, h3 {{
            color: {TEXT} !important;
            font-weight: 700;
        }}

        h1 {{
            font-size: 2.3rem !important;
        }}

        h2 {{
            font-size: 1.7rem !important;
        }}

        h3 {{
            font-size: 1.25rem !important;
        }}

        p, label, span {{
            color: {TEXT_SECONDARY};
        }}

        /* ---------- SIDEBAR ---------- */

        section[data-testid="stSidebar"] {{
            background: linear-gradient(
                180deg,
                #0F172A 0%,
                #111827 100%
            );
            border-right: 1px solid {BORDER};
        }}

        section[data-testid="stSidebar"] * {{
            color: #E2E8F0 !important;
        }}

        section[data-testid="stSidebar"] .stRadio label {{
            font-family: 'Inter', sans-serif;
            font-weight: 500;
        }}

        /* ---------- SIDEBAR RADIO ---------- */

        section[data-testid="stSidebar"]
        div[role="radiogroup"] label {{
            border-radius: 8px;
            padding: 8px 10px;
            margin-bottom: 3px;
            transition: 0.2s ease;
        }}

        section[data-testid="stSidebar"]
        div[role="radiogroup"] label:hover {{
            background-color: #1E293B;
        }}

        /* ---------- METRIC CARDS ---------- */

        div[data-testid="stMetric"] {{
            background: linear-gradient(
                145deg,
                {CARD_BG_LIGHT},
                {CARD_BG}
            );
            border: 1px solid {BORDER};
            border-radius: 14px;
            padding: 18px 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.20);
        }}

        div[data-testid="stMetric"] label {{
            color: {MUTED} !important;
        }}

        div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
            color: {TEXT} !important;
            font-weight: 700;
        }}

        /* ---------- CUSTOM CARDS ---------- */

        .pc-card {{
            background: linear-gradient(
                145deg,
                {CARD_BG_LIGHT},
                {CARD_BG}
            );
            border: 1px solid {BORDER};
            border-radius: 14px;
            padding: 20px 22px;
            margin-bottom: 16px;
            box-shadow: 0 5px 18px rgba(0,0,0,0.18);
        }}

        .pc-card:hover {{
            border-color: #334155;
        }}

        /* ---------- BADGES ---------- */

        .pc-badge {{
            display: inline-block;
            padding: 5px 13px;
            border-radius: 20px;
            font-size: 0.82rem;
            font-weight: 600;
            color: white !important;
        }}

        .pc-badge-recommended {{
            background-color: {SUCCESS};
        }}

        .pc-badge-caution {{
            background-color: {WARNING};
        }}

        .pc-badge-not {{
            background-color: {DANGER};
        }}

        /* ---------- TAGS ---------- */

        .pc-tag {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.78rem;
            margin: 3px 5px 3px 0;
            background-color: #1E293B;
            color: #BAE6FD !important;
            border: 1px solid #334155;
        }}

        /* ---------- CHECK / CROSS ---------- */

        .pc-check {{
            color: {SUCCESS} !important;
            font-weight: 600;
        }}

        .pc-cross {{
            color: {DANGER} !important;
            font-weight: 600;
        }}

        .pc-muted {{
            color: {MUTED} !important;
            font-size: 0.9rem;
        }}

        /* ---------- BUTTONS ---------- */

        .stButton > button {{
            background-color: {ACCENT};
            color: #0F172A !important;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            padding: 8px 18px;
        }}

        .stButton > button:hover {{
            background-color: #7DD3FC;
            color: #0F172A !important;
        }}

        /* ---------- INPUTS ---------- */

        .stTextInput input,
        .stSelectbox div[data-baseweb="select"],
        .stMultiSelect div[data-baseweb="select"] {{
            background-color: {CARD_BG} !important;
            color: {TEXT} !important;
            border-color: {BORDER} !important;
        }}

        /* ---------- DATAFRAMES / TABLES ---------- */

        [data-testid="stDataFrame"] {{
            border: 1px solid {BORDER};
            border-radius: 10px;
        }}

        /* ---------- DIVIDERS ---------- */

        hr {{
            border-color: {BORDER};
        }}

        /* ---------- EXPANDERS ---------- */

        div[data-testid="stExpander"] {{
            background-color: {CARD_BG};
            border: 1px solid {BORDER};
            border-radius: 10px;
        }}

        /* ---------- ALERT BOXES ---------- */

        div[data-testid="stAlert"] {{
            border-radius: 10px;
        }}

        </style>
        """,
        unsafe_allow_html=True,
    )


def verdict_badge(verdict: str) -> str:
    cls = {
        "Recommended": "pc-badge-recommended",
        "Recommended with caution": "pc-badge-caution",
        "Not Recommended": "pc-badge-not",
    }.get(verdict, "pc-badge-caution")

    return f'<span class="pc-badge {cls}">{verdict}</span>'


def tag(text: str) -> str:
    return f'<span class="pc-tag">{text}</span>'