#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 24 08:41:29 2025

@author: matthijsnuus
"""

import matplotlib.pyplot as plt 
import pandas as pd
import numpy as np

bfsb1 = pd.read_csv('/Users/matthijsnuus/Downloads/MtTerriInjectionMay2023_BFSB1_PT_1Hz.csv', sep=',').dropna()


# Parse your measured series timestamps properly (UTC)
rates_csv = pd.read_csv(
    "/Users/matthijsnuus/Desktop/FS-C/model/injection_rates/filtered_FSC_injecrates.csv",
    delimiter=",", index_col=0
)
date_series = pd.to_datetime(rates_csv["UTC"].str.slice(0, 19), utc=True, errors="coerce")

# Time window
t_start = date_series.iloc[0]
t_end   = date_series.iloc[-1]

# Load bfsb1 and parse its time column (assume it has a 'UTC' or similar)
bfsb1 = pd.read_csv(
    "/Users/matthijsnuus/Downloads/MtTerriInjectionMay2023_BFSB1_PT_1Hz.csv",
    sep=","
).dropna(how="all")

# Try common timestamp column names; adjust if needed
time_col_candidates = [c for c in bfsb1.columns if c.lower() in {"utc","time","datetime","timestamp"}]
if not time_col_candidates:
    # fallback: assume first column is time
    time_col = bfsb1.columns[0]
else:
    time_col = time_col_candidates[0]

bfsb1["t_utc"] = pd.to_datetime(bfsb1[time_col].astype(str).str.slice(0, 26), utc=True, errors="coerce")

# Keep rows with valid time and within [t_start, t_end]
m = bfsb1["t_utc"].notna() & (bfsb1["t_utc"] >= t_start) & (bfsb1["t_utc"] <= t_end)
bfsb1_trim = bfsb1.loc[m].sort_values("t_utc").reset_index(drop=True)
df = bfsb1_trim.copy()

# group by minute bucket and pick the row closest to the minute mark
g = df.groupby(df["t_utc"].dt.floor("min"), group_keys=False)
bfsb1_1min = g.apply(lambda d: d.iloc[(d["t_utc"] - d["t_utc"].dt.floor("min")).abs().argmin()])

# make the minute timestamps the index (optional)
bfsb1_1min = bfsb1_1min.set_index("t_utc").sort_index()

bfsb1_5min = (
    bfsb1_trim
    .set_index("t_utc")
    .resample("5min")
    .mean(numeric_only=True)       # or .median(), .max(), etc.
    .dropna(how="all")
)

print(f"Trimmed bfsb1 to {len(bfsb1_trim)} rows between {t_start} and {t_end}")


#utc = pd.to_datetime(bfsb1_5min['UTC'])
utc = bfsb1_5min.index
pres29 =  bfsb1_5min.iloc[:,0]
pres31 =  bfsb1_5min.iloc[:,1]
pres35 =  bfsb1_5min.iloc[:,2]
pres42 =  bfsb1_5min.iloc[:,3]


fig, ax = plt.subplots(figsize=(9,5))
ax.plot(utc, pres42, label="42.2 m")
ax.plot(utc, pres35, label="34.9 m")
ax.plot(utc, pres31, label="31.0 m")
ax.plot(utc, pres29, label="29.0 m")
plt.legend()
ax.set_ylabel('Pressure [bar]')
plt.show()

bfsb1_5min.to_csv("/Users/matthijsnuus/Desktop/FS-C/model/previous_fofts/BFSB1_meas.csv")

print(pres42[10])