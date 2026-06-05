# Contributing to CombinedMarketAnalyzer

Thank you for your interest in contributing to the **Combined Market Analyzer**! This document provides guidelines for contributing to the project.

---

## 📋 Table of Contents

- [Getting Started](#-getting-started)
- [Project Structure](#-project-structure)
- [Adding New Features](#-adding-new-features)
- [Adding New Strategies](#-adding-new-strategies)
- [Testing](#-testing)
- [Code Style](#-code-style)
- [Pull Request Guidelines](#-pull-request-guidelines)
- [Reporting Issues](#-reporting-issues)

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- Git

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/donne4real/CombinedMarketAnalyzer.git
   cd CombinedMarketAnalyzer
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   streamlit run app.py
   ```

---

## 🗂️ Project Structure

```
CombinedMarketAnalyzer/
├── app.py                      # Main Streamlit application entry point
├── requirements.txt             # Python dependencies
├── README.md                   # Project overview
├── DEPLOYMENT.md               # Deployment instructions
├── CONTRIBUTING.md             # This file
├── CHANGELOG.md                # Change history
│
├── pages/                      # Streamlit pages
│   ├── 1_Stock_Market.py        # Stock analysis page
│   ├── 2_ETF_Analyzer.py        # ETF analysis page
│   ├── 3_Mutual_Funds.py        # Mutual fund analysis page
│   ├── 4_100_Bagger_Screener.py # 100-bagger screener page
│   └── 5_Watchlist.py           # Cross-asset watchlist page
│
├── shared_src/                 # Shared source code
│   ├── __init__.py
│   ├── base_fetcher.py         # Base data fetcher with caching & rate limiting
│   ├── enums.py                # Enums and constants
│   ├── ui_helpers.py           # Reusable UI components
│   ├── visuals.py              # Visualization helpers
│   ├── watchlist_manager.py    # Watchlist persistence manager
│   └── ai_summary.py           # AI-powered summary generation
│
├── stock_src/                  # Stock-specific code
│   ├── __init__.py
│   ├── data_fetcher.py         # Stock data fetcher
│   ├── strategies.py           # Stock investment strategies
│   ├── backtester.py           # Backtesting for stocks
│   └── exporter.py             # Export functionality for stocks
│
├── etf_src/                    # ETF-specific code
│   ├── __init__.py
│   ├── data_fetcher.py         # ETF data fetcher
│   ├── strategies.py           # ETF investment strategies
│   ├── backtester.py           # Backtesting for ETFs
│   └── exporter.py             # Export functionality for ETFs
│
├── mf_src/                     # Mutual Fund-specific code
│   ├── __init__.py
│   ├── data_fetcher.py         # Mutual fund data fetcher
│   ├── strategies.py           # Mutual fund investment strategies
│   ├── backtester.py           # Backtesting for mutual funds
│   └── exporter.py             # Export functionality for mutual funds
│
├── bagger_src/                 # 100-Bagger screener code
│   ├── __init__.py
│   ├── data_fetcher.py         # 100-bagger data fetcher
│   ├── strategies.py           # 100-bagger screening strategies
│   ├── backtester.py           # Backtesting for 100-baggers
│   └── exporter.py             # Export functionality for 100-baggers
│
└── tests/                      # Unit and integration tests
    ├── __init__.py
    ├── test_base_fetcher.py    # Tests for base fetcher
    ├── test_watchlist_manager.py # Tests for watchlist manager
    ├── test_strategies.py       # Tests for investment strategies
    └── test_data_fetchers.py    # Tests for data fetchers
```

---

## ✨ Adding New Features

### 1. Adding a New Asset Type

To add support for a new asset type (e.g., Cryptocurrencies, Bonds):

1. **Create a new source directory:**
   ```bash
   mkdir crypto_src
   ```

2. **Add the required files:**
   - `data_fetcher.py` - Data fetching logic (inherit from `BaseDataFetcher`)
   - `strategies.py` - Investment strategies for the asset type
   - `backtester.py` - Backtesting functionality
   - `exporter.py` - Export functionality
   - `__init__.py` - Package initialization

3. **Update the watchlist manager:**
   - Add the new asset type to the `AssetType` enum in `shared_src/enums.py`
   - Update the default watchlist structure in `shared_src/watchlist_manager.py`

4. **Create a new page:**
   - Add a new file to the `pages/` directory (e.g., `6_Crypto_Analyzer.py`)
   - Follow the pattern of existing pages

5. **Update the main app:**
   - Add navigation links to the new page in `app.py`

### 2. Adding a New Strategy

To add a new investment strategy:

1. **Identify the asset type** the strategy applies to (stocks, ETFs, mutual funds, or 100-baggers)

2. **Add the strategy to the appropriate `strategies.py` file:**
   ```python
   def calculate_new_strategy(self, data: dict) -> dict:
       """
       Calculate the new strategy score.
       
       Args:
           data: Dictionary containing asset data
           
       Returns:
           dict: {"score": float (0-10), "reason": str}
       """
       # Your calculation logic here
       score = 0.0
       reason = ""
       
       # Example: Calculate based on some metric
       if data.get("roe", 0) > 0.20:
           score = 10.0
           reason = "Excellent return on equity"
       elif data.get("roe", 0) > 0.15:
           score = 7.5
           reason = "Good return on equity"
       else:
           score = 5.0
           reason = "Average return on equity"
       
       return {"score": score, "reason": reason}
   ```

3. **Register the strategy in the `get_all_strategies` method:**
   ```python
   def get_all_strategies(self) -> dict:
       """Get all strategies with their scores and reasons."""
       strategies = {
           # ... existing strategies ...
           "New Strategy": self.calculate_new_strategy(self.data),
       }
       
       # Calculate total score
       strategies["total_score"] = self._calculate_total_score(strategies)
       
       return strategies
   ```

4. **Add the strategy name to `shared_src/enums.py`:**
   ```python
   class StrategyNames:
       # ... existing names ...
       NEW_STRATEGY = "New Strategy"
   ```

5. **Add tests for the new strategy** in `tests/test_strategies.py`

---

## 🧪 Testing

### Running Tests

To run all tests:
```bash
pytest tests/
```

To run a specific test file:
```bash
pytest tests/test_strategies.py
```

To run with verbose output:
```bash
pytest -v tests/
```

To run with coverage:
```bash
pytest --cov=./ --cov-report=html tests/
```

### Writing Tests

1. **Unit Tests:** Test individual functions in isolation
2. **Integration Tests:** Test interactions between components
3. **Mocking:** Use `unittest.mock` to mock external dependencies (e.g., yfinance)

Example test structure:
```python
import pytest
from unittest.mock import patch, MagicMock

def test_strategy_calculation():
    """Test a strategy calculation with mock data."""
    from stock_src.strategies import InvestmentStrategies
    
    mock_data = {
        "symbol": "TEST",
        "roe": 0.25,
        "pe_ratio": 15.0,
    }
    
    strategies = InvestmentStrategies(mock_data)
    results = strategies.get_all_strategies()
    
    assert "New Strategy" in results
    assert 0 <= results["New Strategy"]["score"] <= 10
```

---

## 🎨 Code Style

### Python Style

- Follow **PEP 8** guidelines
- Use **type hints** for function signatures
- Use **docstrings** for all public functions and classes
- Use **snake_case** for variables and functions
- Use **PascalCase** for classes
- Use **UPPER_CASE** for constants

### Streamlit Style

- Use **consistent spacing** (2 blank lines between sections)
- Use **descriptive labels** for inputs and buttons
- Use **emojis** sparingly and consistently
- Use **st.divider()** to separate sections
- Use **st.columns()** for multi-column layouts

### Documentation

- Use **Google-style docstrings**
- Document **all parameters** and **return values**
- Include **examples** in docstrings where helpful
- Use **type hints** for better IDE support

Example:
```python
def calculate_pe_ratio(data: dict) -> float:
    """
    Calculate the Price-to-Earnings ratio.
    
    Args:
        data: Dictionary containing stock data with 'price' and 'eps' keys
        
    Returns:
        float: The P/E ratio, or None if data is insufficient
        
    Example:
        >>> data = {"price": 100.0, "eps": 5.0}
        >>> calculate_pe_ratio(data)
        20.0
    """
    price = data.get("price")
    eps = data.get("eps")
    
    if price and eps and eps != 0:
        return price / eps
    return None
```

---

## 📝 Pull Request Guidelines

### Before Submitting

1. **Run tests:** Ensure all existing tests pass
   ```bash
   pytest tests/
   ```

2. **Add tests:** Add tests for new functionality

3. **Check code style:** Run a linter (e.g., flake8, pylint)

4. **Update documentation:** Update relevant documentation files

5. **Update CHANGELOG:** Add an entry to `CHANGELOG.md`

### Pull Request Template

```markdown
## 📌 Description

[Brief description of the changes]

## ✅ Changes Made

- [ ] Added new feature: [description]
- [ ] Fixed bug: [description]
- [ ] Improved performance: [description]
- [ ] Updated documentation: [description]
- [ ] Added tests: [description]

## 🧪 Testing

- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## 📝 Notes

[Any additional notes or context]
```

### Commit Messages

Use **conventional commits** format:

- `feat: Add new strategy for value investing`
- `fix: Correct PE ratio calculation bug`
- `docs: Update README with deployment instructions`
- `refactor: Extract common UI components`
- `test: Add tests for watchlist manager`
- `chore: Update dependencies`

---

## 🐛 Reporting Issues

When reporting issues, please include:

1. **Description:** Clear description of the issue
2. **Steps to Reproduce:** How to trigger the issue
3. **Expected Behavior:** What should happen
4. **Actual Behavior:** What actually happens
5. **Screenshots:** If applicable
6. **Environment:**
   - Python version
   - Operating system
   - Browser (for Streamlit issues)
   - Any relevant configuration

---

## 📚 Additional Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [yfinance Documentation](https://pypi.org/project/yfinance/)
- [PEP 8 Style Guide](https://peps.python.org/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)

---

## 🙏 Thank You!

Your contributions help make the Combined Market Analyzer better for everyone. Thank you for your time and effort!

If you have any questions, please open an issue or discussion on GitHub.
