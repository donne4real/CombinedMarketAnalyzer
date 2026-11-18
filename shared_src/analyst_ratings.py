"""
Analyst Ratings Module

Fetches and displays analyst recommendations, price targets, and recent
upgrades/downgrades from Yahoo Finance.

Features:
- Consensus ratings (Buy/Hold/Sell)
- Average price targets with upside potential
- Recent analyst actions (upgrades/downgrades)
- Number of analysts covering the stock

Classes:
    AnalystRatings: Fetches and formats analyst data

Example:
    >>> ratings = AnalystRatings()
    >>> data = ratings.fetch_ratings("AAPL")
    >>> print(f"{data['consensus']} - Target: ${data['target_price']}")
"""

import time
from typing import Optional
import yfinance as yf


class AnalystRatings:
    """
    Fetches analyst ratings and recommendations from Yahoo Finance.

    Attributes:
        cache: In-memory cache for fetched data
        cache_expiry: Cache validity time in seconds
    """

    def __init__(self, cache_expiry: int = 3600):
        self.cache = {}
        self.cache_expiry = cache_expiry

    def fetch_ratings(self, ticker: str) -> Optional[dict]:
        """
        Fetch analyst ratings for a single ticker.

        Returns:
            dict with keys:
                - consensus: str (e.g., "Buy", "Hold", "Sell")
                - num_analysts: int
                - target_price: float (average price target)
                - target_high: float (highest target)
                - target_low: float (lowest target)
                - upside_pct: float (upside to target from current price)
                - current_price: float
                - recommendations: dict (counts of Buy/Hold/Sell)
                - recent_actions: list of recent upgrades/downgrades
        """
        # Check cache
        if ticker in self.cache:
            cached_data, cached_time = self.cache[ticker]
            if time.time() - cached_time < self.cache_expiry:
                return cached_data

        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            if not info:
                return None

            # Get analyst recommendations
            recommendations = stock.recommendations
            rec_counts = {"Buy": 0, "Hold": 0, "Sell": 0, "Strong Buy": 0, "Strong Sell": 0}

            if recommendations is not None and not recommendations.empty:
                # Get most recent month's recommendations
                recent = recommendations.tail(1)
                if not recent.empty:
                    for col in recent.columns:
                        if col in rec_counts:
                            rec_counts[col] = int(recent[col].iloc[0])

            # Calculate consensus
            total_analysts = sum(rec_counts.values())
            if total_analysts > 0:
                buy_score = rec_counts.get("Strong Buy", 0) * 2 + rec_counts.get("Buy", 0)
                hold_score = rec_counts.get("Hold", 0)
                sell_score = rec_counts.get("Strong Sell", 0) * 2 + rec_counts.get("Sell", 0)

                if buy_score > hold_score and buy_score > sell_score:
                    consensus = "Buy"
                elif sell_score > hold_score and sell_score > buy_score:
                    consensus = "Sell"
                else:
                    consensus = "Hold"
            else:
                consensus = "N/A"

            # Get price targets
            target_price = info.get("targetMeanPrice") or info.get("targetMedianPrice")
            target_high = info.get("targetHighPrice")
            target_low = info.get("targetLowPrice")
            current_price = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose")
            num_analysts = info.get("numberOfAnalystOpinions", 0)

            # Calculate upside
            upside_pct = None
            if target_price and current_price and current_price > 0:
                upside_pct = ((target_price - current_price) / current_price) * 100

            # Get recent analyst actions
            recent_actions = []
            if recommendations is not None and not recommendations.empty:
                try:
                    # Get last 10 actions
                    actions_df = recommendations.tail(10)
                    for _, row in actions_df.iterrows():
                        action = {
                            "date": str(row.get("date", "")),
                            "firm": row.get("Firm", "Unknown"),
                            "to_grade": row.get("To Grade", "N/A"),
                            "from_grade": row.get("From Grade", "N/A"),
                            "action": row.get("Action", "N/A")
                        }
                        recent_actions.append(action)
                except Exception:
                    pass

            data = {
                "ticker": ticker,
                "consensus": consensus,
                "num_analysts": num_analysts or total_analysts,
                "target_price": target_price,
                "target_high": target_high,
                "target_low": target_low,
                "current_price": current_price,
                "upside_pct": upside_pct,
                "recommendations": rec_counts,
                "recent_actions": recent_actions
            }

            # Cache the result
            self.cache[ticker] = (data, time.time())
            return data

        except Exception as e:
            print(f"  [ANALYST] {ticker} - Error: {e}")
            return None

    def fetch_multiple(self, tickers: list, progress_callback=None) -> dict:
        """
        Fetch analyst ratings for multiple tickers.

        Args:
            tickers: List of ticker symbols
            progress_callback: Optional callback(current, total, ticker)

        Returns:
            dict mapping ticker -> ratings data
        """
        results = {}
        for i, ticker in enumerate(tickers):
            if progress_callback:
                progress_callback(i + 1, len(tickers), ticker)

            data = self.fetch_ratings(ticker)
            if data:
                results[ticker] = data

            # Rate limiting
            time.sleep(0.5)

        return results

    def clear_cache(self):
        """Clear the in-memory cache."""
        self.cache = {}
