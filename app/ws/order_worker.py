# ws/order_worker.py
import json
import time
import websocket
from auth import get_tokens
from config import WS_ORDER, BROKER
from state import SharedState
from ws.order_processor import process_order_msg

def order_ws_worker(state: SharedState):
    """Runs forever in background, feeds state.history and state.my_open_orders."""
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
                if not raw:
                    raise ConnectionError("closed")
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