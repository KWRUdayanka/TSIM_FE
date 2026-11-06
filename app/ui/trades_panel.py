# ui/trades_panel.py
import streamlit as st
from state import SharedState


def render_trades_panel(state: SharedState, sym: str, limit: int = 30):
    """Recent trades table for the current symbol."""
    st.markdown(f"### Recent Trades · {sym}")

    trades = state.get_trades(sym, limit)

    if not trades:
        st.info(f"No trades for {sym} yet.")
        return

    # Build display rows
    rows = []
    for t in trades:
        side = t.get("tradeType", "")
        side_label = "BUY" if side == "B" else ("SELL" if side == "S" else "—")
        side_colour = "#4ade80" if side == "B" else ("#f87171" if side == "S" else "#a0aec0")

        tts = t.get("tradeTime", "")   # "082522" from feed
        time_str = f"{tts[0:2]}:{tts[2:4]}:{tts[4:6]}" if len(tts) == 6 else tts

        rows.append({
            "Time": time_str,
            "Side": side_label,
            "Price": float(t.get("price", 0)),
            "Qty": int(t.get("quantity", 0)),
            "Seq": t.get("seq", ""),
        })

    # Colour-coded table via HTML for side coloring
    html_rows = "".join(
        f'<tr>'
        f'<td style="padding:2px 8px;color:#a0aec0;font-family:JetBrains Mono,monospace;font-size:11px;">{r["Time"]}</td>'
        f'<td style="padding:2px 8px;text-align:center;'
        f'color:{"#4ade80" if r["Side"]=="BUY" else "#f87171"};'
        f'font-family:JetBrains Mono,monospace;font-size:11px;font-weight:600;">{r["Side"]}</td>'
        f'<td style="padding:2px 8px;text-align:right;color:#e6ecf2;'
        f'font-family:JetBrains Mono,monospace;font-size:11px;">{r["Price"]:.2f}</td>'
        f'<td style="padding:2px 8px;text-align:right;color:#6cb6ff;'
        f'font-family:JetBrains Mono,monospace;font-size:11px;">{r["Qty"]:,}</td>'
        f'<td style="padding:2px 8px;text-align:right;color:#5c6b7f;'
        f'font-family:JetBrains Mono,monospace;font-size:10px;">{r["Seq"]}</td>'
        f'</tr>'
        for r in rows
    )

    st.markdown(f"""
    <div style="
        background: #0d1219;
        border: 1px solid rgba(120,160,210,0.12);
        border-radius: 8px;
        max-height: 400px;
        overflow-y: auto;
        font-family: 'JetBrains Mono', monospace;
    ">
        <table style="width:100%;border-collapse:collapse;">
            <thead>
                <tr style="border-bottom:1px solid rgba(120,160,210,0.15);">
                    <th style="padding:6px 8px;text-align:left;color:#5c6b7f;font-size:10px;font-weight:600;">TIME</th>
                    <th style="padding:6px 8px;text-align:center;color:#5c6b7f;font-size:10px;font-weight:600;">SIDE</th>
                    <th style="padding:6px 8px;text-align:right;color:#5c6b7f;font-size:10px;font-weight:600;">PRICE</th>
                    <th style="padding:6px 8px;text-align:right;color:#5c6b7f;font-size:10px;font-weight:600;">QTY</th>
                    <th style="padding:6px 8px;text-align:right;color:#5c6b7f;font-size:10px;font-weight:600;">SEQ</th>
                </tr>
            </thead>
            <tbody>
                {html_rows}
            </tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)