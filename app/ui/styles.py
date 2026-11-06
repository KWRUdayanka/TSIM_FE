# ui/styles.py
import streamlit as st


def inject_styles():
    st.markdown("""
    <style>
    /* ============================================================
       IMPORTS
       ============================================================ */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    /* ============================================================
       RESET & ROOT
       ============================================================ */
    *, *::before, *::after { box-sizing: border-box; }

    :root {
        --bg-0: #070a0f;         /* page background */
        --bg-1: #0d1219;         /* card background */
        --bg-2: #131a24;         /* elevated surface */
        --bg-3: #1a2230;         /* hover surface */
        --border-subtle: rgba(120, 160, 210, 0.08);
        --border-strong: rgba(120, 160, 210, 0.18);
        --text-hi: #e6ecf2;
        --text-mid: #a0aec0;
        --text-lo: #5c6b7f;
        --accent: #6cb6ff;
        --accent-dim: rgba(108, 182, 255, 0.12);
        --green: #4ade80;
        --green-dim: rgba(74, 222, 128, 0.15);
        --red: #f87171;
        --red-dim: rgba(248, 113, 113, 0.15);
        --amber: #fbbf24;
        --amber-dim: rgba(251, 191, 36, 0.15);
        --violet: #a78bfa;
    }

    html, body, [data-testid="stAppViewContainer"] {
        height: 100vh !important;
        overflow: hidden !important;
        background: var(--bg-0) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: var(--text-hi);
    }

    /* Hide Streamlit chrome */
    header, footer, #MainMenu,
    [data-testid="stToolbar"],
    [data-testid="stDecoration"] {
        visibility: hidden !important;
        display: none !important;
    }

    /* ============================================================
       LAYOUT
       ============================================================ */
    .block-container {
        padding: 0.5rem 1rem !important;
        max-width: 100% !important;
    }

    [data-testid="stVerticalBlock"] {
        gap: 0.5rem !important;
    }

    [data-testid="stHorizontalBlock"] {
        gap: 0.75rem !important;
    }

    /* ============================================================
       CARDS — glassmorphic panels with soft elevation
       ============================================================ */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background:
            linear-gradient(180deg, rgba(255,255,255,0.02) 0%, rgba(255,255,255,0) 100%),
            var(--bg-1) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 10px !important;
        padding: 12px 14px !important;
        box-shadow:
            0 1px 2px rgba(0, 0, 0, 0.3),
            0 4px 12px rgba(0, 0, 0, 0.15),
            inset 0 1px 0 rgba(255, 255, 255, 0.03) !important;
        transition: border-color 0.2s ease;
    }

    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: var(--border-strong) !important;
    }

    /* ============================================================
       TYPOGRAPHY
       ============================================================ */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-hi) !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em !important;
        margin: 0 0 0.5rem 0 !important;
    }

    h3 {
        font-size: 12px !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        color: var(--text-lo) !important;
        padding-bottom: 6px !important;
        border-bottom: 1px solid var(--border-subtle) !important;
        margin-bottom: 10px !important;
    }

    /* ============================================================
       METRICS — modern data tiles
       ============================================================ */
    [data-testid="stMetric"] {
        background: var(--bg-2) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 8px !important;
        padding: 8px 10px !important;
        transition: all 0.15s ease;
    }

    [data-testid="stMetric"]:hover {
        background: var(--bg-3) !important;
        border-color: var(--border-strong) !important;
        transform: translateY(-1px);
    }

    [data-testid="stMetricLabel"] {
        font-size: 9px !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
        color: var(--text-lo) !important;
        margin-bottom: 3px !important;
        line-height: 1 !important;
    }

    [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        color: var(--text-hi) !important;
        line-height: 1.2 !important;
        letter-spacing: -0.02em;
    }

    [data-testid="stMetricDelta"] {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 10px !important;
        font-weight: 500 !important;
        margin-top: 2px !important;
    }

    /* ============================================================
       INPUTS — floating field style
       ============================================================ */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input {
        background: var(--bg-2) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 6px !important;
        color: var(--text-hi) !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 12px !important;
        padding: 7px 10px !important;
        transition: all 0.15s ease;
    }

    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stDateInput > div > div > input:focus {
        border-color: var(--accent) !important;
        background: var(--bg-3) !important;
        box-shadow: 0 0 0 3px rgba(108, 182, 255, 0.1) !important;
        outline: none !important;
    }

    .stSelectbox > div > div {
        background: var(--bg-2) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 6px !important;
        font-size: 12px !important;
        color: var(--text-hi) !important;
    }

    /* ============================================================
       BUTTONS
       ============================================================ */
    .stButton > button {
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
    }

    .stButton > button:hover {
        background: var(--bg-3) !important;
        border-color: var(--accent) !important;
        color: var(--accent) !important;
        transform: translateY(-1px);
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #4ade80 0%, #22c55e 100%) !important;
        border: none !important;
        color: #0a1a10 !important;
        box-shadow: 0 2px 8px rgba(74, 222, 128, 0.3) !important;
    }

    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #5eea90 0%, #2dd063 100%) !important;
        box-shadow: 0 4px 12px rgba(74, 222, 128, 0.4) !important;
    }

    /* ============================================================
       DATAFRAME
       ============================================================ */
    [data-testid="stDataFrame"] {
        border-radius: 8px !important;
        overflow: hidden !important;
        border: 1px solid var(--border-subtle) !important;
    }

    [data-testid="stDataFrame"] table {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 11px !important;
    }

    /* ============================================================
       ORDER BOOK ELEMENTS
       ============================================================ */
    .book-header {
        color: var(--text-hi);
        font-size: 18px;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin-bottom: 6px;
    }

    .spread {
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
    }

    .col-header {
        color: var(--text-lo);
        font-size: 9px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 4px;
        padding: 0;
    }

    .bid {
        color: var(--green);
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        font-weight: 500;
        margin: 0;
        padding: 1px 0;
    }

    .ask {
        color: var(--red);
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        font-weight: 500;
        margin: 0;
        padding: 1px 0;
    }

    .my-order {
        color: var(--amber) !important;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        font-size: 12px;
        margin: 0;
        padding: 1px 0;
        text-shadow: 0 0 10px rgba(251, 191, 36, 0.5);
    }

    /* ============================================================
       STATUS PILLS
       ============================================================ */
    .status-pill {
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
    }

    .status-pill.live {
        background: var(--green-dim);
        color: var(--green);
        border: 1px solid rgba(74, 222, 128, 0.3);
    }

    .status-pill.live::before {
        content: '';
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: var(--green);
        box-shadow: 0 0 8px var(--green);
        animation: pulse 1.8s ease-in-out infinite;
    }

    .status-pill.open {
        background: var(--green-dim);
        color: var(--green);
        border: 1px solid rgba(74, 222, 128, 0.3);
    }

    .status-pill.closed {
        background: var(--red-dim);
        color: var(--red);
        border: 1px solid rgba(248, 113, 113, 0.3);
    }

    .status-pill.warn {
        background: var(--amber-dim);
        color: var(--amber);
        border: 1px solid rgba(251, 191, 36, 0.3);
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; box-shadow: 0 0 8px var(--green); }
        50% { opacity: 0.5; box-shadow: 0 0 4px var(--green); }
    }

    /* ============================================================
       SCROLLBAR
       ============================================================ */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
        background: var(--border-strong);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover { background: var(--accent); }

    /* ============================================================
       DIVIDERS
       ============================================================ */
    hr {
        border: none !important;
        border-top: 1px solid var(--border-subtle) !important;
        margin: 0.5rem 0 !important;
    }

    /* ============================================================
       ALERTS
       ============================================================ */
    [data-testid="stAlert"] {
        border-radius: 8px !important;
        font-size: 12px !important;
        padding: 8px 12px !important;
        border: 1px solid var(--border-subtle) !important;
    }

    /* ============================================================
       TOAST
       ============================================================ */
    [data-testid="stToast"] {
        background: var(--bg-2) !important;
        border: 1px solid var(--border-strong) !important;
        border-radius: 8px !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* ============================================================
       CAPTIONS
       ============================================================ */
    [data-testid="stCaptionContainer"],
    .stCaption {
        color: var(--text-lo) !important;
        font-size: 10px !important;
        font-family: 'JetBrains Mono', monospace !important;
    }
    </style>
    """, unsafe_allow_html=True)