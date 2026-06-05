"""
Unit tests for data fetchers.

Tests cover:
- Stock data fetching (with mocks)
- ETF data fetching (with mocks)
- Mutual Fund data fetching (with mocks)
- Error handling in fetchers
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch, Mock
import pytest

# We'll mock yfinance to avoid actual API calls


class TestStockDataFetcher:
    """Test StockDataFetcher functionality."""
    
    @pytest.fixture
    def mock_yfinance(self):
        """Mock yfinance module."""
        with patch('yfinance.Ticker') as mock_ticker:
            # Create a mock Ticker object
            mock_ticker_instance = MagicMock()
            mock_ticker_instance.info = {
                "symbol": "AAPL",
                "shortName": "Apple Inc.",
                "longName": "Apple Inc.",
                "sector": "Technology",
                "industry": "Consumer Electronics",
                "exchange": "NASDAQ",
                "marketCap": 3000000000000,
                "currentPrice": 180.0,
                "regularMarketPrice": 180.0,
                "trailingPE": 25.0,
                "forwardPE": 22.0,
                "priceToBook": 35.0,
                "priceToSalesTrailing12Months": 6.0,
                "pegRatio": 1.8,
                "dividendYield": 0.005,
                "trailingEps": 7.2,
                "beta": 1.2,
                "fiftyTwoWeekHigh": 190.0,
                "fiftyTwoWeekLow": 130.0,
                "fiftyDayAverage": 175.0,
                "twoHundredDayAverage": 165.0,
                "revenueGrowth": 0.08,
                "earningsGrowth": 0.12,
                "returnOnEquity": 0.50,
                "returnOnAssets": 0.20,
                "debtToEquity": 1.5,
                "currentRatio": 1.8,
                "freeCashflow": 80000000000,
                "operatingCashflow": 100000000000,
                "profitMargins": 0.25,
                "payoutRatio": 0.20,
                "volume": 50000000,
                "averageVolume": 40000000,
            }
            
            # Mock history method
            mock_history = MagicMock()
            mock_history.return_value = Mock()
            mock_history.return_value.__getitem__ = MagicMock(return_value=Mock())
            mock_history.return_value.__getitem__.return_value.iloc = MagicMock()
            mock_history.return_value.__getitem__.return_value.iloc.__getitem__ = MagicMock(return_value=150.0)
            mock_ticker_instance.history = mock_history
            
            mock_ticker.return_value = mock_ticker_instance
            yield mock_ticker
    
    def test_stock_fetcher_initialization(self, temp_cache_dir):
        """Test StockDataFetcher initialization."""
        with patch.object(BaseDataFetcher, 'CACHE_BASE_DIR', temp_cache_dir):
            from stock_src.data_fetcher import StockDataFetcher
            
            fetcher = StockDataFetcher()
            assert fetcher is not None
            assert fetcher.cache == {}
    
    def test_fetch_stock_data(self, mock_yfinance, temp_cache_dir):
        """Test fetching stock data."""
        with patch.object(BaseDataFetcher, 'CACHE_BASE_DIR', temp_cache_dir):
            from stock_src.data_fetcher import StockDataFetcher
            
            fetcher = StockDataFetcher()
            
            # Fetch data for AAPL
            data = fetcher.fetch_data("AAPL")
            
            # Verify we got data
            assert data is not None
            assert data["symbol"] == "AAPL"
            assert data["name"] == "Apple Inc."
            assert data["price"] == 180.0
            assert data["pe_ratio"] == 25.0
    
    def test_fetch_multiple_stocks(self, mock_yfinance, temp_cache_dir):
        """Test fetching multiple stocks."""
        with patch.object(BaseDataFetcher, 'CACHE_BASE_DIR', temp_cache_dir):
            from stock_src.data_fetcher import StockDataFetcher
            
            fetcher = StockDataFetcher()
            
            # Fetch multiple stocks
            tickers = ["AAPL", "MSFT", "GOOGL"]
            results = fetcher.fetch_multiple(tickers, batch_size=10)
            
            # Verify we got results
            assert len(results) == 3
            assert all(result["symbol"] in tickers for result in results)
    
    def test_cached_stock_data(self, mock_yfinance, temp_cache_dir):
        """Test that fetched data is cached."""
        with patch.object(BaseDataFetcher, 'CACHE_BASE_DIR', temp_cache_dir):
            from stock_src.data_fetcher import StockDataFetcher
            
            fetcher = StockDataFetcher()
            
            # Fetch data for AAPL
            data1 = fetcher.fetch_data("AAPL")
            
            # Fetch again - should use cache
            data2 = fetcher.fetch_data("AAPL")
            
            # Both should be the same
            assert data1 == data2
            
            # Verify it's in the cache
            assert "AAPL" in fetcher.cache


class TestETFDataFetcher:
    """Test ETFDataFetcher functionality."""
    
    @pytest.fixture
    def mock_yfinance_etf(self):
        """Mock yfinance module for ETFs."""
        with patch('yfinance.Ticker') as mock_ticker:
            # Create a mock Ticker object for ETF
            mock_ticker_instance = MagicMock()
            mock_ticker_instance.info = {
                "symbol": "SPY",
                "shortName": "SPDR S&P 500 ETF Trust",
                "longName": "SPDR S&P 500 ETF Trust",
                "sector": "N/A",
                "industry": "N/A",
                "exchange": "NYSE ARCA",
                "marketCap": None,
                "currentPrice": 500.0,
                "regularMarketPrice": 500.0,
                "nav_price": 500.0,
                "expenseRatio": 0.000945,
                "dividendYield": 0.015,
                "ytdReturn": 0.10,
                "oneYearReturn": 0.15,
                "threeYearReturn": 0.12,
                "fiveYearReturn": 0.10,
                "beta": 1.0,
                "sharpeRatio": 1.2,
                "trackingError": 0.05,
                "topHoldings": ["AAPL", "MSFT", "AMZN", "GOOGL", "GOOG"],
                "topHoldingsPercentage": [0.07, 0.06, 0.04, 0.02, 0.02],
            }
            
            mock_ticker.return_value = mock_ticker_instance
            yield mock_ticker
    
    def test_etf_fetcher_initialization(self, temp_cache_dir):
        """Test ETFDataFetcher initialization."""
        with patch.object(BaseDataFetcher, 'CACHE_BASE_DIR', temp_cache_dir):
            from etf_src.data_fetcher import ETFDataFetcher
            
            fetcher = ETFDataFetcher()
            assert fetcher is not None
    
    def test_fetch_etf_data(self, mock_yfinance_etf, temp_cache_dir):
        """Test fetching ETF data."""
        with patch.object(BaseDataFetcher, 'CACHE_BASE_DIR', temp_cache_dir):
            from etf_src.data_fetcher import ETFDataFetcher
            
            fetcher = ETFDataFetcher()
            
            # Fetch data for SPY
            data = fetcher.fetch_data("SPY")
            
            # Verify we got data
            assert data is not None
            assert data["symbol"] == "SPY"
            assert data["nav_price"] == 500.0
            assert data["expense_ratio"] == 0.000945


class TestMutualFundDataFetcher:
    """Test MutualFundDataFetcher functionality."""
    
    @pytest.fixture
    def mock_yfinance_mf(self):
        """Mock yfinance module for Mutual Funds."""
        with patch('yfinance.Ticker') as mock_ticker:
            # Create a mock Ticker object for Mutual Fund
            mock_ticker_instance = MagicMock()
            mock_ticker_instance.info = {
                "symbol": "VFINX",
                "shortName": "Vanguard 500 Index Fund Investor Shares",
                "longName": "Vanguard 500 Index Fund Investor Shares",
                "sector": "N/A",
                "industry": "N/A",
                "exchange": "NASDAQ",
                "nav_price": 350.0,
                "currentPrice": 350.0,
                "expenseRatio": 0.0014,
                "dividendYield": 0.018,
                "ytdReturn": 0.08,
                "oneYearReturn": 0.12,
                "threeYearReturn": 0.10,
                "fiveYearReturn": 0.09,
                "tenYearReturn": 0.08,
                "turnoverRatio": 0.05,
                "alpha": 0.02,
                "beta": 0.98,
                "rSquared": 0.99,
                "standardDeviation": 0.15,
            }
            
            mock_ticker.return_value = mock_ticker_instance
            yield mock_ticker
    
    def test_mf_fetcher_initialization(self, temp_cache_dir):
        """Test MutualFundDataFetcher initialization."""
        with patch.object(BaseDataFetcher, 'CACHE_BASE_DIR', temp_cache_dir):
            from mf_src.data_fetcher import MutualFundDataFetcher
            
            fetcher = MutualFundDataFetcher()
            assert fetcher is not None
    
    def test_fetch_mf_data(self, mock_yfinance_mf, temp_cache_dir):
        """Test fetching Mutual Fund data."""
        with patch.object(BaseDataFetcher, 'CACHE_BASE_DIR', temp_cache_dir):
            from mf_src.data_fetcher import MutualFundDataFetcher
            
            fetcher = MutualFundDataFetcher()
            
            # Fetch data for VFINX
            data = fetcher.fetch_data("VFINX")
            
            # Verify we got data
            assert data is not None
            assert data["symbol"] == "VFINX"
            assert data["nav_price"] == 350.0
            assert data["expense_ratio"] == 0.0014


class TestBaggerDataFetcher:
    """Test 100-Bagger DataFetcher functionality."""
    
    def test_bagger_fetcher_initialization(self, temp_cache_dir):
        """Test 100-Bagger DataFetcher initialization."""
        with patch.object(BaseDataFetcher, 'CACHE_BASE_DIR', temp_cache_dir):
            from bagger_src.data_fetcher import StockDataFetcher
            
            fetcher = StockDataFetcher()
            assert fetcher is not None
    
    def test_get_screening_stocks(self):
        """Test getting stocks for screening."""
        from bagger_src.data_fetcher import (
            get_small_cap_stocks,
            get_growth_stocks,
            get_peter_lynch_style_stocks,
            get_all_screening_stocks,
        )
        
        # Test that these functions exist and return lists
        small_caps = get_small_cap_stocks()
        assert isinstance(small_caps, list)
        
        growth_stocks = get_growth_stocks()
        assert isinstance(growth_stocks, list)
        
        peter_lynch_stocks = get_peter_lynch_style_stocks()
        assert isinstance(peter_lynch_stocks, list)
        
        all_stocks = get_all_screening_stocks()
        assert isinstance(all_stocks, list)


# Import BaseDataFetcher for the fixtures
from shared_src.base_fetcher import BaseDataFetcher
