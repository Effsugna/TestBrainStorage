import pandas as pd

abs_url = "https://www.rba.gov.au/statistics/tables/xls/g01hist.xlsx"
xls = pd.ExcelFile(abs_url, engine="openpyxl")
df = pd.read_excel(xls, sheet_name=xls.sheet_names[0], skiprows=10)

# Show the first column to examine possible GDP labels
print(df.iloc[:, 0].dropna().head(30).to_list())

