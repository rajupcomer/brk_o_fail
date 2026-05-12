"""
NIFTY Option Strike Monitor — tvDatafeed Edition
=================================================
• Fetches data 100% from TradingView via tvDatafeed (no API key needed)
• User selects multiple CE and PE strikes manually
• Scans 15-min candles for 20 EMA cross & close below signal
• Works on any machine with internet access to TradingView

Install & Run:
    pip install -r requirements.txt
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import List
from datetime import datetime, timedelta
import time

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NIFTY Strike Monitor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Outfit:wght@300;400;600;700&display=swap');

html,body,[class*="css"]{ background:#07090f; color:#e2e8f0; font-family:'Outfit',sans-serif; }
.main{ background:#07090f; }
.block-container{ padding-top:1.2rem; }

/* Header */
.hdr{
  background:linear-gradient(135deg,#0b1929 0%,#0f2040 50%,#0b1929 100%);
  border:1px solid #1a3a5c; border-radius:14px;
  padding:1.1rem 1.8rem; margin-bottom:1.2rem;
  display:flex; align-items:center; justify-content:space-between;
}
.hdr-left h1{ font-family:'JetBrains Mono',monospace; font-size:1.5rem;
              font-weight:700; color:#38bdf8; margin:0; letter-spacing:-0.5px; }
.hdr-left p { font-size:.7rem; color:#475569; letter-spacing:2px;
              text-transform:uppercase; margin:2px 0 0; }
.hdr-right  { text-align:right; }
.hdr-ts     { font-family:'JetBrains Mono',monospace; font-size:.75rem; color:#38bdf8; }
.hdr-sub    { font-size:.65rem; color:#334155; margin-top:3px; }

/* Metric cards */
.mc{background:#0d1420;border:1px solid #1e2d42;border-radius:10px;
    padding:.85rem .95rem;text-align:center;}
.mc-l{font-size:.65rem;color:#475569;text-transform:uppercase;letter-spacing:1.5px;}
.mc-v{font-family:'JetBrains Mono',monospace;font-size:1.4rem;
      font-weight:700;color:#38bdf8;line-height:1.2;}
.mc-s{font-size:.62rem;color:#334155;margin-top:2px;}

/* Strike selector area */
.selector-box{
  background:#0d1420; border:1px solid #1e2d42; border-radius:12px;
  padding:1rem 1.2rem; margin-bottom:.8rem;
}
.sel-title{font-family:'JetBrains Mono',monospace;font-size:.75rem;
           font-weight:700;letter-spacing:2px;text-transform:uppercase;
           margin-bottom:.6rem;}
.sel-ce{color:#4ade80;border-left:3px solid #22c55e;padding-left:.6rem;}
.sel-pe{color:#f87171;border-left:3px solid #ef4444;padding-left:.6rem;}

/* Results table rows */
.rt-wrap{border-radius:10px;overflow:hidden;margin-bottom:.5rem;}

/* Signal badges */
.s-cross{display:inline-block;background:#2a0f5e;color:#c4b5fd;
          border:1px solid #7c3aed88;border-radius:20px;
          padding:3px 12px;font-size:.72rem;font-family:'JetBrains Mono',monospace;
          font-weight:700;letter-spacing:.5px;}
.s-below{display:inline-block;background:#1f0909;color:#f87171;
          border:1px solid #ef444466;border-radius:20px;
          padding:3px 12px;font-size:.72rem;font-family:'JetBrains Mono',monospace;}
.s-above{display:inline-block;background:#071a0d;color:#4ade80;
          border:1px solid #22c55e66;border-radius:20px;
          padding:3px 12px;font-size:.72rem;font-family:'JetBrains Mono',monospace;}
.s-wait {display:inline-block;background:#111318;color:#475569;
          border:1px solid #2a2a2a;border-radius:20px;
          padding:3px 12px;font-size:.72rem;font-family:'JetBrains Mono',monospace;}

/* Alert rows */
.alrt{border-radius:8px;padding:.6rem 1rem;
      font-family:'JetBrains Mono',monospace;font-size:.78rem;margin:.25rem 0;}
.alrt-cross{background:#1a0a30;border:1px solid #7c3aed55;
             border-left:3px solid #a78bfa;color:#ddd6fe;}
.alrt-ce   {background:#071a0d;border:1px solid #22c55e44;
             border-left:3px solid #22c55e;color:#86efac;}
.alrt-pe   {background:#1a0707;border:1px solid #ef444444;
             border-left:3px solid #ef4444;color:#fca5a5;}

/* Section headers */
.sec-h{border-radius:6px;padding:.45rem .9rem;
        font-family:'JetBrains Mono',monospace;font-size:.75rem;
        font-weight:700;letter-spacing:2px;text-transform:uppercase;margin:.6rem 0 .4rem;}
.sec-ce{background:#071a0d;color:#4ade80;border-left:3px solid #22c55e;}
.sec-pe{background:#1a0707;color:#f87171;border-left:3px solid #ef4444;}

/* Info box */
.info-box{background:#0d1420;border:1px solid #1e3a5c;border-radius:8px;
           padding:.7rem 1rem;font-size:.8rem;color:#64748b;margin:.4rem 0;}

/* Sidebar */
section[data-testid="stSidebar"]{background:#0a0d14 !important;border-right:1px solid #1e293b;}
section[data-testid="stSidebar"] * {color:#94a3b8 !important;}
section[data-testid="stSidebar"] h2{color:#38bdf8 !important;
   font-family:'JetBrains Mono',monospace !important;}

/* Buttons */
.stButton>button{background:linear-gradient(135deg,#0ea5e9,#38bdf8);
                  color:#07090f;font-weight:700;border:none;border-radius:8px;
                  font-family:'JetBrains Mono',monospace;letter-spacing:1px;}
.stButton>button:hover{opacity:.85;}

/* Divider */
.div{border:none;border-top:1px solid #1e2d42;margin:.8rem 0;}

/* Dot */
.dot-live{display:inline-block;width:8px;height:8px;border-radius:50%;
           background:#22c55e;animation:blink 1.5s infinite;margin-right:5px;}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.3}}
</style>
""", unsafe_allow_html=True)


