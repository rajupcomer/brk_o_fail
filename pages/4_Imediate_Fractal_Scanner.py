"""
╔══════════════════════════════════════════════════════════════════╗
║      FRACTAL BREAKOUT SCANNER — STREAMLIT UI (tvdatafeed)       ║
║                                                                  ║
║  MODES:                                                          ║
║    1. 30-Min vs 5-Min   → 12 core F&O watchlist (DEFAULT)       ║
║    2. 1-Week vs 1-Day   → All F&O stocks                        ║
║    3. 1-Day  vs 1-Hour  → All F&O stocks                        ║
║                                                                  ║
║  INSTALL:                                                        ║
║    pip install streamlit tvdatafeed pandas numpy plotly         ║
║                                                                  ║
║  RUN:                                                            ║
║    streamlit run fractal_scanner_app.py                          ║
╚══════════════════════════════════════════════════════════════════╝
"""

# ─────────────────────────────────────────────
#  IMPORTS
# ─────────────────────────────────────────────
import streamlit as st
import pandas as pd
import numpy as np
import datetime
import time
import plotly.graph_objects as go

from tvDatafeed import TvDatafeed, Interval

# ─────────────────────────────────────────────
#  PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title            = "Fractal Scanner",
    page_icon             = "📊",
    layout                = "wide",
    initial_sidebar_state = "expanded",
)

# ─────────────────────────────────────────────
#  GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@600;700;800;900&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Nunito', sans-serif !important;
    background-color: #0b0d12 !important;
    color: #e8ecf5 !important;
}
.block-container { padding: 1.4rem 2rem !important; max-width: 100% !important; }
#MainMenu, footer, header { visibility: hidden; }

