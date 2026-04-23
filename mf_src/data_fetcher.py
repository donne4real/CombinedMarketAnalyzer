"""
Mutual Fund Data Fetcher Module

Provides intelligent mutual fund data retrieval from Yahoo Finance with:
- 24-hour caching to minimize API calls
- Rate limiting (1 second between requests)
- Batch processing with progress tracking
- Automatic fallback to cached data

Classes:
    MutualFundDataFetcher: Main class for fetching mutual fund data with caching

Example:
    >>> fetcher = MutualFundDataFetcher()
    >>> fund = fetcher.fetch_data("VFIAX")
    >>> print(f"{fund['symbol']}: ${fund['price']}")
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



class MutualFundDataFetcher(BaseDataFetcher):
    """
    Fetches mutual fund data from Yahoo Finance with intelligent caching and rate limiting.

    Features:
        - 24-hour local caching reduces API calls
        - Automatic rate limiting (1 second between requests)
        - Batch processing with progress tracking
        - Graceful fallback to cached data on errors
    """

    def __init__(self):
        super().__init__("mf_cache.json")

    def fetch_data(self, ticker: str) -> Optional[dict]:
        """
        Fetch comprehensive mutual fund data for a single ticker.
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
                    "category": info.get("category") or "N/A",
                    "family": info.get("fundFamily") or "N/A",
                    "exchange": info.get("exchange") or "N/A",
                    "nav_price": safe_get_numeric(info, "navPrice"),
                    "price": safe_get_numeric(info, "previousClose") or safe_get_numeric(info, "regularMarketPrice"),
                    "pe_ratio": safe_get_numeric(info, "trailingPE"),
                    "pb_ratio": safe_get_numeric(info, "priceToBook"),
                    "dividend_yield": safe_get_numeric(info, "dividendYield"),
                    "expense_ratio": safe_get_numeric(info, "annualReportExpenseRatio"),
                    "yield": safe_get_numeric(info, "yield"),
                    "ytd_return": safe_get_numeric(info, "ytdReturn"),
                    "three_year_return": safe_get_numeric(info, "threeYearAverageReturn"),
                    "five_year_return": safe_get_numeric(info, "fiveYearAverageReturn"),
                    "ten_year_return": safe_get_numeric(info, "tenYearAverageReturn"),
                    "holdings_count": safe_get_numeric(info, "holdingsCount"),
                    "bond_holdings": safe_get_numeric(info, "bondHoldings"),
                    "stock_holdings": safe_get_numeric(info, "equityHoldings"),
                    "cash_holdings": safe_get_numeric(info, "cashHoldings"),
                    "other_holdings": safe_get_numeric(info, "otherHoldings"),
                    "top_10_holdings_pct": safe_get_numeric(info, "top10Holdings"),
                    "turnover_rate": safe_get_numeric(info, "fundTurnover"),
                    "net_assets": safe_get_numeric(info, "netAssets"),
                    "inception_date": info.get("fundInceptionDate"),
                    "min_initial_investment": safe_get_numeric(info, "minimumInvestment"),
                    "min_subsequent_investment": safe_get_numeric(info, "subsequentInvestment"),
                    "beta": safe_get_numeric(info, "beta"),
                    "alpha": safe_get_numeric(info, "alpha"),
                    "mean_annual_return": safe_get_numeric(info, "meanAnnualReturn"),
                    "risk_rating": info.get("riskRating"),
                    "morningstar_rating": safe_get_numeric(info, "morningStarRating"),
                    "morningstar_risk": info.get("morningStarRiskRating"),
                    "sustainability_rating": safe_get_numeric(info, "sustainabilityRating"),
                }

                # Get historical data for momentum calculation
                try:
                    hist = stock.history(period="1y")
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
                if attempt < max_retries - 1:
                    self._rotate_user_agent()
                    time.sleep(2)
                    continue
                print(f"  [ERROR] {ticker} - {str(e)}")
                return None
        return None