# ── tvDatafeed import ──────────────────────────────────────────────────────────
try:
    from tvDatafeed import TvDatafeed, Interval
    TV_AVAILABLE = True
except ImportError:
    TV_AVAILABLE = False


# ── TradingView symbol builder for NSE options ─────────────────────────────────
def build_tv_symbol(expiry_date: datetime, strike: int, opt_type: str) -> str:
    """
    Build TradingView symbol for NSE option.

    TradingView NSE option symbol format:
      NIFTY{YY}{MON}{DD}{TYPE}{STRIKE}
      e.g. NIFTY25MAY2924000CE  (expiry 29-May-2025, CE 24000)

    For monthly expiry (last Thursday):
      NIFTY{YY}{MON}{STRIKE}{TYPE}
      e.g. NIFTY25MAY24000CE

    We generate both formats and let the caller try them.
    """
    yy  = expiry_date.strftime("%y")          # 25
    #mon = expiry_date.strftime("%b").upper()  # MAY
    mon = expiry_date.strftime("%m")  # MAY
    dd  = expiry_date.strftime("%d")          # 29

    # Weekly format (most common for near-term)
    weekly  = f"NIFTY{yy}{mon}{dd}{opt_type}{int(strike)}"
    # Monthly format (last Thursday of month)
    monthly = f"NIFTY{yy}{mon}{int(strike)}{opt_type}"
    
    print (weekly)
    print (monthly)

    return weekly, monthly


def get_upcoming_expiries(n: int = 8) -> List[datetime]:
    """
    Generate next N weekly expiry dates (every Thursday).
    NSE NIFTY weekly expiry = every Thursday.
    """
    expiries = []
    today = datetime.today()
    d = today
    while len(expiries) < n:
        # Thursday = weekday 3
        days_ahead = (1 - d.weekday()) % 7
        if days_ahead == 0 and d.date() == today.date():
            days_ahead = 7  # if today is Thursday, next Thursday
        d = d + timedelta(days=days_ahead if len(expiries) == 0 else 7)
        if len(expiries) == 0:
            d = today + timedelta(days=days_ahead)
        expiries.append(d)
        d = d + timedelta(days=1)
    return expiries


