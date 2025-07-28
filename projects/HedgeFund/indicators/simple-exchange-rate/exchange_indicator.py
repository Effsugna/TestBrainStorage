import requests
import datetime

# === Config ===
url = "https://open.er-api.com/v6/latest/USD"
log_dir = "projects/indicators/simple-exchange-rate/logs"
now = datetime.datetime.now().strftime("%Y-%m-%d-%H%M")
human_time = datetime.datetime.now().strftime("%Y-%m-%d – %H:%M")
log_path = f"{log_dir}/log-{now}.md"

# === Fetch Exchange Rate ===
response = requests.get(url)
data = response.json()
usd_aud = data['rates']['AUD']

# === Determine Signal ===
if usd_aud > 1.50:
    signal = "📈 Signal: USD strong — Buy AUD assets"
elif usd_aud < 1.45:
    signal = "📉 Signal: USD falling — Risk-off"
else:
    signal = "😐 Neutral range"

# === Write Log ===
log_content = f"# Log – {human_time}\n\nUSD/AUD = {usd_aud}\n\n{signal}\n"
with open(log_path, "w") as f:
    f.write(log_content)

# === Auto-push with gitpush.sh ===
import subprocess
subprocess.run([
    "./gitpush.sh",
    log_path,
    f"@{log_path}"
])

