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

# --- US GDP (placeholder untouched) ---
try:
    bea_url = "https://apps.bea.gov/national/xls/gdp_qtr.xlsx"
    xls = pd.ExcelFile(bea_url, engine="openpyxl")
    df_us = pd.read_excel(xls, sheet_name="Table 1.1.5", skiprows=7)
    df_us = df_us.rename(columns={df_us.columns[0]: "date_str"})
    df_us = df_us[df_us["date_str"].str.contains("Q")]
    df_us["date"] = pd.to_datetime(df_us["date_str"].str.replace("Q1", "-03-31")
                                                    .str.replace("Q2", "-06-30")
                                                    .str.replace("Q3", "-09-30")
                                                    .str.replace("Q4", "-12-31"))
    df_us["gdp_us"] = pd.to_numeric(df_us.iloc[:, 1], errors="coerce")
    df_us = df_us[["date", "gdp_us"]].dropna()
    df_us = df_us[df_us["date"].dt.year >= 1990]
    print(f"🇺🇸 US GDP rows: {len(df_us)}")
except Exception as e:
    print(f"US GDP fetch failed: {e}")
    df_us = pd.DataFrame()

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
