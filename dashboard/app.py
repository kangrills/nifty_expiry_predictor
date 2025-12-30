"""Streamlit dashboard for Nifty Expiry Predictor."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.logging_config import get_logger
from data.collectors.nse_scraper import NSEDataCollector
from features.greeks_calculator import GreeksCalculator
from features.gex_calculator import GammaExposureCalculator
from features.max_pain import MaxPainCalculator
from features.oi_analysis import OIAnalyzer

logger = get_logger(__name__)

# Page configuration
st.set_page_config(
    page_title="Nifty Expiry Predictor",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main():
    """Main dashboard application."""
    st.title("📈 Nifty Weekly Expiry Predictor")
    st.markdown("### Real-time Option Chain Analysis with GEX, Max Pain & OI Insights")

    # Sidebar
    with st.sidebar:
        st.header("Settings")
        symbol = st.selectbox("Select Index", ["NIFTY", "BANKNIFTY", "FINNIFTY"])
        
        refresh_button = st.button("🔄 Refresh Data")
        
        st.markdown("---")
        st.markdown("### Analysis Tools")
        show_gex = st.checkbox("GEX Analysis", value=True)
        show_max_pain = st.checkbox("Max Pain", value=True)
        show_oi = st.checkbox("OI Analysis", value=True)
        show_pcr = st.checkbox("PCR Analysis", value=True)

    # Fetch data
    with st.spinner("Fetching option chain data..."):
        try:
            nse = NSEDataCollector()
            option_chain = nse.get_option_chain(symbol)
            
            if option_chain.empty:
                st.error("Failed to fetch option chain data")
                return
            
            spot = option_chain.attrs.get("underlying", 0)
            timestamp = option_chain.attrs.get("timestamp", "")
            
            st.success(f"✅ Data fetched successfully | Spot: {spot:.2f} | Time: {timestamp}")
            
        except Exception as e:
            st.error(f"Error fetching data: {e}")
            logger.error(f"Dashboard error: {e}")
            return

    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Spot Price", f"₹{spot:.2f}")
    
    with col2:
        total_call_oi = option_chain["call_oi"].sum()
        st.metric("Total Call OI", f"{total_call_oi:,.0f}")
    
    with col3:
        total_put_oi = option_chain["put_oi"].sum()
        st.metric("Total Put OI", f"{total_put_oi:,.0f}")
    
    with col4:
        pcr = total_put_oi / total_call_oi if total_call_oi > 0 else 0
        st.metric("PCR (OI)", f"{pcr:.2f}")

    # Max Pain Analysis
    if show_max_pain:
        st.markdown("---")
        st.subheader("📍 Max Pain Analysis")
        
        try:
            max_pain_calc = MaxPainCalculator()
            max_pain, pain_df = max_pain_calc.calculate_max_pain(option_chain)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Plot pain curve
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=pain_df["strike"],
                    y=pain_df["total_pain"],
                    mode="lines",
                    name="Total Pain",
                    line=dict(color="red", width=2)
                ))
                fig.add_vline(x=max_pain, line_dash="dash", line_color="green",
                             annotation_text=f"Max Pain: {max_pain}")
                fig.add_vline(x=spot, line_dash="dash", line_color="blue",
                             annotation_text=f"Spot: {spot:.0f}")
                
                fig.update_layout(
                    title="Max Pain Curve",
                    xaxis_title="Strike Price",
                    yaxis_title="Total Pain (₹)",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.metric("Max Pain Strike", f"₹{max_pain:.0f}")
                distance = spot - max_pain
                st.metric("Distance from Spot", f"₹{distance:.0f}")
                
                # Support and resistance
                sr_levels = max_pain_calc.find_support_resistance(option_chain, num_levels=3)
                st.write("**Resistance Levels:**")
                for level in sr_levels["resistance"]:
                    st.write(f"- ₹{level:.0f}")
                
                st.write("**Support Levels:**")
                for level in sr_levels["support"]:
                    st.write(f"- ₹{level:.0f}")
        
        except Exception as e:
            st.error(f"Error calculating Max Pain: {e}")

    # GEX Analysis
    if show_gex:
        st.markdown("---")
        st.subheader("🎲 Gamma Exposure (GEX) Analysis")
        
        try:
            gex_calc = GammaExposureCalculator()
            # Assume 1 day to expiry for demonstration
            gex_df = gex_calc.calculate_chain_gex(option_chain, spot, days_to_expiry=1)
            gex_levels = gex_calc.find_gex_levels(gex_df, spot)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Plot GEX profile
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=gex_df["strike"],
                    y=gex_df["net_gex"],
                    name="Net GEX",
                    marker_color=gex_df["net_gex"].apply(lambda x: "green" if x > 0 else "red")
                ))
                fig.add_vline(x=spot, line_dash="dash", line_color="blue",
                             annotation_text=f"Spot: {spot:.0f}")
                
                fig.update_layout(
                    title="Gamma Exposure Profile",
                    xaxis_title="Strike Price",
                    yaxis_title="Net GEX",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.metric("GEX Regime", gex_levels["gex_regime"].upper())
                st.metric("Trading Bias", gex_levels["trading_bias"].replace("_", " ").title())
                st.metric("Total GEX", f"{gex_levels['total_gex']:,.0f}")
                
                if gex_levels["flip_levels"]:
                    st.write("**Flip Levels:**")
                    for level in gex_levels["flip_levels"]:
                        st.write(f"- ₹{level:.0f}")
        
        except Exception as e:
            st.error(f"Error calculating GEX: {e}")

    # Option Chain Table
    st.markdown("---")
    st.subheader("📊 Option Chain")
    
    # Filter strikes near spot
    strike_range = 500
    filtered_chain = option_chain[
        (option_chain["strike"] >= spot - strike_range) &
        (option_chain["strike"] <= spot + strike_range)
    ].copy()
    
    # Format for display
    display_df = filtered_chain[[
        "strike", "call_oi", "call_volume", "call_ltp", 
        "put_ltp", "put_volume", "put_oi"
    ]].copy()
    
    # Highlight ATM strike
    def highlight_atm(row):
        if abs(row["strike"] - spot) < 50:
            return ["background-color: yellow"] * len(row)
        return [""] * len(row)
    
    st.dataframe(
        display_df.style.apply(highlight_atm, axis=1),
        use_container_width=True,
        height=400
    )

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center'>Built with ❤️ using Streamlit | "
        "Data source: NSE India</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
