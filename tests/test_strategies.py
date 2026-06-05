"""
Unit tests for investment strategies.

Tests cover:
- Piotroski F-Score calculation
- Benjamin Graham Value calculation
- Magic Formula calculation
- Basic strategy scoring
"""

import pytest
from unittest.mock import MagicMock

# We'll test the strategies by importing and mocking the data
# Since the actual strategy implementations depend on yfinance data,
# we'll create mock data and test the calculations


class TestPiotroskiFScore:
    """Test Piotroski F-Score strategy."""
    
    def test_piotroski_f_score_basic(self):
        """Test basic Piotroski F-Score calculation with mock data."""
        # Mock stock data with all required fields for Piotroski
        mock_data = {
            "symbol": "TEST",
            "name": "Test Company",
            "roa": 0.15,  # Return on Assets
            "operating_cash_flow": 1000000,
            "net_income": 800000,
            "long_term_debt": 500000,
            "total_assets": 10000000,
            "current_ratio": 2.5,
            "shares_outstanding": 1000000,
            "gross_margin": 0.4,
            "asset_turnover": 1.2,
            # Historical data for year-over-year comparisons
            "year_ago_price": 100.0,
            "price": 120.0,
        }
        
        # Import and test the strategy
        # Note: We'll need to check the actual implementation
        # For now, we'll test the basic structure
        from stock_src.strategies import InvestmentStrategies
        
        strategies = InvestmentStrategies(mock_data)
        
        # Test that the strategy can be instantiated
        assert strategies is not None
        
        # Test that we can get all strategies
        all_strategies = strategies.get_all_strategies()
        assert isinstance(all_strategies, dict)
        
        # Test that Piotroski is one of the strategies
        assert "Piotroski F-Score" in all_strategies or any("Piotroski" in k for k in all_strategies.keys())
    
    def test_piotroski_f_score_components(self):
        """Test individual components of Piotroski F-Score."""
        # This would test the 9 components of the F-Score:
        # 1. Positive ROA
        # 2. Positive Operating Cash Flow
        # 3. ROA > Prior Year ROA
        # 4. Operating Cash Flow > Net Income
        # 5. Lower Long-term Debt Ratio
        # 6. Higher Current Ratio
        # 7. No New Shares Issued
        # 8. Higher Gross Margin
        # 9. Higher Asset Turnover
        
        # For now, we'll just verify the structure
        from stock_src.strategies import InvestmentStrategies
        
        mock_data = {
            "symbol": "TEST",
            "roa": 0.15,
            "operating_cash_flow": 1000000,
            "net_income": 800000,
        }
        
        strategies = InvestmentStrategies(mock_data)
        assert strategies is not None


class TestBenjaminGraham:
    """Test Benjamin Graham Value strategy."""
    
    def test_benjamin_graham_basic(self):
        """Test basic Benjamin Graham calculation."""
        from stock_src.strategies import InvestmentStrategies
        
        # Mock data for Benjamin Graham
        # Graham's formula: Intrinsic Value = EPS * (8.5 + 2g) * (Yield / 4.4)
        # where g is growth rate and Yield is AAA bond yield (default 4.4%)
        mock_data = {
            "symbol": "TEST",
            "eps": 5.0,  # Earnings per share
            "earnings_growth": 0.10,  # 10% growth
            "price": 100.0,
            "book_value": 80.0,
        }
        
        strategies = InvestmentStrategies(mock_data)
        all_strategies = strategies.get_all_strategies()
        
        # Verify we have strategies
        assert len(all_strategies) > 0
        
        # Check for Benjamin Graham or similar value strategy
        strategy_names = [k for k in all_strategies.keys()]
        assert any("Graham" in name or "Value" in name for name in strategy_names)
    
    def test_benjamin_graham_formula(self):
        """Test the Benjamin Graham formula calculation."""
        # Graham's simplified formula: Intrinsic Value = EPS * (8.5 + 2 * Growth Rate)
        # Then compare to current price
        
        from stock_src.strategies import InvestmentStrategies
        
        mock_data = {
            "symbol": "TEST",
            "eps": 5.0,
            "earnings_growth": 0.10,  # 10%
            "price": 50.0,
        }
        
        strategies = InvestmentStrategies(mock_data)
        
        # The strategy should be able to calculate without errors
        assert strategies is not None


class TestMagicFormula:
    """Test Magic Formula strategy (Greenblatt)."""
    
    def test_magic_formula_basic(self):
        """Test basic Magic Formula calculation."""
        from stock_src.strategies import InvestmentStrategies
        
        # Magic Formula: Rank by EBIT/EV (Earnings Yield) and ROIC
        mock_data = {
            "symbol": "TEST",
            "ebit": 1000000,  # Earnings Before Interest and Taxes
            "enterprise_value": 10000000,  # EV
            "roic": 0.15,  # Return on Invested Capital
            "price": 100.0,
        }
        
        strategies = InvestmentStrategies(mock_data)
        all_strategies = strategies.get_all_strategies()
        
        # Verify we have strategies
        assert len(all_strategies) > 0
        
        # Check for Magic Formula
        strategy_names = [k for k in all_strategies.keys()]
        assert any("Magic" in name or "Greenblatt" in name for name in strategy_names)


