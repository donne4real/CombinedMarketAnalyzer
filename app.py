import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(
    page_title="Combined Market Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Theme and UI Polish
st.markdown("""
<style>
    /* Premium Look Header */
    .market-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Metric Cards */
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 700;
        color: #f7f9fd;
    }
    div[data-testid="stMetricDelta"] {
        font-size: 1.1rem !important;
        font-weight: 600;
    }
    
    /* Clean feature boxes */
    .feature-box {
        padding: 1.5rem;
        background-color: rgba(128, 128, 128, 0.1);
        border-radius: 8px;
        border-left: 5px solid #007bff;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="market-header">
    <h1 style='color: white; margin-bottom: 0px;'>📈 Combined Market Analyzer Dashboard</h1>
    <p style='font-size: 1.2rem; opacity: 0.9;'>A unified intelligence platform for Stocks, ETFs, Mutual Funds, and 100-Bagger Scanners</p>
</div>
""", unsafe_allow_html=True)

# Rate Limiting Configuration Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Rate limit delay slider (in seconds)
    rate_limit_delay = st.slider(
        "API Rate Limit Delay (seconds)",
        min_value=0.5,
        max_value=10.0,
        value=2.0,
        step=0.5,
        help="Adjust the delay between API requests. Higher values are more conservative and less likely to hit rate limits, but slower. Lower values are faster but may trigger rate limiting."
    )
    
    # Store in session state for fetchers to use
    st.session_state.rate_limit_delay = rate_limit_delay
    
    st.info(f"Current delay: {rate_limit_delay}s between requests")
    
    st.divider()

# Function to fetch global market indicators quickly
@st.cache_data(ttl=300)  # cache for 5 minutes
def fetch_market_overview():
    tickers = {"^GSPC": "S&P 500", "^RUT": "Russell 2000", "^IXIC": "NASDAQ", "^VIX": "Volatility (VIX)"}
    data = {}
    
    try:
        # Setup a robust session
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        })
        
        # Fetch batch
        hist = yf.download(list(tickers.keys()), period="5d", progress=False, session=session)["Close"]
        
        for symbol, name in tickers.items():
            try:
                if len(hist[symbol]) >= 2:
                    current = hist[symbol].iloc[-1]
                    prev = hist[symbol].iloc[-2]
                    change = current - prev
                    pct_change = (change / prev) * 100
                    data[name] = {"price": current, "change": change, "pct_change": pct_change}
            except KeyError:
                # Symbol not found in the downloaded data
                st.warning(f"Market data for {name} ({symbol}) not available")
            except Exception as e:
                st.warning(f"Error processing {name} ({symbol}): {str(e)}")
    except requests.exceptions.RequestException as e:
        st.error(f"Network error fetching market overview: {str(e)}. Please check your internet connection.")
    except Exception as e:
        st.error(f"Error fetching market overview: {str(e)}. This may be due to Yahoo Finance rate limits.")
        
    return data

st.markdown("### 🌐 Live Market Overview")
market_data = fetch_market_overview()

if market_data:
    cols = st.columns(len(market_data))
    for i, (name, metrics) in enumerate(market_data.items()):
        delta_color = "inverse" if "VIX" in name else "normal"
        with cols[i]:
            st.metric(
                label=name, 
                value=f"{metrics['price']:.2f}",
                delta=f"{metrics['change']:.2f} ({metrics['pct_change']:.2f}%)",
                delta_color=delta_color
            )
elif not st.session_state.get("market_error_shown", False):
    st.session_state.market_error_shown = True
    st.warning("Market data is currently unavailable. This may be due to network issues or Yahoo Finance rate limits. Data will be cached for 5 minutes.")
    
st.divider()

st.markdown("### 🚀 Available Tools")
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-box">
        <h3>📊 1. Stock Market Analysis</h3>
        <p>Run individual stocks through 10 sophisticated investment strategies including Benjamin Graham, Magic Formula, and Piotroski F-Score to find their true value.</p>
    </div>
    
    <div class="feature-box">
        <h3>🏦 2. ETF Analyzer</h3>
        <p>Dive deep into Exchange Traded Funds. Understand their asset allocations, dividend consistency, and risk-adjusted performances compared to the broader market.</p>
    </div>
    """, unsafe_allow_html=True)
    
with col2:
    st.markdown("""
    <div class="feature-box">
        <h3>💼 3. Mutual Funds</h3>
        <p>Screen and track top industry Mutual Funds. Analyze expense ratios, long term returns, and top 10 holding concentrations.</p>
    </div>
    
    <div class="feature-box">
        <h3>🎯 4. 100-Bagger Screener</h3>
        <p>Hunt for the next high-growth unicorn. Scans for low PEGs, high ROE, robust operating cash flows and founder-led organizations to predict massive multipliers.</p>
    </div>
    """, unsafe_allow_html=True)
    
st.info("👈 **Select a module from the Side Navigation Bar to get started!** Alternatively, check out the new **Watchlist** page to manage your entire portfolio from a single dashboard.")

st.markdown(f"**Last Data Refresh:** `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`")
