# ui/nav_bar.py
import streamlit as st

from state import SharedState


def render_nav_bar(state: SharedState):
    # 5 buttons + label. Widths sum to 8.
    c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1, 4])

    with c1:
        active = getattr(state, "view_mode", "MARKET_WATCH") == "INDEX"
        if st.button(
            "📈  INDEX",
            key="nav_index",
            use_container_width=True,
            type="primary" if active else "secondary",
        ):
            state.view_mode = "INDEX"
            st.rerun()

    with c2:
        active = getattr(state, "view_mode", "MARKET_WATCH") == "MARKET_WATCH"
        if st.button(
            "🎯  MARKET WATCH",
            key="nav_market_watch",
            use_container_width=True,
            type="primary" if active else "secondary",
        ):
            state.view_mode = "MARKET_WATCH"
            st.rerun()

    with c3:
        active = getattr(state, "view_mode", "MARKET_WATCH") == "OHLC_CHART"
        if st.button(
            "📊  CHART",
            key="nav_chart",
            use_container_width=True,
            type="primary" if active else "secondary",
        ):
            chart_sym = getattr(state, "context_symbol", None) or state.current_symbol
            if chart_sym:
                state.chart_symbol = chart_sym
                state.view_mode = "OHLC_CHART"
                st.rerun()

    with c4:
        active = getattr(state, "view_mode", "MARKET_WATCH") == "TOP_STOCKS"
        if st.button(
            "🏆  TOP STOCKS",
            key="nav_top_stocks",
            use_container_width=True,
            type="primary" if active else "secondary",
        ):
            state.view_mode = "TOP_STOCKS"
            st.rerun()

    with c5:
        mode = getattr(state, "view_mode", "MARKET_WATCH")
        label = mode
        if mode == "OHLC_CHART" and getattr(state, "chart_symbol", None):
            tf = getattr(state, "ohlc_current_tf", "1m")
            label = f"{mode} · {state.chart_symbol} · {tf}"
        elif mode == "TOP_STOCKS":
            tt = getattr(state, "top_stocks_tt", "0")
            labels = {
                "0": "Gainers·Chg",  "1": "Gainers·%",
                "2": "Losers·Chg",   "3": "Losers·%",
                "4": "Vol",          "5": "Trades",
                "6": "Turnover",     "7": "52w Low",
                "8": "52w High",
            }
            label = f"{mode} · {labels.get(tt, tt)}"
        st.markdown(
            f'<div style="text-align:right;padding-top:8px;'
            f'font-family:JetBrains Mono,monospace;font-size:11px;'
            f'color:#5c6b7f;letter-spacing:0.06em;">'
            f'VIEW: <span style="color:#6cb6ff;font-weight:600;">{label}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )