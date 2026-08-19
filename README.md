# Oil Market Analytics & Forecasting Dashboard

A quantitative oil-market analytics platform built with Python, SQL, Streamlit and machine learning.

The project integrates historical energy-market data from the U.S. Energy Information Administration (EIA) to analyse crude oil prices, supply fundamentals, inventories and trade flows.

## Dashboard Demo
![Oil Market Analytics Dashboard](assets/dashboard-demo.gif)

## Features

- Brent and WTI crude oil price analysis
- Brent-WTI spread monitoring
- U.S. crude oil production analysis
- Commercial crude inventory builds and draws
- Crude import, export and net-import analysis
- Rolling market volatility indicators
- Statistical anomaly detection using rolling z-scores
- One-week Brent price forecasting
- Chronological model backtesting
- Naive forecast baseline comparison
- Interactive Streamlit and Plotly dashboard

## Data

Market data is sourced from the U.S. Energy Information Administration Open Data API.

The project uses:

- Brent spot prices
- WTI spot prices
- U.S. crude oil production
- U.S. commercial crude inventories excluding the Strategic Petroleum Reserve
- U.S. crude imports
- U.S. crude exports

## Architecture

```text
EIA Open Data API
        |
        v
Python ingestion pipeline
        |
        v
SQLite database
        |
        v
Feature engineering
        |
        +-------------------+
        |                   |
        v                   v
Anomaly detection     Forecast model
        |                   |
        +---------+---------+
                  |
                  v
          Streamlit dashboard
```

## Analytics

The pipeline derives a number of market indicators from the raw EIA data, including:

- Brent-WTI price spread
- Weekly inventory changes
- Weekly crude production changes
- Net crude imports
- Weekly Brent returns
- 4-week and 12-week price averages
- Rolling annualised price volatility

Market anomalies are identified when selected indicators move at least two rolling standard deviations from their 52-week mean.

## Forecasting

A Random Forest regression model is used to estimate the following week's Brent crude price.

The model uses current market information including:

- Brent and WTI prices
- Brent-WTI spread
- production
- inventories
- inventory changes
- imports
- exports
- net imports
- price momentum
- rolling averages
- volatility

The dataset is split chronologically to prevent future observations from leaking into the training period.

Model performance is evaluated using:

- Mean Absolute Error (MAE)
- Root Mean Squared Error (RMSE)
- Directional accuracy

Performance is also compared against a naive baseline which assumes that next week's Brent price will equal the current week's price.

## Tech Stack

- Python
- pandas
- NumPy
- SQL / SQLite
- scikit-learn
- Streamlit
- Plotly
- EIA Open Data API

## Running Locally

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/oil-market-analytics.git
cd oil-market-analytics
```

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```env
EIA_API_KEY=your_api_key
START_DATE=2016-01-01
```

Run the analytics pipeline:

```bash
python main.py
```

Launch the dashboard:

```bash
streamlit run dashboard/app.py
```
