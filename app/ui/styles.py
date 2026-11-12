# ui/styles.py
import streamlit as st

DARK_VARS = {
    "--bg-0": "#070a0f",
    "--bg-1": "#0d1219",
    "--bg-2": "#131a24",
    "--bg-3": "#1a2230",
    "--border-subtle": "rgba(120,160,210,0.08)",
    "--border-strong": "rgba(120,160,210,0.18)",
    "--border-input": "rgba(120,160,210,0.28)",
    "--text-hi": "#e6ecf2",
    "--text-mid": "#a0aec0",
    "--text-lo": "#5c6b7f",
    "--accent": "#6cb6ff",
    "--accent-dim": "rgba(108,182,255,0.12)",
    "--green": "#4ade80",
    "--green-dim": "rgba(74,222,128,0.15)",
    "--red": "#f87171",
    "--red-dim": "rgba(248,113,113,0.15)",
    "--amber": "#fbbf24",
    "--amber-dim": "rgba(251,191,36,0.15)",
    "--violet": "#a78bfa",
    "--bid-bar-a": "rgba(74,222,128,0.55)",
    "--bid-bar-b": "rgba(74,222,128,0.25)",
    "--bid-bar-c": "rgba(74,222,128,0.10)",
    "--ask-bar-a": "rgba(248,113,113,0.55)",
    "--ask-bar-b": "rgba(248,113,113,0.25)",
    "--ask-bar-c": "rgba(248,113,113,0.10)",
    "--my-glow": "rgba(251,191,36,0.5)",
}

LIGHT_VARS = {
    "--bg-0": "#f7f9fc",
    "--bg-1": "#ffffff",
    "--bg-2": "#ffffff",
    "--bg-3": "#f1f5fb",
    "--border-subtle": "rgba(40,70,120,0.12)",
    "--border-strong": "rgba(40,70,120,0.24)",
    "--border-input": "rgba(40,70,120,0.35)",
    "--text-hi": "#0f1720",
    "--text-mid": "#2c3a4a",
    "--text-lo": "#5a6878",
    "--accent": "#1f6feb",
    "--accent-dim": "rgba(31,111,235,0.12)",
    "--green": "#0f8a3d",
    "--green-dim": "rgba(15,138,61,0.12)",
    "--red": "#c0392b",
    "--red-dim": "rgba(192,57,43,0.12)",
    "--amber": "#9a6a00",
    "--amber-dim": "rgba(154,106,0,0.14)",
    "--violet": "#6b46c1",
    "--bid-bar-a": "rgba(15,138,61,0.40)",
    "--bid-bar-b": "rgba(15,138,61,0.18)",
    "--bid-bar-c": "rgba(15,138,61,0.06)",
    "--ask-bar-a": "rgba(192,57,43,0.40)",
    "--ask-bar-b": "rgba(192,57,43,0.18)",
    "--ask-bar-c": "rgba(192,57,43,0.06)",
    "--my-glow": "rgba(154,106,0,0.30)",
}


def _vars_block(vars_dict):
    return "\n".join(f"        {k}: {v};" for k, v in vars_dict.items())


