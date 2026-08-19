import numpy as np
import pandas as pd

from src.config import PROCESSED_DATA_DIR
from src.data.database import read_table, write_table


REQUIRED_SERIES = [
    "brent",
    "wti",
    "production_kbd",
    "stocks_kbbl",
    "imports_kbd",
    "exports_kbd",
]


def build_weekly_market() -> pd.DataFrame:
    raw = read_table("market_series")

    raw["period"] = pd.to_datetime(raw["period"])
    raw["value"] = pd.to_numeric(
        raw["value"],
        errors="coerce",
    )

    wide = raw.pivot_table(
        index="period",
        columns="series_name",
        values="value",
        aggfunc="last",
    )

    # Put every series onto the same weekly Friday timeline.
    weekly = wide.resample("W-FRI").last()

    # A one-week fill handles reporting dates shifted by holidays.
    weekly = weekly.ffill(limit=1)

    weekly = weekly.dropna(
        subset=REQUIRED_SERIES
    ).copy()

    weekly["brent_wti_spread"] = (
        weekly["brent"] - weekly["wti"]
    )

    weekly["stock_change_kbbl"] = (
        weekly["stocks_kbbl"].diff()
    )

    weekly["production_change_kbd"] = (
        weekly["production_kbd"].diff()
    )

    weekly["net_imports_kbd"] = (
        weekly["imports_kbd"]
        - weekly["exports_kbd"]
    )

    weekly["brent_return_1w"] = (
        weekly["brent"].pct_change()
    )

    weekly["brent_ma_4w"] = (
        weekly["brent"]
        .rolling(4)
        .mean()
    )

    weekly["brent_ma_12w"] = (
        weekly["brent"]
        .rolling(12)
        .mean()
    )

    weekly["brent_volatility_8w"] = (
        weekly["brent_return_1w"]
        .rolling(8)
        .std()
        * np.sqrt(52)
    )

    weekly = weekly.reset_index()

    ordered_columns = [
        "period",
        "brent",
        "wti",
        "brent_wti_spread",
        "production_kbd",
        "production_change_kbd",
        "stocks_kbbl",
        "stock_change_kbbl",
        "imports_kbd",
        "exports_kbd",
        "net_imports_kbd",
        "brent_return_1w",
        "brent_ma_4w",
        "brent_ma_12w",
        "brent_volatility_8w",
    ]

    weekly = weekly[ordered_columns]

    write_table(
        weekly,
        "weekly_market",
    )

    output_path = (
        PROCESSED_DATA_DIR
        / "weekly_market.csv"
    )

    weekly.to_csv(
        output_path,
        index=False,
    )

    print(
        f"Weekly market dataset contains "
        f"{len(weekly):,} observations."
    )

    return weekly


if __name__ == "__main__":
    build_weekly_market()