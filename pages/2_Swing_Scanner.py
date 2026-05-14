"""
NSE Swing Signal Scanner — Page 2
===================================
Part of the Fractal Trading Suite multi-page app.
Run from the scanner_app/ folder:
    streamlit run Home.py

Requirements:
    pip install streamlit tvdatafeed pandas pandas-ta-classic plotly
"""

import time
import warnings
import pandas as pd
import streamlit as st

warnings.filterwarnings("ignore")

try:
    import pandas_ta_classic as ta
except ImportError:
    st.error("Missing library: `pip install pandas-ta-classic`")
    st.stop()

try:
    from tvdatafeed import TvDatafeed, Interval
except ImportError:
    try:
        from tvDatafeed import TvDatafeed, Interval
    except ImportError:
        st.error("Missing library: `pip install tvdatafeed`")
        st.stop()

# page_config is set in Home.py — do not duplicate here

# ─────────────────────────────────────────────────────────────────────────────
# CSS — matched to the dark Nunito theme of the suite
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@600;700;800;900&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Nunito', sans-serif !important;
    background-color: #0b0d12 !important;
    color: #e8ecf5 !important;
}
.block-container { padding: 1.4rem 2rem !important; max-width: 100% !important; }
footer { visibility: hidden; }
#MainMenu { visibility: hidden; }

