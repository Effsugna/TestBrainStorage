import yfinance as yf
import datetime
import subprocess
import os

# === Config ===
ticker = "AAPL"
price = yf.Ticker(ticker).history(period="1d")["Close"].iloc[-1]
now = datetime.datetime.now().strftime("%Y-%m-%d-%H%M")
human_time = datetime.datetime.now().strftime("%Y-%m-%d – %H:%M")
log_path = f"projects/indicators/stock-price-simple/logs/log-{now}.md"

# === Generate Signal ===
if price > 200:
    signal = "📈 Buy Signal – AAPL price is high"
elif price < 170:
    signal = "📉 Sell Signal – AAPL price is low"
else:
    signal = "😐 Hold – AAPL within neutral range"

# === Create Log Content ===
log_content = f"# Log – {human_time}\n\nAAPL Closing Price = ${price:.2f}\n\n{signal}\n"

# === Write Log File ===
os.makedirs(os.path.dirname(log_path), exist_ok=True)
with open(log_path, "w") as f:
    f.write(log_content)

# === Auto-push using gitpush.sh ===
subprocess.run(["./gitpush.sh", log_path, f"@{log_path}"])

