import json
import os
import tempfile
import time
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any

import yfinance as yf
import requests
from requests_cache import CacheMixin, SQLiteCache
from requests_ratelimiter import LimiterMixin
from pyrate_limiter import Duration, Limiter, RequestRate

# Global shared cache directory for the Combined Analyzer
if os.environ.get("STREAMLIT_SERVER_HEADLESS"):
    CACHE_BASE_DIR = Path(tempfile.gettempdir()) / "qwen_combined_analyzer" / "cache"
else:
    CACHE_BASE_DIR = Path.home() / ".qwen_combined_analyzer" / "cache"
    
CACHE_EXPIRY_HOURS = 24

class CachedLimiterSession(CacheMixin, LimiterMixin, requests.Session):
    """A session that handles both caching and rate limiting."""
    pass

class BaseDataFetcher:
    """
    Base class for fetching financial data with intelligent caching and rate limiting.
    """

    def __init__(self, cache_filename: str):
        """Initialize the fetcher and load existing cache from disk."""
        self.cache_file = CACHE_BASE_DIR / cache_filename
        self.cache: dict = {}
        self.last_error = None
        
        # Setup cache directory
        try:
            CACHE_BASE_DIR.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError) as e:
            print(f"Warning: Could not create cache directory: {e}")

        self.session = self._setup_session()
        self._load_cache()

    def _setup_session(self):
        """Setup a robust requests session for yfinance."""
        sqlite_cache = CACHE_BASE_DIR / "yfinance_cache.sqlite"
        
        # Rate limit: 1 request per 1.5 seconds to be conservative
        limiter = Limiter(RequestRate(1, Duration.SECOND * 1.5))
        
        session = CachedLimiterSession(
            limiter=limiter,
            cache_name=str(sqlite_cache),
            backend='sqlite',
            expire_after=timedelta(hours=1),
            allowable_codes=(200,)
        )
        
        # Modern User-Agent
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Upgrade-Insecure-Requests': '1'
        })
        
        return session

    def _load_cache(self):
        """Load existing JSON cache from disk."""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    self.cache = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load cache: {e}")
            self.cache = {}

    def _save_cache(self):
        """Save current JSON cache to disk."""
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, indent=2, default=str)
        except Exception as e:
            print(f"Warning: Could not save cache: {e}")

    def _is_cache_valid(self, ticker: str) -> bool:
        """Check if cached JSON data for a ticker is still valid."""
        if ticker not in self.cache:
            return False
        cached_time = self.cache[ticker].get("timestamp", "")
        if not cached_time:
            return False
        try:
            cache_dt = datetime.fromisoformat(cached_time)
            return datetime.now() - cache_dt < timedelta(hours=CACHE_EXPIRY_HOURS)
        except:
            return False

    def _get_cached_data(self, ticker: str) -> Optional[dict]:
        """Retrieve valid cached JSON data for a ticker."""
        if self._is_cache_valid(ticker):
            return self.cache[ticker].get("data")
        return None

    def _cache_data(self, ticker: str, data: dict):
        """Store JSON data in cache."""
        self.cache[ticker] = {
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self._save_cache()

    def get_ticker_obj(self, ticker_symbol: str) -> yf.Ticker:
        """Returns a yfinance Ticker object using the robust session."""
        return yf.Ticker(ticker_symbol, session=self.session)

    def fetch_data(self, ticker: str) -> Optional[dict]:
        """To be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement fetch_data")

    def fetch_multiple(self, tickers: list, batch_size: int = 50, item_name: str = "items") -> list:
        """
        Fetch data for multiple tickers with random delays and error protection.
        """
        results = []
        consecutive_failures = 0
        total = len(tickers)

        for i, ticker in enumerate(tickers, 1):
            # Check if already in cache to skip delay
            if self._is_cache_valid(ticker):
                data = self._get_cached_data(ticker)
                if data:
                    results.append(data)
                    continue

            # Random small delay for non-cached items to mimic human behavior
            if i > 1:
                time.sleep(random.uniform(0.5, 1.5))

            try:
                data = self.fetch_data(ticker)
                if data:
                    results.append(data)
                    consecutive_failures = 0
                else:
                    consecutive_failures += 1
            except Exception as e:
                self.last_error = str(e)
                consecutive_failures += 1
                print(f"Error fetching {ticker}: {e}")

            # Safety break if being hard-blocked
            if consecutive_failures >= 10:
                self.last_error = "Too many consecutive failures. Yahoo Finance may be rate-limiting."
                print("Aborting fetch due to consecutive failures.")
                break

        return results

    def clear_cache(self):
        """Clear all cached data."""
        self.cache = {}
        if self.cache_file.exists():
            self.cache_file.unlink()
        sqlite_cache = CACHE_BASE_DIR / "yfinance_cache.sqlite"
        if sqlite_cache.exists():
            sqlite_cache.unlink()
        print("Cache cleared")

def safe_get_numeric(data, key, default=None):
    """Safely extract numeric value, handling None and invalid types."""
    val = data.get(key)
    if val is None:
        return default
    try:
        return float(val) if val not in ('', 'N/A', 'NaN') else default
    except (ValueError, TypeError):
        return default

