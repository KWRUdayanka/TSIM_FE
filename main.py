import json
import threading
import time
import urllib.request
import websocket
import uuid
from datetime import datetime

import streamlit as st
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURATION ---
BASE_URL = "http://localhost:8092/dfn"
WS_PRICE = "ws://localhost:8092/dfn/ws/price"
WS_ORDER = "ws://localhost:8092/dfn/ws/dfn-tsim"
API_KEY = "broker01-key"
API_SECRET = "broker01-secret"
BROKER = "BROKER01"

DEFAULT_SYMBOL = "1010"
DEPTH = 15


# ---------------- TOKEN FETCHER ----------------
def get_tokens():
    data = json.dumps({"apiKey": API_KEY, "apiSecret": API_SECRET}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/api/auth/login", data=data, method='POST')
    req.add_header('Content-Type', 'application/json')
    req.add_header('X-Forwarded-For', '127.0.0.1')
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            return result.get("orderToken"), result.get("priceToken")
    except Exception as e:
        print(f"Failed to fetch token: {e}")
        return None, None


# ---------------- SHARED STATE ----------------
class SharedState:
    def __init__(self):
        self.lock = threading.Lock()
        self.book_cache = {}
        self.my_open_orders = {}
        self.history = []
        self.status = "Starting…"
        self.ws_price = None
        self.ws_order = None
        self.subscribed_symbols = set()
        self.current_symbol = DEFAULT_SYMBOL
        self.stop_event = threading.Event()
        self.threads_started = False

    def set_status(self, s):
        with self.lock: self.status = s

    def get_status(self):
        with self.lock: return self.status

    def update_book(self, sym, bids, asks, ts):
        with self.lock:
            self.book_cache[sym] = {"bids": bids, "asks": asks, "timestamp": ts}

    def add_history(self, entry):
        with self.lock:
            self.history.insert(0, entry)
            self.history = self.history[:300]

    def add_my_order(self, sym, price, side, qty, req_id):
        price_key = f"{float(price):.2f}"
        with self.lock:
            self.my_open_orders.setdefault(sym, {}).setdefault(price_key, []).append({
                "side": side, "qty": qty, "reqId": req_id, "ordId": None
            })

    def remove_order(self, sym, target):
        if not target: return
        with self.lock:
            if sym not in self.my_open_orders: return
            for px_key, orders in list(self.my_open_orders[sym].items()):
                kept = []
                for o in orders:
                    oid = str(o.get("ordId") or "").strip()
                    rid = str(o.get("reqId") or "").strip()
                    if target != oid and target != rid:
                        kept.append(o)
                if kept:
                    self.my_open_orders[sym][px_key] = kept
                else:
                    del self.my_open_orders[sym][px_key]

    def snapshot(self, sym):
        with self.lock:
            book = self.book_cache.get(sym, {"bids": [], "asks": [], "timestamp": ""})
            orders = dict(self.my_open_orders.get(sym, {}))
        return book, orders


@st.cache_resource
def get_state():
    state = SharedState()
    threading.Thread(target=price_ws_worker, args=(state,), daemon=True).start()
    threading.Thread(target=order_ws_worker, args=(state,), daemon=True).start()
    state.threads_started = True
    return state


# ---------------- BACKGROUND WEBSOCKET WORKERS ----------------
def price_ws_worker(state: SharedState):
    while not state.stop_event.is_set():
        try:
            state.set_status("Fetching price token…")
            _, price_token = get_tokens()
            if not price_token:
                raise Exception("No price token")

            state.set_status("Connecting Price WS…")
            ws = websocket.create_connection(WS_PRICE, timeout=None)
            state.ws_price = ws

            ws.send(json.dumps({"action": "AUTH", "brokerCode": BROKER, "token": price_token}))

            while not state.stop_event.is_set():
                raw = ws.recv()
                if not raw: raise ConnectionError("closed")
                msg = json.loads(raw)

                if msg.get("action") == "AUTH":
                    if not msg.get("success"):
                        state.set_status("Price AUTH failed")
                        break
                    state.subscribed_symbols.clear()
                    state.book_cache.clear()
                    if state.current_symbol:
                        ws.send(json.dumps({"action": "SUBSCRIBE", "symbols": [state.current_symbol]}))
                        state.subscribed_symbols.add(state.current_symbol)

                if msg.get("action") == "ORDER_BOOK":
                    state.update_book(
                        msg.get("symbol"),
                        msg.get("bids", []),
                        msg.get("asks", []),
                        msg.get("timestamp", ""),
                    )
                    state.set_status("Live")

        except Exception as e:
            state.set_status(f"Price WS Error: {e}")
        time.sleep(3)


def order_ws_worker(state: SharedState):
    while not state.stop_event.is_set():
        try:
            order_token, _ = get_tokens()
            if not order_token:
                raise Exception("No order token")

            ws = websocket.create_connection(WS_ORDER, timeout=None)
            state.ws_order = ws

            ws.send(json.dumps({"action": "AUTH", "brokerCode": BROKER, "token": order_token}))

            while not state.stop_event.is_set():
                raw = ws.recv()
                if not raw: raise ConnectionError("closed")
                msg = json.loads(raw)

                if msg.get("action") == "AUTH":
                    if not msg.get("success"):
                        state.set_status("Order AUTH failed")
                        break
                    continue

                process_order_msg(state, msg)

        except Exception as e:
            state.set_status(f"Order WS Error: {e}")
        time.sleep(3)


def process_order_msg(state: SharedState, msg: dict):
    fix = msg.get("fix", {})
    if not fix: return

    ord_id = str(fix.get("ordId", "")).strip()
    orig_ord_id = str(fix.get("origOrdId", "")).strip()
    status = fix.get("ordStatus", "")
    text = fix.get("text", "")
    sym = fix.get("symbol", "")
    req_id = str(msg.get("requestId", "")).strip()

    if ord_id and status in ["PENDING_NEW", "QUEUED", "PARTIALLY_FILLED", "REPLACED"]:
        with state.lock:
            if sym in state.my_open_orders:
                for px_key, orders in state.my_open_orders[sym].items():
                    for o in orders:
                        if str(o.get("reqId")).strip() == req_id:
                            o["ordId"] = ord_id

    if status in ["CANCELED", "FILLED", "REJECTED"]:
        if status == "CANCELED":
            target = ord_id or orig_ord_id
        elif status == "REJECTED":
            target = ord_id or req_id
        else:
            target = ord_id
        state.remove_order(sym, target)

    action = msg.get("action") or {
        "CANCELED": "CANCEL_ORDER", "FILLED": "FILLED",
        "REJECTED": "REJECTED", "REPLACED": "REPLACE_ORDER",
    }.get(status, "EXEC_REPORT")

    display_id = ord_id or orig_ord_id
    state.add_history({
        "Time": datetime.now().strftime("%H:%M:%S"),
        "Action": action,
        "Sym": sym,
        "Order ID": display_id,
        "Status": status,
        "Details": text,
    })


# ---------------- STREAMLIT PAGE ----------------
st.set_page_config(page_title="DFN Trade Simulator", layout="wide")
st_autorefresh(interval=500, key="refresh")

state = get_state()

# --- CSS: Force screen fit, no scroll, dark theme ---
st.markdown("""
<style>
    /* 1. Hide the default Streamlit header/footer to maximize space */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}

    /* 2. Make the app container exactly 100vh (viewport height) and hide overflow */
    html, body, [data-testid="stAppViewContainer"] {
        height: 100vh !important;
        overflow: hidden !important;
    }
    [data-testid="stVerticalBlock"] {
        height: 100% !important;
    }

    /* 3. Tighten padding for a compact layout */
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
    }

    /* 4. Colors and fonts */
    .stApp { background: #0f1419; }
    h1, h2, h3, h4 { color: #6cb6ff !important; margin-bottom: 0px !important; }
    .book-header { color: #6cb6ff; font-size: 22px; font-weight: bold; margin-bottom: 0px; }
    .spread { color: #fcc419; font-family: monospace; font-size: 13px; margin-bottom: 8px; }
    .status-dim { color: #778; font-family: monospace; font-size: 12px; }
    .status-live { color: #51cf66; font-family: monospace; font-size: 12px; }

    /* Order book row styles */
    .bid { color: #51cf66; font-family: monospace; font-size: 13px; text-align: right; margin: 0px; padding: 0px; }
    .ask { color: #ff6b6b; font-family: monospace; font-size: 13px; text-align: left; margin: 0px; padding: 0px; }
    .my-order { color: #fcc419 !important; font-weight: bold; font-family: monospace; font-size: 13px; margin: 0px; padding: 0px; }
    .col-header { color: #778; font-size: 11px; font-weight: 600; text-transform: uppercase; margin-bottom: 2px;}

    /* Compact form fields */
    .stTextInput > div > div > input { padding-top: 2px; padding-bottom: 2px; }
    .stNumberInput > div > div > input { padding-top: 2px; padding-bottom: 2px; }
</style>
""", unsafe_allow_html=True)

# --- Header Row (Symbol Loader + Status) ---
hcol1, hcol2, hcol3 = st.columns([2, 1, 2])
with hcol1:
    new_sym = st.text_input("Symbol", value=state.current_symbol, key="sym_input", label_visibility="collapsed")
with hcol2:
    if st.button("Load Book", use_container_width=True):
        sym = new_sym.strip()
        if sym:
            state.current_symbol = sym
            if sym not in state.subscribed_symbols and state.ws_price:
                try:
                    state.ws_price.send(json.dumps({"action": "SUBSCRIBE", "symbols": [sym]}))
                    state.subscribed_symbols.add(sym)
                except Exception:
                    pass
with hcol3:
    status = state.get_status()
    cls = "status-live" if status == "Live" else "status-dim"
    st.markdown(f'<div style="text-align:right; padding-top:8px;"><span class="{cls}">● {status}</span></div>',
                unsafe_allow_html=True)

sym = state.current_symbol

# --- Main Split: Book (Left) + History (Right) ---
left_col, right_col = st.columns([1, 2], gap="medium")

# =============== ORDER BOOK ===============
with left_col:
    st.markdown(f'<div class="book-header">{sym}</div>', unsafe_allow_html=True)

    book, my_orders = state.snapshot(sym)
    bids = book["bids"][:DEPTH]
    asks = book["asks"][:DEPTH]

    if bids and asks:
        spread = asks[0]["price"] - bids[0]["price"]
        st.markdown(f'<div class="spread">spread {spread:.3f}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="spread">—</div>', unsafe_allow_html=True)

    h1, h2, h3, h4 = st.columns(4)
    h1.markdown('<div class="col-header">Bid Qty</div>', unsafe_allow_html=True)
    h2.markdown('<div class="col-header" style="text-align:right;">Bid</div>', unsafe_allow_html=True)
    h3.markdown('<div class="col-header">Ask</div>', unsafe_allow_html=True)
    h4.markdown('<div class="col-header" style="text-align:right;">Ask Qty</div>', unsafe_allow_html=True)

    rows = max(len(bids), len(asks))
    for i in range(rows):
        b = bids[i] if i < len(bids) else {}
        a = asks[i] if i < len(asks) else {}
        b_px = b.get("price")
        a_px = a.get("price")
        b_key = f"{float(b_px):.2f}" if b_px is not None else None
        a_key = f"{float(a_px):.2f}" if a_px is not None else None

        b_qty = f"{int(b['qty']):,}" if b.get("qty") is not None else ""
        a_qty = f"{int(a['qty']):,}" if a.get("qty") is not None else ""

        c1, c2, c3, c4 = st.columns(4)
        b_cls = "my-order" if b_key in my_orders else "bid"
        a_cls = "my-order" if a_key in my_orders else "ask"

        c1.markdown(f'<div class="{b_cls}" style="text-align:left;">{"● " if b_key in my_orders else ""}{b_qty}</div>',
                    unsafe_allow_html=True)
        c2.markdown(f'<div class="bid" style="text-align:right;">{f"{b_px:.2f}" if b_px else ""}</div>',
                    unsafe_allow_html=True)
        c3.markdown(f'<div class="ask" style="text-align:left;">{f"{a_px:.2f}" if a_px else ""}</div>',
                    unsafe_allow_html=True)
        c4.markdown(f'<div class="{a_cls}" style="text-align:right;">{a_qty}{" ●" if a_key in my_orders else ""}</div>',
                    unsafe_allow_html=True)

# =============== EXECUTION HISTORY ===============
with right_col:
    st.markdown("### Execution History")
    with state.lock:
        history = list(state.history)

    if history:
        st.dataframe(
            history,
            column_config={
                "Time": st.column_config.TextColumn(width="small"),
                "Action": st.column_config.TextColumn(width="medium"),
                "Sym": st.column_config.TextColumn(width="small"),
                "Order ID": st.column_config.TextColumn(width="medium"),
                "Status": st.column_config.TextColumn(width="medium"),
                "Details": st.column_config.TextColumn(width="large"),
            },
            use_container_width=True,
            hide_index=True,
            height=450,  # <-- Fixed height so it doesn't push the bottom widget off-screen
        )
    else:
        st.info("No orders yet.")

# =============== ORDER ENTRY (Pinned Bottom) ===============
st.markdown('<hr style="margin: 10px 0px;">', unsafe_allow_html=True)

# Row 1: New Order
o1, o2, o3, o4, o5, o6 = st.columns([2, 1, 1, 1, 1, 2])
with o1:
    ord_sym = st.text_input("Symbol ", value=sym, key="ord_sym", label_visibility="collapsed")
with o2:
    ord_side = st.selectbox("Side", ["BUY", "SELL"], label_visibility="collapsed")
with o3:
    ord_qty = st.number_input("Qty", min_value=1.0, value=100.0, step=1.0, label_visibility="collapsed")
with o4:
    ord_px = st.number_input("Price", min_value=0.0, value=12.50, step=0.01, format="%.2f",
                             label_visibility="collapsed")
with o5:
    ord_type = st.selectbox("Type", ["LIMIT", "MARKET"], label_visibility="collapsed")
with o6:
    if st.button("Send New Order", use_container_width=True, type="primary"):
        if state.ws_order:
            side_code = "1" if ord_side == "BUY" else "2"
            req_id = str(uuid.uuid4())
            req = {
                "requestId": req_id, "action": "NEW_ORDER", "brokerCode": BROKER,
                "order": {
                    "symbolCode": ord_sym, "side": side_code, "ordType": "2" if ord_type == "LIMIT" else "1",
                    "orderQty": float(ord_qty), "price": float(ord_px), "timeInForce": "0",
                    "securityExchange": "TDWL",
                }
            }
            try:
                state.ws_order.send(json.dumps(req))
                state.add_my_order(ord_sym, ord_px, side_code, ord_qty, req_id)
                state.add_history(
                    {"Time": datetime.now().strftime("%H:%M:%S"), "Action": "NEW_ORDER", "Sym": ord_sym, "Order ID": "",
                     "Status": "SENT", "Details": "Request Sent"})
                st.toast(f"NEW_ORDER sent: {ord_sym} {ord_side} {ord_qty} @ {ord_px}", icon="✅")
            except Exception as e:
                st.error(f"Send failed: {e}")
        else:
            st.error("Order WS not connected")

# Row 2: Amend / Cancel
a1, a2, a3, a4 = st.columns([2, 1, 1, 4])
with a1:
    ordid = st.text_input("Order ID (ordId)", key="ordid", placeholder="Order ID (ordId)", label_visibility="collapsed")
with a2:
    if st.button("Amend", use_container_width=True):
        if state.ws_order and ordid:
            side_code = "1" if ord_side == "BUY" else "2"
            req = {
                "requestId": str(uuid.uuid4()), "action": "AMEND_ORDER", "brokerCode": BROKER,
                "amend": {
                    "origOrdID": ordid, "symbolCode": ord_sym, "side": side_code, "ordType": "2",
                    "orderQty": float(ord_qty), "price": float(ord_px), "timeInForce": "0",
                    "securityExchange": "TDWL",
                },
            }
            try:
                state.ws_order.send(json.dumps(req))
                state.add_history(
                    {"Time": datetime.now().strftime("%H:%M:%S"), "Action": "AMEND", "Sym": ord_sym, "Order ID": ordid,
                     "Status": "SENT", "Details": "Request Sent"})
                st.toast(f"AMEND_ORDER sent: {ordid}", icon="✅")
            except Exception as e:
                st.error(f"Amend failed: {e}")
        else:
            st.warning("Order WS not connected or Order ID missing")
with a3:
    if st.button("Cancel", use_container_width=True, type="secondary"):
        if state.ws_order and ordid:
            side_code = "1" if ord_side == "BUY" else "2"
            req = {
                "requestId": str(uuid.uuid4()), "action": "CANCEL_ORDER", "brokerCode": BROKER,
                "cancel": {"origOrdID": ordid, "symbolCode": ord_sym, "side": side_code, "securityExchange": "TDWL"},
            }
            try:
                state.ws_order.send(json.dumps(req))
                state.add_history(
                    {"Time": datetime.now().strftime("%H:%M:%S"), "Action": "CANCEL", "Sym": ord_sym, "Order ID": ordid,
                     "Status": "SENT", "Details": "Request Sent"})
                st.toast(f"CANCEL_ORDER sent: {ordid}", icon="✅")
            except Exception as e:
                st.error(f"Cancel failed: {e}")
        else:
            st.warning("Order WS not connected or Order ID missing")