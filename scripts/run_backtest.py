"""Script to run backtests."""

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.logging_config import get_logger

logger = get_logger(__name__)


def main():
    """Run backtest for a strategy."""
    parser = argparse.ArgumentParser(description="Run strategy backtest")
    parser.add_argument(
        "--strategy",
        type=str,
        required=True,
        help="Strategy name (iron_condor, straddle, gamma_scalping)",
    )
    parser.add_argument(
        "--start",
        type=str,
        required=True,
        help="Start date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--end",
        type=str,
        required=True,
        help="End date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--capital",
        type=float,
        default=1000000,
        help="Initial capital (default: 1000000)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="backtest_results.csv",
        help="Output file for results",
    )
    
    args = parser.parse_args()
    
    logger.info(f"Running backtest for {args.strategy}")
    logger.info(f"Period: {args.start} to {args.end}")
    logger.info(f"Initial Capital: ₹{args.capital:,.0f}")
    
    # TODO: Implement backtest execution
    logger.warning("Backtest execution not yet implemented")
    logger.info("This is a placeholder script for future implementation")
    
    print("\nBacktest Configuration:")
    print(f"  Strategy: {args.strategy}")
    print(f"  Period: {args.start} to {args.end}")
    print(f"  Capital: ₹{args.capital:,.0f}")
    print(f"  Output: {args.output}")
    print("\n⚠️  Backtest execution coming soon!")


if __name__ == "__main__":
    main()
