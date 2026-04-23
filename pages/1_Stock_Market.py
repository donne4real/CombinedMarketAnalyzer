"""
Stock Market Analysis Application
Streamlit Web Interface

Features:
- Stock Analysis: Analyze stocks using 10 investment strategies
- Backtesting: Test strategies on historical data
"""

import os
import sys

# Ensure the root project directory is in the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import streamlit as st

from shared_src.visuals import create_speedometer, create_radar_chart
from shared_src.ai_summary import generate_stock_summary
from stock_src.data_fetcher import StockDataFetcher, get_nasdaq_nyse_tickers, get_sp500_tickers
from stock_src.strategies import InvestmentStrategies, STRATEGY_NAMES
from stock_src.exporter import SpreadsheetExporter
from stock_src.backtester import Backtester, BacktestConfig, BacktestResults


# Page configuration
st.set_page_config(
    page_title="Stock Market Analyzer",
    page_icon="📈",
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
    .strategy-score {
        font-size: 1.2rem;
        font-weight: bold;
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
    if "backtest_results" not in st.session_state:
        st.session_state.backtest_results = None
    if "backtest_complete" not in st.session_state:
        st.session_state.backtest_complete = False


def analyze_stocks(stocks_data):
    """Run all 10 strategies on the fetched stocks."""
    strategies_data = []
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, stock in enumerate(stocks_data):
        analysis = InvestmentStrategies.analyze_stock(stock)
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


def render_stock_analysis_page():
    """Render the main stock analysis page."""
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")

        # Stock universe selection
        stock_universe = st.selectbox(
            "Stock Universe",
            ["S&P 500", "NASDAQ/NYSE Popular", "Custom Tickers"],
            help="Choose which stocks to analyze"
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

        # Price filter
        st.subheader("💰 Price Filter")
        max_price = st.number_input(
            "Max Stock Price ($)",
            min_value=1,
            max_value=10000,
            value=50,
            step=1,
            help="Only analyze stocks with price below this value"
        )
        enable_price_filter = st.checkbox("Enable price filter", value=True)

        # Sector filter
        st.subheader("🏭 Sector Filter")
        sector_options = [
            "Technology",
            "Healthcare",
            "Financial Services",
            "Consumer Cyclical",
            "Consumer Defensive",
            "Industrials",
            "Energy",
            "Utilities",
            "Real Estate",
            "Basic Materials",
            "Communication Services"
        ]
        selected_sectors = st.multiselect(
            "Select Sectors",
            options=sector_options,
            default=[],
            help="Filter stocks by sector (select multiple)"
        )
        enable_sector_filter = st.checkbox("Enable sector filter", value=False)

        # Analysis options
        st.subheader("Analysis Options")
        clear_cache_btn = st.button("🗑️ Clear Cache", on_click=clear_cache)

        # Cache info
        cache_dir = os.path.join(os.path.expanduser("~"), ".qwen_stock_analyzer", "cache")
        cache_file = os.path.join(cache_dir, "stock_cache.json")
        if os.path.exists(cache_file):
            st.info(f"✓ Cache available")
        else:
            st.warning("No cache")

        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        **15 Investment Strategies:**
        - Benjamin Graham (Value)
        - Magic Formula (Greenblatt)
        - Piotroski F-Score
        - Altman Z-Score
        - Growth Model
        - Dividend Discount
        - Momentum Strategy
        - Quality Model
        - Fama-French 3-Factor
        - Mean Reversion
        - Rule of 40 (SaaS/Tech)
        - Buffett Economic Moat
        - CAN SLIM
        - Peter Lynch GARP
        - Beneish M-Score
        """)

    # Main content area
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Strategy Count", "10")
    with col2:
        st.metric("Exchanges", "NASDAQ + NYSE")
    with col3:
        st.metric("Data Source", "Yahoo Finance")
    with col4:
        if st.session_state.analysis_complete:
            st.metric("Stocks Analyzed", len(st.session_state.stocks_data))
        else:
            st.metric("Stocks Analyzed", "-")

    # Start analysis button
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("🚀 Start Analysis")
    with col2:
        start_btn = st.button("▶️ Run Analysis", type="primary", use_container_width=True)

    if start_btn:
        # Get tickers
        if stock_universe == "S&P 500":
            with st.spinner("Fetching S&P 500 ticker list..."):
                tickers = get_sp500_tickers()
                st.success(f"Found {len(tickers)} S&P 500 stocks")
        elif stock_universe == "NASDAQ/NYSE Popular":
            tickers = get_nasdaq_nyse_tickers()
            st.success(f"Analyzing {len(tickers)} popular stocks")
        else:
            tickers = [t.strip().upper() for t in custom_tickers.split(",") if t.strip()]
            if not tickers:
                st.error("Please enter at least one ticker")
                st.stop()
            st.success(f"Analyzing {len(tickers)} custom tickers")

        # Fetch data
        st.markdown("### 📊 Fetching Stock Data...")
        with st.status("Fetching data from Yahoo Finance...", expanded=True) as status:
            stocks_data = st.session_state.fetcher.fetch_multiple(tickers, batch_size=50)
            if stocks_data:
                status.update(label=f"✅ Successfully fetched {len(stocks_data)} stocks!", state="complete", expanded=False)
            else:
                status.update(label="❌ Failed to fetch any stock data", state="error", expanded=True)

        if not stocks_data:
            error_msg = st.session_state.fetcher.last_error or "Yahoo Finance is rate-limiting the server or the tickers are invalid."
            st.error(f"No data fetched for the {len(tickers)} tickers attempted. Reason: {error_msg}")
            st.info("💡 **Tip:** Try again in a few minutes, or try a smaller 'Custom Ticker' list (e.g., AAPL, MSFT) to see if it works.")
            st.stop()

        # Apply price filter
        if enable_price_filter:
            original_count = len(stocks_data)
            stocks_data = [s for s in stocks_data if s.get("price") and s["price"] < max_price]
            filtered_count = original_count - len(stocks_data)
            st.info(f"💰 Price filter applied: {filtered_count} stocks removed (price ≥ ${max_price})")
            st.success(f"Remaining: {len(stocks_data)} stocks under ${max_price}")

        # Apply sector filter
        if enable_sector_filter and selected_sectors:
            original_count = len(stocks_data)
            stocks_data = [s for s in stocks_data if s.get("sector") in selected_sectors]
            filtered_count = original_count - len(stocks_data)
            st.info(f"🏭 Sector filter applied: {filtered_count} stocks removed (not in selected sectors)")
            st.success(f"Remaining: {len(stocks_data)} stocks in {len(selected_sectors)} sector(s)")

        st.session_state.stocks_data = stocks_data

        # Analyze stocks
        st.markdown("### 🧠 Running Strategy Analysis...")
        strategies_data = analyze_stocks(stocks_data)
        st.session_state.strategies_data = strategies_data
        st.session_state.analysis_complete = True

        st.success(f"✅ Analysis complete! {len(stocks_data)} stocks analyzed.")
        st.rerun()

    # Results section
    if st.session_state.analysis_complete and st.session_state.stocks_data:
        render_analysis_results()


def render_analysis_results():
    """Render the analysis results section."""
    st.markdown("---")
    st.header("📊 Analysis Results")

    stocks_data = st.session_state.stocks_data
    strategies_data = st.session_state.strategies_data

    # Create results DataFrame
    results = []
    for stock, strategies in zip(stocks_data, strategies_data):
        row = {"Ticker": stock.get("symbol", "")}
        row["Company"] = stock.get("name", "")[:40]
        row["Sector"] = stock.get("sector", "")
        row["Price"] = stock.get("price")
        row["Market Cap"] = stock.get("market_cap")

        # Add strategy scores
        for strategy_key, strategy_name in STRATEGY_NAMES.items():
            row[strategy_name] = strategies.get(strategy_key, {}).get("score", 0)

        row["Total"] = strategies.get("total_score", 0)
        row["Average"] = strategies.get("average_score", 0)
        results.append(row)

    df = pd.DataFrame(results)
    df = df.sort_values("Total", ascending=False)

    # Top performers
    st.subheader("🏆 Top 10 Stocks")
    top_10 = df.head(10).copy()
    top_10["Price"] = top_10["Price"].apply(lambda x: f"${x:.2f}" if x else "N/A")
    top_10["Market Cap"] = top_10["Market Cap"].apply(
        lambda x: f"${x/1e9:.1f}B" if x and x > 1e9 else f"${x/1e6:.0f}M" if x else "N/A"
    )
    st.dataframe(
        top_10[["Ticker", "Company", "Sector", "Price", "Market Cap", "Total", "Average"]],
        use_container_width=True,
        hide_index=True
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
        sector_counts = df["Sector"].value_counts().sort_values(ascending=False)
        sector_df = pd.DataFrame({
            "Sector": sector_counts.index,
            "Count": sector_counts.values,
            "Avg Score": [df[df["Sector"] == s]["Total"].mean() for s in sector_counts.index]
        })

        col1, col2 = st.columns(2)
        with col1:
            st.bar_chart(sector_df.set_index("Sector")["Count"])
        with col2:
            st.bar_chart(sector_df.set_index("Sector")["Avg Score"])

        # Sector summary table
        st.dataframe(
            sector_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Sector": "Sector",
                "Count": st.column_config.NumberColumn("Stocks", format="%d"),
                "Avg Score": st.column_config.NumberColumn("Avg Total Score", format="%.2f")
            }
        )

    # Full results table
    st.subheader("📋 Full Results")
    st.markdown("Score legend: 🟢 8-10 | 🟡 5-7 | 🔴 0-4")

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

    # Detailed view
    with st.expander("🔍 View Detailed Results Table"):
        display_df = df.copy()
        display_df["Price"] = display_df["Price"].apply(lambda x: f"${x:.2f}" if x else "N/A")
        display_df["Market Cap"] = display_df["Market Cap"].apply(
            lambda x: f"${x/1e9:.2f}B" if x and x > 1e9 else f"${x/1e6:.0f}M" if x else "N/A"
        )
        st.dataframe(
            display_df, 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "Ticker": st.column_config.TextColumn("Ticker", help="The stock symbol used on the exchange."),
                "Company": st.column_config.TextColumn("Company", help="The full name of the corporation."),
                "Sector": st.column_config.TextColumn("Sector", help="The segment of the economy the company operates within."),
                "Market Cap": st.column_config.TextColumn("Market Cap", help="The total dollar value of all outstanding shares. A measure of the company's size."),
                "Price": st.column_config.TextColumn("Price", help="The current trading price per share."),
                "Total Score": st.column_config.NumberColumn("Total Score", help="The sum of all 15 strategy scores. Maximum possible is 150 points. Over 70 suggests strong potential.")
            }
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

            with col2:
                total_score = strategies.get("total_score", 0)
                st.metric("Total Score", f"{total_score}/150")
                st.metric("Average Score", f"{strategies.get('average_score', 0):.2f}/10")

            # --- AI Summary ---
            with st.spinner("🤖 Generating AI Insight..."):
                summary = generate_stock_summary(
                    stock.get("name", ""), 
                    stock.get("symbol", ""), 
                    "Stock", 
                    strategies
                )
                st.info(f"**AI Insight:** {summary}", icon="🤖")

            # --- Visualizations ---
            st.markdown("---")
            viz_col1, viz_col2 = st.columns(2)
            
            with viz_col1:
                st.markdown("#### Overall Rating")
                speedometer = create_speedometer(total_score, max_score=150, title="Investment Grade")
                st.plotly_chart(speedometer, use_container_width=True)
                
            with viz_col2:
                st.markdown("#### Fundamental Balance")
                # Group 15 strategies into 5 radar dimensions
                spider_categories = {
                    "Value": ["graham_value", "lynch_garp"],
                    "Growth/Momentum": ["momentum", "growth", "rule_of_40", "can_slim"],
                    "Quality/Moat": ["quality", "buffett_moat"],
                    "Safety": ["altman_z", "piotroski_f", "beneish_m", "dividend"],
                    "Other": ["risk_adjusted", "insider", "analyst"]
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


def render_backtesting_page():
    """Render the backtesting page."""
    st.markdown('<p class="main-header">🔙 Strategy Backtesting</p>', unsafe_allow_html=True)
    st.markdown("Test investment strategies on **historical data** with realistic simulations")

    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Backtest Settings")

        # Date range
        st.subheader("📅 Date Range")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=datetime.now() - timedelta(days=730),
                max_value=datetime.now() - timedelta(days=30)
            )
        with col2:
            end_date = st.date_input(
                "End Date",
                value=datetime.now(),
                min_value=start_date + timedelta(days=30),
                max_value=datetime.now()
            )

        # Capital
        st.subheader("💰 Initial Capital")
        initial_capital = st.number_input(
            "Amount ($)",
            min_value=1000,
            max_value=10000000,
            value=100000,
            step=10000
        )

        # Rebalance frequency
        st.subheader("🔄 Rebalance Frequency")
        rebalance_freq = st.selectbox(
            "How often to rebalance",
            options=["daily", "weekly", "monthly", "quarterly", "yearly"],
            index=2  # Default to monthly
        )

        # Position sizing
        st.subheader("📊 Position Sizing")
        position_size = st.slider(
            "Max per position (%)",
            min_value=5,
            max_value=50,
            value=10,
            step=5,
            help="Maximum percentage of portfolio in single stock"
        )

        # Score threshold
        st.subheader("🎯 Quality Threshold")
        min_score = st.slider(
            "Minimum total score to buy",
            min_value=30,
            max_value=80,
            value=50,
            step=5,
            help="Stocks must score at least this to be purchased"
        )

        # Transaction costs
        st.subheader("💸 Transaction Costs")
        transaction_cost = st.slider(
            "Cost per trade (%)",
            min_value=0.0,
            max_value=1.0,
            value=0.1,
            step=0.05
        )

        # Benchmark
        st.subheader("📈 Benchmark")
        benchmark = st.selectbox(
            "Comparison benchmark",
            options=["SPY", "QQQ", "DIA", "IWM"],
            index=0
        )

        # Stock selection
        st.subheader("🏢 Stock Universe")
        stock_universe = st.selectbox(
            "Stocks to test",
            ["S&P 500", "NASDAQ/NYSE Popular", "Custom Tickers"],
        )

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

        # Run button
        st.markdown("---")
        run_backtest = st.button("▶️ Run Backtest", type="primary", use_container_width=True)

    # Main display area
    if run_backtest:
        # Get tickers
        with st.spinner("Preparing stock list..."):
            if stock_universe == "S&P 500":
                tickers = get_sp500_tickers()[:50]  # Limit for speed
                st.info(f"Using first 50 S&P 500 stocks")
            elif stock_universe == "NASDAQ/NYSE Popular":
                tickers = get_nasdaq_nyse_tickers()
            else:
                tickers = [t.strip().upper() for t in custom_tickers.split(",") if t.strip()]
                if not tickers:
                    st.error("Please enter at least one ticker")
                    st.stop()

        # Create config
        config = BacktestConfig(
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            initial_capital=initial_capital,
            rebalance_frequency=rebalance_freq,
            position_size_pct=position_size / 100,
            min_score_threshold=min_score,
            transaction_cost_pct=transaction_cost / 100,
            benchmark=benchmark
        )

        # Run backtest
        st.markdown("### 🔄 Running Backtest...")
        progress = st.progress(0)
        status = st.empty()

        try:
            backtester = Backtester(config)
            results = backtester.run_backtest(tickers)
            st.session_state.backtest_results = results
            st.session_state.backtest_complete = True
            st.success("✅ Backtest complete!")
            st.rerun()
        except Exception as e:
            st.error(f"Backtest failed: {str(e)}")
            st.stop()

    # Display results
    if st.session_state.backtest_complete and st.session_state.backtest_results:
        render_backtest_results()


def render_backtest_results():
    """Render backtest results."""
    results = st.session_state.backtest_results

    # Summary metrics
    st.markdown("---")
    st.header("📊 Backtest Results")

    # Key metrics
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        total_ret = results.total_return * 100
        st.metric("Total Return", f"{total_ret:.1f}%")

    with col2:
        ann_ret = results.annualized_return * 100
        st.metric("Annual Return", f"{ann_ret:.1f}%")

    with col3:
        bench_ret = results.benchmark_return * 100
        st.metric("Benchmark Return", f"{bench_ret:.1f}%")

    with col4:
        st.metric("Sharpe Ratio", f"{results.sharpe_ratio:.2f}")

    with col5:
        max_dd = results.max_drawdown * 100
        st.metric("Max Drawdown", f"{-max_dd:.1f}%")

    # Additional metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Volatility", f"{results.volatility * 100:.1f}%")

    with col2:
        st.metric("Sortino Ratio", f"{results.sortino_ratio:.2f}")

    with col3:
        st.metric("Beta", f"{results.beta:.2f}")

    with col4:
        st.metric("Alpha", f"{results.alpha * 100:.1f}%")

    # Performance chart
    st.subheader("📈 Portfolio Growth")

    if len(results.portfolio_values) > 0:
        chart_data = results.portfolio_values.copy()
        chart_data.index = chart_data.index.date
        st.line_chart(chart_data, use_container_width=True)

    # Comparison stats
    st.subheader("📊 Performance Comparison")
    comp_df = pd.DataFrame({
        "Metric": ["Total Return", "Annual Return", "Volatility", "Sharpe", "Max Drawdown"],
        "Strategy": [
            f"{results.total_return * 100:.1f}%",
            f"{results.annualized_return * 100:.1f}%",
            f"{results.volatility * 100:.1f}%",
            f"{results.sharpe_ratio:.2f}",
            f"{-results.max_drawdown * 100:.1f}%"
        ],
        "Benchmark": [
            f"{results.benchmark_return * 100:.1f}%",
            "N/A",
            "N/A",
            "N/A",
            "N/A"
        ]
    })
    st.dataframe(comp_df, use_container_width=True, hide_index=True)

    # Trading statistics
    st.subheader("💹 Trading Statistics")
    trade_col1, trade_col2, trade_col3, trade_col4 = st.columns(4)

    with trade_col1:
        st.metric("Total Trades", results.total_trades)

    with trade_col2:
        st.metric("Winning Trades", results.winning_trades)

    with trade_col3:
        st.metric("Losing Trades", results.losing_trades)

    with trade_col4:
        st.metric("Win Rate", f"{results.win_rate * 100:.1f}%")

    st.metric("Total Transaction Costs", f"${results.total_transaction_costs:,.2f}")

    # Trade history
    with st.expander("📋 View Trade History"):
        if results.trades:
            trade_df = pd.DataFrame([{
                "Date": t.date.strftime("%Y-%m-%d"),
                "Ticker": t.ticker,
                "Action": t.action,
                "Shares": t.shares,
                "Price": f"${t.price:.2f}",
                "Value": f"${t.value:,.2f}",
                "Cost": f"${t.transaction_cost:.2f}",
                "Reason": t.reason
            } for t in results.trades])
            st.dataframe(trade_df, use_container_width=True)

    # Export
    st.subheader("💾 Export Results")
    if st.button("📥 Export to Excel"):
        backtester = Backtester(results.config)
        filepath = backtester.export_results(results)
        with open(filepath, "rb") as f:
            st.download_button(
                label="⬇️ Download Excel",
                data=f.read(),
                file_name=os.path.basename(filepath),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

    # Strategy insights
    st.subheader("💡 Key Insights")
    insights = []

    if results.excess_return > 0:
        insights.append(f"✅ Strategy outperformed benchmark by {results.excess_return * 100:.1f}%")
    else:
        insights.append(f"⚠️ Strategy underperformed benchmark by {abs(results.excess_return) * 100:.1f}%")

    if results.sharpe_ratio > 1.5:
        insights.append("✅ Excellent risk-adjusted returns (Sharpe > 1.5)")
    elif results.sharpe_ratio > 1.0:
        insights.append("✅ Good risk-adjusted returns (Sharpe > 1.0)")
    elif results.sharpe_ratio > 0.5:
        insights.append("⚠️ Moderate risk-adjusted returns")
    else:
        insights.append("⚠️ Low risk-adjusted returns")

    if results.max_drawdown < 0.15:
        insights.append("✅ Low maximum drawdown (< 15%)")
    elif results.max_drawdown < 0.25:
        insights.append("⚠️ Moderate drawdown")
    else:
        insights.append("⚠️ High drawdown (> 25%)")

    for insight in insights:
        st.markdown(insight)


def main():
    """Main entry point for the application."""
    init_session_state()

    # Header
    st.markdown('<p class="main-header">📈 Stock Market Analyzer</p>', unsafe_allow_html=True)
    st.markdown("Analyze NASDAQ & NYSE stocks using **10 top investment strategies**")

    # Navigation
    page = st.sidebar.radio("Navigation", ["Stock Analysis", "Backtesting"])

    if page == "Stock Analysis":
        render_stock_analysis_page()
    else:
        render_backtesting_page()

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "Stock Market Analyzer • Data from Yahoo Finance • For educational purposes only"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
