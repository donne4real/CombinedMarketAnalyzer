import os
import re

def main():
    base_dir = r"c:\Users\leyea\Documents\VibeCoding\Qwen\CombinedMarketAnalyzer"
    
    apps = [
        {"dir": "stock_src", "fetch_method": "fetch_stock_data", "cache_file": "stock_cache.json"},
        {"dir": "etf_src", "fetch_method": "fetch_etf_data", "cache_file": "etf_cache.json"},
        {"dir": "mf_src", "fetch_method": "fetch_fund_data", "cache_file": "mf_cache.json"},
        {"dir": "bagger_src", "fetch_method": "fetch_stock_data", "cache_file": "bagger_cache.json"},
    ]
    
    for app in apps:
        filepath = os.path.join(base_dir, app["dir"], "data_fetcher.py")
        if not os.path.exists(filepath):
            continue
            
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # 1. Replace Imports and add shared_src
        content = re.sub(
            r"(import yfinance as yf\n)", 
            r"\1from shared_src.base_fetcher import BaseDataFetcher, safe_get_numeric, RATE_LIMIT_DELAY\n", 
            content
        )

        # 2. Remove old cache constants
        content = re.sub(r"# Cache configuration(.*?)(?=class )", "\n\n", content, flags=re.DOTALL)
        
        # 3. Change Class definition
        class_name_match = re.search(r"class (\w+DataFetcher)\b", content)
        if not class_name_match:
            continue
        class_name = class_name_match.group(1)
        
        content = re.sub(
            rf"class {class_name}:",
            rf"class {class_name}(BaseDataFetcher):",
            content
        )

        # 4. Replace __init__ and remove internal cache methods
        # This regex matches from __init__ until the exact definition of the specific fetch method
        fetch_method = app["fetch_method"]
        content = re.sub(
            rf"    def __init__\(self\).*?(?=    def {fetch_method}\(self, ticker: str\))",
            f"""    def __init__(self):
        super().__init__("{app['cache_file']}")

""",
            content,
            flags=re.DOTALL
        )

        # 5. Remove 'def safe_get_numeric' inner function
        content = re.sub(
            r"            def safe_get_numeric\(data, key, default=None\):.*?except \(ValueError, TypeError\):\n                    return default\n\n",
            r"",
            content,
            flags=re.DOTALL
        )

        # 6. Change method signature so it's compliant with the base class (optional, but let's map it via fetch_data)
        # We will just rename `fetch_xxx_data` to `fetch_data` to match BaseDataFetcher.
        content = re.sub(rf"def {fetch_method}\(self, ticker: str\)", r"def fetch_data(self, ticker: str)", content)
        
        # 7. Remove `fetch_multiple_*` and `clear_cache`
        # Matches from fetch_multiple_* down to the next top-level function `def ` or the `if __name__` block
        content = re.sub(
            r"    def fetch_multiple.*?def get_.*?\(",
            lambda m: "\n\ndef " + m.group(0).split("def ")[-1],
            content,
            flags=re.DOTALL
        )

        # Handle the case where clear_cache is right before if __name__ instead of get_*
        content = re.sub(
            r"    def fetch_multiple.*?(?=\nif __name__ == )",
            "",
            content,
            flags=re.DOTALL
        )
        content = re.sub(r"    def clear_cache\(self\):.*?(?=\n\n(?:def|if))", "", content, flags=re.DOTALL)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
            
        print(f"Refactored {filepath}")

if __name__ == "__main__":
    main()
