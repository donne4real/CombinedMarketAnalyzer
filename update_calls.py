import os
import re
from pathlib import Path

def main():
    # Use dynamic path relative to this script
    base_dir = Path(__file__).parent
    
    replacements = [
        (r"\.fetch_stock_data\(", ".fetch_data("),
        (r"\.fetch_etf_data\(", ".fetch_data("),
        (r"\.fetch_fund_data\(", ".fetch_data("),
        (r"\.fetch_multiple_stocks\(", ".fetch_multiple("),
        (r"\.fetch_multiple_etfs\(", ".fetch_multiple("),
        (r"\.fetch_multiple_funds\(", ".fetch_multiple("),
    ]
    
    for root, _, files in os.walk(base_dir):
        # Exclude hidden folders and cache
        root_path = Path(root)
        if any(part.startswith('.') for part in root_path.parts):
            continue
            
        for file in files:
            if not file.endswith(".py"):
                continue
            
            filepath = root_path / file
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            new_content = content
            for old_pattern, new_pattern in replacements:
                new_content = re.sub(old_pattern, new_pattern, new_content)
                
            if new_content != content:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"Updated {filepath}")

    print("Replacement complete.")

if __name__ == "__main__":
    from pathlib import Path
    main()
