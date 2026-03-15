"""
Stock Data Fetcher for 100-Bagger Screener

Provides comprehensive stock data retrieval from Yahoo Finance with:
- 24-hour caching to minimize API calls
- Rate limiting (1 second between requests)
- Batch processing with progress tracking
- Peter Lynch's 100-bagger criteria focus

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
        - Focus on 100-bagger criteria (growth, value, insider ownership)
    """

    def __init__(self):
        super().__init__("bagger_cache.json")

    def fetch_data(self, ticker: str) -> Optional[dict]:
        """
        Fetch comprehensive stock data for 100-bagger analysis.

        Args:
            ticker (str): Stock ticker symbol (e.g., 'AAPL', 'MSFT')

        Returns:
            Optional[dict]: Dictionary containing stock data with focus on:
                - Growth metrics (revenue, earnings growth)
                - Value metrics (P/E, PEG, P/B)
                - Financial health (debt, margins, ROE)
                - Insider ownership and buybacks
        """
        cached = self._get_cached_data(ticker)
        if cached:
            print(f"  [CACHE] {ticker}")
            return cached

        try:
            stock = self.get_ticker_obj(ticker)
            info = stock.info

            if not info or not info.get("symbol"):
                print(f"  [SKIP] {ticker} - No data available")
                return None

            # Get financials for deeper analysis
            try:
                income_stmt = stock.financials
                balance_sheet = stock.balance_sheet
                cash_flow = stock.cashflow
            except:
                income_stmt = None
                balance_sheet = None
                cash_flow = None

            data = {
                # Basic Info
                "symbol": info.get("symbol", ticker),
                "name": info.get("shortName") or info.get("longName") or "N/A",
                "sector": info.get("sector") or "N/A",
                "industry": info.get("industry") or "N/A",
                "exchange": info.get("exchange") or "N/A",
                "market_cap": safe_get_numeric(info, "marketCap"),
                
                # Price Data
                "price": safe_get_numeric(info, "currentPrice") or safe_get_numeric(info, "regularMarketPrice"),
                "52_week_high": safe_get_numeric(info, "fiftyTwoWeekHigh"),
                "52_week_low": safe_get_numeric(info, "fiftyTwoWeekLow"),
                "50_day_avg": safe_get_numeric(info, "fiftyDayAverage"),
                "200_day_avg": safe_get_numeric(info, "twoHundredDayAverage"),
                
                # Valuation Metrics (Peter Lynch Focus)
                "pe_ratio": safe_get_numeric(info, "trailingPE"),
                "forward_pe": safe_get_numeric(info, "forwardPE"),
                "peg_ratio": safe_get_numeric(info, "pegRatio"),
                "pb_ratio": safe_get_numeric(info, "priceToBook"),
                "ps_ratio": safe_get_numeric(info, "priceToSalesTrailing12Months"),
                
                # Growth Metrics (Critical for 100-baggers)
                "revenue_growth": safe_get_numeric(info, "revenueGrowth"),
                "earnings_growth": safe_get_numeric(info, "earningsGrowth"),
                "revenue_per_share_growth": safe_get_numeric(info, "revenuePerShareGrowth"),
                
                # Profitability Metrics
                "profit_margin": safe_get_numeric(info, "profitMargins"),
                "gross_margin": safe_get_numeric(info, "grossMargins"),
                "operating_margin": safe_get_numeric(info, "operatingMargins"),
                "roe": safe_get_numeric(info, "returnOnEquity"),
                "roa": safe_get_numeric(info, "returnOnAssets"),
                "roic": safe_get_numeric(info, "returnOnInvestedCapital"),
                
                # Financial Health
                "debt_to_equity": safe_get_numeric(info, "debtToEquity"),
                "current_ratio": safe_get_numeric(info, "currentRatio"),
                "quick_ratio": safe_get_numeric(info, "quickRatio"),
                "total_debt": safe_get_numeric(info, "totalDebt"),
                "total_cash": safe_get_numeric(info, "totalCash"),
                "free_cash_flow": safe_get_numeric(info, "freeCashflow"),
                "operating_cash_flow": safe_get_numeric(info, "operatingCashflow"),
                
                # Per Share Data
                "eps": safe_get_numeric(info, "trailingEps"),
                "book_value_per_share": safe_get_numeric(info, "bookValue"),
                "revenue_per_share": safe_get_numeric(info, "revenuePerShare"),
                
                # Dividend & Buybacks
                "dividend_yield": safe_get_numeric(info, "dividendYield"),
                "payout_ratio": safe_get_numeric(info, "payoutRatio"),
                
                # Insider & Institutional Ownership (Lynch criteria)
                "insider_ownership": safe_get_numeric(info, "insiderPercentHeld"),
                "institutional_ownership": safe_get_numeric(info, "institutionPercentHeld"),
                "shares_outstanding": safe_get_numeric(info, "sharesOutstanding"),
                "shares_short": safe_get_numeric(info, "sharesShort"),
                "short_ratio": safe_get_numeric(info, "shortRatio"),
                
                # Trading Data
                "beta": safe_get_numeric(info, "beta"),
                "volume": safe_get_numeric(info, "volume"),
                "avg_volume": safe_get_numeric(info, "averageVolume"),
                
                # Analyst Data
                "target_price": safe_get_numeric(info, "targetHighPrice"),
                "recommendation": info.get("recommendationKey", "N/A"),
            }

            # Calculate additional metrics
            # PEG Ratio calculation if not provided
            if data["peg_ratio"] is None and data["pe_ratio"] and data["earnings_growth"]:
                if data["earnings_growth"] > 0:
                    data["peg_ratio"] = data["pe_ratio"] / (data["earnings_growth"] * 100)
            
            # Calculate price position in 52-week range
            if data["price"] and data["52_week_high"] and data["52_week_low"]:
                data["price_in_range"] = (data["price"] - data["52_week_low"]) / (data["52_week_high"] - data["52_week_low"])
            
            # Get historical data for momentum
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
            print(f"  [ERROR] {ticker} - {str(e)}")
            return None



