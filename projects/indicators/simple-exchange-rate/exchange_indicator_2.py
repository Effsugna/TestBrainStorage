import requests
import datetime
import os
import re
import subprocess

# === Config ===
url = "https://open.er-api.com/v6/latest/USD"
log_dir = "projects/indicators/simple-exchange-rate/logs"
now = datetime.datetime.now().strftime("%Y-%m-%d-%H%M")
human_time = datetime.datetime.now().strftime("%Y-%m-%d – %H:%M")
log_filename = f"log-{now}.md"
log_path = f"{log_dir}/{log_filename}"

# === Step 1: Fetch Latest USD/AUD Rate ===
response = requests.get(url)
data = response.json()
usd_aud = round(data['rates']['AUD'], 4)

# === Step 2: Read Most Recent Log File (if any) ===
previous_rate = None
log_files = sorted([f for f in os.listdir(log_dir) if f.startswith("log-") and f.endswith(".md")])
if log_files:
    last_log = log_files[-1]
    with open(f"{log_dir}/{last_log}", "r") as f:
        for line in f:
            match = re.search(r"USD/AUD = ([\d.]+)", line)
            if match:
                previous_rate = float(match.group(1))
                break

# === Step 3: Signal Decision + Commentary ===
if usd_aud > 1.50:
    signal = "📈 USD strong – Buy AUD assets"
elif usd_aud < 1.45:
    signal = "📉 USD weak – Risk-off"
else:
    signal = "😐 Neutral range"

# === Step 4: Rate Delta Description ===
if previous_rate:
    delta = round(usd_aud - previous_rate, 4)
    change_desc = f"(Δ {delta:+.4f} from {previous_rate})"
else:
    change_desc = "(No prior rate to compare)"

# === Step 5: Log Content ===
log_content = f"# Log – {human_time}\n\nUSD/AUD = {usd_aud} {change_desc}\n\n{signal}\n"

# === Step 6: Write to Local File ===
with open(log_path, "w") as f:
    f.write(log_content)

# === Step 7: Auto-push to GitHub ===
subprocess.run([
    "./gitpush.sh",
    log_path,
    f"@{log_path}"
])

