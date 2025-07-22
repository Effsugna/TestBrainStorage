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
    tot_df = pd.read_csv("projects/indicators/exchange_rate/csvs/tot/tot.csv", parse_dates=["date"])
    tot_df.sort_values("date", inplace=True)
    terms_of_trade = tot_df["tot_index"].to_numpy()[-lag_days:]
except Exception as e:
    print(f"ToT CSV fetch failed: {e}")
    terms_of_trade = np.full(lag_days, 1.1)

# --- LOAD INTEREST RATE DIFFERENTIAL ---
try:
    rates_df = pd.read_csv("projects/indicators/exchange_rate/csvs/interest_rate/rates.csv", parse_dates=["date"])
    rates_df.sort_values("date", inplace=True)
    # Compute RBA – FED difference
    rates_df["interest_diff"] = rates_df["rba_rate"] - rates_df["fed_rate"]
    interest_diff = rates_df["interest_diff"].to_numpy()[-lag_days:]
except Exception as e:
    print(f"Interest rate differential fetch failed: {e}")
    interest_diff = np.full(lag_days, -5.5)  # fallback placeholder

# --- GDP DATA (Australia + US) from Wikipedia or fallback ---
try:
    gdp_tables = pd.read_html("https://en.wikipedia.org/wiki/Economy_of_Australia", flavor="bs4")
    df_gdp = gdp_tables[0] if len(gdp_tables) else pd.DataFrame()
    gdp_au = float(df_gdp[df_gdp.columns[1]].dropna().values[0])
    gdp_domestic = np.full(lag_days, gdp_au)
except Exception as e:
    print(f"AU GDP fetch failed: {e}")
    gdp_domestic = np.full(lag_days, 2.5)

try:
    gdp_tables_us = pd.read_html("https://en.wikipedia.org/wiki/Economy_of_the_United_States", flavor="bs4")
    df_gdp_us = gdp_tables_us[0] if len(gdp_tables_us) else pd.DataFrame()
    gdp_us = float(df_gdp_us[df_gdp_us.columns[1]].dropna().values[0])
    gdp_foreign = np.full(lag_days, gdp_us)
except Exception as e:
    print(f"US GDP fetch failed: {e}")
    gdp_foreign = np.full(lag_days, 1.9)

# --- EXPECTATIONS BASED ON RECENT PRICES ---
expectations = close_prices[-lag_days:]

# --- PREDICTION LOGIC ---
weights = np.array([0.4, 0.2, 0.1, 0.15, 0.15])
expected_len = lag_days

input_series = {
    "exchange_rate_changes": exchange_rate_changes,
    "terms_of_trade": terms_of_trade,
    "interest_diff": interest_diff,
    "gdp_domestic": gdp_domestic,
    "gdp_foreign": gdp_foreign,
    "expectations": expectations
}

for key, series in input_series.items():
    if len(series) != expected_len:
        print(f"Input '{key}' has invalid length: {len(series)} (expected {expected_len})")
        exit()

# --- DEBUGGING STACK ISSUE ---
for key, series in input_series.items():
    arr = np.ravel(series).astype(float)
    print(f"{key}: shape = {arr.shape}, type = {type(arr)}, first few = {arr[:3]}")

inputs = np.stack([np.ravel(series).astype(float) for series in input_series.values()])

avg_change = np.mean(inputs, axis=1)
prediction = np.dot(weights, avg_change[:len(weights)])
prediction_pct = round(prediction / close_prices[-1] * 100, 4)
predicted_next_rate = round(close_prices[-1] + prediction, 6)

# --- LOG CONTENT ---
timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
filename_timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

log_contents = f"""
[{timestamp}] Predicted 1-day change in {output_currency_pair}: {prediction_pct:+.4f}%
Predicted next rate: {predicted_next_rate}

Inputs:
- Close Prices (last {lag_days+1} days): {close_prices[-(lag_days+1):].tolist()}
- ΔExchangeRate (t-5 to t-1): {exchange_rate_changes.tolist()}
- Terms of Trade: {terms_of_trade.tolist()}
- Interest Rate Differential: {interest_diff.tolist()}
- Domestic GDP (AU): {gdp_domestic.tolist()}
- Foreign GDP (US): {gdp_foreign.tolist()}
- Naive Expectations (from price): {expectations.tolist()}

Model: Lag-weighted structural regression
Forecast horizon: 1 trading day
""".strip()

# --- PUSH TO LOGS FOLDER VIA GIT ---
filename = f"projects/indicators/exchange_rate/logs/signal-{filename_timestamp}.md"
os.system(f'./gitpush.sh {filename} \"{log_contents}\"')