def get_small_cap_stocks() -> list:
    """
    Get a list of small-cap stocks with 100-bagger potential.
    Focus on market cap $100M - $2B range.
    """
    # Small-cap stocks across various sectors with growth potential
    return [
        # Technology
        "UPST", "SOFI", "AFRM", "PLTR", "RBLX", "U", "PATH", "AI", "BBAI", "BROS",
        "DOCS", "GTLB", "NCNO", "PCTY", "TENB", "ZS", "CRWD", "NET", "DDOG",
        
        # Healthcare/Biotech
        "MRNA", "REGN", "VRTX", "BIIB", "ALNY", "BMRN", "TECH", "EXAS", "ILMN",
        "INCY", "NBIX", "UTHR", "RARE", "FOLD", "BLUE", "SRPT", "BPMC", "ARVN",
        
        # Consumer
        "CHWY", "CHEF", "CVNA", "W", "OSTK", "PRTS", "GRPN", "QUOT", "FTCH", "REAL",
        "APRN", "YELP", "TRIP", "ABNB", "DASH", "UBER", "LYFT", "BIRD", "GROV",
        
        # Industrial
        "RKLB", "ASTS", "SPCE", "ASTR", "BLDE", "JOBY", "LILM", "ACHR", "EVTL",
        
        # Financial
        "LC", "UPST", "AFRM", "SQ", "PYPL", "COIN", "HOOD", "SOFI", "AFRM", "MELI",
        
        # Energy/Clean Tech
        "ENPH", "SEDG", "FSLR", "RUN", "NOVA", "PLUG", "BE", "BLDP", "FCEL", "CLNE",
        
        # Real Estate
        "EXR", "CUBE", "REXR", "NSA", "LSI", "CPT", "MAA", "ESS", "UDR", "CPT",
        
        # Materials
        "ALB", "SQM", "LAC", "LTHM", "PLL", "PILBF", "LITM", "SGML", "GLNCY",
    ]


def get_growth_stocks() -> list:
    """
    Get a list of growth stocks with strong revenue/earnings growth.
    """
    return [
        # High Growth Tech
        "NVDA", "AMD", "AVGO", "QCOM", "MU", "AMAT", "LRCX", "KLAC", "SNPS", "CDNS",
        "ADBE", "CRM", "NOW", "INTU", "WDAY", "TEAM", "ZM", "DOCU", "CRWD", "ZS",
        
        # E-commerce/Digital
        "AMZN", "SHOP", "MELI", "SE", "BABA", "JD", "PDD", "CPNG", "GRAB", "GOTO",
        
        # Cloud/SaaS
        "SNOW", "MDB", "ESTC", "S", "CFLT", "GTLB", "IOT", "FROG", "APPN", "NCNO",
        
        # Digital Payments
        "SQ", "PYPL", "AFRM", "UPST", "LC", "COIN", "HOOD", "SOFI",
    ]


def get_peter_lynch_style_stocks() -> list:
    """
    Get stocks that match Peter Lynch's investment style:
    - Simple businesses
    - Boring industries
    - Strong balance sheets
    - Consistent growth
    """
    return [
        # Boring but profitable
        "WM", "RSG", "WCN", "CWST",  # Waste management
        "ROL", "SCI", "CSV", "MATW",  # Services
        "FAST", "GWW", "MSM", "WSO",  # Industrial distribution
        "POOL", "AZEK", "TREX", "FBIN",  # Building products
        "CHD", "CLX", "EL", "EPC",  # Consumer staples
        "TTEK", "STRL", "MTZ", "PRIM",  # Infrastructure
        "EXPO", "APG", "ACM", "KBR",  # Engineering
        "BR", "BCO", "TRU", "EQIX",  # Business services
    ]


def get_all_screening_stocks() -> list:
    """Get comprehensive list of stocks to screen for 100-bagger potential."""
    all_stocks = []
    all_stocks.extend(get_small_cap_stocks())
    all_stocks.extend(get_growth_stocks())
    all_stocks.extend(get_peter_lynch_style_stocks())
    return list(dict.fromkeys(all_stocks))  # Remove duplicates


if __name__ == "__main__":
    fetcher = StockDataFetcher()
    tickers = ["AAPL", "MSFT", "GOOGL"]
    results = fetcher.fetch_multiple(tickers)
    print(f"\nResults: {len(results)} stocks")
    for r in results:
        print(f"  {r['symbol']}: ${r.get('price', 'N/A')} - PEG: {r.get('peg_ratio', 'N/A')}")
