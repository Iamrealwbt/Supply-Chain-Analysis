"""Shared paths and analysis parameters for the SupplyGraph project.

Every path is resolved from this file, so the repository can be cloned to any
location.  Notebooks import these values instead of using machine-specific
absolute paths.

Set ``SUPPLY_CHAIN_PROCESSED_DIR`` when generated CSV files should be written
somewhere other than ``Data/processed`` (for example, during automated tests).
"""

from __future__ import annotations

import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "Data"
RAW_DIR = DATA_DIR / "raw"


def _path_from_env(variable: str, default: Path) -> Path:
    """Return an optional environment path or a project-relative default."""
    value = os.environ.get(variable)
    return Path(value).expanduser().resolve() if value else default


PROCESSED_DIR = _path_from_env(
    "SUPPLY_CHAIN_PROCESSED_DIR",
    DATA_DIR / "processed",
)
OUTPUT_DIR = PROJECT_ROOT / "Outputs"
FIGURE_DIR = OUTPUT_DIR / "figures"

# Raw SupplyGraph files. Names match the source repository exactly so the code
# also works on case-sensitive operating systems such as Linux.
NODES_FILE = RAW_DIR / "Nodes" / "Node Types (Product Group and Subgroup).csv"
TEMPORAL_UNIT_DIR = RAW_DIR / "Temporal Data" / "Unit"
SALES_FILE = TEMPORAL_UNIT_DIR / "Sales Order.csv"
PRODUCTION_FILE = TEMPORAL_UNIT_DIR / "Production .csv"
DELIVERY_FILE = TEMPORAL_UNIT_DIR / "Delivery To distributor.csv"
FACTORY_FILE = TEMPORAL_UNIT_DIR / "Factory Issue.csv"

# Processed datasets.
DAILY_FLOW_FILE = PROCESSED_DIR / "daily_flow.csv"
WEEKLY_FLOW_FILE = PROCESSED_DIR / "weekly_product_flow.csv"
PRODUCT_RISK_FILE = PROCESSED_DIR / "product_risk_current.csv"
FORECAST_PERFORMANCE_FILE = PROCESSED_DIR / "forecast_model_performance.csv"
FORECAST_14D_FILE = PROCESSED_DIR / "forecast_14d.csv"
FORECAST_RISK_LEGACY_FILE = PROCESSED_DIR / "forecast_risk_summary.csv"
FORECAST_TOPDOWN_FILE = PROCESSED_DIR / "forecast_2w_topdown.csv"
FORECAST_RISK_FILE = PROCESSED_DIR / "forecast_risk_topdown.csv"
GRANULARITY_FILE = PROCESSED_DIR / "forecast_granularity_comparison.csv"

# Shared analysis parameters.
WEEK_FREQUENCY = "W-WED"
KPI_WEEK_FREQUENCY = "W-MON"
OPERATIONAL_RISK_DAYS = 28
HOLDOUT_WEEKS = 4
RECENT_WEEKS = 8
HORIZON_WEEKS = 2
RECENT_SHARE_WEIGHT = 0.80
DELIVERY_THRESHOLD = 0.90


def ensure_output_directories() -> None:
    """Create generated-data and figure directories when needed."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)


def check_raw_data() -> None:
    """Fail early with a useful message when source files are unavailable."""
    required = (
        NODES_FILE,
        SALES_FILE,
        PRODUCTION_FILE,
        DELIVERY_FILE,
        FACTORY_FILE,
    )
    missing = [path for path in required if not path.is_file()]
    if missing:
        formatted = "\n  ".join(str(path) for path in missing)
        raise FileNotFoundError(
            f"Missing SupplyGraph files:\n  {formatted}\n\n"
            "Download https://github.com/ciol-researchlab/SupplyGraph and "
            f"place the dataset under {RAW_DIR}."
        )
