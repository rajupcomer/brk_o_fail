"""
╔══════════════════════════════════════════════════════════════════╗
║              FRACTAL TRADING SUITE — HOME                       ║
║                                                                  ║
║  Multi-page Streamlit App                                        ║
║                                                                  ║
║  INSTALL:                                                        ║
║    pip install streamlit tvdatafeed pandas numpy plotly         ║
║    pip install pandas-ta-classic                                 ║
║                                                                  ║
║  RUN:                                                            ║
║    streamlit run Home.py                                         ║
║    (run from inside the scanner_app/ folder)                     ║
╚══════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import datetime

st.set_page_config(
    page_title            = "Fractal Trading Suite",
    page_icon             = "📊",
    layout                = "wide",
    initial_sidebar_state = "expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@600;700;800;900&display=swap');
html, body, [class*="css"], .stApp {
    font-family: 'Nunito', sans-serif !important;
    background-color: #0b0d12 !important;
    color: #e8ecf5 !important;
}
.block-container { padding: 2rem 3rem !important; max-width: 100% !important; }
footer { visibility: hidden; }

/* Keep sidebar nav visible — only hide hamburger menu & footer */
#MainMenu { visibility: hidden; }

/* Style the Streamlit page nav links in sidebar */
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a {
    font-family: 'Nunito', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 800 !important;
    color: #7a90b0 !important;
    padding: 0.5rem 0.8rem !important;
    border-radius: 6px !important;
    margin-bottom: 2px !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover {
    background: #141e30 !important;
    color: #00c8ff !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"] {
    background: #0f1520 !important;
    color: #00c8ff !important;
    border-left: 3px solid #00c8ff !important;
}

.home-banner {
    background: linear-gradient(120deg, #0e131f 0%, #121a2e 60%, #0e131f 100%);
    border: 1px solid #1f2d48;
    border-top: 3px solid #00c8ff;
    border-radius: 14px;
    padding: 2.5rem 3rem;
    margin-bottom: 2.5rem;
    text-align: center;
}
.home-title {
    font-size: 2.8rem; font-weight: 900; color: #00c8ff;
    letter-spacing: 0.04em; line-height: 1.1; margin-bottom: 0.5rem;
}
.home-sub {
    font-size: 1.1rem; font-weight: 700; color: #4a6080; margin-top: 6px;
}

.page-card {
    background: #0f1520;
    border: 1px solid #1a2540;
    border-radius: 14px;
    padding: 2rem 2rem 1.8rem;
    height: 100%;
    position: relative;
    transition: border-color 0.2s;
}
.page-card:hover { border-color: #2a3a60; }
.page-card .card-icon  { font-size: 2.5rem; margin-bottom: 0.8rem; }
.page-card .card-title {
    font-size: 1.3rem; font-weight: 900; color: #e8ecf5;
    margin-bottom: 0.5rem; letter-spacing: 0.02em;
}
.page-card .card-sub {
    font-size: 0.88rem; font-weight: 700; color: #3a5070;
    text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.8rem;
}
.page-card .card-desc {
    font-size: 0.95rem; font-weight: 700; color: #4a6080; line-height: 1.8;
    margin-bottom: 1.2rem;
}
.card-features { list-style: none; padding: 0; margin: 0; }
.card-features li {
    font-size: 0.88rem; font-weight: 700; color: #2e4060;
    padding: 4px 0; border-bottom: 1px solid #141e30;
}
.card-features li:last-child { border-bottom: none; }
.card-features li::before { content: "▸  "; color: #00c8ff; }

.card-accent-cyan   { border-top: 3px solid #00c8ff; }
.card-accent-green  { border-top: 3px solid #00e87a; }

.install-box {
    background: #0a0f1a;
    border: 1px solid #141e30;
    border-radius: 10px;
    padding: 1.5rem 2rem;
    margin-top: 2rem;
}
.install-title {
    font-size: 0.8rem; font-weight: 900; color: #2e4060;
    text-transform: uppercase; letter-spacing: 0.14em; margin-bottom: 0.8rem;
}
code {
    background: #141e30 !important;
    color: #00e87a !important;
    padding: 2px 8px !important;
    border-radius: 4px !important;
    font-size: 0.9rem !important;
    font-weight: 700 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar navigation
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:1rem 0 0.5rem;">
        <div style="font-size:1.5rem; font-weight:900; color:#00c8ff; letter-spacing:0.06em;">
            📊 TRADING SUITE
        </div>
        <div style="font-size:0.72rem; font-weight:800; color:#1e2e45;
                    letter-spacing:0.18em; text-transform:uppercase; margin-top:3px;">
            Select a Tool
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="margin: 1rem 0; border-top: 1px solid #141e30;"></div>
    <div style="font-size:0.72rem; font-weight:900; color:#2e4060;
                text-transform:uppercase; letter-spacing:0.14em;
                margin-bottom:0.7rem; padding-left:4px;">
        NAVIGATION
    </div>
    """, unsafe_allow_html=True)

    st.page_link("Home.py",                        label="🏠  Home",                    )
    st.page_link("pages/1_Fractal_Scanner.py",     label="🔍  Fractal Breakout Scanner", )
    st.page_link("pages/2_Swing_Scanner.py",        label="📈  Swing Signal Scanner",     )

    st.markdown("""
    <div style="margin: 1rem 0; border-top: 1px solid #141e30;"></div>
    <div style="background:#0a0f1a; border:1px solid #141e30; border-radius:8px;
                padding:0.9rem; font-size:0.8rem; font-weight:700;
                color:#2a3e58; line-height:2;">
        <div style="font-size:0.72rem; font-weight:900; color:#1e3050;
                    text-transform:uppercase; letter-spacing:0.1em; margin-bottom:6px;">
            QUICK START
        </div>
        1. Click a tool above<br>
        2. Enter TradingView login<br>
        3. Select symbols / universe<br>
        4. Click Run Scan
    </div>
    """, unsafe_allow_html=True)

