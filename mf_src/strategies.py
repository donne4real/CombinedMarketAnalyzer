"""
Mutual Fund Investment Strategy Analyzers Module

Implements 10 sophisticated investment models for comprehensive mutual fund analysis:

Models:
    1. Cost Efficiency - Low expense ratio, no load fees
    2. Performance Score - Historical returns vs benchmark
    3. Manager Quality - Fund family, tenure, consistency
    4. Risk-Adjusted Return - Sharpe, Sortino, alpha, beta
    5. Diversification Score - Holdings count, concentration
    6. Tax Efficiency - Turnover rate, capital gains distribution
    7. Fund Quality - Morningstar rating, sustainability
    8. Growth Score - Long-term growth trajectory
    9. Income Score - Dividend yield, distribution consistency
    10. ESG Score - Environmental, Social, Governance factors

Scoring System:
    Each model scores funds from 0-10:
    - 8-10: Strong buy signal (🟢)
    - 5-7: Moderate/hold (🟡)
    - 0-4: Weak/avoid (🔴)

Example:
    >>> from mf_src.strategies import MutualFundStrategies
    >>> analysis = MutualFundStrategies.analyze_fund(fund_data)
    >>> print(f"Total Score: {analysis['total_score']}/100")
"""

from typing import Optional


# Strategy names for display
STRATEGY_NAMES = {
    "cost_efficiency": "Cost Efficiency",
    "performance_score": "Performance Score",
    "manager_quality": "Manager Quality",
    "risk_adjusted": "Risk-Adjusted Return",
    "diversification": "Diversification Score",
    "tax_efficiency": "Tax Efficiency",
    "fund_quality": "Fund Quality",
    "growth_score": "Growth Score",
    "income_score": "Income Score",
    "esg_score": "ESG Score",
}


