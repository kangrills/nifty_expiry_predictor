"""Configuration settings for Nifty Expiry Predictor."""

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class BrokerConfig:
    """Broker API configuration."""

    # Zerodha
    zerodha_api_key: Optional[str] = None
    zerodha_api_secret: Optional[str] = None
    zerodha_access_token: Optional[str] = None

    # Upstox
    upstox_api_key: Optional[str] = None
    upstox_api_secret: Optional[str] = None
    upstox_access_token: Optional[str] = None

    # Angel One
    angel_api_key: Optional[str] = None
    angel_client_id: Optional[str] = None
    angel_password: Optional[str] = None
    angel_totp_secret: Optional[str] = None

    @classmethod
    def from_env(cls) -> "BrokerConfig":
        """Load broker configuration from environment variables."""
        return cls(
            zerodha_api_key=os.getenv("ZERODHA_API_KEY"),
            zerodha_api_secret=os.getenv("ZERODHA_API_SECRET"),
            zerodha_access_token=os.getenv("ZERODHA_ACCESS_TOKEN"),
            upstox_api_key=os.getenv("UPSTOX_API_KEY"),
            upstox_api_secret=os.getenv("UPSTOX_API_SECRET"),
            upstox_access_token=os.getenv("UPSTOX_ACCESS_TOKEN"),
            angel_api_key=os.getenv("ANGEL_API_KEY"),
            angel_client_id=os.getenv("ANGEL_CLIENT_ID"),
            angel_password=os.getenv("ANGEL_PASSWORD"),
            angel_totp_secret=os.getenv("ANGEL_TOTP_SECRET"),
        )


@dataclass
class DatabaseConfig:
    """Database configuration."""

    database_url: str
    redis_url: str

    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """Load database configuration from environment variables."""
        return cls(
            database_url=os.getenv(
                "DATABASE_URL",
                "postgresql://nifty_user:nifty_password@localhost:5432/nifty_expiry",
            ),
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        )


@dataclass
class TradingConfig:
    """Trading configuration."""

    trading_mode: str  # "paper" or "live"
    max_daily_loss: float
    max_position_size: int
    lot_size_nifty: int
    lot_size_banknifty: int

    @classmethod
    def from_env(cls) -> "TradingConfig":
        """Load trading configuration from environment variables."""
        return cls(
            trading_mode=os.getenv("TRADING_MODE", "paper"),
            max_daily_loss=float(os.getenv("MAX_DAILY_LOSS", "50000")),
            max_position_size=int(os.getenv("MAX_POSITION_SIZE", "10")),
            lot_size_nifty=int(os.getenv("LOT_SIZE_NIFTY", "50")),
            lot_size_banknifty=int(os.getenv("LOT_SIZE_BANKNIFTY", "25")),
        )


@dataclass
class ModelConfig:
    """ML Model configuration."""

    model_path: str
    retrain_interval_days: int

    @classmethod
    def from_env(cls) -> "ModelConfig":
        """Load model configuration from environment variables."""
        return cls(
            model_path=os.getenv("MODEL_PATH", "models/saved_models/"),
            retrain_interval_days=int(os.getenv("RETRAIN_INTERVAL_DAYS", "7")),
        )


@dataclass
class AlertConfig:
    """Alert configuration."""

    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    sendgrid_api_key: Optional[str] = None
    alert_email_from: Optional[str] = None
    alert_email_to: Optional[str] = None

    @classmethod
    def from_env(cls) -> "AlertConfig":
        """Load alert configuration from environment variables."""
        return cls(
            telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
            telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID"),
            sendgrid_api_key=os.getenv("SENDGRID_API_KEY"),
            alert_email_from=os.getenv("ALERT_EMAIL_FROM"),
            alert_email_to=os.getenv("ALERT_EMAIL_TO"),
        )


@dataclass
class NSEConfig:
    """NSE data collection configuration."""

    rate_limit_delay: float
    max_retries: int

    @classmethod
    def from_env(cls) -> "NSEConfig":
        """Load NSE configuration from environment variables."""
        return cls(
            rate_limit_delay=float(os.getenv("NSE_RATE_LIMIT_DELAY", "1.0")),
            max_retries=int(os.getenv("NSE_MAX_RETRIES", "3")),
        )


@dataclass
class Settings:
    """Main application settings."""

    broker: BrokerConfig
    database: DatabaseConfig
    trading: TradingConfig
    model: ModelConfig
    alert: AlertConfig
    nse: NSEConfig
    log_level: str
    log_file: str

    @classmethod
    def from_env(cls) -> "Settings":
        """Load all settings from environment variables."""
        return cls(
            broker=BrokerConfig.from_env(),
            database=DatabaseConfig.from_env(),
            trading=TradingConfig.from_env(),
            model=ModelConfig.from_env(),
            alert=AlertConfig.from_env(),
            nse=NSEConfig.from_env(),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_file=os.getenv("LOG_FILE", "logs/nifty_expiry.log"),
        )


# Global settings instance
settings = Settings.from_env()
