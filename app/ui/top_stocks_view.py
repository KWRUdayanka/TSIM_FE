# ui/top_stocks_view.py
import time

import pandas as pd
import streamlit as st

TT_LABELS = {
    "0": "Gainers · Net Change",
    "1": "Gainers · % Change",
    "2": "Losers · Net Change",
    "3": "Losers · % Change",
    "4": "Gainers · Volume",
    "5": "Gainers · Trades",
    "6": "Gainers · Turnover",
    "7": "Losers · 52-Week Low",
    "8": "Gainers · 52-Week High",
}


def render_top_stocks(state):
    exg = getattr(state, "market_exchange", "TDWL") or "TDWL"
    mkt = "1"

    st.markdown(f"### Top Stocks — {exg}")

    current = getattr(state, "top_stocks_tt", "0")
    labels = list(TT_LABELS.keys())
    idx = labels.index(current) if current in labels else 0
    picked = st.radio(
        "Ranking", labels, index=idx,
        format_func=lambda k: TT_LABELS[k],
        horizontal=True, key="top_stocks_tt_radio",
        label_visibility="collapsed",
    )
    if picked != current:
        state.top_stocks_tt = picked

    snapshot = state.get_top_stocks(exg, picked, mkt)
    entries = snapshot.get("entries") or []
    if not entries:
        st.caption(f"Waiting for Top Stocks type {picked} ({TT_LABELS[picked]})…")
        return

    df = pd.DataFrame([{
        "Symbol": e.get("sym"),
        "Name": e.get("desc"),
        "LTP": e.get("ltp"),
        "Change": e.get("chg"),
        "Change %": e.get("pctChg"),
        "Volume": e.get("vol"),
        "Trades": e.get("trades"),
        "Turnover": e.get("tovr"),
    } for e in entries])

    def _color_change(v):
        try:
            return "color: #26a69a" if float(v) >= 0 else "color: #ef5350"
        except Exception:
            return ""

    styled = (
        df.style
          .format({
              "LTP":      "{:.3f}",
              "Change":   "{:+.3f}",
              "Change %": "{:+.2f}%",
              "Volume":   "{:,}",
              "Trades":   "{:,}",
              "Turnover": "{:,.2f}",
          })
          .map(_color_change, subset=["Change", "Change %"])
    )

    st.dataframe(styled, use_container_width=True, hide_index=True)

    ts = snapshot.get("ts")
    if ts:
        age = (time.time() * 1000 - ts) / 1000
        st.caption(f"Type {picked} · {TT_LABELS[picked]} · "
                   f"{len(entries)} stocks · updated {age:.0f}s ago")