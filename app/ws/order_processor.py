# ws/order_processor.py
from datetime import datetime
from state import SharedState


def process_order_msg(state: SharedState, msg: dict):
    fix = msg.get("fix", {})
    if not fix:
        return

    ord_id = str(fix.get("ordId", "")).strip()
    orig_ord_id = str(fix.get("origOrdId", "")).strip()
    status = str(fix.get("ordStatus", "")).strip()
    exec_type = str(fix.get("execType", "")).strip()
    text = fix.get("text", "")
    sym = fix.get("symbol", "")
    req_id = str(msg.get("requestId", "")).strip()

    price_str = fix.get("price")
    qty_str = fix.get("orderQty") or fix.get("leavesQty")
    side_str = str(fix.get("side", "1"))

    print(f"[ORDER MSG] ordStatus={status} execType={exec_type} "
          f"ordId={ord_id} origOrdId={orig_ord_id} "
          f"price={price_str} qty={qty_str} sym={sym} reqId={req_id}")

    # ============================================================
    # 1. REPLACED (execType=5)
    # ============================================================
    if exec_type == "5":
        print(f"[SHADOW] Amend: removing {orig_ord_id}, adding {ord_id} @ {price_str}")

        if orig_ord_id:
            state.remove_order(sym, orig_ord_id)

        if price_str is not None and qty_str is not None:
            state.add_my_order(
                sym=sym,
                price=float(price_str),
                side=side_str,
                qty=float(qty_str),
                req_id=req_id,
            )
            with state.lock:
                for px_key, orders in state.my_open_orders.get(sym, {}).items():
                    for o in orders:
                        if str(o.get("reqId")).strip() == req_id:
                            o["ordId"] = ord_id

        state.add_history({
            "Time": datetime.now().strftime("%H:%M:%S"),
            "Action": "REPLACED",
            "Sym": sym,
            "Order ID": ord_id,
            "Status": "REPLACED",
            "Details": text or "Order replaced",
        })
        return

    # ============================================================
    # 2. NEW / QUEUED / PARTIAL FILL
    # ============================================================
    if ord_id and status in ["PENDING_NEW", "QUEUED", "PARTIALLY_FILLED"]:
        with state.lock:
            if sym in state.my_open_orders:
                for px_key, orders in state.my_open_orders[sym].items():
                    for o in orders:
                        if str(o.get("reqId")).strip() == req_id:
                            o["ordId"] = ord_id

    # ============================================================
    # 3. CANCELED / FILLED / REJECTED — remove from shadow
    # ============================================================
    # The shadow row may be keyed by reqId (created when the broker sent
    # the request) or by ordId (after the exchange accepted it). Remove it
    # using ALL available identifiers so we never leave a phantom row.
    if status in ["CANCELED", "FILLED", "REJECTED", "EXPIRED"]:
        candidates = []
        if req_id:
            candidates.append(req_id)
        if ord_id:
            candidates.append(ord_id)
        if orig_ord_id:
            candidates.append(orig_ord_id)

        for target in candidates:
            state.remove_order(sym, target)

        # Debug print so we can see what was tried
        print(f"[SHADOW] Remove tried targets: {candidates}")

    # ============================================================
    # 4. History log
    # ============================================================
    action = msg.get("action") or {
        "CANCELED": "CANCEL_ORDER",
        "FILLED": "FILLED",
        "REJECTED": "REJECTED",
        "EXPIRED": "EXPIRED",
    }.get(status, "EXEC_REPORT")

    state.add_history({
        "Time": datetime.now().strftime("%H:%M:%S"),
        "Action": action,
        "Sym": sym,
        "Order ID": ord_id or orig_ord_id,
        "Status": status,
        "Details": text,
    })