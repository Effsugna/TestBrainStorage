import yfinance as yf
import datetime
import subprocess
import os

# === Config ===
ticker = "GME"
price = yf.Ticker(ticker).history(period="1d")["Close"].iloc[-1]
now = datetime.datetime.now().strftime("%Y-%m-%d-%H%M")
human_time = datetime.datetime.now().strftime("%Y-%m-%d – %H:%M")
log_path = f"projects/indicators/stock-price-simple/logs/log-{ticker}-{now}.md"

# === Generate Signal ===
if price > 25:
    signal = f"📈 Buy Signal – {ticker} price is strong"
elif price < 15:
    signal = f"📉 Sell Signal – {ticker} price is weak"
else:
    signal = f"😐 Hold – {ticker} within neutral range"

# === Create Log Content ===
log_content = f"# Log – {human_time}\n\n{ticker} Closing Price = ${price:.2f}\n\n{signal}\n"

# === Write Log File ===
os.makedirs(os.path.dirname(log_path), exist_ok=True)
with open(log_path, "w") as f:
    f.write(log_content)

# === Auto-push using gitpush.sh ===
subprocess.run(["./gitpush.sh", log_path, f"@{log_path}"])