class MutualFundStrategies:
    """
    Analyzes mutual funds using 10 different investment models.

    Each model implements a specific investment philosophy and scores
    funds from 0-10 based on how well they match the criteria.
    """

    @staticmethod
    def score_cost_efficiency(data: dict) -> tuple[int, str]:
        """
        Cost Efficiency Score for Mutual Funds.

        Criteria:
        - Expense ratio (max 5 points)
        - No load fees (max 2 points)
        - Low minimum investment (max 2 points)
        - Low turnover (max 1 point)
        """
        score = 0
        reasons = []

        expense_ratio = data.get("expense_ratio")
        turnover = data.get("turnover_rate")
        min_investment = data.get("min_initial_investment")

        # Expense Ratio scoring (lower is better)
        if expense_ratio and expense_ratio >= 0:
            if expense_ratio < 0.0005:  # < 5 bps
                score += 5
                reasons.append(f"Ultra-low expense ({expense_ratio:.2%})")
            elif expense_ratio < 0.0010:  # < 10 bps
                score += 4
                reasons.append(f"Very low expense ({expense_ratio:.2%})")
            elif expense_ratio < 0.0020:  # < 20 bps
                score += 3
                reasons.append(f"Low expense ({expense_ratio:.2%})")
            elif expense_ratio < 0.0050:  # < 50 bps
                score += 2
                reasons.append(f"Moderate expense ({expense_ratio:.2%})")
            elif expense_ratio < 0.01:  # < 100 bps
                score += 1
                reasons.append(f"Higher expense ({expense_ratio:.2%})")
            else:
                reasons.append(f"Expensive ({expense_ratio:.2%})")
        else:
            reasons.append("No expense data")

        # Turnover Rate (lower = more tax efficient)
        if turnover and turnover >= 0:
            if turnover < 0.20:
                score += 1
                reasons.append("Low turnover")
            elif turnover > 0.80:
                reasons.append("High turnover")

        # Minimum Investment
        if min_investment and min_investment >= 0:
            if min_investment < 1000:
                score += 1
                reasons.append("Low minimum")
            elif min_investment > 10000:
                reasons.append("High minimum")

        return min(max(score, 0), 10), "; ".join(reasons[:4])

    @staticmethod
    def score_performance(data: dict) -> tuple[int, str]:
        """
        Performance Score for Mutual Funds.

        Criteria:
        - 10-year return (max 4 points)
        - 5-year return (max 3 points)
        - 3-year return (max 2 points)
        - YTD return (max 1 point)
        """
        score = 0
        reasons = []

        ten_year = data.get("ten_year_return")
        five_year = data.get("five_year_return")
        three_year = data.get("three_year_return")
        ytd = data.get("ytd_return")

        # 10-Year Return (most important for long-term)
        if ten_year and ten_year >= 0:
            if ten_year > 0.12:
                score += 4
                reasons.append(f"Excellent 10Y ({ten_year:.1%})")
            elif ten_year > 0.09:
                score += 3
                reasons.append(f"Good 10Y ({ten_year:.1%})")
            elif ten_year > 0.06:
                score += 2
                reasons.append(f"Moderate 10Y ({ten_year:.1%})")
            elif ten_year < 0.03:
                reasons.append(f"Weak 10Y ({ten_year:.1%})")
        elif ten_year is None:
            reasons.append("No 10Y data")

        # 5-Year Return
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

        # 3-Year Return
        if three_year and three_year >= 0:
            if three_year > 0.10:
                score += 2
                reasons.append(f"Strong 3Y ({three_year:.1%})")
            elif three_year > 0.06:
                score += 1
                reasons.append(f"Good 3Y ({three_year:.1%})")

        # YTD Return
        if ytd and ytd > 0.10:
            score += 1
            reasons.append(f"Good YTD ({ytd:.1%})")

        return min(max(score, 0), 10), "; ".join(reasons[:4])

    @staticmethod
    def score_manager_quality(data: dict) -> tuple[int, str]:
        """
        Manager Quality Score.

        Criteria:
        - Fund family reputation
        - Fund age/track record
        - Net assets (fund size)
        """
        score = 0
        reasons = []

        family = data.get("family", "")
        inception_date = data.get("inception_date")
        net_assets = data.get("net_assets")

        # Fund Family scoring
        top_families = ["Vanguard", "Fidelity", "Schwab", "T. Rowe Price", 
                       "American Funds", "PIMCO", "BlackRock", "JPMorgan"]
        if any(f in family for f in top_families):
            score += 4
            reasons.append(f"Top-tier family ({family})")
        elif family and family != "N/A":
            score += 2
            reasons.append(f"Known family ({family})")
        else:
            reasons.append("Unknown family")

        # Fund Age (older = more track record)
        if inception_date:
            try:
                from datetime import datetime
                inception = datetime.fromtimestamp(inception_date) if isinstance(inception_date, (int, float)) else datetime.now()
                age_years = (datetime.now() - inception).days / 365
                if age_years > 15:
                    score += 3
                    reasons.append(f"Established ({age_years:.0f} yrs)")
                elif age_years > 10:
                    score += 2
                    reasons.append(f"Mature ({age_years:.0f} yrs)")
                elif age_years > 5:
                    score += 1
                    reasons.append(f"Developing ({age_years:.0f} yrs)")
                else:
                    reasons.append(f"New fund ({age_years:.1f} yrs)")
            except:
                pass

        # Net Assets (larger = more stable, but not too large)
        if net_assets and net_assets > 0:
            if net_assets > 10e9:  # > $10B
                score += 2
                reasons.append("Large fund")
            elif net_assets > 1e9:  # > $1B
                score += 1
                reasons.append("Medium fund")
            elif net_assets < 100e6:
                reasons.append("Small fund risk")

        return min(max(score, 0), 10), "; ".join(reasons[:4])

    @staticmethod
    def score_risk_adjusted(data: dict) -> tuple[int, str]:
        """
        Risk-Adjusted Return Score.

        Criteria:
        - Alpha (excess return vs benchmark)
        - Beta (market sensitivity)
        - Morningstar risk rating
        - Standard deviation/volatility
        """
        score = 0
        reasons = []

        alpha = data.get("alpha")
        beta = data.get("beta")
        morningstar_risk = data.get("morningstar_risk")
        mean_return = data.get("mean_annual_return")

        # Alpha (positive = outperformance)
        if alpha and alpha > 0:
            if alpha > 3:
                score += 4
                reasons.append(f"Excellent alpha ({alpha:.1f})")
            elif alpha > 1:
                score += 3
                reasons.append(f"Good alpha ({alpha:.1f})")
            elif alpha > 0:
                score += 1
                reasons.append(f"Positive alpha ({alpha:.1f})")
        elif alpha and alpha < -1:
            score -= 1
            reasons.append(f"Negative alpha ({alpha:.1f})")

        # Beta (closer to 1 = market-like, lower = less volatile)
        if beta and beta > 0:
            if 0.8 <= beta <= 1.1:
                score += 2
                reasons.append(f"Market beta ({beta:.2f})")
            elif 0.6 <= beta < 0.8:
                score += 2
                reasons.append(f"Low beta ({beta:.2f})")
            elif beta > 1.3:
                reasons.append(f"High beta ({beta:.2f})")

        # Morningstar Risk Rating
        if morningstar_risk:
            risk_lower = str(morningstar_risk).lower()
            if "low" in risk_lower:
                score += 3
                reasons.append("Low Morningstar risk")
            elif "below" in risk_lower:
                score += 2
                reasons.append("Below avg risk")
            elif "high" in risk_lower:
                score -= 1
                reasons.append("High Morningstar risk")

        # Mean Annual Return
        if mean_return and mean_return > 0.10:
            score += 1
            reasons.append("Strong mean return")

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
        cash_holdings = data.get("cash_holdings")

        # Holdings Count
        if holdings_count and holdings_count > 0:
            if holdings_count > 500:
                score += 4
                reasons.append(f"Highly diversified ({holdings_count})")
            elif holdings_count > 200:
                score += 3
                reasons.append(f"Diversified ({holdings_count})")
            elif holdings_count > 50:
                score += 2
                reasons.append(f"Moderate ({holdings_count})")
            else:
                reasons.append(f"Concentrated ({holdings_count})")
        else:
            reasons.append("No holdings data")

        # Top 10 Holdings Concentration
        if top_10_pct and top_10_pct >= 0:
            if top_10_pct < 0.25:
                score += 3
                reasons.append("Low concentration")
            elif top_10_pct < 0.40:
                score += 2
                reasons.append("Moderate concentration")
            elif top_10_pct < 0.60:
                score += 1
                reasons.append("Higher concentration")
            else:
                reasons.append("Very concentrated")

        # Asset Allocation
        if stock_holdings and bond_holdings:
            total = stock_holdings + bond_holdings + (cash_holdings or 0)
            if 0.3 <= stock_holdings <= 0.7 and 0.2 <= bond_holdings <= 0.5:
                score += 2
                reasons.append("Balanced allocation")

        return min(max(score, 0), 10), "; ".join(reasons[:4])

    @staticmethod
    def score_tax_efficiency(data: dict) -> tuple[int, str]:
        """
        Tax Efficiency Score.

        Criteria:
        - Turnover rate (lower = more tax efficient)
        - Fund type (index funds more efficient)
        - Capital gains distribution history
        """
        score = 5  # Start neutral
        reasons = []

        turnover = data.get("turnover_rate")
        category = data.get("category", "")
        name = data.get("name", "")

        # Turnover Rate (lower = better for taxes)
        if turnover and turnover >= 0:
            if turnover < 0.15:
                score += 4
                reasons.append(f"Very low turnover ({turnover:.0%})")
            elif turnover < 0.30:
                score += 3
                reasons.append(f"Low turnover ({turnover:.0%})")
            elif turnover < 0.50:
                score += 2
                reasons.append(f"Moderate turnover ({turnover:.0%})")
            elif turnover > 0.80:
                score -= 2
                reasons.append(f"High turnover ({turnover:.0%})")
        else:
            reasons.append("No turnover data")

        # Index funds are more tax efficient
        combined = f"{category} {name}".upper()
        if "INDEX" in combined or "PASSIVE" in combined:
            score += 2
            reasons.append("Index fund (tax efficient)")
        elif "ACTIVE" in combined or "MANAGED" in combined:
            reasons.append("Actively managed")

        # ETF structure is more tax efficient (if applicable)
        if "ETF" in combined:
            score += 1
            reasons.append("ETF structure")

        return min(max(score, 0), 10), "; ".join(reasons[:4])

    @staticmethod
    def score_fund_quality(data: dict) -> tuple[int, str]:
        """
        Fund Quality Score.

        Criteria:
        - Morningstar rating
        - Sustainability rating
        - Risk rating
        """
        score = 5  # Start neutral
        reasons = []

        morningstar = data.get("morningstar_rating")
        sustainability = data.get("sustainability_rating")
        risk_rating = data.get("risk_rating")

        # Morningstar Rating (1-5 stars)
        if morningstar and morningstar > 0:
            if morningstar >= 5:
                score += 4
                reasons.append(f"5-star Morningstar")
            elif morningstar >= 4:
                score += 3
                reasons.append(f"4-star Morningstar")
            elif morningstar >= 3:
                score += 1
                reasons.append(f"3-star Morningstar")
            else:
                score -= 1
                reasons.append(f"Low Morningstar rating")
        else:
            reasons.append("No Morningstar rating")

        # Sustainability Rating (1-5 globes)
        if sustainability and sustainability > 0:
            if sustainability >= 4:
                score += 2
                reasons.append(f"High sustainability ({sustainability} globes)")
            elif sustainability >= 3:
                score += 1
                reasons.append(f"Avg sustainability ({sustainability} globes)")

        # Risk Rating
        if risk_rating:
            risk_lower = str(risk_rating).lower()
            if "low" in risk_lower or "below" in risk_lower:
                score += 1
                reasons.append("Low risk rating")

        return min(max(score, 0), 10), "; ".join(reasons[:4])

    @staticmethod
    def score_growth(data: dict) -> tuple[int, str]:
        """
        Growth Score for Mutual Funds.

        Criteria:
        - Long-term growth trajectory
        - Consistency of returns
        - Capital appreciation potential
        """
        score = 0
        reasons = []

        ten_year = data.get("ten_year_return")
        five_year = data.get("five_year_return")
        three_year = data.get("three_year_return")
        ytd = data.get("ytd_return")

        # Consistency check (all positive returns)
        returns = [r for r in [ten_year, five_year, three_year, ytd] if r is not None]
        if returns and all(r > 0 for r in returns):
            score += 2
            reasons.append("Consistent positive returns")

        # Long-term growth
        if ten_year and ten_year > 0.10:
            score += 4
            reasons.append(f"Strong 10Y growth ({ten_year:.1%})")
        elif ten_year and ten_year > 0.07:
            score += 3
            reasons.append(f"Good 10Y growth ({ten_year:.1%})")
        elif ten_year and ten_year > 0.04:
            score += 2
            reasons.append(f"Moderate 10Y growth ({ten_year:.1%})")

        # Recent momentum
        if ytd and ytd > 0.15:
            score += 2
            reasons.append(f"Strong YTD ({ytd:.1%})")
        elif ytd and ytd > 0.08:
            score += 1
            reasons.append(f"Good YTD ({ytd:.1%})")

        # 5-year trajectory
        if five_year and five_year > 0.10:
            score += 2
            reasons.append(f"Solid 5Y ({five_year:.1%})")

        return min(max(score, 0), 10), "; ".join(reasons[:4])

    @staticmethod
    def score_income(data: dict) -> tuple[int, str]:
        """
        Income Score for Mutual Funds.

        Criteria:
        - Dividend yield
        - Distribution consistency
        - Bond/stock allocation
        """
        score = 0
        reasons = []

        div_yield = data.get("dividend_yield")
        fund_yield = data.get("yield")
        category = data.get("category", "")
        bond_holdings = data.get("bond_holdings")

        # Use whichever yield is available
        yield_val = div_yield or fund_yield

        if yield_val and yield_val > 0:
            if yield_val > 0.05:
                score += 4
                reasons.append(f"High yield ({yield_val:.2%})")
            elif yield_val > 0.03:
                score += 3
                reasons.append(f"Good yield ({yield_val:.2%})")
            elif yield_val > 0.02:
                score += 2
                reasons.append(f"Moderate yield ({yield_val:.2%})")
            elif yield_val > 0.01:
                score += 1
                reasons.append(f"Low yield ({yield_val:.2%})")
        else:
            reasons.append("No yield data")

        # Category bonus for income/dividend funds
        income_keywords = ["INCOME", "DIVIDEND", "BOND", "FIXED", "INVESTOR"]
        if category and any(kw in category.upper() for kw in income_keywords):
            score += 2
            reasons.append("Income-focused fund")

        # Bond allocation (higher = more income potential)
        if bond_holdings and bond_holdings > 0.7:
            score += 1
            reasons.append("Bond-heavy allocation")

        return min(max(score, 0), 10), "; ".join(reasons[:4])

    @staticmethod
    def score_esg(data: dict) -> tuple[int, str]:
        """
        ESG Score (Environmental, Social, Governance).

        Criteria:
        - Sustainability rating
        - ESG category identification
        - Fund family ESG commitment
        """
        score = 5  # Start neutral
        reasons = []

        sustainability = data.get("sustainability_rating")
        category = data.get("category", "")
        name = data.get("name", "")
        family = data.get("family", "")

        # Sustainability Rating (1-5 globes)
        if sustainability and sustainability > 0:
            if sustainability >= 5:
                score += 4
                reasons.append(f"5-globe sustainability")
            elif sustainability >= 4:
                score += 3
                reasons.append(f"4-globe sustainability")
            elif sustainability >= 3:
                score += 1
                reasons.append(f"Avg sustainability ({sustainability} globes)")
            elif sustainability < 3:
                score -= 1
                reasons.append("Below avg sustainability")
        else:
            reasons.append("No sustainability rating")

        # Check for ESG-focused funds
        combined = f"{category} {name} {family}".upper()
        esg_keywords = ["ESG", "SUSTAINABLE", "CLEAN", "GREEN", "SOCIAL", 
                       "GOVERNANCE", "ENVIRONMENTAL", "CARBON", "CLIMATE"]
        
        esg_count = sum(1 for kw in esg_keywords if kw in combined)
        
        if esg_count >= 2:
            score += 3
            reasons.append("ESG-focused fund")
        elif esg_count == 1:
            score += 1
            reasons.append("ESG considerations")

        return min(max(score, 0), 10), "; ".join(reasons[:4])

    @staticmethod
    def analyze_fund(fund_data: dict) -> dict:
        """
        Run all 10 strategies on a mutual fund and return comprehensive analysis.

        Args:
            fund_data (dict): Fund data dictionary from MutualFundDataFetcher

        Returns:
            dict: Analysis results with scores and reasons for each strategy
        """
        if not fund_data:
            return {"error": "No fund data provided"}

        strategies = {
            "cost_efficiency": MutualFundStrategies.score_cost_efficiency(fund_data),
            "performance_score": MutualFundStrategies.score_performance(fund_data),
            "manager_quality": MutualFundStrategies.score_manager_quality(fund_data),
            "risk_adjusted": MutualFundStrategies.score_risk_adjusted(fund_data),
            "diversification": MutualFundStrategies.score_diversification(fund_data),
            "tax_efficiency": MutualFundStrategies.score_tax_efficiency(fund_data),
            "fund_quality": MutualFundStrategies.score_fund_quality(fund_data),
            "growth_score": MutualFundStrategies.score_growth(fund_data),
            "income_score": MutualFundStrategies.score_income(fund_data),
            "esg_score": MutualFundStrategies.score_esg(fund_data),
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
