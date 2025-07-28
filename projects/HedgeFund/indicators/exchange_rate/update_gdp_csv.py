import pandas as pd
import numpy as np
from datetime import datetime
from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri, default_converter
from rpy2.robjects.conversion import localconverter
import rpy2.robjects as ro

# --- R SETUP ---
readrba = importr("readrba")

# --- FILE PATHS ---
real_csv = "projects/indicators/exchange_rate/csvs/gdp/aus_real_gdp.csv"
nom_csv = "projects/indicators/exchange_rate/csvs/gdp/aus_nominal_gdp.csv"
merged_csv = "projects/indicators/exchange_rate/csvs/gdp/gdp.csv"

# --- Series IDs ---
REAL_SERIES = "GGDPCVGDP"
NOM_SERIES = "GGDPECCPGDP"

# --- Load Existing CSVs ---
real_au = pd.read_csv(real_csv, parse_dates=["date"])
nom_au = pd.read_csv(nom_csv, parse_dates=["date"])

# --- Pull Latest RBA Data ---
def update_gdp_series(series_id, existing_df, label, path):
    r_df = ro.r(f'readrba::read_rba_seriesid("{series_id}")')
    with localconverter(default_converter + pandas2ri.converter):
        new_df = pandas2ri.rpy2py(r_df)

    new_df = new_df[["date", "value"]]
    new_df["date"] = pd.to_datetime(new_df["date"])  # ✅ Ensure proper datetime format

    new_df = new_df[new_df["date"] >= datetime(2000, 1, 1)]

    merged = pd.merge(existing_df, new_df, on="date", how="outer", suffixes=("", "_new"))
    merged["value"] = merged["value"].combine_first(merged["value_new"])
    merged = merged[["date", "value"]].sort_values("date")

    if merged.equals(existing_df.sort_values("date").reset_index(drop=True)):
        print(f"✅ {label} GDP is already up to date")
    else:
        merged.to_csv(path, index=False)
        print(f"⬆️  Updated {label} GDP CSV with {len(merged) - len(existing_df)} new row(s)")


# --- Update AU Real and Nominal GDP ---
update_gdp_series(REAL_SERIES, real_au, "Real AUS", real_csv)
update_gdp_series(NOM_SERIES, nom_au, "Nominal AUS", nom_csv)

# --- US GDP via quantmod (from R, no API key) ---
us_nom_csv = "projects/indicators/exchange_rate/csvs/gdp/us_nominal_gdp.csv"
us_real_csv = "projects/indicators/exchange_rate/csvs/gdp/us_real_gdp.csv"

def update_us_gdp(series_id, path, label):
    try:
        # Load existing
        try:
            existing_df = pd.read_csv(path, parse_dates=["date"])
        except FileNotFoundError:
            existing_df = pd.DataFrame(columns=["date", "value"])

        # Pull via quantmod
        ro.r("suppressMessages(library(quantmod))")
        ro.r(f"getSymbols('{series_id}', src = 'FRED')")

        # Evaluate and convert R object to pandas
        r_ts = ro.r(f"as.data.frame({series_id})")
        with localconverter(default_converter + pandas2ri.converter):
            r_df = pandas2ri.rpy2py(r_ts)

        # Ensure column names and formatting
        # r_df comes from as.data.frame(GDP) which has rownames = date, and 1 unnamed column
        if r_df.shape[1] == 1:
            r_df.columns = ["value"]
            r_df["date"] = pd.to_datetime(r_df.index)
            r_df = r_df[["date", "value"]]
        else:
            raise ValueError(f"Unexpected structure in R GDP dataframe: {r_df.columns}")

        r_df["date"] = pd.to_datetime(r_df["date"])

        r_df = r_df[r_df["date"] >= datetime(1990, 1, 1)]

        # Merge and deduplicate
        merged = pd.merge(existing_df, r_df, on="date", how="outer", suffixes=("", "_new"))
        merged["value"] = merged["value"].combine_first(merged["value_new"])
        merged = merged[["date", "value"]].sort_values("date")

        if merged.equals(existing_df.sort_values("date").reset_index(drop=True)):
            print(f"✅ {label} GDP is already up to date")
        else:
            merged.to_csv(path, index=False)
            print(f"⬆️  Updated {label} GDP CSV with {len(merged) - len(existing_df)} new row(s)")

    except Exception as e:
        print(f"❌ Failed to update {label} GDP: {e}")

# --- Update US Real and Nominal GDP ---
update_us_gdp("GDP", us_nom_csv, "Nominal US")
update_us_gdp("GDPC1", us_real_csv, "Real US")


# --- Merge AU + US GDP if needed (leave for now) ---
try:
    # You can re-enable this when ready to produce a merged dataset
    # aus_gdp = pd.merge(real_au, nom_au, on="date", how="inner")
    # df_au = pd.merge(aus_gdp, df_us, on="date", how="inner")
    # df_au["date"] = df_au["date"].dt.strftime("%Y-%m-%d")
    # df_au.to_csv(merged_csv, index=False)
    pass
except Exception as e:
    print(f"❌ Merge/write failed: {e}")
