# ui/equity.py
import streamlit as st


def render_equity(state, sym: str):
    """Renders the equity snapshot panel for the given symbol."""
    eq = state.get_equity(sym)

    if not eq:
        st.info(f"Waiting for equity data for {sym}…")
        return

    # Row 1 — price summary
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Last (ltp)", _fmt(eq.get("ltp")), _fmt_signed(eq.get("chg")))
    c2.metric("Bid (bbp)",  _fmt(eq.get("bbp")), _qty(eq.get("bbq")))
    c3.metric("Ask (bap)",  _fmt(eq.get("bap")), _qty(eq.get("baq")))
    c4.metric("Open",       _fmt(eq.get("open")))

    # Row 2 — session stats
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("High",     _fmt(eq.get("high")))
    c2.metric("Low",      _fmt(eq.get("low")))
    c3.metric("Volume",   _num(eq.get("vol")))
    c4.metric("Turnover", _num(eq.get("tovr")))

    # Row 3 — best-of-book totals
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Bid Levels",       _num(eq.get("nob")))
    c2.metric("Ask Levels",       _num(eq.get("noa")))
    c3.metric("Total Bid Qty",    _num(eq.get("tbq")))
    c4.metric("Total Ask Qty",    _num(eq.get("taq")))

    # Row 4 — valuation
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("52W High", _fmt(eq.get("h52")))
    c2.metric("52W Low",  _fmt(eq.get("l52")))
    c3.metric("P/E",      _fmt(eq.get("per")))
    c4.metric("P/B",      _fmt(eq.get("pbr")))

    # Footer
    st.caption(
        f"Updated: {eq.get('lutt', '—')} | "
        f"Trades: {_num(eq.get('trades'))} | "
        f"Currency: {eq.get('cur', 'SAR')}"
    )


def _fmt(v):
    """Format a float or return — if None."""
    if v is None:
        return "—"
    try:
        return f"{float(v):.2f}"
    except (ValueError, TypeError):
        return "—"


def _fmt_signed(v):
    """Signed format for change (+, -)."""
    if v is None:
        return None
    try:
        return f"{float(v):+.2f}"
    except (ValueError, TypeError):
        return None


def _num(v):
    """Format a number with thousands separator."""
    if v is None:
        return "—"
    try:
        return f"{float(v):,.0f}"
    except (ValueError, TypeError):
        return "—"


def _qty(v):
    """Format a quantity — same as _num for now."""
    return _num(v)