# Quick Start Guide

## Installation

```bash
# Clone repository
git clone https://github.com/kangrills/nifty_expiry_predictor.git
cd nifty_expiry_predictor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running the Demo

The fastest way to see the system in action:

```bash
python scripts/demo.py
```

This will demonstrate:
- Greeks calculation (Delta, Gamma, Theta, Vega)
- Gamma Exposure (GEX) analysis
- Max Pain calculation
- Open Interest (OI) analysis
- Put-Call Ratio (PCR)

## Using the Library

### 1. Calculate Greeks

```python
from features.greeks_calculator import GreeksCalculator

calc = GreeksCalculator(risk_free_rate=0.07)
greeks = calc.calculate_greeks(
    spot=19500,
    strike=19500,
    time_to_expiry=7/365,  # 7 days
    volatility=0.20,
    option_type="call"
)

print(f"Delta: {greeks.delta:.4f}")
print(f"Gamma: {greeks.gamma:.6f}")
```

### 2. Calculate GEX

```python
from features.gex_calculator import GammaExposureCalculator

gex_calc = GammaExposureCalculator()
gex_df = gex_calc.calculate_chain_gex(
    option_chain=option_chain_df,
    spot=19500,
    days_to_expiry=7
)

levels = gex_calc.find_gex_levels(gex_df, 19500)
print(f"GEX Regime: {levels['gex_regime']}")
```

### 3. Calculate Max Pain

```python
from features.max_pain import MaxPainCalculator

mp_calc = MaxPainCalculator()
max_pain, pain_df = mp_calc.calculate_max_pain(option_chain_df)

print(f"Max Pain: {max_pain}")
```

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_greeks.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
nano .env
```

Key settings:
- `TRADING_MODE`: Set to `paper` or `live`
- `MAX_DAILY_LOSS`: Maximum daily loss limit
- Broker API credentials (if using live data)

## Next Steps

1. **Explore Notebooks**: See `notebooks/01_data_exploration.ipynb`
2. **Run Dashboard**: `streamlit run dashboard/app.py`
3. **Read Documentation**: See `README.md` for detailed information
4. **Download Historical Data**: `python scripts/download_historical.py --start-date 2024-01-01`

## Common Issues

### ModuleNotFoundError

Make sure you've installed all dependencies:
```bash
pip install -r requirements.txt
```

### Database Connection Error

If you're not using PostgreSQL/Redis:
- The system will work without them for basic features
- Database is only needed for storing historical data
- Redis is optional for caching

### NSE Data Fetch Issues

- NSE may block frequent requests
- Add delays between requests
- Consider using broker APIs for live data

## Support

- Open an issue on GitHub
- Check existing issues and discussions
- Review the full README.md for detailed documentation