.top-banner {
    background: linear-gradient(120deg, #0e131f 0%, #121a2e 60%, #0e131f 100%);
    border: 1px solid #1f2d48;
    border-top: 3px solid #00c8ff;
    border-radius: 12px;
    padding: 1.4rem 2rem;
    margin-bottom: 1.4rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.banner-title { font-size: 2rem; font-weight: 900; color: #00c8ff; letter-spacing: 0.04em; line-height: 1.1; }
.banner-sub   { font-size: 1rem; font-weight: 700; color: #4a6080; margin-top: 4px; }
.banner-right { text-align: right; }
.mkt-open     { font-size: 1rem; font-weight: 800; color: #00e87a; }
.mkt-close    { font-size: 1rem; font-weight: 800; color: #ff4466; }
.banner-time  { font-size: 0.9rem; font-weight: 700; color: #2e4060; margin-top: 4px; }
.live-dot {
    display: inline-block; width: 10px; height: 10px;
    background: #00e87a; border-radius: 50%; margin-right: 6px;
    animation: blink 1.4s infinite; box-shadow: 0 0 8px #00e87a;
}
@keyframes blink { 0%,100%{opacity:1;} 50%{opacity:0.3;} }

/* Mode badge */
.mode-badge {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.88rem;
    font-weight: 900;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 1rem;
}
.mode-default { background: rgba(0,200,255,0.12); color: #00c8ff; border: 1px solid rgba(0,200,255,0.35); }
.mode-weekly  { background: rgba(160,80,255,0.12); color: #c060ff; border: 1px solid rgba(160,80,255,0.35); }
.mode-daily   { background: rgba(255,160,30,0.12); color: #ffa020; border: 1px solid rgba(255,160,30,0.35); }

/* Metrics */
.metrics-row { display: flex; gap: 1rem; margin-bottom: 1.4rem; flex-wrap: wrap; }
.metric-box {
    flex: 1; min-width: 100px;
    background: #0f1520; border: 1px solid #1a2540;
    border-radius: 10px; padding: 1rem 1.2rem; text-align: center;
}
.metric-box .m-label { font-size: 0.85rem; font-weight: 800; color: #3a5070; text-transform: uppercase; letter-spacing: 0.08em; }
.metric-box .m-value { font-size: 2rem; font-weight: 900; margin-top: 4px; line-height: 1; }
.col-cyan   { color: #00c8ff; }
.col-green  { color: #00e87a; }
.col-red    { color: #ff4466; }
.col-yellow { color: #ffd600; }
.col-purple { color: #c060ff; }
.col-orange { color: #ffa020; }

/* Status bar */
.status-bar {
    background: #0f1520; border: 1px solid #1a2540; border-radius: 8px;
    padding: 0.65rem 1.2rem; font-size: 0.9rem; font-weight: 700;
    color: #3a5070; margin-bottom: 1.2rem; display: flex; gap: 1.5rem; align-items: center; flex-wrap: wrap;
}
.status-bar span { color: #4499ff; }

/* Alert cards */
.alert-card {
    border-radius: 10px; padding: 1.4rem 1.6rem;
    margin-bottom: 1rem; border-left: 5px solid; position: relative;
}
.card-bull { background: #0a1a12; border-color: #00e87a; box-shadow: 0 0 18px rgba(0,232,122,0.15); }
.card-bear { background: #1a0a10; border-color: #ff4466; box-shadow: 0 0 18px rgba(255,68,102,0.15); }
.card-none { background: #0f1520; border-color: #1a2540; }

.card-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.card-symbol { font-size: 1.5rem; font-weight: 900; letter-spacing: 0.06em; }
.card-ltp    { font-size: 1.6rem; font-weight: 900; }
.card-tags   { display: flex; gap: 0.5rem; margin-top: 6px; flex-wrap: wrap; }
.tag {
    font-size: 0.82rem; font-weight: 800; padding: 4px 12px;
    border-radius: 5px; letter-spacing: 0.06em; text-transform: uppercase;
}
.tag-bull   { background: rgba(0,232,122,0.15);  color: #00e87a; border: 1px solid rgba(0,232,122,0.35);  }
.tag-bear   { background: rgba(255,68,102,0.15); color: #ff4466; border: 1px solid rgba(255,68,102,0.35); }
.tag-close  { background: rgba(0,200,255,0.12);  color: #00c8ff; border: 1px solid rgba(0,200,255,0.3);   }
.tag-wick   { background: rgba(255,214,0,0.1);   color: #ffd600; border: 1px solid rgba(255,214,0,0.25);  }
.tag-weekly { background: rgba(160,80,255,0.12); color: #c060ff; border: 1px solid rgba(160,80,255,0.3);  }
.tag-daily  { background: rgba(255,160,30,0.12); color: #ffa020; border: 1px solid rgba(255,160,30,0.3);  }

.pgrid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.8rem; margin-top: 0.4rem; }
.pgrid-label { font-size: 0.78rem; font-weight: 800; color: #3a5070; text-transform: uppercase; letter-spacing: 0.06em; }
.pgrid-value { font-size: 1.1rem; font-weight: 900; color: #e8ecf5; margin-top: 2px; }

.tv-btn {
    display: inline-block; margin-top: 1rem; padding: 7px 18px;
    background: rgba(0,200,255,0.08); border: 1px solid rgba(0,200,255,0.3);
    border-radius: 6px; color: #00c8ff !important; font-size: 0.88rem;
    font-weight: 800; text-decoration: none; letter-spacing: 0.04em; transition: background 0.2s;
}
.tv-btn:hover { background: rgba(0,200,255,0.18); }

/* Quiet cards */
.q-card { background: #0f1520; border: 1px solid #1a2540; border-radius: 8px; padding: 1rem 1.2rem; margin-bottom: 0.6rem; }
.q-symbol    { font-size: 1.1rem; font-weight: 900; color: #c0c8d8; margin-bottom: 4px; }
.q-ltp       { font-size: 1rem;  font-weight: 800; color: #4499ff; }
.q-level-label { font-size: 0.78rem; font-weight: 800; color: #2e4060; text-transform: uppercase; letter-spacing: 0.06em; margin-top: 6px; }
.q-levels    { font-size: 0.88rem; font-weight: 700; color: #4a6080; }

/* No-alert box */
.no-alert-box {
    text-align: center; padding: 3.5rem 2rem;
    border: 2px dashed #1a2540; border-radius: 12px;
    color: #2e4060; font-size: 1rem; font-weight: 700;
}
.no-alert-box .big-icon { font-size: 3rem; margin-bottom: 0.8rem; }

/* Sidebar */
section[data-testid="stSidebar"] { background: #090c14 !important; border-right: 1px solid #141e30 !important; }
section[data-testid="stSidebar"] .block-container { padding: 1rem 1.2rem !important; }
.sb-section {
    font-size: 0.78rem; font-weight: 900; text-transform: uppercase;
    letter-spacing: 0.12em; color: #2e4060; border-bottom: 1px solid #141e30;
    padding-bottom: 5px; margin: 1.2rem 0 0.7rem;
}

/* Widget overrides */
label, .stCheckbox label, div[data-testid="stMarkdownContainer"] p {
    font-family: 'Nunito', sans-serif !important;
    font-size: 0.92rem !important; font-weight: 700 !important; color: #7a90b0 !important;
}
.stButton button {
    background: #0d2a1a !important; color: #00e87a !important;
    border: 2px solid rgba(0,232,122,0.4) !important;
    font-family: 'Nunito', sans-serif !important; font-size: 0.95rem !important;
    font-weight: 900 !important; letter-spacing: 0.06em !important;
    border-radius: 8px !important; padding: 0.55rem 1.2rem !important;
    width: 100% !important; text-transform: uppercase !important;
}
.stButton button:hover { background: #143d22 !important; box-shadow: 0 0 14px rgba(0,232,122,0.25) !important; }
.stTabs [data-baseweb="tab-list"] { background: #0f1520 !important; border-radius: 8px !important; padding: 4px !important; border: 1px solid #1a2540 !important; }
.stTabs [data-baseweb="tab"] { font-family: 'Nunito', sans-serif !important; font-size: 0.9rem !important; font-weight: 800 !important; color: #3a5070 !important; border-radius: 6px !important; }
.stTabs [aria-selected="true"] { background: #141e30 !important; color: #00c8ff !important; }

/* Level table */
.lvl-table { width: 100%; border-collapse: collapse; font-size: 0.92rem; font-weight: 700; }
.lvl-table th { background: #0f1520; color: #3a5070; padding: 0.55rem 0.9rem; text-align: left; font-size: 0.8rem; font-weight: 900; text-transform: uppercase; letter-spacing: 0.08em; border-bottom: 1px solid #1a2540; }
.lvl-table td { padding: 0.55rem 0.9rem; border-bottom: 1px solid #141e30; color: #c0c8d8; font-weight: 700; }
.lvl-table tr:hover td { background: #0f1520; }
hr { border-color: #141e30 !important; margin: 1rem 0 !important; }

/* Section divider label */
.section-label {
    font-size: 0.75rem; font-weight: 900; color: #2e4060;
    text-transform: uppercase; letter-spacing: 0.14em;
    border-left: 3px solid #1a2540; padding-left: 8px;
    margin: 1.5rem 0 0.8rem;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  WATCHLISTS
# ─────────────────────────────────────────────

# Default 30-min / 5-min watchlist (12 core stocks)
WATCHLIST_DEFAULT = [
    ("NIFTY",       "NSE"),
    ("BANKNIFTY",   "NSE"),
    ("HDFCBANK",    "NSE"),
    ("ICICIBANK",   "NSE"),
    ("SBIN",        "NSE"),
    ("AXISBANK",    "NSE"),
    ("BAJFINANCE",  "NSE"),
    ("INFY",        "NSE"),
    ("TCS",         "NSE"),
    ("RELIANCE",    "NSE"),
    ("MARUTI",      "NSE"),
    ("TMPV",  "NSE"),
]

# Full F&O watchlist for higher timeframe scans
WATCHLIST_FNO = [
    # Indices
    ("NIFTY",        "NSE"), ("BANKNIFTY",   "NSE"), ("FINNIFTY",    "NSE"),
    # Banking
    ("HDFCBANK",     "NSE"), ("ICICIBANK",   "NSE"), ("SBIN",        "NSE"),
    ("AXISBANK",     "NSE"), ("KOTAKBANK",   "NSE"), ("BANKBARODA",  "NSE"),
    ("FEDERALBNK",   "NSE"), ("IDFCFIRSTB",  "NSE"), ("INDUSINDBK",  "NSE"),
    ("PNB",          "NSE"), ("CANBK",       "NSE"), ("AUBANK",      "NSE"),
    ("UNIONBANK",    "NSE"), ("BANDHANBNK",  "NSE"), 

    # Finance / NBFC
    ("BAJFINANCE",   "NSE"), ("BAJAJFINSV",  "NSE"), ("HDFCLIFE",    "NSE"),
    ("SBILIFE",      "NSE"), ("CHOLAFIN",    "NSE"), ("MUTHOOTFIN",  "NSE"),
    ("LICHSGFIN",    "NSE"), ("IRFC",        "NSE"), ("JIOFIN",      "NSE"),
    ("SAMMAANCAP",   "NSE"), ("VAIBHAVGBL",  "NSE"), ("MANAPPURAM",  "NSE"),
    # IT
    ("INFY",         "NSE"), ("TCS",         "NSE"), ("WIPRO",       "NSE"),
    ("HCLTECH",      "NSE"), ("TECHM",       "NSE"), ("LTIM",        "NSE"),
    ("PERSISTENT",   "NSE"), ("COFORGE",     "NSE"),
    # Auto
    ("MARUTI",       "NSE"), ("TMPV",        "NSE"), ("M&M",         "NSE"),
    ("HEROMOTOCO",   "NSE"), ("BAJAJ-AUTO",  "NSE"), ("EICHERMOT",   "NSE"),
    ("TVSMOTOR",     "NSE"), ("ASHOKLEY",    "NSE"), ("MOTHERSON",   "NSE"),
    ("SONACOMS",     "NSE"), ("TIINDIA",     "NSE"), ("BOSCHLTD",   "NSE"),
    ("BHARATFORG",   "NSE"), ("EXIDEIND",    "NSE"), ("TMCV",       "NSE"),
    # Oil & Gas / Energy
    ("RELIANCE",     "NSE"), ("ONGC",        "NSE"), ("IOC",         "NSE"),
    ("BPCL",         "NSE"), ("GAIL",        "NSE"), ("POWERGRID",   "NSE"),
    ("NTPC",         "NSE"), ("ADANIGREEN",  "NSE"), ("ADANIPORTS",  "NSE"),
    ("TATAPOWER",    "NSE"),
    # Pharma
    ("SUNPHARMA",    "NSE"), ("DRREDDY",     "NSE"), ("CIPLA",       "NSE"),
    ("DIVISLAB",     "NSE"), ("APOLLOHOSP",  "NSE"), ("AUROPHARMA",  "NSE"),
    ("ABBOTINDIA",   "NSE"), ("AJANTPHARM",  "NSE"), ("ALKEM",        "NSE"),
    ("BIOCON",       "NSE"), ("GLAND",       "NSE"), ("GLENMARK",     "NSE"),
    ("IPCALAB",      "NSE"), ("JBCHEPHARM",  "NSE"), ("LAURUSLABS",   "NSE"),
    ("LUPIN",        "NSE"), ("MANKIND",     "NSE"), ("PPLPHARMA",     "NSE"),
    ("TORNTPHARM",   "NSE"), ("WOCKPHARMA",  "NSE"), ("ZYDUSLIFE",     "NSE"),

    # Metals / Mining
    ("TATASTEEL",    "NSE"), ("HINDALCO",    "NSE"), ("JSWSTEEL",    "NSE"),
    ("COALINDIA",    "NSE"), ("VEDL",        "NSE"), ("WELCORP",     "NSE"),
    ("APLAPOLLO",    "NSE"), ("ADANIENT",    "NSE"), ("HINDCOPPER",  "NSE"),
    ("HINDZINC",     "NSE"), ("JSWSTEEL",    "NSE"), ("JINDALSTEL",  "NSE"),
    ("NMDC",         "NSE"), ("NATIONALUM",  "NSE"), ("SAIL",        "NSE"),
    # FMCG / Consumer
    ("HINDUNILVR",   "NSE"), ("ITC",         "NSE"), ("NESTLEIND",   "NSE"),
    ("BRITANNIA",    "NSE"), ("DABUR",       "NSE"), ("MARICO",      "NSE"),
    ("EMAMILTD",     "NSE"), ("COLPAL",      "NSE"), ("GODREJCP",    "NSE"),
    ("PATANJALI",    "NSE"), ("RADICO",      "NSE"), ("TATACONSUM",  "NSE"),
    ("UBL",          "NSE"), ("UNITDSPR",    "NSE"), ("JYOTHYLAB",   "NSE"),
    ("CROMPTON",     "NSE"),
    # Infra / Cement
    ("LT",           "NSE"), ("ULTRACEMCO",  "NSE"), ("GRASIM",      "NSE"),
    ("SHREECEM",     "NSE"), ("ACC",         "NSE"), ("AMBUJACEM",   "NSE"),
    ("NUVOCO",       "NSE"), ("BEML",        "NSE"), ("RITES",       "NSE"),
    ("NCC",          "NSE"),
    # Others
    ("TITAN",       "NSE"), ("ASIANPAINT",  "NSE"), ("DMART",       "NSE"),
    ("UPL",         "NSE"), ("PIIND",       "NSE"), ("PRESTIGE",    "NSE"),
    ("DLF",         "NSE"), ("ANANTRAJ",    "NSE"), ("GODREJPROP",  "NSE"),
    ("OBEROIRLTY",  "NSE"), ("SOBHA",       "NSE"), ("CHAMBLFERT",  "NSE"),
    ("ZEEL",        "NSE"), ("ITCHOTELS",   "NSE"), ("IRCTC",       "NSE"),
    ("IEx",         "NSE"), ("PAYTM",       "NSE"), ("UGROCAP",     "NSE"),
]

TV_CHART_URLS = {
    "5min"  : "https://www.tradingview.com/chart/?symbol=NSE%3A{symbol}&interval=5",
    "1hour" : "https://www.tradingview.com/chart/?symbol=NSE%3A{symbol}&interval=60",
    "1day"  : "https://www.tradingview.com/chart/?symbol=NSE%3A{symbol}&interval=D",
}

# ── Scan mode definitions
SCAN_MODES = {
    "30-Min / 5-Min  (Default)": {
        "key"          : "default",
        "htf_interval" : Interval.in_30_minute,
        "ltf_interval" : Interval.in_5_minute,
        "htf_bars"     : 100,
        "ltf_bars"     : 20,   # enough to find break+recovery pattern
        "htf_label"    : "30-Min",
        "ltf_label"    : "5-Min",
        "chart_tf"     : "5min",
        "chart_bars"   : 78,
        "watchlist"    : WATCHLIST_DEFAULT,
        "badge_cls"    : "mode-default",
        "tag_cls"      : "tag-close",
    },
    "1-Week / 1-Day  (Swing)": {
        "key"          : "weekly",
        "htf_interval" : Interval.in_weekly,
        "ltf_interval" : Interval.in_daily,
        "htf_bars"     : 60,
        "ltf_bars"     : 20,
        "htf_label"    : "1-Week",
        "ltf_label"    : "1-Day",
        "chart_tf"     : "1day",
        "chart_bars"   : 60,
        "watchlist"    : WATCHLIST_FNO,
        "badge_cls"    : "mode-weekly",
        "tag_cls"      : "tag-weekly",
    },
    "1-Day / 1-Hour  (Positional)": {
        "key"          : "daily",
        "htf_interval" : Interval.in_daily,
        "ltf_interval" : Interval.in_1_hour,
        "htf_bars"     : 60,
        "ltf_bars"     : 20,
        "htf_label"    : "1-Day",
        "ltf_label"    : "1-Hour",
        "chart_tf"     : "1hour",
        "chart_bars"   : 30,
        "watchlist"    : WATCHLIST_FNO,
        "badge_cls"    : "mode-daily",
        "tag_cls"      : "tag-daily",
    },
}


# ─────────────────────────────────────────────
#  TIMEZONE — single source of truth for IST
# ─────────────────────────────────────────────
import pytz
IST = pytz.timezone("Asia/Kolkata")

def now_ist():
    """Return current datetime in IST (always correct regardless of server location)."""
    return datetime.datetime.now(tz=IST)

def is_market_open():
    """Check if NSE market is open — uses IST time."""
    now = now_ist()
    if now.weekday() >= 5:          # Saturday=5, Sunday=6
        return False
    t = now.time()
    return datetime.time(9, 15) <= t <= datetime.time(15, 30)


# ─────────────────────────────────────────────
#  ROBUST DATA FETCHER
#  Handles timeout, bad symbol, network errors
#  Retries with exponential backoff
# ─────────────────────────────────────────────

MAX_RETRIES   = 3
RETRY_DELAY   = 2.0
RETRY_BACKOFF = 1.5

RETRY_ERRORS = (
    "timed out", "read operation timed out", "connection", "timeout",
    "remote end closed", "broken pipe", "reset by peer",
    "temporarily unavailable", "socket", "ssl", "502", "503", "504",
)
SKIP_ERRORS = (
    "no data", "no history", "invalid symbol", "not found",
    "unauthorized", "please check the exchange and symbol",
)


def safe_get_hist(tv, symbol, exchange, interval, n_bars, label="data"):
    """
    Robust wrapper around tv.get_hist() with retry + exponential backoff.

    Returns:
        (df, None)       — on success, df has lowercased OHLCV columns
        (None, err_msg)  — on failure after all retries
    """
    last_error = None
    delay      = RETRY_DELAY

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            df = tv.get_hist(
                symbol   = symbol,
                exchange = exchange,
                interval = interval,
                n_bars   = n_bars,
            )

            if df is None or df.empty:
                return None, f"No {label} — check symbol/exchange ({symbol}:{exchange})"

            df.columns = df.columns.str.lower()
            required   = {"open", "high", "low", "close"}
            missing    = required - set(df.columns)
            if missing:
                return None, f"Missing columns {missing} in {label} for {symbol}"

            return df[["open", "high", "low", "close", "volume"]].copy(), None

        except Exception as e:
            err_lower  = str(e).lower()
            last_error = str(e)

            # Bad symbol — no point retrying
            if any(s in err_lower for s in SKIP_ERRORS):
                return None, f"Symbol error ({symbol}:{exchange}) — {e}"

            # Transient error — retry with backoff
            if attempt < MAX_RETRIES:
                time.sleep(delay)
                delay *= RETRY_BACKOFF
                continue

    return None, f"Failed after {MAX_RETRIES} retries ({symbol}) — {last_error}"


# ─────────────────────────────────────────────
#  CORE LOGIC  — unchanged from fractal_scanner.py
#  Same functions, now parameterised with intervals
# ─────────────────────────────────────────────

def find_fractals(df, strength=2):
    """
    Identify fractal Highs and Lows.
    Fractal High: candle[i].high is highest among `strength` candles on each side.
    Fractal Low : candle[i].low  is lowest  among `strength` candles on each side.
    Returns dataframe with added columns: fractal_high, fractal_low
    """
    df = df.copy()
    df["fractal_high"] = np.nan
    df["fractal_low"]  = np.nan

    for i in range(strength, len(df) - strength):
        window_high = df["high"].iloc[i - strength : i + strength + 1]
        window_low  = df["low"].iloc[i - strength : i + strength + 1]

        if df["high"].iloc[i] == window_high.max():
            df.at[df.index[i], "fractal_high"] = df["high"].iloc[i]

        if df["low"].iloc[i] == window_low.min():
            df.at[df.index[i], "fractal_low"] = df["low"].iloc[i]

    return df


def get_unmitigated_levels(df, strength=2):
    """
    From all fractals, return only UNMITIGATED ones.
    Unmitigated High: price has NOT revisited that high after formation.
    Unmitigated Low : price has NOT revisited that low  after formation.
    Returns: (unmitigated_highs, unmitigated_lows) — sorted lists of float
    """
    df = find_fractals(df, strength)

    fractal_highs = df[df["fractal_high"].notna()].copy()
    fractal_lows  = df[df["fractal_low"].notna()].copy()

    unmitigated_highs = []
    unmitigated_lows  = []

    for idx, row in fractal_highs.iterrows():
        level      = row["fractal_high"]
        after_data = df.loc[idx:].iloc[1:]
        if after_data.empty or not (after_data["close"] > level).any():
            unmitigated_highs.append(level)

    for idx, row in fractal_lows.iterrows():
        level      = row["fractal_low"]
        after_data = df.loc[idx:].iloc[1:]
        if after_data.empty or not (after_data["close"] < level).any():
            unmitigated_lows.append(level)

    return sorted(unmitigated_highs), sorted(unmitigated_lows)


def check_breakout(symbol, exchange, tv, mode_cfg, strength=2, max_recovery=2):
    """
    Generic breakout checker — works for ALL three scan modes.

    CLOSE_BREAK (new sliding window logic):
      Scans the last N LTF candles as a sliding window.
      BULLISH: candle[i] closes BELOW HTF support
               → within max_recovery candles, candle[i+k] closes BACK ABOVE support
               → complete reversal confirmed on recovery candle
      BEARISH: mirror logic for HTF resistance.

    WICK_SWEEP (unchanged):
      Latest candle wick pierces level but closes back on same side.
    """
    chart_url = TV_CHART_URLS[mode_cfg["chart_tf"]].format(symbol=symbol)

    result = {
        "symbol"            : symbol,
        "exchange"          : exchange,
        "status"            : "OK",
        "alert"             : None,
        "direction"         : None,
        "broken_level"      : None,
        "current_price"     : None,
        "candle_high"       : None,
        "candle_low"        : None,
        "candle_open"       : None,
        "candle_time"       : None,
        "sweep_type"        : None,
        "break_candle_low"  : None,   # SL for bullish setup
        "break_candle_high" : None,   # SL for bearish setup
        "recovery_candles"  : None,   # how many candles the recovery took
        "unmitigated_highs" : [],
        "unmitigated_lows"  : [],
        "htf_label"         : mode_cfg["htf_label"],
        "ltf_label"         : mode_cfg["ltf_label"],
        "chart_url"         : chart_url,
        "error"             : None,
    }

    try:
        # ── HTF data
        df_htf, err = safe_get_hist(
            tv, symbol, exchange,
            mode_cfg["htf_interval"], mode_cfg["htf_bars"],
            label=mode_cfg["htf_label"],
        )
        if err:
            result["status"] = "ERROR"
            result["error"]  = err
            return result

        u_highs, u_lows = get_unmitigated_levels(df_htf, strength)
        result["unmitigated_highs"] = u_highs
        result["unmitigated_lows"]  = u_lows

        # ── LTF data
        df_ltf, err = safe_get_hist(
            tv, symbol, exchange,
            mode_cfg["ltf_interval"], mode_cfg["ltf_bars"],
            label=mode_cfg["ltf_label"],
        )
        if err:
            result["status"] = "ERROR"
            result["error"]  = err
            return result

        # ── Latest candle info (always from last bar)
        latest = df_ltf.iloc[-1]
        result["current_price"] = round(float(latest["close"]), 2)
        result["candle_high"]   = round(float(latest["high"]),  2)
        result["candle_low"]    = round(float(latest["low"]),   2)
        result["candle_open"]   = round(float(latest["open"]),  2)

        # ── Timestamp → IST
        try:
            ts = latest.name
            ts_ist = ts.astimezone(IST) if (hasattr(ts, "tzinfo") and ts.tzinfo) \
                     else pytz.utc.localize(ts).astimezone(IST)
            result["candle_time"] = ts_ist.strftime("%d-%b  %H:%M IST")
        except Exception:
            result["candle_time"] = str(latest.name)[:16] if latest.name else "--"

        # ════════════════════════════════════════════
        #  CLOSE_BREAK — sliding window
        #  Window: last (max_recovery + 3) candles
        #  For each candle[i] that closes beyond a level,
        #  check if any candle[i+1 … i+max_recovery] closes back.
        #  Most recent qualifying pattern wins.
        # ════════════════════════════════════════════
        window      = df_ltf.iloc[-(max_recovery + 3):].copy()
        n           = len(window)
        cb_bullish  = None   # (level, break_idx, recovery_idx, bc_low, k)
        cb_bearish  = None

        for i in range(n - 1):
            bc       = window.iloc[i]
            bc_close = float(bc["close"])
            bc_low   = float(bc["low"])
            bc_high  = float(bc["high"])

            # ── BULLISH: break candle closes BELOW support
            for level in u_lows:
                if bc_close < level:
                    for k in range(1, max_recovery + 1):
                        ri = i + k
                        if ri >= n:
                            break
                        rc = window.iloc[ri]
                        if float(rc["close"]) > level:   # ✅ closed back above
                            if cb_bullish is None or i > cb_bullish[1]:
                                cb_bullish = (level, i, ri, bc_low, k)
                            break

            # ── BEARISH: break candle closes ABOVE resistance
            for level in u_highs:
                if bc_close > level:
                    for k in range(1, max_recovery + 1):
                        ri = i + k
                        if ri >= n:
                            break
                        rc = window.iloc[ri]
                        if float(rc["close"]) < level:   # ✅ closed back below
                            if cb_bearish is None or i > cb_bearish[1]:
                                cb_bearish = (level, i, ri, bc_high, k)
                            break

        # Apply CLOSE_BREAK result — bearish takes priority (same as original)
        if cb_bearish:
            level, bi, ri, bc_high, k = cb_bearish
            result["alert"]             = "HIGH_BREAK"
            result["direction"]         = "BEARISH_SETUP"
            result["broken_level"]      = round(level, 2)
            result["sweep_type"]        = "CLOSE_BREAK"
            result["break_candle_high"] = round(bc_high, 2)
            result["recovery_candles"]  = k

        elif cb_bullish:
            level, bi, ri, bc_low, k = cb_bullish
            result["alert"]            = "LOW_BREAK"
            result["direction"]        = "BULLISH_SETUP"
            result["broken_level"]     = round(level, 2)
            result["sweep_type"]       = "CLOSE_BREAK"
            result["break_candle_low"] = round(bc_low, 2)
            result["recovery_candles"] = k

        # ════════════════════════════════════════════
        #  WICK_SWEEP — latest candle only (unchanged)
        # ════════════════════════════════════════════
        if result["alert"] is None:
            cl = float(latest["close"])
            hi = float(latest["high"])
            lo = float(latest["low"])

            for level in u_highs:
                if hi > level >= cl:
                    result["alert"]             = "HIGH_BREAK"
                    result["direction"]         = "BEARISH_SETUP"
                    result["broken_level"]      = round(level, 2)
                    result["sweep_type"]        = "WICK_SWEEP"
                    result["break_candle_high"] = round(hi, 2)
                    break

            if result["alert"] is None:
                for level in u_lows:
                    if lo < level <= cl:
                        result["alert"]            = "LOW_BREAK"
                        result["direction"]        = "BULLISH_SETUP"
                        result["broken_level"]     = round(level, 2)
                        result["sweep_type"]       = "WICK_SWEEP"
                        result["break_candle_low"] = round(lo, 2)
                        break

    except Exception as e:
        result["status"] = "ERROR"
        result["error"]  = str(e)

    return result


# ─────────────────────────────────────────────
#  CHART BUILDER
# ─────────────────────────────────────────────

def build_chart(symbol, exchange, tv, u_highs, u_lows, mode_cfg):
    """Build Plotly candlestick using LTF bars with HTF fractal levels drawn."""
    try:
        df = tv.get_hist(
            symbol   = symbol,
            exchange = exchange,
            interval = mode_cfg["ltf_interval"],
            n_bars   = mode_cfg["chart_bars"],
        )
        if df is None or df.empty:
            return None

        df = df[["open", "high", "low", "close", "volume"]].copy()

        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x                     = df.index,
            open                  = df["open"],
            high                  = df["high"],
            low                   = df["low"],
            close                 = df["close"],
            name                  = mode_cfg["ltf_label"],
            increasing_line_color = "#00e87a",
            decreasing_line_color = "#ff4466",
            increasing_fillcolor  = "rgba(0,232,122,0.25)",
            decreasing_fillcolor  = "rgba(255,68,102,0.25)",
        ))

        for lv in u_highs[-4:]:
            fig.add_hline(
                y                    = lv,
                line_color           = "rgba(255,68,102,0.75)",
                line_dash            = "dash",
                line_width           = 1.5,
                annotation_text      = f"R  {lv:,.2f}",
                annotation_position  = "right",
                annotation_font_size = 12,
                annotation_font_color= "#ff4466",
            )

        for lv in u_lows[:4]:
            fig.add_hline(
                y                    = lv,
                line_color           = "rgba(0,232,122,0.75)",
                line_dash            = "dash",
                line_width           = 1.5,
                annotation_text      = f"S  {lv:,.2f}",
                annotation_position  = "right",
                annotation_font_size = 12,
                annotation_font_color= "#00e87a",
            )

        fig.update_layout(
            paper_bgcolor = "#0b0d12",
            plot_bgcolor  = "#0b0d12",
            font          = dict(family="Nunito", color="#4a6080", size=12),
            title         = dict(
                text  = f"{symbol} — {mode_cfg['ltf_label']} Chart  |  {mode_cfg['htf_label']} Fractal Levels",
                font  = dict(size=15, color="#00c8ff", family="Nunito"),
                x     = 0.01,
            ),
            xaxis  = dict(gridcolor="#141e30", rangeslider=dict(visible=False)),
            yaxis  = dict(gridcolor="#141e30", side="right"),
            margin = dict(l=10, r=110, t=50, b=10),
            height = 460,
            legend = dict(bgcolor="#0f1520", bordercolor="#1a2540", borderwidth=1),
        )
        return fig

    except Exception:
        return None


# ─────────────────────────────────────────────
#  SESSION STATE  INIT
# ─────────────────────────────────────────────
defaults = {
    "tv"           : None,
    "connected"    : False,
    "login_info"   : "",
    "results"      : {},
    "last_scan"    : {},
    "scan_count"   : {},
    "custom_stocks": [],
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:1rem 0 0.5rem;">
        <div style="font-size:1.6rem; font-weight:900; color:#00c8ff; letter-spacing:0.06em;">
            ⬡ FRACTAL
        </div>
        <div style="font-size:0.78rem; font-weight:800; color:#1e2e45;
                    letter-spacing:0.18em; text-transform:uppercase; margin-top:3px;">
            BREAKOUT SCANNER
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── TradingView Login
    st.markdown('<div class="sb-section">TRADINGVIEW LOGIN</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#0a0f1a; border:1px solid #1a2540; border-radius:8px;
                padding:0.8rem 1rem; margin-bottom:0.8rem; font-size:0.8rem;
                font-weight:700; color:#3a5070; line-height:1.9;">
        <div style="color:#ffd600; font-weight:900; margin-bottom:4px;">
            ⚠ Username/Password login is broken in tvdatafeed
        </div>
        TradingView now blocks automated login with captcha.<br>
        Use <span style="color:#00c8ff;">Session Token</span> instead — it works reliably.<br><br>
        <span style="color:#00e87a; font-weight:900;">How to get your token:</span><br>
        1. Open <b>tradingview.com</b> in Chrome/Firefox<br>
        2. Press <b>F12</b> → Application tab → Cookies<br>
        3. Click <b>tradingview.com</b> in the list<br>
        4. Find cookie named <b>sessionid</b><br>
        5. Copy its value and paste below
    </div>
    """, unsafe_allow_html=True)

    login_method = st.radio(
        "Login Method",
        options  = ["Session Token (Recommended)", "Username & Password", "Guest (No Login)"],
        index    = 0,
        key      = "login_method",
        label_visibility = "collapsed",
    )

    tv_token = ""
    tv_user  = ""
    tv_pass  = ""

    if login_method == "Session Token (Recommended)":
        tv_token = st.text_input(
            "Session Token (sessionid cookie)",
            placeholder = "Paste your TradingView sessionid cookie here",
            type        = "password",
            key         = "tv_token_input",
        ).strip()

    elif login_method == "Username & Password":
        st.markdown(
            '<div style="font-size:0.75rem; font-weight:700; color:#ff4466; margin-bottom:4px;">'
            '⚠ May fail due to TradingView captcha — use Session Token if this fails.</div>',
            unsafe_allow_html=True,
        )
        tv_user = st.text_input("Username", placeholder="TradingView username", key="tv_user_input").strip()
        tv_pass = st.text_input("Password", type="password", placeholder="TradingView password", key="tv_pass_input").strip()

    if st.button("🔌  CONNECT TO TRADINGVIEW"):
        with st.spinner("Connecting..."):
            try:
                if login_method == "Session Token (Recommended)" and tv_token:
                    # ── Session token login — most reliable method
                    # tvdatafeed stores token in its auth header directly
                    tv_obj = TvDatafeed()
                    tv_obj.token = tv_token        # inject token directly
                    # Quick validation — try fetching 1 bar of NIFTY
                    test = tv_obj.get_hist("NIFTY", "NSE", interval=Interval.in_daily, n_bars=1)
                    if test is not None and not test.empty:
                        st.session_state.tv        = tv_obj
                        st.session_state.connected = True
                        st.session_state.login_info = f"Session Token ✓"
                        st.success("✅  Connected via Session Token")
                    else:
                        st.error("❌  Token may be invalid or expired. Try refreshing your browser and copying sessionid again.")

                elif login_method == "Username & Password" and tv_user and tv_pass:
                    # ── Username/password — may fail with captcha
                    tv_obj = TvDatafeed(username=tv_user, password=tv_pass)
                    st.session_state.tv        = tv_obj
                    st.session_state.connected = True
                    st.session_state.login_info = f"User: {tv_user}"
                    st.success(f"✅  Logged in as {tv_user}")

                else:
                    # ── Guest / no login
                    tv_obj = TvDatafeed()
                    st.session_state.tv        = tv_obj
                    st.session_state.connected = True
                    st.session_state.login_info = "Guest (limited data)"
                    st.warning("⚠ Connected as Guest — some symbols may be limited")

            except Exception as e:
                err = str(e).lower()
                if "captcha" in err or "recaptcha" in err:
                    st.error("❌  TradingView blocked login with captcha. Please use Session Token method instead.")
                elif "signin" in err or "sign_in" in err:
                    st.error("❌  Login failed. Try Session Token method — see instructions above.")
                else:
                    st.error(f"❌  Connection error: {e}")

    # Show current connection status
    if st.session_state.connected:
        info = st.session_state.get("login_info", "Connected")
        st.markdown(f"""
        <div style="background:#0a1a12; border:1px solid rgba(0,232,122,0.3);
                    border-radius:6px; padding:0.5rem 0.9rem; margin-top:0.4rem;
                    font-size:0.82rem; font-weight:800; color:#00e87a;">
            🟢 {info}
        </div>
        """, unsafe_allow_html=True)

    # ── Scan Mode
    st.markdown('<div class="sb-section">SCAN MODE</div>', unsafe_allow_html=True)
    selected_mode_label = st.radio(
        "Select Mode",
        options = list(SCAN_MODES.keys()),
        index   = 0,
        label_visibility = "collapsed",
    )
    mode_cfg = SCAN_MODES[selected_mode_label]

    # ── Watchlist selector
    st.markdown('<div class="sb-section">WATCHLIST</div>', unsafe_allow_html=True)

    if mode_cfg["key"] == "default":
        # ── 3 universe options for 30-min / 5-min mode
        universe_choice = st.radio(
            "Universe",
            options = [
                "12 Core Stocks",
                "All F&O Stocks",
                "Custom Selection",
            ],
            index = 0,
            key   = "default_universe",
            label_visibility = "collapsed",
        )

        if universe_choice == "12 Core Stocks":
            selected_symbols = [s for s, _ in WATCHLIST_DEFAULT]
            st.markdown(f"""
            <div style="background:#0a0f1a; border:1px solid rgba(0,200,255,0.2);
                        border-radius:8px; padding:0.7rem 1rem; margin-top:0.4rem;">
                <div style="font-size:0.75rem; font-weight:900; color:#1e3050;
                            text-transform:uppercase; letter-spacing:0.1em; margin-bottom:3px;">
                    CORE WATCHLIST
                </div>
                <div style="font-size:0.95rem; font-weight:800; color:#00c8ff;">
                    {len(selected_symbols)} stocks
                </div>
                <div style="font-size:0.75rem; font-weight:700; color:#1e2e45; margin-top:2px;">
                    {", ".join(selected_symbols)}
                </div>
            </div>
            """, unsafe_allow_html=True)

        elif universe_choice == "All F&O Stocks":
            selected_symbols = [s for s, _ in WATCHLIST_FNO]
            st.markdown(f"""
            <div style="background:#0a0f1a; border:1px solid rgba(160,80,255,0.2);
                        border-radius:8px; padding:0.7rem 1rem; margin-top:0.4rem;">
                <div style="font-size:0.75rem; font-weight:900; color:#1e2040;
                            text-transform:uppercase; letter-spacing:0.1em; margin-bottom:3px;">
                    FULL F&O UNIVERSE
                </div>
                <div style="font-size:0.95rem; font-weight:800; color:#c060ff;">
                    {len(selected_symbols)} stocks
                </div>
                <div style="font-size:0.75rem; font-weight:700; color:#1e2e45; margin-top:2px;">
                    All NSE F&O eligible stocks scanned
                </div>
            </div>
            """, unsafe_allow_html=True)

        else:  # Custom Selection
            all_syms = [s for s, _ in WATCHLIST_FNO]
            selected_symbols = st.multiselect(
                "Pick symbols",
                options  = all_syms,
                default  = [s for s, _ in WATCHLIST_DEFAULT],
                key      = "custom_multiselect",
                label_visibility = "collapsed",
            )
            if selected_symbols:
                st.markdown(f"""
                <div style="background:#0a1a12; border:1px solid rgba(0,232,122,0.2);
                            border-radius:8px; padding:0.7rem 1rem; margin-top:0.4rem;">
                    <div style="font-size:0.75rem; font-weight:900; color:#1e4030;
                                text-transform:uppercase; letter-spacing:0.1em; margin-bottom:3px;">
                        CUSTOM SELECTION
                    </div>
                    <div style="font-size:0.95rem; font-weight:800; color:#00e87a;">
                        {len(selected_symbols)} stocks selected
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("Select at least one symbol.")
                selected_symbols = [s for s, _ in WATCHLIST_DEFAULT]

    else:
        # Swing / Positional modes always use full F&O list
        selected_symbols = [s for s, _ in WATCHLIST_FNO]
        st.markdown(f"""
        <div style="background:#0a0f1a; border:1px solid #141e30; border-radius:8px;
                    padding:0.8rem 1rem; margin-top:0.4rem;">
            <div style="font-size:0.78rem; font-weight:900; color:#2e4060;
                        text-transform:uppercase; letter-spacing:0.1em; margin-bottom:4px;">
                F&O UNIVERSE
            </div>
            <div style="font-size:1rem; font-weight:800; color:#c060ff;">
                {len(WATCHLIST_FNO)} Stocks
            </div>
            <div style="font-size:0.78rem; font-weight:700; color:#1e2e45; margin-top:2px;">
                Full F&O watchlist — all scanned
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Strategy params
    st.markdown('<div class="sb-section">FRACTAL SETTINGS</div>', unsafe_allow_html=True)
    strength     = st.slider("Fractal Strength (candles each side)", 1, 4, 2)
    max_recovery = st.slider(
        "Close Break — Max Recovery Candles",
        min_value = 1,
        max_value = 5,
        value     = 2,
        help      = (
            "How many LTF candles after the close-break are allowed to recover.\n\n"
            "1 = immediate next candle must close back (strictest — A+ only)\n"
            "2 = break candle + 1 intermediate = recommended\n"
            "5 = original loose rule"
        ),
    )
    st.markdown(f"""
    <div style="background:#0a0f1a; border:1px solid #1a2540; border-radius:6px;
                padding:0.6rem 0.9rem; margin-top:0.3rem; font-size:0.78rem;
                font-weight:700; color:#2e4060; line-height:1.8;">
        <span style="color:#00c8ff;">Close Break rule:</span><br>
        Break candle closes beyond level<br>
        → recovery within
        <span style="color:#ffd600;">{max_recovery}</span>
        candle{'s' if max_recovery > 1 else ''} closes back<br>
        <span style="color:#00e87a;">
            {'⚡ Strictest — A+ setups only' if max_recovery == 1 else
             '✅ Recommended — strong reversals' if max_recovery == 2 else
             '⚠ Loose — more signals, lower quality' if max_recovery >= 4 else
             '👍 Balanced'}
        </span>
    </div>
    """, unsafe_allow_html=True)
    show_chart = st.checkbox("Show Chart on Alert", value=True)

    # ── Scan controls
    st.markdown('<div class="sb-section">SCAN CONTROLS</div>', unsafe_allow_html=True)
    scan_btn = st.button("⚡  RUN SCAN NOW")
    auto_ref = st.checkbox("Auto Refresh", value=False)
    ref_mins = st.selectbox("Refresh Every", [1, 2, 5, 10, 15], index=2,
                             format_func=lambda x: f"{x} minutes")

    # ── Custom Stocks
    st.markdown('<div class="sb-section">ADD CUSTOM STOCKS</div>', unsafe_allow_html=True)

    col_sym, col_exch = st.columns([2, 1])
    with col_sym:
        new_symbol = st.text_input(
            "Symbol", placeholder="e.g. ZOMATO",
            label_visibility="collapsed", key="input_symbol"
        ).strip().upper()
    with col_exch:
        new_exchange = st.selectbox(
            "Exchange", ["NSE", "BSE"],
            label_visibility="collapsed", key="input_exchange"
        )

    col_add, col_clear = st.columns(2)
    with col_add:
        if st.button("➕  ADD", key="btn_add"):
            if new_symbol:
                existing = [s for s, _ in st.session_state.custom_stocks]
                if new_symbol in existing:
                    st.warning(f"{new_symbol} already added.")
                else:
                    st.session_state.custom_stocks.append((new_symbol, new_exchange))
                    st.success(f"✅ {new_symbol} added!")
            else:
                st.warning("Enter a symbol first.")

    with col_clear:
        if st.button("🗑  CLEAR", key="btn_clear"):
            st.session_state.custom_stocks = []
            st.success("Cleared all custom stocks.")

    # Show current custom list
    if st.session_state.custom_stocks:
        custom_count = len(st.session_state.custom_stocks)
        custom_names = ", ".join([s for s, _ in st.session_state.custom_stocks])
        st.markdown(f"""
        <div style="background:#0a1a12; border:1px solid rgba(0,232,122,0.25);
                    border-radius:8px; padding:0.75rem 1rem; margin-top:0.5rem;">
            <div style="font-size:0.75rem; font-weight:900; color:#1e4030;
                        text-transform:uppercase; letter-spacing:0.1em; margin-bottom:4px;">
                Custom Stocks Added
            </div>
            <div style="font-size:0.92rem; font-weight:800; color:#00e87a;">
                {custom_count} stock{'s' if custom_count > 1 else ''}
            </div>
            <div style="font-size:0.78rem; font-weight:700; color:#1e4030;
                        margin-top:3px; word-break:break-word;">
                {custom_names}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Allow removing individual stocks
        remove_sym = st.selectbox(
            "Remove a stock",
            options=["— select to remove —"] + [s for s, _ in st.session_state.custom_stocks],
            label_visibility="collapsed", key="remove_select"
        )
        if remove_sym != "— select to remove —":
            if st.button(f"❌  Remove {remove_sym}", key="btn_remove"):
                st.session_state.custom_stocks = [
                    (s, e) for s, e in st.session_state.custom_stocks if s != remove_sym
                ]
                st.success(f"Removed {remove_sym}.")

    # Strategy reminder
    if mode_cfg["key"] == "default":
        universe_label = (
            "12 Core Stocks" if universe_choice == "12 Core Stocks"
            else "All F&O Stocks" if universe_choice == "All F&O Stocks"
            else "Custom Selection"
        )
    else:
        universe_label = "Full F&O Universe"

    total_scan_count = len(selected_symbols) + len(st.session_state.custom_stocks)
    st.markdown(f"""
    <div style="margin-top:1.5rem; background:#0a0f1a; border:1px solid #141e30;
                border-radius:8px; padding:1rem; font-size:0.82rem;
                font-weight:700; color:#2a3e58; line-height:2;">
        <div style="font-size:0.75rem; font-weight:900; color:#1e3050;
                    text-transform:uppercase; letter-spacing:0.1em; margin-bottom:6px;">
            ACTIVE MODE
        </div>
        HTF: <span style="color:#00c8ff;">{mode_cfg['htf_label']}</span> (fractals)<br>
        LTF: <span style="color:#00e87a;">{mode_cfg['ltf_label']}</span> (entry signal)<br>
        Universe: <span style="color:#ffd600;">{universe_label}</span><br>
        Predefined: <span style="color:#ffd600;">{len(selected_symbols)}</span> &nbsp;+&nbsp;
        Custom: <span style="color:#00e87a;">{len(st.session_state.custom_stocks)}</span><br>
        Total: <span style="color:#00c8ff;">{total_scan_count}</span> stocks
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  TOP BANNER
# ─────────────────────────────────────────────
_now     = now_ist()
now_str  = _now.strftime("%d %b %Y   %H:%M:%S") + " IST"
mkt_open = is_market_open()
mkt_html = ('<span class="live-dot"></span><span class="mkt-open">MARKET OPEN</span>'
            if mkt_open else '<span class="mkt-close">⬛  MARKET CLOSED</span>')

st.markdown(f"""
<div class="top-banner">
    <div>
        <div class="banner-title">📊 FRACTAL BREAKOUT SCANNER</div>
        <div class="banner-sub">
            Multi-Timeframe · Unmitigated Fractal Levels · F&O Universe
        </div>
    </div>
    <div class="banner-right">
        <div>{mkt_html}</div>
        <div class="banner-time">{now_str}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  CONNECTION GUARD
# ─────────────────────────────────────────────
if not st.session_state.connected:
    st.markdown("""
    <div class="no-alert-box">
        <div class="big-icon">🔌</div>
        <div style="font-size:1.1rem; font-weight:900; color:#3a5070; margin-bottom:6px;">
            Not Connected to TradingView
        </div>
        <div style="font-size:0.92rem; font-weight:700; color:#1e2e45;">
            Enter credentials in the sidebar and click<br>
            <span style="color:#00c8ff;">CONNECT TO TRADINGVIEW</span><br><br>
            Leave blank for Guest access.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ─────────────────────────────────────────────
#  MAIN TABS
# ─────────────────────────────────────────────
tab_scan, tab_levels, tab_about = st.tabs([
    "⚡  LIVE SCAN",
    "📋  LEVEL TABLE",
    "ℹ  ABOUT",
])


# ══════════════════════════════════════════════
#  SHARED RENDER FUNCTION
#  — renders alerts + quiet cards for any mode
# ══════════════════════════════════════════════
def render_scan_results(results, mode_cfg, show_chart_flag):
    """Render metrics, alert cards, quiet cards, errors for a given result set."""
    if not results:
        st.markdown("""
        <div class="no-alert-box">
            <div class="big-icon">⚡</div>
            <div style="font-size:1.1rem; font-weight:900; color:#3a5070; margin-bottom:6px;">
                Ready to Scan
            </div>
            <div style="font-size:0.92rem; font-weight:700; color:#1e2e45;">
                Click <span style="color:#00e87a;">RUN SCAN NOW</span> in the sidebar
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    alerts   = [r for r in results if r["alert"] and r["status"] == "OK"]
    bullish  = [r for r in alerts  if r["direction"] == "BULLISH_SETUP"]
    bearish  = [r for r in alerts  if r["direction"] == "BEARISH_SETUP"]
    cl_brk   = [r for r in alerts  if r["sweep_type"] == "CLOSE_BREAK"]
    wick_sw  = [r for r in alerts  if r["sweep_type"] == "WICK_SWEEP"]
    quiet    = [r for r in results if not r["alert"] and r["status"] == "OK"]
    errors   = [r for r in results if r["status"] == "ERROR"]

    mode_key = mode_cfg["key"]
    mk        = st.session_state
    last_scan = mk["last_scan"].get(mode_key, "—")
    scn_count = mk["scan_count"].get(mode_key, 0)

    # Badge
    st.markdown(
        f'<div class="mode-badge {mode_cfg["badge_cls"]}">'
        f'{mode_cfg["htf_label"]} fractals  →  {mode_cfg["ltf_label"]} signal'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Metrics
    a_col = "col-green" if alerts else "col-yellow"
    st.markdown(f"""
    <div class="metrics-row">
        <div class="metric-box"><div class="m-label">Scanned</div><div class="m-value col-cyan">{len(results)}</div></div>
        <div class="metric-box"><div class="m-label">Alerts</div><div class="m-value {a_col}">{len(alerts)}</div></div>
        <div class="metric-box"><div class="m-label">Bullish</div><div class="m-value col-green">{len(bullish)}</div></div>
        <div class="metric-box"><div class="m-label">Bearish</div><div class="m-value col-red">{len(bearish)}</div></div>
        <div class="metric-box"><div class="m-label">Close Break</div><div class="m-value col-cyan">{len(cl_brk)}</div></div>
        <div class="metric-box"><div class="m-label">Wick Sweep</div><div class="m-value col-yellow">{len(wick_sw)}</div></div>
    </div>
    """, unsafe_allow_html=True)

    # Status bar
    st.markdown(f"""
    <div class="status-bar">
        Last Scan: <span>{last_scan}</span>
        &nbsp;|&nbsp; Scans: <span>{scn_count}</span>
        &nbsp;|&nbsp; HTF: <span>{mode_cfg['htf_label']}</span>
        &nbsp;|&nbsp; LTF: <span>{mode_cfg['ltf_label']}</span>
        &nbsp;|&nbsp; Fractal: <span>{strength}</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Alert Cards
    st.markdown("### 🚨 ALERTS")

    if not alerts:
        st.markdown("""
        <div class="no-alert-box">
            <div class="big-icon">🔍</div>
            <div style="font-size:1rem; font-weight:900; color:#2e4060;">
                No breakouts detected right now
            </div>
            <div style="font-size:0.88rem; font-weight:700; color:#1a2a3a; margin-top:6px;">
                All fractal levels intact — click Scan to refresh
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for r in alerts:
            is_bull  = r["direction"] == "BULLISH_SETUP"
            card_cls = "card-bull" if is_bull else "card-bear"
            sym_col  = "#00e87a" if is_bull else "#ff4466"
            icon     = "🟢" if is_bull else "🔴"
            dir_lbl  = ("BULLISH — Bull Put Spread" if is_bull
                        else "BEARISH — Bear Call Spread")
            dir_tag  = "tag-bull" if is_bull else "tag-bear"
            swp_tag  = "tag-close" if r["sweep_type"] == "CLOSE_BREAK" else "tag-wick"
            swp_lbl  = r["sweep_type"].replace("_", " ")
            tf_tag   = mode_cfg["tag_cls"]
            tf_lbl   = f"{r['htf_label']} → {r['ltf_label']}"

            chg     = (r["current_price"] or 0) - (r["candle_open"] or 0)
            chg_col = "#00e87a" if chg >= 0 else "#ff4466"
            chg_str = (f'<span style="color:{chg_col}; font-size:1rem; font-weight:800;">'
                       f'({("+" if chg>=0 else "")}{chg:.2f})</span>')

            st.markdown(f"""
            <div class="alert-card {card_cls}">
                <div class="card-top">
                    <div>
                        <div class="card-symbol" style="color:{sym_col};">
                            {icon}  {r['symbol']}
                        </div>
                        <div class="card-tags">
                            <span class="tag {dir_tag}">{dir_lbl}</span>
                            <span class="tag {swp_tag}">{swp_lbl}</span>
                            <span class="tag {tf_tag}">{tf_lbl}</span>
                        </div>
                    </div>
                    <div style="text-align:right;">
                        <div class="card-ltp" style="color:{sym_col};">₹{r['current_price']:,}</div>
                        {chg_str}
                    </div>
                </div>
                <div class="pgrid">
                    <div class="pgrid-item">
                        <div class="pgrid-label">Swept Level</div>
                        <div class="pgrid-value" style="color:{sym_col};">₹{r['broken_level']:,}</div>
                    </div>
                    <div class="pgrid-item">
                        <div class="pgrid-label">SL Reference</div>
                        <div class="pgrid-value" style="color:#ff4466;">
                            ₹{r['break_candle_low'] if is_bull else r['break_candle_high']}
                        </div>
                    </div>
                    <div class="pgrid-item">
                        <div class="pgrid-label">{r['ltf_label']} High</div>
                        <div class="pgrid-value">₹{r['candle_high']:,}</div>
                    </div>
                    <div class="pgrid-item">
                        <div class="pgrid-label">{r['ltf_label']} Low</div>
                        <div class="pgrid-value">₹{r['candle_low']:,}</div>
                    </div>
                    <div class="pgrid-item">
                        <div class="pgrid-label">Candle Time</div>
                        <div class="pgrid-value">{r['candle_time']}</div>
                    </div>
                    <div class="pgrid-item">
                        <div class="pgrid-label">Recovery</div>
                        <div class="pgrid-value" style="color:#ffd600;">
                            {(str(r['recovery_candles']) + " candle" + ("s" if r['recovery_candles'] and r['recovery_candles'] > 1 else "")) if r.get('recovery_candles') else "Wick sweep"}
                        </div>
                    </div>
                </div>
                <a class="tv-btn" href="{r['chart_url']}" target="_blank">
                    ↗ Open TradingView Chart
                </a>
            </div>
            """, unsafe_allow_html=True)

            if show_chart_flag:
                with st.expander(
                    f"📈  {r['symbol']}  —  {r['ltf_label']} Chart", expanded=True
                ):
                    fig = build_chart(
                        r["symbol"], r["exchange"],
                        st.session_state.tv,
                        r["unmitigated_highs"], r["unmitigated_lows"],
                        mode_cfg,
                    )
                    if fig:
                        st.plotly_chart(fig, width="stretch",
                                        config={"displayModeBar": False},
                                        key=f"chart_{mode_cfg['key']}_{r['symbol']}")
                    else:
                        st.info("Chart data unavailable.")

    # ── Quiet symbols
    if quiet:
        st.markdown("### ✅ MONITORING — No Alert")
        cols = st.columns(4)
        for idx, r in enumerate(quiet):
            uh_str = "  ".join([f"₹{x:,.0f}" for x in r["unmitigated_highs"][-2:]]) or "—"
            ul_str = "  ".join([f"₹{x:,.0f}" for x in r["unmitigated_lows"][:2]])  or "—"
            with cols[idx % 4]:
                st.markdown(f"""
                <div class="q-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div class="q-symbol">{r['symbol']}</div>
                        <div class="q-ltp">₹{r['current_price']:,}</div>
                    </div>
                    <div class="q-level-label">Resistance</div>
                    <div class="q-levels" style="color:#ff6680;">{uh_str}</div>
                    <div class="q-level-label">Support</div>
                    <div class="q-levels" style="color:#00c870;">{ul_str}</div>
                    <div style="font-size:0.75rem; font-weight:700; color:#1e2e45; margin-top:6px;">
                        {r['candle_time']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ── Errors
    if errors:
        with st.expander(f"⚠  {len(errors)} symbol(s) had errors"):
            for r in errors:
                st.markdown(f"**{r['symbol']}** — {r['error']}")


# ══════════════════════════════════════════════
#  TAB 1  —  LIVE SCAN
# ══════════════════════════════════════════════
with tab_scan:

    mode_key = mode_cfg["key"]

    # ── Run scan if button pressed
    if scan_btn:
        tv  = st.session_state.tv

        # Build base watchlist for this mode
        # selected_symbols already contains the correct list based on universe choice
        if mode_cfg["key"] == "default":
            # Build exchange lookup from both watchlists combined
            exch_lookup = {s: e for s, e in WATCHLIST_DEFAULT + WATCHLIST_FNO}
            wl = [(s, exch_lookup.get(s, "NSE")) for s in selected_symbols]
        else:
            wl = list(mode_cfg["watchlist"])

        # Merge custom stocks (avoid duplicates)
        existing_syms = {s for s, _ in wl}
        for s, e in st.session_state.custom_stocks:
            if s not in existing_syms:
                wl.append((s, e))

        results = []
        prog    = st.progress(0, text="Starting scan...")
        total   = len(wl)

        for idx, (sym, exch) in enumerate(wl):
            prog.progress(idx / total, text=f"Scanning {sym}...  ({idx+1}/{total})")
            r = check_breakout(sym, exch, tv, mode_cfg, strength, max_recovery)
            results.append(r)
            time.sleep(0.6)

        prog.progress(1.0, text="Scan complete ✓")
        time.sleep(0.4)
        prog.empty()

        st.session_state["results"][mode_key]    = results
        st.session_state["last_scan"][mode_key]  = now_ist().strftime("%H:%M:%S IST")
        st.session_state["scan_count"][mode_key] = \
            st.session_state["scan_count"].get(mode_key, 0) + 1

    # ── Render results for current mode
    results = st.session_state["results"].get(mode_key, [])
    render_scan_results(results, mode_cfg, show_chart)

    # ── Auto refresh
    if auto_ref and st.session_state["last_scan"].get(mode_key):
        st.markdown("---")
        cd = st.empty()
        for secs in range(ref_mins * 60, 0, -1):
            m, s = divmod(secs, 60)
            cd.markdown(
                f'<div style="text-align:center; font-size:0.95rem; font-weight:800; color:#1e2e45;">'
                f'Next scan in &nbsp;<span style="color:#4499ff;">{m:02d}:{s:02d}</span></div>',
                unsafe_allow_html=True,
            )
            time.sleep(1)
        st.rerun()


# ══════════════════════════════════════════════
#  TAB 2  —  LEVEL TABLE
# ══════════════════════════════════════════════
with tab_levels:
    st.markdown("### 📋 Unmitigated Fractal Levels")

    mode_key = mode_cfg["key"]
    results  = st.session_state["results"].get(mode_key, [])

    if not results:
        st.info("Run a scan first to populate levels.")
    else:
        st.markdown(
            f'<div style="font-size:0.9rem; font-weight:700; color:#2e4060; margin-bottom:1.2rem;">'
            f'Mode: <span style="color:#00c8ff;">{mode_cfg["htf_label"]} fractals</span> &nbsp;|&nbsp; '
            f'Monitoring: <span style="color:#00e87a;">{mode_cfg["ltf_label"]}</span> &nbsp;|&nbsp; '
            f'{len([r for r in results if r["status"]=="OK"])} symbols loaded</div>',
            unsafe_allow_html=True,
        )

        for r in results:
            if r["status"] == "ERROR":
                continue
            uh = r["unmitigated_highs"]
            ul = r["unmitigated_lows"]

            col_a, col_b = st.columns([1, 3])
            with col_a:
                alert_clr = ("#00e87a" if r.get("direction") == "BULLISH_SETUP"
                             else "#ff4466" if r.get("direction") == "BEARISH_SETUP"
                             else "#00c8ff")
                st.markdown(f"""
                <div style="font-size:1.3rem; font-weight:900; color:{alert_clr}; margin-bottom:4px;">
                    {r['symbol']}
                    {'  🟢' if r.get('direction')=='BULLISH_SETUP' else
                     '  🔴' if r.get('direction')=='BEARISH_SETUP' else ''}
                </div>
                <div style="font-size:1rem; font-weight:800; color:#4499ff;">
                    ₹{r['current_price']:,}
                </div>
                """, unsafe_allow_html=True)

            with col_b:
                rows = (
                    [(f"₹{x:,.2f}", "RESISTANCE", "#ff4466") for x in reversed(uh[-4:])] +
                    [(f"₹{x:,.2f}", "SUPPORT",    "#00e87a") for x in ul[:4]]
                )
                if rows:
                    table_html = """<table class="lvl-table">
                    <tr><th>Level</th><th>Type</th><th>Status</th></tr>"""
                    for (price, typ, clr) in rows:
                        table_html += f"""
                        <tr>
                            <td style="color:{clr}; font-weight:900; font-size:1rem;">{price}</td>
                            <td style="color:#4a6080;">{typ}</td>
                            <td style="color:#2e4060;">UNMITIGATED</td>
                        </tr>"""
                    table_html += "</table>"
                    st.markdown(table_html, unsafe_allow_html=True)
                else:
                    st.markdown(
                        '<div style="font-size:0.9rem; font-weight:700; color:#1e2e45;">'
                        'No unmitigated levels found</div>',
                        unsafe_allow_html=True,
                    )
            st.markdown("<hr>", unsafe_allow_html=True)


# ══════════════════════════════════════════════
#  TAB 3  —  ABOUT
# ══════════════════════════════════════════════
with tab_about:
    st.markdown("""
    <div style="max-width:760px; line-height:1.9;">

    <div style="font-size:1.5rem; font-weight:900; color:#00c8ff; margin-bottom:1.2rem;">
        About This Scanner
    </div>

    <div style="background:#0f1520; border:1px solid #1a2540; border-radius:10px;
                padding:1.2rem 1.5rem; margin-bottom:1.2rem;">
        <div style="font-size:0.8rem; font-weight:900; color:#1e3050;
                    text-transform:uppercase; letter-spacing:0.12em; margin-bottom:0.7rem;">
            THREE SCAN MODES
        </div>
        <div style="font-size:0.95rem; font-weight:700; color:#4a6080; line-height:2.4;">
            <span style="color:#00c8ff;">30-Min / 5-Min (Default)</span><br>
            &nbsp;&nbsp;▸ Mark unmitigated fractals on 30-min chart<br>
            &nbsp;&nbsp;▸ Monitor 5-min candle for sweep signal<br>
            &nbsp;&nbsp;▸ 12 core F&O stocks<br><br>
            <span style="color:#c060ff;">1-Week / 1-Day (Swing)</span><br>
            &nbsp;&nbsp;▸ Mark unmitigated fractals on Weekly chart<br>
            &nbsp;&nbsp;▸ Monitor Daily candle for sweep signal<br>
            &nbsp;&nbsp;▸ Full F&O universe (~70 stocks)<br><br>
            <span style="color:#ffa020;">1-Day / 1-Hour (Positional)</span><br>
            &nbsp;&nbsp;▸ Mark unmitigated fractals on Daily chart<br>
            &nbsp;&nbsp;▸ Monitor 1-Hour candle for sweep signal<br>
            &nbsp;&nbsp;▸ Full F&O universe (~70 stocks)
        </div>
    </div>

    <div style="background:#0f1520; border:1px solid #1a2540; border-radius:10px;
                padding:1.2rem 1.5rem; margin-bottom:1.2rem;">
        <div style="font-size:0.8rem; font-weight:900; color:#1e3050;
                    text-transform:uppercase; letter-spacing:0.12em; margin-bottom:0.7rem;">
            SAME LOGIC ACROSS ALL MODES
        </div>
        <div style="font-size:0.95rem; font-weight:700; color:#4a6080; line-height:2.2;">
            <span style="color:#00e87a;">1.</span> HTF: Identify unmitigated fractal Highs & Lows<br>
            <span style="color:#00e87a;">2.</span> LTF candle CLOSES beyond level → CLOSE BREAK alert<br>
            <span style="color:#00e87a;">3.</span> LTF candle WICKS beyond level → WICK SWEEP alert<br>
            <span style="color:#00e87a;">4.</span> Stop Loss: low/high of the sweep candle<br>
            <span style="color:#00e87a;">5.</span> Target: nearest LTF fractal High/Low<br>
            <span style="color:#00e87a;">6.</span> Max 1 trade per signal
        </div>
    </div>

    <div style="background:#0f1520; border:1px solid #1a2540; border-radius:10px;
                padding:1.2rem 1.5rem; margin-bottom:1.2rem;">
        <div style="font-size:0.8rem; font-weight:900; color:#1e3050;
                    text-transform:uppercase; letter-spacing:0.12em; margin-bottom:0.7rem;">
            CREDIT SPREAD STRUCTURE
        </div>
        <div style="font-size:0.95rem; font-weight:700; color:#4a6080; line-height:2.2;">
            <span style="color:#00c8ff;">Bullish Setup</span> →
            Bull Put Spread: SELL 200 OTM Put | BUY 400 OTM Put<br>
            <span style="color:#ff4466;">Bearish Setup</span> →
            Bear Call Spread: SELL 200 OTM Call | BUY 400 OTM Call<br>
            <span style="color:#ffd600;">Expiry Rule</span> →
            Current week until 2 days before expiry → switch to next week
        </div>
    </div>

    <div style="background:#0f1520; border:1px solid #1a2540; border-radius:10px;
                padding:1.2rem 1.5rem;">
        <div style="font-size:0.8rem; font-weight:900; color:#1e3050;
                    text-transform:uppercase; letter-spacing:0.12em; margin-bottom:0.7rem;">
            DATA SOURCE
        </div>
        <div style="font-size:0.95rem; font-weight:700; color:#4a6080; line-height:2.2;">
            <span style="color:#00c8ff;">tvdatafeed</span> — TradingView real-time data<br>
            Login with TradingView account for best quality<br>
            Guest mode works but may have rate limits on large scans<br>
            <span style="color:#ffd600;">Tip:</span> For 70-stock F&O scans, TradingView login recommended
        </div>
    </div>

    </div>
    """, unsafe_allow_html=True)