def get_fund_categories() -> dict:
    """Get a dictionary of mutual fund categories with representative tickers."""
    return {
        "Index Funds": [
            "VFIAX", "FXAIX", "SWPPX",  # S&P 500
            "VTSAX", "FSKAX", "SWTSX",  # Total Market
            "VTIAX", "FTIHX", "SWISX",  # International
            "VWIAX", "VBIAX",  # Balanced
            "VBTLX", "FXNAX", "SWAGX",  # Total Bond
        ],
        "Large Cap Blend": [
            "VFIAX", "FXAIX", "SWPPX", "VFINX",
            "FSKAX", "SWTSX", "VTSAX",
            "DODGX", "VQNPX", "TRBCX",
        ],
        "Large Cap Growth": [
            "VIGAX", "TRSGX", "FMAGX", "FBGRX",
            "AGTHX", "PRGFX", "VWUSX", "TRBCX",
            "FCNTX", "XLCGX",
        ],
        "Large Cap Value": [
            "VVIAX", "VWELX", "DODBX", "FSMAX",
            "VHDYX", "TRBCX", "PRIDX", "FDVLX",
        ],
        "Mid Cap": [
            "VIMAX", "FSMDX", "SWMCX", "VIMSX",
            "TRMCX", "PRMTX", "JDMAX",
        ],
        "Small Cap": [
            "VSMAX", "FSSNX", "SWSSX", "NAESX",
            "TRSSX", "JAFVX", "PRDSX",
        ],
        "International": [
            "VTIAX", "FTIHX", "SWISX", "VGTSX",
            "FSPSX", "HAINX", "DODFX", "PRIDX",
            "VFWAX", "VTMGX",
        ],
        "Emerging Markets": [
            "VEMAX", "FEMKX", "MSOAX", "VEIEX",
            "DODMX", "PRMSX", "SEEMX",
        ],
        "Bond Funds": [
            "VBTLX", "FXNAX", "SWAGX", "VBMFX",
            "FTBFX", "PIMIX", "DODIX", "VWITX",
            "VFSTX", "FSHBX",
        ],
        "Target Date": [
            "VFIFX", "FFNOX", "TRRFX", "VTTVX",
            "VTHRX", "VTTSX", "FFTLX", "TRRCX",
        ],
        "Sector Funds": [
            "VGSLX", "FSRNX",  # Real Estate
            "VGHAX", "FBIOX",  # Healthcare
            "FSENX", "VGENX",  # Energy
            "FSPTX", "VITAX",  # Technology
            "FSUTX", "VUIAX",  # Utilities
        ],
        "Balanced/Allocation": [
            "VWELX", "VBIAX", "SWOBX", "VWINX",
            "DODBX", "FBALX", "TRPBX", "VSCGX",
        ],
        "Dividend/Income": [
            "VHDYX", "FDVV", "SCHD", "VYM",
            "Fidelity Dividend Growth", "VDIGX",
        ],
        "ESG/Sustainable": [
            "VFTAX", "ESGV", "SUSL", "DSI",
            "VSGAX", "ESGU", "SUSA",
        ],
    }


def get_all_fund_tickers() -> list:
    """Get a comprehensive list of popular mutual fund tickers."""
    categories = get_fund_categories()
    all_tickers = []
    for tickers in categories.values():
        all_tickers.extend(tickers)
    return list(dict.fromkeys(all_tickers))  # Remove duplicates while preserving order


def get_vanguard_funds() -> list:
    """Get Vanguard mutual fund tickers."""
    return [
        "VFIAX", "VTSAX", "VTIAX", "VBTLX", "VWELX", "VWIAX",
        "VIGAX", "VVIAX", "VIMAX", "VSMAX", "VEMAX", "VHDYX",
        "VFTAX", "VSGAX", "VFIFX", "VTHRX", "VTTVX", "VTTSX",
        "VGSLX", "VGHAX", "VGENX", "VITAX", "VUIAX", "VBMFX",
        "VWINX", "VSCGX", "VDIGX", "VWITX", "VFSTX",
    ]


def get_fidelity_funds() -> list:
    """Get Fidelity mutual fund tickers."""
    return [
        "FXAIX", "FSKAX", "FTIHX", "FXNAX", "FBALX",
        "FMAGX", "FBGRX", "FSENX", "FSPTX", "FSUTX",
        "FSRNX", "FBIOX", "FSSNX", "FEMKX", "FTBFX",
        "FFNOX", "FFTLX", "FDVV", "FSMDX", "FSHBX",
    ]


def get_schwab_funds() -> list:
    """Get Schwab mutual fund tickers."""
    return [
        "SWPPX", "SWTSX", "SWISX", "SWAGX", "SWOBX",
        "SWMCX", "SWSSX", "SWOAX", "SWRAX",
    ]


if __name__ == "__main__":
    fetcher = MutualFundDataFetcher()
    tickers = ["VFIAX", "FXAIX", "VTSAX"]
    results = fetcher.fetch_multiple(tickers)
    print(f"\nResults: {len(results)} mutual funds")
    for r in results:
        print(f"  {r['symbol']}: ${r.get('nav_price', 'N/A')} - {r.get('name', 'N/A')}")
