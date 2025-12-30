"""Open Interest analysis."""

import pandas as pd
import numpy as np
from typing import Dict, Tuple

from config.constants import PCR_BULLISH_THRESHOLD, PCR_BEARISH_THRESHOLD
from config.logging_config import get_logger

logger = get_logger(__name__)


class OIAnalyzer:
    """Analyze Open Interest patterns."""

    def __init__(self):
        """Initialize OI analyzer."""
        pass

    def calculate_pcr(
        self, option_chain: pd.DataFrame, method: str = "oi"
    ) -> float:
        """Calculate Put-Call Ratio.

        Args:
            option_chain: DataFrame with columns: strike, call_oi, put_oi, call_volume, put_volume
            method: 'oi' for OI-based PCR, 'volume' for volume-based PCR

        Returns:
            Put-Call Ratio
        """
        if method == "oi":
            total_put_oi = option_chain["put_oi"].fillna(0).sum()
            total_call_oi = option_chain["call_oi"].fillna(0).sum()
            pcr = total_put_oi / total_call_oi if total_call_oi > 0 else 0
        elif method == "volume":
            total_put_volume = option_chain.get("put_volume", pd.Series([0])).fillna(0).sum()
            total_call_volume = option_chain.get("call_volume", pd.Series([0])).fillna(0).sum()
            pcr = total_put_volume / total_call_volume if total_call_volume > 0 else 0
        else:
            raise ValueError("method must be 'oi' or 'volume'")

        return pcr

    def interpret_pcr(self, pcr: float) -> str:
        """Interpret Put-Call Ratio signal.

        Args:
            pcr: Put-Call Ratio value

        Returns:
            Market sentiment interpretation
        """
        if pcr > PCR_BULLISH_THRESHOLD:
            return "bullish"  # High put OI suggests bullish sentiment
        elif pcr < PCR_BEARISH_THRESHOLD:
            return "bearish"  # High call OI suggests bearish sentiment
        else:
            return "neutral"

    def analyze_oi_changes(
        self,
        current_chain: pd.DataFrame,
        previous_chain: pd.DataFrame,
    ) -> pd.DataFrame:
        """Analyze changes in Open Interest.

        Args:
            current_chain: Current option chain
            previous_chain: Previous option chain

        Returns:
            DataFrame with OI change analysis
        """
        # Merge on strike
        merged = current_chain.merge(
            previous_chain,
            on="strike",
            suffixes=("_current", "_previous"),
        )

        # Calculate OI changes
        merged["call_oi_change"] = (
            merged["call_oi_current"] - merged["call_oi_previous"]
        )
        merged["put_oi_change"] = merged["put_oi_current"] - merged["put_oi_previous"]

        # Calculate percentage changes
        merged["call_oi_change_pct"] = (
            merged["call_oi_change"] / merged["call_oi_previous"] * 100
        )
        merged["put_oi_change_pct"] = (
            merged["put_oi_change"] / merged["put_oi_previous"] * 100
        )

        # Replace inf values with 0
        merged.replace([np.inf, -np.inf], 0, inplace=True)
        merged.fillna(0, inplace=True)

        return merged[
            [
                "strike",
                "call_oi_current",
                "put_oi_current",
                "call_oi_change",
                "put_oi_change",
                "call_oi_change_pct",
                "put_oi_change_pct",
            ]
        ]

    def find_call_put_walls(
        self, option_chain: pd.DataFrame, num_walls: int = 5
    ) -> Dict[str, list]:
        """Identify major call and put walls (max OI strikes).

        Args:
            option_chain: DataFrame with columns: strike, call_oi, put_oi
            num_walls: Number of walls to identify

        Returns:
            Dictionary with call and put walls
        """
        # Call walls - highest call OI
        call_walls = (
            option_chain[["strike", "call_oi"]]
            .sort_values("call_oi", ascending=False)
            .head(num_walls)
        )

        # Put walls - highest put OI
        put_walls = (
            option_chain[["strike", "put_oi"]]
            .sort_values("put_oi", ascending=False)
            .head(num_walls)
        )

        return {
            "call_walls": call_walls[["strike", "call_oi"]].to_dict("records"),
            "put_walls": put_walls[["strike", "put_oi"]].to_dict("records"),
        }

    def calculate_oi_distribution(
        self, option_chain: pd.DataFrame, spot: float
    ) -> Dict[str, any]:
        """Calculate OI distribution around spot.

        Args:
            option_chain: DataFrame with columns: strike, call_oi, put_oi
            spot: Current spot price

        Returns:
            Dictionary with OI distribution metrics
        """
        # ITM/OTM classification
        option_chain = option_chain.copy()
        option_chain["itm_call"] = option_chain["strike"] < spot
        option_chain["itm_put"] = option_chain["strike"] > spot

        # Calculate OI for ITM/OTM options
        itm_call_oi = option_chain[option_chain["itm_call"]]["call_oi"].sum()
        otm_call_oi = option_chain[~option_chain["itm_call"]]["call_oi"].sum()
        itm_put_oi = option_chain[option_chain["itm_put"]]["put_oi"].sum()
        otm_put_oi = option_chain[~option_chain["itm_put"]]["put_oi"].sum()

        total_call_oi = itm_call_oi + otm_call_oi
        total_put_oi = itm_put_oi + otm_put_oi

        return {
            "itm_call_oi": itm_call_oi,
            "otm_call_oi": otm_call_oi,
            "itm_put_oi": itm_put_oi,
            "otm_put_oi": otm_put_oi,
            "total_call_oi": total_call_oi,
            "total_put_oi": total_put_oi,
            "itm_call_oi_pct": (
                itm_call_oi / total_call_oi * 100 if total_call_oi > 0 else 0
            ),
            "otm_call_oi_pct": (
                otm_call_oi / total_call_oi * 100 if total_call_oi > 0 else 0
            ),
            "itm_put_oi_pct": (
                itm_put_oi / total_put_oi * 100 if total_put_oi > 0 else 0
            ),
            "otm_put_oi_pct": (
                otm_put_oi / total_put_oi * 100 if total_put_oi > 0 else 0
            ),
        }

    def calculate_oi_buildup(
        self, oi_change_df: pd.DataFrame, spot: float
    ) -> Dict[str, str]:
        """Analyze OI buildup patterns for market signals.

        Args:
            oi_change_df: DataFrame from analyze_oi_changes
            spot: Current spot price

        Returns:
            Dictionary with buildup interpretation
        """
        # Classify by strike relative to spot
        oi_change_df = oi_change_df.copy()
        oi_change_df["relative_to_spot"] = oi_change_df["strike"].apply(
            lambda x: "above" if x > spot else "below"
        )

        # Aggregate changes
        above_spot = oi_change_df[oi_change_df["relative_to_spot"] == "above"]
        below_spot = oi_change_df[oi_change_df["relative_to_spot"] == "below"]

        call_above_increase = above_spot["call_oi_change"].sum() > 0
        call_below_increase = below_spot["call_oi_change"].sum() > 0
        put_above_increase = above_spot["put_oi_change"].sum() > 0
        put_below_increase = below_spot["put_oi_change"].sum() > 0

        # Interpret patterns
        signals = []

        if call_below_increase and put_above_increase:
            signals.append("long_buildup")  # Bullish
        elif call_above_increase and put_below_increase:
            signals.append("short_buildup")  # Bearish
        elif call_below_increase and put_below_increase:
            signals.append("long_unwinding")  # Bearish
        elif call_above_increase and put_above_increase:
            signals.append("short_covering")  # Bullish

        return {
            "signals": signals,
            "call_above_change": above_spot["call_oi_change"].sum(),
            "call_below_change": below_spot["call_oi_change"].sum(),
            "put_above_change": above_spot["put_oi_change"].sum(),
            "put_below_change": below_spot["put_oi_change"].sum(),
        }