# ── Banner
now_str = datetime.datetime.now().strftime("%d %b %Y   %H:%M:%S")
st.markdown(f"""
<div class="home-banner">
    <div class="home-title">📊 FRACTAL TRADING SUITE</div>
    <div class="home-sub">
        Multi-Timeframe Fractal Scanner &nbsp;·&nbsp; Swing Signal Scanner &nbsp;·&nbsp;
        Powered by TvDatafeed
    </div>
    <div style="font-size:0.85rem; font-weight:700; color:#1e2e45; margin-top:10px;">
        {now_str}  IST
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(
    '<div style="font-size:1rem; font-weight:800; color:#3a5070; margin-bottom:1.5rem;">'
    'Use the sidebar to navigate between tools. Each tool runs independently.</div>',
    unsafe_allow_html=True,
)

# ── Page Cards
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("""
    <div class="page-card card-accent-cyan">
        <div class="card-icon">🔍</div>
        <div class="card-title">Fractal Breakout Scanner</div>
        <div class="card-sub">Pages → Fractal Scanner</div>
        <div class="card-desc">
            Scan F&O stocks for unmitigated fractal level sweeps across
            three timeframe pairs. Get instant alerts with TradingView chart links.
        </div>
        <ul class="card-features">
            <li>30-Min fractals → 5-Min entry signal (12 core stocks)</li>
            <li>1-Week fractals → 1-Day signal (full F&O universe)</li>
            <li>1-Day fractals → 1-Hour signal (full F&O universe)</li>
            <li>Close Break & Wick Sweep detection</li>
            <li>Bullish & Bearish setup alerts</li>
            <li>Add custom stocks beyond predefined list</li>
            <li>Auto-refresh every 1–15 minutes</li>
            <li>Inline Plotly candlestick chart with fractal levels</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="page-card card-accent-green">
        <div class="card-icon">📈</div>
        <div class="card-title">Swing Signal Scanner</div>
        <div class="card-sub">Pages → Swing Scanner</div>
        <div class="card-desc">
            Scan the full NSE universe for EMA/SMA crossover and RSI extreme
            signals across any timeframe. Based on the Pine Script "SWING CALLS" strategy.
        </div>
        <ul class="card-features">
            <li>Nifty 50, Nifty Next 50, All F&O stocks</li>
            <li>10+ sector groups (Banking, IT, Pharma, Auto…)</li>
            <li>BUY: SMA crosses under EMA + High > SMA</li>
            <li>SELL: SMA crosses over EMA + Open > Close</li>
            <li>RSI Bullish ↑ / RSI Bearish ↓ signals</li>
            <li>Any timeframe from 1-min to Monthly</li>
            <li>Configurable EMA, SMA, RSI lengths</li>
            <li>Download results as CSV</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ── Install instructions
st.markdown("""
<div class="install-box">
    <div class="install-title">SETUP INSTRUCTIONS</div>
    <div style="font-size:0.92rem; font-weight:700; color:#2e4060; line-height:2.2;">
        <b style="color:#00c8ff;">1. Install dependencies</b><br>
        &nbsp;&nbsp;&nbsp;
        <code>pip install streamlit tvdatafeed pandas numpy plotly pandas-ta-classic</code>
        <br>
        <b style="color:#00c8ff;">2. Run the app (from inside scanner_app/ folder)</b><br>
        &nbsp;&nbsp;&nbsp;
        <code>streamlit run Home.py</code>
        <br>
        <b style="color:#00c8ff;">3. Navigate</b><br>
        &nbsp;&nbsp;&nbsp;
        Use the <b style="color:#00e87a;">sidebar</b> to switch between pages.
        <br>
        <b style="color:#00c8ff;">4. TradingView login</b><br>
        &nbsp;&nbsp;&nbsp;
        Both tools accept TV username/password — leave blank for Guest mode.
    </div>
</div>
""", unsafe_allow_html=True)
