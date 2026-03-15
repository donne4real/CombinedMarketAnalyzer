"""
Investment Strategy Analyzers Module

Implements 10 sophisticated investment models for comprehensive stock analysis:

Models:
    1. Benjamin Graham - Deep value with margin of safety
    2. Magic Formula (Greenblatt) - Earnings yield + return on capital
    3. Piotroski F-Score - 9-point financial strength scale
    4. Altman Z-Score - Bankruptcy prediction
    5. Growth Model - Revenue/earnings growth focus
    6. Dividend Discount Model - DDM valuation
    7. Momentum Strategy - Price trends and moving averages
    8. Quality Model - High ROE/ROA, strong cash flow
    9. Fama-French 3-Factor - Market, size, value factors
    10. Mean Reversion - Oversold conditions

Scoring System:
    Each model scores stocks from 0-10:
    - 8-10: Strong buy signal (🟢)
    - 5-7: Moderate/hold (🟡)
    - 0-4: Weak/avoid (🔴)

Example:
    >>> from stock_src.strategies import InvestmentStrategies
    >>> analysis = InvestmentStrategies.analyze_stock(stock_data)
    >>> print(f"Total Score: {analysis['total_score']}/100")
    >>> print(f"Average Score: {analysis['average_score']}/10")
"""

from typing import Optional
import math


