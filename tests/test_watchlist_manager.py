"""
Unit tests for WatchlistManager.

Tests cover:
- Adding/removing tickers
- Persistence to/from JSON
- Watchlist initialization
"""

import json
import tempfile
from pathlib import Path
import pytest

from shared_src.watchlist_manager import WatchlistManager


@pytest.fixture
def temp_watchlist_file():
    """Create a temporary watchlist file for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        watchlist_path = Path(tmpdir) / "test_watchlist.json"
        # Monkey-patch the WATCHLIST_FILE for this test
        original_file = WatchlistManager.WATCHLIST_FILE if hasattr(WatchlistManager, 'WATCHLIST_FILE') else None
        
        # Create a new manager with the temp path
        class TestWatchlistManager(WatchlistManager):
            WATCHLIST_FILE = watchlist_path
        
        yield TestWatchlistManager, watchlist_path
        
        # Cleanup
        if original_file:
            WatchlistManager.WATCHLIST_FILE = original_file


def test_watchlist_initialization():
    """Test that WatchlistManager initializes with empty lists."""
    manager = WatchlistManager()
    watchlist = manager.get_watchlist()
    
    assert "stocks" in watchlist
    assert "etfs" in watchlist
    assert "funds" in watchlist
    assert isinstance(watchlist["stocks"], list)
    assert isinstance(watchlist["etfs"], list)
    assert isinstance(watchlist["funds"], list)


def test_add_ticker():
    """Test adding a ticker to the watchlist."""
    manager = WatchlistManager()
    
    # Add a stock ticker
    result = manager.add_ticker("stocks", "AAPL")
    assert result is True
    
    watchlist = manager.get_watchlist()
    assert "AAPL" in watchlist["stocks"]
    
    # Add an ETF ticker
    result = manager.add_ticker("etfs", "SPY")
    assert result is True
    
    watchlist = manager.get_watchlist()
    assert "SPY" in watchlist["etfs"]
    
    # Add a mutual fund ticker
    result = manager.add_ticker("funds", "VFINX")
    assert result is True
    
    watchlist = manager.get_watchlist()
    assert "VFINX" in watchlist["funds"]


def test_add_duplicate_ticker():
    """Test that adding a duplicate ticker returns False."""
    manager = WatchlistManager()
    
    # Add a ticker
    result1 = manager.add_ticker("stocks", "AAPL")
    assert result1 is True
    
    # Try to add the same ticker again
    result2 = manager.add_ticker("stocks", "AAPL")
    assert result2 is False
    
    # Verify only one instance exists
    watchlist = manager.get_watchlist()
    assert watchlist["stocks"].count("AAPL") == 1


def test_remove_ticker():
    """Test removing a ticker from the watchlist."""
    manager = WatchlistManager()
    
    # Add a ticker first
    manager.add_ticker("stocks", "AAPL")
    watchlist = manager.get_watchlist()
    assert "AAPL" in watchlist["stocks"]
    
    # Remove the ticker
    result = manager.remove_ticker("stocks", "AAPL")
    assert result is True
    
    watchlist = manager.get_watchlist()
    assert "AAPL" not in watchlist["stocks"]


def test_remove_nonexistent_ticker():
    """Test that removing a non-existent ticker returns False."""
    manager = WatchlistManager()
    
    # Try to remove a ticker that doesn't exist
    result = manager.remove_ticker("stocks", "NONEXISTENT")
    assert result is False


def test_get_tickers_by_type():
    """Test getting tickers for a specific asset type."""
    manager = WatchlistManager()
    
    # Add some tickers
    manager.add_ticker("stocks", "AAPL")
    manager.add_ticker("stocks", "MSFT")
    manager.add_ticker("etfs", "SPY")
    
    # Get stocks
    stocks = manager.get_tickers_by_type("stocks")
    assert "AAPL" in stocks
    assert "MSFT" in stocks
    assert "SPY" not in stocks
    
    # Get ETFs
    etfs = manager.get_tickers_by_type("etfs")
    assert "SPY" in etfs
    assert "AAPL" not in etfs


def test_case_insensitive_tickers():
    """Test that tickers are stored in uppercase."""
    manager = WatchlistManager()
    
    # Add a lowercase ticker
    manager.add_ticker("stocks", "aapl")
    
    watchlist = manager.get_watchlist()
    assert "AAPL" in watchlist["stocks"]
    assert "aapl" not in watchlist["stocks"]


def test_whitespace_handling():
    """Test that tickers with whitespace are stripped."""
    manager = WatchlistManager()
    
    # Add a ticker with whitespace
    manager.add_ticker("stocks", "  AAPL  ")
    
    watchlist = manager.get_watchlist()
    assert "AAPL" in watchlist["stocks"]
    assert "  AAPL  " not in watchlist["stocks"]


# Integration tests for persistence
class TestWatchlistPersistence:
    """Test watchlist persistence to disk."""
    
    @pytest.fixture
    def temp_watchlist_path(self):
        """Create a temporary watchlist file path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            watchlist_path = Path(tmpdir) / "watchlist.json"
            yield watchlist_path
    
    def test_save_and_load_watchlist(self, temp_watchlist_path):
        """Test saving and loading watchlist from disk."""
        # Create a manager with the temp path
        manager = WatchlistManager()
        manager.WATCHLIST_FILE = temp_watchlist_path
        
        # Add some tickers
        manager.add_ticker("stocks", "AAPL")
        manager.add_ticker("etfs", "SPY")
        
        # Verify the file was created
        assert temp_watchlist_path.exists()
        
        # Read the file directly
        with open(temp_watchlist_path, "r") as f:
            data = json.load(f)
        
        assert "AAPL" in data["stocks"]
        assert "SPY" in data["etfs"]
        
        # Create a new manager and verify it loads the data
        manager2 = WatchlistManager()
        manager2.WATCHLIST_FILE = temp_watchlist_path
        watchlist = manager2.get_watchlist()
        
        assert "AAPL" in watchlist["stocks"]
        assert "SPY" in watchlist["etfs"]
    
    def test_load_corrupted_watchlist(self, temp_watchlist_path):
        """Test loading a corrupted watchlist file."""
        # Write invalid JSON to the file
        with open(temp_watchlist_path, "w") as f:
            f.write("invalid json")
        
        # Create a manager and verify it handles the error gracefully
        manager = WatchlistManager()
        manager.WATCHLIST_FILE = temp_watchlist_path
        
        # Should return empty watchlist
        watchlist = manager.get_watchlist()
        assert watchlist == {"stocks": [], "etfs": [], "funds": []}
    
    def test_load_nonexistent_watchlist(self, temp_watchlist_path):
        """Test loading from a non-existent file."""
        # Make sure the file doesn't exist
        if temp_watchlist_path.exists():
            temp_watchlist_path.unlink()
        
        # Create a manager and verify it initializes empty
        manager = WatchlistManager()
        manager.WATCHLIST_FILE = temp_watchlist_path
        
        watchlist = manager.get_watchlist()
        assert watchlist == {"stocks": [], "etfs": [], "funds": []}
