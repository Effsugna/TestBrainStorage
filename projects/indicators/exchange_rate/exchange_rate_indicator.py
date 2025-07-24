import yfinance as yf
import datetime
import numpy as np
import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

# --- CONFIG ---
symbol = 'AUDUSD=X'
prediction_window = 1
lag_days = 5
output_currency_pair = "AUD/USD"

# --- FETCH DATA ---
data = yf.download(symbol, period='15d', interval='1d', auto_adjust=True)

# --- EXTRACT CLOSE PRICES SAFELY ---
try:
    if isinstance(data, pd.DataFrame) and 'Close' in data.columns:
        close_prices_series = data['Close']
    else:
        raise ValueError("Expected 'Close' column missing from downloaded data.")
    close_prices = close_prices_series.dropna().astype(float).to_numpy().flatten()
except Exception as e:
    print(f"Data parsing error: {e}")
    exit()

if len(close_prices) < lag_days + 2:
    print("Not enough data to make prediction.")
    exit()

# --- CALCULATE DAILY CHANGES ---
print(f"close_prices: {close_prices}, len = {len(close_prices)}")
exchange_rate_changes = np.round(np.diff(close_prices), 6)[-lag_days:]

# --- TERMS OF TRADE (from CSV) ---
try:
    tot_df = pd.read_csv(
        "projects/indicators/exchange_rate/csvs/tot/tot.csv",
        parse_dates=["date"],
        date_format=lambda x: pd.to_datetime(x, format="%Y-%m-%d")
    )
    tot_df.sort_values("date", inplace=True)
    terms_of_trade = tot_df["tot_index"].to_numpy()[-lag_days:]
except Exception as e:
    print(f"ToT CSV fetch failed: {e}")
    terms_of_trade = np.full(lag_days, 1.1)

# --- LOAD INTEREST RATE DIFFERENTIAL ---
try:
    rates_df = pd.read_csv("projects/indicators/exchange_rate/csvs/interest_rate/rates.csv", parse_dates=["date"])
    rates_df.sort_values("date", inplace=True)
    rates_df["interest_diff"] = rates_df["rba_rate"] - rates_df["fed_rate"]
    interest_diff = rates_df["interest_diff"].to_numpy()[-lag_days:]
except Exception as e:
    print(f"Interest rate differential fetch failed: {e}")
    interest_diff = np.full(lag_days, -5.5)

# --- GDP DATA (Australia + US) from CSV ---
try:
    df_au = pd.read_csv("projects/indicators/exchange_rate/csvs/gdp/aus_real_gdp.csv", parse_dates=["date"])
    df_au.sort_values("date", inplace=True)
    gdp_domestic = df_au["value"].to_numpy()[-lag_days:]
except Exception as e:
    print(f"AU GDP load failed: {e}")
    gdp_domestic = np.full(lag_days, 2.5)

try:
    df_us = pd.read_csv("projects/indicators/exchange_rate/csvs/gdp/us_real_gdp.csv", parse_dates=["date"])
    df_us.sort_values("date", inplace=True)
    gdp_foreign = df_us["value"].to_numpy()[-lag_days:]
except Exception as e:
    print(f"US GDP load failed: {e}")
    gdp_foreign = np.full(lag_days, 1.9)

# --- EXPECTATIONS BASED ON RECENT PRICES ---
expectations = close_prices[-lag_days:]

# --- INPUT NORMALIZATION ---
def zscore(x):
    x = np.asarray(x, dtype=float)
    if np.std(x) == 0:
        return np.zeros_like(x)
    return (x - np.mean(x)) / np.std(x)

input_series = {
    "exchange_rate_changes": exchange_rate_changes,
    "terms_of_trade": terms_of_trade,
    "interest_diff": interest_diff,
    "gdp_domestic": gdp_domestic,
    "gdp_foreign": gdp_foreign
}

# --- DEBUG RAW INPUTS ---
for key, series in input_series.items():
    print(f"{key} (raw): {series}")

# --- NORMALIZE ---
normalized_inputs = {k: zscore(v) for k, v in input_series.items()}

# --- STACK VECTOR ---
feature_vector = np.concatenate(list(normalized_inputs.values()))
print(f"Feature vector (z-scored, stacked): {feature_vector}")

# --- WEIGHTS AND OUTPUT ---
weights = np.linspace(1.0, 0.6, len(feature_vector))
weights /= np.sum(weights)

prediction_change = np.dot(feature_vector, weights)
prediction_change = np.clip(prediction_change, -0.02, 0.02)
prediction_pct = round(prediction_change * 100, 4)
predicted_next_rate = round(close_prices[-1] * (1 + prediction_change), 6)

# --- LOG CONTENT ---
timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
filename_timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

log_contents = f"""
[{timestamp}] Predicted 1-day change in {output_currency_pair}: {prediction_pct:+.4f}%
Predicted next rate: {predicted_next_rate}

Inputs (raw):
- Close Prices (last {lag_days+1} days): {close_prices[-(lag_days+1):].tolist()}
- ∆ExchangeRate (t-5 to t-1): {exchange_rate_changes.tolist()}
- Terms of Trade: {terms_of_trade.tolist()}
- Interest Rate Differential: {interest_diff.tolist()}
- Domestic GDP (AU): {gdp_domestic.tolist()}
- Foreign GDP (US): {gdp_foreign.tolist()}

Model: Normalized Z-Score + Weighted Sum
Forecast horizon: 1 trading day
""".strip()

# --- PUSH TO LOGS FOLDER VIA GIT ---
filename = f"projects/indicators/exchange_rate/logs/signal-{filename_timestamp}.md"
os.system(f'./gitpush.sh {filename} \"{log_contents}\"')
