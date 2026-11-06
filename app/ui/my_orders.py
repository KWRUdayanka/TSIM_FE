# ui/my_orders.py
import json
import uuid
import streamlit as st
from datetime import datetime
from state import SharedState
from config import BROKER


@st.dialog("Amend Order")
def _amend_dialog(state: SharedState, sym: str):
    # Read the target from session_state (set when ✏️ was clicked)
    order = st.session_state.get("amend_order")
    if not order:
        st.rerun()
        return

    st.write(f"Order ID: **{order['Order ID']}**")
    st.write(f"Side: **{order['Side']}**")
    st.markdown("---")

    new_price = st.number_input(
        "New Price", min_value=0.0, value=order["Price"], step=0.01, format="%.2f"
    )
    new_qty = st.number_input(
        "New Quantity", min_value=1.0, value=float(order["Qty"]), step=1.0
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Submit Amend", type="primary", use_container_width=True):
            _send_amend(state, order, sym, new_qty, new_price)
            st.session_state["amend_order"] = None   # clear target
            st.rerun()
    with col2:
        if st.button("Close", use_container_width=True):
            st.session_state["amend_order"] = None
            st.rerun()


def render_my_orders(state: SharedState, sym: str):
    st.markdown("### My Open Orders")

    with state.lock:
        sym_orders_dict = state.my_open_orders.get(sym, {})
        flat_orders = []
        for price_str, orders in sym_orders_dict.items():
            for o in orders:
                flat_orders.append({
                    "Order ID": o.get("ordId") or "PENDING...",
                    "Side": "BUY" if o.get("side") == "1" else "SELL",
                    "Price": float(price_str),
                    "Qty": int(o.get("qty", 0)),
                    "_reqId": o.get("reqId"),
                })

    if not flat_orders:
        st.info(f"No open orders for {sym}")
        return

    # Header
    hc1, hc2, hc3, hc4, hc5 = st.columns([3, 1, 1, 1, 1])
    hc1.markdown("**Order ID**")
    hc2.markdown("**Side**")
    hc3.markdown("**Price**")
    hc4.markdown("**Qty**")
    hc5.markdown("**Action**")

    st.markdown('<hr style="margin: 5px 0px;">', unsafe_allow_html=True)

    for i, order in enumerate(flat_orders):
        c1, c2, c3, c4, c5 = st.columns([3, 1, 1, 1, 1])
        c1.write(order["Order ID"])
        c2.write(order["Side"])
        c3.write(f"{order['Price']:.2f}")
        c4.write(f"{order['Qty']:,}")

        bcol1, bcol2 = c5.columns(2)

        if bcol1.button("❌", key=f"cancel_{order['_reqId']}", help="Cancel Order"):
            if order["Order ID"] == "PENDING...":
                st.warning("Wait for the order to be acknowledged")
            else:
                _cancel_order(state, order["Order ID"], sym, order["Side"])
                st.rerun()

        if bcol2.button("✏️", key=f"amend_{order['_reqId']}", help="Amend Order"):
            if order["Order ID"] == "PENDING...":
                st.warning("Wait for the order to be acknowledged")
            else:
                # Persist target order → survives the autorefresh rerun
                st.session_state["amend_order"] = order

        st.markdown('<hr style="margin: 2px 0px; opacity: 0.2;">', unsafe_allow_html=True)

    # After rendering the table, check if a dialog should be open
    if st.session_state.get("amend_order"):
        _amend_dialog(state, sym)


def _cancel_order(state, ord_id, sym, side):
    if not state.ws_order:
        st.error("Order WS not connected")
        return
    req = {
        "requestId": str(uuid.uuid4()),
        "action": "CANCEL_ORDER",
        "brokerCode": BROKER,
        "cancel": {
            "origOrdID": ord_id,
            "symbolCode": sym,
            "side": "1" if side == "BUY" else "2",
            "securityExchange": "TDWL",
        },
    }
    try:
        state.ws_order.send(json.dumps(req))
        state.add_history({
            "Time": datetime.now().strftime("%H:%M:%S"),
            "Action": "CANCEL", "Sym": sym,
            "Order ID": ord_id, "Status": "SENT", "Details": "Quick Cancel",
        })
        st.toast(f"CANCEL sent for {ord_id}", icon="✅")
    except Exception as e:
        st.error(f"Cancel failed: {e}")


def _send_amend(state, order, sym, new_qty, new_px):
    if not state.ws_order:
        st.error("Order WS not connected")
        return

    ord_id = order["Order ID"]
    side_code = "1" if order["Side"] == "BUY" else "2"

    req = {
        "requestId": str(uuid.uuid4()),
        "action": "AMEND_ORDER",
        "brokerCode": BROKER,
        "amend": {
            "origOrdID": ord_id,
            "symbolCode": sym,
            "side": side_code,
            "ordType": "2",
            "orderQty": float(new_qty),
            "price": float(new_px),
            "timeInForce": "0",
            "securityExchange": "TDWL",
        },
    }
    try:
        state.ws_order.send(json.dumps(req))
        state.add_history({
            "Time": datetime.now().strftime("%H:%M:%S"),
            "Action": "AMEND", "Sym": sym,
            "Order ID": ord_id, "Status": "SENT",
            "Details": f"Amend to {new_qty} @ {new_px}",
        })
        st.toast(f"AMEND sent for {ord_id}", icon="✅")
    except Exception as e:
        st.error(f"Amend failed: {e}")