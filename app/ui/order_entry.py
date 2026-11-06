# ui/order_entry.py
import json
import uuid
import datetime
import streamlit as st
from state import SharedState
from config import BROKER

TIF_MAP = {"DAY": "0", "GTC": "1", "IOC": "3", "FOK": "4", "GTD": "6"}


def render_order_entry(state: SharedState, default_sym: str):
    st.markdown('<hr style="margin: 10px 0px;">', unsafe_allow_html=True)
    st.markdown("### Order Entry")

    o1, o2, o3, o4, o5, o6, o7, o8 = st.columns([2, 1, 1, 1, 1, 1, 1, 2])

    with o1:
        ord_sym = st.text_input("Symbol", value=default_sym, key="ord_sym",
                                label_visibility="collapsed", placeholder="Symbol")
    with o2:
        ord_side = st.selectbox("Side", ["BUY", "SELL"],
                                key="ord_side", label_visibility="collapsed")
    with o3:
        ord_qty = st.number_input("Qty", min_value=1.0, value=100.0, step=1.0,
                                  key="ord_qty", label_visibility="collapsed")

    # ── Order type is rendered BEFORE price so we know whether to show price ──
    with o5:
        ord_type = st.selectbox("Type", ["LIMIT", "MARKET"],
                                key="ord_type", label_visibility="collapsed")

    is_market = ord_type == "MARKET"

    # ── Price field: shown and editable for LIMIT, hidden for MARKET ──
    with o4:
        if is_market:
            # Disabled placeholder keeps the column width and shows "—"
            st.text_input("Price", value="—", disabled=True,
                          key="ord_px_disabled", label_visibility="collapsed")
            ord_px = 0.0
        else:
            ord_px = st.number_input("Price", min_value=0.0, value=12.50,
                                     step=0.01, format="%.2f",
                                     key="ord_px", label_visibility="collapsed")

    with o6:
        tif_label = st.selectbox("TIF", list(TIF_MAP.keys()),
                                 key="ord_tif", label_visibility="collapsed")

    with o7:
        expire_date = None
        if tif_label == "GTD":
            expire_date = st.date_input(
                "Expiry",
                value=datetime.date.today() + datetime.timedelta(days=1),
                min_value=datetime.date.today(),
                label_visibility="collapsed",
                key="gtd_expire",
            )
        else:
            st.write("&nbsp;", unsafe_allow_html=True)

    with o8:
        if st.button("Send New Order", use_container_width=True, type="primary"):
            _send_new_order(
                state, ord_sym, ord_side, ord_qty, ord_px,
                ord_type, tif_label, expire_date
            )


def _side_code(side_label):
    return "1" if side_label == "BUY" else "2"


def _send_new_order(state, sym, side, qty, px, ord_type, tif_label, expire_date):
    if not state.ws_order:
        st.error("Order WS not connected")
        return

    tif_code = TIF_MAP.get(tif_label)
    if tif_code is None:
        st.error(f"Unknown TIF: {tif_label}")
        return

    if tif_code == "6" and expire_date is None:
        st.error("GTD orders require an expiry date")
        return

    req_id = str(uuid.uuid4())
    order_payload = {
        "symbolCode": sym,
        "side": _side_code(side),
        "ordType": "2" if ord_type == "LIMIT" else "1",
        "orderQty": float(qty),
        "timeInForce": tif_code,
        "securityExchange": "TDWL",
    }
    if ord_type == "LIMIT":
        order_payload["price"] = float(px)
    if tif_code == "6":
        order_payload["expireDate"] = expire_date.isoformat()

    req = {
        "requestId": req_id,
        "action": "NEW_ORDER",
        "brokerCode": BROKER,
        "order": order_payload,
    }

    try:
        state.ws_order.send(json.dumps(req))
        state.add_my_order(sym, px, _side_code(side), qty, req_id)

        toast_msg = (
            f"MARKET {side} {qty} {sym} [{tif_label}]"
            if ord_type == "MARKET"
            else f"LIMIT {side} {qty} {sym} @ {px} [{tif_label}]"
        )

        state.add_history({
            "Time": datetime.datetime.now().strftime("%H:%M:%S"),
            "Action": "NEW_ORDER",
            "Sym": sym,
            "Order ID": "",
            "Status": "SENT",
            "Details": toast_msg,
        })
        st.toast(toast_msg, icon="✅")
    except Exception as e:
        st.error(f"Send failed: {e}")