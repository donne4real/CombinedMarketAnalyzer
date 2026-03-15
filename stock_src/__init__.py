"""
Stock Market Analyzer Package

A comprehensive stock analysis application that evaluates NASDAQ and NYSE stocks
using 10 sophisticated investment models and exports results to Excel.

Modules:
    data_fetcher: Stock data retrieval with caching and rate limiting
    strategies: Implementation of 10 investment analysis models
    exporter: Excel and CSV export functionality
    backtester: Historical backtesting with performance metrics

Example:
    >>> from stock_src.data_fetcher import StockDataFetcher
    >>> from stock_src.strategies import InvestmentStrategies
    >>> from stock_src.exporter import SpreadsheetExporter
    >>> from stock_src.backtester import Backtester, BacktestConfig
    >>>
    >>> # Fetch stock data
    >>> fetcher = StockDataFetcher()
    >>> stock = fetcher.fetch_data("AAPL")
    >>>
    >>> # Analyze with all 10 models
    >>> analysis = InvestmentStrategies.analyze_stock(stock)
    >>>
    >>> # Export results
    >>> exporter = SpreadsheetExporter()
    >>> exporter.export_to_excel([stock], [analysis])
    >>>
    >>> # Run backtest
    >>> config = BacktestConfig(start_date="2022-01-01", end_date="2023-12-31")
    >>> backtester = Backtester(config)
    >>> results = backtester.run_backtest(["AAPL", "MSFT"])
"""

__version__ = "2.0.0"
__author__ = "Stock Market Analyzer"
__all__ = ["data_fetcher", "strategies", "exporter", "backtester"]
