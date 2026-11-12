# ui/styles.py
import streamlit as st


DARK_VARS = {
    "--bg-0": "#070a0f",
    "--bg-1": "#0d1219",
    "--bg-2": "#131a24",
    "--bg-3": "#1a2230",
    "--border-subtle": "rgba(120,160,210,0.08)",
    "--border-strong": "rgba(120,160,210,0.18)",
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
    "--bg-2": "#eef2f7",
    "--bg-3": "#e3e9f1",
    "--border-subtle": "rgba(40,70,120,0.10)",
    "--border-strong": "rgba(40,70,120,0.22)",
    "--text-hi": "#0f1720",
    "--text-mid": "#3b4a5c",
    "--text-lo": "#6b7a8d",
    "--accent": "#1f6feb",
    "--accent-dim": "rgba(31,111,235,0.12)",
    "--green": "#138a3d",
    "--green-dim": "rgba(19,138,61,0.12)",
    "--red": "#c0392b",
    "--red-dim": "rgba(192,57,43,0.12)",
    "--amber": "#b7791f",
    "--amber-dim": "rgba(183,121,31,0.15)",
    "--violet": "#6b46c1",
    "--bid-bar-a": "rgba(19,138,61,0.45)",
    "--bid-bar-b": "rgba(19,138,61,0.20)",
    "--bid-bar-c": "rgba(19,138,61,0.08)",
    "--ask-bar-a": "rgba(192,57,43,0.45)",
    "--ask-bar-b": "rgba(192,57,43,0.20)",
    "--ask-bar-c": "rgba(192,57,43,0.08)",
    "--my-glow": "rgba(183,121,31,0.35)",
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
        background:
            linear-gradient(180deg, rgba(255,255,255,0.02) 0%, rgba(255,255,255,0) 100%),
            var(--bg-1) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 10px !important;
        padding: 12px 14px !important;
        box-shadow:
            0 1px 2px rgba(0,0,0,0.10),
            0 4px 12px rgba(0,0,0,0.06) !important;
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

    /* Widget labels and values */
    label, .stSelectbox label, .stNumberInput label,
    .stTextInput label, .stDateInput label {{
        color: var(--text-lo) !important;
    }}
    [data-baseweb="select"] > div,
    [data-baseweb="input"] > div,
    [data-baseweb="base-input"] {{
        background: var(--bg-2) !important;
        color: var(--text-hi) !important;
        border-color: var(--border-subtle) !important;
    }}
    [data-baseweb="popover"] ul {{
        background: var(--bg-2) !important;
        color: var(--text-hi) !important;
    }}
    [data-baseweb="popover"] li:hover {{
        background: var(--bg-3) !important;
    }}

    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input {{
        background: var(--bg-2) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 6px !important;
        color: var(--text-hi) !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 12px !important;
        padding: 7px 10px !important;
        transition: all 0.15s ease;
    }}
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stDateInput > div > div > input:focus {{
        border-color: var(--accent) !important;
        background: var(--bg-3) !important;
        box-shadow: 0 0 0 3px var(--accent-dim) !important;
        outline: none !important;
    }}
    .stSelectbox > div > div {{
        background: var(--bg-2) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 6px !important;
        font-size: 12px !important;
        color: var(--text-hi) !important;
    }}

    .stButton > button {{
        background: var(--bg-2) !important;
        border: 1px solid var(--border-strong) !important;
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
        color: #0a1a10 !important;
        box-shadow: 0 2px 8px var(--green-dim) !important;
    }}
    .stButton > button[kind="primary"]:hover {{
        box-shadow: 0 4px 12px var(--green-dim) !important;
    }}

    [data-testid="stDataFrame"] {{
        border-radius: 8px !important;
        overflow: hidden !important;
        border: 1px solid var(--border-subtle) !important;
    }}
    [data-testid="stDataFrame"] table {{
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 11px !important;
    }}

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
    .status-pill.live {{
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
    .status-pill.open {{
        background: var(--green-dim);
        color: var(--green);
        border: 1px solid var(--green-dim);
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

    ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
    ::-webkit-scrollbar-track {{ background: transparent; }}
    ::-webkit-scrollbar-thumb {{
        background: var(--border-strong);
        border-radius: 4px;
    }}
    ::-webkit-scrollbar-thumb:hover {{ background: var(--accent); }}

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