# 📈 Combined Market Analyzer

A unified, comprehensive intelligence platform designed to analyze Stocks, ETFs, Mutual Funds, and hunt for 100-Bagger opportunities—all from a single, fast Streamlit dashboard.

---

## 🚀 Features

The **Combined Market Analyzer** merges 4 powerful financial tools into one cohesive application, complete with cross-asset Watchlist tracking and global caching.

### 1. Stock Market Analyzer
Run deep fundamental and technical analysis on individual stocks using 10 sophisticated investment models:
- Benjamin Graham Value
- Magic Formula
- Piotroski F-Score
- Altman Z-Score
- Dividend Discount Model
- ..and 5 more.

### 2. ETF Analyzer
Dive deep into Exchange Traded Funds. Understand their asset allocations, dividend consistency, tracking error, and risk-adjusted performances compared to the broader market.

### 3. Mutual Fund Screener
Screen and track top industry Mutual Funds. Analyze expense ratios, long term returns, and top 10 holding concentrations quickly.

### 4. 100-Bagger Screener
Hunt for the next high-growth unicorn. Scans for low PEGs, high ROE, robust operating cash flows and founder-led organizations to predict massive multipliers.

### 📋 Cross-Asset Watchlist
Track your favorite Stocks, ETFs, and Mutual Funds all in a single place. The application features **Global Caching**, meaning data fetched on one page is instantly available on your Watchlist.

---

## 🛠️ Installation & Setup

1. **Clone the repository:**
```bash
git clone https://github.com/YOUR_USERNAME/CombinedMarketAnalyzer.git
cd CombinedMarketAnalyzer
```

2. **Install the dependencies:**
Using `pip`, install the required Python libraries.
```bash
pip install -r requirements.txt
```

3. **Run the Streamlit Dashboard:**
```bash
streamlit run app.py
```
*The dashboard will automatically open in your default web browser.*

---

## ☁️ Deployment

This project is fully structured to be deployed instantly on **Streamlit Community Cloud** with zero configuration required. 

See the detailed instructions in [DEPLOYMENT.md](DEPLOYMENT.md) for how to get your app live in under 2 minutes!

---

## 💾 Caching & Performance

The Combined Market Analyzer uses intelligent caching to minimize API calls and improve performance:

### Cache Behavior
- **24-hour cache**: All fetched data is cached for 24 hours in JSON format
- **SQLite cache**: yfinance requests are cached in SQLite for 1 hour
- **Global cache**: Data fetched in one module is instantly available in the watchlist
- **Cache location**: `~/.qwen_combined_analyzer/cache/` (or temp directory in Streamlit Cloud)

### Rate Limiting
- **Configurable delay**: API requests have a configurable delay (default: 2 seconds)
- **User-Agent rotation**: Automatically rotates user agents to avoid blocks
- **Exponential backoff**: Increases delay after consecutive failures
- **Cooling off**: 60-second pause after 15 consecutive failures

### Configuration
You can configure the rate limit delay in three ways:
1. **Streamlit sidebar**: Use the slider in the main app (0.5s - 10s)
2. **Environment variable**: Set `RATE_LIMIT_DELAY` (in seconds)
3. **Session state**: Set `st.session_state.rate_limit_delay`

Lower values = faster but more likely to hit rate limits
Higher values = slower but more reliable

---
*Built using `streamlit`, `pandas`, and `yfinance`.*
