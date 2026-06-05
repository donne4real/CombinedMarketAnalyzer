"""
Unit tests for BaseDataFetcher.

Tests cover:
- Cache loading/saving
- Cache validity checking
- Safe numeric extraction
"""

import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from shared_src.base_fetcher import BaseDataFetcher, safe_get_numeric


class MockFetcher(BaseDataFetcher):
    """Mock fetcher for testing."""
    
    def __init__(self, cache_filename="test_cache.json"):
        super().__init__(cache_filename)
    
    def fetch_data(self, ticker: str):
        """Mock fetch_data implementation."""
        return {"symbol": ticker, "price": 100.0, "name": f"Test {ticker}"}


@pytest.fixture
def temp_cache_dir():
    """Create a temporary cache directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


def test_safe_get_numeric():
    """Test safe_get_numeric helper function."""
    data = {
        "valid_float": 123.45,
        "valid_int": 100,
        "string_number": "123.45",
        "none_value": None,
        "empty_string": "",
        "na_string": "N/A",
        "nan_string": "NaN",
        "invalid_string": "not a number"
    }
    
    # Test valid numeric values
    assert safe_get_numeric(data, "valid_float") == 123.45
    assert safe_get_numeric(data, "valid_int") == 100.0
    assert safe_get_numeric(data, "string_number") == 123.45
    
    # Test None and empty values
    assert safe_get_numeric(data, "none_value") is None
    assert safe_get_numeric(data, "empty_string") is None
    assert safe_get_numeric(data, "na_string") is None
    assert safe_get_numeric(data, "nan_string") is None
    
    # Test invalid string
    assert safe_get_numeric(data, "invalid_string") is None
    
    # Test with default value
    assert safe_get_numeric(data, "nonexistent_key", default=0) == 0
    assert safe_get_numeric(data, "none_value", default=0) == 0


def test_cache_initialization(temp_cache_dir):
    """Test that cache directory is created on initialization."""
    cache_file = temp_cache_dir / "test_cache.json"
    
    with patch.object(BaseDataFetcher, 'CACHE_BASE_DIR', temp_cache_dir):
        fetcher = MockFetcher("test_cache.json")
        
        # Verify cache file path is set
        assert fetcher.cache_file == cache_file
        
        # Verify cache directory exists
        assert temp_cache_dir.exists()


def test_cache_loading(temp_cache_dir):
    """Test loading existing cache from disk."""
    cache_file = temp_cache_dir / "test_cache.json"
    
    # Create a cache file with test data
    cache_data = {
        "AAPL": {
            "timestamp": datetime.now().isoformat(),
            "data": {"symbol": "AAPL", "price": 150.0}
        }
    }
    with open(cache_file, "w") as f:
        json.dump(cache_data, f)
    
    with patch.object(BaseDataFetcher, 'CACHE_BASE_DIR', temp_cache_dir):
        fetcher = MockFetcher("test_cache.json")
        
        # Verify cache was loaded
        assert "AAPL" in fetcher.cache
        assert fetcher.cache["AAPL"]["data"]["price"] == 150.0


def test_cache_saving(temp_cache_dir):
    """Test saving cache to disk."""
    cache_file = temp_cache_dir / "test_cache.json"
    
    with patch.object(BaseDataFetcher, 'CACHE_BASE_DIR', temp_cache_dir):
        fetcher = MockFetcher("test_cache.json")
        
        # Add data to cache
        fetcher.cache["AAPL"] = {
            "timestamp": datetime.now().isoformat(),
            "data": {"symbol": "AAPL", "price": 150.0}
        }
        
        # Save cache
        fetcher._save_cache()
        
        # Verify file was created and contains the data
        assert cache_file.exists()
        with open(cache_file, "r") as f:
            saved_data = json.load(f)
        
        assert "AAPL" in saved_data
        assert saved_data["AAPL"]["data"]["price"] == 150.0


def test_cache_validity(temp_cache_dir):
    """Test cache validity checking."""
    cache_file = temp_cache_dir / "test_cache.json"
    
    with patch.object(BaseDataFetcher, 'CACHE_BASE_DIR', temp_cache_dir):
        fetcher = MockFetcher("test_cache.json")
        
        # Test with recent timestamp (should be valid)
        recent_time = datetime.now() - timedelta(hours=1)
        fetcher.cache["AAPL"] = {
            "timestamp": recent_time.isoformat(),
            "data": {"symbol": "AAPL"}
        }
        
        assert fetcher._is_cache_valid("AAPL") is True
        
        # Test with old timestamp (should be invalid)
        old_time = datetime.now() - timedelta(hours=25)
        fetcher.cache["MSFT"] = {
            "timestamp": old_time.isoformat(),
            "data": {"symbol": "MSFT"}
        }
        
        assert fetcher._is_cache_valid("MSFT") is False
        
        # Test with missing timestamp
        fetcher.cache["GOOGL"] = {"data": {"symbol": "GOOGL"}}
        assert fetcher._is_cache_valid("GOOGL") is False
        
        # Test with non-existent ticker
        assert fetcher._is_cache_valid("NONEXISTENT") is False


def test_get_cached_data(temp_cache_dir):
    """Test retrieving cached data."""
    cache_file = temp_cache_dir / "test_cache.json"
    
    with patch.object(BaseDataFetcher, 'CACHE_BASE_DIR', temp_cache_dir):
        fetcher = MockFetcher("test_cache.json")
        
        # Add valid cached data
        recent_time = datetime.now() - timedelta(hours=1)
        test_data = {"symbol": "AAPL", "price": 150.0}
        fetcher.cache["AAPL"] = {
            "timestamp": recent_time.isoformat(),
            "data": test_data
        }
        
        # Retrieve the data
        cached_data = fetcher._get_cached_data("AAPL")
        assert cached_data == test_data
        
        # Test with invalid cache
        old_time = datetime.now() - timedelta(hours=25)
        fetcher.cache["MSFT"] = {
            "timestamp": old_time.isoformat(),
            "data": {"symbol": "MSFT"}
        }
        
        assert fetcher._get_cached_data("MSFT") is None
        
        # Test with non-existent ticker
        assert fetcher._get_cached_data("NONEXISTENT") is None


def test_cache_data(temp_cache_dir):
    """Test storing data in cache."""
    cache_file = temp_cache_dir / "test_cache.json"
    
    with patch.object(BaseDataFetcher, 'CACHE_BASE_DIR', temp_cache_dir):
        fetcher = MockFetcher("test_cache.json")
        
        # Cache some data
        test_data = {"symbol": "AAPL", "price": 150.0}
        fetcher._cache_data("AAPL", test_data)
        
        # Verify it was stored
        assert "AAPL" in fetcher.cache
        assert fetcher.cache["AAPL"]["data"] == test_data
        assert "timestamp" in fetcher.cache["AAPL"]


def test_clear_cache(temp_cache_dir):
    """Test clearing the cache."""
    cache_file = temp_cache_dir / "test_cache.json"
    sqlite_cache = temp_cache_dir / "yfinance_cache.sqlite"
    
    with patch.object(BaseDataFetcher, 'CACHE_BASE_DIR', temp_cache_dir):
        fetcher = MockFetcher("test_cache.json")
        
        # Add data to cache
        fetcher.cache["AAPL"] = {"timestamp": datetime.now().isoformat(), "data": {"symbol": "AAPL"}}
        fetcher._save_cache()
        
        # Create a dummy SQLite cache file
        sqlite_cache.touch()
        
        # Clear cache
        fetcher.clear_cache()
        
        # Verify in-memory cache is empty
        assert fetcher.cache == {}
        
        # Verify JSON cache file was deleted
        assert not cache_file.exists()
        
        # Verify SQLite cache file was deleted
        assert not sqlite_cache.exists()


class TestFetchMultiple:
    """Test fetch_multiple functionality."""
    
    def test_fetch_multiple_basic(self, temp_cache_dir):
        """Test basic fetch_multiple functionality."""
        with patch.object(BaseDataFetcher, 'CACHE_BASE_DIR', temp_cache_dir):
            fetcher = MockFetcher("test_cache.json")
            
            # Mock the fetch_data method to return consistent data
            def mock_fetch(ticker):
                return {"symbol": ticker, "price": 100.0}
            
            fetcher.fetch_data = mock_fetch
            
            # Fetch multiple tickers
            tickers = ["AAPL", "MSFT", "GOOGL"]
            results = fetcher.fetch_multiple(tickers, batch_size=10)
            
            # Verify we got results for all tickers
            assert len(results) == 3
            assert all(result["symbol"] in tickers for result in results)
    
    def test_fetch_multiple_with_cache(self, temp_cache_dir):
        """Test fetch_multiple with cached data."""
        with patch.object(BaseDataFetcher, 'CACHE_BASE_DIR', temp_cache_dir):
            fetcher = MockFetcher("test_cache.json")
            
            # Pre-cache one ticker
            recent_time = datetime.now() - timedelta(hours=1)
            fetcher.cache["AAPL"] = {
                "timestamp": recent_time.isoformat(),
                "data": {"symbol": "AAPL", "price": 150.0}
            }
            
            # Mock fetch_data for uncached tickers
            def mock_fetch(ticker):
                return {"symbol": ticker, "price": 100.0}
            
            fetcher.fetch_data = mock_fetch
            
            # Fetch multiple tickers (one cached, two not)
            tickers = ["AAPL", "MSFT", "GOOGL"]
            results = fetcher.fetch_multiple(tickers, batch_size=10)
            
            # Verify we got results for all tickers
            assert len(results) == 3
            
            # Verify the cached ticker was used
            assert results[0]["symbol"] == "AAPL"
            assert results[0]["price"] == 150.0
    
    def test_fetch_multiple_with_errors(self, temp_cache_dir):
        """Test fetch_multiple with some errors."""
        with patch.object(BaseDataFetcher, 'CACHE_BASE_DIR', temp_cache_dir):
            fetcher = MockFetcher("test_cache.json")
            
            # Mock fetch_data to raise an error for one ticker
            def mock_fetch(ticker):
                if ticker == "MSFT":
                    raise Exception("Network error")
                return {"symbol": ticker, "price": 100.0}
            
            fetcher.fetch_data = mock_fetch
            
            # Fetch multiple tickers
            tickers = ["AAPL", "MSFT", "GOOGL"]
            results = fetcher.fetch_multiple(tickers, batch_size=10)
            
            # Verify we got results for successful tickers
            assert len(results) == 2  # MSFT should be skipped
            assert all(result["symbol"] in ["AAPL", "GOOGL"] for result in results)
            
            # Verify error was recorded
            assert fetcher.last_error is not None
