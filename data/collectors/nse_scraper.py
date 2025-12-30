"""NSE data scraper for option chain and historical data."""

import requests
import pandas as pd
import time
from datetime import datetime, timedelta
from typing import Optional, Dict
from pathlib import Path

from config.settings import settings
from config.logging_config import get_logger

logger = get_logger(__name__)


class NSEDataCollector:
    """Collect data from NSE India website."""

    BASE_URL = "https://www.nseindia.com"
    OPTION_CHAIN_URL = f"{BASE_URL}/api/option-chain-indices"
    BHAVCOPY_URL = f"{BASE_URL}/products/content/sec_bhavdata_full.csv"

    def __init__(self):
        """Initialize NSE data collector."""
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
            }
        )
        self._initialize_session()

    def _initialize_session(self):
        """Initialize session by accessing NSE homepage for cookies."""
        try:
            self.session.get(self.BASE_URL, timeout=10)
            logger.info("NSE session initialized")
        except Exception as e:
            logger.error(f"Failed to initialize NSE session: {e}")

    def _rate_limit(self):
        """Apply rate limiting delay."""
        time.sleep(settings.nse.rate_limit_delay)

    def get_option_chain(self, symbol: str = "NIFTY") -> pd.DataFrame:
        """Fetch live option chain from NSE.

        Args:
            symbol: Index symbol (NIFTY, BANKNIFTY, FINNIFTY)

        Returns:
            DataFrame with option chain data
        """
        url = f"{self.OPTION_CHAIN_URL}?symbol={symbol}"

        for attempt in range(settings.nse.max_retries):
            try:
                self._rate_limit()
                response = self.session.get(url, timeout=10)
                response.raise_for_status()

                data = response.json()
                records = data.get("records", {})
                option_data = records.get("data", [])

                # Parse option chain
                parsed_data = []
                for item in option_data:
                    strike = item.get("strikePrice")
                    expiry_date = item.get("expiryDate")

                    ce_data = item.get("CE", {})
                    pe_data = item.get("PE", {})

                    parsed_data.append(
                        {
                            "strike": strike,
                            "expiry_date": expiry_date,
                            "call_oi": ce_data.get("openInterest", 0),
                            "call_oi_change": ce_data.get("changeinOpenInterest", 0),
                            "call_volume": ce_data.get("totalTradedVolume", 0),
                            "call_iv": ce_data.get("impliedVolatility", 0) / 100,  # Convert to decimal
                            "call_ltp": ce_data.get("lastPrice", 0),
                            "call_bid": ce_data.get("bidprice", 0),
                            "call_ask": ce_data.get("askPrice", 0),
                            "put_oi": pe_data.get("openInterest", 0),
                            "put_oi_change": pe_data.get("changeinOpenInterest", 0),
                            "put_volume": pe_data.get("totalTradedVolume", 0),
                            "put_iv": pe_data.get("impliedVolatility", 0) / 100,  # Convert to decimal
                            "put_ltp": pe_data.get("lastPrice", 0),
                            "put_bid": pe_data.get("bidprice", 0),
                            "put_ask": pe_data.get("askPrice", 0),
                        }
                    )

                df = pd.DataFrame(parsed_data)

                # Store metadata
                df.attrs["underlying"] = records.get("underlyingValue", 0)
                df.attrs["timestamp"] = records.get("timestamp", "")
                df.attrs["symbol"] = symbol

                logger.info(f"Fetched option chain for {symbol}: {len(df)} strikes")
                return df

            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < settings.nse.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Failed to fetch option chain after {settings.nse.max_retries} attempts")
                    raise

        return pd.DataFrame()

    def get_india_vix(self) -> Optional[float]:
        """Fetch India VIX value.

        Returns:
            India VIX value or None
        """
        url = f"{self.BASE_URL}/api/equity-stockIndices?index=INDIA VIX"

        try:
            self._rate_limit()
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()
            vix_data = data.get("data", [])

            if vix_data:
                vix = vix_data[0].get("last", 0)
                logger.info(f"India VIX: {vix}")
                return vix

        except Exception as e:
            logger.error(f"Failed to fetch India VIX: {e}")

        return None

    def download_bhavcopy(self, date: datetime, output_dir: str = "data/raw") -> Optional[Path]:
        """Download NSE Bhavcopy for a specific date.

        Args:
            date: Date for which to download Bhavcopy
            output_dir: Directory to save the file

        Returns:
            Path to downloaded file or None
        """
        date_str = date.strftime("%d%m%y")
        filename = f"fo{date_str}bhav.csv.zip"
        url = f"https://www.nseindia.com/content/historical/DERIVATIVES/{date.strftime('%Y/%b').upper()}/{filename}"

        output_path = Path(output_dir) / filename

        try:
            self._rate_limit()
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(response.content)

            logger.info(f"Downloaded Bhavcopy for {date.strftime('%Y-%m-%d')}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to download Bhavcopy for {date.strftime('%Y-%m-%d')}: {e}")
            return None

    def get_fii_dii_data(self) -> Optional[Dict]:
        """Fetch FII/DII data.

        Returns:
            Dictionary with FII/DII data or None
        """
        # Note: This is a placeholder. Actual implementation would require
        # parsing the NSE reports page or using alternative data sources
        logger.warning("FII/DII data fetching not fully implemented")
        return None

    def get_expiry_dates(self, symbol: str = "NIFTY") -> list:
        """Get list of expiry dates for an index.

        Args:
            symbol: Index symbol

        Returns:
            List of expiry dates
        """
        try:
            df = self.get_option_chain(symbol)
            expiry_dates = sorted(df["expiry_date"].unique().tolist())
            logger.info(f"Found {len(expiry_dates)} expiry dates for {symbol}")
            return expiry_dates
        except Exception as e:
            logger.error(f"Failed to fetch expiry dates: {e}")
            return []