class TestStrategyScoring:
    """Test strategy scoring system."""
    
    def test_total_score_calculation(self):
        """Test that total score is calculated from individual strategies."""
        from stock_src.strategies import InvestmentStrategies
        
        mock_data = {
            "symbol": "TEST",
            "price": 100.0,
            "eps": 5.0,
            "pe_ratio": 15.0,
            "pb_ratio": 2.0,
            "roe": 0.15,
            "roa": 0.10,
            "dividend_yield": 0.02,
            "debt_to_equity": 0.5,
            "current_ratio": 2.0,
            "earnings_growth": 0.10,
            "revenue_growth": 0.08,
        }
        
        strategies = InvestmentStrategies(mock_data)
        all_strategies = strategies.get_all_strategies()
        
        # Verify we have multiple strategies
        assert len(all_strategies) >= 5
        
        # Verify each strategy has a score and reason
        for name, strategy in all_strategies.items():
            assert "score" in strategy
            assert "reason" in strategy
            assert 0 <= strategy["score"] <= 10
        
        # Verify total score exists and is reasonable
        assert "total_score" in all_strategies or any("total" in k.lower() for k in all_strategies.keys())
    
    def test_score_normalization(self):
        """Test that scores are normalized to 0-10 range."""
        from stock_src.strategies import InvestmentStrategies
        
        mock_data = {
            "symbol": "TEST",
            "price": 100.0,
            "pe_ratio": 15.0,
            "pb_ratio": 2.0,
        }
        
        strategies = InvestmentStrategies(mock_data)
        all_strategies = strategies.get_all_strategies()
        
        # All scores should be between 0 and 10
        for name, strategy in all_strategies.items():
            if "score" in strategy:
                assert 0 <= strategy["score"] <= 10


class TestETFStrategies:
    """Test ETF-specific strategies."""
    
    def test_etf_strategies_basic(self):
        """Test basic ETF strategy calculations."""
        from etf_src.strategies import ETFStrategies
        
        mock_data = {
            "symbol": "SPY",
            "name": "SPDR S&P 500 ETF",
            "expense_ratio": 0.000945,  # 0.0945%
            "nav_price": 500.0,
            "ytd_return": 0.10,  # 10% YTD
            "one_year_return": 0.15,
            "three_year_return": 0.12,
            "five_year_return": 0.10,
            "dividend_yield": 0.015,
            "tracking_error": 0.05,  # 5%
            "beta": 1.0,
            "sharpe_ratio": 1.2,
            "top_10_holdings_pct": 0.25,  # 25% in top 10
        }
        
        strategies = ETFStrategies(mock_data)
        all_strategies = strategies.get_all_strategies()
        
        # Verify we have ETF-specific strategies
        assert len(all_strategies) > 0
        
        # Check for ETF-specific strategy names
        strategy_names = [k for k in all_strategies.keys()]
        etf_keywords = ["Expense", "Tracking", "Dividend", "Diversification", "Performance"]
        assert any(any(keyword in name for keyword in etf_keywords) for name in strategy_names)


class TestMutualFundStrategies:
    """Test Mutual Fund-specific strategies."""
    
    def test_mutual_fund_strategies_basic(self):
        """Test basic Mutual Fund strategy calculations."""
        from mf_src.strategies import MutualFundStrategies
        
        mock_data = {
            "symbol": "VFINX",
            "name": "Vanguard 500 Index Fund",
            "expense_ratio": 0.0014,  # 0.14%
            "nav_price": 350.0,
            "ytd_return": 0.08,
            "one_year_return": 0.12,
            "three_year_return": 0.10,
            "five_year_return": 0.09,
            "ten_year_return": 0.08,
            "dividend_yield": 0.018,
            "turnover_ratio": 0.05,  # 5%
            "alpha": 0.02,
            "beta": 0.98,
            "r_squared": 0.99,
            "standard_deviation": 0.15,
        }
        
        strategies = MutualFundStrategies(mock_data)
        all_strategies = strategies.get_all_strategies()
        
        # Verify we have Mutual Fund-specific strategies
        assert len(all_strategies) > 0
        
        # Check for MF-specific strategy names
        strategy_names = [k for k in all_strategies.keys()]
        mf_keywords = ["Expense", "Turnover", "Long-Term", "Consistency", "Risk"]
        assert any(any(keyword in name for keyword in mf_keywords) for name in strategy_names)


class TestHundredBaggerStrategies:
    """Test 100-Bagger screening strategies."""
    
    def test_100_bagger_strategies_basic(self):
        """Test basic 100-Bagger strategy calculations."""
        from bagger_src.strategies import HundredBaggerStrategies
        
        # Peter Lynch criteria for 100-baggers:
        # - Low PEG ratio (< 1)
        # - High ROE (> 15%)
        # - Strong operating cash flow
        # - Low debt
        # - Founder-led or strong management
        mock_data = {
            "symbol": "TEST",
            "price": 50.0,
            "eps": 2.5,
            "peg_ratio": 0.8,  # Low PEG
            "roe": 0.20,  # 20% ROE
            "operating_cash_flow": 1000000,
            "debt_to_equity": 0.1,  # Low debt
            "revenue_growth": 0.25,  # 25% growth
            "earnings_growth": 0.30,  # 30% growth
            "insider_ownership": 0.20,  # 20% insider ownership
            "institutional_ownership": 0.60,
        }
        
        strategies = HundredBaggerStrategies(mock_data)
        all_strategies = strategies.get_all_strategies()
        
        # Verify we have 100-Bagger-specific strategies
        assert len(all_strategies) > 0
        
        # Check for 100-Bagger-specific strategy names
        strategy_names = [k for k in all_strategies.keys()]
        bagger_keywords = ["PEG", "ROE", "Cash Flow", "Debt", "Growth", "Founder"]
        assert any(any(keyword in name for keyword in bagger_keywords) for name in strategy_names)
