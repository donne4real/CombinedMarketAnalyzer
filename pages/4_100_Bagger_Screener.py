"""
100-Bagger Stock Screener Application
Streamlit Web Interface

Based on Peter Lynch's investment philosophy from:
- "One Up on Wall Street"
- "Beating the Street"

Features:
- Screen for stocks with 100-bagger potential
- 10 investment strategies based on Lynch's criteria
- Export results to Excel/CSV
"""

import os
import sys
from datetime import datetime, timedelta

# Ensure the root project directory is in the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import streamlit as st

from shared_src.visuals import create_speedometer, create_radar_chart
from shared_src.ai_summary import generate_stock_summary
from bagger_src.data_fetcher import (
    StockDataFetcher,
    get_small_cap_stocks,
    get_growth_stocks,
    get_peter_lynch_style_stocks,
    get_all_screening_stocks,
)
from bagger_src.strategies import HundredBaggerStrategies, STRATEGY_NAMES
from bagger_src.exporter import SpreadsheetExporter


# Page configuration
st.set_page_config(
    page_title="100-Bagger Stock Screener",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A8A;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .score-high { color: #059669; }
    .score-medium { color: #D97706; }
    .score-low { color: #DC2626; }
    </style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables."""
    if "stocks_data" not in st.session_state:
        st.session_state.stocks_data = []
    if "strategies_data" not in st.session_state:
        st.session_state.strategies_data = []
    if "analysis_complete" not in st.session_state:
        st.session_state.analysis_complete = False
    if "fetcher" not in st.session_state:
        st.session_state.fetcher = StockDataFetcher()


def analyze_stocks(stocks_data):
    """Run all 10 strategies on the fetched stocks."""
    strategies_data = []
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, stock in enumerate(stocks_data):
        analysis = HundredBaggerStrategies.analyze_stock(stock)
        strategies_data.append(analysis)
        progress_bar.progress((i + 1) / len(stocks_data))
        status_text.text(f"Analyzing: {stock.get('symbol', 'N/A')} ({i + 1}/{len(stocks_data)})")

    status_text.text("Analysis complete!")
    return strategies_data


def clear_cache():
    """Clear the data cache."""
    st.session_state.fetcher.clear_cache()
    st.session_state.stocks_data = []
    st.session_state.strategies_data = []
    st.session_state.analysis_complete = False
    st.success("Cache cleared!")


def get_100bagger_recommendation(score: float) -> str:
    """Get 100-bagger recommendation based on score."""
    if score >= 70:
        return "🚀 Strong 100-Bagger Potential"
    elif score >= 50:
        return "⭐ Good Potential"
    elif score >= 30:
        return "⚠️ Moderate Potential"
    else:
        return "❌ Low Potential"


def render_main_page():
    """Render the main screening page."""
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Screening Settings")

        # Stock universe selection
        stock_universe = st.selectbox(
            "Stock Universe",
            ["All Stocks", "Small-Cap Focus", "Growth Stocks", "Lynch-Style", "Custom Tickers"],
            help="Choose which stocks to screen"
        )

        # Custom tickers input
        custom_tickers = ""
        if stock_universe == "Custom Tickers":
            uploaded_file = st.file_uploader("Upload CSV/TXT of Tickers", type=["csv", "txt"], help="Upload a file with one ticker per line, or comma-separated.")
            if uploaded_file is not None:
                try:
                    df = pd.read_csv(uploaded_file, header=None)
                    # Flatten in case of multiple columns, but usually it's just one
                    file_tickers = []
                    for col in df.columns:
                        file_tickers.extend(df[col].dropna().astype(str).tolist())
                    custom_tickers = ",".join(file_tickers)
                    st.success(f"Loaded {len(file_tickers)} tickers from file!")
                except Exception as e:
                    st.error(f"Error reading file: {e}")
                    
            custom_tickers = st.text_area(
                "Or manually enter/edit tickers (comma-separated)",
                value=custom_tickers,
                placeholder="AAPL, MSFT, GOOGL, TSLA",
                height=100
            )

        # Screening criteria
        st.subheader("🎯 Screening Criteria")

        max_market_cap = st.number_input(
            "Max Market Cap ($B)",
            min_value=0.1,
            max_value=1000.0,
            value=10.0,
            step=0.5,
            help="Filter out stocks larger than this"
        )

        min_revenue_growth = st.slider(
            "Min Revenue Growth (%)",
            min_value=-50,
            max_value=100,
            value=10,
            step=5,
            help="Filter stocks with revenue growth below this"
        )

        max_pe_ratio = st.number_input(
            "Max P/E Ratio",
            min_value=0,
            max_value=200,
            value=50,
            step=5,
            help="Filter out stocks with P/E above this"
        )

        max_debt_equity = st.number_input(
            "Max Debt/Equity",
            min_value=0.0,
            max_value=5.0,
            value=2.0,
            step=0.1,
            help="Filter out stocks with higher debt"
        )

        # Analysis options
        st.subheader("Analysis Options")
        clear_cache_btn = st.button("🗑️ Clear Cache", on_click=clear_cache)

        # Cache info
        cache_dir = os.path.join(os.path.expanduser("~"), ".qwen_100bagger_screener", "cache")
        cache_file = os.path.join(cache_dir, "stock_cache.json")
        if os.path.exists(cache_file):
            st.info(f"✓ Cache available")
        else:
            st.warning("No cache")

        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        **Peter Lynch's 100-Bagger Criteria:**
        - PEG Ratio < 1.5
        - Earnings Growth > 15%
        - Revenue Growth > 15%
        - Low Debt (D/E < 0.5)
        - High Insider Ownership
        - Simple, Understandable Business
        - Small-Cap with Room to Grow
        - Strong Profit Margins
        - Consistent Growth Trajectory
        - "Invest in What You Know"
        """)

    # Main content area
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Strategies", "15")
    with col2:
        st.metric("Focus", "100-Baggers")
    with col3:
        st.metric("Philosophy", "Peter Lynch")
    with col4:
        if st.session_state.analysis_complete:
            st.metric("Stocks Analyzed", len(st.session_state.stocks_data))
        else:
            st.metric("Stocks Analyzed", "-")

    # Start screening button
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("🚀 Start 100-Bagger Screen")
    with col2:
        start_btn = st.button("▶️ Run Screen", type="primary", use_container_width=True)

    if start_btn:
        # Get tickers
        if stock_universe == "All Stocks":
            with st.spinner("Fetching stock list..."):
                tickers = get_all_screening_stocks()
                st.success(f"Found {len(tickers)} stocks to analyze")
        elif stock_universe == "Small-Cap Focus":
            tickers = get_small_cap_stocks()
            st.success(f"Analyzing {len(tickers)} small-cap stocks")
        elif stock_universe == "Growth Stocks":
            tickers = get_growth_stocks()
            st.success(f"Analyzing {len(tickers)} growth stocks")
        elif stock_universe == "Lynch-Style":
            tickers = get_peter_lynch_style_stocks()
            st.success(f"Analyzing {len(tickers)} Lynch-style stocks")
        else:
            tickers = [t.strip().upper() for t in custom_tickers.split(",") if t.strip()]
            if not tickers:
                st.error("Please enter at least one ticker")
                st.stop()
            st.success(f"Analyzing {len(tickers)} custom tickers")

        # Fetch data
        st.markdown("### 📊 Fetching Stock Data...")
        stocks_data = st.session_state.fetcher.fetch_multiple(tickers, batch_size=50)

        if not stocks_data:
            st.error("No data fetched. Please try again or check your internet connection.")
            st.stop()

        # Apply filters
        st.markdown("### 🔍 Applying Filters...")

        original_count = len(stocks_data)

        # Market cap filter
        max_cap_numeric = max_market_cap * 1e9
        stocks_data = [s for s in stocks_data if s.get("market_cap") and s["market_cap"] <= max_cap_numeric]
        st.info(f"Market cap filter: {original_count - len(stocks_data)} stocks removed")

        # Revenue growth filter
        min_growth = min_revenue_growth / 100
        stocks_data = [s for s in stocks_data if s.get("revenue_growth") and s["revenue_growth"] >= min_growth]
        st.info(f"Revenue growth filter: stocks below {min_revenue_growth}% removed")

        # P/E filter
        stocks_data = [s for s in stocks_data if s.get("pe_ratio") and (s["pe_ratio"] <= max_pe_ratio or s["pe_ratio"] < 0)]
        st.info(f"P/E filter: stocks above {max_pe_ratio} removed")

        # Debt/Equity filter
        stocks_data = [s for s in stocks_data if s.get("debt_to_equity") is not None and s["debt_to_equity"] <= max_debt_equity]
        st.info(f"Debt/Equity filter: stocks above {max_debt_equity} removed")

        st.success(f"Remaining: {len(stocks_data)} stocks after filters")

        st.session_state.stocks_data = stocks_data

        # Analyze stocks
        st.markdown("### 🧠 Running 100-Bagger Analysis...")
        strategies_data = analyze_stocks(stocks_data)
        st.session_state.strategies_data = strategies_data
        st.session_state.analysis_complete = True

        st.success(f"✅ Analysis complete! {len(stocks_data)} stocks analyzed.")
        st.rerun()

    # Results section
    if st.session_state.analysis_complete and st.session_state.stocks_data:
        render_results()


def render_results():
    """Render the analysis results section."""
    st.markdown("---")
    st.header("📊 100-Bagger Screening Results")

    stocks_data = st.session_state.stocks_data
    strategies_data = st.session_state.strategies_data

    # Create results DataFrame
    results = []
    for stock, strategies in zip(stocks_data, strategies_data):
        row = {"Ticker": stock.get("symbol", "")}
        row["Company"] = stock.get("name", "")[:40]
        row["Sector"] = stock.get("sector", "")
        row["Market Cap"] = stock.get("market_cap")
        row["Price"] = stock.get("price")
        row["P/E"] = stock.get("pe_ratio")
        row["PEG"] = stock.get("peg_ratio")
        row["Revenue Growth"] = stock.get("revenue_growth")
        row["Earnings Growth"] = stock.get("earnings_growth")
        row["D/E"] = stock.get("debt_to_equity")
        row["Insider Own"] = stock.get("insider_ownership")

        # Add strategy scores
        for strategy_key, strategy_name in STRATEGY_NAMES.items():
            row[strategy_name] = strategies.get(strategy_key, {}).get("score", 0)

        row["Total Score"] = strategies.get("total_score", 0)
        row["Avg Score"] = strategies.get("average_score", 0)
        row["Recommendation"] = get_100bagger_recommendation(row["Total Score"])
        results.append(row)

    df = pd.DataFrame(results)
    df = df.sort_values("Total Score", ascending=False)

    # Summary stats
    total = len(df)
    strong_potential = len(df[df["Total Score"] >= 70])
    good_potential = len(df[(df["Total Score"] >= 50) & (df["Total Score"] < 70)])
    avg_score = round(df["Total Score"].mean()) if not df.empty else 0

    # Display summary
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Stocks", total)
    col2.metric("🚀 Strong Potential", strong_potential, delta_color="off")
    col3.metric("⭐ Good Potential", good_potential, delta_color="off")
    col4.metric("Avg Score", avg_score, delta_color="off")

    # Top 100-bagger candidates
    st.subheader("🏆 Top 100-Bagger Candidates")
    top_10 = df.head(10).copy()

    # Format for display
    display_cols = ["Ticker", "Company", "Sector", "Market Cap", "PEG", "Revenue Growth", "Total Score", "Recommendation"]
    top_10_display = top_10[display_cols].copy()
    top_10_display["Market Cap"] = top_10_display["Market Cap"].apply(lambda x: f"${x/1e9:.2f}B" if x else "N/A")
    top_10_display["PEG"] = top_10_display["PEG"].apply(lambda x: f"{x:.2f}" if x else "N/A")
    top_10_display["Revenue Growth"] = top_10_display["Revenue Growth"].apply(lambda x: f"{x:.1%}" if x else "N/A")

    st.dataframe(
        top_10_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Ticker": st.column_config.TextColumn("Ticker", help="The stock symbol used on the exchange."),
            "Company": st.column_config.TextColumn("Company", help="The full name of the corporation."),
            "Sector": st.column_config.TextColumn("Sector", help="The segment of the economy the company operates within."),
            "Market Cap": st.column_config.TextColumn("Market Cap", help="The total dollar value of all outstanding shares. A measure of the company's size."),
            "PEG": st.column_config.TextColumn("PEG Ratio", help="Price/Earnings-to-Growth. Under 1.0 is considered classically undervalued. Indicates how much you are paying for future growth."),
            "Revenue Growth": st.column_config.TextColumn("Revenue Growth", help="The year-over-year percentage increase in top-line sales. The fuel for future earnings."),
            "Total Score": st.column_config.NumberColumn("Total Score", help="The sum of all 15 strategy scores. Maximum possible is 150 points. Over 70 suggests strong potential."),
            "Recommendation": st.column_config.TextColumn("Recommendation", help="Automated investment thesis based on the Total Score.")
        }
    )

    # Strategy score distribution
    st.subheader("📈 Strategy Score Distribution")
    strategy_cols = list(STRATEGY_NAMES.values())
    strategy_scores = df[strategy_cols].mean().sort_values(ascending=False)

    fig_col, stat_col = st.columns([3, 1])
    with fig_col:
        st.bar_chart(strategy_scores)
    with stat_col:
        st.markdown("**Best Strategy:**")
        st.success(f"{strategy_scores.index[0]}")
        st.markdown("**Worst Strategy:**")
        st.error(f"{strategy_scores.index[-1]}")

    # Sector breakdown
    st.subheader("🏭 Sector Breakdown")
    if "Sector" in df.columns:
        sector_counts = df["Sector"].value_counts().head(10)
        sector_df = pd.DataFrame({
            "Sector": sector_counts.index,
            "Count": sector_counts.values,
            "Avg Score": [df[df["Sector"] == s]["Total Score"].mean() for s in sector_counts.index]
        })

        col1, col2 = st.columns(2)
        with col1:
            st.bar_chart(sector_df.set_index("Sector")["Count"])
        with col2:
            st.bar_chart(sector_df.set_index("Sector")["Avg Score"])

    # Full results table
    st.subheader("📋 Full Results")
    st.markdown("Score legend: 🟢 70-100 | 🟡 50-69 | 🔴 0-49")

    # Export options
    st.subheader("💾 Export")
    export_col1, export_col2 = st.columns(2)

    with export_col1:
        if st.button("📥 Export to Excel", use_container_width=True):
            exporter = SpreadsheetExporter()
            filepath = exporter.export_to_excel(stocks_data, strategies_data)
            with open(filepath, "rb") as f:
                st.download_button(
                    label="⬇️ Download Excel",
                    data=f.read(),
                    file_name=os.path.basename(filepath),
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

    with export_col2:
        if st.button("📄 Export to CSV", use_container_width=True):
            exporter = SpreadsheetExporter()
            filepath = exporter.export_to_csv(stocks_data, strategies_data)
            with open(filepath, "rb") as f:
                st.download_button(
                    label="⬇️ Download CSV",
                    data=f.read(),
                    file_name=os.path.basename(filepath),
                    mime="text/csv",
                    use_container_width=True
                )

    # Individual stock analysis
    st.subheader("🔎 Individual Stock Analysis")
    selected_ticker = st.selectbox(
        "Select a stock to view detailed analysis",
        options=[s.get("symbol", "") for s in stocks_data]
    )

    if selected_ticker:
        idx = next((i for i, s in enumerate(stocks_data) if s.get("symbol") == selected_ticker), None)
        if idx is not None:
            stock = stocks_data[idx]
            strategies = strategies_data[idx]

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"### {stock.get('symbol', '')}")
                st.markdown(f"**{stock.get('name', '')}**")
                st.markdown(f"Sector: {stock.get('sector', 'N/A')}")
                st.markdown(f"Industry: {stock.get('industry', 'N/A')}")
                st.markdown(f"**Market Cap:** ${stock.get('market_cap', 0)/1e9:.2f}B" if stock.get('market_cap') else "**Market Cap:** N/A")
                st.markdown(f"**Price:** ${stock.get('price', 0):.2f}" if stock.get('price') else "**Price:** N/A")
                st.markdown(f"**P/E:** {stock.get('pe_ratio', 0):.1f}" if stock.get('pe_ratio') else "**P/E:** N/A")
                st.markdown(f"**PEG:** {stock.get('peg_ratio', 0):.2f}" if stock.get('peg_ratio') else "**PEG:** N/A")
                st.markdown(f"**Revenue Growth:** {stock.get('revenue_growth', 0):.1%}" if stock.get('revenue_growth') else "**Revenue Growth:** N/A")
                st.markdown(f"**D/E:** {stock.get('debt_to_equity', 0):.2f}" if stock.get('debt_to_equity') is not None else "**D/E:** N/A")
                st.markdown(f"**Insider Ownership:** {stock.get('insider_ownership', 0):.1%}" if stock.get('insider_ownership') else "**Insider Ownership:** N/A")

            with col2:
                total_score = strategies.get("total_score", 0)
                st.metric("Total Score", f"{total_score}/150")
                st.metric("Average Score", f"{strategies.get('average_score', 0):.1f}/10")
                st.metric("Recommendation", get_100bagger_recommendation(total_score))

            # --- AI Summary ---
            with st.spinner("🤖 Generating AI Insight..."):
                summary = generate_stock_summary(
                    stock.get("name", ""), 
                    stock.get("symbol", ""), 
                    "Potential 100-Bagger Stock", 
                    strategies
                )
                st.info(f"**AI Insight:** {summary}", icon="🤖")

            # --- Visualizations ---
            st.markdown("---")
            viz_col1, viz_col2 = st.columns(2)
            
            with viz_col1:
                st.markdown("#### 100-Bagger Potential")
                speedometer = create_speedometer(total_score, max_score=150, title="Multi-Bagger Grade")
                st.plotly_chart(speedometer, use_container_width=True)
                
            with viz_col2:
                st.markdown("#### Fundamental Balance")
                # Group 100-Bagger specific strategies
                spider_categories = {
                    "Growth Engine": ["revenue_growth", "earnings_growth", "peg_ratio", "can_slim", "rule_of_40"],
                    "Profitability & Moat": ["profit_margin", "roc", "quality", "buffett_moat"],
                    "Financial Strength": ["debt_to_equity", "beneish_m", "altman_z", "piotroski_f"],
                    "Valuation": ["market_cap", "graham_value", "lynch_garp"],
                    "Management": ["insider_ownership"]
                }
                radar_chart = create_radar_chart(strategies, spider_categories, title="")
                st.plotly_chart(radar_chart, use_container_width=True)

            # --- Detailed Breakdown ---
            with st.expander("🔍 View Detailed Strategy Breakdown", expanded=False):
                for strategy_key, strategy_name in STRATEGY_NAMES.items():
                    result = strategies.get(strategy_key, {})
                    score = result.get("score", 0)
                    reason = result.get("reason", "")
    
                    score_emoji = ""
                    if score >= 8:
                        score_emoji = "🟢"
                    elif score >= 5:
                        score_emoji = "🟡"
                    else:
                        score_emoji = "🔴"
    
                    st.markdown(f"{score_emoji} **{strategy_name}**: {score}/10 - {reason}")


def main():
    """Main entry point for the application."""
    init_session_state()

    # Header
    st.markdown('<p class="main-header">🚀 100-Bagger Stock Screener</p>', unsafe_allow_html=True)
    st.markdown("""
    Find stocks with **100x potential** using Peter Lynch's investment philosophy.
    
    Based on principles from *"One Up on Wall Street"* and *"Beating the Street"*.
    """)

    render_main_page()


if __name__ == "__main__":
    main()
