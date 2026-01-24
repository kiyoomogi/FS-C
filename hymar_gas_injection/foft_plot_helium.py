#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 23 20:20:32 2026

@author: matthijsnuus
"""

import os
import glob
import pandas as pd
import matplotlib.pyplot as plt

folder = "/Users/matthijsnuus/Desktop/FS-C/model/hymar_gas_injection/2_TH"

# Find all FOFT*.csv files
files = sorted(glob.glob(os.path.join(folder, "FOFT*.csv")))

if not files:
    raise FileNotFoundError(f"No FOFT*.csv files found in: {folder}")

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

for f in files:
    # Read CSV (skipinitialspace handles the spaces after commas)
    df = pd.read_csv(f, skipinitialspace=True)

    # Clean column names (strip spaces + quotes)
    df.columns = df.columns.str.strip().str.strip('"')

    # Make sure numeric
    df["TIME(S)"] = pd.to_numeric(df["TIME(S)"], errors="coerce")
    df["PRES"] = pd.to_numeric(df["PRES"], errors="coerce")
    df["SAT_G"] = pd.to_numeric(df["SAT_G"], errors="coerce")

    # Drop any bad rows
    df = df.dropna(subset=["TIME(S)", "PRES", "SAT_G"])

    label = os.path.basename(f).replace(".csv", "")

    # Plot TIME vs PRES
    ax1.plot(df["TIME(S)"], df["PRES"] / 1e6, label=label)

    # Plot TIME vs SAT_G
    ax2.plot(df["TIME(S)"], df["SAT_G"], label=label)

# Formatting
ax1.set_ylabel("Pressure (MPa)")
ax1.set_title("TIME vs PRES (all FOFT files)")
ax1.grid(True)
ax1.ticklabel_format(axis='y', style='plain', useOffset=False)

ax2.set_xlabel("Time (s)")
ax2.set_ylabel("Gas Saturation SAT_G (-)")
ax2.set_title("TIME vs SAT_G (all FOFT files)")
ax2.grid(True)

# Optional: legends (can get big if many files)
ax1.legend(fontsize=8, ncol=2)
ax2.legend(fontsize=8, ncol=2)

plt.tight_layout()
plt.show()
