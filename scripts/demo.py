"""Demo script to showcase the Nifty Expiry Predictor functionality."""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from features.greeks_calculator import GreeksCalculator
from features.gex_calculator import GammaExposureCalculator
from features.max_pain import MaxPainCalculator
from features.oi_analysis import OIAnalyzer
from config.logging_config import get_logger

logger = get_logger(__name__)


def create_sample_option_chain(spot: float = 19500) -> pd.DataFrame:
    """Create a sample option chain for demonstration.
    
    Args:
        spot: Current spot price
        
    Returns:
        Sample option chain DataFrame
    """
    # Generate strikes around spot
    strikes = np.arange(spot - 500, spot + 500, 100)
    
    data = []
    for strike in strikes:
        # Simulate realistic OI distribution
        distance_from_spot = abs(strike - spot)
        base_oi = 5000 - (distance_from_spot * 5)  # Higher OI near spot
        
        # Add some randomness
        call_oi = max(100, base_oi + np.random.randint(-1000, 1000))
        put_oi = max(100, base_oi + np.random.randint(-1000, 1000))
        
        # Simulate IV smile
        iv_base = 0.18 + (distance_from_spot / 10000)  # Higher IV further from spot
        
        data.append({
            "strike": strike,
            "expiry_date": "2025-01-02",
            "call_oi": call_oi,
            "call_volume": int(call_oi * 0.1),
            "call_ltp": max(10, (spot - strike) * 0.5) if strike < spot else 50,
            "call_iv": iv_base + np.random.uniform(-0.02, 0.02),
            "put_oi": put_oi,
            "put_volume": int(put_oi * 0.1),
            "put_ltp": max(10, (strike - spot) * 0.5) if strike > spot else 50,
            "put_iv": iv_base + np.random.uniform(-0.02, 0.02),
        })
    
    df = pd.DataFrame(data)
    df.attrs["underlying"] = spot
    df.attrs["timestamp"] = "2025-12-30T15:30:00"
    df.attrs["symbol"] = "NIFTY"
    
    return df


