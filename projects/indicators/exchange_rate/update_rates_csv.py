import pandas as pd
from datetime import datetime

# --- FILE DESTINATION ---
csv_path = "projects/indicators/exchange_rate/csvs/interest_rate/rates.csv"
rba_url = "https://www.rba.gov.au/statistics/tables/xls/f01hist.xlsx"
fed_url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DFF"

# --- READ SHEET NAMES ---
xls = pd.ExcelFile(rba_url, engine="openpyxl")
sheet = xls.sheet_names[0]

# --- READ RBA CASH RATE ---
rba_df = pd.read_excel(xls, sheet_name=sheet, skiprows=10)
rba_df = rba_df[rba_df.iloc[:, 0].apply(lambda x: isinstance(x, (pd.Timestamp, datetime)))]
rba_df = rba_df[[rba_df.columns[0], rba_df.columns[1]]].copy()
rba_df.columns = ["date", "rba_rate"]
rba_df["date"] = rba_df["date"].dt.to_period("M").dt.to_timestamp()

# --- FED RATE (FRED daily rate, averaged monthly) ---
fed_df = pd.read_csv(fed_url)
fed_df.columns = ["date", "fed_rate"]
fed_df["date"] = pd.to_datetime(fed_df["date"])
fed_df = fed_df.dropna()
fed_df = fed_df.set_index("date").resample("MS").mean().reset_index()
fed_df["date"] = fed_df["date"].dt.to_period("M").dt.to_timestamp()

# --- DIAGNOSTICS ---
print(f"🔎 RBA rows: {len(rba_df)}, FED rows: {len(fed_df)}")
print(f"📅 RBA dates: {rba_df['date'].min()} to {rba_df['date'].max()}")
print(f"📅 FED dates: {fed_df['date'].min()} to {fed_df['date'].max()}")

# --- MERGE AND SAVE ---
merged = pd.merge(rba_df, fed_df, on="date", how="inner")

# Convert rate columns to proper numeric format (optional: round if needed)
merged["rba_rate"] = pd.to_numeric(merged["rba_rate"])
merged["fed_rate"] = pd.to_numeric(merged["fed_rate"])

# Format the date cleanly
merged["date"] = merged["date"].dt.strftime("%Y-%m-%d")

# Write to CSV
merged.to_csv(csv_path, index=False)


print(f"✅ Wrote {len(merged)} real rows to {csv_path}")
