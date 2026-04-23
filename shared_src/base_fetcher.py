import json
import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import yfinance as yf
import requests
from requests_cache import CachedSession
from requests_ratelimiter import LimiterSession

# Global shared cache directory for the Combined Analyzer
# Use /tmp on Streamlit Cloud (read-only home dir), otherwise use home directory
if os.environ.get("STREAMLIT_SERVER_HEADLESS"):
    # Running on Streamlit Cloud - use temp directory
    CACHE_BASE_DIR = Path(tempfile.gettempdir()) / "qwen_combined_analyzer" / "cache"
else:
    CACHE_BASE_DIR = Path.home() / ".qwen_combined_analyzer" / "cache"
    
CACHE_EXPIRY_HOURS = 24  # Custom JSON cache valid for 24 hours

class BaseDataFetcher:
    """
    Base class for fetching financial data with intelligent caching.
    Provides global caching across all modules using JSON-based caching.
    Uses a robust requests session with caching and rate limiting for yfinance.
    """

    def __init__(self, cache_filename: str):
        """Initialize the fetcher and load existing cache from disk."""
        self.cache_file = CACHE_BASE_DIR / cache_filename
        self.cache: dict = {}
        self.session = self._setup_session()

        # Setup cache directory
        try:
            CACHE_BASE_DIR.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError) as e:
            print(f"Warning: Could not create cache directory: {e}")

        self._load_cache()

    def _setup_session(self):
        """Setup a robust requests session for yfinance to avoid rate limits."""
        # Path for the sqlite cache
        sqlite_cache = CACHE_BASE_DIR / "yfinance_cache.sqlite"
        
        # Create a session that caches and rate limits
        session = CachedSession(
            str(sqlite_cache),
            backend='sqlite',
            expire_after=timedelta(hours=1)
        )
        
        # Add a realistic user-agent
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        })
        
        return session

    def _load_cache(self):
        """Load existing JSON cache from disk on initialization."""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    self.cache = json.load(f)
                print(f"Loaded cache with {len(self.cache)} items from {self.cache_file.name}")
        except (json.JSONDecodeError, IOError, PermissionError) as e:
            print(f"Warning: Could not load cache: {e}")
            self.cache = {}

    def _save_cache(self):
        """Save current JSON cache to disk."""
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, indent=2, default=str)
        except (OSError, IOError, PermissionError, TypeError) as e:
            print(f"Warning: Could not save cache: {e}")

    def _is_cache_valid(self, ticker: str) -> bool:
        """Check if cached JSON data for a ticker is still valid (not expired)."""
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
        """Store JSON data in cache with current timestamp."""
        self.cache[ticker] = {
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self._save_cache()

    def get_ticker_obj(self, ticker_symbol: str) -> yf.Ticker:
        """Returns a yfinance Ticker object using the robust session."""
        return yf.Ticker(ticker_symbol, session=self.session)

    def fetch_data(self, ticker: str) -> Optional[dict]:
        """
        To be implemented by subclasses.
        Should handle fetching from yfinance using self.get_ticker_obj() and returning formatted data.
        """
        raise NotImplementedError("Subclasses must implement fetch_data")

    def fetch_multiple(self, tickers: list, batch_size: int = 50, item_name: str = "items") -> list:
        """
        Fetch data for multiple tickers with batching and progress tracking.
        """
        results = []
        total = len(tickers)

        print(f"\nFetching data for {total} {item_name} (batch size: {batch_size})...")
        print("=" * 60)

        for i, ticker in enumerate(tickers, 1):
            print(f"[{i}/{total}] ", end="")
            try:
                data = self.fetch_data(ticker)
                if data:
                    results.append(data)
            except Exception as e:
                print(f"Unhandled error fetching {ticker}: {e}")

        print("=" * 60)
        print(f"Fetched {len(results)} of {total} {item_name} successfully")
        return results

    def clear_cache(self):
        """Clear all cached data from memory and disk."""
        self.cache = {}
        if self.cache_file.exists():
            self.cache_file.unlink()
        
        # Also clear the sqlite cache
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

