"""Script to download historical data."""

import argparse
from datetime import datetime, timedelta
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from data.collectors.nse_scraper import NSEDataCollector
from config.logging_config import get_logger

logger = get_logger(__name__)


def main():
    """Download historical Bhavcopy data."""
    parser = argparse.ArgumentParser(description="Download historical NSE data")
    parser.add_argument(
        "--start-date",
        type=str,
        required=True,
        help="Start date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--end-date",
        type=str,
        default=None,
        help="End date (YYYY-MM-DD), defaults to today",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/raw",
        help="Output directory for downloaded files",
    )
    
    args = parser.parse_args()
    
    # Parse dates
    start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
    end_date = (
        datetime.strptime(args.end_date, "%Y-%m-%d")
        if args.end_date
        else datetime.now()
    )
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize collector
    collector = NSEDataCollector()
    
    # Download data for each date
    current_date = start_date
    success_count = 0
    fail_count = 0
    
    while current_date <= end_date:
        # Skip weekends
        if current_date.weekday() < 5:  # Monday = 0, Friday = 4
            logger.info(f"Downloading data for {current_date.strftime('%Y-%m-%d')}")
            
            result = collector.download_bhavcopy(current_date, str(output_dir))
            
            if result:
                success_count += 1
            else:
                fail_count += 1
        
        current_date += timedelta(days=1)
    
    logger.info(f"Download complete. Success: {success_count}, Failed: {fail_count}")


if __name__ == "__main__":
    main()
