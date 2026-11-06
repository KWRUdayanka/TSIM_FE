# ui/index_view.py
import streamlit as st
from state import SharedState
from ui.index_panel import render_index


def render_index_view(state: SharedState):
    """Index-only view. No equity, no order book, no orders."""

    # Show one or more indices — add to the list as you subscribe more
    INDEX_SYMBOLS = ["TASI"]

    # Full-width index panel(s). If more than one, split columns.
    if len(INDEX_SYMBOLS) == 1:
        with st.container(border=True):
            render_index(state, INDEX_SYMBOLS[0])
    else:
        cols = st.columns(len(INDEX_SYMBOLS))
        for col, idx_sym in zip(cols, INDEX_SYMBOLS):
            with col:
                with st.container(border=True):
                    st.markdown(f"### {idx_sym} — INDEX")
                    render_index(state, idx_sym)