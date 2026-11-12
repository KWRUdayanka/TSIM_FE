# state.py
import threading
import time
from collections import deque

from config import DEFAULT_SYMBOL, OHLC_RING_SIZE
from ohlc import Tick, build_all


class SharedState:
    """Thread-safe state shared between WebSocket workers and Streamlit UI."""

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

        self.market_status = "UNKNOWN"
        self.market_exchange = "TDWL"
        self.msg_count = 0
        self.equity_cache = {}
        self.index_cache = {}
        self.market_date = None
        self.market_time = None
        self.market_advances = None
        self.market_declines = None
        self.market_unchanged = None
        self.market_symbols = None
        self.market_volume = None
        self.market_turnover = None
        self.market_trades = None
        self.market_cap = None
        self.market_cash_in = None
        self.market_cash_out = None
        self.trade_cache = {}
        self.trade_log_max = 100

        self.view_mode = "MARKET_WATCH"
        self.context_symbol = None
        self.context_open = False
        self.chart_symbol = None

        self.top_stocks_cache = {}
        self.top_stocks_tt = "0"

        self.ohlc_cache = {}
        self.ohlc_current_tf = "1m"

    # ---------------- market status / status ----------------
    def set_market_status(self, exchange, status, date=None, time=None, aggregates=None):
        with self.lock:
            self.market_exchange = exchange
            self.market_status = status
            if date is not None: self.market_date = date
            if time is not None: self.market_time = time
            if aggregates:
                for k, v in aggregates.items():
                    if v is not None:
                        setattr(self, f"market_{k}", v)

    def set_status(self, s):
        with self.lock: self.status = s

    def get_status(self):
        with self.lock: return self.status

    # ---------------- market book ----------------
    def update_book(self, sym, bids, asks, ts):
        with self.lock:
            self.book_cache[sym] = {"bids": bids, "asks": asks, "timestamp": ts}

    def snapshot(self, sym):
        with self.lock:
            book = self.book_cache.get(sym, {"bids": [], "asks": [], "timestamp": ""})
            orders = dict(self.my_open_orders.get(sym, {}))
        return book, orders

    # ---------------- history ----------------
    def add_history(self, entry):
        with self.lock:
            self.history.insert(0, entry)
            self.history = self.history[:300]

    # ---------------- shadow orders ----------------
    def add_my_order(self, sym, price, side, qty, req_id):
        price_key = f"{float(price):.2f}"
        with self.lock:
            self.my_open_orders.setdefault(sym, {}).setdefault(price_key, []).append({
                "side": str(side),
                "qty": float(qty),
                "reqId": str(req_id or ""),
                "ordId": None,
            })

    def _all_rows(self, sym):
        for px_key, orders in self.my_open_orders.get(sym, {}).items():
            for o in orders:
                yield px_key, o

    def ensure_my_order(self, sym, price, side, qty, req_id, ord_id):
        if not ord_id:
            return
        with self.lock:
            for _, o in self._all_rows(sym):
                if str(o.get("ordId") or "") == str(ord_id):
                    return
            for _, o in self._all_rows(sym):
                if str(o.get("reqId") or "") == str(req_id) and not o.get("ordId"):
                    o["ordId"] = str(ord_id)
                    o["qty"] = float(qty)
                    return
            price_key = f"{float(price):.2f}"
            self.my_open_orders.setdefault(sym, {}).setdefault(price_key, []).append({
                "side": str(side),
                "qty": float(qty),
                "reqId": str(req_id or ""),
                "ordId": str(ord_id),
            })

    def attach_ord_id(self, sym, req_id, ord_id):
        if not req_id or not ord_id:
            return
        with self.lock:
            for _, o in self._all_rows(sym):
                if str(o.get("reqId") or "") == str(req_id) and not o.get("ordId"):
                    o["ordId"] = str(ord_id)
                    return

    def reduce_qty(self, sym, ord_id, leaves_qty):
        if not ord_id or leaves_qty is None:
            return
        with self.lock:
            for px_key, o in list(self._all_rows(sym)):
                if str(o.get("ordId") or "") == str(ord_id):
                    o["qty"] = float(leaves_qty)
                    if o["qty"] <= 0:
                        self._drop_row(sym, px_key, o)
                    return

    def remove_order(self, sym, *targets):
        wanted = {str(t) for t in targets if t}
        if not wanted:
            return
        with self.lock:
            levels = self.my_open_orders.get(sym)
            if not levels:
                return
            for px_key in list(levels.keys()):
                kept = []
                for o in levels[px_key]:
                    row_ids = {
                        str(o.get("ordId") or ""),
                        str(o.get("reqId") or ""),
                        str(o.get("origOrdId") or ""),
                    } - {""}
                    if row_ids & wanted:
                        continue
                    kept.append(o)
                if kept:
                    levels[px_key] = kept
                else:
                    del levels[px_key]

    def _drop_row(self, sym, px_key, order_ref):
        levels = self.my_open_orders.get(sym, {})
        rows = [o for o in levels.get(px_key, []) if o is not order_ref]
        if rows:
            levels[px_key] = rows
        elif px_key in levels:
            del levels[px_key]

    def has_order_at(self, sym, price_key, side):
        if not price_key:
            return False
        with self.lock:
            for o in self.my_open_orders.get(sym, {}).get(price_key, []):
                if str(o.get("side")) == str(side):
                    return True
        return False

    # ---------------- merged book ----------------
    def merged_book(self, sym):
        with self.lock:
            book = self.book_cache.get(sym, {"bids": [], "asks": [], "timestamp": ""})
            shadow = {px: list(rows) for px, rows in self.my_open_orders.get(sym, {}).items()}

        def _overlay(levels, side_code):
            merged = {}
            for lvl in levels:
                px = float(lvl["price"])
                merged[f"{px:.2f}"] = {"price": px, "qty": float(lvl["qty"]), "mine": 0.0}
            for px_key, rows in shadow.items():
                for o in rows:
                    if str(o["side"]) != side_code:
                        continue
                    if px_key not in merged:
                        merged[px_key] = {"price": float(px_key), "qty": 0.0, "mine": 0.0}
                    merged[px_key]["qty"] += float(o["qty"])
                    merged[px_key]["mine"] += float(o["qty"])
            rev = side_code == "1"
            return sorted(merged.values(), key=lambda x: x["price"], reverse=rev)

        return {
            "bids": _overlay(book["bids"], "1"),
            "asks": _overlay(book["asks"], "2"),
            "timestamp": book.get("timestamp", ""),
        }

    # ---------------- equity / index ----------------
    def update_equity(self, symbol, fields):
        with self.lock: self.equity_cache[symbol] = fields

    def get_equity(self, symbol):
        with self.lock: return dict(self.equity_cache.get(symbol, {}))

    def update_index(self, symbol, fields):
        with self.lock: self.index_cache[symbol] = fields

    def get_index(self, symbol):
        with self.lock: return dict(self.index_cache.get(symbol, {}))

    # ---------------- trades ----------------
    def update_trade(self, symbol, trade):
        with self.lock:
            trades = self.trade_cache.setdefault(symbol, [])
            trades.insert(0, trade)
            if len(trades) > self.trade_log_max:
                del trades[self.trade_log_max:]

    def get_trades(self, symbol, limit=50):
        with self.lock:
            return list(self.trade_cache.get(symbol, [])[:limit])

    def clear_trades(self, symbol):
        with self.lock:
            self.trade_cache.pop(symbol, None)

    # ---------------- OHLC ----------------
    def update_ohlc(self, symbol, fields):
        try:
            tick = Tick(
                ts=int(fields.get("ts") or 0),
                open=float(fields.get("open") or 0.0),
                high=float(fields.get("high") or 0.0),
                low=float(fields.get("low") or 0.0),
                close=float(fields.get("close") or 0.0),
                vwap=float(fields.get("vwap") or 0.0),
                volume=int(fields.get("volume") or 0),
                turnover=float(fields.get("turnover") or 0.0),
                trades=int(fields.get("trades") or 0),
            )
        except (TypeError, ValueError):
            return
        if not tick.ts:
            return
        with self.lock:
            ring = self.ohlc_cache.get(symbol)
            if ring is None:
                ring = deque(maxlen=OHLC_RING_SIZE)
                self.ohlc_cache[symbol] = ring
            if ring and tick.ts < ring[-1].ts:
                return
            ring.append(tick)

    def seed_ohlc(self, symbol, ticks_payload):
        with self.lock:
            ring = self.ohlc_cache.get(symbol)
            if ring is None:
                ring = deque(maxlen=OHLC_RING_SIZE)
                self.ohlc_cache[symbol] = ring
            for raw in ticks_payload or []:
                try:
                    tick = Tick(
                        ts=int(raw.get("ts") or 0),
                        open=float(raw.get("open") or 0.0),
                        high=float(raw.get("high") or 0.0),
                        low=float(raw.get("low") or 0.0),
                        close=float(raw.get("close") or 0.0),
                        vwap=float(raw.get("vwap") or 0.0),
                        volume=int(raw.get("volume") or 0),
                        turnover=float(raw.get("turnover") or 0.0),
                        trades=int(raw.get("trades") or 0),
                    )
                except (TypeError, ValueError):
                    continue
                if not tick.ts:
                    continue
                if ring and tick.ts < ring[-1].ts:
                    continue
                ring.append(tick)

    def get_ohlc_ticks(self, symbol):
        with self.lock:
            ring = self.ohlc_cache.get(symbol)
            return list(ring) if ring else []

    def get_ohlc_series(self, symbol, tf_label=None):
        tf_label = tf_label or self.ohlc_current_tf
        ticks = self.get_ohlc_ticks(symbol)
        if not ticks:
            return []
        return build_all(ticks).get(tf_label, [])

    def set_ohlc_tf(self, tf):
        if tf in ("1m", "5m", "1h"):
            with self.lock:
                self.ohlc_current_tf = tf

    # ---------------- top stocks ----------------
    def update_top_stocks(self, exchange, tt, mkt, entries):
        key = f"{exchange}:{tt}:{mkt}"
        with self.lock:
            self.top_stocks_cache[key] = {
                "ts": time.time() * 1000,
                "exchange": exchange, "tt": tt, "mkt": mkt,
                "entries": list(entries),
            }

    def get_top_stocks(self, exchange, tt, mkt="1"):
        with self.lock:
            return dict(self.top_stocks_cache.get(f"{exchange}:{tt}:{mkt}") or {})