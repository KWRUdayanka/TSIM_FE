# ui/market_watch.py
import streamlit as st
from state import SharedState
from ui.order_book import render_order_book
from ui.equity import render_equity
from ui.my_orders import render_my_orders
from ui.history import render_history
from ui.order_entry import render_order_entry
from ui.trades_panel import render_trades_panel

def render_market_watch(state: SharedState, sym: str):
    """Full broker workspace: order book, equity, orders, history."""

    # ── Top row: order book (left) | equity + my orders (right) ──
    left, right = st.columns([1, 1], gap="medium")

    with left:
        with st.container(border=True):
            render_order_book(state, sym)

        with st.container(border=True):
            render_my_orders(state, sym)

    with right:
        with st.container(border=True):
            st.markdown(f"### {sym} · EQUITY")
            render_equity(state, sym)

        with st.container(border=True):
            render_history(state)

    # ── Bottom row: order entry ──────────────────────────────────
    with st.container(border=True):
        render_order_entry(state, sym)

    with st.container(border=True):
        render_trades_panel(state, sym, limit=30)