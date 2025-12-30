"""Base strategy class."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import pandas as pd

from config.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class Signal:
    """Trading signal."""

    timestamp: datetime
    signal_type: str  # 'buy', 'sell', 'hold'
    symbol: str
    strike: Optional[float] = None
    option_type: Optional[str] = None  # 'call', 'put'
    quantity: int = 0
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    confidence: float = 0.0
    reason: str = ""


@dataclass
class Position:
    """Trading position."""

    position_id: str
    symbol: str
    strike: float
    option_type: str
    quantity: int
    entry_price: float
    entry_time: datetime
    current_price: float = 0.0
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    status: str = "open"  # 'open', 'closed'


class BaseStrategy(ABC):
    """Abstract base class for trading strategies."""

    def __init__(self, name: str):
        """Initialize strategy.

        Args:
            name: Strategy name
        """
        self.name = name
        self.positions: List[Position] = []
        self.signals: List[Signal] = []
        self.pnl_history: List[Dict] = []

    @abstractmethod
    def generate_signals(
        self,
        option_chain: pd.DataFrame,
        spot: float,
        market_data: Dict,
    ) -> List[Signal]:
        """Generate trading signals.

        Args:
            option_chain: Option chain data
            spot: Current spot price
            market_data: Additional market data (VIX, GEX, Max Pain, etc.)

        Returns:
            List of trading signals
        """
        pass

    @abstractmethod
    def entry_criteria(self, market_data: Dict) -> bool:
        """Check if entry criteria are met.

        Args:
            market_data: Market data dictionary

        Returns:
            True if entry conditions are satisfied
        """
        pass

    @abstractmethod
    def exit_criteria(self, position: Position, market_data: Dict) -> bool:
        """Check if exit criteria are met.

        Args:
            position: Current position
            market_data: Market data dictionary

        Returns:
            True if exit conditions are satisfied
        """
        pass

    def execute(self, signals: List[Signal]) -> List[Position]:
        """Execute trading signals.

        Args:
            signals: List of signals to execute

        Returns:
            List of opened positions
        """
        new_positions = []

        for signal in signals:
            if signal.signal_type == "buy":
                position = self._open_position(signal)
                if position:
                    new_positions.append(position)
                    self.positions.append(position)
            elif signal.signal_type == "sell":
                self._close_positions(signal)

        return new_positions

    def _open_position(self, signal: Signal) -> Optional[Position]:
        """Open a new position from signal.

        Args:
            signal: Trading signal

        Returns:
            Position object or None
        """
        position = Position(
            position_id=f"{signal.symbol}_{signal.strike}_{datetime.now().timestamp()}",
            symbol=signal.symbol,
            strike=signal.strike or 0,
            option_type=signal.option_type or "call",
            quantity=signal.quantity,
            entry_price=signal.entry_price or 0,
            entry_time=signal.timestamp,
        )

        logger.info(f"Opened position: {position.position_id}")
        return position

    def _close_positions(self, signal: Signal):
        """Close positions matching signal.

        Args:
            signal: Trading signal
        """
        for position in self.positions:
            if position.status == "open" and position.symbol == signal.symbol:
                position.status = "closed"
                position.realized_pnl = (
                    (signal.entry_price or 0) - position.entry_price
                ) * position.quantity
                logger.info(f"Closed position: {position.position_id}, P&L: {position.realized_pnl}")

    def calculate_pnl(self, current_prices: Dict[str, float]) -> float:
        """Calculate total P&L.

        Args:
            current_prices: Dictionary mapping position_id to current price

        Returns:
            Total P&L
        """
        total_pnl = 0.0

        for position in self.positions:
            if position.status == "open":
                current_price = current_prices.get(position.position_id, position.entry_price)
                position.current_price = current_price
                position.unrealized_pnl = (current_price - position.entry_price) * position.quantity
                total_pnl += position.unrealized_pnl
            else:
                total_pnl += position.realized_pnl

        return total_pnl

    def get_open_positions(self) -> List[Position]:
        """Get list of open positions.

        Returns:
            List of open positions
        """
        return [p for p in self.positions if p.status == "open"]

    def get_closed_positions(self) -> List[Position]:
        """Get list of closed positions.

        Returns:
            List of closed positions
        """
        return [p for p in self.positions if p.status == "closed"]

    def reset(self):
        """Reset strategy state."""
        self.positions = []
        self.signals = []
        self.pnl_history = []
        logger.info(f"Strategy {self.name} reset")
