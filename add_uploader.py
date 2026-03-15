import os
import re

def main():
    base_dir = r"c:\Users\leyea\Documents\VibeCoding\Qwen\CombinedMarketAnalyzer"
    pages_dir = os.path.join(base_dir, "pages")
    
    # We want to replace the custom_tickers block
    old_block = r'''        custom_tickers = ""
        if (stock_universe|universe|fund_universe) == "Custom Tickers":
            custom_tickers = st\.text_area\([\s\S]*?height=100\n            \)'''
            
    new_block = r'''        custom_tickers = ""
        if \1 == "Custom Tickers":
            uploaded_file = st.file_uploader("Upload CSV/TXT of Tickers", type=["csv", "txt"], help="Upload a file with one ticker per line, or comma-separated.")
            if uploaded_file is not None:
                try:
                    df = pd.read_csv(uploaded_file, header=None)
                    # Flatten in case of multiple columns, but usually it's just one
                    file_tickers = []
                    for col in df.columns:
                        file_tickers.extend(df[col].dropna().astype(str).tolist())
                    custom_tickers = ",".join(file_tickers)
                    st.success(f"Loaded {len(file_tickers)} tickers from file!")
                except Exception as e:
                    st.error(f"Error reading file: {e}")
                    
            custom_tickers = st.text_area(
                "Or manually enter/edit tickers (comma-separated)",
                value=custom_tickers,
                placeholder="AAPL, MSFT, GOOGL, TSLA",
                height=100
            )'''

    for file in os.listdir(pages_dir):
        if not file.endswith(".py") or "Watchlist" in file:
            continue
            
        filepath = os.path.join(pages_dir, file)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Also let's check if the file has "import pandas as pd"
        if "import pandas as pd" not in content:
            content = content.replace("import streamlit as st", "import streamlit as st\nimport pandas as pd")
            
        new_content = re.sub(old_block, new_block, content)
        
        if new_content != content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"Updated CSV uploader in {file}")

if __name__ == "__main__":
    main()