/* ── Banner ── */
.swing-banner {
    background: linear-gradient(120deg, #0e131f 0%, #12201a 60%, #0e131f 100%);
    border: 1px solid #1a3028;
    border-top: 3px solid #00e87a;
    border-radius: 12px;
    padding: 1.4rem 2rem;
    margin-bottom: 1.4rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.swing-title { font-size: 2rem; font-weight: 900; color: #00e87a; letter-spacing: 0.04em; }
.swing-sub   { font-size: 1rem; font-weight: 700; color: #2e5040; margin-top: 4px; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] { background: #090c14 !important; border-right: 1px solid #141e30 !important; }
section[data-testid="stSidebar"] .block-container { padding: 1rem 1.2rem !important; }
.sb-section {
    font-size: 0.78rem; font-weight: 900; text-transform: uppercase;
    letter-spacing: 0.12em; color: #2e4060; border-bottom: 1px solid #141e30;
    padding-bottom: 5px; margin: 1.2rem 0 0.7rem;
}
label, .stCheckbox label {
    font-family: 'Nunito', sans-serif !important;
    font-size: 0.92rem !important; font-weight: 700 !important; color: #7a90b0 !important;
}
.stButton button {
    background: #0d2a1a !important; color: #00e87a !important;
    border: 2px solid rgba(0,232,122,0.4) !important;
    font-family: 'Nunito', sans-serif !important; font-size: 0.95rem !important;
    font-weight: 900 !important; border-radius: 8px !important;
    padding: 0.55rem 1.2rem !important; width: 100% !important;
    text-transform: uppercase !important;
}
.stButton button:hover { background: #143d22 !important; }
.stTabs [data-baseweb="tab-list"] {
    background: #0f1520 !important; border-radius: 8px !important;
    padding: 4px !important; border: 1px solid #1a2540 !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Nunito', sans-serif !important; font-size: 0.9rem !important;
    font-weight: 800 !important; color: #3a5070 !important; border-radius: 6px !important;
}
.stTabs [aria-selected="true"] { background: #141e30 !important; color: #00e87a !important; }

/* ── Universe selector ── */
.universe-header {
    font-size: 1rem; font-weight: 900; color: #e8ecf5;
    margin-bottom: 0.6rem; margin-top: 0.4rem;
}
.universe-sub {
    font-size: 0.82rem; font-weight: 700; color: #2e4060; margin-bottom: 1rem;
}

/* ── Summary cards ── */
.metric-row { display: flex; gap: 1rem; margin-bottom: 1.4rem; flex-wrap: wrap; }
.metric-card {
    flex: 1; min-width: 110px;
    background: #0f1520; border-radius: 10px;
    padding: 1rem 1.2rem; border-left: 4px solid #00c8ff;
    text-align: center;
}
.metric-card.buy   { border-color: #00e87a; }
.metric-card.sell  { border-color: #ff4466; }
.metric-card.bull  { border-color: #69f0ae; }
.metric-card.bear  { border-color: #ff6d00; }
.metric-card .val  { font-size: 2rem; font-weight: 900; color: #e8ecf5; line-height: 1.1; }
.metric-card .lbl  { font-size: 0.78rem; font-weight: 800; color: #3a5070; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.06em; }

/* ── Badges ── */
.badge {
    display: inline-block; border-radius: 5px;
    padding: 3px 9px; font-size: 0.78rem; font-weight: 800; margin: 1px 2px;
}
.badge-buy  { background: #00e87a; color: #000; }
.badge-sell { background: #ff4466; color: #fff; }
.badge-bull { background: #69f0ae; color: #000; }
.badge-bear { background: #ff6d00; color: #fff; }

/* ── Log box ── */
.log-box {
    background: #0a0f1a; border: 1px solid #1a2540; border-radius: 8px;
    padding: 0.8rem 1.2rem; font-family: 'Courier New', monospace;
    font-size: 0.82rem; color: #3a5070;
    max-height: 220px; overflow-y: auto; margin-bottom: 1rem;
}
.log-ok  { color: #1a4030; }
.log-err { color: #6a1020; }
.log-sig { color: #c0a020; font-weight: 800; }

/* ── Results table ── */
table { width: 100%; border-collapse: collapse; font-size: 0.9rem; font-weight: 700; }
th {
    background: #0f1520; color: #3a5070; padding: 0.6rem 0.9rem;
    text-align: left; font-size: 0.8rem; font-weight: 900;
    text-transform: uppercase; letter-spacing: 0.08em;
    border-bottom: 1px solid #1a2540;
}
td { padding: 0.55rem 0.9rem; border-bottom: 1px solid #141e30; color: #c0c8d8; }
tr:hover td { background: #0f1520; }

/* ── Signal info table ── */
.sig-table { width: 100%; border-collapse: collapse; font-size: 0.92rem; font-weight: 700; margin-top: 0.5rem; }
.sig-table th { background: #0f1520; color: #3a5070; padding: 8px 12px; text-align: left; font-size: 0.8rem; font-weight: 900; text-transform: uppercase; letter-spacing: 0.08em; border-bottom: 1px solid #1a2540; }
.sig-table td { padding: 8px 12px; border-bottom: 1px solid #141e30; color: #c0c8d8; }

/* ── Universe grid ── */
.universe-grid { display: flex; flex-wrap: wrap; gap: 0.4rem; margin-top: 0.5rem; }
.sym-chip {
    background: #0f1520; border: 1px solid #1a2540; border-radius: 5px;
    padding: 3px 10px; font-size: 0.78rem; font-weight: 800; color: #4a6080;
}

hr { border-color: #141e30 !important; margin: 1rem 0 !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Stock Universe
# ─────────────────────────────────────────────────────────────────────────────
UNIVERSE = {
    "🏆 Nifty 50": [
        "RELIANCE", "TCS", "HDFCBANK", "BHARTIARTL", "ICICIBANK",
        "INFOSYS", "SBIN", "HINDUNILVR", "ITC", "LT",
        "KOTAKBANK", "AXISBANK", "BAJFINANCE", "MARUTI", "HCLTECH",
        "SUNPHARMA", "TITAN", "ULTRACEMCO", "WIPRO", "NTPC",
        "POWERGRID", "ONGC", "TATAMOTORS", "TECHM", "ADANIPORTS",
        "ASIANPAINT", "BAJAJFINSV", "COALINDIA", "GRASIM", "HINDALCO",
        "JSWSTEEL", "M&M", "NESTLEIND", "TATASTEEL", "TATACONSUM",
        "DRREDDY", "CIPLA", "DIVISLAB", "BPCL", "EICHERMOT",
        "HEROMOTOCO", "INDUSINDBK", "BRITANNIA", "APOLLOHOSP", "ADANIENT",
        "SHRIRAMFIN", "TRENT", "BEL", "JIOFIN", "ZOMATO",
    ],
    "🥈 Nifty Next 50": [
        "ABB", "ADANIGREEN", "ADANITRANS", "AMBUJACEM", "AUROPHARMA",
        "BAJAJ-AUTO", "BANKBARODA", "BERGEPAINT", "BHEL", "BOSCHLTD",
        "CANBK", "CHOLAFIN", "COLPAL", "CONCOR", "DABUR",
        "DLF", "GAIL", "GODREJCP", "HAVELLS", "ICICIPRULI",
        "INDHOTEL", "INDUSTOWER", "IOC", "IRFC", "LODHA",
        "LUPIN", "MARICO", "MUTHOOTFIN", "NAUKRI", "NHPC",
        "NMDC", "PAGEIND", "PFC", "PIDILITIND", "POLYCAB",
        "PNB", "RECLTD", "SAIL", "SBICARD", "SBILIFE",
        "SHREECEM", "SIEMENS", "TORNTPHARM", "TVSMOTOR", "UPL",
        "VEDL", "VOLTAS", "ZYDUSLIFE", "TORNTPOWER", "ONGC",
    ],
    "🏦 Banking & Finance": [
        "HDFCBANK", "ICICIBANK", "SBIN", "KOTAKBANK", "AXISBANK",
        "INDUSINDBK", "BANKBARODA", "PNB", "CANBK", "FEDERALBNK",
        "IDFCFIRSTB", "BAJFINANCE", "BAJAJFINSV", "CHOLAFIN", "MUTHOOTFIN",
        "MANAPPURAM", "SBICARD", "SBILIFE", "HDFCLIFE", "ICICIPRULI",
        "ICICIGI", "PFC", "RECLTD", "IRFC", "SHRIRAMFIN",
    ],
    "💻 IT & Technology": [
        "TCS", "INFOSYS", "HCLTECH", "WIPRO", "TECHM",
        "LTIM", "MPHASIS", "COFORGE", "LTTS", "OFSS",
        "PERSISTENT", "KPITTECH", "TATAELXSI", "NAUKRI", "ZOMATO",
    ],
    "💊 Pharma & Healthcare": [
        "SUNPHARMA", "DRREDDY", "CIPLA", "DIVISLAB", "LUPIN",
        "AUROPHARMA", "BIOCON", "TORNTPHARM", "ALKEM", "IPCALAB",
        "NATCOPHARM", "GRANULES", "LAURUSLABS", "ZYDUSLIFE", "APOLLOHOSP",
        "MAXHEALTH", "FORTIS", "METROPOLIS", "LALPATHLAB",
    ],
    "🚗 Auto & Ancillary": [
        "MARUTI", "TATAMOTORS", "M&M", "BAJAJ-AUTO", "HEROMOTOCO",
        "EICHERMOT", "TVSMOTOR", "BOSCHLTD", "MOTHERSON", "EXIDEIND",
        "AMARAJABAT", "APOLLOTYRE", "MRF", "CEATLTD", "BALKRISIND",
        "TIINDIA", "SCHAEFFLER", "ESCORTS", "SWARAJENG",
    ],
    "🏗️ Metal & Mining": [
        "TATASTEEL", "JSWSTEEL", "HINDALCO", "SAIL", "NMDC",
        "VEDL", "COALINDIA", "MOIL", "NATIONALUM", "RATNAMANI",
        "WELCORP", "HINDCOPPER",
    ],
    "🏠 Realty": [
        "DLF", "GODREJPROP", "OBEROI", "PRESTIGE", "BRIGADE",
        "LODHA", "SOBHA", "PHOENIXLTD", "MAHLIFE", "SUNTECK",
    ],
    "⚡ Energy & Power": [
        "RELIANCE", "ONGC", "BPCL", "IOC", "GAIL",
        "NTPC", "POWERGRID", "ADANIGREEN", "ADANITRANS", "TORNTPOWER",
        "TATAPOWER", "CESC", "NHPC", "SJVN", "PFC", "RECLTD",
    ],
    "🏭 Capital Goods & Infra": [
        "LT", "BHEL", "SIEMENS", "ABB", "HAVELLS",
        "POLYCAB", "CONCOR", "NBCC", "IRCTC", "BEL",
        "HAL", "BEML", "RVNL",
    ],
    "🧴 FMCG & Consumer": [
        "HINDUNILVR", "ITC", "NESTLEIND", "BRITANNIA", "DABUR",
        "GODREJCP", "MARICO", "COLPAL", "TATACONSUM", "EMAMILTD",
        "VARUNBEV", "JUBLFOOD",
    ],
    "🧱 Cement & Building Materials": [
        "ULTRACEMCO", "SHREECEM", "AMBUJACEM", "RAMCOCEM", "JKCEMENT",
        "HEIDELBERG", "CENTURYPLY", "GREENPLY", "ASTRAL",
        "SUPREMEIND", "FINOLEX", "PIDILITIND",
    ],
    "📡 Telecom & Media": [
        "BHARTIARTL", "INDUSTOWER", "TATACOMM", "ZEEL",
        "SUNTV", "PVRINOX",
    ],
    "🔬 Chemicals": [
        "PIDILITIND", "ATUL", "DEEPAKNTR", "GNFC", "GSFC",
        "COROMANDEL", "CHAMBLFERT", "UPL", "PIIND", "NAVINFLUOR",
        "AARTIIND",
    ],
    "🏨 Hotels & Retail": [
        "INDHOTEL", "TRENT", "DMART", "NYKAA",
        "PAGEIND", "RAYMOND", "ABFRL", "BATAINDIA",
    ],
    "📋 All F&O Stocks": [
        "RELIANCE", "TCS", "INFOSYS", "HDFCBANK", "ICICIBANK", "HINDUNILVR",
        "SBIN", "BHARTIARTL", "KOTAKBANK", "ITC", "LT", "AXISBANK",
        "BAJFINANCE", "MARUTI", "ASIANPAINT", "TITAN", "HCLTECH", "SUNPHARMA",
        "WIPRO", "ULTRACEMCO", "TECHM", "POWERGRID", "NTPC", "ONGC",
        "JSWSTEEL", "TATASTEEL", "HINDALCO", "COALINDIA", "GRASIM", "M&M",
        "ADANIENT", "ADANIPORTS", "BAJAJFINSV", "BPCL", "BRITANNIA",
        "CIPLA", "DIVISLAB", "DRREDDY", "EICHERMOT", "GAIL", "GODREJCP",
        "HAVELLS", "HEROMOTOCO", "INDUSINDBK", "NESTLEIND", "PIDILITIND",
        "SBILIFE", "SHREECEM", "SIEMENS", "TATACONSUM", "TATAMOTORS",
        "TATAPOWER", "TORNTPHARM", "UPL", "VEDL", "VOLTAS", "ZOMATO",
        "NYKAA", "PAYTM", "POLYCAB", "DMART", "IRCTC", "BANKBARODA",
        "CANBK", "PNB", "FEDERALBNK", "IDFCFIRSTB", "MUTHOOTFIN", "CHOLAFIN",
        "BAJAJ-AUTO", "APOLLOHOSP", "LICI", "HDFCLIFE", "ICICIPRULI",
        "ICICIGI", "SBICARD", "MANAPPURAM", "INDHOTEL", "JUBLFOOD", "PIIND",
        "PERSISTENT", "LTIM", "MPHASIS", "COFORGE", "LTTS", "OFSS",
        "KPITTECH", "TRENT", "ABFRL", "PAGEIND", "RAYMOND", "BATAINDIA",
        "METROPOLIS", "LALPATHLAB", "MAXHEALTH", "FORTIS", "CONCOR",
        "AUROPHARMA", "BIOCON", "LUPIN", "ALKEM", "IPCALAB", "NATCOPHARM",
        "GRANULES", "LAURUSLABS", "CANFINHOME", "RECLTD", "PFC", "IRFC",
        "HUDCO", "NBCC", "NHPC", "SJVN", "CESC", "TORNTPOWER", "ADANIGREEN",
        "ADANITRANS", "SAIL", "NMDC", "MOIL", "NATIONALUM", "RATNAMANI",
        "WELCORP", "RAMCOCEM", "JKCEMENT", "CENTURYPLY", "GREENPLY", "ASTRAL",
        "SUPREMEIND", "FINOLEX", "WHIRLPOOL", "CROMPTON", "ORIENTELEC",
        "VGUARD", "AMBER", "ATUL", "DEEPAKNTR", "GNFC", "GSFC",
        "COROMANDEL", "CHAMBLFERT", "MRF", "APOLLOTYRE", "BALKRISIND",
        "CEATLTD", "MOTHERSON", "BOSCHLTD", "EXIDEIND", "AMARAJABAT",
        "ESCORTS", "TIINDIA", "SCHAEFFLER", "DLF", "GODREJPROP",
        "PRESTIGE", "LODHA", "PHOENIXLTD", "TVSMOTOR", "ZYDUSLIFE",
        "BEL", "HAL", "ABB", "NAUKRI", "INDUSTOWER", "SHRIRAMFIN",
        "JIOFIN", "EMAMILTD", "COLPAL", "MARICO", "DABUR",
    ],
}

INTERVAL_MAP = {
    "1 min"   : Interval.in_1_minute,
    "3 min"   : Interval.in_3_minute,
    "5 min"   : Interval.in_5_minute,
    "15 min"  : Interval.in_15_minute,
    "30 min"  : Interval.in_30_minute,
    "1 hour"  : Interval.in_1_hour,
    "2 hour"  : Interval.in_2_hour,
    "4 hour"  : Interval.in_4_hour,
    "Daily"   : Interval.in_daily,
    "Weekly"  : Interval.in_weekly,
    "Monthly" : Interval.in_monthly,
}


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


def safe_get_hist(tv, symbol, exchange, interval, n_bars):
    """
    Robust wrapper around tv.get_hist() with retry + backoff.
    Returns (df, None) on success or (None, error_string) on failure.
    """
    last_error = None
    delay      = RETRY_DELAY

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            df = tv.get_hist(
                symbol=symbol, exchange=exchange,
                interval=interval, n_bars=n_bars,
            )
            if df is None or df.empty:
                return None, f"No data for {symbol}:{exchange}"
            df.columns = df.columns.str.lower()
            return df, None

        except Exception as e:
            err_lower  = str(e).lower()
            last_error = str(e)

            if any(s in err_lower for s in SKIP_ERRORS):
                return None, f"Bad symbol {symbol} — {e}"

            if attempt < MAX_RETRIES:
                time.sleep(delay)
                delay *= RETRY_BACKOFF
                continue

    return None, f"Failed after {MAX_RETRIES} retries ({symbol}) — {last_error}"


# ─────────────────────────────────────────────────────────────────────────────
# Signal Logic  — exact same as fno_swing_app.py
# ─────────────────────────────────────────────────────────────────────────────
def crossover(a: pd.Series, b) -> pd.Series:
    if not isinstance(b, pd.Series):
        b = pd.Series(b, index=a.index)
    return (a > b) & (a.shift(1) <= b.shift(1))


def crossunder(a: pd.Series, b) -> pd.Series:
    if not isinstance(b, pd.Series):
        b = pd.Series(b, index=a.index)
    return (a < b) & (a.shift(1) >= b.shift(1))


def compute_signals(df, ema_len, sma_len, rsi_len, ob, os_):
    df = df.copy()
    df["ema"]      = ta.ema(df["close"], length=ema_len)
    df["sma"]      = ta.sma(df["close"], length=sma_len)
    df["rsi"]      = ta.rsi(df["close"], length=rsi_len)
    df["buycall"]  = crossunder(df["sma"], df["ema"]) & (df["high"]  > df["sma"])
    df["sellcall"] = crossover (df["sma"], df["ema"]) & (df["open"]  > df["close"])
    df["rsi_bull"] = crossover (df["rsi"], os_)
    df["rsi_bear"] = crossunder(df["rsi"], ob)
    return df


# ─────────────────────────────────────────────────────────────────────────────
# Banner
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="swing-banner">
    <div>
        <div class="swing-title">📈 SWING SIGNAL SCANNER</div>
        <div class="swing-sub">
            EMA / SMA Crossover · RSI Extremes · Nifty 50 · Nifty Next 50 · F&O · 10+ Sectors
        </div>
    </div>
    <div style="text-align:right;">
        <div style="font-size:0.82rem; font-weight:700; color:#1e3028;">
            Powered by TvDatafeed · Pine Script "SWING CALLS"
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:0.8rem 0 0.3rem;">
        <div style="font-size:1.4rem; font-weight:900; color:#00e87a; letter-spacing:0.06em;">
            📈 SWING SCANNER
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Page navigation
    st.markdown("""
    <div style="font-size:0.72rem; font-weight:900; color:#2e4060;
                text-transform:uppercase; letter-spacing:0.14em;
                margin: 0.6rem 0 0.4rem; padding-left:4px;">
        NAVIGATE
    </div>
    """, unsafe_allow_html=True)
    st.page_link("Home.py",                    label="🏠  Home")
    st.page_link("pages/1_Fractal_Scanner.py", label="🔍  Fractal Scanner")
    st.page_link("pages/2_Swing_Scanner.py",   label="📈  Swing Scanner")
    st.markdown('<div style="border-top:1px solid #141e30; margin:0.8rem 0;"></div>',
                unsafe_allow_html=True)

    st.markdown('<div class="sb-section">TRADINGVIEW LOGIN</div>', unsafe_allow_html=True)
    tv_user = st.text_input("Username", placeholder="optional — leave blank for Guest",
                             key="swing_tv_user")
    tv_pass = st.text_input("Password", type="password", placeholder="optional",
                             key="swing_tv_pass")

    st.markdown('<div class="sb-section">SCAN PARAMETERS</div>', unsafe_allow_html=True)
    interval_label = st.selectbox("Timeframe", list(INTERVAL_MAP.keys()), index=8,
                                   key="swing_tf")
    bars_back = st.slider("Candles to fetch", 100, 500, 200, 50, key="swing_bars")

    st.markdown('<div class="sb-section">INDICATOR SETTINGS</div>', unsafe_allow_html=True)
    ema_len = st.number_input("EMA Length", min_value=1,  max_value=200, value=3,  key="swing_ema")
    sma_len = st.number_input("SMA Length", min_value=2,  max_value=500, value=17, key="swing_sma")
    rsi_len = st.number_input("RSI Length", min_value=2,  max_value=100, value=14, key="swing_rsi")
    ob_lim  = st.slider("RSI Overbought", 50, 100, 80, key="swing_ob")
    os_lim  = st.slider("RSI Oversold",    0,  50, 20, key="swing_os")

    st.markdown('<div class="sb-section">SIGNAL FILTERS</div>', unsafe_allow_html=True)
    show_buy  = st.checkbox("BUY  (B)",       value=True, key="swing_f_buy")
    show_sell = st.checkbox("SELL (S)",        value=True, key="swing_f_sell")
    show_bull = st.checkbox("RSI Bullish ↑",  value=True, key="swing_f_bull")
    show_bear = st.checkbox("RSI Bearish ↓",  value=True, key="swing_f_bear")

    st.markdown('<div class="sb-section">RUN</div>', unsafe_allow_html=True)
    scan_btn = st.button("🚀  RUN SCANNER", key="swing_scan_btn")

    # Signal legend in sidebar
    st.markdown("""
    <div style="margin-top:1.5rem; background:#0a0f1a; border:1px solid #141e30;
                border-radius:8px; padding:1rem; font-size:0.82rem;
                font-weight:700; color:#2a3e58; line-height:2.2;">
        <div style="font-size:0.75rem; font-weight:900; color:#1e3050;
                    text-transform:uppercase; letter-spacing:0.1em; margin-bottom:6px;">
            SIGNAL RULES
        </div>
        <span style="color:#00e87a;">BUY</span> — SMA crosses under EMA & High > SMA<br>
        <span style="color:#ff4466;">SELL</span> — SMA crosses over EMA & Open > Close<br>
        <span style="color:#69f0ae;">RSI ↑</span> — RSI crosses above Oversold<br>
        <span style="color:#ff6d00;">RSI ↓</span> — RSI crosses below Overbought
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Universe Selector
# ─────────────────────────────────────────────────────────────────────────────
universe_names = list(UNIVERSE.keys())
index_groups   = [k for k in universe_names if any(x in k for x in ["Nifty", "F&O"])]
sector_groups  = [k for k in universe_names if k not in index_groups]

st.markdown('<div class="universe-header">🗂️ Select Universe / Sector</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="universe-sub">Tick one or more groups — stocks are merged and deduplicated automatically.</div>',
    unsafe_allow_html=True,
)

col_idx, col_sec = st.columns([1, 2])
selected_groups  = []

with col_idx:
    st.markdown(
        '<div style="font-size:0.88rem; font-weight:900; color:#4a6080; margin-bottom:0.5rem;">'
        'INDICES & BROAD</div>',
        unsafe_allow_html=True,
    )
    for grp in index_groups:
        n = len(UNIVERSE[grp])
        if st.checkbox(f"{grp}  ({n})", key=f"swing_chk_{grp}"):
            selected_groups.append(grp)

with col_sec:
    st.markdown(
        '<div style="font-size:0.88rem; font-weight:900; color:#4a6080; margin-bottom:0.5rem;">'
        'SECTORS</div>',
        unsafe_allow_html=True,
    )
    sec_col1, sec_col2 = st.columns(2)
    for i, grp in enumerate(sector_groups):
        n = len(UNIVERSE[grp])
        target_col = sec_col1 if i % 2 == 0 else sec_col2
        if target_col.checkbox(f"{grp}  ({n})", key=f"swing_chk_{grp}"):
            selected_groups.append(grp)

st.markdown("<hr>", unsafe_allow_html=True)

# ── Guard: need at least one group
if not selected_groups:
    # Show landing page
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div style="background:#0f1520; border:1px solid #1a2540; border-radius:10px; padding:1.2rem 1.5rem;">
        <div style="font-size:0.8rem; font-weight:900; color:#1e3050; text-transform:uppercase;
                    letter-spacing:0.12em; margin-bottom:0.7rem;">SIGNALS DETECTED</div>
        <table class="sig-table">
        <tr><th>Signal</th><th>Condition</th></tr>
        <tr><td><span class="badge badge-buy">BUY</span></td><td style="color:#4a6080;">SMA crosses under EMA & High > SMA</td></tr>
        <tr><td><span class="badge badge-sell">SELL</span></td><td style="color:#4a6080;">SMA crosses over EMA & Open > Close</td></tr>
        <tr><td><span class="badge badge-bull">RSI↑</span></td><td style="color:#4a6080;">RSI crosses above Oversold level</td></tr>
        <tr><td><span class="badge badge-bear">RSI↓</span></td><td style="color:#4a6080;">RSI crosses below Overbought level</td></tr>
        </table>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background:#0f1520; border:1px solid #1a2540; border-radius:10px; padding:1.2rem 1.5rem;">
        <div style="font-size:0.8rem; font-weight:900; color:#1e3050; text-transform:uppercase;
                    letter-spacing:0.12em; margin-bottom:0.7rem;">AVAILABLE UNIVERSES</div>
        """, unsafe_allow_html=True)
        for name, stocks in UNIVERSE.items():
            st.markdown(
                f'<div style="font-size:0.88rem; font-weight:700; color:#3a5070; '
                f'padding:4px 0; border-bottom:1px solid #141e30;">'
                f'<span style="color:#00c8ff;">{name}</span> — {len(stocks)} stocks</div>',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center; padding:2rem; border:2px dashed #1a2540;
                border-radius:12px; color:#2e4060; font-size:1rem; font-weight:700; margin-top:1rem;">
        ☝️ Tick one or more universes/sectors above, configure settings in the sidebar,
        then click <span style="color:#00e87a;">🚀 RUN SCANNER</span>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Merge and show selection
merged     = []
for grp in selected_groups:
    merged.extend(UNIVERSE[grp])
stock_list = list(dict.fromkeys(merged))   # deduplicate, preserve order

label_str  = ", ".join(selected_groups)
st.markdown(f"""
<div style="background:#0a1a12; border:1px solid rgba(0,232,122,0.25); border-radius:8px;
            padding:0.9rem 1.2rem; margin-bottom:1rem; font-size:0.95rem; font-weight:700;">
    <span style="color:#00e87a;">{len(selected_groups)} group(s)</span> selected
    &nbsp;→&nbsp;
    <span style="color:#00c8ff;">{len(stock_list)} unique stocks</span> will be scanned
    <br>
    <span style="color:#1e4030; font-size:0.82rem;">{label_str}</span>
</div>
""", unsafe_allow_html=True)

with st.expander("👁️ Preview all stocks in selection"):
    chips = "".join([f'<span class="sym-chip">{s}</span>' for s in stock_list])
    st.markdown(f'<div class="universe-grid">{chips}</div>', unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Helper functions
# ─────────────────────────────────────────────────────────────────────────────
def badge_html(row):
    b = ""
    if row["BUY"]:      b += '<span class="badge badge-buy">BUY</span>'
    if row["SELL"]:     b += '<span class="badge badge-sell">SELL</span>'
    if row["RSI_BULL"]: b += '<span class="badge badge-bull">RSI↑</span>'
    if row["RSI_BEAR"]: b += '<span class="badge badge-bear">RSI↓</span>'
    return b


def show_table(df_show):
    if df_show.empty:
        st.markdown(
            '<div style="font-size:0.92rem; font-weight:700; color:#2e4060; padding:1rem;">'
            'No signals in this category.</div>',
            unsafe_allow_html=True,
        )
        return
    disp = df_show[["Symbol", "Date", "Close", "EMA", "SMA", "RSI"]].copy()
    disp["Signals"] = df_show.apply(badge_html, axis=1)
    st.write(disp.to_html(escape=False, index=False), unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Scan
# ─────────────────────────────────────────────────────────────────────────────
if scan_btn:
    interval = INTERVAL_MAP[interval_label]
    tv       = TvDatafeed(username=tv_user or None, password=tv_pass or None)

    total    = len(stock_list)
    results  = []
    log_msgs = []

    st.markdown(
        f'<div style="font-size:1rem; font-weight:800; color:#e8ecf5; margin-bottom:0.8rem;">'
        f'🔄 Scanning <span style="color:#00e87a;">{len(selected_groups)} group(s)</span>'
        f' — <span style="color:#00c8ff;">{total} stocks</span>'
        f' on <span style="color:#ffd600;">{interval_label}</span></div>',
        unsafe_allow_html=True,
    )

    prog_bar   = st.progress(0)
    status_txt = st.empty()
    log_box    = st.empty()

    for idx, symbol in enumerate(stock_list, 1):
        prog_bar.progress(idx / total)
        status_txt.markdown(
            f'<div style="font-size:0.92rem; font-weight:700; color:#3a5070;">'
            f'[{idx}/{total}] Fetching <span style="color:#00c8ff;">{symbol}</span> …</div>',
            unsafe_allow_html=True,
        )

        raw, err = safe_get_hist(tv, symbol, "NSE", interval, bars_back)

        if err:
            log_msgs.append(
                f'<span class="log-err">✗ {symbol:<18} {err}</span>'
            )
        elif len(raw) < sma_len + 5:
            log_msgs.append(
                f'<span class="log-err">✗ {symbol:<18} insufficient data ({len(raw)} bars)</span>'
            )
        else:
            df   = compute_signals(raw, ema_len, sma_len, rsi_len, ob_lim, os_lim)
            last = df.iloc[-1]

            sigs = []
            if last["buycall"]:  sigs.append("BUY")
            if last["sellcall"]: sigs.append("SELL")
            if last["rsi_bull"]: sigs.append("RSI_BULL")
            if last["rsi_bear"]: sigs.append("RSI_BEAR")

            if sigs:
                log_msgs.append(
                    f'<span class="log-sig">✔ {symbol:<18} → {", ".join(sigs)}</span>'
                )
                results.append({
                    "Symbol"  : symbol,
                    "Date"    : str(last.name)[:10],
                    "Close"   : round(last["close"], 2),
                    "EMA"     : round(last["ema"],   2),
                    "SMA"     : round(last["sma"],   2),
                    "RSI"     : round(last["rsi"],   2),
                    "BUY"     : bool(last["buycall"]),
                    "SELL"    : bool(last["sellcall"]),
                    "RSI_BULL": bool(last["rsi_bull"]),
                    "RSI_BEAR": bool(last["rsi_bear"]),
                })
            else:
                log_msgs.append(
                    f'<span class="log-ok">· {symbol:<18} no signal</span>'
                )

        log_box.markdown(
            '<div class="log-box">' + "<br>".join(log_msgs[-25:]) + "</div>",
            unsafe_allow_html=True,
        )
        time.sleep(0.25)

    prog_bar.progress(1.0)
    status_txt.markdown(
        f'<div style="font-size:1rem; font-weight:800; color:#00e87a;">'
        f'✅ Done — {len(results)} signal(s) found across {total} stocks</div>',
        unsafe_allow_html=True,
    )

    if not results:
        st.markdown(
            '<div style="font-size:0.95rem; font-weight:700; color:#2e4060; padding:1rem;">'
            'No signals found. Try a different timeframe or universe.</div>',
            unsafe_allow_html=True,
        )
        st.stop()

    df_all = pd.DataFrame(results)

    # Apply signal filters
    mask = pd.Series([False] * len(df_all))
    if show_buy:  mask |= df_all["BUY"]
    if show_sell: mask |= df_all["SELL"]
    if show_bull: mask |= df_all["RSI_BULL"]
    if show_bear: mask |= df_all["RSI_BEAR"]
    df_filtered = df_all[mask].reset_index(drop=True)

    # ── Summary cards
    n_buy  = int(df_all["BUY"].sum())
    n_sell = int(df_all["SELL"].sum())
    n_bull = int(df_all["RSI_BULL"].sum())
    n_bear = int(df_all["RSI_BEAR"].sum())

    st.markdown(
        '<div style="font-size:1.1rem; font-weight:900; color:#e8ecf5; margin: 1.2rem 0 0.8rem;">📊 Signal Summary</div>',
        unsafe_allow_html=True,
    )
    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card buy">
            <div class="val">{n_buy}</div><div class="lbl">BUY (B)</div>
        </div>
        <div class="metric-card sell">
            <div class="val">{n_sell}</div><div class="lbl">SELL (S)</div>
        </div>
        <div class="metric-card bull">
            <div class="val">{n_bull}</div><div class="lbl">RSI Bullish ↑</div>
        </div>
        <div class="metric-card bear">
            <div class="val">{n_bear}</div><div class="lbl">RSI Bearish ↓</div>
        </div>
        <div class="metric-card">
            <div class="val">{len(df_filtered)}</div><div class="lbl">Filtered Total</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tabbed results
    st.markdown(
        '<div style="font-size:1.1rem; font-weight:900; color:#e8ecf5; margin-bottom:0.8rem;">📋 Signal Details</div>',
        unsafe_allow_html=True,
    )
    tab_all, tab_buy, tab_sell, tab_bull, tab_bear = st.tabs([
        "All", "🟢 BUY", "🔴 SELL", "🟩 RSI Bull ↑", "🟠 RSI Bear ↓"
    ])
    with tab_all:  show_table(df_filtered)
    with tab_buy:  show_table(df_all[df_all["BUY"]].reset_index(drop=True))
    with tab_sell: show_table(df_all[df_all["SELL"]].reset_index(drop=True))
    with tab_bull: show_table(df_all[df_all["RSI_BULL"]].reset_index(drop=True))
    with tab_bear: show_table(df_all[df_all["RSI_BEAR"]].reset_index(drop=True))

    st.markdown("<hr>", unsafe_allow_html=True)
    st.download_button(
        label             = "⬇️  Download Results as CSV",
        data              = df_filtered.to_csv(index=False).encode(),
        file_name         = (
            f"swing_signals_"
            f"{'_'.join([g.split()[-1] for g in selected_groups])}_"
            f"{pd.Timestamp.now():%Y%m%d_%H%M}.csv"
        ),
        mime  = "text/csv",
        width = "stretch",
    )
