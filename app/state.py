# state.py
import threading
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

        # ---- OHLC ----
        self.ohlc_cache = {}
        self.ohlc_current_tf = "1m"

    # ---------------- existing helpers ----------------
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

    def update_book(self, sym, bids, asks, ts):
        with self.lock:
            self.book_cache[sym] = {"bids": bids, "asks": asks, "timestamp": ts}

    def snapshot(self, sym):
        with self.lock:
            book = self.book_cache.get(sym, {"bids": [], "asks": [], "timestamp": ""})
            orders = dict(self.my_open_orders.get(sym, {}))
        return book, orders

    def add_history(self, entry):
        with self.lock:
            self.history.insert(0, entry)
            self.history = self.history[:300]

    def add_my_order(self, sym, price, side, qty, req_id):
        price_key = f"{float(price):.2f}"
        with self.lock:
            self.my_open_orders.setdefault(sym, {}).setdefault(price_key, []).append({
                "side": side, "qty": qty, "reqId": req_id, "ordId": None,
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
                if kept: self.my_open_orders[sym][px_key] = kept
                else: del self.my_open_orders[sym][px_key]

    def has_order_at(self, symbol, price_key, side):
        if not price_key: return False
        with self.lock:
            for o in self.my_open_orders.get(symbol, {}).get(price_key, []):
                if str(o.get("side")) == str(side):
                    return True
            return False

    def update_equity(self, symbol, fields):
        with self.lock: self.equity_cache[symbol] = fields

    def get_equity(self, symbol):
        with self.lock: return dict(self.equity_cache.get(symbol, {}))

    def update_index(self, symbol, fields):
        with self.lock: self.index_cache[symbol] = fields

    def get_index(self, symbol):
        with self.lock: return dict(self.index_cache.get(symbol, {}))

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

    def update_top_stocks(self, exchange, tt, mkt, entries):
        key = f"{exchange}:{tt}:{mkt}"
        with self.lock:
            self.top_stocks_cache[key] = {
                "ts": __import__("time").time() * 1000,
                "exchange": exchange, "tt": tt, "mkt": mkt,
                "entries": list(entries),
            }

    def get_top_stocks(self, exchange, tt, mkt="1"):
        with self.lock:
            return dict(self.top_stocks_cache.get(f"{exchange}:{tt}:{mkt}") or {})