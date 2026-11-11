# config.py
BASE_URL       = "https://172.20.71.15/dfn"
WS_PRICE       = "wss://172.20.71.15/dfn/ws/price"
WS_ORDER       = "wss://172.20.71.15/dfn/ws/dfn-tsim"
SSL_CERT_PATH  = r"D:\Git\ESBTest\fastApiProject\server.crt"
API_KEY        = "broker01-key"
API_SECRET     = "broker01-secret"
BROKER         = "BROKER01"

DEFAULT_SYMBOL = "1010"
DEPTH          = 15
AUTOREFRESH_MS = 500

# Colors
BG, PANEL, FG      = "#0f1419", "#1a1f2e", "#d4d4d4"
BID_FG, ASK_FG     = "#51cf66", "#ff6b6b"
HEAD_FG, DIM_FG    = "#6cb6ff", "#778"
MY_ORDER_FG        = "#fcc419"

OHLC_TFS = {"1m": 60_000, "5m": 300_000, "1h": 3_600_000}
OHLC_RING_SIZE = 500
OHLC_DEFAULT_TF = "1m"