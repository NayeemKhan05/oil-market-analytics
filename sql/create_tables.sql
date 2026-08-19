CREATE TABLE IF NOT EXISTS weekly_market (
    period TEXT PRIMARY KEY,
    brent REAL,
    wti REAL,
    brent_wti_spread REAL,
    production_kbd REAL,
    production_change_kbd REAL,
    stocks_kbbl REAL,
    stock_change_kbbl REAL,
    imports_kbd REAL,
    exports_kbd REAL,
    net_imports_kbd REAL,
    brent_return_1w REAL,
    brent_ma_4w REAL,
    brent_ma_12w REAL,
    brent_volatility_8w REAL
);

CREATE TABLE IF NOT EXISTS market_anomalies (
    period TEXT,
    metric TEXT,
    value REAL,
    z_score REAL,
    direction TEXT,
    severity TEXT
);

CREATE TABLE IF NOT EXISTS forecast_results (
    period TEXT PRIMARY KEY,
    actual_brent REAL,
    predicted_brent REAL,
    baseline_brent REAL
);

CREATE INDEX IF NOT EXISTS idx_anomalies_period
ON market_anomalies(period);

CREATE INDEX IF NOT EXISTS idx_anomalies_metric
ON market_anomalies(metric);