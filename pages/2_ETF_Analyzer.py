"""
ETF Analyzer Application
Streamlit Web Interface

Features:
- ETF Analysis: Analyze ETFs using 10 investment strategies
- Backtesting: Test strategies on historical data
"""

import os
import sys
from datetime import datetime, timedelta

# Ensure the root project directory is in the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import streamlit as st

from shared_src.base_fetcher import RATE_LIMIT_DELAY
from shared_src.visuals import create_speedometer, create_radar_chart
from shared_src.ai_summary import generate_stock_summary
from etf_src.data_fetcher import ETFDataFetcher, get_etf_categories, get_all_etf_tickers
from etf_src.strategies import ETFStrategies, STRATEGY_NAMES
from etf_src.exporter import SpreadsheetExporter
from etf_src.backtester import Backtester, BacktestConfig


# Page configuration
st.set_page_config(
    page_title="ETF Analyzer",
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
    if "etfs_data" not in st.session_state:
        st.session_state.etfs_data = []
    if "strategies_data" not in st.session_state:
        st.session_state.strategies_data = []
    if "analysis_complete" not in st.session_state:
        st.session_state.analysis_complete = False
    if "fetcher" not in st.session_state:
        st.session_state.fetcher = ETFDataFetcher()
    if "backtest_results" not in st.session_state:
        st.session_state.backtest_results = None
    if "backtest_complete" not in st.session_state:
        st.session_state.backtest_complete = False


def analyze_etfs(etfs_data):
    """Run all 10 strategies on the fetched ETFs."""
    strategies_data = []
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, etf in enumerate(etfs_data):
        analysis = ETFStrategies.analyze_etf(etf)
        strategies_data.append(analysis)
        progress_bar.progress((i + 1) / len(etfs_data))
        status_text.text(f"Analyzing: {etf.get('symbol', 'N/A')} ({i + 1}/{len(etfs_data)})")

    status_text.text("Analysis complete!")
    return strategies_data


def clear_cache():
    """Clear the data cache."""
    st.session_state.fetcher.clear_cache()
    st.session_state.etfs_data = []
    st.session_state.strategies_data = []
    st.session_state.analysis_complete = False
    st.success("Cache cleared!")


def render_etf_analysis_page():
    """Render the main ETF analysis page."""
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")

        # ETF category selection
        categories = get_etf_categories()
        category_names = ["All ETFs"] + list(categories.keys())
        selected_category = st.selectbox(
            "ETF Category",
            options=category_names,
            help="Choose which ETFs to analyze"
        )

        # Custom tickers input
        custom_tickers = ""
        if selected_category == "All ETFs":
            st.info("Analyzing all popular ETFs (~100)")
        elif selected_category != "Custom Tickers":
            st.info(f"Analyzing {len(categories.get(selected_category, []))} ETFs in {selected_category}")
        else:
            custom_tickers = st.text_area(
                "Enter tickers (comma-separated)",
                placeholder="SPY, QQQ, VTI, VOO",
                height=100
            )

        # Analysis options
        st.subheader("Analysis Options")
        clear_cache_btn = st.button("🗑️ Clear Cache", on_click=clear_cache)

        # Cache info
        cache_dir = os.path.join(os.path.expanduser("~"), ".qwen_etf_analyzer", "cache")
        cache_file = os.path.join(cache_dir, "etf_cache.json")
        if os.path.exists(cache_file):
            st.info(f"✓ Cache available")
        else:
            st.warning("No cache")

        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        **10 Investment Strategies:**
        - Value Score (low cost, P/E, P/B)
        - Momentum Strategy
        - Quality Score
        - Growth Score
        - Dividend Score
        - Risk-Adjusted Return
        - Diversification Score
        - Cost Efficiency
        - Liquidity Score
        - ESG Score
        """)

    # Main content area
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Strategy Count", "10")
    with col2:
        st.metric("ETF Categories", len(categories))
    with col3:
        st.metric("Data Source", "Yahoo Finance")
    with col4:
        if st.session_state.analysis_complete:
            st.metric("ETFs Analyzed", len(st.session_state.etfs_data))
        else:
            st.metric("ETFs Analyzed", "-")

    # Start analysis button
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("🚀 Start Analysis")
    with col2:
        start_btn = st.button("▶️ Run Analysis", type="primary", use_container_width=True)

    if start_btn:
        # Get tickers
        if selected_category == "All ETFs":
            with st.spinner("Fetching ETF list..."):
                tickers = get_all_etf_tickers()
                st.success(f"Found {len(tickers)} popular ETFs")
        elif selected_category == "Custom Tickers":
            tickers = [t.strip().upper() for t in custom_tickers.split(",") if t.strip()]
            if not tickers:
                st.error("Please enter at least one ticker")
                st.stop()
            st.success(f"Analyzing {len(tickers)} custom ETFs")
        else:
            tickers = categories.get(selected_category, [])
            st.success(f"Analyzing {len(tickers)} {selected_category} ETFs")

        # Fetch data
        st.markdown("### 📊 Fetching ETF Data...")
        etfs_data = st.session_state.fetcher.fetch_multiple(tickers, batch_size=50)

        if not etfs_data:
            st.error("No data fetched. Please try again or check your internet connection.")
            st.stop()

        st.session_state.etfs_data = etfs_data

        # Analyze ETFs
        st.markdown("### 🧠 Running Strategy Analysis...")
        strategies_data = analyze_etfs(etfs_data)
        st.session_state.strategies_data = strategies_data
        st.session_state.analysis_complete = True

        st.success(f"✅ Analysis complete! {len(etfs_data)} ETFs analyzed.")
        st.rerun()

    # Results section
    if st.session_state.analysis_complete and st.session_state.etfs_data:
        render_analysis_results()


def render_analysis_results():
    """Render the analysis results section."""
    st.markdown("---")
    st.header("📊 Analysis Results")

    etfs_data = st.session_state.etfs_data
    strategies_data = st.session_state.strategies_data

    # Create results DataFrame
    results = []
    for etf, strategies in zip(etfs_data, strategies_data):
        row = {"Ticker": etf.get("symbol", "")}
        row["Name"] = etf.get("name", "")[:40]
        row["Category"] = etf.get("category", "")
        row["Price"] = etf.get("price")
        row["Expense Ratio"] = etf.get("expense_ratio")

        # Add strategy scores
        for strategy_key, strategy_name in STRATEGY_NAMES.items():
            row[strategy_name] = strategies.get(strategy_key, {}).get("score", 0)

        row["Total"] = strategies.get("total_score", 0)
        row["Average"] = strategies.get("average_score", 0)
        results.append(row)

    df = pd.DataFrame(results)
    df = df.sort_values("Total", ascending=False)

    # Top performers
    st.subheader("🏆 Top 10 ETFs")
    top_10 = df.head(10).copy()
    top_10["Price"] = top_10["Price"].apply(lambda x: f"${x:.2f}" if x else "N/A")
    top_10["Expense Ratio"] = top_10["Expense Ratio"].apply(
        lambda x: f"{x:.2%}" if x else "N/A"
    )
    st.dataframe(
        top_10[["Ticker", "Name", "Category", "Price", "Expense Ratio", "Total", "Average"]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Ticker": st.column_config.TextColumn("Ticker", help="The fund's trading symbol."),
            "Name": st.column_config.TextColumn("Name", help="The full name of the Exchange Traded Fund."),
            "Category": st.column_config.TextColumn("Category", help="The specific market sector or asset class this ETF tracks."),
            "Price": st.column_config.TextColumn("Price", help="The current trading price per share."),
            "Expense Ratio": st.column_config.TextColumn("Expense Ratio", help="The annual fee charged by the fund. Lower is better. 0.10% means you pay $10 per $10,000 invested."),
            "Total": st.column_config.NumberColumn("Total Score", help="The sum of all strategy scores. Higher means better historical and structural quality."),
            "Average": st.column_config.NumberColumn("Average Score", help="The average score across all tested methodologies.")
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
                "Count": st.column_config.NumberColumn("ETFs", format="%d"),
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
            filepath = exporter.export_to_excel(etfs_data, strategies_data)
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
            filepath = exporter.export_to_csv(etfs_data, strategies_data)
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
        display_df["Expense Ratio"] = display_df["Expense Ratio"].apply(
            lambda x: f"{x:.2%}" if x else "N/A"
        )
        st.dataframe(display_df, use_container_width=True, hide_index=True)

    # Individual ETF analysis
    st.subheader("🔎 Individual ETF Analysis")
    selected_ticker = st.selectbox(
        "Select an ETF to view detailed analysis",
        options=[e.get("symbol", "") for e in etfs_data]
    )

    if selected_ticker:
        idx = next((i for i, e in enumerate(etfs_data) if e.get("symbol") == selected_ticker), None)
        if idx is not None:
            etf = etfs_data[idx]
            strategies = strategies_data[idx]

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"### {etf.get('symbol', '')}")
                st.markdown(f"**{etf.get('name', '')}**")
                st.markdown(f"Category: {etf.get('category', 'N/A')}")
                st.markdown(f"Family: {etf.get('family', 'N/A')}")
                expense = etf.get('expense_ratio')
                st.markdown(f"**Expense Ratio:** {expense:.2%}" if expense is not None else "**Expense Ratio:** N/A")
                st.markdown(f"**Holdings:** {etf.get('holdings_count', 'N/A')}")

            with col2:
                total_score = strategies.get("total_score", 0)
                st.metric("Total Score", f"{total_score}/100")
                st.metric("Average Score", f"{strategies.get('average_score', 0):.2f}/10")

            # --- AI Summary ---
            with st.spinner("🤖 Generating AI Insight..."):
                summary = generate_stock_summary(
                    etf.get("name", ""), 
                    etf.get("symbol", ""), 
                    "ETF", 
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
                # Group ETF specific strategies into 5 dimensions
                spider_categories = {
                    "Performance": ["momentum", "growth", "risk_adjusted"],
                    "Quality & Fundamentals": ["quality", "dividend"],
                    "Value & Cost": ["value", "cost_efficiency"],
                    "Structure": ["diversification", "liquidity"],
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
    st.markdown('<p class="main-header">🔙 ETF Strategy Backtesting</p>', unsafe_allow_html=True)
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
            help="Maximum percentage of portfolio in single ETF"
        )

        # Score threshold
        st.subheader("🎯 Quality Threshold")
        min_score = st.slider(
            "Minimum total score to buy",
            min_value=30,
            max_value=80,
            value=50,
            step=5,
            help="ETFs must score at least this to be purchased"
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

        # ETF selection
        st.subheader("🏢 ETF Universe")
        categories = get_etf_categories()
        etf_universe = st.selectbox(
            "ETFs to test",
            ["All ETFs"] + list(categories.keys()) + ["Custom Tickers"],
        )

        custom_tickers = ""
        if etf_universe == "Custom Tickers":
            custom_tickers = st.text_area(
                "Enter tickers (comma-separated)",
                placeholder="SPY, QQQ, VTI, VOO, IWM",
                height=100
            )

        # Run button
        st.markdown("---")
        run_backtest = st.button("▶️ Run Backtest", type="primary", use_container_width=True)

    # Main display area
    if run_backtest:
        # Get tickers
        with st.spinner("Preparing ETF list..."):
            if etf_universe == "All ETFs":
                tickers = get_all_etf_tickers()[:50]  # Limit for speed
                st.info(f"Using top 50 popular ETFs")
            elif etf_universe == "Custom Tickers":
                tickers = [t.strip().upper() for t in custom_tickers.split(",") if t.strip()]
                if not tickers:
                    st.error("Please enter at least one ticker")
                    st.stop()
            else:
                tickers = categories.get(etf_universe, [])[:30]  # Limit for speed
                st.info(f"Using {len(tickers)} ETFs from {etf_universe}")

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
    st.markdown('<p class="main-header">📈 ETF Analyzer</p>', unsafe_allow_html=True)
    st.markdown("Comprehensive ETF analysis using **10 investment strategies** with backtesting capabilities")

    # Navigation
    page = st.sidebar.radio(
        "Navigation",
        ["ETF Analysis", "Backtesting"],
        index=0
    )

    if page == "ETF Analysis":
        render_etf_analysis_page()
    else:
        render_backtesting_page()


if __name__ == "__main__":
    main()
