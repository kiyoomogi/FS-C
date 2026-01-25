#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 24 15:27:10 2026

@author: matthijsnuus
"""

# -*- coding: utf-8 -*-

import pandas as pd
import matplotlib.pyplot as plt

# ---- path to the single file ----
file_path = "/Users/matthijsnuus/Desktop/FS-C/model/hymar_gas_injection/tank_model/model_run/OUTPUT_CONNE.csv"

# Read the CSV (skip first row if it's an extra header line)
df = pd.read_csv(file_path, skiprows=1)

# Clean column names
df = df.rename(columns=lambda x: x.strip())

# Shift first column down by 1 and drop NaNs (same as original logic)
df.iloc[:, 0] = df.iloc[:, 0].shift(1)
df = df.dropna().reset_index(drop=True)

# Keep only: first column (time) and second-to-last column (rate)
df = df.iloc[:, [0, -2]].copy()

# Convert time column:
# if values look like "TIME  12345", take last token
df.iloc[:, 0] = df.iloc[:, 0].astype(str).str.split().str[-1]
df.iloc[:, 0] = pd.to_numeric(df.iloc[:, 0], errors="coerce")

# Convert rate column to numeric
df.iloc[:, 1] = pd.to_numeric(df.iloc[:, 1], errors="coerce")

# Drop any remaining bad rows
df = df.dropna().reset_index(drop=True)

# Rename columns
df = df.rename(columns={df.columns[0]: "TimeElapsed", df.columns[1]: "GAS_INJEC"})

# Flip sign (same as your previous script)
df["GAS_INJEC"] = df["GAS_INJEC"] * -1

# Sort by time
df = df.sort_values("TimeElapsed").reset_index(drop=True)

# ---- Plot ----
plt.figure(figsize=(8, 5))
plt.plot(df["TimeElapsed"], df["GAS_INJEC"], "-o")

plt.axvline(22593785)
#plt.yscale("log")
plt.xlabel("Time Elapsed [s]")
plt.ylabel("Gas Injection Rate")
plt.grid(True)
plt.title("Gas Injection Rate from OUTPUT_CONNE.csv")
plt.tight_layout()
plt.show()

out_path = "/Users/matthijsnuus/Desktop/FS-C/model/hymar_gas_injection/tank_model/model_run/filtered_gasrate_from_conne.csv"
df.to_csv(out_path, index=False)
print("Saved:", out_path)
