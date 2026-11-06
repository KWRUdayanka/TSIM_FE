# ui/history.py
import streamlit as st
import pandas as pd
from state import SharedState


def render_history(state: SharedState):
    """Renders the execution history table with colour-coded statuses."""
    st.markdown("### Execution History")

    with state.lock:
        history = list(state.history)

    if not history:
        st.info("No orders yet.")
        return

    df = pd.DataFrame(history)

    def _row_style(row):
        s = str(row.get("Status", ""))
        if s in ("REJECTED", "CANCELED"):
            return ["background-color: #3a1a1a"] * len(row)
        if s in ("FILLED", "REPLACED"):
            return ["background-color: #1a3a1a"] * len(row)
        if s == "EXPIRED":
            return ["background-color: #3a2a1a"] * len(row)
        if s.startswith("PENDING_"):
            return ["background-color: #3a3a1a"] * len(row)
        return [""] * len(row)

    styled = df.style.apply(_row_style, axis=1)

    st.dataframe(
        styled,
        column_config={
            "Time":     st.column_config.TextColumn(width="small"),
            "Action":   st.column_config.TextColumn(width="medium"),
            "Sym":      st.column_config.TextColumn(width="small"),
            "Order ID": st.column_config.TextColumn(width="medium"),
            "Status":   st.column_config.TextColumn(width="medium"),
            "Details":  st.column_config.TextColumn(width="large"),
        },
        use_container_width=True,
        hide_index=True,
        height=450,
    )