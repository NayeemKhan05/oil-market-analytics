import pandas as pd

from src.config import EIA_API_KEY, RAW_DATA_DIR, START_DATE
from src.data.eia_client import EIAClient


SERIES_CONFIG = [
    {
        "name": "brent",
        "series_id": "RBRTE",
        "routes": ["petroleum/pri/spt"],
    },
    {
        "name": "wti",
        "series_id": "RWTC",
        "routes": ["petroleum/pri/spt"],
    },
    {
        "name": "production_kbd",
        "series_id": "WCRFPUS2",
        "routes": [
            "petroleum/sum/sndw",
            "petroleum/crd/crpdn",
        ],
    },
    {
        "name": "stocks_kbbl",
        "series_id": "WCESTUS1",
        "routes": [
            "petroleum/stoc/wstk",
            "petroleum/sum/sndw",
        ],
    },
    {
        "name": "imports_kbd",
        "series_id": "WCRIMUS2",
        "routes": ["petroleum/move/wkly"],
    },
    {
        "name": "exports_kbd",
        "series_id": "WCREXUS2",
        "routes": ["petroleum/move/wkly"],
    },
]


def fetch_all_series() -> pd.DataFrame:
    client = EIAClient(EIA_API_KEY)

    frames = []

    for config in SERIES_CONFIG:
        print(
            f"Fetching {config['name']} "
            f"({config['series_id']})..."
        )

        df = client.fetch_from_candidate_routes(
            routes=config["routes"],
            series_id=config["series_id"],
            series_name=config["name"],
            frequency="weekly",
            start=START_DATE,
        )

        frames.append(df)

        print(f"  {len(df):,} rows")

    combined = pd.concat(frames, ignore_index=True)

    combined = combined.sort_values(
        ["period", "series_name"]
    ).reset_index(drop=True)

    output_path = RAW_DATA_DIR / "eia_market_data.csv"
    combined.to_csv(output_path, index=False)

    print(f"Raw data saved to {output_path}")

    return combined


if __name__ == "__main__":
    fetch_all_series()