def get_nifty_spot_from_tv(tv) -> float:
    """Fetch current NIFTY spot from TradingView."""
    try:
        df = tv.get_hist("NIFTY", "NSE", interval=Interval.in_1_minute, n_bars=5)
        if df is not None and not df.empty:
            return float(df["close"].iloc[-1])
    except Exception:
        pass
    return 0.0


# ── Fetch candles ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=60, show_spinner=False)
def fetch_candles(symbol: str, exchange: str = "NSE", n_bars: int = 100) -> pd.DataFrame:
    """Fetch 15-min candles via tvDatafeed."""
    if not TV_AVAILABLE:
        return pd.DataFrame()
    try:
        tv = TvDatafeed()
        df = tv.get_hist(symbol, exchange, interval=Interval.in_15_minute, n_bars=n_bars)
        if df is None or df.empty:
            return pd.DataFrame()
        df = df[["open","high","low","close","volume"]].copy()
        df.columns = ["Open","High","Low","Close","Volume"]
        return df
    except Exception as e:
        return pd.DataFrame()


# ── 20 EMA + Signal ────────────────────────────────────────────────────────────
def compute_ema_signal(df: pd.DataFrame, period: int = 20) -> dict:
    """
    Compute 20 EMA on 15-min candles and detect cross/close below.

    CROSS_BELOW  : previous candle closed ABOVE EMA, current candle CLOSED BELOW EMA
    CLOSE_BELOW  : candle closed below EMA (not a fresh cross — was already below)
    ABOVE        : candle closed above EMA
    INSUFFICIENT : not enough bars
    """
    empty = {
        "signal": "INSUFFICIENT", "last_close": 0.0, "ema": 0.0,
        "prev_close": 0.0, "prev_ema": 0.0, "last_time": "--",
        "bars_used": 0, "error": ""
    }
    if df.empty or len(df) < 5:
        empty["error"] = f"Only {len(df)} bars"
        return empty

    df = df.copy()
    df["EMA"] = df["Close"].ewm(span=period, adjust=False).mean()

    last = df.iloc[-1]
    prev = df.iloc[-2]
    lc, le = float(last["Close"]), float(last["EMA"])
    pc, pe = float(prev["Close"]), float(prev["EMA"])

    # Fresh cross: prev closed ABOVE EMA, current closed BELOW EMA
    if pc > pe and lc < le:
        signal = "CROSS_BELOW"
    elif lc < le:
        signal = "CLOSE_BELOW"
    else:
        signal = "ABOVE"

    try:
        t = df.index[-1].strftime("%d-%b %H:%M")
    except Exception:
        t = "--"

    return {
        "signal":     signal,
        "last_close": round(lc, 2),
        "ema":        round(le, 2),
        "prev_close": round(pc, 2),
        "prev_ema":   round(pe, 2),
        "last_time":  t,
        "bars_used":  len(df),
        "error":      "",
    }


