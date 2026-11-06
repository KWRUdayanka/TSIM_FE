# ui/equity_popup.py
import streamlit as st
from state import SharedState
from ui.equity import render_equity


@st.dialog("Equity", width="large")
def show_equity_dialog(state: SharedState, symbol: str):
    st.markdown(f"### {symbol} · EQUITY")
    render_equity(state, symbol)

    if st.button("Close", use_container_width=True):
        st.rerun()


def maybe_show_equity_popup(state: SharedState):
    """If state.context_symbol is set, open the dialog and clear the flag."""
    if not state.context_symbol:
        return

    symbol = state.context_symbol
    # Clear before opening (so the dialog doesn't loop after closing)
    state.context_symbol = None

    show_equity_dialog(state, symbol)