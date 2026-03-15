"""
ETF Data Fetcher Module

Provides intelligent ETF data retrieval from Yahoo Finance with:
- 24-hour caching to minimize API calls
- Rate limiting (1 second between requests)
- Batch processing with progress tracking
- Automatic fallback to cached data

Classes:
    ETFDataFetcher: Main class for fetching ETF data with caching

Example:
    >>> fetcher = ETFDataFetcher()
    >>> etf = fetcher.fetch_data("SPY")
    >>> print(f"{etf['symbol']}: ${etf['price']}")
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



class ETFDataFetcher(BaseDataFetcher):
    """
    Fetches ETF data from Yahoo Finance with intelligent caching and rate limiting.

    Features:
        - 24-hour local caching reduces API calls
        - Automatic rate limiting (1 second between requests)
        - Batch processing with progress tracking
        - Graceful fallback to cached data on errors
    """

    def __init__(self):
        super().__init__("etf_cache.json")

    def fetch_data(self, ticker: str) -> Optional[dict]:
        """
        Fetch comprehensive ETF data for a single ticker.

        Args:
            ticker (str): ETF ticker symbol (e.g., 'SPY', 'QQQ')

        Returns:
            Optional[dict]: Dictionary containing ETF data
        """
        cached = self._get_cached_data(ticker)
        if cached:
            print(f"  [CACHE] {ticker}")
            return cached

        try:
            etf = self.get_ticker_obj(ticker)
            info = etf.info

            if not info or not info.get("symbol"):
                print(f"  [SKIP] {ticker} - No data available")
                return None

            data = {
                "symbol": info.get("symbol", ticker),
                "name": info.get("shortName") or info.get("longName") or "N/A",
                "category": info.get("category") or "N/A",
                "family": info.get("fundFamily") or "N/A",
                "exchange": info.get("exchange") or "N/A",
                "market_cap": safe_get_numeric(info, "marketCap"),
                "nav_price": safe_get_numeric(info, "navPrice"),
                "price": safe_get_numeric(info, "currentPrice") or safe_get_numeric(info, "regularMarketPrice"),
                "pe_ratio": safe_get_numeric(info, "trailingPE"),
                "pb_ratio": safe_get_numeric(info, "priceToBook"),
                "dividend_yield": safe_get_numeric(info, "dividendYield"),
                "expense_ratio": safe_get_numeric(info, "annualReportExpenseRatio"),
                "beta": safe_get_numeric(info, "beta"),
                "52_week_high": safe_get_numeric(info, "fiftyTwoWeekHigh"),
                "52_week_low": safe_get_numeric(info, "fiftyTwoWeekLow"),
                "50_day_avg": safe_get_numeric(info, "fiftyDayAverage"),
                "200_day_avg": safe_get_numeric(info, "twoHundredDayAverage"),
                "ytd_return": safe_get_numeric(info, "ytdReturn"),
                "three_year_return": safe_get_numeric(info, "threeYearAverageReturn"),
                "five_year_return": safe_get_numeric(info, "fiveYearAverageReturn"),
                "holdings_count": safe_get_numeric(info, "holdingsCount"),
                "bond_holdings": safe_get_numeric(info, "bondHoldings"),
                "stock_holdings": safe_get_numeric(info, "equityHoldings"),
                "top_10_holdings_pct": safe_get_numeric(info, "top10Holdings"),
                "volume": safe_get_numeric(info, "volume"),
                "avg_volume": safe_get_numeric(info, "averageVolume"),
                "fund_inception_date": info.get("fundInceptionDate"),
            }

            # Get historical data for momentum calculation
            try:
                hist = etf.history(period="1y")
                if hist is not None and len(hist) > 0:
                    close_prices = hist["Close"]
                    if len(close_prices) > 0:
                        data["year_ago_price"] = float(close_prices.iloc[0])
                    if len(close_prices) > 126:
                        data["6_month_ago_price"] = float(close_prices.iloc[len(close_prices)//2])
                    if len(close_prices) > 189:
                        data["3_month_ago_price"] = float(close_prices.iloc[len(close_prices)*3//4])
            except Exception as e:
                print(f"  [WARN] {ticker} - Could not fetch historical data: {e}")

            self._cache_data(ticker, data)
            print(f"  [FETCH] {ticker} - {data.get('name', 'N/A')}")
            return data

        except Exception as e:
            print(f"  [ERROR] {ticker} - {str(e)}")
            return None



def get_etf_categories() -> dict:
    """Get a dictionary of ETF categories with representative tickers."""
    return {
        "Broad Market": [
            "SPY", "VOO", "IVV",  # S&P 500
            "QQQ", "QQQM",  # Nasdaq 100
            "DIA",  # Dow Jones
            "IWM", "VTWO",  # Russell 2000
            "VTI", "ITOT",  # Total Market
            "VEA", "IEFA",  # Developed Markets
            "VWO", "IEMG",  # Emerging Markets
            "ACWI", "VT",  # All World
        ],
        "Sector": [
            "XLK", "VGT", "FTEC",  # Technology
            "XLF", "VFH", "FNCL",  # Financial
            "XLV", "VHT", "FHLC",  # Healthcare
            "XLE", "VDE", "FENY",  # Energy
            "XLI", "VIS", "FIDU",  # Industrial
            "XLP", "VDC", "FSTA",  # Consumer Defensive
            "XLY", "VCR", "FDIS",  # Consumer Cyclical
            "XLB", "VAW", "FMAT",  # Materials
            "XLU", "VPU", "FUTY",  # Utilities
            "XLRE", "VNQ", "FREL",  # Real Estate
        ],
        "Dividend": [
            "VYM", "SCHD", "HDV",  # High Dividend
            "VIG", "DGRO", "NOBL",  # Dividend Growth
            "SPHD", "SDIV", "JEPI",  # High Yield
            "DVY", "IDV", "VYMI",  # International Dividend
        ],
        "Growth": [
            "VUG", "SCHG", "IWF",  # Large Growth
            "VONG", "QQQM",  # Nasdaq Growth
            "IVW", "SPYG",  # S&P Growth
            "VIOG", "IJT",  # Small Cap Growth
        ],
        "Value": [
            "VOO", "SCHV", "IWD",  # Large Value
            "VBR", "VIOV", "IJR",  # Small Value
            "IVE", "SPYV",  # S&P Value
        ],
        "Fixed Income": [
            "BND", "AGG", "FBND",  # Total Bond
            "TLT", "IEF", "SHY",  # Treasury
            "LQD", "VCIT", "VCSH",  # Corporate
            "HYG", "JNK", "USHY",  # High Yield
            "TIP", "SCHP", "VTIP",  # TIPS
            "MUB", "VTEB", "TFI",  # Municipal
            "BNDX", "IGOV", "VWOB",  # International Bond
        ],
        "Thematic": [
            "ARKK", "ARKG", "ARKW",  # ARK Innovation
            "ICLN", "QCLN", "PBW",  # Clean Energy
            "BOTZ", "ROBO", "IRBO",  # Robotics/AI
            "SOXX", "SMH", "PSI",  # Semiconductors
            "IBB", "XBI", "ARKG",  # Biotech
            "FINX", "IPAY", "BLOK",  # Fintech/Crypto
            "ESGU", "ESGD", "ESGE",  # ESG
        ],
        "Commodities": [
            "GLD", "IAU", "GLDM",  # Gold
            "SLV", "PSLV", "SIVR",  # Silver
            "USO", "BNO", "UCO",  # Oil
            "UNG", "BOIL", "KOLD",  # Natural Gas
            "DBA", "CORN", "WEAT",  # Agriculture
            "DBC", "GSG", "PDBC",  # Broad Commodities
        ],
        "Currency": [
            "UUP",  # Dollar Bullish
            "FXE", "FXB", "FXY",  # Euro, Pound, Yen
            "FXF", "FXC", "FXA",  # Swiss Franc, CAD, AUD
        ],
        "Volatility": [
            "VIXY", "VIXM",  # VIX Short/Mid Term
            "UVXY", "SVXY",  # VIX Leveraged/Inverse
        ],
    }


def get_all_etf_tickers() -> list:
    """Get a comprehensive list of popular ETF tickers."""
    categories = get_etf_categories()
    all_tickers = []
    for tickers in categories.values():
        all_tickers.extend(tickers)
    return list(dict.fromkeys(all_tickers))  # Remove duplicates while preserving order


def get_sp500_etfs() -> list:
    """Get S&P 500 related ETFs."""
    return ["SPY", "VOO", "IVV", "SPLG", "SPYG", "SPYV", "RSP", "SPHQ"]


def get_nasdaq100_etfs() -> list:
    """Get Nasdaq 100 related ETFs."""
    return ["QQQ", "QQQM", "QLD", "QID", "PSQ", "UGA"]


if __name__ == "__main__":
    fetcher = ETFDataFetcher()
    tickers = ["SPY", "QQQ", "VTI"]
    results = fetcher.fetch_multiple(tickers)
    print(f"\nResults: {len(results)} ETFs")
    for r in results:
        print(f"  {r['symbol']}: ${r.get('price', 'N/A')} - {r.get('name', 'N/A')}")
