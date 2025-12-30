"""Broker API interfaces."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, List
from datetime import datetime
import pandas as pd

from config.settings import settings
from config.logging_config import get_logger

logger = get_logger(__name__)


class BrokerInterface(ABC):
    """Abstract base class for broker API connections."""

    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to broker API.

        Returns:
            True if connection successful
        """
        pass

    @abstractmethod
    def get_ltp(self, symbol: str, exchange: str = "NSE") -> Optional[float]:
        """Get Last Traded Price for a symbol.

        Args:
            symbol: Trading symbol
            exchange: Exchange name

        Returns:
            Last traded price or None
        """
        pass

    @abstractmethod
    def get_option_chain(
        self, symbol: str, expiry: str
    ) -> Optional[pd.DataFrame]:
        """Get option chain data.

        Args:
            symbol: Underlying symbol
            expiry: Expiry date

        Returns:
            DataFrame with option chain or None
        """
        pass

    @abstractmethod
    def get_historical_data(
        self,
        symbol: str,
        from_date: datetime,
        to_date: datetime,
        interval: str = "day",
    ) -> Optional[pd.DataFrame]:
        """Get historical data.

        Args:
            symbol: Trading symbol
            from_date: Start date
            to_date: End date
            interval: Data interval (minute, day, etc.)

        Returns:
            DataFrame with OHLCV data or None
        """
        pass

    @abstractmethod
    def place_order(
        self,
        symbol: str,
        quantity: int,
        order_type: str,
        transaction_type: str,
        price: Optional[float] = None,
    ) -> Optional[str]:
        """Place an order.

        Args:
            symbol: Trading symbol
            quantity: Order quantity
            order_type: MARKET or LIMIT
            transaction_type: BUY or SELL
            price: Limit price (for LIMIT orders)

        Returns:
            Order ID or None
        """
        pass


class ZerodhaConnector(BrokerInterface):
    """Zerodha Kite Connect API integration."""

    def __init__(self):
        """Initialize Zerodha connector."""
        self.api_key = settings.broker.zerodha_api_key
        self.api_secret = settings.broker.zerodha_api_secret
        self.access_token = settings.broker.zerodha_access_token
        self.kite = None

    def connect(self) -> bool:
        """Connect to Zerodha Kite API."""
        try:
            from kiteconnect import KiteConnect

            self.kite = KiteConnect(api_key=self.api_key)

            if self.access_token:
                self.kite.set_access_token(self.access_token)
                logger.info("Connected to Zerodha Kite API")
                return True
            else:
                logger.error("Zerodha access token not found")
                return False

        except Exception as e:
            logger.error(f"Failed to connect to Zerodha: {e}")
            return False

    def get_ltp(self, symbol: str, exchange: str = "NSE") -> Optional[float]:
        """Get LTP from Zerodha."""
        if not self.kite:
            logger.error("Not connected to Zerodha")
            return None

        try:
            instrument_key = f"{exchange}:{symbol}"
            ltp_data = self.kite.ltp([instrument_key])
            return ltp_data[instrument_key]["last_price"]
        except Exception as e:
            logger.error(f"Failed to get LTP for {symbol}: {e}")
            return None

    def get_option_chain(
        self, symbol: str, expiry: str
    ) -> Optional[pd.DataFrame]:
        """Get option chain from Zerodha."""
        # Note: Zerodha doesn't provide direct option chain API
        # Would need to use instruments list and filter
        logger.warning("Option chain retrieval from Zerodha requires instrument list parsing")
        return None

    def get_historical_data(
        self,
        symbol: str,
        from_date: datetime,
        to_date: datetime,
        interval: str = "day",
    ) -> Optional[pd.DataFrame]:
        """Get historical data from Zerodha."""
        if not self.kite:
            logger.error("Not connected to Zerodha")
            return None

        try:
            # Get instrument token (simplified - would need proper instrument lookup)
            data = self.kite.historical_data(
                instrument_token=symbol,  # Should be token, not symbol
                from_date=from_date,
                to_date=to_date,
                interval=interval,
            )
            return pd.DataFrame(data)
        except Exception as e:
            logger.error(f"Failed to get historical data: {e}")
            return None

    def place_order(
        self,
        symbol: str,
        quantity: int,
        order_type: str,
        transaction_type: str,
        price: Optional[float] = None,
    ) -> Optional[str]:
        """Place order via Zerodha."""
        if not self.kite:
            logger.error("Not connected to Zerodha")
            return None

        try:
            order_id = self.kite.place_order(
                variety=self.kite.VARIETY_REGULAR,
                exchange="NFO",  # Derivatives segment
                tradingsymbol=symbol,
                transaction_type=transaction_type,
                quantity=quantity,
                product=self.kite.PRODUCT_NRML,
                order_type=order_type,
                price=price,
            )
            logger.info(f"Order placed: {order_id}")
            return order_id
        except Exception as e:
            logger.error(f"Failed to place order: {e}")
            return None


