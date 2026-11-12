# ui/ohlc_chart.py
"""Candlestick chart view — 1m / 5m / 1h from raw OHLC ticks in SharedState."""
import json

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from config import OHLC_TFS

_TF_LABELS = list(OHLC_TFS.keys())


def render_ohlc_chart(state):
    if not hasattr(state, "get_ohlc_series"):
        st.error("OHLC methods missing on SharedState. Restart Streamlit.")
        return

    sym = getattr(state, "chart_symbol", None) or getattr(state, "current_symbol", None)
    if not sym:
        st.info("Select a symbol (right-click any row) to open its chart.")
        return

    if getattr(state, "chart_symbol", None) != sym:
        state.chart_symbol = sym

    _ensure_ohlc_subscription(state, sym)

    # ---- header + timeframe selector ----
    left, right = st.columns([3, 1])
    with left:
        st.markdown(f"### {sym} — Candles")

    with right:
        current_tf = getattr(state, "ohlc_current_tf", "1m")
        idx = _TF_LABELS.index(current_tf) if current_tf in _TF_LABELS else 0
        picked_tf = st.radio(
            "TF", _TF_LABELS, index=idx, horizontal=True,
            key=f"tf_{sym}", label_visibility="collapsed",
        )
    if picked_tf != current_tf:
        state.set_ohlc_tf(picked_tf)

    if st.session_state.get("ohlc_show_diag", False):
        _render_diagnostics(state, sym)

    candles = state.get_ohlc_series(sym, picked_tf)
    if not candles:
        ticks = state.get_ohlc_ticks(sym)
        st.caption(
            f"Waiting for OHLC ticks…  "
            f"(raw ticks stored: {len(ticks)}, "
            f"cache keys: {list(state.ohlc_cache.keys()) or '[]'})"
        )
        return

    _render_candles(candles, sym)
    _render_ohlc_footer(candles)


# --------------------------------------------------------------------------- #
def _ensure_ohlc_subscription(state, sym):
    ws = getattr(state, "ws_price", None)
    if ws is None:
        return
    with state.lock:
        already = sym in state.subscribed_symbols
    if already:
        return
    try:
        ws.send(json.dumps({
            "action": "SUBSCRIBE",
            "symbols": [sym],
            "exchange": state.market_exchange or "TDWL",
        }))
        with state.lock:
            state.subscribed_symbols.add(sym)
        print(f"[CHART-SUB] subscribed {sym}")
    except Exception as e:
        print(f"[CHART-SUB] failed for {sym}: {e}")


# --------------------------------------------------------------------------- #
def _render_candles(candles, sym):
    df = pd.DataFrame([{
        "time":   pd.to_datetime(c.time, unit="ms"),
        "open":   float(c.open),
        "high":   float(c.high),
        "low":    float(c.low),
        "close":  float(c.close),
        "volume": float(c.volume),
    } for c in candles]).sort_values("time").reset_index(drop=True)

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.78, 0.22],
    )

    # ---- candles (row 1) ----
    fig.add_trace(go.Candlestick(
        x=df["time"],
        open=df["open"], high=df["high"], low=df["low"], close=df["close"],
        name=sym,
        increasing_line_color="#26a69a", increasing_fillcolor="#26a69a",
        decreasing_line_color="#ef5350", decreasing_fillcolor="#ef5350",
        showlegend=False,
    ), row=1, col=1)

    # ---- volume (row 2) ----
    bar_colors = [
        "rgba(38,166,154,1.0)" if c >= o else "rgba(239,83,80,1.0)"
        for c, o in zip(df["close"], df["open"])
    ]
    fig.add_trace(go.Bar(
        x=df["time"], y=df["volume"],
        marker_color=bar_colors,
        name="Volume",
        opacity=0.6,
        showlegend=False,
    ), row=2, col=1)

    # ---- THEME-AWARE COLORS ----
    mode = st.session_state.get("theme_mode", "dark")
    if mode == "dark":
        bg_color       = "#131722"
        grid_color     = "#2a2e39"
        text_color     = "#d1d4dc"
        line_color     = "#2a2e39"
    else:
        bg_color       = "#ffffff"
        grid_color     = "rgba(0,0,0,0.08)"
        text_color     = "#0f1720"
        line_color     = "rgba(0,0,0,0.15)"

    fig.update_layout(
        height=560,
        margin=dict(l=10, r=10, t=20, b=10),
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        font=dict(color=text_color),
        dragmode="pan",
        hovermode="x unified",
        bargap=0.15,
    )
    fig.update_xaxes(
        gridcolor=grid_color,
        linecolor=line_color,
        rangeslider=dict(visible=False),
        showspikes=False,
    )
    fig.update_yaxes(gridcolor=grid_color, linecolor=line_color, side="right", row=1, col=1)
    fig.update_yaxes(showgrid=False, showticklabels=False, side="right", row=2, col=1)

    # candle y-range — include open/close so nothing is clipped
    if len(df):
        lo = min(df["low"].min(),  df["open"].min(),  df["close"].min())
        hi = max(df["high"].max(), df["open"].max(), df["close"].max())
        pad = max((hi - lo) * 0.05, hi * 0.0005, 1e-6)
        fig.update_yaxes(range=[lo - pad, hi + pad], row=1, col=1)

    # volume y-range — always give the strip space
    vol_max = df["volume"].max() if len(df) else 0
    fig.update_yaxes(range=[0, vol_max * 1.1 if vol_max > 0 else 1.0], row=2, col=1)

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displaylogo": False, "scrollZoom": False},
        key=f"ohlc_chart_{sym}_{mode}",   # <- include mode in key so Plotly remounts on toggle
    )


def _render_ohlc_footer(candles):
    last = candles[-1]
    prev_close = candles[-2].close if len(candles) > 1 else None

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Open",  f"{last.open:.2f}")
    c2.metric("High",  f"{last.high:.2f}")
    c3.metric("Low",   f"{last.low:.2f}")
    c4.metric(
        "Close",
        f"{last.close:.2f}",
        delta=f"{last.close - prev_close:+.2f}" if prev_close is not None else None,
    )


# --------------------------------------------------------------------------- #
def _render_diagnostics(state, sym):
    with st.expander("🔧 OHLC diagnostics", expanded=True):
        ticks = state.get_ohlc_ticks(sym)
        counts = [len(state.get_ohlc_series(sym, tf)) for tf in _TF_LABELS]

        st.write("**symbol:**", sym)
        st.write("**context_symbol:**", getattr(state, "context_symbol", None))
        st.write("**chart_symbol:**", getattr(state, "chart_symbol", None))
        st.write("**subscribed_symbols:**", list(state.subscribed_symbols))
        st.write("**ohlc_cache keys:**", list(state.ohlc_cache.keys()))
        st.write("**raw tick count for this symbol:**", len(ticks))
        st.write("**1m / 5m / 1h candle counts:**", counts)

        if ticks:
            st.write("**first tick:**", ticks[0].__dict__)
            st.write("**last tick:**", ticks[-1].__dict__)
            import time as _t
            age = (_t.time() * 1000 - ticks[-1].ts) / 1000
            st.write("**last tick age (s):**", round(age, 1))

        series = state.get_ohlc_series(sym, state.ohlc_current_tf)
        if series:
            st.write("**last candle:**", series[-1].__dict__)