# ── Demo data ──────────────────────────────────────────────────────────────────
def demo_candles(seed: int = 42, n: int = 80, base: float = 120.0) -> pd.DataFrame:
    """Generate realistic fake 15-min option candles for preview."""
    rng = np.random.default_rng(seed)
    closes = [base]
    for _ in range(n - 1):
        closes.append(max(1.0, closes[-1] + rng.normal(0, base * 0.015)))
    closes = np.array(closes)
    opens  = np.roll(closes, 1); opens[0] = closes[0]
    highs  = np.maximum(opens, closes) * (1 + rng.uniform(0, 0.008, n))
    lows   = np.minimum(opens, closes) * (1 - rng.uniform(0, 0.008, n))
    idx = pd.date_range("2025-05-29 09:15", periods=n, freq="15min")
    return pd.DataFrame({"Open":opens,"High":highs,"Low":lows,
                          "Close":closes,"Volume":rng.integers(500,5000,n)}, index=idx)


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ SETTINGS")
    st.markdown("---")

    ema_period  = st.slider("EMA Period", 5, 50, 20, 1)
    n_bars      = st.slider("Candle History (bars)", 50, 500, 100, 25)
    st.markdown("---")

    auto_ref = st.checkbox("Auto-refresh (3 min)", False)
    st.markdown("---")

    st.markdown("**LOGIN (optional)**")
    st.caption("Anonymous login works for most data.\nAdd credentials for extended history.")
    tv_user = st.text_input("TradingView Username", placeholder="optional")
    tv_pass = st.text_input("TradingView Password", type="password", placeholder="optional")
    st.markdown("---")

    st.markdown("**SIGNAL GUIDE**")
    st.markdown('<span class="s-cross">⚡ CROSS↓EMA</span>', unsafe_allow_html=True)
    st.caption("Prev candle > EMA, current candle close < EMA — **fresh signal**")
    st.markdown('<span class="s-below">▼ CLOSE BELOW</span>', unsafe_allow_html=True)
    st.caption("Closed below EMA (was already below, no fresh cross)")
    st.markdown('<span class="s-above">▲ ABOVE EMA</span>', unsafe_allow_html=True)
    st.caption("Closed above EMA — no bearish signal")
    st.markdown("---")
    st.caption("Data: TradingView via tvDatafeed")
    st.caption("Exchange: NSE")

if auto_ref:
    time.sleep(180)
    st.rerun()


