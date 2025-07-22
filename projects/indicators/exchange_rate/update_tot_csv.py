import os
import pandas as pd
from rpy2.robjects import r
from rpy2.robjects.packages import importr

# Load R package
readrba = importr("readrba")

# Load RBA table I1
r('df <- read_rba(table_no = "I1")')

# Filter in R for ToT series
r('tot_df <- subset(df, series == "Trade balance as a per cent of output")')

# Extract filtered dataframe
tot_df = r['tot_df']

# Build pandas DataFrame
df = pd.DataFrame({
    "date": list(tot_df.rx2("date")),
    "tot_index": list(tot_df.rx2("value"))
})

# Sort by date
df.sort_values("date", inplace=True)

# Create directory if needed
output_dir = "projects/indicators/exchange_rate/csvs/tot"
os.makedirs(output_dir, exist_ok=True)

# Save to CSV
output_path = os.path.join(output_dir, "tot.csv")
df.to_csv(output_path, index=False)

print("✅ ToT data saved successfully at:", output_path)
