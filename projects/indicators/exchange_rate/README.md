Exchange Rate Indicator Architecture

This module is designed as a prototype structural indicator for predicting short-term changes in the AUD/USD exchange rate using a weighted regression model across five economic factors.

## 🎯 Objective

To create a **daily-predictive indicator** for AUD/USD that:
- Draws data from live and official sources (Yahoo Finance, RBA, BEA)
- Processes and aligns it through standardized CSV interfaces
- Outputs structured markdown logs with the predicted rate and breakdown of inputs

---

## 🔁 Pipeline Architecture

### 1. **Raw Data Collection**

#### 📉 Exchange Rate History
- **Source**: \`yfinance\`
- **Variable**: \`close_prices\`
- **Use**: Primary series for calculating delta changes and expectations

#### 💼 Terms of Trade (ToT)
- **Source**: CSV from \`update_tot_csv.py\`
- **Path**: \`csvs/tot/tot.csv\`
- **Behavior**: Indexed quarterly series from RBA, parsed to match latest 5 lags

#### 🏦 Interest Rate Differential
- **Source**: \`csvs/interest_rate/rates.csv\`
- **Computation**: \`rba_rate - fed_rate\`
- **Use**: Captures monetary policy divergence as a pressure indicator

#### 📊 GDP (Australia + US)
- **Current**: Wikipedia HTML table fallback (temporary)
- **Goal**: Use \`update_gdp_csv.py\` with:
  - Real GDP: \`GGDPCVGDP\`
  - Nominal GDP: \`GGDPECCPGDP\`
- **Output CSVs**:
  - \`csvs/gdp/aus_real_gdp.csv\`
  - \`csvs/gdp/aus_nominal_gdp.csv\`

---

### 2. **Series Write + Maintenance**

Each \`update_*.py\` script:
- Pulls from upstream official source (R, pandas, or requests)
- Sorts by \`date\`
- Appends only new rows
- Skips if fully up to date
- Fails safely on broken remote sources

Each CSV is structured with:
\`\`\`csv
date,value
2024-03-01,XXX
2024-06-01,YYY
\`\`\`

---

### 3. **Indicator Logic (\`exchange_rate_indicator.py\`)**

#### 👇 Inputs:
- \`exchange_rate_changes\`: Δ from past 5 days of \`Close\` prices
- \`terms_of_trade\`: Final 5 entries from \`tot.csv\`
- \`interest_diff\`: 5-day interest rate spread (RBA - Fed)
- \`gdp_domestic\`: AU GDP (5x, same value for now)
- \`gdp_foreign\`: US GDP (5x, same value for now)
- \`expectations\`: Last 5 \`Close\` prices

#### 🧮 Model:
- Lag-weighted average via hard-coded weights:
  \`\`\`python
  weights = np.array([0.4, 0.2, 0.1, 0.15, 0.15])
  prediction = dot(weights, mean(inputs))
  \`\`\`

#### 🪵 Logging:
- Markdown snapshot written to \`logs/signal-YYYY-MM-DD_HH-MM-SS.md\`
- Auto committed and pushed via \`gitpush.sh\`

---

## ⚠️ Still to Complete

1. **GDP Integration**
   - Replace Wikipedia GDP scrapes with CSV imports from \`update_gdp_csv.py\`
   - Merge Real + Nominal GDPs if needed

2. **US GDP**
   - Finalize \`bea.gov\` BEA integration
   - Output to \`csvs/gdp/us_nominal_gdp.csv\`

3. **Weights + Model Flexibility**
   - Parametrize weighting system
   - Add CLI options for backtesting vs live run

4. **Validation**
   - Create a diagnostics report script per signal
   - Export per-day forecast vs actual performance

5. **Dashboard Integration**
   - Live feed into HTML dashboard or streamlit app

---

## ✅ Confirmed Working

- [x] RBA GDP live pull via \`rpy2\` and \`readrba\`
- [x] ToT pipeline tested and appended
- [x] Git logging with robust fallback
- [x] Full run from terminal confirmed safe, clean, idempotent
