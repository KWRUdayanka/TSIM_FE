# main.py — top of file
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
from ui.theme_toggle import render_theme_toggle
from ws.order_worker import order_ws_worker
from ws.price_worker import price_ws_worker
from ui.top_stocks_view import render_top_stocks

st.set_page_config(page_title="DFN Trade Simulator", layout="wide")

if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "dark"

inject_styles()                    # ← single call, after set_page_config

@st.cache_resource
def get_state():
    state = SharedState()
    threading.Thread(target=price_ws_worker, args=(state,), daemon=True).start()
    threading.Thread(target=order_ws_worker,  args=(state,), daemon=True).start()
    return state


st_autorefresh(interval=AUTOREFRESH_MS, key="refresh")

state = get_state()
inject_right_click_handler()
consume_context_click(state)

sym = render_header(state)         # render_header is where the toggle should live
render_market_overview(state)
render_nav_bar(state)

mode = getattr(state, "view_mode", "MARKET_WATCH")

if mode == "INDEX":
    render_index_view(state)
elif mode == "OHLC_CHART":
    render_ohlc_chart(state)
elif mode == "TOP_STOCKS":
    render_top_stocks(state)
else:
    render_market_watch(state, sym)

if mode != "OHLC_CHART":
    maybe_show_equity_popup(state)