def main():
    """Run demo of all features."""
    print("=" * 80)
    print("🎯 Nifty Expiry Predictor - Demo")
    print("=" * 80)
    print()
    
    # Create sample data
    print("📊 Creating sample option chain data...")
    spot = 19500
    option_chain = create_sample_option_chain(spot)
    print(f"✅ Generated option chain with {len(option_chain)} strikes")
    print(f"   Spot Price: ₹{spot:,.2f}")
    print()
    
    # 1. Greeks Calculation
    print("-" * 80)
    print("1️⃣  GREEKS CALCULATION")
    print("-" * 80)
    calc = GreeksCalculator(risk_free_rate=0.07)
    
    # Calculate Greeks for ATM call
    greeks = calc.calculate_greeks(
        spot=spot,
        strike=spot,
        time_to_expiry=3/365,  # 3 days to expiry
        volatility=0.20,
        option_type="call"
    )
    
    print(f"ATM Call Option (Strike: {spot})")
    print(f"  Price:  ₹{greeks.price:.2f}")
    print(f"  Delta:  {greeks.delta:.4f}")
    print(f"  Gamma:  {greeks.gamma:.6f}")
    print(f"  Theta:  {greeks.theta:.4f} (per day)")
    print(f"  Vega:   {greeks.vega:.4f}")
    print()
    
    # 2. GEX Analysis
    print("-" * 80)
    print("2️⃣  GAMMA EXPOSURE (GEX) ANALYSIS")
    print("-" * 80)
    gex_calc = GammaExposureCalculator()
    gex_df = gex_calc.calculate_chain_gex(option_chain, spot, days_to_expiry=3)
    gex_levels = gex_calc.find_gex_levels(gex_df, spot)
    
    print(f"GEX Regime:     {gex_levels['gex_regime'].upper()}")
    print(f"Trading Bias:   {gex_levels['trading_bias'].replace('_', ' ').title()}")
    print(f"Total GEX:      {gex_levels['total_gex']:,.0f}")
    print(f"GEX Above Spot: {gex_levels['gex_above_spot']:,.0f}")
    print(f"GEX Below Spot: {gex_levels['gex_below_spot']:,.0f}")
    
    if gex_levels['flip_levels']:
        print(f"\nGEX Flip Levels:")
        for i, level in enumerate(gex_levels['flip_levels'], 1):
            print(f"  {i}. ₹{level:.2f}")
    
    print(f"\nKey Strikes:")
    print(f"  Max Positive GEX: ₹{gex_levels['max_positive_gex_strike']:.0f}")
    print(f"  Max Negative GEX: ₹{gex_levels['max_negative_gex_strike']:.0f}")
    print()
    
    # 3. Max Pain
    print("-" * 80)
    print("3️⃣  MAX PAIN ANALYSIS")
    print("-" * 80)
    mp_calc = MaxPainCalculator()
    max_pain, pain_df = mp_calc.calculate_max_pain(option_chain)
    
    print(f"Max Pain Strike:       ₹{max_pain:.0f}")
    print(f"Current Spot:          ₹{spot:.0f}")
    print(f"Distance from Spot:    ₹{spot - max_pain:.0f}")
    print(f"Distance (% of spot):  {((spot - max_pain) / spot * 100):.2f}%")
    
    # Support and resistance
    sr_levels = mp_calc.find_support_resistance(option_chain, num_levels=3)
    print(f"\nResistance Levels (High Call OI):")
    for i, level in enumerate(sr_levels['resistance'], 1):
        print(f"  {i}. ₹{level:.0f}")
    
    print(f"\nSupport Levels (High Put OI):")
    for i, level in enumerate(sr_levels['support'], 1):
        print(f"  {i}. ₹{level:.0f}")
    print()
    
    # 4. OI Analysis
    print("-" * 80)
    print("4️⃣  OPEN INTEREST ANALYSIS")
    print("-" * 80)
    oi_analyzer = OIAnalyzer()
    
    # PCR
    pcr = oi_analyzer.calculate_pcr(option_chain, method='oi')
    sentiment = oi_analyzer.interpret_pcr(pcr)
    
    print(f"Put-Call Ratio (OI):  {pcr:.2f}")
    print(f"Market Sentiment:     {sentiment.upper()}")
    
    # OI Distribution
    oi_dist = oi_analyzer.calculate_oi_distribution(option_chain, spot)
    print(f"\nOI Distribution:")
    print(f"  Total Call OI:  {oi_dist['total_call_oi']:,.0f}")
    print(f"  Total Put OI:   {oi_dist['total_put_oi']:,.0f}")
    print(f"  ITM Call OI:    {oi_dist['itm_call_oi']:,.0f} ({oi_dist['itm_call_oi_pct']:.1f}%)")
    print(f"  OTM Call OI:    {oi_dist['otm_call_oi']:,.0f} ({oi_dist['otm_call_oi_pct']:.1f}%)")
    print(f"  ITM Put OI:     {oi_dist['itm_put_oi']:,.0f} ({oi_dist['itm_put_oi_pct']:.1f}%)")
    print(f"  OTM Put OI:     {oi_dist['otm_put_oi']:,.0f} ({oi_dist['otm_put_oi_pct']:.1f}%)")
    
    # Call/Put Walls
    walls = oi_analyzer.find_call_put_walls(option_chain, num_walls=3)
    print(f"\nCall Walls (Resistance):")
    for i, wall in enumerate(walls['call_walls'], 1):
        print(f"  {i}. Strike: ₹{wall['strike']:.0f}, OI: {wall['call_oi']:,.0f}")
    
    print(f"\nPut Walls (Support):")
    for i, wall in enumerate(walls['put_walls'], 1):
        print(f"  {i}. Strike: ₹{wall['strike']:.0f}, OI: {wall['put_oi']:,.0f}")
    print()
    
    # Summary
    print("=" * 80)
    print("✅ DEMO COMPLETED SUCCESSFULLY")
    print("=" * 80)
    print("\nNext Steps:")
    print("  1. Run the dashboard:  streamlit run dashboard/app.py")
    print("  2. Explore notebooks:  jupyter notebook notebooks/")
    print("  3. Run tests:          pytest tests/ -v")
    print("  4. See documentation:  cat README.md")
    print()


if __name__ == "__main__":
    main()
