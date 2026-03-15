import json
from pathlib import Path

# Use the same base directory as the cache
WATCHLIST_FILE = Path.home() / ".qwen_combined_analyzer" / "watchlist.json"

class WatchlistManager:
    """Manages a persistent watchlist of multi-asset tickers (Stocks, ETFs, Mutual Funds)."""
    
    def __init__(self):
        self.watchlist = self._load_watchlist()

    def _load_watchlist(self) -> dict:
        """Loads the watchlist from disk."""
        if WATCHLIST_FILE.exists():
            try:
                with open(WATCHLIST_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {"stocks": [], "etfs": [], "funds": []}
        return {"stocks": [], "etfs": [], "funds": []}

    def _save_watchlist(self):
        """Saves current watchlist to disk."""
        WATCHLIST_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(WATCHLIST_FILE, "w", encoding="utf-8") as f:
            json.dump(self.watchlist, f, indent=2)

    def add_ticker(self, asset_type: str, ticker: str) -> bool:
        """
        Adds a ticker to the given asset_type watchlist.
        Returns True if added, False if it was already there.
        """
        ticker = ticker.upper().strip()
        if asset_type not in self.watchlist:
            self.watchlist[asset_type] = []
            
        if ticker not in self.watchlist[asset_type]:
            self.watchlist[asset_type].append(ticker)
            self._save_watchlist()
            return True
        return False

    def remove_ticker(self, asset_type: str, ticker: str) -> bool:
        """
        Removes a ticker from the watchlist.
        Returns True if removed, False if it was not found.
        """
        ticker = ticker.upper().strip()
        if asset_type in self.watchlist and ticker in self.watchlist[asset_type]:
            self.watchlist[asset_type].remove(ticker)
            self._save_watchlist()
            return True
        return False

    def get_watchlist(self) -> dict:
        """Returns the full watchlist dictionary."""
        return self.watchlist

    def get_tickers_by_type(self, asset_type: str) -> list:
        """Returns a list of tickers for a specific asset type."""
        return self.watchlist.get(asset_type, [])
