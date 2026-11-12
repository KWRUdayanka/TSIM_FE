# ui/market_overview.py
import streamlit as st
from state import SharedState


def render_market_overview(state: SharedState):
    """Full-width market aggregate strip."""
    with state.lock:
        adv     = getattr(state, "market_advances", None)
        dec     = getattr(state, "market_declines", None)
        unchg   = getattr(state, "market_unchanged", None)
        symbols = getattr(state, "market_symbols", None)
        vol     = getattr(state, "market_volume", None)
        tovr    = getattr(state, "market_turnover", None)
        trades  = getattr(state, "market_trades", None)
        cap     = getattr(state, "market_cap", None)

    def fmt_int(v):
        return "—" if v is None else f"{int(v):,}"

    def fmt_amt(v):
        if v is None:
            return "—"
        try:
            fv = float(v)
            if abs(fv) >= 1e9:
                return f"{fv/1e9:,.2f}B"
            if abs(fv) >= 1e6:
                return f"{fv/1e6:,.2f}M"
            if abs(fv) >= 1e3:
                return f"{fv/1e3:,.2f}K"
            return f"{fv:,.2f}"
        except (ValueError, TypeError):
            return "—"

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, var(--bg-1) 0%, var(--bg-2) 100%);
        border: 1px solid var(--border-subtle);
        border-radius: 10px;
        padding: 8px 20px;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
    ">
        <div style="display:flex; gap:100px; align-items:center;">
            <span style="display:inline-flex; gap:20px; align-items:baseline;">
                <span style="color:var(--text-lo);">Up</span>
                <span style="color:var(--green);font-weight:600;">{fmt_int(adv)}</span>
            </span>
            <span style="display:inline-flex; gap:20px; align-items:baseline;">
                <span style="color:var(--text-lo);">Down</span>
                <span style="color:var(--red);font-weight:600;">{fmt_int(dec)}</span>
            </span>
            <span style="display:inline-flex; gap:20px; align-items:baseline;">
                <span style="color:var(--text-lo);">Unchanged</span>
                <span style="color:var(--text-mid);font-weight:600;">{fmt_int(unchg)}</span>
            </span>
            <span style="display:inline-flex; gap:20px; align-items:baseline;">
                <span style="color:var(--text-lo);">Symbol Traded</span>
                <span style="color:var(--text-hi);font-weight:600;">{fmt_int(symbols)}</span>
            </span>
            <span style="width:1px;height:16px;background:var(--border-strong);"></span>
            <span style="display:inline-flex; gap:20px; align-items:baseline;">
                <span style="color:var(--text-lo);">Volume</span>
                <span style="color:var(--accent);font-weight:600;">{fmt_amt(vol)}</span>
            </span>
            <span style="display:inline-flex; gap:20px; align-items:baseline;">
                <span style="color:var(--text-lo);">Turnover</span>
                <span style="color:var(--accent);font-weight:600;">{fmt_amt(tovr)}</span>
            </span>
            <span style="display:inline-flex; gap:20px; align-items:baseline;">
                <span style="color:var(--text-lo);">Trades</span>
                <span style="color:var(--text-mid);font-weight:600;">{fmt_int(trades)}</span>
            </span>
            <span style="display:inline-flex; gap:20px; align-items:baseline;">
                <span style="color:var(--text-lo);">Market Cap</span>
                <span style="color:var(--violet);font-weight:600;">{fmt_amt(cap)}</span>
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)