from src.analytics.anomalies import detect_anomalies
from src.analytics.features import build_weekly_market
from src.analytics.forecast import train_forecast_model
from src.data.database import (
    initialise_database,
    write_market_series,
)
from src.data.fetch_eia import fetch_all_series


def main() -> None:
    print("Starting oil market analytics pipeline.")
    print()

    initialise_database()

    raw_data = fetch_all_series()
    write_market_series(raw_data)

    print()

    build_weekly_market()

    print()

    detect_anomalies()

    print()

    train_forecast_model()

    print()
    print("Pipeline complete.")


if __name__ == "__main__":
    main()