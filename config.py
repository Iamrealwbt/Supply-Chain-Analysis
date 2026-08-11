"""
Central path and parameter configuration.

Import at the top of every notebook:

    import sys; sys.path.append("..")
    from config import RAW_DIR, PROCESSED_DIR, FIG_DIR

Override the output location without editing code:

    export SUPPLY_CHAIN_OUTPUT_DIR=/some/other/path
"""

import os
from pathlib import Path

# Project root = folder containing this file. Works from notebooks/ or repo root.
PROJECT_ROOT = Path(__file__).resolve().parent

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = Path(os.environ.get("SUPPLY_CHAIN_OUTPUT_DIR", DATA_DIR / "processed"))
FIG_DIR = PROJECT_ROOT / "fig"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

# ---- Raw SupplyGraph files -------------------------------------------------
# Adjust only if you unpack the download with different folder names.
NODES_FILE = RAW_DIR / "Nodes" / "Node Types (Product Group and Subgroup).csv"
TEMPORAL_DIR = RAW_DIR / "Temporal Data" / "Unit"

SALES_FILE = TEMPORAL_DIR / "Sales Order.csv"
PRODUCTION_FILE = TEMPORAL_DIR / "Production .csv"   # trailing space is in the source
DELIVERY_FILE = TEMPORAL_DIR / "Delivery To distributor.csv"
FACTORY_FILE = TEMPORAL_DIR / "Factory issue.csv"

# ---- Processed outputs -----------------------------------------------------
DAILY_FLOW_FILE = PROCESSED_DIR / "daily_flow.csv"
WEEKLY_FLOW_FILE = PROCESSED_DIR / "weekly_product_flow.csv"
FORECAST_TOPDOWN_FILE = PROCESSED_DIR / "forecast_2w_topdown.csv"
FORECAST_RISK_FILE = PROCESSED_DIR / "forecast_risk_topdown.csv"
GRANULARITY_FILE = PROCESSED_DIR / "forecast_granularity_comparison.csv"

# ---- Analysis parameters ---------------------------------------------------
WEEK_END_DAY = "W-WED"      # keeps the final observed week (2023-08-03 to 08-09) complete
HOLDOUT_WEEKS = 4           # backtest window
RECENT_WEEKS = 8            # lookback for allocation shares and production proxy
HORIZON_WEEKS = 2           # forward forecast horizon
RECENT_SHARE_WEIGHT = 0.80  # recent vs long-run weight in SKU allocation
DELIVERY_THRESHOLD = 0.90   # delivery-to-demand ratio below which a SKU is flagged


def check_raw_data() -> None:
    """Fail early with a useful message if the dataset has not been downloaded."""
    missing = [
        p for p in (NODES_FILE, SALES_FILE, PRODUCTION_FILE, DELIVERY_FILE, FACTORY_FILE)
        if not p.exists()
    ]
    if missing:
        raise FileNotFoundError(
            "Missing SupplyGraph files:\n  "
            + "\n  ".join(str(p) for p in missing)
            + "\n\nDownload from https://github.com/ciol-researchlab/SupplyGraph "
              f"and unpack into {RAW_DIR}"
        )
