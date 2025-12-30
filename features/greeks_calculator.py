"""Black-Scholes Greeks calculator."""

import numpy as np
from dataclasses import dataclass
from typing import Optional
from scipy.stats import norm

from config.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class GreeksResult:
    """Container for Black-Scholes Greeks calculation results."""

    price: float
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float
    implied_volatility: Optional[float] = None


class GreeksCalculator:
    """Black-Scholes Greeks calculator."""

    def __init__(self, risk_free_rate: float = 0.07):
        """Initialize Greeks calculator.

        Args:
            risk_free_rate: Annual risk-free interest rate (default 7%)
        """
        self.risk_free_rate = risk_free_rate

    def calculate_d1_d2(
        self, spot: float, strike: float, time_to_expiry: float, volatility: float
    ) -> tuple[float, float]:
        """Calculate d1 and d2 for Black-Scholes formula.

        Args:
            spot: Current spot price
            strike: Strike price
            time_to_expiry: Time to expiry in years
            volatility: Implied volatility (as decimal, e.g., 0.20 for 20%)

        Returns:
            Tuple of (d1, d2)
        """
        if time_to_expiry <= 0:
            raise ValueError("Time to expiry must be positive")

        d1 = (
            np.log(spot / strike)
            + (self.risk_free_rate + 0.5 * volatility**2) * time_to_expiry
        ) / (volatility * np.sqrt(time_to_expiry))

        d2 = d1 - volatility * np.sqrt(time_to_expiry)

        return d1, d2

    def call_price(
        self, spot: float, strike: float, time_to_expiry: float, volatility: float
    ) -> float:
        """Calculate Black-Scholes call option price.

        Args:
            spot: Current spot price
            strike: Strike price
            time_to_expiry: Time to expiry in years
            volatility: Implied volatility

        Returns:
            Call option price
        """
        d1, d2 = self.calculate_d1_d2(spot, strike, time_to_expiry, volatility)

        call = spot * norm.cdf(d1) - strike * np.exp(
            -self.risk_free_rate * time_to_expiry
        ) * norm.cdf(d2)

        return call

    def put_price(
        self, spot: float, strike: float, time_to_expiry: float, volatility: float
    ) -> float:
        """Calculate Black-Scholes put option price.

        Args:
            spot: Current spot price
            strike: Strike price
            time_to_expiry: Time to expiry in years
            volatility: Implied volatility

        Returns:
            Put option price
        """
        d1, d2 = self.calculate_d1_d2(spot, strike, time_to_expiry, volatility)

        put = strike * np.exp(-self.risk_free_rate * time_to_expiry) * norm.cdf(
            -d2
        ) - spot * norm.cdf(-d1)

        return put

    def calculate_greeks(
        self,
        spot: float,
        strike: float,
        time_to_expiry: float,
        volatility: float,
        option_type: str = "call",
    ) -> GreeksResult:
        """Calculate all Greeks for an option.

        Args:
            spot: Current spot price
            strike: Strike price
            time_to_expiry: Time to expiry in years
            volatility: Implied volatility
            option_type: 'call' or 'put'

        Returns:
            GreeksResult with all Greeks
        """
        if option_type not in ["call", "put"]:
            raise ValueError("option_type must be 'call' or 'put'")

        d1, d2 = self.calculate_d1_d2(spot, strike, time_to_expiry, volatility)

        # Calculate price
        if option_type == "call":
            price = self.call_price(spot, strike, time_to_expiry, volatility)
        else:
            price = self.put_price(spot, strike, time_to_expiry, volatility)

        # Delta
        if option_type == "call":
            delta = norm.cdf(d1)
        else:
            delta = norm.cdf(d1) - 1

        # Gamma (same for call and put)
        gamma = norm.pdf(d1) / (spot * volatility * np.sqrt(time_to_expiry))

        # Theta (daily)
        if option_type == "call":
            theta = (
                -spot * norm.pdf(d1) * volatility / (2 * np.sqrt(time_to_expiry))
                - self.risk_free_rate
                * strike
                * np.exp(-self.risk_free_rate * time_to_expiry)
                * norm.cdf(d2)
            ) / 365
        else:
            theta = (
                -spot * norm.pdf(d1) * volatility / (2 * np.sqrt(time_to_expiry))
                + self.risk_free_rate
                * strike
                * np.exp(-self.risk_free_rate * time_to_expiry)
                * norm.cdf(-d2)
            ) / 365

        # Vega (for 1% change in volatility)
        vega = spot * norm.pdf(d1) * np.sqrt(time_to_expiry) / 100

        # Rho (for 1% change in interest rate)
        if option_type == "call":
            rho = (
                strike
                * time_to_expiry
                * np.exp(-self.risk_free_rate * time_to_expiry)
                * norm.cdf(d2)
                / 100
            )
        else:
            rho = (
                -strike
                * time_to_expiry
                * np.exp(-self.risk_free_rate * time_to_expiry)
                * norm.cdf(-d2)
                / 100
            )

        return GreeksResult(
            price=price, delta=delta, gamma=gamma, theta=theta, vega=vega, rho=rho
        )

    def implied_volatility(
        self,
        market_price: float,
        spot: float,
        strike: float,
        time_to_expiry: float,
        option_type: str = "call",
        max_iterations: int = 100,
        tolerance: float = 1e-5,
    ) -> Optional[float]:
        """Calculate implied volatility using Newton-Raphson method.

        Args:
            market_price: Observed market price of the option
            spot: Current spot price
            strike: Strike price
            time_to_expiry: Time to expiry in years
            option_type: 'call' or 'put'
            max_iterations: Maximum number of iterations
            tolerance: Convergence tolerance

        Returns:
            Implied volatility or None if not converged
        """
        # Initial guess for volatility
        volatility = 0.20

        for i in range(max_iterations):
            # Calculate theoretical price
            if option_type == "call":
                theoretical_price = self.call_price(
                    spot, strike, time_to_expiry, volatility
                )
            else:
                theoretical_price = self.put_price(
                    spot, strike, time_to_expiry, volatility
                )

            # Calculate vega
            d1, _ = self.calculate_d1_d2(spot, strike, time_to_expiry, volatility)
            vega = spot * norm.pdf(d1) * np.sqrt(time_to_expiry)

            # Price difference
            diff = theoretical_price - market_price

            # Check convergence
            if abs(diff) < tolerance:
                return volatility

            # Newton-Raphson update
            if vega > 0:
                volatility = volatility - diff / vega
            else:
                return None

            # Ensure volatility stays positive
            if volatility <= 0:
                volatility = 0.01

        logger.warning(
            f"Implied volatility did not converge after {max_iterations} iterations"
        )
        return None
