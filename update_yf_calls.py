import os
import re
from pathlib import Path

def main():
    # Use dynamic path relative to this script
    base_dir = Path(__file__).parent
    
    # We want to replace yf.Ticker(ticker) with self.get_ticker_obj(ticker) in the data_fetcher files
    
    apps = ["stock_src", "etf_src", "mf_src", "bagger_src"]
    
    for app in apps:
        filepath = base_dir / app / "data_fetcher.py"
        if not filepath.exists():
            continue
            
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Simple replacement
        # Careful: it might be yf.Ticker(ticker_symbol) or yf.Ticker(ticker)
        new_content = re.sub(r'yf\.Ticker\(([^)]+)\)', r'self.get_ticker_obj(\1)', content)
        
        if new_content != content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"Updated {filepath} to use self.get_ticker_obj")

if __name__ == "__main__":
    main()
