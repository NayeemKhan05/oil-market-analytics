import json
import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


ROOT_DIR = Path(__file__).resolve().parents[1]

DB_PATH = (
    ROOT_DIR
    / "data"
    / "processed"
    / "oil_market.db"
)

METRICS_PATH = (
    ROOT_DIR
    / "data"
    / "processed"
    / "forecast_metrics.json"
)


st.set_page_config(
    page_title="Oil Market Analytics",
    page_icon=None,
    layout="wide",
)


@st.cache_data
def load_table(table_name: str) -> pd.DataFrame:
    connection = sqlite3.connect(DB_PATH)

    try:
        df = pd.read_sql_query(
            f"SELECT * FROM {table_name}",
            connection,
        )
    finally:
        connection.close()

    if "period" in df.columns:
        df["period"] = pd.to_datetime(
            df["period"]
        )

    return df


@st.cache_data
def load_forecast_metrics() -> dict:
    with open(
        METRICS_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


if not DB_PATH.exists():
    st.error(
        "Market database not found. "
        "Run `python main.py` first."
    )
    st.stop()


market = load_table("weekly_market")
anomalies = load_table("market_anomalies")
forecast_results = load_table(
    "forecast_results"
)
forecast_metrics = load_forecast_metrics()


market = market.sort_values("period")

latest = market.iloc[-1]
previous = market.iloc[-2]


st.title("Oil Market Analytics")

st.caption(
    "Quantitative analysis of crude oil prices, "
    "US supply fundamentals, trade flows, "
    "market anomalies and short-term Brent forecasts."
)


overview_tab, fundamentals_tab, anomalies_tab, forecast_tab = st.tabs(
    [
        "Market Overview",
        "Fundamentals & Trade",
        "Market Anomalies",
        "Price Forecast",
    ]
)


with overview_tab:
    brent_change = (
        latest["brent"]
        - previous["brent"]
    )

    wti_change = (
        latest["wti"]
        - previous["wti"]
    )

    spread_change = (
        latest["brent_wti_spread"]
        - previous["brent_wti_spread"]
    )

    inventory_change = (
        latest["stock_change_kbbl"]
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Brent",
        f"${latest['brent']:.2f}",
        f"{brent_change:+.2f}",
    )

    col2.metric(
        "WTI",
        f"${latest['wti']:.2f}",
        f"{wti_change:+.2f}",
    )

    col3.metric(
        "Brent-WTI Spread",
        f"${latest['brent_wti_spread']:.2f}",
        f"{spread_change:+.2f}",
    )

    col4.metric(
        "Weekly Inventory Change",
        f"{inventory_change / 1000:+.2f}m bbl",
    )

    st.subheader("Crude Oil Prices")

    prices = market[
        [
            "period",
            "brent",
            "wti",
        ]
    ].melt(
        id_vars="period",
        var_name="benchmark",
        value_name="price",
    )

    price_chart = px.line(
        prices,
        x="period",
        y="price",
        color="benchmark",
        labels={
            "period": "Date",
            "price": "USD per barrel",
            "benchmark": "Benchmark",
        },
    )

    st.plotly_chart(
        price_chart,
        width="stretch",
    )

    st.subheader("Brent-WTI Spread")

    spread_chart = px.line(
        market,
        x="period",
        y="brent_wti_spread",
        labels={
            "period": "Date",
            "brent_wti_spread": (
                "USD per barrel"
            ),
        },
    )

    spread_chart.add_hline(
        y=0,
        line_dash="dash",
    )

    st.plotly_chart(
        spread_chart,
        width="stretch",
    )


with fundamentals_tab:
    col1, col2, col3 = st.columns(3)

    production_delta = (
        latest["production_kbd"]
        - previous["production_kbd"]
    )

    imports_delta = (
        latest["imports_kbd"]
        - previous["imports_kbd"]
    )

    exports_delta = (
        latest["exports_kbd"]
        - previous["exports_kbd"]
    )

    col1.metric(
        "US Crude Production",
        f"{latest['production_kbd']:,.0f} kb/d",
        f"{production_delta:+,.0f} kb/d",
    )

    col2.metric(
        "Crude Imports",
        f"{latest['imports_kbd']:,.0f} kb/d",
        f"{imports_delta:+,.0f} kb/d",
    )

    col3.metric(
        "Crude Exports",
        f"{latest['exports_kbd']:,.0f} kb/d",
        f"{exports_delta:+,.0f} kb/d",
    )

    st.subheader("US Crude Production")

    production_chart = px.line(
        market,
        x="period",
        y="production_kbd",
        labels={
            "period": "Date",
            "production_kbd": (
                "Thousand barrels per day"
            ),
        },
    )

    st.plotly_chart(
        production_chart,
        width="stretch",
    )

    st.subheader("Commercial Crude Inventories")

    inventory_chart = px.line(
        market,
        x="period",
        y="stocks_kbbl",
        labels={
            "period": "Date",
            "stocks_kbbl": (
                "Thousand barrels"
            ),
        },
    )

    st.plotly_chart(
        inventory_chart,
        width="stretch",
    )

    st.subheader("Weekly Inventory Builds and Draws")

    recent_market = market.tail(104)

    inventory_change_chart = px.bar(
        recent_market,
        x="period",
        y="stock_change_kbbl",
        labels={
            "period": "Date",
            "stock_change_kbbl": (
                "Weekly change "
                "(thousand barrels)"
            ),
        },
    )

    inventory_change_chart.add_hline(
        y=0,
    )

    st.plotly_chart(
        inventory_change_chart,
        width="stretch",
    )

    st.subheader("Crude Trade Flows")

    trade = market[
        [
            "period",
            "imports_kbd",
            "exports_kbd",
            "net_imports_kbd",
        ]
    ].melt(
        id_vars="period",
        var_name="flow",
        value_name="volume",
    )

    trade_chart = px.line(
        trade,
        x="period",
        y="volume",
        color="flow",
        labels={
            "period": "Date",
            "volume": (
                "Thousand barrels per day"
            ),
            "flow": "Trade Flow",
        },
    )

    st.plotly_chart(
        trade_chart,
        width="stretch",
    )


with anomalies_tab:
    st.subheader(
        "Statistically Unusual Market Movements"
    )

    st.write(
        "Anomalies are observations at least "
        "two rolling standard deviations from "
        "their 52-week mean."
    )

    if anomalies.empty:
        st.info(
            "No anomalies were detected."
        )
    else:
        recent_cutoff = (
            market["period"].max()
            - pd.DateOffset(years=2)
        )

        recent_anomalies = anomalies[
            anomalies["period"]
            >= recent_cutoff
        ].copy()

        anomaly_chart = px.scatter(
            recent_anomalies,
            x="period",
            y="z_score",
            color="metric",
            hover_data=[
                "value",
                "direction",
                "severity",
            ],
            labels={
                "period": "Date",
                "z_score": "Rolling Z-score",
                "metric": "Metric",
            },
        )

        anomaly_chart.add_hline(
            y=2,
            line_dash="dash",
        )

        anomaly_chart.add_hline(
            y=-2,
            line_dash="dash",
        )

        st.plotly_chart(
            anomaly_chart,
            width="stretch",
        )

        st.subheader("Latest Signals")

        display_anomalies = (
            anomalies.sort_values(
                "period",
                ascending=False,
            )
            .head(20)
            .copy()
        )

        display_anomalies[
            "z_score"
        ] = display_anomalies[
            "z_score"
        ].round(2)

        st.dataframe(
            display_anomalies,
            width="stretch",
            hide_index=True,
        )


with forecast_tab:
    st.subheader(
        "One-Week Brent Price Forecast"
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Latest Brent",
        (
            f"${forecast_metrics['latest_brent']:.2f}"
        ),
    )

    col2.metric(
        "Next-Week Forecast",
        (
            f"${forecast_metrics['next_week_prediction']:.2f}"
        ),
    )

    col3.metric(
        "Model MAE",
        (
            f"${forecast_metrics['model_mae']:.2f}"
        ),
    )

    col4.metric(
        "Direction Accuracy",
        (
            f"{forecast_metrics['directional_accuracy']:.1%}"
        ),
    )

    st.caption(
        "Forecast date: "
        f"{forecast_metrics['forecast_date']}"
    )

    st.subheader("Backtest")

    forecast_chart = go.Figure()

    forecast_chart.add_trace(
        go.Scatter(
            x=forecast_results["period"],
            y=forecast_results[
                "actual_brent"
            ],
            mode="lines",
            name="Actual Brent",
        )
    )

    forecast_chart.add_trace(
        go.Scatter(
            x=forecast_results["period"],
            y=forecast_results[
                "predicted_brent"
            ],
            mode="lines",
            name="Model Forecast",
        )
    )

    forecast_chart.add_trace(
        go.Scatter(
            x=forecast_results["period"],
            y=forecast_results[
                "baseline_brent"
            ],
            mode="lines",
            name="Naive Baseline",
        )
    )

    forecast_chart.update_layout(
        xaxis_title="Date",
        yaxis_title="USD per barrel",
    )

    st.plotly_chart(
        forecast_chart,
        width="stretch",
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("MAE Comparison")

        mae_data = pd.DataFrame(
            {
                "Model": [
                    "Random Forest",
                    "Naive Baseline",
                ],
                "MAE": [
                    forecast_metrics[
                        "model_mae"
                    ],
                    forecast_metrics[
                        "baseline_mae"
                    ],
                ],
            }
        )

        mae_chart = px.bar(
            mae_data,
            x="Model",
            y="MAE",
            labels={
                "MAE": "Mean absolute error ($)"
            },
        )

        st.plotly_chart(
            mae_chart,
            width="stretch",
        )

    with col2:
        st.subheader("RMSE Comparison")

        rmse_data = pd.DataFrame(
            {
                "Model": [
                    "Random Forest",
                    "Naive Baseline",
                ],
                "RMSE": [
                    forecast_metrics[
                        "model_rmse"
                    ],
                    forecast_metrics[
                        "baseline_rmse"
                    ],
                ],
            }
        )

        rmse_chart = px.bar(
            rmse_data,
            x="Model",
            y="RMSE",
            labels={
                "RMSE": (
                    "Root mean squared error ($)"
                )
            },
        )

        st.plotly_chart(
            rmse_chart,
            width="stretch",
        )

    st.subheader("Model Feature Importance")

    importance = pd.DataFrame(
        {
            "feature": list(
                forecast_metrics[
                    "feature_importance"
                ].keys()
            ),
            "importance": list(
                forecast_metrics[
                    "feature_importance"
                ].values()
            ),
        }
    )

    importance = importance.sort_values(
        "importance",
        ascending=True,
    )

    importance_chart = px.bar(
        importance,
        x="importance",
        y="feature",
        orientation="h",
        labels={
            "importance": "Importance",
            "feature": "Feature",
        },
    )

    st.plotly_chart(
        importance_chart,
        width="stretch",
    )

    st.caption(
        "The forecast is an analytical experiment, "
        "not investment advice. Model performance "
        "should be interpreted relative to the "
        "naive baseline."
    )