class InvestmentStrategies:
    """
    Analyzes stocks using 10 different investment models.

    Each model implements a specific investment philosophy and scores
    stocks from 0-10 based on how well they match the criteria.

    Models:
        - Benjamin Graham: Deep value investing
        - Magic Formula: Quantitative value + quality
        - Piotroski F-Score: Financial strength
        - Altman Z-Score: Bankruptcy risk
        - Growth Model: Revenue/earnings growth
        - Dividend Discount: DDM valuation
        - Momentum: Price trends
        - Quality Model: Fundamental quality
        - Fama-French: Factor exposure
        - Mean Reversion: Contrarian signals

    Example:
        >>> strategies = InvestmentStrategies()
        >>> analysis = strategies.analyze_stock(stock_data)
        >>> print(f"Benjamin Graham Score: {analysis['benjamin_graham']['score']}/10")
    """

    @staticmethod
    def score_benjamin_graham(data: dict) -> tuple[int, str]:
        """
        Benjamin Graham Strategy - Deep value with margin of safety.

        Based on principles from "The Intelligent Investor":
        - P/E ratio < 15 (max 3 points)
        - P/B ratio < 1.5 (max 3 points)
        - Current ratio > 2 (max 2 points)
        - Debt/Equity < 0.5 (max 2 points)
        - Pays dividend (1 point)
        - Positive earnings (1 point)

        Args:
            data (dict): Stock data dictionary with financial metrics

        Returns:
            tuple[int, str]: Score (0-10) and explanation string
        """
        score = 0
        reasons = []

        pe = data.get("pe_ratio")
        pb = data.get("pb_ratio")
        current_ratio = data.get("current_ratio")
        debt_to_equity = data.get("debt_to_equity")
        div_yield = data.get("dividend_yield")
        eps = data.get("eps")

        # P/E < 15 (Graham's rule)
        if pe and pe > 0:
            if pe < 10:
                score += 3
                reasons.append(f"Very low P/E ({pe:.1f})")
            elif pe < 15:
                score += 2
                reasons.append(f"P/E < 15 ({pe:.1f})")
            elif pe < 20:
                score += 1
            else:
                reasons.append(f"High P/E ({pe:.1f})")

        # P/B < 1.5 (Graham's rule)
        if pb and pb > 0:
            if pb < 1:
                score += 3
                reasons.append(f"P/B < 1 ({pb:.1f})")
            elif pb < 1.5:
                score += 2
                reasons.append(f"P/B < 1.5 ({pb:.1f})")
            elif pb < 2:
                score += 1
            else:
                reasons.append(f"High P/B ({pb:.1f})")

        # Current Ratio > 2 (liquidity)
        if current_ratio and current_ratio > 0:
            if current_ratio > 2:
                score += 2
                reasons.append("Strong liquidity")
            elif current_ratio > 1.5:
                score += 1
            else:
                reasons.append("Weak liquidity")

        # Debt/Equity < 0.5 (conservative)
        if debt_to_equity and debt_to_equity >= 0:
            if debt_to_equity < 0.3:
                score += 2
                reasons.append("Very low debt")
            elif debt_to_equity < 0.5:
                score += 1
                reasons.append("Low debt")
            elif debt_to_equity > 1:
                score -= 1
                reasons.append("High debt")

        # Dividend preference
        if div_yield and div_yield > 0:
            score += 1
            reasons.append("Pays dividend")

        # Positive earnings
        if eps and eps > 0:
            score += 1
        elif eps and eps < 0:
            score -= 1
            reasons.append("Negative earnings")

        return min(max(score, 0), 10), "; ".join(reasons[:4])

    @staticmethod
    def score_magic_formula(data: dict) -> tuple[int, str]:
        """
        Magic Formula (Joel Greenblatt)
        Ranks stocks by:
        1. Earnings Yield (EBIT / Enterprise Value) - high is good
        2. Return on Capital (EBIT / (Net Fixed Assets + Working Capital)) - high is good
        """
        score = 0
        reasons = []

        # Earnings Yield approximation (EBIT / Market Cap)
        # Using operating cash flow as EBIT proxy
        ocf = data.get("operating_cash_flow")
        market_cap = data.get("market_cap")
        fcf = data.get("free_cash_flow")
        pe = data.get("pe_ratio")

        if ocf and market_cap and market_cap > 0:
            earnings_yield = ocf / market_cap
            if earnings_yield > 0.15:
                score += 5
                reasons.append(f"Excellent earnings yield ({earnings_yield:.1%})")
            elif earnings_yield > 0.10:
                score += 4
                reasons.append(f"High earnings yield ({earnings_yield:.1%})")
            elif earnings_yield > 0.07:
                score += 3
                reasons.append(f"Good earnings yield ({earnings_yield:.1%})")
            elif earnings_yield > 0.05:
                score += 2
            elif earnings_yield > 0:
                score += 1
            else:
                reasons.append(f"Negative earnings yield ({earnings_yield:.1%})")
        elif pe and pe > 0:
            # Fallback: use E/P (earnings yield from P/E)
            earnings_yield = 1 / pe
            if earnings_yield > 0.10:
                score += 4
                reasons.append(f"High E/P yield ({earnings_yield:.1%})")
            elif earnings_yield > 0.07:
                score += 3
            elif earnings_yield > 0.05:
                score += 2

        # Return on Capital approximation (using ROE/ROA as proxy)
        roe = data.get("roe")
        roa = data.get("roa")

        if roe and roe > 0:
            if roe > 0.25:
                score += 5
                reasons.append(f"Excellent ROE ({roe:.1%})")
            elif roe > 0.15:
                score += 4
                reasons.append(f"High ROE ({roe:.1%})")
            elif roe > 0.10:
                score += 3
                reasons.append(f"Good ROE ({roe:.1%})")
            elif roe > 0.05:
                score += 2
        elif roe and roe < 0:
            reasons.append(f"Negative ROE ({roe:.1%})")

        if roa and roa > 0:
            if roa > 0.10:
                score += 2
                reasons.append(f"Strong ROA ({roa:.1%})")
            elif roa > 0.05:
                score += 1

        return min(max(score, 0), 10), "; ".join(reasons[:4])

    @staticmethod
    def score_piotroski_fscore(data: dict) -> tuple[int, str]:
        """
        Piotroski F-Score (0-9 scale)
        Measures financial strength based on 9 criteria:
        
        Profitability (4):
        - Positive ROA
        - Positive operating cash flow
        - ROA increasing
        - Operating cash flow > ROA
        
        Leverage (3):
        - Long-term debt decreasing
        - Current ratio increasing
        - No new shares issued
        
        Efficiency (2):
        - Gross margin increasing
        - Asset turnover increasing
        """
        score = 0
        reasons = []

        roa = data.get("roa")
        roe = data.get("roe")
        ocf = data.get("operating_cash_flow")
        fcf = data.get("free_cash_flow")
        current_ratio = data.get("current_ratio")
        debt_to_equity = data.get("debt_to_equity")
        profit_margin = data.get("profit_margin")

        # 1. Positive ROA
        if roa and roa > 0:
            score += 1
            reasons.append("Positive ROA")
        elif roa and roa < 0:
            reasons.append("Negative ROA")

        # 2. Positive operating cash flow
        if ocf and ocf > 0:
            score += 1
            reasons.append("Positive OCF")
        elif ocf and ocf < 0:
            reasons.append("Negative OCF")

        # 3. ROA improvement (approximation using profit margin as proxy)
        if profit_margin and profit_margin > 0:
            if profit_margin > 0.10:
                score += 1
                reasons.append("Good margin")
            elif profit_margin > 0.05:
                score += 1

        # 4. OCF > Net Income (using FCF as proxy)
        if fcf and fcf > 0 and roa and roa > 0:
            score += 1
            reasons.append("OCF > earnings")

        # 5. Low/Decreasing leverage
        if debt_to_equity and debt_to_equity >= 0:
            if debt_to_equity < 0.5:
                score += 1
                reasons.append("Low debt")
            elif debt_to_equity < 1:
                score += 1
            elif debt_to_equity > 2:
                reasons.append("High debt")

        # 6. Current ratio (liquidity)
        if current_ratio and current_ratio > 0:
            if current_ratio > 2:
                score += 1
                reasons.append("Strong liquidity")
            elif current_ratio > 1.5:
                score += 1
            elif current_ratio < 1:
                score -= 1
                reasons.append("Poor liquidity")

        # 7. No new shares (approximation - check if market cap is reasonable)
        market_cap = data.get("market_cap")
        if market_cap and market_cap > 0:
            score += 1  # Assume no major dilution

        # 8. Gross margin (using profit margin as proxy)
        if profit_margin and profit_margin > 0:
            if profit_margin > 0.15:
                score += 1
                reasons.append("High margin")
            elif profit_margin > 0.08:
                score += 1

        # 9. Asset turnover (using ROA/Profit margin as proxy)
        if roa and profit_margin and profit_margin > 0:
            asset_turnover = roa / profit_margin if profit_margin != 0 else 0
            if asset_turnover > 1:
                score += 1
                reasons.append("Good turnover")

        return min(max(score, 0), 9), f"F-Score: {score}/9; " + "; ".join(reasons[:4])

    @staticmethod
    def score_altman_zscore(data: dict) -> tuple[int, str]:
        """
        Altman Z-Score (Bankruptcy prediction)
        Z > 2.99 = Safe zone
        1.81 < Z < 2.99 = Grey zone
        Z < 1.81 = Distress zone
        
        Simplified version using available metrics.
        """
        score = 0
        reasons = []

        # Calculate approximate Z-score components
        working_capital_proxy = data.get("current_ratio")
        retained_earnings_proxy = data.get("roe")
        ebit_proxy = data.get("operating_cash_flow")
        market_cap = data.get("market_cap")
        book_value_proxy = data.get("pb_ratio")
        sales_proxy = data.get("revenue_growth")

        z_score = 0

        # X1: Working Capital / Total Assets (proxy: current ratio normalized)
        if working_capital_proxy and working_capital_proxy > 0:
            x1 = min(working_capital_proxy / 5, 1)  # Normalize
            z_score += 1.2 * x1

        # X2: Retained Earnings / Total Assets (proxy: ROE normalized)
        if retained_earnings_proxy and retained_earnings_proxy > 0:
            x2 = min(retained_earnings_proxy / 0.3, 1)
            z_score += 1.4 * x2

        # X3: EBIT / Total Assets (proxy: operating cash flow / market cap)
        if ebit_proxy and market_cap and market_cap > 0:
            x3 = ebit_proxy / market_cap
            z_score += 3.3 * min(x3 * 10, 1)

        # X4: Market Value of Equity / Book Value of Liabilities
        if book_value_proxy and book_value_proxy > 0:
            x4 = 1 / book_value_proxy if book_value_proxy < 1 else book_value_proxy
            z_score += 0.6 * min(x4, 2)

        # X5: Sales / Total Assets (proxy: revenue growth)
        if sales_proxy and sales_proxy > 0:
            x5 = min(sales_proxy / 0.3, 1)
            z_score += 1.0 * x5

        # Score based on Z-score zones
        if z_score > 2.5:
            score = 10
            reasons.append(f"Safe zone (Z≈{z_score:.2f})")
        elif z_score > 1.8:
            score = 7
            reasons.append(f"Grey zone (Z≈{z_score:.2f})")
        elif z_score > 1.0:
            score = 4
            reasons.append(f"Warning zone (Z≈{z_score:.2f})")
        else:
            score = 1
            reasons.append(f"Distress zone (Z≈{z_score:.2f})")

        return score, "; ".join(reasons)

    @staticmethod
    def score_growth_model(data: dict) -> tuple[int, str]:
        """
        Growth Investing Model
        Focuses on companies with strong, sustainable growth.
        
        Criteria:
        - Revenue growth > 15%
        - Earnings growth > 15%
        - Consistent growth trajectory
        - Reinvestment potential
        """
        score = 0
        reasons = []

        rev_growth = data.get("revenue_growth")
        earn_growth = data.get("earnings_growth")
        roe = data.get("roe")
        profit_margin = data.get("profit_margin")

        # Revenue Growth
        if rev_growth and rev_growth > 0:
            if rev_growth > 0.30:
                score += 4
                reasons.append(f"Exceptional revenue growth ({rev_growth:.1%})")
            elif rev_growth > 0.20:
                score += 3
                reasons.append(f"Strong revenue growth ({rev_growth:.1%})")
            elif rev_growth > 0.15:
                score += 2
                reasons.append(f"Good revenue growth ({rev_growth:.1%})")
            elif rev_growth > 0.10:
                score += 1
                reasons.append(f"Moderate revenue growth ({rev_growth:.1%})")
            else:
                reasons.append(f"Low revenue growth ({rev_growth:.1%})")
        elif rev_growth and rev_growth < 0:
            score -= 1
            reasons.append(f"Declining revenue ({rev_growth:.1%})")

        # Earnings Growth
        if earn_growth and earn_growth > 0:
            if earn_growth > 0.30:
                score += 4
                reasons.append(f"Exceptional earnings growth ({earn_growth:.1%})")
            elif earn_growth > 0.20:
                score += 3
                reasons.append(f"Strong earnings growth ({earn_growth:.1%})")
            elif earn_growth > 0.15:
                score += 2
                reasons.append(f"Good earnings growth ({earn_growth:.1%})")
            elif earn_growth > 0.10:
                score += 1
            else:
                reasons.append(f"Low earnings growth ({earn_growth:.1%})")
        elif earn_growth and earn_growth < 0:
            score -= 1
            reasons.append(f"Declining earnings ({earn_growth:.1%})")

        # ROE (sustainable growth indicator)
        if roe and roe > 0:
            if roe > 0.20:
                score += 2
                reasons.append(f"High ROE ({roe:.1%})")
            elif roe > 0.15:
                score += 1

        # Profit Margin (quality of growth)
        if profit_margin and profit_margin > 0:
            if profit_margin > 0.15:
                score += 1
                reasons.append("Quality growth")

        return min(max(score, 0), 10), "; ".join(reasons[:4])

    @staticmethod
    def score_dividend_discount(data: dict) -> tuple[int, str]:
        """
        Dividend Discount Model (DDM)
        Values stocks based on present value of future dividends.
        
        Intrinsic Value = D1 / (r - g)
        Where:
        - D1 = Next year's dividend
        - r = Required rate of return
        - g = Dividend growth rate
        
        Higher score = appears undervalued by DDM
        """
        score = 0
        reasons = []

        div_yield = data.get("dividend_yield")
        payout_ratio = data.get("payout_ratio")
        rev_growth = data.get("revenue_growth")
        earn_growth = data.get("earnings_growth")
        price = data.get("price")
        eps = data.get("eps")

        # Must have dividend
        if not div_yield or div_yield <= 0:
            return 0, "No dividend"

        # Dividend Yield scoring
        if div_yield > 0.05:
            score += 3
            reasons.append(f"High yield ({div_yield:.2%})")
        elif div_yield > 0.03:
            score += 2
            reasons.append(f"Good yield ({div_yield:.2%})")
        elif div_yield > 0.02:
            score += 1
            reasons.append(f"Moderate yield ({div_yield:.2%})")
        else:
            reasons.append(f"Low yield ({div_yield:.2%})")

        # Payout Ratio (sustainability)
        if payout_ratio and payout_ratio > 0:
            if payout_ratio < 0.4:
                score += 3
                reasons.append("Very sustainable payout")
            elif payout_ratio < 0.6:
                score += 2
                reasons.append("Sustainable payout")
            elif payout_ratio < 0.8:
                score += 1
            elif payout_ratio > 1:
                score -= 2
                reasons.append("Unsustainable payout")

        # Growth rate for DDM (using earnings/revenue growth as proxy)
        growth_rate = 0
        if earn_growth and earn_growth > 0:
            growth_rate = earn_growth
        elif rev_growth and rev_growth > 0:
            growth_rate = rev_growth * 0.5  # Conservative

        if growth_rate > 0:
            if growth_rate > 0.10:
                score += 2
                reasons.append(f"Good dividend growth potential ({growth_rate:.1%})")
            elif growth_rate > 0.05:
                score += 1
        elif growth_rate < 0:
            score -= 1
            reasons.append("Negative growth")

        # Dividend safety check
        if eps and eps > 0 and div_yield:
            dividend_per_share = price * div_yield if price else 0
            if dividend_per_share < eps * 0.6:
                score += 2
                reasons.append("Safe dividend")

        return min(max(score, 0), 10), "; ".join(reasons[:4])

    @staticmethod
    def score_momentum_strategy(data: dict) -> tuple[int, str]:
        """
        Momentum Strategy
        Buys stocks that are trending upward, sells those trending down.
        
        Measures:
        - 12-month price momentum
        - 6-month price momentum
        - Price vs 52-week high
        - Price vs moving averages
        """
        score = 0
        reasons = []

        price = data.get("price")
        high_52 = data.get("52_week_high")
        low_52 = data.get("52_week_low")
        avg_50 = data.get("50_day_avg")
        avg_200 = data.get("200_day_avg")
        year_ago = data.get("year_ago_price")
        month_6_ago = data.get("6_month_ago_price")
        month_3_ago = data.get("3_month_ago_price")

        # 12-month momentum
        if price and year_ago and year_ago > 0:
            momentum_12m = (price - year_ago) / year_ago
            if momentum_12m > 0.50:
                score += 4
                reasons.append(f"Excellent 12M momentum ({momentum_12m:.1%})")
            elif momentum_12m > 0.25:
                score += 3
                reasons.append(f"Strong 12M momentum ({momentum_12m:.1%})")
            elif momentum_12m > 0.10:
                score += 2
                reasons.append(f"Good 12M momentum ({momentum_12m:.1%})")
            elif momentum_12m > 0:
                score += 1
            else:
                reasons.append(f"Negative 12M momentum ({momentum_12m:.1%})")

        # 6-month momentum
        if price and month_6_ago and month_6_ago > 0:
            momentum_6m = (price - month_6_ago) / month_6_ago
            if momentum_6m > 0.20:
                score += 2
                reasons.append(f"Strong 6M momentum ({momentum_6m:.1%})")
            elif momentum_6m > 0.10:
                score += 1
            elif momentum_6m < -0.10:
                score -= 1

        # 3-month momentum (recent trend)
        if price and month_3_ago and month_3_ago > 0:
            momentum_3m = (price - month_3_ago) / month_3_ago
            if momentum_3m > 0.10:
                score += 2
                reasons.append(f"Positive 3M trend ({momentum_3m:.1%})")
            elif momentum_3m < -0.10:
                score -= 1

        # Position in 52-week range
        if price and high_52 and low_52 and high_52 != low_52:
            position = (price - low_52) / (high_52 - low_52)
            if position > 0.8:
                score += 2
                reasons.append("Near 52-week high")
            elif position > 0.6:
                score += 1
            elif position < 0.2:
                score -= 1
                reasons.append("Near 52-week low")

        # Price vs 50-day MA
        if price and avg_50:
            if price > avg_50 * 1.05:
                score += 1
                reasons.append("Above 50-day MA")
            elif price < avg_50 * 0.95:
                score -= 1

        # Price vs 200-day MA
        if price and avg_200:
            if price > avg_200 * 1.05:
                score += 1
                reasons.append("Above 200-day MA")
            elif price < avg_200 * 0.95:
                score -= 1

        return min(max(score, 0), 10), "; ".join(reasons[:4])

    @staticmethod
    def score_quality_model(data: dict) -> tuple[int, str]:
        """
        Quality Investing Model
        Focuses on companies with superior fundamentals.
        
        Criteria:
        - High ROE (>15%)
        - High ROA (>8%)
        - Stable/improving margins
        - Low debt
        - Strong cash flow
        - Consistent earnings
        """
        score = 0
        reasons = []

        roe = data.get("roe")
        roa = data.get("roa")
        debt_to_equity = data.get("debt_to_equity")
        current_ratio = data.get("current_ratio")
        profit_margin = data.get("profit_margin")
        fcf = data.get("free_cash_flow")
        ocf = data.get("operating_cash_flow")

        # ROE scoring
        if roe and roe > 0:
            if roe > 0.25:
                score += 3
                reasons.append(f"Excellent ROE ({roe:.1%})")
            elif roe > 0.20:
                score += 2
                reasons.append(f"High ROE ({roe:.1%})")
            elif roe > 0.15:
                score += 1
                reasons.append(f"Good ROE ({roe:.1%})")
        elif roe and roe < 0:
            reasons.append(f"Negative ROE ({roe:.1%})")

        # ROA scoring
        if roa and roa > 0:
            if roa > 0.12:
                score += 2
                reasons.append(f"Excellent ROA ({roa:.1%})")
            elif roa > 0.08:
                score += 1
                reasons.append(f"Good ROA ({roa:.1%})")
            elif roa > 0.05:
                score += 1
        elif roa and roa < 0:
            reasons.append(f"Negative ROA ({roa:.1%})")

        # Debt to Equity
        if debt_to_equity and debt_to_equity >= 0:
            if debt_to_equity < 0.3:
                score += 2
                reasons.append("Very low debt")
            elif debt_to_equity < 0.5:
                score += 1
                reasons.append("Low debt")
            elif debt_to_equity < 1:
                score += 1
            elif debt_to_equity > 2:
                score -= 1
                reasons.append("High debt")

        # Current Ratio
        if current_ratio and current_ratio > 0:
            if current_ratio > 2:
                score += 1
                reasons.append("Strong liquidity")
            elif current_ratio > 1.5:
                score += 1
            elif current_ratio < 1:
                score -= 1
                reasons.append("Poor liquidity")

        # Profit Margin
        if profit_margin and profit_margin > 0:
            if profit_margin > 0.20:
                score += 2
                reasons.append(f"Excellent margin ({profit_margin:.1%})")
            elif profit_margin > 0.15:
                score += 1
                reasons.append(f"High margin ({profit_margin:.1%})")
            elif profit_margin > 0.10:
                score += 1
        elif profit_margin and profit_margin < 0:
            reasons.append(f"Negative margin ({profit_margin:.1%})")

        # Free Cash Flow
        if fcf and fcf > 0:
            score += 1
            reasons.append("Positive FCF")
        elif fcf and fcf < 0:
            reasons.append("Negative FCF")

        return min(max(score, 0), 10), "; ".join(reasons[:4])

    @staticmethod
    def score_fama_french(data: dict) -> tuple[int, str]:
        """
        Fama-French 3-Factor Model
        Based on three factors:
        1. Market Risk (Beta)
        2. Size (SMB - Small Minus Big)
        3. Value (HML - High Minus Low book-to-market)
        
        Scores based on exposure to return-premium factors.
        """
        score = 0
        reasons = []

        beta = data.get("beta")
        market_cap = data.get("market_cap")
        pb_ratio = data.get("pb_ratio")
        pe_ratio = data.get("pe_ratio")

        # Size Factor (SMB) - Small caps have premium
        if market_cap and market_cap > 0:
            if market_cap < 500_000_000:  # < $500M
                score += 4
                reasons.append(f"Micro cap (${market_cap/1e6:.0f}M)")
            elif market_cap < 2_000_000_000:  # < $2B
                score += 3
                reasons.append(f"Small cap (${market_cap/1e6:.0f}M)")
            elif market_cap < 10_000_000_000:  # < $10B
                score += 2
                reasons.append(f"Mid cap (${market_cap/1e6:.0f}M)")
            elif market_cap < 50_000_000_000:  # < $50B
                score += 1
                reasons.append(f"Large cap (${market_cap/1e9:.0f}B)")
            else:
                reasons.append(f"Mega cap (${market_cap/1e9:.0f}B)")

        # Value Factor (HML) - High book-to-market (low P/B) has premium
        if pb_ratio and pb_ratio > 0:
            if pb_ratio < 1:
                score += 3
                reasons.append(f"Deep value (P/B {pb_ratio:.1f})")
            elif pb_ratio < 1.5:
                score += 2
                reasons.append(f"Value (P/B {pb_ratio:.1f})")
            elif pb_ratio < 2.5:
                score += 1
                reasons.append(f"Fair value (P/B {pb_ratio:.1f})")
            elif pb_ratio > 4:
                reasons.append(f"Growth stock (P/B {pb_ratio:.1f})")

        # Market Factor - Beta exposure
        if beta and beta > 0:
            # Moderate beta is often preferred
            if 0.8 <= beta <= 1.2:
                score += 2
                reasons.append(f"Market beta ({beta:.2f})")
            elif 0.5 <= beta < 0.8:
                score += 1
                reasons.append(f"Low beta ({beta:.2f})")
            elif 1.2 < beta <= 1.5:
                score += 1
                reasons.append(f"High beta ({beta:.2f})")
            elif beta < 0.5:
                reasons.append(f"Very low beta ({beta:.2f})")
            elif beta > 1.5:
                reasons.append(f"Very high beta ({beta:.2f})")

        # P/E as additional value indicator
        if pe_ratio and pe_ratio > 0:
            if pe_ratio < 12:
                score += 1
                reasons.append(f"Low P/E ({pe_ratio:.1f})")
            elif pe_ratio < 18:
                score += 1

        return min(max(score, 0), 10), "; ".join(reasons[:4])

    @staticmethod
    def score_mean_reversion(data: dict) -> tuple[int, str]:
        """
        Mean Reversion Strategy
        Assumes prices revert to their mean over time.
        Buys when price is significantly below moving averages or historical norms.
        
        Signals:
        - Price far below 52-week high
        - Price below 200-day MA (oversold)
        - Low RSI conditions (approximated)
        - Price below intrinsic value estimates
        """
        score = 0
        reasons = []

        price = data.get("price")
        high_52 = data.get("52_week_high")
        low_52 = data.get("52_week_low")
        avg_50 = data.get("50_day_avg")
        avg_200 = data.get("200_day_avg")
        pe_ratio = data.get("pe_ratio")
        pb_ratio = data.get("pb_ratio")

        # Distance from 52-week high (oversold = opportunity)
        if price and high_52 and high_52 > 0:
            drawdown = (high_52 - price) / high_52
            if drawdown > 0.40:
                score += 4
                reasons.append(f"Deeply oversold (-{drawdown:.1%} from high)")
            elif drawdown > 0.25:
                score += 3
                reasons.append(f"Oversold (-{drawdown:.1%} from high)")
            elif drawdown > 0.15:
                score += 2
                reasons.append(f"Below high (-{drawdown:.1%})")
            elif drawdown < 0.10:
                reasons.append("Near highs")

        # Distance from 52-week low (not too beaten up)
        if price and low_52 and low_52 > 0:
            from_low = (price - low_52) / low_52
            if from_low > 0.50:
                score += 1
                reasons.append("Recovering from lows")
            elif from_low < 0.10:
                score -= 1
                reasons.append("Near 52-week low")

        # Price vs 200-day MA (mean reversion signal)
        if price and avg_200:
            deviation = (price - avg_200) / avg_200
            if deviation < -0.20:
                score += 4
                reasons.append(f"Far below 200-day MA ({deviation:.1%})")
            elif deviation < -0.10:
                score += 3
                reasons.append(f"Below 200-day MA ({deviation:.1%})")
            elif deviation < 0:
                score += 2
                reasons.append(f"Slightly below 200-day MA ({deviation:.1%})")
            elif deviation > 0.30:
                score -= 1
                reasons.append(f"Extended above mean ({deviation:.1%})")

        # Price vs 50-day MA
        if price and avg_50:
            deviation_50 = (price - avg_50) / avg_50
            if deviation_50 < -0.15:
                score += 2
                reasons.append("Below 50-day MA")
            elif deviation_50 > 0.20:
                score -= 1

        # Valuation mean reversion (low P/E, P/B suggests reversion potential)
        if pe_ratio and pe_ratio > 0:
            if pe_ratio < 10:
                score += 2
                reasons.append(f"Low P/E ({pe_ratio:.1f})")
            elif pe_ratio < 15:
                score += 1

        if pb_ratio and pb_ratio > 0:
            if pb_ratio < 1:
                score += 1
                reasons.append(f"P/B < 1 ({pb_ratio:.1f})")

        return min(max(score, 0), 10), "; ".join(reasons[:4])

    @classmethod
    def analyze_stock(cls, data: dict) -> dict:
        """
        Run all 10 strategies on a stock and return scores.
        """
        strategies = [
            ("benjamin_graham", cls.score_benjamin_graham),
            ("magic_formula", cls.score_magic_formula),
            ("piotroski_fscore", cls.score_piotroski_fscore),
            ("altman_zscore", cls.score_altman_zscore),
            ("growth_model", cls.score_growth_model),
            ("dividend_discount", cls.score_dividend_discount),
            ("momentum_strategy", cls.score_momentum_strategy),
            ("quality_model", cls.score_quality_model),
            ("fama_french", cls.score_fama_french),
            ("mean_reversion", cls.score_mean_reversion),
        ]

        results = {}
        total_score = 0

        for name, func in strategies:
            score, reason = func(data)
            results[name] = {"score": score, "reason": reason}
            total_score += score

        results["total_score"] = total_score
        results["average_score"] = round(total_score / 10, 2)

        return results


# Strategy display names for UI
STRATEGY_NAMES = {
    "benjamin_graham": "Benjamin Graham",
    "magic_formula": "Magic Formula",
    "piotroski_fscore": "Piotroski F-Score",
    "altman_zscore": "Altman Z-Score",
    "growth_model": "Growth Model",
    "dividend_discount": "Dividend Discount",
    "momentum_strategy": "Momentum",
    "quality_model": "Quality Model",
    "fama_french": "Fama-French 3-Factor",
    "mean_reversion": "Mean Reversion",
}
