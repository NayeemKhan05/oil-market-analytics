import json

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    root_mean_squared_error,
)

from src.config import MODELS_DIR, PROCESSED_DATA_DIR
from src.data.database import read_table, write_table


FEATURE_COLUMNS = [
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


def directional_accuracy(
    current_price: np.ndarray,
    actual_price: np.ndarray,
    predicted_price: np.ndarray,
) -> float:
    actual_direction = np.sign(
        actual_price - current_price
    )

    predicted_direction = np.sign(
        predicted_price - current_price
    )

    return float(
        np.mean(
            actual_direction
            == predicted_direction
        )
    )


def train_forecast_model() -> dict:
    market = read_table("weekly_market")

    market["period"] = pd.to_datetime(
        market["period"]
    )

    for column in FEATURE_COLUMNS:
        market[column] = pd.to_numeric(
            market[column],
            errors="coerce",
        )

    market["target_next_week_brent"] = (
        market["brent"].shift(-1)
    )

    modelling_data = market.dropna(
        subset=(
            FEATURE_COLUMNS
            + ["target_next_week_brent"]
        )
    ).copy()

    if len(modelling_data) < 100:
        raise ValueError(
            "Not enough observations to train "
            "the forecasting model."
        )

    split_index = int(
        len(modelling_data) * 0.8
    )

    train = modelling_data.iloc[
        :split_index
    ]

    test = modelling_data.iloc[
        split_index:
    ]

    X_train = train[FEATURE_COLUMNS]
    y_train = train[
        "target_next_week_brent"
    ]

    X_test = test[FEATURE_COLUMNS]
    y_test = test[
        "target_next_week_brent"
    ]

    model = RandomForestRegressor(
        n_estimators=300,
        max_depth=8,
        min_samples_leaf=3,
        random_state=42,
        n_jobs=-1,
    )

    model.fit(
        X_train,
        y_train,
    )

    predictions = model.predict(X_test)

    # The baseline simply assumes next week's price
    # will equal this week's price.
    baseline_predictions = (
        X_test["brent"].to_numpy()
    )

    model_mae = mean_absolute_error(
        y_test,
        predictions,
    )

    baseline_mae = mean_absolute_error(
        y_test,
        baseline_predictions,
    )

    model_rmse = root_mean_squared_error(
        y_test,
        predictions,
    )

    baseline_rmse = root_mean_squared_error(
        y_test,
        baseline_predictions,
    )

    direction_accuracy = (
        directional_accuracy(
            current_price=X_test[
                "brent"
            ].to_numpy(),
            actual_price=y_test.to_numpy(),
            predicted_price=predictions,
        )
    )

    forecast_results = pd.DataFrame(
        {
            "period": test["period"],
            "actual_brent": y_test.to_numpy(),
            "predicted_brent": predictions,
            "baseline_brent": baseline_predictions,
        }
    )

    write_table(
        forecast_results,
        "forecast_results",
    )

    forecast_results.to_csv(
        PROCESSED_DATA_DIR
        / "forecast_results.csv",
        index=False,
    )

    latest_features = (
        market
        .dropna(subset=FEATURE_COLUMNS)
        .iloc[-1]
    )

    latest_X = pd.DataFrame(
        [
            latest_features[
                FEATURE_COLUMNS
            ].to_dict()
        ]
    )

    next_week_prediction = float(
        model.predict(latest_X)[0]
    )

    forecast_date = (
        latest_features["period"]
        + pd.Timedelta(days=7)
    )

    feature_importance = {
        feature: float(importance)
        for feature, importance in sorted(
            zip(
                FEATURE_COLUMNS,
                model.feature_importances_,
            ),
            key=lambda item: item[1],
            reverse=True,
        )
    }

    metrics = {
        "training_observations": len(train),
        "testing_observations": len(test),
        "model_mae": float(model_mae),
        "baseline_mae": float(
            baseline_mae
        ),
        "model_rmse": float(model_rmse),
        "baseline_rmse": float(
            baseline_rmse
        ),
        "directional_accuracy": float(
            direction_accuracy
        ),
        "latest_brent": float(
            latest_features["brent"]
        ),
        "forecast_date": str(
            forecast_date.date()
        ),
        "next_week_prediction": (
            next_week_prediction
        ),
        "feature_importance": (
            feature_importance
        ),
    }

    with open(
        PROCESSED_DATA_DIR
        / "forecast_metrics.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            metrics,
            file,
            indent=4,
        )

    joblib.dump(
        model,
        MODELS_DIR
        / "brent_random_forest.joblib",
    )

    print(
        f"Model MAE: ${model_mae:.2f}"
    )

    print(
        f"Baseline MAE: "
        f"${baseline_mae:.2f}"
    )

    print(
        f"Directional accuracy: "
        f"{direction_accuracy:.1%}"
    )

    return metrics


if __name__ == "__main__":
    train_forecast_model()