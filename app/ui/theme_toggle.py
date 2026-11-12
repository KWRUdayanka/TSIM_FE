# ui/theme_toggle.py
import streamlit as st


def render_theme_toggle():
    mode = st.session_state.get("theme_mode", "dark")
    label = "☀️ Light" if mode == "dark" else "🌙 Dark"
    if st.button(label, key="theme_toggle_btn", help="Switch theme"):
        st.session_state["theme_mode"] = "light" if mode == "dark" else "dark"
        st.rerun()