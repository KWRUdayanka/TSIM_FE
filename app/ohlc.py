# ohlc.py
"""Pure OHLC bucketing — no I/O, no locks. Called from SharedState."""
from dataclasses import dataclass
from typing import Dict, Iterable, List

from config import OHLC_TFS


@dataclass
class Tick:
    ts: int                 # epoch ms
    open: float
    high: float
    low: float
    close: float
    vwap: float = 0.0
    volume: int = 0         # cumulative-day volume from feed
    turnover: float = 0.0
    trades: int = 0


@dataclass
class Candle:
    time: int               # bucket start, epoch ms
    open: float
    high: float
    low: float
    close: float
    vwap: float
    volume: int             # per-candle delta volume
    turnover: float
    trades: int


def build_series(ticks: Iterable[Tick], tf_ms: int) -> List[Candle]:
    """
    Bucket ticks into candles of `tf_ms`.

    - open  = first tick's open in the bucket
    - high  = max of all highs in the bucket
    - low   = min of all lows in the bucket
    - close = last tick's close in the bucket
    - volume = sum of per-tick deltas (feed volume is cumulative)
    """
    candles: List[Candle] = []
    last_vol = 0

    for t in ticks:
        dvol = max(0, t.volume - last_vol)
        last_vol = t.volume

        bucket = (t.ts // tf_ms) * tf_ms

        if candles and candles[-1].time == bucket:
            c = candles[-1]
            c.high = max(c.high, t.high)
            c.low = min(c.low, t.low)
            c.close = t.close
            c.volume += dvol
            c.turnover = t.turnover
            c.trades = t.trades
        else:
            candles.append(Candle(
                time=bucket,
                open=t.open,
                high=t.high,
                low=t.low,
                close=t.close,
                vwap=t.vwap,
                volume=dvol,
                turnover=t.turnover,
                trades=t.trades,
            ))

    return candles


def build_all(ticks: Iterable[Tick]) -> Dict[str, List[Candle]]:
    ticks = list(ticks)
    return {tf: build_series(ticks, ms) for tf, ms in OHLC_TFS.items()}