class UpstoxConnector(BrokerInterface):
    """Upstox API integration."""

    def __init__(self):
        """Initialize Upstox connector."""
        self.api_key = settings.broker.upstox_api_key
        self.api_secret = settings.broker.upstox_api_secret
        self.access_token = settings.broker.upstox_access_token

    def connect(self) -> bool:
        """Connect to Upstox API."""
        logger.warning("Upstox connector not fully implemented")
        return False

    def get_ltp(self, symbol: str, exchange: str = "NSE") -> Optional[float]:
        logger.warning("Upstox get_ltp not implemented")
        return None

    def get_option_chain(
        self, symbol: str, expiry: str
    ) -> Optional[pd.DataFrame]:
        logger.warning("Upstox get_option_chain not implemented")
        return None

    def get_historical_data(
        self,
        symbol: str,
        from_date: datetime,
        to_date: datetime,
        interval: str = "day",
    ) -> Optional[pd.DataFrame]:
        logger.warning("Upstox get_historical_data not implemented")
        return None

    def place_order(
        self,
        symbol: str,
        quantity: int,
        order_type: str,
        transaction_type: str,
        price: Optional[float] = None,
    ) -> Optional[str]:
        logger.warning("Upstox place_order not implemented")
        return None


class AngelOneConnector(BrokerInterface):
    """Angel One Smart API integration."""

    def __init__(self):
        """Initialize Angel One connector."""
        self.api_key = settings.broker.angel_api_key
        self.client_id = settings.broker.angel_client_id
        self.password = settings.broker.angel_password

    def connect(self) -> bool:
        """Connect to Angel One Smart API."""
        logger.warning("Angel One connector not fully implemented")
        return False

    def get_ltp(self, symbol: str, exchange: str = "NSE") -> Optional[float]:
        logger.warning("Angel One get_ltp not implemented")
        return None

    def get_option_chain(
        self, symbol: str, expiry: str
    ) -> Optional[pd.DataFrame]:
        logger.warning("Angel One get_option_chain not implemented")
        return None

    def get_historical_data(
        self,
        symbol: str,
        from_date: datetime,
        to_date: datetime,
        interval: str = "day",
    ) -> Optional[pd.DataFrame]:
        logger.warning("Angel One get_historical_data not implemented")
        return None

    def place_order(
        self,
        symbol: str,
        quantity: int,
        order_type: str,
        transaction_type: str,
        price: Optional[float] = None,
    ) -> Optional[str]:
        logger.warning("Angel One place_order not implemented")
        return None


def get_broker_connector(broker_name: str) -> Optional[BrokerInterface]:
    """Factory function to get broker connector.

    Args:
        broker_name: Name of the broker (zerodha, upstox, angelone)

    Returns:
        BrokerInterface instance or None
    """
    brokers = {
        "zerodha": ZerodhaConnector,
        "upstox": UpstoxConnector,
        "angelone": AngelOneConnector,
    }

    broker_class = brokers.get(broker_name.lower())
    if broker_class:
        return broker_class()
    else:
        logger.error(f"Unknown broker: {broker_name}")
        return None
