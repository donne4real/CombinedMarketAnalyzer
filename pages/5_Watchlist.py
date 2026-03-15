import streamlit as st
import pandas as pd

from shared_src.watchlist_manager import WatchlistManager
from stock_src.data_fetcher import StockDataFetcher
from etf_src.data_fetcher import ETFDataFetcher
from mf_src.data_fetcher import MutualFundDataFetcher

st.set_page_config(
    page_title="Portfolio Watchlist",
    page_icon="📋",
    layout="wide"
)

# Initialize Session State & Managers
if "watchlist_mgr" not in st.session_state:
    st.session_state.watchlist_mgr = WatchlistManager()
if "stock_fetcher" not in st.session_state:
    st.session_state.stock_fetcher = StockDataFetcher()
if "etf_fetcher" not in st.session_state:
    st.session_state.etf_fetcher = ETFDataFetcher()
if "mf_fetcher" not in st.session_state:
    st.session_state.mf_fetcher = MutualFundDataFetcher()

manager = st.session_state.watchlist_mgr

st.title("📋 Cross-Asset Portfolio Watchlist")
st.markdown("Track and manage your Favorite Stocks, ETFs, and Mutual Funds all in one place.")

# Sidebar Controls
with st.sidebar:
    st.header("Manage Watchlist")
    
    with st.form("add_ticker_form", clear_on_submit=True):
        st.subheader("Add Asset")
        new_ticker = st.text_input("Ticker Symbol (e.g., AAPL, SPY)").upper()
        asset_type = st.selectbox("Asset Type", ["stocks", "etfs", "funds"])
        submit_add = st.form_submit_button("Add to Watchlist")
        
        if submit_add and new_ticker:
            success = manager.add_ticker(asset_type, new_ticker)
            if success:
                st.success(f"Added {new_ticker} to {asset_type}!")
            else:
                st.info(f"{new_ticker} is already in the watchlist.")
                
    st.divider()
    
    with st.form("remove_ticker_form", clear_on_submit=True):
        st.subheader("Remove Asset")
        rem_ticker = st.text_input("Ticker to Remove").upper()
        rem_asset_type = st.selectbox("Type", ["stocks", "etfs", "funds"])
        submit_remove = st.form_submit_button("Remove from Watchlist")
        
        if submit_remove and rem_ticker:
            success = manager.remove_ticker(rem_asset_type, rem_ticker)
            if success:
                st.success(f"Removed {rem_ticker}")
            else:
                st.warning(f"Could not find {rem_ticker} in {rem_asset_type}.")

# Fetch and Display Data
watchlist = manager.get_watchlist()

# Helper function to render a clean dataframe
def render_metrics_grid(title, tickers, fetcher, fetch_logic_desc=""):
    st.subheader(title)
    if not tickers:
        st.info(f"No {title.lower()} currently tracked in Watchlist.")
        return

    with st.spinner(f"Loading {title}..."):
        # We assume fetch_multiple exists directly on the instantiated subclasses
        data = fetcher.fetch_multiple(tickers, batch_size=20)
        
    if not data:
        st.warning("Could not retrieve data for the requested trackers.")
        return

    # Convert complex dicts into a simpler flat DataFrame for overview
    rows = []
    for d in data:
        row = {
            "Symbol": d.get("symbol", "N/A"),
            "Name": d.get("name", "N/A"),
            "Price/NAV": d.get("price", d.get("nav_price", "N/A")),
        }
        # Safely add return fields if they exist depending on the asset
        if "dividend_yield" in d and isinstance(d["dividend_yield"], float):
            row["Yield"] = f"{d['dividend_yield']*100:.2f}%"
        if "ytd_return" in d and isinstance(d["ytd_return"], float):
            row["YTD Return"] = f"{d['ytd_return']*100:.2f}%"
        if "pe_ratio" in d:
            row["P/E"] = str(round(d["pe_ratio"], 2)) if isinstance(d["pe_ratio"], float) else "N/A"
            
        rows.append(row)
        
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)


col1, col2 = st.tabs(["Dashboard View", "Detailed Statistics"])

with col1:
    render_metrics_grid("Tracked Stocks", watchlist.get("stocks", []), st.session_state.stock_fetcher)
    st.divider()
    render_metrics_grid("Tracked ETFs", watchlist.get("etfs", []), st.session_state.etf_fetcher)
    st.divider()
    render_metrics_grid("Tracked Mutual Funds", watchlist.get("funds", []), st.session_state.mf_fetcher)

with col2:
    st.markdown("### Raw Combined JSON")
    st.json(watchlist)
