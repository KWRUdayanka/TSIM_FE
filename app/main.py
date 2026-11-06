# main.py
import threading

import streamlit as st
from streamlit_autorefresh import st_autorefresh

from config import AUTOREFRESH_MS
from state import SharedState
from ui.context_menu import consume_context_click, inject_right_click_handler
from ui.equity_popup import maybe_show_equity_popup
from ui.header import render_header
from ui.index_view import render_index_view
from ui.market_overview import render_market_overview
from ui.market_watch import render_market_watch
from ui.nav_bar import render_nav_bar
from ui.ohlc_chart import render_ohlc_chart
from ui.styles import inject_styles
from ui.trades_panel import render_trades_panel
from ws.order_worker import order_ws_worker
from ws.price_worker import price_ws_worker
from ui.top_stocks_view import render_top_stocks

@st.cache_resource
def get_state():
    state = SharedState()
    threading.Thread(target=price_ws_worker, args=(state,), daemon=True).start()
    threading.Thread(target=order_ws_worker,  args=(state,), daemon=True).start()
    return state


st.set_page_config(page_title="DFN Trade Simulator", layout="wide")
st_autorefresh(interval=AUTOREFRESH_MS, key="refresh")

state = get_state()
inject_styles()
inject_right_click_handler()
consume_context_click(state)

# ── HEADER + MARKET STRIP + NAV BAR ──────────────────────────
sym = render_header(state)
render_market_overview(state)
render_nav_bar(state)

# ── MAIN CONTENT ─────────────────────────────────────────────
mode = getattr(state, "view_mode", "MARKET_WATCH")

if mode == "INDEX":
    render_index_view(state)
elif mode == "OHLC_CHART":
    render_ohlc_chart(state)
elif mode == "TOP_STOCKS":
    render_top_stocks(state)
else:
    render_market_watch(state, sym)

# ── POPUP (only on list views) ───────────────────────────────
if mode != "OHLC_CHART":
    maybe_show_equity_popup(state)