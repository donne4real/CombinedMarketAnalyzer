"""
Stock Data Fetcher Module

Provides intelligent stock data retrieval from Yahoo Finance with:
- 24-hour caching to minimize API calls
- Rate limiting (1 second between requests)
- Batch processing with progress tracking
- Automatic fallback to cached data

Classes:
    StockDataFetcher: Main class for fetching stock data with caching

Example:
    >>> fetcher = StockDataFetcher()
    >>> stock = fetcher.fetch_data("AAPL")
    >>> print(f"{stock['symbol']}: ${stock['price']}")
"""

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import pandas as pd
import yfinance as yf
from shared_src.base_fetcher import BaseDataFetcher, safe_get_numeric



class StockDataFetcher(BaseDataFetcher):
    """
    Fetches stock data from Yahoo Finance with intelligent caching and rate limiting.

    Features:
        - 24-hour local caching reduces API calls
        - Automatic rate limiting (1 second between requests)
        - Batch processing with progress tracking
        - Graceful fallback to cached data on errors

    Attributes:
        cache (dict): In-memory cache of stock data
        CACHE_DIR (Path): Directory for cache storage
        CACHE_FILE (Path): JSON file for persistent cache
        CACHE_EXPIRY_HOURS (int): Cache validity period (default: 24)
        RATE_LIMIT_DELAY (float): Delay between API requests (default: 1.0s)

    Example:
        >>> fetcher = StockDataFetcher()
        >>> # First call - fetches from API
        >>> stock = fetcher.fetch_data("AAPL")
        >>> # Second call - uses cache (instant)
        >>> stock = fetcher.fetch_data("AAPL")
    """

    def __init__(self):
        super().__init__("stock_cache.json")

    def fetch_data(self, ticker: str) -> Optional[dict]:
        """
        Fetch comprehensive stock data for a single ticker.
        """
        # Check cache first
        cached = self._get_cached_data(ticker)
        if cached:
            return cached

        # Fetch from Yahoo Finance with retry and rotation
        max_retries = 2
        for attempt in range(max_retries):
            try:
                stock = self.get_ticker_obj(ticker)
                info = stock.info

                # If info is empty, try rotating and retrying
                if not info or not info.get("symbol"):
                    if attempt < max_retries - 1:
                        print(f"  [RETRY] {ticker} - Attempt {attempt+1} failed, rotating UA...")
                        self._rotate_user_agent()
                        time.sleep(2)
                        continue
                    else:
                        print(f"  [SKIP] {ticker} - No data available after retries")
                        return None

                # Safely extract numeric values with validation
                data = {
                    "symbol": info.get("symbol", ticker),
                    "name": info.get("shortName") or info.get("longName") or "N/A",
                    "sector": info.get("sector") or "N/A",
                    "industry": info.get("industry") or "N/A",
                    "exchange": info.get("exchange") or "N/A",
                    "market_cap": safe_get_numeric(info, "marketCap"),
                    "price": safe_get_numeric(info, "currentPrice") or safe_get_numeric(info, "regularMarketPrice"),
                    "pe_ratio": safe_get_numeric(info, "trailingPE"),
                    "forward_pe": safe_get_numeric(info, "forwardPE"),
                    "pb_ratio": safe_get_numeric(info, "priceToBook"),
                    "ps_ratio": safe_get_numeric(info, "priceToSalesTrailing12Months"),
                    "peg_ratio": safe_get_numeric(info, "pegRatio"),
                    "dividend_yield": safe_get_numeric(info, "dividendYield"),
                    "eps": safe_get_numeric(info, "trailingEps"),
                    "beta": safe_get_numeric(info, "beta"),
                    "52_week_high": safe_get_numeric(info, "fiftyTwoWeekHigh"),
                    "52_week_low": safe_get_numeric(info, "fiftyTwoWeekLow"),
                    "50_day_avg": safe_get_numeric(info, "fiftyDayAverage"),
                    "200_day_avg": safe_get_numeric(info, "twoHundredDayAverage"),
                    "revenue_growth": safe_get_numeric(info, "revenueGrowth"),
                    "earnings_growth": safe_get_numeric(info, "earningsGrowth"),
                    "roe": safe_get_numeric(info, "returnOnEquity"),
                    "roa": safe_get_numeric(info, "returnOnAssets"),
                    "debt_to_equity": safe_get_numeric(info, "debtToEquity"),
                    "current_ratio": safe_get_numeric(info, "currentRatio"),
                    "free_cash_flow": safe_get_numeric(info, "freeCashflow"),
                    "operating_cash_flow": safe_get_numeric(info, "operatingCashflow"),
                    "profit_margin": safe_get_numeric(info, "profitMargins"),
                    "payout_ratio": safe_get_numeric(info, "payoutRatio"),
                    "volume": safe_get_numeric(info, "volume"),
                    "avg_volume": safe_get_numeric(info, "averageVolume"),
                }

                # Get historical data for momentum calculation
                try:
                    hist = stock.history(period="1y")
                    if hist is not None and len(hist) > 0:
                        close_prices = hist["Close"]
                        if len(close_prices) > 0:
                            data["year_ago_price"] = float(close_prices.iloc[0])
                        if len(close_prices) > 126:  # ~6 months
                            data["6_month_ago_price"] = float(close_prices.iloc[len(close_prices)//2])
                        if len(close_prices) > 189:  # ~3 months from end
                            data["3_month_ago_price"] = float(close_prices.iloc[len(close_prices)*3//4])
                except Exception as e:
                    print(f"  [WARN] {ticker} - Could not fetch historical data: {e}")

                self._cache_data(ticker, data)
                print(f"  [FETCH] {ticker} - {data.get('name', 'N/A')}")
                return data

            except Exception as e:
                if attempt < max_retries - 1:
                    self._rotate_user_agent()
                    time.sleep(2)
                    continue
                print(f"  [ERROR] {ticker} - {str(e)}")
                return None
        return None



def get_nasdaq_nyse_tickers() -> list:
    """
    Get a curated list of popular NASDAQ and NYSE tickers.

    Returns a representative sample of ~200 liquid stocks across all sectors
    to stay within Yahoo Finance rate limits while providing broad market coverage.

    Returns:
        list: List of ~200 ticker symbols including:
            - Technology (AAPL, MSFT, GOOGL, NVDA, etc.)
            - Finance (JPM, BAC, WFC, GS, etc.)
            - Healthcare (JNJ, UNH, PFE, MRK, etc.)
            - Consumer (WMT, PG, KO, PEP, etc.)
            - Industrial (CAT, BA, HON, UPS, etc.)
            - Energy (XOM, CVX, COP, etc.)
            - Real Estate, Utilities, Materials, Communication
            - Major ETFs (SPY, QQQ, DIA, etc.)

    Note:
        This is a curated list to avoid rate limiting. For complete market
        coverage, consider using get_sp500_tickers() or a premium API.
    """
    # S&P 500 + Nasdaq 100 + Popular stocks (curated list to stay within rate limits)
    # This is a representative sample that covers major companies
    popular_tickers = [
        # Technology
        "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "META", "NVDA", "TSLA", "AMD", "INTC",
        "CRM", "ORCL", "ADBE", "NFLX", "CSCO", "AVGO", "QCOM", "TXN", "IBM", "NOW",
        "INTU", "AMAT", "MU", "LRCX", "KLAC", "SNPS", "CDNS", "MCHP", "ADI", "NXPI",
        
        # Finance
        "JPM", "BAC", "WFC", "GS", "MS", "C", "BLK", "SCHW", "AXP", "USB",
        "PNC", "TFC", "COF", "BK", "STT", "NTRS", "RF", "KEY", "FITB", "HBAN",
        
        # Healthcare
        "JNJ", "UNH", "PFE", "MRK", "ABBV", "TMO", "ABT", "DHR", "BMY", "LLY",
        "AMGN", "GILD", "ISRG", "VRTX", "REGN", "ZTS", "SYK", "BDX", "MDT", "CI",
        
        # Consumer
        "WMT", "PG", "KO", "PEP", "COST", "MDLZ", "CL", "KMB", "GIS", "K",
        "HSY", "SJM", "CAG", "CPB", "HRL", "MKC", "CHD", "CLX", "EL", "TAP",
        
        # Industrial
        "CAT", "BA", "HON", "UPS", "RTX", "LMT", "GE", "MMM", "DE", "UNP",
        "CSX", "NSC", "FDX", "LUV", "DAL", "UAL", "AAL", "JBLU", "ALK", "SAVE",
        
        # Energy
        "XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO", "OXY", "HAL",
        "BKR", "DVN", "FANG", "APA", "HES", "KMI", "WMB", "OKE", "TRGP", "LNG",
        
        # Real Estate
        "AMT", "PLD", "CCI", "EQIX", "SPG", "PSA", "WELL", "DLR", "O", "SBAC",
        "EXR", "AVB", "EQR", "VTR", "ESS", "MAA", "UDR", "CPT", "FRT", "REG",
        
        # Utilities
        "NEE", "DUK", "SO", "D", "AEP", "EXC", "SRE", "XEL", "WEC", "ED",
        "ETR", "ES", "FE", "EIX", "PPL", "CMS", "DTE", "NI", "LNT", "EVRG",
        
        # Materials
        "LIN", "APD", "SHW", "ECL", "FCX", "NEM", "DOW", "DD", "PPG", "NUE",
        "STLD", "VMC", "MLM", "PKG", "IP", "BALL", "AVY", "CF", "MOS", "FMC",
        
        # Communication
        "T", "VZ", "TMUS", "CMCSA", "DIS", "CHTR", "EA", "ATVI", "TTWO", "OMC",
        "IPG", "NWSA", "NWS", "FOXA", "FOX", "PARA", "WBD", "LUMN", "FYBR", "LBRDK",
        
        # Consumer Discretionary
        "AMZN", "TSLA", "HD", "MCD", "NKE", "SBUX", "LOW", "TJX", "BKNG", "CMG",
        "ORLY", "AZO", "ULTA", "RH", "LULU", "DECK", "GPS", "ANF", "AEO", "URBN",
        
        # ETFs for market comparison
        "SPY", "QQQ", "DIA", "IWM", "VTI", "VOO", "VEA", "VWO", "BND", "AGG",
    ]
    
    return popular_tickers


def get_sp500_tickers() -> list:
    """
    Get current S&P 500 tickers from Wikipedia.

    Fetches the live list of S&P 500 components from Wikipedia.
    Falls back to curated list if Wikipedia is unavailable.

    Returns:
        list: List of ~500 S&P 500 ticker symbols

    Note:
        Requires internet connection. Falls back to get_nasdaq_nyse_tickers()
        if Wikipedia cannot be reached.

    Example:
        >>> tickers = get_sp500_tickers()
        >>> print(f"S&P 500 has {len(tickers)} components")
    """
    try:
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        tables = pd.read_html(url)
        df = tables[0]
        tickers = df["Symbol"].replace(".", "-").tolist()
        return tickers
    except Exception as e:
        print(f"Warning: Could not fetch S&P 500 list: {e}")
        # Fallback to curated list
        return get_nasdaq_nyse_tickers()


if __name__ == "__main__":
    # Test the fetcher
    fetcher = StockDataFetcher()
    tickers = ["AAPL", "MSFT", "GOOGL"]
    results = fetcher.fetch_multiple(tickers)
    print(f"\nResults: {len(results)} stocks")
    for r in results:
        print(f"  {r['symbol']}: ${r.get('price', 'N/A')} - {r.get('name', 'N/A')}")
