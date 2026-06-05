"""
Enums and constants for CombinedMarketAnalyzer.

This module contains:
- AssetType: Enum for asset types (stocks, etfs, funds)
- Cache configuration constants
- Strategy names
"""

from enum import Enum


class AssetType(Enum):
    """Enum for asset types."""
    STOCK = "stocks"
    ETF = "etfs"
    MUTUAL_FUND = "funds"
    
    @classmethod
    def get_all_types(cls) -> list:
        """Get all asset types as a list."""
        return [asset_type.value for asset_type in cls]
    
    @classmethod
    def from_string(cls, value: str) -> 'AssetType':
        """Convert a string to an AssetType enum."""
        for asset_type in cls:
            if asset_type.value == value:
                return asset_type
        raise ValueError(f"Unknown asset type: {value}")


class CacheConfig:
    """Cache configuration constants."""
    EXPIRY_HOURS = 24
    BASE_DIR_ENV_VAR = "COMBINED_ANALYZER_CACHE_DIR"


class StrategyNames:
    """Strategy name constants."""
    # Stock Strategies
    BENJAMIN_GRAHAM = "Benjamin Graham Value"
    MAGIC_FORMULA = "Magic Formula"
    PIOTROSKI_F_SCORE = "Piotroski F-Score"
    ALTMAZ_Z_SCORE = "Altman Z-Score"
    DIVIDEND_DISCOUNT_MODEL = "Dividend Discount Model"
    PEG_RATIO = "PEG Ratio"
    PRICE_TO_BOOK = "Price to Book"
    PRICE_TO_EARNINGS = "Price to Earnings"
    RETURN_ON_EQUITY = "Return on Equity"
    DEBT_TO_EQUITY = "Debt to Equity"
    
    # ETF Strategies
    EXPENSE_RATIO = "Expense Ratio"
    TRACKING_ERROR = "Tracking Error"
    DIVIDEND_YIELD = "Dividend Yield"
    DIVERSIFICATION = "Diversification"
    PERFORMANCE = "Performance"
    RISK_ADJUSTED_RETURN = "Risk-Adjusted Return"
    ASSET_ALLOCATION = "Asset Allocation"
    LIQUIDITY = "Liquidity"
    
    # Mutual Fund Strategies
    LONG_TERM_PERFORMANCE = "Long-Term Performance"
    EXPENSE_EFFICIENCY = "Expense Efficiency"
    TURNOVER_RATIO = "Turnover Ratio"
    CONSISTENCY = "Consistency"
    RISK_METRICS = "Risk Metrics"
    ALPHA = "Alpha"
    BETA = "Beta"
    
    # 100-Bagger Strategies
    PEG_RATIO_BAGGER = "PEG Ratio Analysis"
    RETURN_ON_EQUITY_BAGGER = "Return on Equity"
    CASH_FLOW_STRENGTH = "Cash Flow Strength"
    DEBT_LEVEL = "Debt Level"
    GROWTH_POTENTIAL = "Growth Potential"
    INSIDER_OWNERSHIP = "Insider Ownership"
    FOUNDER_LED = "Founder-Led"
    MARKET_POSITION = "Market Position"
    COMPETITIVE_ADVANTAGE = "Competitive Advantage"
    INDUSTRY_TRENDS = "Industry Trends"


class DataFields:
    """Data field constants."""
    # Common fields
    SYMBOL = "symbol"
    NAME = "name"
    PRICE = "price"
    NAV_PRICE = "nav_price"
    
    # Stock fields
    SECTOR = "sector"
    INDUSTRY = "industry"
    MARKET_CAP = "market_cap"
    PE_RATIO = "pe_ratio"
    FORWARD_PE = "forward_pe"
    PB_RATIO = "pb_ratio"
    PS_RATIO = "ps_ratio"
    PEG_RATIO = "peg_ratio"
    DIVIDEND_YIELD = "dividend_yield"
    EPS = "eps"
    BETA = "beta"
    ROE = "roe"
    ROA = "roa"
    DEBT_TO_EQUITY = "debt_to_equity"
    CURRENT_RATIO = "current_ratio"
    FREE_CASH_FLOW = "free_cash_flow"
    OPERATING_CASH_FLOW = "operating_cash_flow"
    PROFIT_MARGIN = "profit_margin"
    PAYOUT_RATIO = "payout_ratio"
    VOLUME = "volume"
    AVG_VOLUME = "avg_volume"
    
    # ETF fields
    EXPENSE_RATIO = "expense_ratio"
    YTD_RETURN = "ytd_return"
    ONE_YEAR_RETURN = "one_year_return"
    THREE_YEAR_RETURN = "three_year_return"
    FIVE_YEAR_RETURN = "five_year_return"
    TRACKING_ERROR = "tracking_error"
    SHARPE_RATIO = "sharpe_ratio"
    TOP_10_HOLDINGS_PCT = "top_10_holdings_pct"
    
    # Mutual Fund fields
    TURNOVER_RATIO = "turnover_ratio"
    ALPHA = "alpha"
    R_SQUARED = "r_squared"
    STANDARD_DEVIATION = "standard_deviation"
    TEN_YEAR_RETURN = "ten_year_return"
    
    # 100-Bagger fields
    REVENUE_GROWTH = "revenue_growth"
    EARNINGS_GROWTH = "earnings_growth"
    INSIDER_OWNERSHIP = "insider_ownership"
    INSTITUTIONAL_OWNERSHIP = "institutional_ownership"


class ErrorMessages:
    """Error message constants."""
    NETWORK_ERROR = "Network error: {error}. Please check your internet connection."
    RATE_LIMIT_ERROR = "Rate limit error: {error}. Please try again later."
    DATA_UNAVAILABLE = "Data unavailable for {symbol}. Please try a different ticker."
    INVALID_TICKER = "Invalid ticker symbol: {symbol}"
    CACHE_ERROR = "Cache error: {error}"
    API_KEY_MISSING = "API key not found. Please configure your {service} API key."
