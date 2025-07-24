import os
import pandas as pd
from rpy2.robjects import r
from rpy2.robjects.packages import importr
from rpy2.robjects.conversion import localconverter
from rpy2.robjects import pandas2ri

# Load RBA library
readrba = importr("readrba")

# Load and subset ToT data
r('library(readrba)')
r('df <- read_rba(table_no = "H1")')
r('tot_df <- subset(df, series_id == "GOPITT")')
r('tot_df$date <- as.POSIXct(tot_df$date)')  # Enforce POSIX datetime

# Convert from R to pandas
with localconverter(pandas2ri.converter):
    df = r['tot_df']

# Clean & rename
df_cleaned = df[['date', 'value']].copy()
df_cleaned = df_cleaned.rename(columns={'value': 'tot_index'})

print("🧼 Cleaned DataFrame before sort/save:")
print(df_cleaned.head(10))
print(df_cleaned.dtypes)

# Remove timezone if present
df_cleaned["date"] = pd.to_datetime(df_cleaned["date"]).dt.tz_localize(None)

# Load existing CSV (if exists)
csv_path = 'projects/indicators/exchange_rate/csvs/tot/tot.csv'
os.makedirs(os.path.dirname(csv_path), exist_ok=True)

if os.path.exists(csv_path):
    df_old = pd.read_csv(csv_path, parse_dates=['date'])
    df_old["date"] = pd.to_datetime(df_old["date"]).dt.tz_localize(None)
    df_final = pd.concat([df_old, df_cleaned])
    df_final = df_final.drop_duplicates(subset='date').sort_values('date')
else:
    df_final = df_cleaned

# ✅ Format `date` column for export
df_final["date"] = df_final["date"].dt.strftime('%Y-%m-%d')

# Export to CSV
df_final.to_csv(csv_path, index=False)
print(f"\n✅ Terms of Trade data updated at: {csv_path}")
