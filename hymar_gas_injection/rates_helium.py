#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 23 19:22:07 2026

@author: matthijsnuus
"""

import pandas as pd
import matplotlib.pyplot as plt

# --- path to your file ---
path = "/Users/matthijsnuus/Desktop/FS-C/model/hymar_gas_injection/injec_rates.csv"

# Read CSV
df = pd.read_csv(path)

# Remove the units row
df = df.drop(index=0).reset_index(drop=True)

# Convert TIME to numeric and drop invalid TIME rows
df["TIME"] = pd.to_numeric(df["TIME"], errors="coerce")
df = df.dropna(subset=["TIME"]).reset_index(drop=True)

# Create TimeElapsed in seconds
df["TimeElapsed"] = df["TIME"] * 86400
df.loc[0, "TimeElapsed"] = 0.0


# First column is time in days (whatever its header is)
time_days_col = df.columns[0]

# Create TimeElapsed in seconds:
# - first value = 0
# - others = days * 86400
df["TimeElapsed"] = df[time_days_col] * 86400
df.loc[df.index[0], "TimeElapsed"] = 0.0   # force first entry to 0

df["TimeElapsed"] = pd.to_numeric(df["TimeElapsed"], errors="coerce")
df["Moles of gas pumped into clay"] = pd.to_numeric(df["Moles of gas pumped into clay"], errors="coerce")
df = df.dropna(subset=["Moles of gas pumped into clay"]).reset_index(drop=True)


df1000 = df.iloc[::800].copy()
if df1000.index[-1] != df.index[-1]:
    df1000 = pd.concat([df1000, df.iloc[[-1]]])
df1000 = df1000.reset_index(drop=True)


# ---- Convert cumulative moles -> cumulative kg ----
M_HE = 0.0040026  # kg/mol (helium)

df1000["GasMass_kg"] = df1000["Moles of gas pumped into clay"] * M_HE

# ---- Convert cumulative kg -> rate [kg/s] ----
# rate = d(mass)/d(time)
df1000["GasRate_kg_s"] = df1000["GasMass_kg"].diff() / df1000["TimeElapsed"].diff()

# Optional: replace NaN in first row with 0
df1000["GasRate_kg_s"] = df1000["GasRate_kg_s"].fillna(0.0)
df1000 = df1000[df1000["GasRate_kg_s"] >= 0].reset_index(drop=True)


plt.figure(figsize=(8,5))
plt.plot(df1000["TimeElapsed"], df1000["GasRate_kg_s"], marker="o", linestyle="-")
plt.xlabel("TimeElapsed (s)")
plt.ylabel("Gas injection rate (kg/s)")
plt.title("Helium injection rate vs Time")
plt.grid(True)
plt.tight_layout()
plt.show()

# Keep only TimeElapsed and rate
df_out = df1000[["TimeElapsed", "GasRate_kg_s"]].copy()

# Save to CSV
out_path = "/Users/matthijsnuus/Desktop/FS-C/model/hymar_gas_injection/filtered_rates_kgs.csv"
df_out.to_csv(out_path, index=False)

print("Saved:", out_path)
