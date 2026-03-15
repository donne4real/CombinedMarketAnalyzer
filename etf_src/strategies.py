"""
ETF Investment Strategy Analyzers Module

Implements 10 sophisticated investment models for comprehensive ETF analysis:

Models:
    1. Value Score - Low expense ratio, P/E, P/B
    2. Momentum Strategy - Price trends and moving averages
    3. Quality Score - Fund family, holdings quality
    4. Growth Score - Historical returns, YTD performance
    5. Dividend Score - Yield, consistency, growth
    6. Risk-Adjusted Return - Sharpe ratio, volatility
    7. Diversification Score - Holdings count, concentration
    8. Cost Efficiency - Expense ratio, tracking error
    9. Liquidity Score - Volume, AUM, bid-ask spread
    10. ESG Score - Environmental, Social, Governance factors

Scoring System:
    Each model scores ETFs from 0-10:
    - 8-10: Strong buy signal (🟢)
    - 5-7: Moderate/hold (🟡)
    - 0-4: Weak/avoid (🔴)

Example:
    >>> from etf_src.strategies import ETFStrategies
    >>> analysis = ETFStrategies.analyze_etf(etf_data)
    >>> print(f"Total Score: {analysis['total_score']}/100")
"""

from typing import Optional


# Strategy names for display
STRATEGY_NAMES = {
    "value_score": "Value Score",
    "momentum": "Momentum Strategy",
    "quality_score": "Quality Score",
    "growth_score": "Growth Score",
    "dividend_score": "Dividend Score",
    "risk_adjusted": "Risk-Adjusted Return",
    "diversification": "Diversification Score",
    "cost_efficiency": "Cost Efficiency",
    "liquidity_score": "Liquidity Score",
    "esg_score": "ESG Score",
}


