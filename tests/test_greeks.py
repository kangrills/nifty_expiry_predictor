"""Tests for Greeks calculator."""

import pytest
import numpy as np
from features.greeks_calculator import GreeksCalculator


class TestGreeksCalculator:
    """Test suite for Greeks calculator."""

    def test_call_price(self, sample_spot_price, sample_strike, sample_time_to_expiry, sample_volatility):
        """Test call option pricing."""
        calc = GreeksCalculator()
        
        call_price = calc.call_price(
            spot=sample_spot_price,
            strike=sample_strike,
            time_to_expiry=sample_time_to_expiry,
            volatility=sample_volatility,
        )
        
        assert call_price > 0
        assert isinstance(call_price, float)

    def test_put_price(self, sample_spot_price, sample_strike, sample_time_to_expiry, sample_volatility):
        """Test put option pricing."""
        calc = GreeksCalculator()
        
        put_price = calc.put_price(
            spot=sample_spot_price,
            strike=sample_strike,
            time_to_expiry=sample_time_to_expiry,
            volatility=sample_volatility,
        )
        
        assert put_price > 0
        assert isinstance(put_price, float)

    def test_call_greeks(self, sample_spot_price, sample_strike, sample_time_to_expiry, sample_volatility):
        """Test call option Greeks calculation."""
        calc = GreeksCalculator()
        
        greeks = calc.calculate_greeks(
            spot=sample_spot_price,
            strike=sample_strike,
            time_to_expiry=sample_time_to_expiry,
            volatility=sample_volatility,
            option_type="call",
        )
        
        # Delta should be between 0 and 1 for calls
        assert 0 <= greeks.delta <= 1
        
        # Gamma should be positive
        assert greeks.gamma > 0
        
        # Vega should be positive
        assert greeks.vega > 0
        
        # Theta should be negative for long options
        assert greeks.theta < 0

    def test_put_greeks(self, sample_spot_price, sample_strike, sample_time_to_expiry, sample_volatility):
        """Test put option Greeks calculation."""
        calc = GreeksCalculator()
        
        greeks = calc.calculate_greeks(
            spot=sample_spot_price,
            strike=sample_strike,
            time_to_expiry=sample_time_to_expiry,
            volatility=sample_volatility,
            option_type="put",
        )
        
        # Delta should be between -1 and 0 for puts
        assert -1 <= greeks.delta <= 0
        
        # Gamma should be positive
        assert greeks.gamma > 0
        
        # Vega should be positive
        assert greeks.vega > 0

    def test_put_call_parity(self, sample_spot_price, sample_strike, sample_time_to_expiry, sample_volatility):
        """Test put-call parity relationship."""
        calc = GreeksCalculator()
        
        call_price = calc.call_price(
            spot=sample_spot_price,
            strike=sample_strike,
            time_to_expiry=sample_time_to_expiry,
            volatility=sample_volatility,
        )
        
        put_price = calc.put_price(
            spot=sample_spot_price,
            strike=sample_strike,
            time_to_expiry=sample_time_to_expiry,
            volatility=sample_volatility,
        )
        
        # Put-Call Parity: C - P = S - K*e^(-rT)
        pv_strike = sample_strike * np.exp(-calc.risk_free_rate * sample_time_to_expiry)
        parity_lhs = call_price - put_price
        parity_rhs = sample_spot_price - pv_strike
        
        assert abs(parity_lhs - parity_rhs) < 0.01  # Allow small numerical error

    def test_implied_volatility(self, sample_spot_price, sample_strike, sample_time_to_expiry):
        """Test implied volatility calculation."""
        calc = GreeksCalculator()
        
        # Calculate a theoretical price with known volatility
        known_volatility = 0.25
        market_price = calc.call_price(
            spot=sample_spot_price,
            strike=sample_strike,
            time_to_expiry=sample_time_to_expiry,
            volatility=known_volatility,
        )
        
        # Calculate implied volatility
        iv = calc.implied_volatility(
            market_price=market_price,
            spot=sample_spot_price,
            strike=sample_strike,
            time_to_expiry=sample_time_to_expiry,
            option_type="call",
        )
        
        assert iv is not None
        assert abs(iv - known_volatility) < 0.01  # Should converge to known volatility
