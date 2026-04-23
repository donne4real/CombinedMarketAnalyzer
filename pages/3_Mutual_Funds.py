"""
Mutual Fund Analyzer Application
Streamlit Web Interface

Features:
- Mutual Fund Analysis: Analyze funds using 10 investment strategies
- Backtesting: Test strategies on historical data
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
from mf_src.data_fetcher import MutualFundDataFetcher, get_fund_categories, get_all_fund_tickers
from mf_src.strategies import MutualFundStrategies, STRATEGY_NAMES
from mf_src.exporter import SpreadsheetExporter
from mf_src.backtester import Backtester, BacktestConfig


# Page configuration
st.set_page_config(
    page_title="Mutual Fund Analyzer",
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
    if "funds_data" not in st.session_state:
        st.session_state.funds_data = []
    if "strategies_data" not in st.session_state:
        st.session_state.strategies_data = []
    if "analysis_complete" not in st.session_state:
        st.session_state.analysis_complete = False
    if "fetcher" not in st.session_state:
        st.session_state.fetcher = MutualFundDataFetcher()
    if "backtest_results" not in st.session_state:
        st.session_state.backtest_results = None
    if "backtest_complete" not in st.session_state:
        st.session_state.backtest_complete = False


def analyze_funds(funds_data):
    """Run all 10 strategies on the fetched mutual funds."""
    strategies_data = []
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, fund in enumerate(funds_data):
        analysis = MutualFundStrategies.analyze_fund(fund)
        strategies_data.append(analysis)
        progress_bar.progress((i + 1) / len(funds_data))
        status_text.text(f"Analyzing: {fund.get('symbol', 'N/A')} ({i + 1}/{len(funds_data)})")

    status_text.text("Analysis complete!")
    return strategies_data


def clear_cache():
    """Clear the data cache."""
    st.session_state.fetcher.clear_cache()
    st.session_state.funds_data = []
    st.session_state.strategies_data = []
    st.session_state.analysis_complete = False
    st.success("Cache cleared!")


def render_fund_analysis_page():
    """Render the main mutual fund analysis page."""
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")

        # Fund category selection
        categories = get_fund_categories()
        category_names = ["All Funds"] + list(categories.keys())
        selected_category = st.selectbox(
            "Fund Category",
            options=category_names,
            help="Choose which mutual funds to analyze"
        )

        # Custom tickers input
        custom_tickers = ""
        if selected_category == "All Funds":
            st.info("Analyzing all popular mutual funds (~100)")
        elif selected_category != "Custom Tickers":
            st.info(f"Analyzing {len(categories.get(selected_category, []))} funds in {selected_category}")
        else:
            custom_tickers = st.text_area(
                "Enter tickers (comma-separated)",
                placeholder="VFIAX, FXAIX, VTSAX, VBTLX",
                height=100
            )

        # Analysis options
        st.subheader("Analysis Options")
        clear_cache_btn = st.button("🗑️ Clear Cache", on_click=clear_cache)

        # Cache info
        cache_dir = os.path.join(os.path.expanduser("~"), ".qwen_mutual_fund_analyzer", "cache")
        cache_file = os.path.join(cache_dir, "mutual_fund_cache.json")
        if os.path.exists(cache_file):
            st.info(f"✓ Cache available")
        else:
            st.warning("No cache")

        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        **10 Investment Strategies:**
        - Cost Efficiency (expense ratio, turnover)
        - Performance Score (historical returns)
        - Manager Quality (family, track record)
        - Risk-Adjusted Return (alpha, beta)
        - Diversification Score
        - Tax Efficiency
        - Fund Quality (Morningstar rating)
        - Growth Score
        - Income Score
        - ESG Score
        """)

    # Main content area
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Strategy Count", "10")
    with col2:
        st.metric("Fund Categories", len(categories))
    with col3:
        st.metric("Data Source", "Yahoo Finance")
    with col4:
        if st.session_state.analysis_complete:
            st.metric("Funds Analyzed", len(st.session_state.funds_data))
        else:
            st.metric("Funds Analyzed", "-")

    # Start analysis button
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("🚀 Start Analysis")
    with col2:
        start_btn = st.button("▶️ Run Analysis", type="primary", use_container_width=True)

    if start_btn:
        # Get tickers
        if selected_category == "All Funds":
            with st.spinner("Fetching mutual fund list..."):
                tickers = get_all_fund_tickers()
                st.success(f"Found {len(tickers)} popular mutual funds")
        elif selected_category == "Custom Tickers":
            tickers = [t.strip().upper() for t in custom_tickers.split(",") if t.strip()]
            if not tickers:
                st.error("Please enter at least one ticker")
                st.stop()
            st.success(f"Analyzing {len(tickers)} custom funds")
        else:
            tickers = categories.get(selected_category, [])
            st.success(f"Analyzing {len(tickers)} {selected_category} funds")

        # Fetch data
        st.markdown("### 📊 Fetching Mutual Fund Data...")
        with st.status("Fetching data from Yahoo Finance...", expanded=True) as status:
            fund_data = st.session_state.fetcher.fetch_multiple(tickers, batch_size=50)
            if fund_data:
                status.update(label=f"✅ Successfully fetched {len(fund_data)} Funds!", state="complete", expanded=False)
            else:
                status.update(label="❌ Failed to fetch any Mutual Fund data", state="error", expanded=True)

        if not fund_data:
            st.error(f"No data fetched for the {len(tickers)} tickers attempted. This usually happens if Yahoo Finance is rate-limiting the server or if the tickers are invalid.")
            st.info("💡 **Tip:** Try again in a few minutes, or try a smaller 'Custom Ticker' list (e.g., VFIAX, VTSAX) to see if it works.")
            st.stop()


        st.session_state.funds_data = funds_data

        # Analyze funds
        st.markdown("### 🧠 Running Strategy Analysis...")
        strategies_data = analyze_funds(funds_data)
        st.session_state.strategies_data = strategies_data
        st.session_state.analysis_complete = True

        st.success(f"✅ Analysis complete! {len(funds_data)} funds analyzed.")
        st.rerun()

    # Results section
    if st.session_state.analysis_complete and st.session_state.funds_data:
        render_analysis_results()


