import json
import os
import tempfile
import time
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable

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

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/121.0.0.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15',
]

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
        
        # Rate limit: 1 request per 2 seconds to be very conservative
        limiter = Limiter(RequestRate(1, Duration.SECOND * 2))
        
        session = CachedLimiterSession(
            limiter=limiter,
            cache_name=str(sqlite_cache),
            backend='sqlite',
            expire_after=timedelta(hours=1),
            allowable_codes=(200,)
        )
        
        # Random initial User-Agent
        session.headers.update({
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Upgrade-Insecure-Requests': '1'
        })
        
        return session

    def _rotate_user_agent(self):
        """Rotate to a different User-Agent to help avoid persistent IP/browser fingerprint blocks."""
        new_ua = random.choice(USER_AGENTS)
        self.session.headers.update({'User-Agent': new_ua})
        return new_ua

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

    def fetch_multiple(self, tickers: list, batch_size: int = 50, item_name: str = "items", 
                       progress_callback: Optional[Callable[[int, int, str], None]] = None) -> list:
        """
        Fetch data for multiple tickers with intelligent retry logic and error protection.
        """
        results = []
        consecutive_failures = 0
        total = len(tickers)

        for i, ticker in enumerate(tickers, 1):
            if progress_callback:
                progress_callback(i, total, ticker)
            
            # Check if already in cache
            if self._is_cache_valid(ticker):
                data = self._get_cached_data(ticker)
                if data:
                    results.append(data)
                    continue

            # Adaptive delay
            delay = random.uniform(1.0, 3.0)
            if consecutive_failures > 0:
                delay += consecutive_failures * 2  # Exponential-ish backoff
            
            if i > 1:
                time.sleep(delay)

            try:
                data = self.fetch_data(ticker)
                if data:
                    results.append(data)
                    consecutive_failures = 0
                else:
                    consecutive_failures += 1
                    if consecutive_failures % 5 == 0:
                        self._rotate_user_agent()
            except Exception as e:
                self.last_error = str(e)
                consecutive_failures += 1
                print(f"Error fetching {ticker}: {e}")
                if consecutive_failures % 3 == 0:
                    self._rotate_user_agent()

            # "Cooling off" if we hit a streak of failures
            if consecutive_failures >= 15:
                wait_time = 60 # 1 minute cooling off
                print(f"Streaked {consecutive_failures} failures. Cooling off for {wait_time}s...")
                if progress_callback:
                    progress_callback(i, total, f"Cooling off ({wait_time}s)...")
                time.sleep(wait_time)
                consecutive_failures = 5 # Reset but keep partial penalty

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

