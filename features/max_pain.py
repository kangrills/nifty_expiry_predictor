"""Max Pain calculator."""

import pandas as pd
import numpy as np
from typing import Tuple, Dict

from config.logging_config import get_logger

logger = get_logger(__name__)


class MaxPainCalculator:
    """Calculate Max Pain level for options."""

    def __init__(self):
        """Initialize Max Pain calculator."""
        pass

    def calculate_max_pain(
        self, option_chain: pd.DataFrame, lot_size: int = 50
    ) -> Tuple[float, pd.DataFrame]:
        """Calculate Max Pain strike (minimum loss to option writers).

        Args:
            option_chain: DataFrame with columns: strike, call_oi, put_oi
            lot_size: Contract lot size (default 50 for NIFTY)

        Returns:
            Tuple of (max_pain_strike, pain_curve_df)
        """
        strikes = option_chain["strike"].values
        call_oi = option_chain["call_oi"].fillna(0).values
        put_oi = option_chain["put_oi"].fillna(0).values

        pain_data = []

        # For each possible settlement price (at each strike)
        for settlement in strikes:
            # Calculate total loss for call writers (ITM calls)
            # Loss occurs when settlement > strike
            call_loss = sum(
                (settlement - strike) * call_oi[i] * lot_size
                for i, strike in enumerate(strikes)
                if settlement > strike
            )

            # Calculate total loss for put writers (ITM puts)
            # Loss occurs when settlement < strike
            put_loss = sum(
                (strike - settlement) * put_oi[i] * lot_size
                for i, strike in enumerate(strikes)
                if settlement < strike
            )

            total_pain = call_loss + put_loss

            pain_data.append(
                {
                    "strike": settlement,
                    "call_loss": call_loss,
                    "put_loss": put_loss,
                    "total_pain": total_pain,
                }
            )

        pain_df = pd.DataFrame(pain_data)

        # Max Pain is the strike with minimum total pain
        max_pain_idx = pain_df["total_pain"].idxmin()
        max_pain_strike = pain_df.loc[max_pain_idx, "strike"]

        logger.info(f"Max Pain calculated at strike: {max_pain_strike}")

        return max_pain_strike, pain_df

    def find_support_resistance(
        self, option_chain: pd.DataFrame, num_levels: int = 3
    ) -> Dict[str, list]:
        """Find support and resistance levels based on OI walls.

        Args:
            option_chain: DataFrame with columns: strike, call_oi, put_oi
            num_levels: Number of support/resistance levels to identify

        Returns:
            Dictionary with support and resistance levels
        """
        # Resistance: High call OI (sellers defending these levels)
        call_oi_sorted = (
            option_chain[["strike", "call_oi"]]
            .sort_values("call_oi", ascending=False)
            .head(num_levels)
        )
        resistance_levels = call_oi_sorted["strike"].tolist()

        # Support: High put OI (buyers supporting these levels)
        put_oi_sorted = (
            option_chain[["strike", "put_oi"]]
            .sort_values("put_oi", ascending=False)
            .head(num_levels)
        )
        support_levels = put_oi_sorted["strike"].tolist()

        return {
            "resistance": sorted(resistance_levels, reverse=True),
            "support": sorted(support_levels),
        }

    def calculate_oi_concentration(
        self, option_chain: pd.DataFrame, spot: float, range_points: int = 200
    ) -> Dict[str, float]:
        """Calculate OI concentration around spot price.

        Args:
            option_chain: DataFrame with columns: strike, call_oi, put_oi
            spot: Current spot price
            range_points: Points above and below spot to consider

        Returns:
            Dictionary with OI concentration metrics
        """
        # Filter strikes near spot
        near_spot = option_chain[
            (option_chain["strike"] >= spot - range_points)
            & (option_chain["strike"] <= spot + range_points)
        ]

        total_call_oi = near_spot["call_oi"].sum()
        total_put_oi = near_spot["put_oi"].sum()
        total_oi = total_call_oi + total_put_oi

        # Calculate Put-Call Ratio
        pcr = total_put_oi / total_call_oi if total_call_oi > 0 else 0

        return {
            "near_spot_call_oi": total_call_oi,
            "near_spot_put_oi": total_put_oi,
            "near_spot_total_oi": total_oi,
            "near_spot_pcr": pcr,
            "range_points": range_points,
        }

    def calculate_pain_score(
        self, current_price: float, max_pain: float, pain_df: pd.DataFrame
    ) -> Dict[str, float]:
        """Calculate pain score showing distance from Max Pain.

        Args:
            current_price: Current spot price
            max_pain: Max Pain strike
            pain_df: Pain curve DataFrame from calculate_max_pain

        Returns:
            Dictionary with pain score metrics
        """
        distance_from_max_pain = current_price - max_pain
        distance_percentage = (distance_from_max_pain / max_pain) * 100

        # Get current pain level
        closest_strike_idx = (pain_df["strike"] - current_price).abs().idxmin()
        current_pain = pain_df.loc[closest_strike_idx, "total_pain"]

        # Get minimum pain (at max pain strike)
        min_pain = pain_df["total_pain"].min()

        # Pain score: how much more pain than minimum
        pain_score = (current_pain - min_pain) / min_pain if min_pain > 0 else 0

        return {
            "distance_from_max_pain": distance_from_max_pain,
            "distance_percentage": distance_percentage,
            "current_pain": current_pain,
            "min_pain": min_pain,
            "pain_score": pain_score,
        }
