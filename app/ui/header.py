# ui/header.py
import json
import streamlit as st
from datetime import datetime, timedelta
from state import SharedState


def _fmt_time(t: str) -> str:
    """Feed time '063204' (UTC) → '09:32:04' (Riyadh, UTC+3)."""
    if not t or len(t) != 6:
        return t or "—"
    try:
        utc = datetime.strptime(t, "%H%M%S")
        riyadh = utc + timedelta(hours=3)
        return riyadh.strftime("%H:%M:%S")
    except ValueError:
        return f"{t[0:2]}:{t[2:4]}:{t[4:6]}"


def _fmt_date(d: str) -> str:
    """Feed date '20261028' → '2026-10-28'."""
    if not d or len(d) != 8:
        return d or "—"
    return f"{d[0:4]}-{d[4:6]}-{d[6:8]}"


def render_header(state: SharedState):
    left, right = st.columns([3, 3])

    with left:
        h1, h2 = st.columns([3, 1])
        with h1:
            new_sym = st.text_input(
                "Symbol", value=state.current_symbol, key="sym_input",
                label_visibility="collapsed", placeholder="Symbol",
            )
        with h2:
            if st.button("LOAD", use_container_width=True, type="primary"):
                sym = new_sym.strip()
                if sym:
                    state.current_symbol = sym
                    if sym not in state.subscribed_symbols and state.ws_price:
                        try:
                            state.ws_price.send(json.dumps({
                                "action": "SUBSCRIBE",
                                "symbols": [sym],
                                "exchange": state.market_exchange or "TDWL",
                            }))
                            state.subscribed_symbols.add(sym)
                        except Exception:
                            pass

    with right:
        ws_status = state.get_status()
        with state.lock:
            mkt_status = state.market_status
            mkt_exch = state.market_exchange
            mkt_date = state.market_date
            mkt_time = state.market_time

        ws_class = "live" if ws_status == "Live" else "warn"
        ws_label = "LIVE" if ws_status == "Live" else ws_status.upper()

        if mkt_status == "OPEN":
            mkt_class = "open"
        elif mkt_status in ("PRE_OPEN", "PRE_CLOSE"):
            mkt_status = "PRE OPEN" if mkt_status == "PRE_OPEN" else "PRE CLOSE"
            mkt_class = "warn"
        elif mkt_status == "CLOSING_AUCTION":
            mkt_status = "CLOSING AUCTION"
            mkt_class = "warn"
        elif mkt_status == "TRADE_AT_LAST":
            mkt_status = "TRADE AT LAST"
            mkt_class = "warn"
        elif mkt_status == "CLOSE":
            mkt_class = "closed"
        else:
            mkt_class = "closed"

            # ── Exchange date/time from the feed ─────────────────
        if mkt_date and mkt_time:
            date_display = _fmt_date(mkt_date)
            time_display = _fmt_time(mkt_time)
        else:
            # Fallback to local clock until first feed message arrives
            now = datetime.now()
            date_display = now.strftime("%Y-%m-%d")
            time_display = now.strftime("%H:%M:%S")

        st.markdown(
            f"""
            <div style="display:flex; flex-direction:column; gap:6px;
                        align-items:flex-end; padding-top:2px;">
                <div style="display:flex; gap:8px;">
                    <span class="status-pill {ws_class}">WS&nbsp;{ws_label}</span>
                    <span class="status-pill {mkt_class}">
                        {mkt_exch}&nbsp;{mkt_status}
                    </span>
                </div>
                <div style="
                    padding:5px 12px;
                    background:rgba(108,182,255,0.08);
                    border:1px solid rgba(108,182,255,0.2);
                    border-radius:6px;
                    font-family:'JetBrains Mono',monospace;
                    font-size:11px;
                    font-weight:500;
                    color:#a0aec0;
                    letter-spacing:0.04em;">
                    <span style="color:#6cb6ff;font-weight:600;">{mkt_exch}</span>
                    &nbsp;·&nbsp;
                    <span>{date_display}</span>
                    &nbsp;
                    <span style="color:#e6ecf2;font-weight:600;
                                 font-variant-numeric:tabular-nums;">
                        {time_display}
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    return state.current_symbol