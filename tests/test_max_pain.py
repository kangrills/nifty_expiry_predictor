"""Tests for Max Pain calculator."""

import pytest
from features.max_pain import MaxPainCalculator


class TestMaxPainCalculator:
    """Test suite for Max Pain calculator."""

    def test_calculate_max_pain(self, sample_option_chain):
        """Test Max Pain calculation."""
        calc = MaxPainCalculator()
        
        max_pain, pain_df = calc.calculate_max_pain(sample_option_chain)
        
        # Max Pain should be a valid strike
        assert max_pain in sample_option_chain["strike"].values
        
        # Pain DataFrame should have required columns
        assert not pain_df.empty
        assert "strike" in pain_df.columns
        assert "call_loss" in pain_df.columns
        assert "put_loss" in pain_df.columns
        assert "total_pain" in pain_df.columns

    def test_find_support_resistance(self, sample_option_chain):
        """Test support/resistance level identification."""
        calc = MaxPainCalculator()
        
        levels = calc.find_support_resistance(sample_option_chain, num_levels=3)
        
        assert "resistance" in levels
        assert "support" in levels
        assert len(levels["resistance"]) <= 3
        assert len(levels["support"]) <= 3
        
        # Resistance levels should be based on high call OI
        # Support levels should be based on high put OI
        for resistance in levels["resistance"]:
            assert resistance in sample_option_chain["strike"].values

    def test_oi_concentration(self, sample_option_chain, sample_spot_price):
        """Test OI concentration calculation."""
        calc = MaxPainCalculator()
        
        concentration = calc.calculate_oi_concentration(
            sample_option_chain,
            sample_spot_price,
            range_points=200
        )
        
        assert "near_spot_call_oi" in concentration
        assert "near_spot_put_oi" in concentration
        assert "near_spot_total_oi" in concentration
        assert "near_spot_pcr" in concentration
        
        # PCR should be positive
        assert concentration["near_spot_pcr"] >= 0

    def test_pain_score(self, sample_option_chain, sample_spot_price):
        """Test pain score calculation."""
        calc = MaxPainCalculator()
        
        max_pain, pain_df = calc.calculate_max_pain(sample_option_chain)
        score = calc.calculate_pain_score(sample_spot_price, max_pain, pain_df)
        
        assert "distance_from_max_pain" in score
        assert "distance_percentage" in score
        assert "current_pain" in score
        assert "min_pain" in score
        assert "pain_score" in score
        
        # Pain score should be non-negative
        assert score["pain_score"] >= 0
