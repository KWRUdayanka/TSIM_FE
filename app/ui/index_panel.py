# ui/index_panel.py
import streamlit as st


# ============================================================
#  Helpers
# ============================================================

def _fmt(v):
    if v is None:
        return "—"
    try:
        return f"{float(v):.2f}"
    except (ValueError, TypeError):
        return "—"


def _signed(v, suffix=""):
    if v is None:
        return "—"
    try:
        return f"{float(v):+.2f}{suffix}"
    except (ValueError, TypeError):
        return "—"


def _num(v):
    if v is None:
        return "—"
    try:
        return f"{float(v):,.0f}"
    except (ValueError, TypeError):
        return "—"


# ============================================================
#  Compact strip (for multiple indices side-by-side)
# ============================================================

def render_index_strip(state, symbols):
    """Compact inline strip for multiple indices — one per column."""
    if not symbols:
        return

    cols = st.columns(len(symbols))
    for i, sym in enumerate(symbols):
        idx = state.get_index(sym)
        with cols[i]:
            if not idx:
                st.caption(f"**{sym}**: —")
                continue

            ltp = idx.get("ltp")
            chg = idx.get("chg")
            pct = idx.get("pctChg")

            try:
                chg_val = float(chg) if chg is not None else 0
            except (ValueError, TypeError):
                chg_val = 0

            if chg_val > 0:
                color = "#51cf66"   # green
            elif chg_val < 0:
                color = "#ff6b6b"   # red
            else:
                color = "#d4d4d4"   # grey

            st.markdown(
                f'<div style="font-family:monospace;font-size:12px;padding:4px 0;">'
                f'<b style="color:#6cb6ff;">{sym}</b>&nbsp;'
                f'<span style="color:#d4d4d4;">{_fmt(ltp)}</span>&nbsp;'
                f'<span style="color:{color};">'
                f'{_signed(chg)} ({_signed(pct, "%")})'
                f'</span>'
                f'</div>',
                unsafe_allow_html=True,
            )


# ============================================================
#  Detailed panel (5×4 metric grid)
# ============================================================

def render_index(state, sym: str):
    """Detailed panel (full 5×4 grid) for a single index."""
    idx = state.get_index(sym)

    if not idx:
        st.info(f"Waiting for index data for {sym}…")
        return

    st.markdown(f"### {sym} — Index")

    # Row 1 — value + daily change
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Value (ltp)",  _fmt(idx.get("ltp")))
    c2.metric("Change",        _signed(idx.get("chg")))
    c3.metric("Change %",      _signed(idx.get("pctChg"), "%"))
    c4.metric("Prev Close",    _fmt(idx.get("prvCls")))

    # Row 2 — session OHLC
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Open",   _fmt(idx.get("open")))
    c2.metric("High",   _fmt(idx.get("high")))
    c3.metric("Low",    _fmt(idx.get("low")))
    c4.metric("Close",  _fmt(idx.get("cls")))

    # Row 3 — market breadth
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Advances",       _num(idx.get("ups")))
    c2.metric("Declines",       _num(idx.get("dwns")))
    c3.metric("Unchanged",      _num(idx.get("unchg")))
    c4.metric("Symbols Traded", _num(idx.get("symt")))

    # Row 4 — turnover
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Volume",   _num(idx.get("vol")))
    c2.metric("Turnover", _num(idx.get("tovr")))
    c3.metric("Cash In",  _num(idx.get("cit")))
    c4.metric("Cash Out", _num(idx.get("cot")))

    # Row 5 — valuation + YTD + 52W
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Mkt Cap",      _num(idx.get("mktCap")))
    c2.metric("YTD Change",   _signed(idx.get("ytdChg")))
    c3.metric("YTD Change %", _signed(idx.get("pctYtd"), "%"))
    c4.metric("52W High",     _fmt(idx.get("h52")))

    # Footer
    st.caption(
        f"Updated: {idx.get('lutt', '—')} | "
        f"Trades: {_num(idx.get('trades'))} | "
        f"Exchange: {idx.get('exg', '—')}"
    )