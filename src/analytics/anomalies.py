import numpy as np
import pandas as pd

from src.config import PROCESSED_DATA_DIR
from src.data.database import read_table, write_table


ANOMALY_METRICS = {
    "stock_change_kbbl": "Inventory Change",
    "brent_return_1w": "Brent Weekly Return",
    "net_imports_kbd": "Net Imports",
    "production_change_kbd": "Production Change",
}


def rolling_z_score(
    series: pd.Series,
    window: int = 52,
    min_periods: int = 26,
) -> pd.Series:
    rolling_mean = series.rolling(
        window,
        min_periods=min_periods,
    ).mean()

    rolling_std = series.rolling(
        window,
        min_periods=min_periods,
    ).std()

    return (
        (series - rolling_mean)
        / rolling_std.replace(0, np.nan)
    )


def get_severity(z_score: float) -> str:
    magnitude = abs(z_score)

    if magnitude >= 3:
        return "High"

    if magnitude >= 2.5:
        return "Elevated"

    return "Moderate"


def detect_anomalies(
    threshold: float = 2.0,
) -> pd.DataFrame:
    market = read_table("weekly_market")

    market["period"] = pd.to_datetime(
        market["period"]
    )

    anomalies = []

    for column, display_name in ANOMALY_METRICS.items():
        values = pd.to_numeric(
            market[column],
            errors="coerce",
        )

        z_scores = rolling_z_score(values)

        anomaly_mask = (
            z_scores.abs() >= threshold
        )

        for index in market.index[anomaly_mask]:
            z_score = float(
                z_scores.loc[index]
            )

            anomalies.append(
                {
                    "period": market.loc[
                        index,
                        "period",
                    ],
                    "metric": display_name,
                    "value": float(
                        values.loc[index]
                    ),
                    "z_score": z_score,
                    "direction": (
                        "Above normal"
                        if z_score > 0
                        else "Below normal"
                    ),
                    "severity": get_severity(
                        z_score
                    ),
                }
            )

    anomalies_df = pd.DataFrame(anomalies)

    if not anomalies_df.empty:
        anomalies_df = anomalies_df.sort_values(
            ["period", "z_score"],
            ascending=[False, False],
        ).reset_index(drop=True)

    write_table(
        anomalies_df,
        "market_anomalies",
    )

    output_path = (
        PROCESSED_DATA_DIR
        / "market_anomalies.csv"
    )

    anomalies_df.to_csv(
        output_path,
        index=False,
    )

    print(
        f"Detected {len(anomalies_df):,} "
        f"historical anomalies."
    )

    return anomalies_df


if __name__ == "__main__":
    detect_anomalies()