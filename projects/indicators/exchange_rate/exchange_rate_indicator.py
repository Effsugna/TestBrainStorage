import datetime
import numpy as np

# Sample placeholder data for last 5 days
exchange_rate_changes = [0.002, -0.001, 0.0005, 0.0012, -0.0007]  # ΔExchangeRate(t-5 to t-1)
terms_of_trade = [1.1, 1.12, 1.11, 1.13, 1.14]
interest_diff = [0.25, 0.3, 0.28, 0.27, 0.26]
gdp_domestic = [2.5, 2.52, 2.51, 2.53, 2.55]
gdp_foreign = [1.9, 1.88, 1.87, 1.89, 1.9]
expectations = [0.001, 0.0005, -0.0003, 0.0009, -0.0006]  # Previous day's rate assumed to persist

def predict_exchange_rate_change():
    weights = np.array([0.4, 0.2, 0.1, 0.15, 0.15])  # Example weighting for simplicity
    lags = 5

    inputs = np.array([
        exchange_rate_changes[-lags:],
        terms_of_trade[-lags:],
        interest_diff[-lags:],
        gdp_domestic[-lags:],
        gdp_foreign[-lags:],
        expectations[-lags:]
    ])

    avg_change = np.average(inputs, axis=1)
    prediction = np.dot(weights, avg_change[:len(weights)])  # Simplified projection

    return round(prediction, 6)

if __name__ == "__main__":
    change = predict_exchange_rate_change()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] Predicted exchange rate change: {change}")