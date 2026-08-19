import sqlite3

import pandas as pd

from src.config import DB_PATH, ROOT_DIR


def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def initialise_database() -> None:
    schema_path = ROOT_DIR / "sql" / "create_tables.sql"

    with open(schema_path, "r", encoding="utf-8") as file:
        schema = file.read()

    with get_connection() as connection:
        connection.executescript(schema)


def write_market_series(df: pd.DataFrame) -> None:
    data = df.copy()
    data["period"] = data["period"].astype(str)

    with get_connection() as connection:
        data.to_sql(
            "market_series",
            connection,
            if_exists="replace",
            index=False,
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_market_series_period
            ON market_series(period)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_market_series_name
            ON market_series(series_name)
            """
        )


def write_table(
    df: pd.DataFrame,
    table_name: str,
    if_exists: str = "replace",
) -> None:
    data = df.copy()

    for column in data.select_dtypes(
        include=["datetime64[ns]"]
    ).columns:
        data[column] = data[column].astype(str)

    with get_connection() as connection:
        data.to_sql(
            table_name,
            connection,
            if_exists=if_exists,
            index=False,
        )


def read_table(table_name: str) -> pd.DataFrame:
    query = f"SELECT * FROM {table_name}"

    with get_connection() as connection:
        return pd.read_sql_query(query, connection)