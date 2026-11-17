"""Test script to verify all module imports work correctly."""

import sys
import os

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_shared_imports():
    """Test shared module imports."""
    print("Testing shared imports...")
    from shared_src.watchlist_manager import WatchlistManager
    from shared_src.base_fetcher import BaseDataFetcher
    from shared_src.visuals import create_speedometer, create_radar_chart
    from shared_src.ai_summary import generate_stock_summary
    print("  ✓ shared_src.watchlist_manager")
    print("  ✓ shared_src.base_fetcher")
    print("  ✓ shared_src.visuals")
    print("  ✓ shared_src.ai_summary")

def test_stock_imports():
    """Test stock module imports."""
    print("\nTesting stock module imports...")
    from stock_src.data_fetcher import StockDataFetcher
    from stock_src.strategies import InvestmentStrategies
    from stock_src.exporter import SpreadsheetExporter
    from stock_src.backtester import Backtester
    print("  ✓ stock_src.data_fetcher")
    print("  ✓ stock_src.strategies")
    print("  ✓ stock_src.exporter")
    print("  ✓ stock_src.backtester")

def test_etf_imports():
    """Test ETF module imports."""
    print("\nTesting ETF module imports...")
    from etf_src.data_fetcher import ETFDataFetcher
    from etf_src.strategies import ETFStrategies
    from etf_src.exporter import SpreadsheetExporter
    from etf_src.backtester import Backtester
    print("  ✓ etf_src.data_fetcher")
    print("  ✓ etf_src.strategies")
    print("  ✓ etf_src.exporter")
    print("  ✓ etf_src.backtester")

def test_mf_imports():
    """Test mutual fund module imports."""
    print("\nTesting mutual fund module imports...")
    from mf_src.data_fetcher import MutualFundDataFetcher
    from mf_src.strategies import MutualFundStrategies
    from mf_src.exporter import SpreadsheetExporter
    from mf_src.backtester import Backtester
    print("  ✓ mf_src.data_fetcher")
    print("  ✓ mf_src.strategies")
    print("  ✓ mf_src.exporter")
    print("  ✓ mf_src.backtester")

def test_bagger_imports():
    """Test bagger module imports."""
    print("\nTesting bagger module imports...")
    from bagger_src.data_fetcher import BaggerDataFetcher
    from bagger_src.strategies import HundredBaggerStrategies
    from bagger_src.exporter import SpreadsheetExporter
    from bagger_src.backtester import Backtester
    print("  ✓ bagger_src.data_fetcher")
    print("  ✓ bagger_src.strategies")
    print("  ✓ bagger_src.exporter")
    print("  ✓ bagger_src.backtester")

def test_instantiation():
    """Test that all fetchers can be instantiated."""
    print("\nTesting fetcher instantiation...")
    from stock_src.data_fetcher import StockDataFetcher
    from etf_src.data_fetcher import ETFDataFetcher
    from mf_src.data_fetcher import MutualFundDataFetcher
    from bagger_src.data_fetcher import BaggerDataFetcher
    
    stock = StockDataFetcher()
    print(f"  ✓ StockDataFetcher created (cache: {stock.cache_file})")
    
    etf = ETFDataFetcher()
    print(f"  ✓ ETFDataFetcher created (cache: {etf.cache_file})")
    
    mf = MutualFundDataFetcher()
    print(f"  ✓ MutualFundDataFetcher created (cache: {mf.cache_file})")
    
    bagger = BaggerDataFetcher()
    print(f"  ✓ BaggerDataFetcher created (cache: {bagger.cache_file})")

def main():
    print("=" * 50)
    print("CombinedMarketAnalyzer Import Tests")
    print("=" * 50)
    
    try:
        test_shared_imports()
        test_stock_imports()
        test_etf_imports()
        test_mf_imports()
        test_bagger_imports()
        test_instantiation()
        
        print("\n" + "=" * 50)
        print("ALL TESTS PASSED! ✓")
        print("=" * 50)
        return 0
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
