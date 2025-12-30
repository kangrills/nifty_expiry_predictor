"""Trading constants for Nifty Expiry Predictor."""

from dataclasses import dataclass
from typing import Dict

# Lot sizes for Indian derivatives
LOT_SIZES: Dict[str, int] = {
    "NIFTY": 50,
    "BANKNIFTY": 25,
    "FINNIFTY": 40,
    "MIDCPNIFTY": 75,
}

# Contract multipliers
CONTRACT_MULTIPLIER = 1

# Trading hours (IST)
MARKET_OPEN_HOUR = 9
MARKET_OPEN_MINUTE = 15
MARKET_CLOSE_HOUR = 15
MARKET_CLOSE_MINUTE = 30

# Expiry day (Thursday for weekly options)
WEEKLY_EXPIRY_DAY = 3  # 0=Monday, 3=Thursday

# Risk-free rate (approximate Indian government bond rate)
RISK_FREE_RATE = 0.07  # 7%

# Gamma Exposure constants
GEX_MULTIPLIER = 0.01

# Max Pain calculation constants
MAX_PAIN_STRIKE_RANGE = 1000  # Points above and below spot to check

# Put-Call Ratio constants
PCR_BULLISH_THRESHOLD = 1.2
PCR_BEARISH_THRESHOLD = 0.8

# GEX regime thresholds
GEX_POSITIVE_THRESHOLD = 0  # Above this is positive GEX regime
GEX_NEGATIVE_THRESHOLD = 0  # Below this is negative GEX regime

# Technical indicator parameters
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

BOLLINGER_PERIOD = 20
BOLLINGER_STD = 2

# Position limits
MAX_OPEN_POSITIONS = 5
MAX_POSITION_VALUE = 1000000  # 10 lakhs per position

# Risk management
STOP_LOSS_PERCENTAGE = 0.20  # 20% stop loss
TAKE_PROFIT_PERCENTAGE = 0.30  # 30% take profit
MAX_DAILY_LOSS_PERCENTAGE = 0.05  # 5% of capital

# Strategy specific constants
IRON_CONDOR_WING_WIDTH = 100  # Points between strikes
STRADDLE_DELTA_THRESHOLD = 0.25  # Delta threshold for adjustment

# Backtesting constants
INITIAL_CAPITAL = 1000000  # 10 lakhs
COMMISSION_PER_LOT = 20  # ₹20 per lot
SLIPPAGE_POINTS = 2  # 2 points slippage


@dataclass
class TradingHours:
    """Trading hours configuration."""

    pre_open_start: str = "09:00"
    market_open: str = "09:15"
    market_close: str = "15:30"
    post_close: str = "16:00"


@dataclass
class SymbolInfo:
    """Symbol information."""

    symbol: str
    lot_size: int
    tick_size: float
    contract_multiplier: int

    @classmethod
    def get_nifty(cls) -> "SymbolInfo":
        """Get NIFTY symbol info."""
        return cls(
            symbol="NIFTY",
            lot_size=LOT_SIZES["NIFTY"],
            tick_size=0.05,
            contract_multiplier=CONTRACT_MULTIPLIER,
        )

    @classmethod
    def get_banknifty(cls) -> "SymbolInfo":
        """Get BANKNIFTY symbol info."""
        return cls(
            symbol="BANKNIFTY",
            lot_size=LOT_SIZES["BANKNIFTY"],
            tick_size=0.05,
            contract_multiplier=CONTRACT_MULTIPLIER,
        )


# Expiry dates (to be updated periodically)
WEEKLY_EXPIRY_DATES = [
    # These should be updated regularly or fetched dynamically
]

MONTHLY_EXPIRY_DATES = [
    # Last Thursday of each month
]
