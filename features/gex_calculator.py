"""Gamma Exposure (GEX) calculator."""

import pandas as pd
import numpy as np
from typing import Dict, Optional

from config.constants import GEX_MULTIPLIER
from config.logging_config import get_logger
from features.greeks_calculator import GreeksCalculator

logger = get_logger(__name__)


class GammaExposureCalculator:
    """Calculate Gamma Exposure for option chains."""

    def __init__(self, greeks_calculator: Optional[GreeksCalculator] = None):
        """Initialize GEX calculator.

        Args:
            greeks_calculator: Greeks calculator instance (creates new if None)
        """
        self.greeks_calculator = greeks_calculator or GreeksCalculator()

    def calculate_strike_gex(
        self,
        spot: float,
        strike: float,
        call_oi: float,
        put_oi: float,
        call_gamma: float,
        put_gamma: float,
        lot_size: int,
    ) -> Dict[str, float]:
        """Calculate GEX for a single strike.

        Args:
            spot: Current spot price
            strike: Strike price
            call_oi: Call open interest
            put_oi: Put open interest
            call_gamma: Call gamma
            put_gamma: Put gamma
            lot_size: Contract lot size

        Returns:
            Dictionary with call_gex, put_gex, and net_gex
        """
        # GEX = Gamma × OI × Lot Size × Spot² × 0.01
        # Call GEX is positive, Put GEX is negative (from dealer perspective)
        spot_squared = spot**2

        call_gex = call_gamma * call_oi * lot_size * spot_squared * GEX_MULTIPLIER
        put_gex = -1 * put_gamma * put_oi * lot_size * spot_squared * GEX_MULTIPLIER
        net_gex = call_gex + put_gex

        return {"call_gex": call_gex, "put_gex": put_gex, "net_gex": net_gex}

    def calculate_chain_gex(
        self,
        option_chain: pd.DataFrame,
        spot: float,
        days_to_expiry: int,
        lot_size: int = 50,
    ) -> pd.DataFrame:
        """Calculate GEX for entire option chain.

        Args:
            option_chain: DataFrame with columns: strike, call_oi, put_oi, call_iv, put_iv
            spot: Current spot price
            days_to_expiry: Days until expiry
            lot_size: Contract lot size (default 50 for NIFTY)

        Returns:
            DataFrame with GEX calculations for each strike
        """
        time_to_expiry = days_to_expiry / 365.0

        results = []

        for _, row in option_chain.iterrows():
            strike = row["strike"]

            # Calculate gamma for calls
            if pd.notna(row.get("call_iv")) and row.get("call_iv", 0) > 0:
                call_greeks = self.greeks_calculator.calculate_greeks(
                    spot=spot,
                    strike=strike,
                    time_to_expiry=time_to_expiry,
                    volatility=row["call_iv"],
                    option_type="call",
                )
                call_gamma = call_greeks.gamma
            else:
                call_gamma = 0

            # Calculate gamma for puts
            if pd.notna(row.get("put_iv")) and row.get("put_iv", 0) > 0:
                put_greeks = self.greeks_calculator.calculate_greeks(
                    spot=spot,
                    strike=strike,
                    time_to_expiry=time_to_expiry,
                    volatility=row["put_iv"],
                    option_type="put",
                )
                put_gamma = put_greeks.gamma
            else:
                put_gamma = 0

            # Calculate GEX
            gex = self.calculate_strike_gex(
                spot=spot,
                strike=strike,
                call_oi=row.get("call_oi", 0),
                put_oi=row.get("put_oi", 0),
                call_gamma=call_gamma,
                put_gamma=put_gamma,
                lot_size=lot_size,
            )

            results.append(
                {
                    "strike": strike,
                    "call_oi": row.get("call_oi", 0),
                    "put_oi": row.get("put_oi", 0),
                    "call_gamma": call_gamma,
                    "put_gamma": put_gamma,
                    "call_gex": gex["call_gex"],
                    "put_gex": gex["put_gex"],
                    "net_gex": gex["net_gex"],
                }
            )

        gex_df = pd.DataFrame(results)

        # Add cumulative GEX
        gex_df["cumulative_gex"] = gex_df["net_gex"].cumsum()

        return gex_df

    def find_gex_levels(
        self, gex_df: pd.DataFrame, spot: float
    ) -> Dict[str, any]:
        """Find key GEX levels (flip levels, max GEX strikes).

        Args:
            gex_df: DataFrame from calculate_chain_gex
            spot: Current spot price

        Returns:
            Dictionary with key GEX levels and regime information
        """
        # Find zero gamma (flip) level
        # This is where net GEX crosses zero
        zero_crossings = []
        for i in range(len(gex_df) - 1):
            if (gex_df.iloc[i]["net_gex"] * gex_df.iloc[i + 1]["net_gex"]) < 0:
                # Linear interpolation to find exact crossing
                strike1 = gex_df.iloc[i]["strike"]
                strike2 = gex_df.iloc[i + 1]["strike"]
                gex1 = gex_df.iloc[i]["net_gex"]
                gex2 = gex_df.iloc[i + 1]["net_gex"]

                flip_level = strike1 + (strike2 - strike1) * abs(gex1) / (
                    abs(gex1) + abs(gex2)
                )
                zero_crossings.append(flip_level)

        # Find max absolute GEX strikes
        max_positive_gex_idx = gex_df["net_gex"].idxmax()
        max_negative_gex_idx = gex_df["net_gex"].idxmin()

        max_positive_gex_strike = gex_df.loc[max_positive_gex_idx, "strike"]
        max_negative_gex_strike = gex_df.loc[max_negative_gex_idx, "strike"]

        # Calculate total GEX above and below spot
        above_spot = gex_df[gex_df["strike"] > spot]["net_gex"].sum()
        below_spot = gex_df[gex_df["strike"] < spot]["net_gex"].sum()
        total_gex = gex_df["net_gex"].sum()

        # Determine GEX regime
        if total_gex > 0:
            gex_regime = "positive"
            trading_bias = "mean_reverting"  # Market tends to gravitate towards high GEX
        else:
            gex_regime = "negative"
            trading_bias = "trending"  # Market tends to move away from negative GEX

        return {
            "gex_regime": gex_regime,
            "trading_bias": trading_bias,
            "total_gex": total_gex,
            "gex_above_spot": above_spot,
            "gex_below_spot": below_spot,
            "flip_levels": zero_crossings,
            "max_positive_gex_strike": max_positive_gex_strike,
            "max_negative_gex_strike": max_negative_gex_strike,
            "spot": spot,
        }

    def calculate_gex_profile(
        self, gex_df: pd.DataFrame
    ) -> Dict[str, pd.DataFrame]:
        """Calculate GEX profile for visualization.

        Args:
            gex_df: DataFrame from calculate_chain_gex

        Returns:
            Dictionary with DataFrames for different GEX components
        """
        return {
            "net_gex": gex_df[["strike", "net_gex"]],
            "call_gex": gex_df[["strike", "call_gex"]],
            "put_gex": gex_df[["strike", "put_gex"]],
            "cumulative_gex": gex_df[["strike", "cumulative_gex"]],
        }
