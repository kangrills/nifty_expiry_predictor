"""Pytest configuration and fixtures."""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime


@pytest.fixture
def sample_option_chain():
    """Sample option chain data for testing."""
    strikes = np.arange(19000, 20000, 100)
    
    data = []
    for strike in strikes:
        data.append({
            "strike": strike,
            "expiry_date": "2024-12-31",
            "call_oi": np.random.randint(100, 10000),
            "call_volume": np.random.randint(10, 1000),
            "call_ltp": np.random.uniform(50, 500),
            "call_iv": np.random.uniform(0.15, 0.25),
            "put_oi": np.random.randint(100, 10000),
            "put_volume": np.random.randint(10, 1000),
            "put_ltp": np.random.uniform(50, 500),
            "put_iv": np.random.uniform(0.15, 0.25),
        })
    
    df = pd.DataFrame(data)
    df.attrs["underlying"] = 19500
    df.attrs["timestamp"] = datetime.now().isoformat()
    df.attrs["symbol"] = "NIFTY"
    
    return df


@pytest.fixture
def sample_spot_price():
    """Sample spot price for testing."""
    return 19500.0


@pytest.fixture
def sample_strike():
    """Sample strike price for testing."""
    return 19500.0


@pytest.fixture
def sample_volatility():
    """Sample volatility for testing."""
    return 0.20


@pytest.fixture
def sample_time_to_expiry():
    """Sample time to expiry for testing."""
    return 7 / 365.0  # 7 days
