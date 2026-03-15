"""
100-Bagger Investment Strategy Analyzers Module

Implements Peter Lynch's investment philosophy and other 100-bagger strategies:

Models:
    1. Lynch Score - PEG ratio, growth consistency, simple business
    2. Growth Score - Revenue/earnings growth rate, sustainability
    3. Value Score - P/E, P/B, P/S relative to growth
    4. Financial Health - Debt levels, cash position, current ratio
    5. Profitability Score - Margins, ROE, ROIC
    6. Moat Score - Competitive advantages, market position
    7. Insider Score - Insider ownership, buying activity
    8. Momentum Score - Price trends, relative strength
    9. Small-Cap Potential - Market cap room to grow
    10. Lynch's "Story" Score - Understandable business model

Scoring System:
    Each model scores stocks from 0-10:
    - 8-10: Strong 100-bagger potential (🟢)
    - 5-7: Moderate potential (🟡)
    - 0-4: Low potential (🔴)

Example:
    >>> from bagger_src.strategies import HundredBaggerStrategies
    >>> analysis = HundredBaggerStrategies.analyze_stock(stock_data)
    >>> print(f"100-Bagger Score: {analysis['total_score']}/100")
"""

from typing import Optional


# Strategy names for display
STRATEGY_NAMES = {
    "lynch_score": "Lynch Score (PEG + Growth)",
    "growth_score": "Growth Score",
    "value_score": "Value Score",
    "financial_health": "Financial Health",
    "profitability_score": "Profitability Score",
    "moat_score": "Moat Score",
    "insider_score": "Insider Ownership",
    "momentum_score": "Momentum Score",
    "small_cap_potential": "Small-Cap Potential",
    "business_story": "Business Story",
}