def inject_styles():
    mode = st.session_state.get("theme_mode", "dark")
    v = DARK_VARS if mode == "dark" else LIGHT_VARS

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    *, *::before, *::after {{ box-sizing: border-box; }}

    :root {{
{_vars_block(v)}
    }}

    html, body, [data-testid="stAppViewContainer"] {{
        height: 100vh !important;
        overflow: hidden !important;
        background: var(--bg-0) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: var(--text-hi);
    }}

    header, footer, #MainMenu,
    [data-testid="stToolbar"],
    [data-testid="stDecoration"] {{
        visibility: hidden !important;
        display: none !important;
    }}

    .block-container {{
        padding: 0.5rem 1rem !important;
        max-width: 100% !important;
    }}

    [data-testid="stVerticalBlock"] {{ gap: 0.5rem !important; }}
    [data-testid="stHorizontalBlock"] {{ gap: 0.75rem !important; }}

    [data-testid="stVerticalBlockBorderWrapper"] {{
        background: var(--bg-1) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 10px !important;
        padding: 12px 14px !important;
        box-shadow:
            0 1px 2px rgba(0,0,0,0.08),
            0 4px 12px rgba(0,0,0,0.05) !important;
        transition: border-color 0.2s ease;
    }}
    [data-testid="stVerticalBlockBorderWrapper"]:hover {{
        border-color: var(--border-strong) !important;
    }}

    h1, h2, h3, h4, h5, h6 {{
        color: var(--text-hi) !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em !important;
        margin: 0 0 0.5rem 0 !important;
    }}
    h3 {{
        font-size: 12px !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        color: var(--text-lo) !important;
        padding-bottom: 6px !important;
        border-bottom: 1px solid var(--border-subtle) !important;
        margin-bottom: 10px !important;
    }}

    [data-testid="stMetric"] {{
        background: var(--bg-2) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 8px !important;
        padding: 8px 10px !important;
        transition: all 0.15s ease;
    }}
    [data-testid="stMetric"]:hover {{
        background: var(--bg-3) !important;
        border-color: var(--border-strong) !important;
        transform: translateY(-1px);
    }}
    [data-testid="stMetricLabel"] {{
        font-size: 9px !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
        color: var(--text-lo) !important;
        margin-bottom: 3px !important;
        line-height: 1 !important;
    }}
    [data-testid="stMetricValue"] {{
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        color: var(--text-hi) !important;
        line-height: 1.2 !important;
        letter-spacing: -0.02em;
    }}
    [data-testid="stMetricDelta"] {{
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 10px !important;
        font-weight: 500 !important;
        margin-top: 2px !important;
    }}

    /* ---------- widget labels ---------- */
    label,
    .stTextInput > label,
    .stNumberInput > label,
    .stSelectbox > label,
    .stDateInput > label {{
        color: var(--text-lo) !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        letter-spacing: 0.04em !important;
    }}

    /* ---------- text inputs / number inputs / date inputs ---------- */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input,
    [data-baseweb="input"] input {{
        background: var(--bg-2) !important;
        color: var(--text-hi) !important;
        -webkit-text-fill-color: var(--text-hi) !important;
        caret-color: var(--text-hi) !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 12px !important;
        padding: 7px 10px !important;
        border: none !important;
        box-shadow: none !important;
    }}

    [data-baseweb="input"] > div {{
        background: var(--bg-2) !important;
        border: 1px solid var(--border-input) !important;
        border-radius: 6px !important;
    }}

    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stDateInput > div > div > input:focus,
    [data-baseweb="input"] input:focus {{
        background: var(--bg-2) !important;
        color: var(--text-hi) !important;
        box-shadow: 0 0 0 3px var(--accent-dim) !important;
        outline: none !important;
    }}

    .stTextInput input::placeholder,
    .stNumberInput input::placeholder {{
        color: var(--text-lo) !important;
        -webkit-text-fill-color: var(--text-lo) !important;
        opacity: 0.85 !important;
    }}

    .stTextInput input:disabled,
    .stNumberInput input:disabled {{
        background: var(--bg-3) !important;
        color: var(--text-mid) !important;
        -webkit-text-fill-color: var(--text-mid) !important;
    }}

    /* ---------- number input stepper buttons (+ / -) ---------- */
    .stNumberInput [data-testid="stNumberInputStepDown"],
    .stNumberInput [data-testid="stNumberInputStepUp"] {{
        background-color: var(--bg-3) !important;
        border: none !important;
        border-left: 1px solid var(--border-input) !important;
        color: var(--text-hi) !important;
        border-radius: 0 !important;
    }}

    .stNumberInput [data-testid="stNumberInputStepDown"]:last-child,
    .stNumberInput [data-testid="stNumberInputStepUp"]:last-child {{
        border-top-right-radius: 6px !important;
        border-bottom-right-radius: 6px !important;
    }}

    .stNumberInput [data-testid="stNumberInputStepDown"]:hover,
    .stNumberInput [data-testid="stNumberInputStepUp"]:hover {{
        background-color: var(--border-input) !important;
        color: var(--accent) !important;
    }}

    .stNumberInput [data-testid="stNumberInputStepDown"] svg,
    .stNumberInput [data-testid="stNumberInputStepUp"] svg {{
        fill: var(--text-hi) !important;
        color: var(--text-hi) !important;
    }}

    /* ---------- selectbox ---------- */
    .stSelectbox > div > div,
    [data-baseweb="select"] > div {{
        background: var(--bg-2) !important;
        border: 1px solid var(--border-input) !important;
        border-radius: 6px !important;
        font-size: 12px !important;
        color: var(--text-hi) !important;
    }}

    div[data-baseweb="select"] > div > div,
    div[data-baseweb="select"] span,
    div[data-baseweb="select"] input {{
        color: var(--text-hi) !important;
        -webkit-text-fill-color: var(--text-hi) !important;
    }}

    div[data-baseweb="select"] svg {{
        fill: var(--text-mid) !important;
        color: var(--text-mid) !important;
    }}

    [data-baseweb="popover"] > div,
    [data-baseweb="menu"] {{
        background: var(--bg-1) !important;
        border: 1px solid var(--border-input) !important;
        border-radius: 6px !important;
        color: var(--text-hi) !important;
    }}
    [data-baseweb="menu"] li,
    [data-baseweb="menu"] ul li {{
        color: var(--text-hi) !important;
        background: var(--bg-1) !important;
    }}
    [data-baseweb="menu"] li:hover,
    [data-baseweb="menu"] ul li:hover,
    [data-baseweb="menu"] [aria-selected="true"] {{
        background: var(--bg-3) !important;
        color: var(--accent) !important;
    }}

    [data-baseweb="base-input"] {{
        background: var(--bg-2) !important;
        border-color: var(--border-input) !important;
        color: var(--text-hi) !important;
    }}

    /* ---------- radio buttons ---------- */
    [data-baseweb="radio"] div {{
        color: var(--text-hi) !important;
    }}
    [data-baseweb="radio"] [data-testid="stMarkdownContainer"] p {{
        color: var(--text-hi) !important;
        -webkit-text-fill-color: var(--text-hi) !important;
        font-family: 'Inter', sans-serif !important;
    }}
    [data-baseweb="radio"] div[role="radio"] > div:first-child {{
        border-color: var(--text-mid) !important;
    }}
    [data-baseweb="radio"] div[aria-checked="true"] > div:first-child > div {{
        background-color: var(--accent) !important;
    }}
    [data-baseweb="radio"] div[aria-checked="true"] > div:first-child {{
        border-color: var(--accent) !important;
    }}

    /* ---------- buttons ---------- */
    .stButton > button {{
        background: var(--bg-2) !important;
        border: 1px solid var(--border-input) !important;
        border-radius: 6px !important;
        color: var(--text-hi) !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        letter-spacing: 0.03em !important;
        text-transform: uppercase !important;
        padding: 7px 14px !important;
        transition: all 0.15s ease;
    }}
    .stButton > button:hover {{
        background: var(--bg-3) !important;
        border-color: var(--accent) !important;
        color: var(--accent) !important;
        transform: translateY(-1px);
    }}
    .stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, var(--green) 0%, var(--green) 100%) !important;
        border: none !important;
        color: #ffffff !important;
        box-shadow: 0 2px 8px var(--green-dim) !important;
    }}
    .stButton > button[kind="primary"]:hover {{
        box-shadow: 0 4px 12px var(--green-dim) !important;
        color: #ffffff !important;
    }}

    /* ---------- dataframe fallback styling ---------- */
    [data-testid="stDataFrame"] {{
        border-radius: 8px !important;
        overflow: hidden !important;
        border: 1px solid var(--border-subtle) !important;
        background-color: var(--bg-1) !important;
    }}
    [data-testid="stDataFrame"] > div,
    [data-testid="stDataFrame"] iframe {{
        background-color: var(--bg-1) !important;
        color: var(--text-hi) !important;
    }}
    [data-testid="stDataFrame"] canvas {{
        opacity: 0.99 !important; 
    }}
    [data-testid="stDataFrame"] [role="grid"] {{
        background-color: var(--bg-1) !important;
        color: var(--text-hi) !important;
        border-color: var(--border-subtle) !important;
    }}
    [data-testid="stDataFrame"] [role="row"] {{
        background-color: var(--bg-1) !important;
    }}
    [data-testid="stDataFrame"] [role="columnheader"] {{
        background-color: var(--bg-2) !important;
        color: var(--text-lo) !important;
    }}
    [data-testid="stDataFrame"] [role="gridcell"] {{
        color: var(--text-hi) !important;
    }}
    [data-testid="stDataFrame"] table {{
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 11px !important;
    }}

    /* ---------- order book ---------- */
    .book-header {{
        color: var(--text-hi);
        font-size: 18px;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin-bottom: 6px;
    }}
    .spread {{
        color: var(--amber);
        font-family: 'JetBrains Mono', monospace;
        font-size: 10px;
        font-weight: 600;
        letter-spacing: 0.05em;
        padding: 3px 8px;
        background: var(--amber-dim);
        border-radius: 4px;
        display: inline-block;
        margin-bottom: 8px;
    }}
    .col-header {{
        color: var(--text-lo);
        font-size: 9px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 4px;
        padding: 0;
    }}
    .bid {{
        color: var(--green);
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        font-weight: 500;
        margin: 0;
        padding: 1px 0;
    }}
    .ask {{
        color: var(--red);
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        font-weight: 500;
        margin: 0;
        padding: 1px 0;
    }}
    .my-order {{
        color: var(--amber) !important;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        font-size: 12px;
        margin: 0;
        padding: 1px 0;
        text-shadow: 0 0 10px var(--my-glow);
    }}

    /* ---------- status pills ---------- */
    .status-pill {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 10px;
        border-radius: 6px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 10px;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }}
    .status-pill.live,
    .status-pill.open {{
        background: var(--green-dim);
        color: var(--green);
        border: 1px solid var(--green-dim);
    }}
    .status-pill.live::before {{
        content: '';
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: var(--green);
        box-shadow: 0 0 8px var(--green);
        animation: pulse 1.8s ease-in-out infinite;
    }}
    .status-pill.closed {{
        background: var(--red-dim);
        color: var(--red);
        border: 1px solid var(--red-dim);
    }}
    .status-pill.warn {{
        background: var(--amber-dim);
        color: var(--amber);
        border: 1px solid var(--amber-dim);
    }}
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; box-shadow: 0 0 8px var(--green); }}
        50% {{ opacity: 0.5; box-shadow: 0 0 4px var(--green); }}
    }}

    /* ---------- scrollbar ---------- */
    ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
    ::-webkit-scrollbar-track {{ background: transparent; }}
    ::-webkit-scrollbar-thumb {{
        background: var(--border-strong);
        border-radius: 4px;
    }}
    ::-webkit-scrollbar-thumb:hover {{ background: var(--accent); }}

    /* ---------- misc ---------- */
    hr {{
        border: none !important;
        border-top: 1px solid var(--border-subtle) !important;
        margin: 0.5rem 0 !important;
    }}
    [data-testid="stAlert"] {{
        border-radius: 8px !important;
        font-size: 12px !important;
        padding: 8px 12px !important;
        border: 1px solid var(--border-subtle) !important;
    }}
    [data-testid="stToast"] {{
        background: var(--bg-2) !important;
        border: 1px solid var(--border-strong) !important;
        border-radius: 8px !important;
        font-family: 'Inter', sans-serif !important;
    }}
    [data-testid="stCaptionContainer"],
    .stCaption {{
        color: var(--text-lo) !important;
        font-size: 10px !important;
        font-family: 'JetBrains Mono', monospace !important;
    }}
    </style>
    """, unsafe_allow_html=True)