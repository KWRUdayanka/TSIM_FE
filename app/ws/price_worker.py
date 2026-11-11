# ws/price_ws_worker.py
import datetime
import json
import time
import re
import ssl
import websocket

from auth import get_tokens
from config import WS_PRICE, BROKER
from state import SharedState
from config import WS_PRICE, BROKER, SSL_CERT_PATH

INDEX_SYMBOLS = ["TASI"]
_UESCAPE = re.compile(r"\\u([0-9a-fA-F]{4})")

def price_ws_worker(state: SharedState):
    while not state.stop_event.is_set():
        ws = None
        try:
            state.set_status("Fetching price token…")
            _, price_token = get_tokens()
            if not price_token:
                raise Exception("No price token")

            state.set_status("Connecting Price WS…")
            ws = websocket.create_connection(
                WS_PRICE,
                timeout=None,
                sslopt={
                    "ca_certs": SSL_CERT_PATH,
                    "cert_reqs": ssl.CERT_REQUIRED
                }
            )
            state.ws_price = ws

            ws.send(json.dumps({
                "action": "AUTH",
                "brokerCode": BROKER,
                "token": price_token,
            }))

            while not state.stop_event.is_set():
                raw = ws.recv()
                if not raw:
                    raise ConnectionError("closed")
                msg = json.loads(raw)

                # ---------- AUTH ----------
                if msg.get("action") == "AUTH":
                    if not msg.get("success"):
                        state.set_status("Price AUTH failed")
                        break

                    with state.lock:
                        state.subscribed_symbols.clear()
                        state.book_cache.clear()
                        # do NOT clear ohlc_cache on reconnect — preserve history

                    symbols_to_sub = []
                    if state.current_symbol:
                        symbols_to_sub.append(state.current_symbol)
                    symbols_to_sub.extend(INDEX_SYMBOLS)

                    if symbols_to_sub:
                        ws.send(json.dumps({
                            "action": "SUBSCRIBE",
                            "symbols": symbols_to_sub,
                            "exchange": state.market_exchange or "TDWL",
                        }))
                        state.subscribed_symbols.update(symbols_to_sub)

                    state.set_status("Live")
                    continue

                # ---------- Routing ----------
                action = msg.get("action")
                mtype  = msg.get("1")
                mtype2 = msg.get("type")          # normalized DTOs use "type"
                sym    = msg.get("symbol") or msg.get("sym")

                if action == "ORDER_BOOK":
                    state.update_book(
                        msg.get("symbol"),
                        msg.get("bids", []),
                        msg.get("asks", []),
                        msg.get("timestamp", ""),
                    )
                    state.set_status("Live")

                elif action == "OHLC" or mtype2 == "OHLC":
                    if sym:
                        state.update_ohlc(sym, msg)
                    state.set_status("Live")

                elif action == "OHLC_BACKFILL" or mtype2 == "OHLC_BACKFILL":
                    if sym:
                        state.seed_ohlc(sym, msg.get("ticks") or [])

                elif action == "MARKET_STATUS":
                    state.set_market_status(
                        msg.get("exchange", "TDWL"),
                        msg.get("status", "CLOSE"),
                        msg.get("date"),
                        msg.get("time"),
                        aggregates={
                            "advances":  msg.get("ups"),
                            "declines":  msg.get("dwns"),
                            "unchanged": msg.get("nChg"),
                            "symbols":   msg.get("symt"),
                            "volume":    msg.get("vol"),
                            "turnover":  msg.get("tovr"),
                            "trades":    msg.get("trades"),
                            "cap":       msg.get("mktCap"),
                            "cash_in":   msg.get("cit"),
                            "cash_out":  msg.get("cot"),
                        },
                    )

                elif action == "TRADE":
                    if sym:
                        state.update_trade(sym, msg)

                elif action == "TOP_STOCKS" or msg.get("action") == "TOP_STOCKS":
                    exg = msg.get("exchange")
                    tt = msg.get("tt")
                    mkt = msg.get("mkt", "1")
                    entries = msg.get("entries") or []

                    for e in entries:
                        if isinstance(e, dict) and isinstance(e.get("desc"), str):
                            e["desc"] = _decode_unicode(e["desc"])

                    if exg and tt is not None:
                        state.update_top_stocks(exg, str(tt), mkt, entries)
                    state.set_status("Live")

                elif mtype == 3 and sym:
                    state.update_equity(sym, msg)

                elif mtype == 4 and sym:
                    state.update_index(sym, msg)

                elif mtype == 6 and sym:
                    # raw-feed OHLC (defensive)
                    state.update_ohlc(sym, {
                        "ts":       msg.get("ts") or int(time.time() * 1000),
                        "open":     msg.get("open"),
                        "high":     msg.get("high"),
                        "low":      msg.get("low"),
                        "close":    msg.get("close") or msg.get("cls"),
                        "vwap":     msg.get("vwap"),
                        "volume":   msg.get("volume") or msg.get("vol"),
                        "turnover": msg.get("turnover") or msg.get("tOvr"),
                        "trades":   msg.get("trades"),
                    })

                elif mtype == 10 and sym:
                    trp = msg.get("trp")
                    trq = msg.get("trq")
                    if trp is not None and trq is not None:
                        state.update_trade(sym, {
                            "symbol": sym,
                            "exchange": msg.get("exg", "TDWL"),
                            "seq": msg.get("seq"),
                            "price": float(trp),
                            "quantity": int(trq),
                            "tradeTime": msg.get("tts", ""),
                            "tradeType": msg.get("trdType", ""),
                            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                        })

                with state.lock:
                    state.msg_count += 1

        except Exception as e:
            state.set_status(f"Price WS Error: {e}")
        finally:
            if ws is not None:
                try:
                    ws.close()
                except Exception:
                    pass
        time.sleep(3)

def _decode_unicode(s):
    """Decode literal \\uXXXX escape sequences to real characters."""
    if not s or "\\u" not in s:
        return s
    return _UESCAPE.sub(lambda m: chr(int(m.group(1), 16)), s)