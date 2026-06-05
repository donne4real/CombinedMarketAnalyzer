# Changelog

All notable changes to the **Combined Market Analyzer** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### ✨ Added

- **Configurable Rate Limiting**: Added a sidebar slider in the main app to configure the API rate limit delay (0.5s to 10s). This allows users to balance speed vs. rate limit safety based on their needs. The delay can also be set via the `RATE_LIMIT_DELAY` environment variable.
- **Shared UI Helpers**: Created `shared_src/ui_helpers.py` with reusable UI components:
  - `render_page_header()` - Consistent page headers
  - `render_strategy_card()` - Strategy display cards
  - `render_total_score()` - Total score display
  - `render_metric_card()` - Metric cards
  - `render_progress_bar()` - Styled progress bars
  - `render_info_box()` - Info/warning/error boxes
- **Enums Module**: Created `shared_src/enums.py` with:
  - `AssetType` enum for asset types (STOCK, ETF, MUTUAL_FUND)
  - `CacheConfig` constants
  - `StrategyNames` constants for all strategy names
  - `DataFields` constants for data field names
  - `ErrorMessages` constants for error messages

### 🔧 Changed

- **Fixed Hardcoded Paths**: Updated all utility scripts (`refactor_fetchers.py`, `update_calls.py`, `update_yf_calls.py`, `add_uploader.py`) to use dynamic paths relative to the script location instead of hardcoded Windows paths. This makes the scripts portable across different operating systems and user directories.
- **Improved Error Handling**: 
  - Enhanced `app.py` with better error messages for market data fetching, including specific handling for network errors and rate limits
  - Updated `ai_summary.py` to show Streamlit warnings when OpenAI API key is missing or when AI summary generation fails
- **Watchlist Manager**: Updated to use `AssetType` enum for type safety and better code organization
- **Base Fetcher**: Made rate limiting delay configurable through constructor parameter, environment variable, or Streamlit session state

### 🧪 Testing

- **Added Comprehensive Test Suite**: Created `tests/` directory with:
  - `test_watchlist_manager.py` - Tests for watchlist functionality (add/remove tickers, persistence, edge cases)
  - `test_base_fetcher.py` - Tests for base fetcher (caching, cache validity, safe numeric extraction)
  - `test_strategies.py` - Tests for all investment strategies (Piotroski F-Score, Benjamin Graham, Magic Formula, etc.)
  - `test_data_fetchers.py` - Tests for data fetchers with mocked yfinance

### 📚 Documentation

- **Added CONTRIBUTING.md**: Comprehensive contribution guide including:
  - Project structure overview
  - Getting started instructions
  - Adding new features/strategies
  - Testing guidelines
  - Code style guide
  - Pull request template
  - Issue reporting template
- **Added CHANGELOG.md**: This file to track all changes

### 🐛 Fixed

- **Path Portability**: Fixed hardcoded Windows paths that prevented scripts from running on other operating systems
- **Error Visibility**: Improved error messages to be more visible and helpful to users
- **Cache Behavior**: Documented cache behavior and made it more configurable

---

## [1.0.0] - 2024-06-05

### ✨ Initial Release

The first public release of **Combined Market Analyzer** with the following features:

#### Core Features
- **Unified Dashboard**: Single Streamlit application with navigation across all modules
- **Cross-Asset Watchlist**: Track stocks, ETFs, and mutual funds in one place with global caching
- **Global Caching**: Data fetched in one module is instantly available in the watchlist

#### Asset Modules
1. **Stock Market Analyzer**
   - 10 sophisticated investment strategies:
     - Benjamin Graham Value
     - Magic Formula (Greenblatt)
     - Piotroski F-Score
     - Altman Z-Score
     - Dividend Discount Model
     - PEG Ratio
     - Price to Book
     - Price to Earnings
     - Return on Equity
     - Debt to Equity
   - Backtesting functionality
   - Export to Excel/CSV

2. **ETF Analyzer**
   - Deep analysis of Exchange Traded Funds
   - Asset allocation analysis
   - Dividend consistency tracking
   - Tracking error measurement
   - Risk-adjusted performance comparison
   - Top 10 holdings concentration analysis

3. **Mutual Fund Screener**
   - Screen and track top mutual funds
   - Expense ratio analysis
   - Long-term return analysis
   - Top 10 holding concentrations
   - Risk metrics

4. **100-Bagger Screener**
   - Hunt for high-growth opportunities
   - Peter Lynch-inspired criteria:
     - Low PEG ratios
     - High ROE
     - Robust operating cash flows
     - Founder-led organizations
   - Predict massive multipliers

#### Technical Features
- **Intelligent Caching**: 24-hour JSON caching with SQLite backend for yfinance
- **Rate Limiting**: Conservative 1 request per 2 seconds with User-Agent rotation
- **Error Handling**: Graceful fallbacks to cached data on errors
- **AI Summaries**: OpenAI integration for plain-English summaries (optional)

#### Deployment
- **Streamlit Community Cloud Ready**: Zero-configuration deployment
- **Detailed Documentation**: README.md and DEPLOYMENT.md with step-by-step guides

---

## 📋 Format Guide

### Types of Changes

- `Added` - for new features
- `Changed` - for changes in existing functionality
- `Deprecated` - for soon-to-be removed features
- `Removed` - for now removed features
- `Fixed` - for any bug fixes
- `Security` - in case of vulnerabilities

### Sections

- `Unreleased` - for changes not yet released
- `[Version]` - for released versions (use SemVer)

### Categories

Each version can have:
- ✨ Added
- 🔧 Changed
- 🐛 Fixed
- 📚 Documentation
- 🧪 Testing
- 🚀 Performance
- 🎨 UI/UX
