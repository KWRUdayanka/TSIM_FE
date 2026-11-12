# ui/history.py
import streamlit as st
from state import SharedState


def render_history(state: SharedState):
    """Renders the execution history table with colour-coded statuses."""
    st.markdown("### Execution History")

    with state.lock:
        history = list(state.history)

    if not history:
        st.info("No orders yet.")
        return

    mode = st.session_state.get("theme_mode", "dark")

    if mode == "dark":
        fills = {
            "rejected": "background-color: #3a1a1a; color: #fca5a5;",
            "filled": "background-color: #1a3a1a; color: #86efac;",
            "expired": "background-color: #3a2a1a; color: #fcd34d;",
            "pending": "background-color: #3a3a1a; color: #fde68a;",
        }
    else:
        fills = {
            "rejected": "background-color: #fde8e8; color: #991b1b;",
            "filled": "background-color: #e6f6ec; color: #14532d;",
            "expired": "background-color: #fef3e0; color: #92400e;",
            "pending": "background-color: #fdf9dc; color: #713f12;",
        }

    def get_row_style(status):
        s = str(status)
        if s in ("REJECTED", "CANCELED"):
            return fills["rejected"]
        if s in ("FILLED", "REPLACED"):
            return fills["filled"]
        if s == "EXPIRED":
            return fills["expired"]
        if s.startswith("PENDING_") or s == "SENT":
            return fills["pending"]
        return ""

    html_rows = ""
    for row in history:
        status = row.get("Status", "")
        row_style = get_row_style(status)

        # Build cell styles
        td_base = "padding:6px 8px;font-family:JetBrains Mono,monospace;font-size:11px;border-bottom:1px solid var(--border-subtle);"

        html_rows += f"<tr style='{row_style}'>"
        html_rows += f"<td style='{td_base}'>{row.get('Time', '')}</td>"
        html_rows += f"<td style='{td_base}'>{row.get('Action', '')}</td>"
        html_rows += f"<td style='{td_base}'>{row.get('Sym', '')}</td>"
        html_rows += f"<td style='{td_base}'>{row.get('Order ID', '')}</td>"
        html_rows += f"<td style='{td_base}'><strong>{status}</strong></td>"
        html_rows += f"<td style='{td_base}'>{row.get('Details', '')}</td>"
        html_rows += "</tr>"

    st.markdown(f"""
    <div style="
        background: var(--bg-1);
        border: 1px solid var(--border-subtle);
        border-radius: 8px;
        max-height: 450px;
        overflow-y: auto;
        font-family: 'JetBrains Mono', monospace;
    ">
        <table style="width:100%;border-collapse:collapse;">
            <thead style="position:sticky;top:0;background:var(--bg-2);z-index:1;">
                <tr style="border-bottom:1px solid var(--border-strong);">
                    <th style="padding:6px 8px;text-align:left;color:var(--text-lo);font-size:11px;font-weight:600;">Time</th>
                    <th style="padding:6px 8px;text-align:left;color:var(--text-lo);font-size:11px;font-weight:600;">Action</th>
                    <th style="padding:6px 8px;text-align:left;color:var(--text-lo);font-size:11px;font-weight:600;">Sym</th>
                    <th style="padding:6px 8px;text-align:left;color:var(--text-lo);font-size:11px;font-weight:600;">Order ID</th>
                    <th style="padding:6px 8px;text-align:left;color:var(--text-lo);font-size:11px;font-weight:600;">Status</th>
                    <th style="padding:6px 8px;text-align:left;color:var(--text-lo);font-size:11px;font-weight:600;">Details</th>
                </tr>
            </thead>
            <tbody>
                {html_rows}
            </tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)