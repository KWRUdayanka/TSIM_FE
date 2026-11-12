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

    rows = []
    for t in trades:
        side = t.get("tradeType", "")
        side_label = "BUY" if side == "B" else ("SELL" if side == "S" else "—")

        tts = t.get("tradeTime", "")   # "082522" from feed
        time_str = f"{tts[0:2]}:{tts[2:4]}:{tts[4:6]}" if len(tts) == 6 else tts

        rows.append({
            "Time": time_str,
            "Side": side_label,
            "Price": float(t.get("price", 0)),
            "Qty": int(t.get("quantity", 0)),
            "Seq": t.get("seq", ""),
        })

    html_rows = "".join(
        f'<tr>'
        f'<td style="padding:2px 8px;color:var(--text-mid);'
        f'font-family:JetBrains Mono,monospace;font-size:11px;">{r["Time"]}</td>'
        f'<td style="padding:2px 8px;text-align:center;'
        f'color:var(--green) if BUY else var(--red);'  # placeholder, replaced below
        f'</td>'
        f'</tr>'
        for r in rows
    )
    # The f-string above cannot branch on a value inside a style attribute, so
    # build the row with a real conditional on each cell's color.
    html_rows = "".join(
        f'<tr>'
        f'<td style="padding:2px 8px;color:var(--text-mid);'
        f'font-family:JetBrains Mono,monospace;font-size:11px;">{r["Time"]}</td>'
        f'<td style="padding:2px 8px;text-align:center;'
        f'color:{ "var(--green)" if r["Side"]=="BUY" else ("var(--red)" if r["Side"]=="SELL" else "var(--text-mid)") };'
        f'font-family:JetBrains Mono,monospace;font-size:11px;font-weight:600;">{r["Side"]}</td>'
        f'<td style="padding:2px 8px;text-align:right;color:var(--text-hi);'
        f'font-family:JetBrains Mono,monospace;font-size:11px;">{r["Price"]:.2f}</td>'
        f'<td style="padding:2px 8px;text-align:right;color:var(--accent);'
        f'font-family:JetBrains Mono,monospace;font-size:11px;">{r["Qty"]:,}</td>'
        f'<td style="padding:2px 8px;text-align:right;color:var(--text-lo);'
        f'font-family:JetBrains Mono,monospace;font-size:10px;">{r["Seq"]}</td>'
        f'</tr>'
        for r in rows
    )

    st.markdown(f"""
    <div style="
        background: var(--bg-1);
        border: 1px solid var(--border-subtle);
        border-radius: 8px;
        max-height: 400px;
        overflow-y: auto;
        font-family: 'JetBrains Mono', monospace;
    ">
        <table style="width:100%;border-collapse:collapse;">
            <thead>
                <tr style="border-bottom:1px solid var(--border-strong);">
                    <th style="padding:6px 8px;text-align:left;color:var(--text-lo);font-size:10px;font-weight:600;">TIME</th>
                    <th style="padding:6px 8px;text-align:center;color:var(--text-lo);font-size:10px;font-weight:600;">SIDE</th>
                    <th style="padding:6px 8px;text-align:right;color:var(--text-lo);font-size:10px;font-weight:600;">PRICE</th>
                    <th style="padding:6px 8px;text-align:right;color:var(--text-lo);font-size:10px;font-weight:600;">QTY</th>
                    <th style="padding:6px 8px;text-align:right;color:var(--text-lo);font-size:10px;font-weight:600;">SEQ</th>
                </tr>
            </thead>
            <tbody>
                {html_rows}
            </tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)