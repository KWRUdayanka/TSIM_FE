# ui/history.py
import streamlit as st
import pandas as pd
from state import SharedState


def render_history(state: SharedState):
    st.markdown("### Execution History")

    with state.lock:
        history = list(state.history)

    if not history:
        st.info("No orders yet.")
        return

    df = pd.DataFrame(history)
    mode = st.session_state.get("theme_mode", "dark")

    fills_dark = {
        "rejected": "background-color: #3a1a1a",
        "filled":   "background-color: #1a3a1a",
        "expired":  "background-color: #3a2a1a",
        "pending":  "background-color: #3a3a1a",
    }
    fills_light = {
        "rejected": "background-color: #fbeaea",
        "filled":   "background-color: #eaf7ee",
        "expired":  "background-color: #fdf3e3",
        "pending":  "background-color: #f7f4dc",
    }
    fills = fills_dark if mode == "dark" else fills_light

    def _row_style(row):
        s = str(row.get("Status", ""))
        if s in ("REJECTED", "CANCELED"):
            return [fills["rejected"]] * len(row)
        if s in ("FILLED", "REPLACED"):
            return [fills["filled"]] * len(row)
        if s == "EXPIRED":
            return [fills["expired"]] * len(row)
        if s.startswith("PENDING_"):
            return [fills["pending"]] * len(row)
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