class ETFStrategies:
    """
    Analyzes ETFs using 10 different investment models.

    Each model implements a specific investment philosophy and scores
    ETFs from 0-10 based on how well they match the criteria.
    """

    @staticmethod
    def score_value(data: dict) -> tuple[int, str]:
        """
        Value Score for ETFs.

        Criteria:
        - Low expense ratio (max 3 points)
        - Low P/E ratio (max 2 points)
        - Low P/B ratio (max 2 points)
        - NAV discount/premium (max 2 points)
        - Low beta (max 1 point)
        """
        score = 0
        reasons = []

        expense_ratio = data.get("expense_ratio")
        pe_ratio = data.get("pe_ratio")
        pb_ratio = data.get("pb_ratio")
        nav_price = data.get("nav_price")
        price = data.get("price")
        beta = data.get("beta")

        # Expense Ratio scoring (lower is better)
        if expense_ratio and expense_ratio >= 0:
            if expense_ratio < 0.0003:  # < 3 bps
                score += 3
                reasons.append(f"Ultra-low expense ({expense_ratio:.2%})")
            elif expense_ratio < 0.0010:  # < 10 bps
                score += 2
                reasons.append(f"Very low expense ({expense_ratio:.2%})")
            elif expense_ratio < 0.0020:  # < 20 bps
                score += 1
                reasons.append(f"Low expense ({expense_ratio:.2%})")
            elif expense_ratio < 0.0050:  # < 50 bps
                score += 0
            else:
                score -= 1
                reasons.append(f"High expense ({expense_ratio:.2%})")
        else:
            reasons.append("No expense data")

        # P/E Ratio (for equity ETFs)
        if pe_ratio and pe_ratio > 0:
            if pe_ratio < 12:
                score += 2
                reasons.append(f"Low P/E ({pe_ratio:.1f})")
            elif pe_ratio < 18:
                score += 1
                reasons.append(f"Fair P/E ({pe_ratio:.1f})")
            elif pe_ratio > 30:
                score -= 1
                reasons.append(f"High P/E ({pe_ratio:.1f})")

        # P/B Ratio
        if pb_ratio and pb_ratio > 0:
            if pb_ratio < 1.5:
                score += 2
                reasons.append(f"Low P/B ({pb_ratio:.1f})")
            elif pb_ratio < 3:
                score += 1
                reasons.append(f"Fair P/B ({pb_ratio:.1f})")

        # NAV Discount/Premium
        if nav_price and price and nav_price > 0:
            nav_diff = (price - nav_price) / nav_price
            if abs(nav_diff) < 0.001:  # Within 0.1%
                score += 2
                reasons.append("Fair NAV pricing")
            elif nav_diff < 0:  # Trading at discount
                score += 1
                reasons.append(f"NAV discount ({nav_diff:.2%})")
            elif nav_diff > 0.01:  # Premium > 1%
                score -= 1
                reasons.append(f"NAV premium ({nav_diff:.2%})")

        # Low Beta (lower volatility)
        if beta and beta > 0:
            if beta < 0.8:
                score += 1
                reasons.append("Low volatility")
            elif beta > 1.3:
                reasons.append("High volatility")

        return min(max(score, 0), 10), "; ".join(reasons[:4])

    @staticmethod
    def score_momentum(data: dict) -> tuple[int, str]:
        """
        Momentum Strategy for ETFs.

        Measures:
        - 12-month price momentum
        - 6-month price momentum
        - 3-month price momentum
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
        ytd_return = data.get("ytd_return")

        # 12-month momentum
        if price and year_ago and year_ago > 0:
            momentum_12m = (price - year_ago) / year_ago
            if momentum_12m > 0.30:
                score += 3
                reasons.append(f"Excellent 12M momentum ({momentum_12m:.1%})")
            elif momentum_12m > 0.15:
                score += 2
                reasons.append(f"Strong 12M momentum ({momentum_12m:.1%})")
            elif momentum_12m > 0.05:
                score += 1
                reasons.append(f"Positive 12M momentum ({momentum_12m:.1%})")
            elif momentum_12m < -0.10:
                score -= 1
                reasons.append(f"Negative 12M momentum ({momentum_12m:.1%})")

        # 6-month momentum
        if price and month_6_ago and month_6_ago > 0:
            momentum_6m = (price - month_6_ago) / month_6_ago
            if momentum_6m > 0.15:
                score += 2
                reasons.append(f"Strong 6M momentum ({momentum_6m:.1%})")
            elif momentum_6m > 0.05:
                score += 1
            elif momentum_6m < -0.10:
                score -= 1

        # 3-month momentum
        if price and month_3_ago and month_3_ago > 0:
            momentum_3m = (price - month_3_ago) / month_3_ago
            if momentum_3m > 0.10:
                score += 2
                reasons.append(f"Positive 3M trend ({momentum_3m:.1%})")
            elif momentum_3m < -0.10:
                score -= 1

        # YTD Return
        if ytd_return and ytd_return > 0:
            if ytd_return > 0.20:
                score += 2
                reasons.append(f"Excellent YTD ({ytd_return:.1%})")
            elif ytd_return > 0.10:
                score += 1
                reasons.append(f"Good YTD ({ytd_return:.1%})")

        # Position in 52-week range
        if price and high_52 and low_52 and high_52 != low_52:
            position = (price - low_52) / (high_52 - low_52)
            if position > 0.85:
                score += 1
                reasons.append("Near 52-week high")
            elif position < 0.15:
                score -= 1
                reasons.append("Near 52-week low")

        # Price vs 50-day MA
        if price and avg_50:
            if price > avg_50 * 1.02:
                score += 1
                reasons.append("Above 50-day MA")
            elif price < avg_50 * 0.98:
                score -= 1

        # Price vs 200-day MA
        if price and avg_200:
            if price > avg_200 * 1.02:
                score += 1
                reasons.append("Above 200-day MA")
            elif price < avg_200 * 0.98:
                score -= 1

        return min(max(score, 0), 10), "; ".join(reasons[:4])

    @staticmethod
    def score_quality(data: dict) -> tuple[int, str]:
        """
        Quality Score for ETFs.

        Criteria:
        - Fund family reputation
        - Holdings quality (stock/bond %)
        - Tracking accuracy
        - Fund age
        """
        score = 0
        reasons = []

        family = data.get("family", "")
        stock_holdings = data.get("stock_holdings")
        bond_holdings = data.get("bond_holdings")
        holdings_count = data.get("holdings_count")
        inception_date = data.get("fund_inception_date")

        # Fund Family scoring (major providers)
        top_families = ["Vanguard", "iShares", "SPDR", "Schwab", "Invesco", 
                       "Fidelity", "BlackRock", "JPMorgan", "Goldman Sachs"]
        if any(f in family for f in top_families):
            score += 3
            reasons.append(f"Top-tier family ({family})")
        elif family and family != "N/A":
            score += 2
            reasons.append(f"Known family ({family})")
        else:
            reasons.append("Unknown family")

        # Holdings Quality - Stock/Bond allocation clarity
        if stock_holdings is not None or bond_holdings is not None:
            total_holdings = (stock_holdings or 0) + (bond_holdings or 0)
            if 0.8 < total_holdings < 1.1:  # Close to 100%
                score += 2
                reasons.append("Clear asset allocation")
            if stock_holdings and stock_holdings > 0.9:
                reasons.append("Equity-focused")
            elif bond_holdings and bond_holdings > 0.9:
                reasons.append("Bond-focused")
        else:
            reasons.append("No holdings data")

        # Holdings Count (diversification indicator)
        if holdings_count and holdings_count > 0:
            if holdings_count > 500:
                score += 2
                reasons.append(f"Highly diversified ({holdings_count} holdings)")
            elif holdings_count > 100:
                score += 1
                reasons.append(f"Diversified ({holdings_count} holdings)")
            elif holdings_count > 20:
                score += 0
            else:
                reasons.append(f"Concentrated ({holdings_count} holdings)")

        # Fund Age (older = more track record)
        if inception_date:
            try:
                from datetime import datetime
                inception = datetime.fromtimestamp(inception_date)
                age_years = (datetime.now() - inception).days / 365
                if age_years > 10:
                    score += 2
                    reasons.append(f"Established fund ({age_years:.0f} yrs)")
                elif age_years > 5:
                    score += 1
                    reasons.append(f"Mature fund ({age_years:.0f} yrs)")
                elif age_years > 2:
                    score += 0
                else:
                    reasons.append(f"New fund ({age_years:.1f} yrs)")
            except:
                pass

        return min(max(score, 0), 10), "; ".join(reasons[:4])

    @staticmethod
    def score_growth(data: dict) -> tuple[int, str]:
        """
        Growth Score for ETFs.

        Criteria:
        - YTD return
        - 3-year average return
        - 5-year average return
        - Recent momentum
        """
        score = 0
        reasons = []

        ytd_return = data.get("ytd_return")
        three_year = data.get("three_year_return")
        five_year = data.get("five_year_return")
        price = data.get("price")
        year_ago = data.get("year_ago_price")

        # YTD Return
        if ytd_return and ytd_return >= 0:
            if ytd_return > 0.25:
                score += 3
                reasons.append(f"Exceptional YTD ({ytd_return:.1%})")
            elif ytd_return > 0.15:
                score += 2
                reasons.append(f"Strong YTD ({ytd_return:.1%})")
            elif ytd_return > 0.08:
                score += 1
                reasons.append(f"Good YTD ({ytd_return:.1%})")
            elif ytd_return < 0:
                score -= 1
                reasons.append(f"Negative YTD ({ytd_return:.1%})")

        # 3-Year Return (annualized)
        if three_year and three_year >= 0:
            if three_year > 0.15:
                score += 3
                reasons.append(f"Excellent 3Y ({three_year:.1%})")
            elif three_year > 0.10:
                score += 2
                reasons.append(f"Good 3Y ({three_year:.1%})")
            elif three_year > 0.05:
                score += 1
                reasons.append(f"Moderate 3Y ({three_year:.1%})")
            elif three_year < 0:
                reasons.append(f"Negative 3Y ({three_year:.1%})")

        # 5-Year Return (annualized)
        if five_year and five_year >= 0:
            if five_year > 0.12:
                score += 3
                reasons.append(f"Excellent 5Y ({five_year:.1%})")
            elif five_year > 0.08:
                score += 2
                reasons.append(f"Good 5Y ({five_year:.1%})")
            elif five_year > 0.05:
                score += 1
                reasons.append(f"Moderate 5Y ({five_year:.1%})")

        # 12-Month Price Growth
        if price and year_ago and year_ago > 0:
            growth_12m = (price - year_ago) / year_ago
            if growth_12m > 0.20:
                score += 1
                reasons.append("Strong price growth")

        return min(max(score, 0), 10), "; ".join(reasons[:4])

    @staticmethod
    def score_dividend(data: dict) -> tuple[int, str]:
        """
        Dividend Score for ETFs.

        Criteria:
        - Dividend yield
        - Dividend consistency
        - Dividend growth potential
        """
        score = 0
        reasons = []

        div_yield = data.get("dividend_yield")
        category = data.get("category", "")

        # Dividend Yield scoring
        if div_yield and div_yield > 0:
            if div_yield > 0.05:  # > 5%
                score += 4
                reasons.append(f"High yield ({div_yield:.2%})")
            elif div_yield > 0.03:  # > 3%
                score += 3
                reasons.append(f"Good yield ({div_yield:.2%})")
            elif div_yield > 0.02:  # > 2%
                score += 2
                reasons.append(f"Moderate yield ({div_yield:.2%})")
            elif div_yield > 0.01:  # > 1%
                score += 1
                reasons.append(f"Low yield ({div_yield:.2%})")
            else:
                reasons.append(f"Minimal yield ({div_yield:.2%})")
        else:
            reasons.append("No dividend")

        # Category bonus for dividend-focused ETFs
        dividend_keywords = ["dividend", "income", "yield", "div"]
        if category and any(kw in category.lower() for kw in dividend_keywords):
            score += 2
            reasons.append("Dividend-focused ETF")

        # Bonus for reasonable yield with growth potential
        three_year = data.get("three_year_return")
        if three_year and three_year > 0.08 and div_yield and div_yield > 0.02:
            score += 2
            reasons.append("Yield + growth combination")

        return min(max(score, 0), 10), "; ".join(reasons[:4])

    @staticmethod
    def score_risk_adjusted(data: dict) -> tuple[int, str]:
        """
        Risk-Adjusted Return Score.

        Criteria:
        - Beta (market sensitivity)
        - Volatility (52-week range)
        - Downside protection
        """
        score = 0
        reasons = []

        beta = data.get("beta")
        high_52 = data.get("52_week_high")
        low_52 = data.get("52_week_low")
        price = data.get("price")

        # Beta scoring (closer to 1 = market-like, lower = less volatile)
        if beta and beta > 0:
            if 0.7 <= beta <= 1.1:
                score += 3
                reasons.append(f"Market-like beta ({beta:.2f})")
            elif 0.5 <= beta < 0.7:
                score += 2
                reasons.append(f"Low beta ({beta:.2f})")
            elif 1.1 < beta <= 1.3:
                score += 1
                reasons.append(f"Slightly high beta ({beta:.2f})")
            elif beta > 1.5:
                score -= 1
                reasons.append(f"High beta ({beta:.2f})")
            elif beta < 0.5:
                score += 1
                reasons.append(f"Very low beta ({beta:.2f})")
        else:
            reasons.append("No beta data")

        # Volatility based on 52-week range
        if high_52 and low_52 and high_52 > 0:
            range_pct = (high_52 - low_52) / low_52
            if range_pct < 0.20:  # Low volatility
                score += 3
                reasons.append("Low volatility")
            elif range_pct < 0.35:  # Moderate volatility
                score += 2
                reasons.append("Moderate volatility")
            elif range_pct < 0.50:  # Higher volatility
                score += 1
                reasons.append("Higher volatility")
            else:
                reasons.append("High volatility")

        # Current position in range (closer to high = better momentum)
        if price and high_52 and low_52 and high_52 != low_52:
            position = (price - low_52) / (high_52 - low_52)
            if position > 0.7:
                score += 2
                reasons.append("Strong relative performance")
            elif position > 0.5:
                score += 1
            elif position < 0.3:
                score -= 1
                reasons.append("Weak relative performance")

        return min(max(score, 0), 10), "; ".join(reasons[:4])

    @staticmethod
    def score_diversification(data: dict) -> tuple[int, str]:
        """
        Diversification Score.

        Criteria:
        - Number of holdings
        - Top 10 holdings concentration
        - Asset allocation balance
        """
        score = 0
        reasons = []

        holdings_count = data.get("holdings_count")
        top_10_pct = data.get("top_10_holdings_pct")
        stock_holdings = data.get("stock_holdings")
        bond_holdings = data.get("bond_holdings")

        # Holdings Count
        if holdings_count and holdings_count > 0:
            if holdings_count > 1000:
                score += 4
                reasons.append(f"Ultra-diversified ({holdings_count})")
            elif holdings_count > 500:
                score += 3
                reasons.append(f"Highly diversified ({holdings_count})")
            elif holdings_count > 100:
                score += 2
                reasons.append(f"Diversified ({holdings_count})")
            elif holdings_count > 30:
                score += 1
                reasons.append(f"Moderate ({holdings_count})")
            else:
                reasons.append(f"Concentrated ({holdings_count})")
        else:
            reasons.append("No holdings data")

        # Top 10 Holdings Concentration
        if top_10_pct and top_10_pct >= 0:
            if top_10_pct < 0.30:  # < 30%
                score += 3
                reasons.append("Low concentration")
            elif top_10_pct < 0.50:  # < 50%
                score += 2
                reasons.append("Moderate concentration")
            elif top_10_pct < 0.70:  # < 70%
                score += 1
                reasons.append("Higher concentration")
            else:
                reasons.append("Very concentrated")

        # Asset Allocation (for balanced funds)
        if stock_holdings and bond_holdings:
            total = stock_holdings + bond_holdings
            if 0.4 <= stock_holdings <= 0.6 and 0.4 <= bond_holdings <= 0.6:
                score += 2
                reasons.append("Balanced allocation")
            elif stock_holdings > 0.9:
                reasons.append("Equity-focused")
            elif bond_holdings > 0.9:
                reasons.append("Bond-focused")

        return min(max(score, 0), 10), "; ".join(reasons[:4])

    @staticmethod
    def score_cost_efficiency(data: dict) -> tuple[int, str]:
        """
        Cost Efficiency Score.

        Criteria:
        - Expense ratio
        - Value for features provided
        """
        score = 0
        reasons = []

        expense_ratio = data.get("expense_ratio")
        category = data.get("category", "")

        # Expense Ratio scoring
        if expense_ratio and expense_ratio >= 0:
            if expense_ratio < 0.0003:  # < 3 bps
                score += 5
                reasons.append(f"Ultra-low cost ({expense_ratio:.2%})")
            elif expense_ratio < 0.0010:  # < 10 bps
                score += 4
                reasons.append(f"Very low cost ({expense_ratio:.2%})")
            elif expense_ratio < 0.0020:  # < 20 bps
                score += 3
                reasons.append(f"Low cost ({expense_ratio:.2%})")
            elif expense_ratio < 0.0050:  # < 50 bps
                score += 2
                reasons.append(f"Moderate cost ({expense_ratio:.2%})")
            elif expense_ratio < 0.01:  # < 100 bps
                score += 1
                reasons.append(f"Higher cost ({expense_ratio:.2%})")
            else:
                reasons.append(f"Expensive ({expense_ratio:.2%})")
        else:
            reasons.append("No expense data")

        # Category adjustment (some categories justify higher fees)
        if category:
            specialized = ["ESG", "Thematic", "Active", "Smart Beta", 
                          "International", "Emerging", "Commodity", "Bond"]
            if any(kw in category for kw in specialized):
                # Slightly more lenient for specialized ETFs
                if expense_ratio and expense_ratio < 0.0030:
                    score += 1
                    reasons.append("Good value for category")

        return min(max(score, 0), 10), "; ".join(reasons[:4])

    @staticmethod
    def score_liquidity(data: dict) -> tuple[int, str]:
        """
        Liquidity Score.

        Criteria:
        - Average volume
        - Current volume vs average
        - AUM (market cap as proxy)
        """
        score = 0
        reasons = []

        avg_volume = data.get("avg_volume")
        volume = data.get("volume")
        market_cap = data.get("market_cap")

        # Average Volume scoring
        if avg_volume and avg_volume > 0:
            if avg_volume > 5000000:  # > 5M
                score += 4
                reasons.append(f"Excellent liquidity ({avg_volume/1e6:.1f}M avg)")
            elif avg_volume > 1000000:  # > 1M
                score += 3
                reasons.append(f"High liquidity ({avg_volume/1e6:.1f}M avg)")
            elif avg_volume > 500000:  # > 500K
                score += 2
                reasons.append(f"Good liquidity ({avg_volume/1e6:.1f}M avg)")
            elif avg_volume > 100000:  # > 100K
                score += 1
                reasons.append(f"Moderate liquidity ({avg_volume/1e6:.1f}M avg)")
            else:
                reasons.append(f"Low liquidity ({avg_volume/1e6:.2f}M avg)")
        else:
            reasons.append("No volume data")

        # Current vs Average Volume
        if volume and avg_volume and avg_volume > 0:
            vol_ratio = volume / avg_volume
            if vol_ratio > 1.5:
                score += 1
                reasons.append("Above average volume today")
            elif vol_ratio < 0.5:
                reasons.append("Below average volume")

        # AUM (Market Cap as proxy)
        if market_cap and market_cap > 0:
            if market_cap > 10e9:  # > $10B
                score += 2
                reasons.append("Large AUM")
            elif market_cap > 1e9:  # > $1B
                score += 1
                reasons.append("Medium AUM")
            elif market_cap < 100e6:  # < $100M
                score -= 1
                reasons.append("Small AUM risk")

        return min(max(score, 0), 10), "; ".join(reasons[:4])

    @staticmethod
    def score_esg(data: dict) -> tuple[int, str]:
        """
        ESG Score (Environmental, Social, Governance).

        Criteria:
        - ESG category identification
        - Fund family ESG commitment
        - Holdings type
        """
        score = 5  # Start neutral
        reasons = []

        category = data.get("category", "")
        name = data.get("name", "")
        family = data.get("family", "")

        # Check for ESG-focused ETFs
        esg_keywords = ["ESG", "Sustainable", "Clean", "Green", "Social", 
                       "Governance", "Environmental", "Carbon", "Climate"]
        
        combined_text = f"{category} {name} {family}".upper()
        
        esg_count = sum(1 for kw in esg_keywords if kw.upper() in combined_text)
        
        if esg_count >= 2:
            score += 4
            reasons.append("ESG-focused ETF")
        elif esg_count == 1:
            score += 2
            reasons.append("ESG considerations")

        # Clean energy / sustainability bonus
        clean_keywords = ["ICLN", "QCLN", "PBW", "ERTH", "SMOG", "CTEC"]
        if any(ticker in name.upper() for ticker in clean_keywords):
            score += 2
            reasons.append("Clean energy focus")

        # Broad market ETFs get neutral score
        broad_keywords = ["S&P 500", "TOTAL MARKET", "ALL WORLD", "RUSSELL"]
        if any(kw in combined_text for kw in broad_keywords):
            reasons.append("Broad market exposure")

        if not reasons:
            reasons.append("Standard ETF")

        return min(max(score, 0), 10), "; ".join(reasons[:4])

    @staticmethod
    def analyze_etf(etf_data: dict) -> dict:
        """
        Run all 10 strategies on an ETF and return comprehensive analysis.

        Args:
            etf_data (dict): ETF data dictionary from ETFDataFetcher

        Returns:
            dict: Analysis results with scores and reasons for each strategy
        """
        if not etf_data:
            return {"error": "No ETF data provided"}

        strategies = {
            "value_score": ETFStrategies.score_value(etf_data),
            "momentum": ETFStrategies.score_momentum(etf_data),
            "quality_score": ETFStrategies.score_quality(etf_data),
            "growth_score": ETFStrategies.score_growth(etf_data),
            "dividend_score": ETFStrategies.score_dividend(etf_data),
            "risk_adjusted": ETFStrategies.score_risk_adjusted(etf_data),
            "diversification": ETFStrategies.score_diversification(etf_data),
            "cost_efficiency": ETFStrategies.score_cost_efficiency(etf_data),
            "liquidity_score": ETFStrategies.score_liquidity(etf_data),
            "esg_score": ETFStrategies.score_esg(etf_data),
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