def render_analysis_results():
    """Render the analysis results section."""
    st.markdown("---")
    st.header("📊 Analysis Results")

    funds_data = st.session_state.funds_data
    strategies_data = st.session_state.strategies_data

    # Create results DataFrame
    results = []
    for fund, strategies in zip(funds_data, strategies_data):
        row = {"Ticker": fund.get("symbol", "")}
        row["Name"] = fund.get("name", "")[:40]
        row["Category"] = fund.get("category", "")
        row["Family"] = fund.get("family", "")
        row["Expense Ratio"] = fund.get("expense_ratio")
        row["NAV"] = fund.get("nav_price")

        # Add strategy scores
        for strategy_key, strategy_name in STRATEGY_NAMES.items():
            row[strategy_name] = strategies.get(strategy_key, {}).get("score", 0)

        row["Total"] = strategies.get("total_score", 0)
        row["Average"] = strategies.get("average_score", 0)
        results.append(row)

    df = pd.DataFrame(results)
    df = df.sort_values("Total", ascending=False)

    # Top performers
    st.subheader("🏆 Top 10 Funds")
    top_10 = df.head(10).copy()
    top_10["NAV"] = top_10["NAV"].apply(lambda x: f"${x:.2f}" if x else "N/A")
    top_10["Expense Ratio"] = top_10["Expense Ratio"].apply(
        lambda x: f"{x:.2%}" if x else "N/A"
    )
    st.dataframe(
        top_10[["Ticker", "Name", "Family", "Category", "NAV", "Expense Ratio", "Total", "Average"]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Ticker": st.column_config.TextColumn("Ticker", help="The fund's trading symbol."),
            "Name": st.column_config.TextColumn("Name", help="The full name of the Mutual Fund."),
            "Family": st.column_config.TextColumn("Family", help="The company that manages the mutual fund. Example: Vanguard, Fidelity."),
            "Category": st.column_config.TextColumn("Category", help="The specific market sector or asset class this fund focuses on."),
            "NAV": st.column_config.TextColumn("Net Asset Value", help="The per-share value of the fund. Similar to a stock's price."),
            "Expense Ratio": st.column_config.TextColumn("Expense Ratio", help="The annual fee charged by the fund. Lower numbers eat less of your profit over time."),
            "Total": st.column_config.NumberColumn("Total Score", help="The sum of all strategy scores. Higher means better historical and structural quality."),
            "Average": st.column_config.NumberColumn("Average Score", help="The average score across all tested analysis methodologies.")
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

    # Category breakdown
    st.subheader("🏭 Category Breakdown")
    if "Category" in df.columns:
        category_counts = df["Category"].value_counts().sort_values(ascending=False)
        category_df = pd.DataFrame({
            "Category": category_counts.index,
            "Count": category_counts.values,
            "Avg Score": [df[df["Category"] == c]["Total"].mean() for c in category_counts.index]
        })

        col1, col2 = st.columns(2)
        with col1:
            st.bar_chart(category_df.set_index("Category")["Count"])
        with col2:
            st.bar_chart(category_df.set_index("Category")["Avg Score"])

        st.dataframe(
            category_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Category": "Category",
                "Count": st.column_config.NumberColumn("Funds", format="%d"),
                "Avg Score": st.column_config.NumberColumn("Avg Total Score", format="%.2f")
            }
        )

    # Family breakdown
    st.subheader("🏢 Fund Family Breakdown")
    if "Family" in df.columns:
        family_counts = df["Family"].value_counts().head(10)
        family_df = pd.DataFrame({
            "Family": family_counts.index,
            "Count": family_counts.values,
            "Avg Score": [df[df["Family"] == f]["Total"].mean() for f in family_counts.index]
        })
        st.dataframe(
            family_df,
            use_container_width=True,
            hide_index=True,
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
            filepath = exporter.export_to_excel(funds_data, strategies_data)
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
            filepath = exporter.export_to_csv(funds_data, strategies_data)
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
        display_df["NAV"] = display_df["NAV"].apply(lambda x: f"${x:.2f}" if x else "N/A")
        display_df["Expense Ratio"] = display_df["Expense Ratio"].apply(
            lambda x: f"{x:.2%}" if x else "N/A"
        )
        st.dataframe(display_df, use_container_width=True, hide_index=True)

    # Individual fund analysis
    st.subheader("🔎 Individual Fund Analysis")
    selected_ticker = st.selectbox(
        "Select a fund to view detailed analysis",
        options=[f.get("symbol", "") for f in funds_data]
    )

    if selected_ticker:
        idx = next((i for i, f in enumerate(funds_data) if f.get("symbol") == selected_ticker), None)
        if idx is not None:
            fund = funds_data[idx]
            strategies = strategies_data[idx]

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"### {fund.get('symbol', '')}")
                st.markdown(f"**{fund.get('name', '')}**")
                st.markdown(f"Category: {fund.get('category', 'N/A')}")
                st.markdown(f"Family: {fund.get('family', 'N/A')}")
                expense = fund.get('expense_ratio')
                st.markdown(f"**Expense Ratio:** {expense:.2%}" if expense is not None else "**Expense Ratio:** N/A")
                st.markdown(f"**Holdings:** {fund.get('holdings_count', 'N/A')}")
                turnover = fund.get('turnover_rate')
                st.markdown(f"**Turnover:** {turnover:.0%}" if turnover is not None else "**Turnover:** N/A")
                if fund.get('morningstar_rating'):
                    stars = "⭐" * int(fund.get('morningstar_rating', 0))
                    st.markdown(f"**Morningstar:** {stars}")

            with col2:
                total_score = strategies.get("total_score", 0)
                st.metric("Total Score", f"{total_score}/100")
                st.metric("Average Score", f"{strategies.get('average_score', 0):.2f}/10")

            # --- AI Summary ---
            with st.spinner("🤖 Generating AI Insight..."):
                summary = generate_stock_summary(
                    fund.get("name", ""), 
                    fund.get("symbol", ""), 
                    "Mutual Fund", 
                    strategies
                )
                st.info(f"**AI Insight:** {summary}", icon="🤖")

            # --- Visualizations ---
            st.markdown("---")
            viz_col1, viz_col2 = st.columns(2)
            
            with viz_col1:
                st.markdown("#### Overall Rating")
                speedometer = create_speedometer(total_score, max_score=100, title="Investment Grade")
                st.plotly_chart(speedometer, use_container_width=True)
                
            with viz_col2:
                st.markdown("#### Fundamental Balance")
                # Group Mutual Fund specific strategies into 5 dimensions
                spider_categories = {
                    "Performance": ["momentum", "growth", "risk_adjusted"],
                    "Manager Skill": ["manager_tenure", "morningstar_rating"],
                    "Value & Cost": ["value", "cost_efficiency"],
                    "Structure": ["turnover_efficiency", "liquidity"],
                    "ESG": ["esg"]
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
    st.markdown('<p class="main-header">🔙 Mutual Fund Strategy Backtesting</p>', unsafe_allow_html=True)
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
            help="Maximum percentage of portfolio in single fund"
        )

        # Score threshold
        st.subheader("🎯 Quality Threshold")
        min_score = st.slider(
            "Minimum total score to buy",
            min_value=30,
            max_value=80,
            value=50,
            step=5,
            help="Funds must score at least this to be purchased"
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
            options=["SPY", "VOO", "VTI", "BND"],
            index=0
        )

        # Fund selection
        st.subheader("🏢 Fund Universe")
        categories = get_fund_categories()
        fund_universe = st.selectbox(
            "Funds to test",
            ["All Funds"] + list(categories.keys()) + ["Custom Tickers"],
        )

        custom_tickers = ""
        if fund_universe == "Custom Tickers":
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
        with st.spinner("Preparing fund list..."):
            if fund_universe == "All Funds":
                tickers = get_all_fund_tickers()[:50]  # Limit for speed
                st.info(f"Using top 50 popular funds")
            elif fund_universe == "Custom Tickers":
                tickers = [t.strip().upper() for t in custom_tickers.split(",") if t.strip()]
                if not tickers:
                    st.error("Please enter at least one ticker")
                    st.stop()
            else:
                tickers = categories.get(fund_universe, [])[:30]  # Limit for speed
                st.info(f"Using {len(tickers)} funds from {fund_universe}")

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
        st.line_chart(chart_data[["portfolio_value"]], use_container_width=True)

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
    st.markdown('<p class="main-header">📈 Mutual Fund Analyzer</p>', unsafe_allow_html=True)
    st.markdown("Comprehensive mutual fund analysis using **10 investment strategies** with backtesting capabilities")

    # Navigation
    page = st.sidebar.radio(
        "Navigation",
        ["Fund Analysis", "Backtesting"],
        index=0
    )

    if page == "Fund Analysis":
        render_fund_analysis_page()
    else:
        render_backtesting_page()


if __name__ == "__main__":
    main()
