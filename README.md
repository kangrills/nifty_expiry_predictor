# Nifty Weekly Expiry Predictor 📈

A production-grade quantitative trading system for predicting Nifty weekly expiry levels using Gamma Exposure (GEX), Max Pain, Open Interest analysis, and Machine Learning models.

## 🚀 Features

- **Real-time Data Collection**: Fetch live option chain data from NSE India
- **Advanced Analytics**:
  - Gamma Exposure (GEX) calculation and regime identification
  - Max Pain calculation with support/resistance levels
  - Open Interest (OI) analysis with PCR calculations
  - Black-Scholes Greeks calculation (Delta, Gamma, Theta, Vega, Rho)
- **Trading Strategies**: Iron Condor, Straddle/Strangle, Gamma Scalping
- **ML Models**: XGBoost and LSTM for expiry prediction
- **Interactive Dashboard**: Real-time Streamlit dashboard with visualizations
- **Broker Integration**: Support for Zerodha, Upstox, and Angel One
- **Risk Management**: Position limits, stop-loss, and daily loss controls
- **Alerts**: Telegram and email notifications

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [Dashboard](#dashboard)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Key Formulas](#key-formulas)
- [Contributing](#contributing)
- [License](#license)

## 🛠️ Installation

### Prerequisites

- Python 3.9 or higher
- PostgreSQL (optional, for data storage)
- Redis (optional, for caching)

### Local Installation

```bash
# Clone the repository
git clone https://github.com/kangrills/nifty_expiry_predictor.git
cd nifty_expiry_predictor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .

# For development
pip install -r requirements-dev.txt
```

### Docker Installation

```bash
# Build and start services
docker-compose up -d

# The dashboard will be available at http://localhost:8501
```

## ⚡ Quick Start

### 1. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
nano .env
```

### 2. Fetch Option Chain Data

```python
from data.collectors.nse_scraper import NSEDataCollector

# Initialize collector
nse = NSEDataCollector()

# Fetch NIFTY option chain
option_chain = nse.get_option_chain("NIFTY")
spot = option_chain.attrs['underlying']

print(f"Spot Price: {spot}")
print(f"Number of strikes: {len(option_chain)}")
```

### 3. Calculate GEX and Max Pain

```python
from features.gex_calculator import GammaExposureCalculator
from features.max_pain import MaxPainCalculator

# Calculate GEX
gex_calc = GammaExposureCalculator()
gex_df = gex_calc.calculate_chain_gex(option_chain, spot, days_to_expiry=1)
levels = gex_calc.find_gex_levels(gex_df, spot)

print(f"GEX Regime: {levels['gex_regime']}")
print(f"Trading Bias: {levels['trading_bias']}")

# Calculate Max Pain
mp_calc = MaxPainCalculator()
max_pain, pain_df = mp_calc.calculate_max_pain(option_chain)

print(f"Max Pain: {max_pain}")
print(f"Distance from Spot: {spot - max_pain}")
```

## ⚙️ Configuration

### Environment Variables

Edit `.env` file with your settings:

```bash
# Broker API Credentials
ZERODHA_API_KEY=your_api_key
ZERODHA_API_SECRET=your_api_secret

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/nifty_expiry
REDIS_URL=redis://localhost:6379/0

# Trading Configuration
TRADING_MODE=paper  # paper or live
MAX_DAILY_LOSS=50000
MAX_POSITION_SIZE=10

# Alerts
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

## 📊 Usage Examples

### Greeks Calculation

```python
from features.greeks_calculator import GreeksCalculator

calc = GreeksCalculator(risk_free_rate=0.07)

# Calculate Greeks for a call option
greeks = calc.calculate_greeks(
    spot=19500,
    strike=19500,
    time_to_expiry=7/365,  # 7 days
    volatility=0.20,
    option_type="call"
)

print(f"Delta: {greeks.delta:.4f}")
print(f"Gamma: {greeks.gamma:.6f}")
print(f"Theta: {greeks.theta:.4f}")
print(f"Vega: {greeks.vega:.4f}")
```

### Open Interest Analysis

```python
from features.oi_analysis import OIAnalyzer

analyzer = OIAnalyzer()

# Calculate PCR
pcr = analyzer.calculate_pcr(option_chain, method='oi')
sentiment = analyzer.interpret_pcr(pcr)

print(f"Put-Call Ratio: {pcr:.2f}")
print(f"Market Sentiment: {sentiment}")

# Find OI walls
walls = analyzer.find_call_put_walls(option_chain, num_walls=5)
print(f"Call Walls: {walls['call_walls']}")
print(f"Put Walls: {walls['put_walls']}")
```

## 🎨 Dashboard

Launch the interactive Streamlit dashboard:

```bash
# Using make
make dashboard

# Or directly
streamlit run dashboard/app.py
```

The dashboard provides:
- Real-time option chain display
- GEX profile visualization
- Max Pain curve
- OI distribution heatmaps
- PCR analysis
- Support and resistance levels

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_greeks.py -v

# Run with coverage
pytest --cov=. --cov-report=html
```

## 📁 Project Structure

```
nifty_expiry_predictor/
│
├── config/                      # Configuration modules
│   ├── settings.py             # Application settings
│   ├── logging_config.py       # Logging configuration
│   └── constants.py            # Trading constants
│
├── data/                       # Data layer
│   ├── collectors/             # Data collection
│   │   ├── nse_scraper.py     # NSE data scraper
│   │   └── broker_api.py      # Broker API interfaces
│   └── storage/                # Data storage
│       ├── database.py        # PostgreSQL connection
│       └── cache.py           # Redis cache
│
├── features/                   # Feature engineering
│   ├── greeks_calculator.py   # Black-Scholes Greeks
│   ├── gex_calculator.py      # Gamma Exposure
│   ├── max_pain.py            # Max Pain calculation
│   └── oi_analysis.py         # Open Interest analysis
│
├── models/                     # ML models
│   ├── statistical/           # Statistical models
│   ├── ml/                    # Machine learning models
│   └── training/              # Training pipeline
│
├── strategies/                 # Trading strategies
│   ├── base_strategy.py       # Base strategy class
│   ├── iron_condor.py         # Iron Condor strategy
│   ├── straddle_strangle.py   # Straddle/Strangle
│   └── gamma_scalping.py      # Gamma scalping
│
├── dashboard/                  # Streamlit dashboard
│   └── app.py                 # Main dashboard app
│
├── tests/                      # Test suite
│   ├── test_greeks.py         # Greeks tests
│   ├── test_gex.py            # GEX tests
│   └── test_max_pain.py       # Max Pain tests
│
└── scripts/                    # Utility scripts
```

## 📐 Key Formulas

### Gamma Exposure (GEX)

```
GEX = Gamma × OI × Lot Size × Spot² × 0.01

Call GEX = Positive (dealer is short gamma)
Put GEX = Negative (dealer is long gamma)
Net GEX = Call GEX + Put GEX
```

**GEX Regime Interpretation:**
- **Positive GEX**: Market tends to be mean-reverting (dealers hedge by buying dips, selling rallies)
- **Negative GEX**: Market tends to be trending (dealers amplify moves)

### Max Pain

```
For each settlement price:
  Call Loss = Σ(max(0, settlement - strike) × call_oi)
  Put Loss = Σ(max(0, strike - settlement) × put_oi)
  Total Pain = Call Loss + Put Loss

Max Pain = Strike with minimum Total Pain
```

### Black-Scholes Greeks

```
d1 = [ln(S/K) + (r + σ²/2)T] / (σ√T)
d2 = d1 - σ√T

Delta (Call) = N(d1)
Delta (Put) = N(d1) - 1

Gamma = N'(d1) / (S × σ × √T)

Theta (Call) = [-S × N'(d1) × σ / (2√T) - r × K × e^(-rT) × N(d2)] / 365
Theta (Put) = [-S × N'(d1) × σ / (2√T) + r × K × e^(-rT) × N(-d2)] / 365

Vega = S × N'(d1) × √T / 100
```

Where:
- S = Spot price
- K = Strike price
- T = Time to expiry (years)
- σ = Volatility
- r = Risk-free rate
- N(x) = Cumulative normal distribution
- N'(x) = Normal probability density function

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This software is for educational and research purposes only. Trading derivatives involves substantial risk of loss. Past performance is not indicative of future results. Always do your own research and consult with a licensed financial advisor before making trading decisions.

## 📞 Support

For issues, questions, or contributions, please:
- Open an issue on GitHub
- Check the documentation
- Review existing issues and discussions

## 🙏 Acknowledgments

- NSE India for providing market data
- The open-source Python community
- Contributors to NumPy, Pandas, and SciPy

---

**Built with ❤️ for the quant trading community**