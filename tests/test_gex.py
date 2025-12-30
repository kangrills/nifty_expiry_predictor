"""Tests for GEX calculator."""

import pytest
from features.gex_calculator import GammaExposureCalculator


class TestGEXCalculator:
    """Test suite for GEX calculator."""

    def test_calculate_strike_gex(self):
        """Test GEX calculation for a single strike."""
        calc = GammaExposureCalculator()
        
        gex = calc.calculate_strike_gex(
            spot=19500,
            strike=19500,
            call_oi=1000,
            put_oi=1500,
            call_gamma=0.001,
            put_gamma=0.001,
            lot_size=50,
        )
        
        assert "call_gex" in gex
        assert "put_gex" in gex
        assert "net_gex" in gex
        
        # Call GEX should be positive
        assert gex["call_gex"] > 0
        
        # Put GEX should be negative
        assert gex["put_gex"] < 0
        
        # Net GEX is sum of both
        assert abs(gex["net_gex"] - (gex["call_gex"] + gex["put_gex"])) < 0.01

    def test_calculate_chain_gex(self, sample_option_chain, sample_spot_price):
        """Test GEX calculation for entire chain."""
        calc = GammaExposureCalculator()
        
        gex_df = calc.calculate_chain_gex(
            option_chain=sample_option_chain,
            spot=sample_spot_price,
            days_to_expiry=7,
            lot_size=50,
        )
        
        assert not gex_df.empty
        assert "strike" in gex_df.columns
        assert "call_gex" in gex_df.columns
        assert "put_gex" in gex_df.columns
        assert "net_gex" in gex_df.columns
        assert "cumulative_gex" in gex_df.columns

    def test_find_gex_levels(self, sample_option_chain, sample_spot_price):
        """Test finding key GEX levels."""
        calc = GammaExposureCalculator()
        
        gex_df = calc.calculate_chain_gex(
            option_chain=sample_option_chain,
            spot=sample_spot_price,
            days_to_expiry=7,
        )
        
        levels = calc.find_gex_levels(gex_df, sample_spot_price)
        
        assert "gex_regime" in levels
        assert levels["gex_regime"] in ["positive", "negative"]
        assert "trading_bias" in levels
        assert levels["trading_bias"] in ["mean_reverting", "trending"]
        assert "total_gex" in levels
        assert "flip_levels" in levels
        assert isinstance(levels["flip_levels"], list)

    def test_gex_profile(self, sample_option_chain, sample_spot_price):
        """Test GEX profile calculation."""
        calc = GammaExposureCalculator()
        
        gex_df = calc.calculate_chain_gex(
            option_chain=sample_option_chain,
            spot=sample_spot_price,
            days_to_expiry=7,
        )
        
        profile = calc.calculate_gex_profile(gex_df)
        
        assert "net_gex" in profile
        assert "call_gex" in profile
        assert "put_gex" in profile
        assert "cumulative_gex" in profile