class HundredBaggerStrategies:
    """
    Analyzes stocks using Peter Lynch's 100-bagger criteria.

    Based on principles from:
    - "One Up on Wall Street" (1989)
    - "Beating the Street" (1993)
    - "Learn to Earn" (1995)
    """

    @staticmethod
    def score_lynch(data: dict) -> tuple[int, str]:
        """
        Peter Lynch Score - The core 100-bagger criteria.

        Lynch's key metrics:
        - PEG Ratio < 1.0 (ideal), < 1.5 (acceptable)
        - Earnings growth > 15% annually
        - Consistent growth trajectory
        - Simple, understandable business
        """
        score = 0
        reasons = []

        peg = data.get("peg_ratio")
        earnings_growth = data.get("earnings_growth")
        pe_ratio = data.get("pe_ratio")

        # PEG Ratio (Lynch's favorite metric)
        if peg and peg > 0:
            if peg < 0.5:
                score += 5
                reasons.append(f"Excellent PEG ({peg:.2f})")
            elif peg < 1.0:
                score += 4
                reasons.append(f"Great PEG ({peg:.2f})")
            elif peg < 1.5:
                score += 3
                reasons.append(f"Good PEG ({peg:.2f})")
            elif peg < 2.0:
                score += 2
                reasons.append(f"Fair PEG ({peg:.2f})")
            elif peg < 3.0:
                score += 1
                reasons.append(f"High PEG ({peg:.2f})")
            else:
                reasons.append(f"Very high PEG ({peg:.2f})")
        elif pe_ratio and pe_ratio > 0 and earnings_growth and earnings_growth > 0:
            # Calculate PEG if not available
            peg_calc = pe_ratio / (earnings_growth * 100)
            if peg_calc < 1.0:
                score += 4
                reasons.append(f"Calculated PEG ({peg_calc:.2f})")
            elif peg_calc < 1.5:
                score += 3
                reasons.append(f"Calculated PEG ({peg_calc:.2f})")

        # Earnings Growth (Lynch wants 15-25% annually)
        if earnings_growth and earnings_growth > 0:
            if earnings_growth > 0.30:
                score += 3
                reasons.append(f"Exceptional growth ({earnings_growth:.1%})")
            elif earnings_growth > 0.20:
                score += 2
                reasons.append(f"Strong growth ({earnings_growth:.1%})")
            elif earnings_growth > 0.15:
                score += 1
                reasons.append(f"Good growth ({earnings_growth:.1%})")
            elif earnings_growth < 0:
                score -= 1
                reasons.append(f"Declining earnings ({earnings_growth:.1%})")

        # Reasonable P/E (Lynch avoids overpaying)
        if pe_ratio and pe_ratio > 0:
            if pe_ratio < 10:
                score += 2
                reasons.append(f"Low P/E ({pe_ratio:.1f})")
            elif pe_ratio < 20:
                score += 1
                reasons.append(f"Fair P/E ({pe_ratio:.1f})")
            elif pe_ratio > 40:
                score -= 1
                reasons.append(f"Very high P/E ({pe_ratio:.1f})")

        return min(max(score, 0), 10), "; ".join(reasons[:4])

    @staticmethod
    def score_growth(data: dict) -> tuple[int, str]:
        """
        Growth Score - Revenue and earnings growth sustainability.

        100-baggers need consistent, sustainable growth over many years.
        """
        score = 0
        reasons = []

        revenue_growth = data.get("revenue_growth")
        earnings_growth = data.get("earnings_growth")
        revenue_per_share_growth = data.get("revenue_per_share_growth")

        # Revenue Growth (top-line growth is crucial)
        if revenue_growth and revenue_growth > 0:
            if revenue_growth > 0.30:
                score += 4
                reasons.append(f"Exceptional revenue growth ({revenue_growth:.1%})")
            elif revenue_growth > 0.20:
                score += 3
                reasons.append(f"Strong revenue growth ({revenue_growth:.1%})")
            elif revenue_growth > 0.15:
                score += 2
                reasons.append(f"Good revenue growth ({revenue_growth:.1%})")
            elif revenue_growth > 0.10:
                score += 1
                reasons.append(f"Moderate revenue growth ({revenue_growth:.1%})")
            else:
                reasons.append(f"Low revenue growth ({revenue_growth:.1%})")
        elif revenue_growth and revenue_growth < 0:
            score -= 2
            reasons.append(f"Declining revenue ({revenue_growth:.1%})")

        # Earnings Growth (bottom-line must follow)
        if earnings_growth and earnings_growth > 0:
            if earnings_growth > 0.25:
                score += 4
                reasons.append(f"Exceptional earnings growth ({earnings_growth:.1%})")
            elif earnings_growth > 0.15:
                score += 3
                reasons.append(f"Strong earnings growth ({earnings_growth:.1%})")
            elif earnings_growth > 0.10:
                score += 2
                reasons.append(f"Good earnings growth ({earnings_growth:.1%})")
            elif earnings_growth > 0:
                score += 1
                reasons.append(f"Positive earnings growth ({earnings_growth:.1%})")
        elif earnings_growth and earnings_growth < 0:
            score -= 1
            reasons.append(f"Declining earnings ({earnings_growth:.1%})")

        # Revenue per Share Growth (accounts for dilution)
        if revenue_per_share_growth and revenue_per_share_growth > 0:
            if revenue_per_share_growth > 0.15:
                score += 2
                reasons.append("Strong per-share growth")
            elif revenue_per_share_growth > 0.10:
                score += 1
                reasons.append("Good per-share growth")

        return min(max(score, 0), 10), "; ".join(reasons[:4])

    @staticmethod
    def score_value(data: dict) -> tuple[int, str]:
        """
        Value Score - Is the stock reasonably priced?

        Lynch looked for "growth at a reasonable price" (GARP).
        """
        score = 0
        reasons = []

        pe_ratio = data.get("pe_ratio")
        pb_ratio = data.get("pb_ratio")
        ps_ratio = data.get("ps_ratio")
        peg_ratio = data.get("peg_ratio")

        # P/E Ratio
        if pe_ratio and pe_ratio > 0:
            if pe_ratio < 10:
                score += 3
                reasons.append(f"Very low P/E ({pe_ratio:.1f})")
            elif pe_ratio < 15:
                score += 2
                reasons.append(f"Low P/E ({pe_ratio:.1f})")
            elif pe_ratio < 25:
                score += 1
                reasons.append(f"Fair P/E ({pe_ratio:.1f})")
            elif pe_ratio > 50:
                score -= 2
                reasons.append(f"Very high P/E ({pe_ratio:.1f})")

        # P/B Ratio (important for asset-heavy businesses)
        if pb_ratio and pb_ratio > 0:
            if pb_ratio < 1.5:
                score += 2
                reasons.append(f"Low P/B ({pb_ratio:.1f})")
            elif pb_ratio < 3:
                score += 1
                reasons.append(f"Fair P/B ({pb_ratio:.1f})")
            elif pb_ratio > 10:
                reasons.append(f"Very high P/B ({pb_ratio:.1f})")

        # P/S Ratio (good for early-stage growth)
        if ps_ratio and ps_ratio > 0:
            if ps_ratio < 2:
                score += 2
                reasons.append(f"Reasonable P/S ({ps_ratio:.1f})")
            elif ps_ratio < 5:
                score += 1
                reasons.append(f"Fair P/S ({ps_ratio:.1f})")
            elif ps_ratio > 15:
                score -= 1
                reasons.append(f"High P/S ({ps_ratio:.1f})")

        return min(max(score, 0), 10), "; ".join(reasons[:4])

    @staticmethod
    def score_financial_health(data: dict) -> tuple[int, str]:
        """
        Financial Health Score - Balance sheet strength.

        Lynch avoided companies with dangerous debt levels.
        """
        score = 0
        reasons = []

        debt_to_equity = data.get("debt_to_equity")
        current_ratio = data.get("current_ratio")
        quick_ratio = data.get("quick_ratio")
        total_debt = data.get("total_debt")
        total_cash = data.get("total_cash")

        # Debt to Equity (lower is better)
        if debt_to_equity is not None and debt_to_equity >= 0:
            if debt_to_equity < 0.3:
                score += 4
                reasons.append(f"Very low debt (D/E: {debt_to_equity:.2f})")
            elif debt_to_equity < 0.5:
                score += 3
                reasons.append(f"Low debt (D/E: {debt_to_equity:.2f})")
            elif debt_to_equity < 1.0:
                score += 2
                reasons.append(f"Moderate debt (D/E: {debt_to_equity:.2f})")
            elif debt_to_equity < 2.0:
                score += 1
                reasons.append(f"Higher debt (D/E: {debt_to_equity:.2f})")
            else:
                score -= 2
                reasons.append(f"High debt (D/E: {debt_to_equity:.2f})")
        else:
            reasons.append("No debt data")

        # Current Ratio (liquidity)
        if current_ratio and current_ratio > 0:
            if current_ratio > 2:
                score += 2
                reasons.append("Strong liquidity")
            elif current_ratio > 1.5:
                score += 1
                reasons.append("Good liquidity")
            elif current_ratio < 1:
                score -= 2
                reasons.append("Weak liquidity")

        # Quick Ratio (more stringent liquidity)
        if quick_ratio and quick_ratio > 0:
            if quick_ratio > 1.5:
                score += 2
                reasons.append("Excellent quick ratio")
            elif quick_ratio > 1:
                score += 1
                reasons.append("Good quick ratio")
            elif quick_ratio < 0.5:
                score -= 1
                reasons.append("Weak quick ratio")

        # Net Cash Position
        if total_cash and total_debt and total_cash > 0:
            net_debt = total_debt - total_cash
            if net_debt < 0:
                score += 2
                reasons.append("Net cash position")
            elif net_debt < total_cash * 0.5:
                score += 1
                reasons.append("Manageable net debt")

        return min(max(score, 0), 10), "; ".join(reasons[:4])

    @staticmethod
    def score_profitability(data: dict) -> tuple[int, str]:
        """
        Profitability Score - How well does the company make money?

        100-baggers typically have expanding margins and high returns on capital.
        """
        score = 0
        reasons = []

        profit_margin = data.get("profit_margin")
        gross_margin = data.get("gross_margin")
        operating_margin = data.get("operating_margin")
        roe = data.get("roe")
        roic = data.get("roic")

        # Profit Margin
        if profit_margin and profit_margin > 0:
            if profit_margin > 0.25:
                score += 3
                reasons.append(f"Excellent margin ({profit_margin:.1%})")
            elif profit_margin > 0.15:
                score += 2
                reasons.append(f"Good margin ({profit_margin:.1%})")
            elif profit_margin > 0.08:
                score += 1
                reasons.append(f"Moderate margin ({profit_margin:.1%})")
            elif profit_margin < 0:
                score -= 2
                reasons.append(f"Negative margin ({profit_margin:.1%})")

        # Gross Margin (indicates pricing power)
        if gross_margin and gross_margin > 0:
            if gross_margin > 0.60:
                score += 3
                reasons.append(f"High gross margin ({gross_margin:.1%})")
            elif gross_margin > 0.40:
                score += 2
                reasons.append(f"Good gross margin ({gross_margin:.1%})")
            elif gross_margin > 0.25:
                score += 1
                reasons.append(f"Fair gross margin ({gross_margin:.1%})")

        # Operating Margin
        if operating_margin and operating_margin > 0:
            if operating_margin > 0.20:
                score += 2
                reasons.append(f"Strong operating margin ({operating_margin:.1%})")
            elif operating_margin > 0.10:
                score += 1
                reasons.append(f"Good operating margin ({operating_margin:.1%})")

        # ROE (return on equity)
        if roe and roe > 0:
            if roe > 0.25:
                score += 2
                reasons.append(f"Excellent ROE ({roe:.1%})")
            elif roe > 0.15:
                score += 1
                reasons.append(f"Good ROE ({roe:.1%})")
            elif roe > 0.30:
                score += 1
                reasons.append(f"Outstanding ROE ({roe:.1%})")

        # ROIC (return on invested capital - Lynch's favorite)
        if roic and roic > 0:
            if roic > 0.20:
                score += 2
                reasons.append(f"Excellent ROIC ({roic:.1%})")
            elif roic > 0.12:
                score += 1
                reasons.append(f"Good ROIC ({roic:.1%})")

        return min(max(score, 0), 10), "; ".join(reasons[:4])

    @staticmethod
    def score_moat(data: dict) -> tuple[int, str]:
        """
        Moat Score - Competitive advantages.

        Based on Buffett/Lynch principles of durable competitive advantages.
        """
        score = 0
        reasons = []

        gross_margin = data.get("gross_margin")
        operating_margin = data.get("operating_margin")
        roic = data.get("roic")
        sector = data.get("sector", "")
        industry = data.get("industry", "")

        # High Gross Margin indicates pricing power
        if gross_margin and gross_margin > 0:
            if gross_margin > 0.70:
                score += 4
                reasons.append("Strong pricing power")
            elif gross_margin > 0.50:
                score += 3
                reasons.append("Good pricing power")
            elif gross_margin > 0.35:
                score += 2
                reasons.append("Moderate pricing power")

        # High ROIC indicates moat
        if roic and roic > 0:
            if roic > 0.25:
                score += 3
                reasons.append("High returns on capital")
            elif roic > 0.15:
                score += 2
                reasons.append("Good returns on capital")

        # Certain sectors have natural moats
        moat_industries = ["Software", "Semiconductor", "Biotechnology", 
                          "Medical Devices", "Specialty Chemical", "Luxury"]
        if any(ind in sector or ind in industry for ind in moat_industries):
            score += 2
            reasons.append("Moat-friendly industry")

        # Consistent operating margin (proxy for stability)
        if operating_margin and operating_margin > 0.15:
            score += 1
            reasons.append("Stable operations")

        return min(max(score, 0), 10), "; ".join(reasons[:4])

    @staticmethod
    def score_insider(data: dict) -> tuple[int, str]:
        """
        Insider Score - Management alignment with shareholders.

        Lynch loved companies where insiders owned significant stock.
        """
        score = 0
        reasons = []

        insider_ownership = data.get("insider_ownership")
        institutional_ownership = data.get("institutional_ownership")

        # Insider Ownership (higher is better, up to a point)
        if insider_ownership and insider_ownership > 0:
            if insider_ownership > 0.30:
                score += 5
                reasons.append(f"Excellent insider ownership ({insider_ownership:.1%})")
            elif insider_ownership > 0.20:
                score += 4
                reasons.append(f"High insider ownership ({insider_ownership:.1%})")
            elif insider_ownership > 0.10:
                score += 3
                reasons.append(f"Good insider ownership ({insider_ownership:.1%})")
            elif insider_ownership > 0.05:
                score += 2
                reasons.append(f"Moderate insider ownership ({insider_ownership:.1%})")
            elif insider_ownership > 0.01:
                score += 1
                reasons.append(f"Low insider ownership ({insider_ownership:.1%})")
        else:
            reasons.append("No insider ownership data")

        # Institutional Ownership (some is good, too much can be bad)
        if institutional_ownership and institutional_ownership > 0:
            if 0.30 <= institutional_ownership <= 0.80:
                score += 2
                reasons.append("Good institutional support")
            elif institutional_ownership > 0.90:
                reasons.append("Very high institutional ownership")
            elif institutional_ownership < 0.10:
                reasons.append("Low institutional interest")

        return min(max(score, 0), 10), "; ".join(reasons[:4])

    @staticmethod
    def score_momentum(data: dict) -> tuple[int, str]:
        """
        Momentum Score - Price trends and relative strength.

        Lynch bought stocks going up, not down (contrary to value investors).
        """
        score = 0
        reasons = []

        price = data.get("price")
        high_52 = data.get("52_week_high")
        low_52 = data.get("52_week_low")
        avg_50 = data.get("50_day_avg")
        avg_200 = data.get("200_day_avg")
        year_ago = data.get("year_ago_price")

        # Position in 52-week range (Lynch liked stocks near highs)
        if price and high_52 and low_52 and high_52 != low_52:
            position = (price - low_52) / (high_52 - low_52)
            if position > 0.80:
                score += 3
                reasons.append("Near 52-week high")
            elif position > 0.60:
                score += 2
                reasons.append("Strong relative position")
            elif position > 0.40:
                score += 1
                reasons.append("Mid-range position")
            elif position < 0.20:
                score -= 1
                reasons.append("Near 52-week low")

        # Price vs 50-day MA
        if price and avg_50:
            if price > avg_50 * 1.05:
                score += 2
                reasons.append("Above 50-day MA")
            elif price < avg_50 * 0.95:
                score -= 1
                reasons.append("Below 50-day MA")

        # Price vs 200-day MA (long-term trend)
        if price and avg_200:
            if price > avg_200 * 1.05:
                score += 2
                reasons.append("Above 200-day MA")
            elif price < avg_200 * 0.95:
                score -= 1
                reasons.append("Below 200-day MA")

        # 12-month price performance
        if price and year_ago and year_ago > 0:
            performance = (price - year_ago) / year_ago
            if performance > 0.50:
                score += 2
                reasons.append(f"Strong 12M performance ({performance:.1%})")
            elif performance > 0.20:
                score += 1
                reasons.append(f"Positive 12M performance ({performance:.1%})")
            elif performance < -0.30:
                score -= 1
                reasons.append(f"Weak 12M performance ({performance:.1%})")

        return min(max(score, 0), 10), "; ".join(reasons[:4])

    @staticmethod
    def score_small_cap_potential(data: dict) -> tuple[int, str]:
        """
        Small-Cap Potential - Room to grow.

        Lynch found most 100-baggers in small-cap stocks that could grow large.
        """
        score = 0
        reasons = []

        market_cap = data.get("market_cap")

        if market_cap and market_cap > 0:
            market_cap_b = market_cap / 1e9  # Convert to billions

            # Small caps have most room to grow
            if market_cap_b < 0.5:  # < $500M
                score += 5
                reasons.append(f"Micro-cap (${market_cap_b:.2f}B) - maximum room")
            elif market_cap_b < 1:  # < $1B
                score += 4
                reasons.append(f"Small-cap (${market_cap_b:.2f}B) - great room")
            elif market_cap_b < 2:  # < $2B
                score += 3
                reasons.append(f"Small-cap (${market_cap_b:.2f}B) - good room")
            elif market_cap_b < 5:  # < $5B
                score += 2
                reasons.append(f"Mid-cap (${market_cap_b:.2f}B) - moderate room")
            elif market_cap_b < 10:  # < $10B
                score += 1
                reasons.append(f"Mid-cap (${market_cap_b:.2f}B) - some room")
            elif market_cap_b > 100:
                score -= 2
                reasons.append(f"Large-cap (${market_cap_b:.1f}B) - limited room")
        else:
            reasons.append("No market cap data")

        return min(max(score, 0), 10), "; ".join(reasons[:4])

    @staticmethod
    def score_business_story(data: dict) -> tuple[int, str]:
        """
        Business Story Score - Understandable, simple business.

        Lynch's famous advice: "Invest in what you know."
        """
        score = 5  # Start neutral
        reasons = []

        sector = data.get("sector", "")
        industry = data.get("industry", "")
        name = data.get("name", "")

        # Simple, understandable businesses (Lynch's preference)
        simple_sectors = ["Consumer", "Retail", "Restaurant", "Hotel", 
                         "Auto", "Food", "Beverage", "Apparel"]
        
        boring_industries = ["Waste Management", "Funeral", "Pest Control",
                            "Laundry", "Janitorial", "Security", "Rental"]

        combined = f"{sector} {industry} {name}".upper()

        # Simple consumer businesses
        if any(s in combined for s in simple_sectors):
            score += 2
            reasons.append("Simple consumer business")

        # "Boring" businesses (less competition)
        if any(b in combined for b in boring_industries):
            score += 3
            reasons.append("Boring business (less competition)")

        # Tech can be good if understandable
        if "SOFTWARE" in combined or "TECHNOLOGY" in combined:
            if "APPLICATION" in combined or "CLOUD" in combined:
                score += 1
                reasons.append("Understandable tech business")

        # Avoid overly complex businesses
        complex_keywords = ["HOLDING", "CONGLOMERATE", "DIVERSIFIED", "CAPITAL"]
        if any(c in combined for c in complex_keywords):
            score -= 1
            reasons.append("Complex business structure")

        if not reasons:
            reasons.append("Standard business model")

        return min(max(score, 0), 10), "; ".join(reasons[:4])

    @staticmethod
    def analyze_stock(stock_data: dict) -> dict:
        """
        Run all 10 strategies on a stock for 100-bagger analysis.

        Args:
            stock_data (dict): Stock data dictionary from StockDataFetcher

        Returns:
            dict: Analysis results with scores and reasons for each strategy
        """
        if not stock_data:
            return {"error": "No stock data provided"}

        strategies = {
            "lynch_score": HundredBaggerStrategies.score_lynch(stock_data),
            "growth_score": HundredBaggerStrategies.score_growth(stock_data),
            "value_score": HundredBaggerStrategies.score_value(stock_data),
            "financial_health": HundredBaggerStrategies.score_financial_health(stock_data),
            "profitability_score": HundredBaggerStrategies.score_profitability(stock_data),
            "moat_score": HundredBaggerStrategies.score_moat(stock_data),
            "insider_score": HundredBaggerStrategies.score_insider(stock_data),
            "momentum_score": HundredBaggerStrategies.score_momentum(stock_data),
            "small_cap_potential": HundredBaggerStrategies.score_small_cap_potential(stock_data),
            "business_story": HundredBaggerStrategies.score_business_story(stock_data),
        }

        # Calculate total and average scores
        total_score = sum(score for score, _ in strategies.values())
        average_score = total_score / len(strategies) if strategies else 0

        # Build result dictionary
        result = {
            "total_score": total_score,
            "average_score": round(average_score, 2),
        }

        for strategy_name, (score, reason) in strategies.items():
            result[strategy_name] = {
                "score": score,
                "reason": reason
            }

        return result
