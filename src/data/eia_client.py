from typing import Iterable

import pandas as pd
import requests


class EIAClient:
    BASE_URL = "https://api.eia.gov/v2"

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError(
                "EIA_API_KEY is missing. Add your API key to the .env file."
            )

        self.api_key = api_key

    def fetch_series(
        self,
        route: str,
        series_id: str,
        series_name: str,
        frequency: str = "weekly",
        start: str | None = None,
    ) -> pd.DataFrame:
        url = f"{self.BASE_URL}/{route}/data/"

        params = {
            "api_key": self.api_key,
            "frequency": frequency,
            "data[0]": "value",
            "facets[series][]": series_id,
            "sort[0][column]": "period",
            "sort[0][direction]": "asc",
            "offset": 0,
            "length": 5000,
        }

        if start:
            params["start"] = start

        response = requests.get(url, params=params, timeout=30)

        response.raise_for_status()

        payload = response.json()
        rows = payload.get("response", {}).get("data", [])

        if not rows:
            raise ValueError(
                f"No data returned for {series_id} from route {route}."
            )

        df = pd.DataFrame(rows)

        df["period"] = pd.to_datetime(df["period"])
        df["value"] = pd.to_numeric(df["value"], errors="coerce")

        df = df.dropna(subset=["period", "value"])

        df["series_name"] = series_name
        df["source_series"] = series_id

        if "units" not in df.columns:
            df["units"] = None

        return df[
            [
                "period",
                "series_name",
                "value",
                "units",
                "source_series",
            ]
        ].copy()

    def fetch_from_candidate_routes(
        self,
        routes: Iterable[str],
        series_id: str,
        series_name: str,
        frequency: str = "weekly",
        start: str | None = None,
    ) -> pd.DataFrame:
        errors = []

        for route in routes:
            try:
                return self.fetch_series(
                    route=route,
                    series_id=series_id,
                    series_name=series_name,
                    frequency=frequency,
                    start=start,
                )
            except (requests.RequestException, ValueError) as exc:
                errors.append(f"{route}: {exc}")

        error_text = "\n".join(errors)

        raise RuntimeError(
            f"Unable to fetch {series_id} from any candidate route:\n"
            f"{error_text}"
        )