# ── Header ─────────────────────────────────────────────────────────────────────
now_str = datetime.now().strftime("%d %b %Y  |  %H:%M:%S IST")
st.markdown(f"""
<div class="hdr">
  <div class="hdr-left">
    <p>TradingView · NSE Options · 15-Min</p>
    <h1>📊 NIFTY Strike Monitor</h1>
  </div>
  <div class="hdr-right">
    <div class="hdr-ts">{now_str}</div>
    <div class="hdr-sub">15-Min Candle  ×  {ema_period}-Period EMA Cross</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ── TV connection ──────────────────────────────────────────────────────────────
if not TV_AVAILABLE:
    st.error("tvDatafeed not installed. Run: `pip install git+https://github.com/rongardF/tvdatafeed.git`")
    st.stop()

@st.cache_resource(show_spinner=False)
def get_tv_client(username="", password=""):
    if username and password:
        return TvDatafeed(username, password)
    return TvDatafeed()  # anonymous

tv_client = get_tv_client(tv_user, tv_pass)


# ── Step 1: Choose Expiry ──────────────────────────────────────────────────────
st.markdown("### Step 1 — Choose Expiry")

# Generate upcoming Thursdays
expiry_options = []
today = datetime.today()
d = today
found = 0
while found < 10:
    # next Thursday
    days_to_thu = (1 - d.weekday()) % 7
    if days_to_thu == 0:
        days_to_thu = 7
    d = d + timedelta(days=days_to_thu)
    expiry_options.append(d)
    found += 1
    d = d + timedelta(days=1)

expiry_labels = [e.strftime("%d-%b-%Y (%a)") for e in expiry_options]

col_exp, col_idx = st.columns([2, 2])
with col_exp:
    sel_exp_label = st.selectbox("Expiry Date", expiry_labels, index=0)
    sel_expiry = expiry_options[expiry_labels.index(sel_exp_label)]

with col_idx:
    index_name = st.selectbox("Index", ["NIFTY", "BANKNIFTY", "FINNIFTY"], index=0)
    step = 50 if index_name == "NIFTY" else 100

st.markdown('<hr class="div">', unsafe_allow_html=True)


# ── Step 2: Get Spot & Build Strike List ───────────────────────────────────────
st.markdown("### Step 2 — Enter Spot / ATM & Select Strikes")

spot_col, atm_col = st.columns([2, 2])
with spot_col:
    manual_spot = st.number_input(
        f"Current {index_name} Spot (enter manually or fetch)",
        min_value=1000.0, max_value=100000.0,
        value=24500.0, step=float(step),
        help="Enter the current index spot price to auto-generate strikes"
    )
with atm_col:
    fetch_spot = st.button("🔄 Fetch Live Spot from TradingView")
    if fetch_spot:
        with st.spinner("Fetching spot…"):
            live_spot = get_nifty_spot_from_tv(tv_client)
        if live_spot > 0:
            st.success(f"Live Spot: ₹{live_spot:,.2f} — update the field above")
        else:
            st.warning("Could not fetch spot — enter manually")

# Compute ATM
atm = round(manual_spot / step) * step

# Generate strike range: ATM ± 20 strikes
all_strikes = [atm + step * i for i in range(-20, 21)]

st.markdown(f"**ATM Strike:** `{atm:,}` &nbsp;|&nbsp; Strike step: `{step}`", unsafe_allow_html=True)
st.markdown('<hr class="div">', unsafe_allow_html=True)


# ── Step 3: Multi-select CE & PE Strikes ──────────────────────────────────────
st.markdown("### Step 3 — Select CE & PE Strikes to Monitor")

# Default OTM suggestions
default_ce = [atm + step * i for i in range(1, 6)]   # 5 CE OTM
default_pe = [atm - step * i for i in range(1, 6)]   # 5 PE OTM

c1, c2 = st.columns(2)
with c1:
    st.markdown('<div class="sec-h sec-ce">📗 CE — Call Strikes</div>', unsafe_allow_html=True)
    selected_ce = st.multiselect(
        "Select CE strikes",
        options=[int(s) for s in all_strikes],
        default=[int(s) for s in default_ce],
        key="ce_strikes",
        label_visibility="collapsed"
    )

with c2:
    st.markdown('<div class="sec-h sec-pe">📕 PE — Put Strikes</div>', unsafe_allow_html=True)
    selected_pe = st.multiselect(
        "Select PE strikes",
        options=[int(s) for s in all_strikes],
        default=[int(s) for s in default_pe],
        key="pe_strikes",
        label_visibility="collapsed"
    )

if not selected_ce and not selected_pe:
    st.warning("Please select at least one CE or PE strike above.")
    st.stop()

st.markdown('<hr class="div">', unsafe_allow_html=True)


# ── Step 4: Scan ───────────────────────────────────────────────────────────────
scan_col, _ = st.columns([1, 4])
with scan_col:
    run_scan = st.button("⚡  RUN SCAN", use_container_width=True)

if "scan_results" not in st.session_state:
    st.session_state.scan_results = {"ce": [], "pe": [], "ts": None}

if run_scan:
    ce_rows, pe_rows = [], []

    # Build weekly & monthly symbol variants
    weekly_sym, monthly_sym = build_tv_symbol(sel_expiry, 0, "")

    total = len(selected_ce) + len(selected_pe)
    prog = st.progress(0, f"Scanning {total} strikes…")

    def scan_strike(strike, opt_type, idx):
        weekly, monthly = build_tv_symbol(sel_expiry, strike, opt_type)
        # Try weekly format first, then monthly
        df = fetch_candles(weekly, "NSE", n_bars)
        sym_used = weekly
        if df.empty:
            df = fetch_candles(monthly, "NSE", n_bars)
            sym_used = monthly
        # If still empty, use demo data (offline/demo mode)
        demo_used = False
        if df.empty:
            df = demo_candles(seed=strike % 100, n=n_bars, base=max(5, 200 - idx * 15))
            demo_used = True
        sig = compute_ema_signal(df, ema_period)
        return {
            "Strike":    strike,
            "Type":      opt_type,
            "Symbol":    sym_used,
            "Demo":      demo_used,
            **sig,
        }

    done = 0
    for i, s in enumerate(sorted(selected_ce)):
        ce_rows.append(scan_strike(s, "C", i))
        done += 1
        prog.progress(done / total, f"C {s}…")

    for i, s in enumerate(sorted(selected_pe, reverse=True)):
        pe_rows.append(scan_strike(s, "P", i))
        done += 1
        prog.progress(done / total, f"P {s}…")

    prog.progress(1.0, "Done ✓")
    time.sleep(0.3)
    prog.empty()

    st.session_state.scan_results = {
        "ce": ce_rows, "pe": pe_rows,
        "ts": datetime.now().strftime("%H:%M:%S")
    }

results = st.session_state.scan_results
ce_results = results["ce"]
pe_results = results["pe"]
scan_ts    = results["ts"]

if not ce_results and not pe_results:
    st.markdown("""
    <div class="info-box">
      👆 Select CE / PE strikes above and click <b>⚡ RUN SCAN</b> to fetch 15-min candles
      and compute 20 EMA signals.
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ── Metric bar ─────────────────────────────────────────────────────────────────
all_results = ce_results + pe_results
cross_all   = [r for r in all_results if r["signal"] == "CROSS_BELOW"]
below_all   = [r for r in all_results if r["signal"] in ("CROSS_BELOW","CLOSE_BELOW")]
above_all   = [r for r in all_results if r["signal"] == "ABOVE"]
demo_any    = any(r.get("Demo") for r in all_results)

m_cols = st.columns(6)
for col, (lbl, val, sub) in zip(m_cols, [
    ("SPOT",          f"{manual_spot:,.0f}",     index_name),
    ("ATM",           f"{atm:,}",                "Strike"),
    ("EXPIRY",        sel_expiry.strftime("%d-%b-%Y"), ""),
    ("⚡ CROSSOVERS", str(len(cross_all)),        "Fresh cross↓EMA"),
    ("▼ BELOW EMA",   str(len(below_all)),        "Including crosses"),
    ("▲ ABOVE EMA",   str(len(above_all)),        "No signal"),
]):
    col.markdown(f"""
    <div class="mc">
      <div class="mc-l">{lbl}</div>
      <div class="mc-v">{val}</div>
      <div class="mc-s">{sub}</div>
    </div>""", unsafe_allow_html=True)

if scan_ts:
    st.caption(f"Last scan: {scan_ts}" + (" · ⚠️ Some strikes using demo data (TradingView unreachable)" if demo_any else " · <span class='dot-live'></span> Live data"))

st.markdown('<hr class="div">', unsafe_allow_html=True)


# ── Alert Panel ────────────────────────────────────────────────────────────────
if cross_all:
    st.markdown("### ⚡ Fresh EMA Crossover Alerts")
    ac1, ac2 = st.columns(2)
    ce_cross = [r for r in ce_results if r["signal"] == "CROSS_BELOW"]
    pe_cross = [r for r in pe_results if r["signal"] == "CROSS_BELOW"]
    with ac1:
        for r in ce_cross:
            st.markdown(
                f'<div class="alrt alrt-cross">'
                f'⚡ CE {r["Strike"]} — Close <b>{r["last_close"]}</b> crossed ↓ '
                f'EMA{ema_period} <b>{r["ema"]}</b> &nbsp;|&nbsp; {r["last_time"]}'
                f'</div>',
                unsafe_allow_html=True
            )
    with ac2:
        for r in pe_cross:
            st.markdown(
                f'<div class="alrt alrt-cross">'
                f'⚡ PE {r["Strike"]} — Close <b>{r["last_close"]}</b> crossed ↓ '
                f'EMA{ema_period} <b>{r["ema"]}</b> &nbsp;|&nbsp; {r["last_time"]}'
                f'</div>',
                unsafe_allow_html=True
            )
    st.markdown('<hr class="div">', unsafe_allow_html=True)


# ── Table renderer ─────────────────────────────────────────────────────────────
SIG_LABELS = {
    "CROSS_BELOW":  "⚡ CROSS↓EMA",
    "CLOSE_BELOW":  "▼ CLOSE BELOW",
    "ABOVE":        "▲ ABOVE EMA",
    "INSUFFICIENT": "— WAIT",
}

def render_results(rows: list, opt_type: str):
    if not rows:
        st.caption("No strikes selected.")
        return

    records = []
    for r in rows:
        records.append({
            "Strike":        r["Strike"],
            "Signal":        SIG_LABELS.get(r["signal"], r["signal"]),
            "Last Close":    r["last_close"],
            f"EMA{ema_period}": r["ema"],
            "Prev Close":    r["prev_close"],
            f"Prev EMA":     r["prev_ema"],
            "Time":          r["last_time"],
            "Bars":          r["bars_used"],
            "Symbol":        r["Symbol"],
            "Data":          "🟡 Demo" if r.get("Demo") else "🟢 Live",
        })

    df = pd.DataFrame(records)

    def style_sig(val):
        if "CROSS" in val:
            return "background-color:#1e0a3d;color:#c4b5fd;font-weight:700;font-family:JetBrains Mono,monospace"
        if "BELOW" in val:
            return "background-color:#1a0808;color:#f87171;font-family:JetBrains Mono,monospace"
        if "ABOVE" in val:
            return "background-color:#071a0e;color:#4ade80;font-family:JetBrains Mono,monospace"
        return "color:#475569;font-family:JetBrains Mono,monospace"

    def style_strike(val):
        return "font-family:JetBrains Mono,monospace;font-weight:700;color:#e2e8f0"

    def style_live(val):
        return "font-size:0.75rem"

    fmt = {
        "Last Close":        "{:.2f}",
        f"EMA{ema_period}":  "{:.2f}",
        "Prev Close":        "{:.2f}",
        "Prev EMA":          "{:.2f}",
        "Strike":            "{:,.0f}",
    }

    styled = (
        df.style
        .map(style_sig,     subset=["Signal"])
        .map(style_strike,  subset=["Strike"])
        .format(fmt)
        .set_properties(**{"font-size": "12px"})
    )
    st.dataframe(styled, use_container_width=True, height=min(80 + len(rows)*42, 450))


# ── CE Results ─────────────────────────────────────────────────────────────────
if ce_results:
    st.markdown('<div class="sec-h sec-ce">📗 CALL (CE) — Selected Strikes</div>', unsafe_allow_html=True)
    render_results(ce_results, "CE")
    st.markdown('<hr class="div">', unsafe_allow_html=True)

# ── PE Results ─────────────────────────────────────────────────────────────────
if pe_results:
    st.markdown('<div class="sec-h sec-pe">📕 PUT (PE) — Selected Strikes</div>', unsafe_allow_html=True)
    render_results(pe_results, "PE")
    st.markdown('<hr class="div">', unsafe_allow_html=True)


# ── Legend ─────────────────────────────────────────────────────────────────────
with st.expander("📖 How signals work · TradingView symbol format"):
    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown('<span class="s-cross">⚡ CROSS↓EMA</span>', unsafe_allow_html=True)
        st.caption("**Previous** 15-min candle closed **above** EMA20, **current** candle closed **below** EMA20. This is the primary signal.")
    with s2:
        st.markdown('<span class="s-below">▼ CLOSE BELOW</span>', unsafe_allow_html=True)
        st.caption("Current candle closed below EMA, but the crossover happened in an earlier candle — already in a downtrend.")
    with s3:
        st.markdown('<span class="s-above">▲ ABOVE EMA</span>', unsafe_allow_html=True)
        st.caption("Candle closed above EMA — no bearish signal active.")

    st.markdown(f"""
    **EMA Calculation**
    - Uses **Exponential Moving Average** (EMA) with span={ema_period}, `adjust=False` (standard TradingView formula)
    - Applied on 15-minute candle **close** prices
    - Requires minimum 5 candles; more bars = more accurate EMA

    **TradingView Symbol Format (NSE Options)**

    | Format | Example | When |
    |---|---|---|
    | Weekly | `NIFTY25MAY2924000CE` | Weekly expiry (most NIFTY contracts) |
    | Monthly | `NIFTY25MAY24000CE` | Monthly expiry (last Thursday of month) |

    The app tries the weekly format first, then monthly. If TradingView has no data
    for a strike (very deep OTM, no trades), demo data is shown in yellow.

    **Tips**
    - Add your TradingView login in the sidebar for extended history (up to 5000 bars)
    - Anonymous login is limited to ~100 bars per request
    - Use `n_bars = 200+` for more accurate EMA on weekly symbols
    """)


# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="text-align:center;color:#1e293b;font-size:.65rem;
     padding:1.5rem 0 .5rem;font-family:'JetBrains Mono',monospace;">
  NIFTY Strike Monitor · TradingView / tvDatafeed · NSE ·
  {datetime.now().strftime("%H:%M:%S IST")} · Not financial advice
</div>
""", unsafe_allow_html=True)
