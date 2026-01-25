#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import glob
import pandas as pd
import matplotlib.pyplot as plt

folder = "/Users/matthijsnuus/Desktop/FS-C/model/hymar_gas_injection/2_TH"

# ✅ injection rate file
rate_file = "/Users/matthijsnuus/Desktop/FS-C/model/hymar_gas_injection/tank_model/model_run/filtered_gasrate_from_conne.csv"

# Find all FOFT*.csv files
files = sorted(glob.glob(os.path.join(folder, "FOFT*.csv")))
if not files:
    raise FileNotFoundError(f"No FOFT*.csv files found in: {folder}")

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

# =========================
# 1) Plot FOFT curves
# =========================
for f in files:
    df = pd.read_csv(f, skipinitialspace=True)
    df.columns = df.columns.str.strip().str.strip('"')

    df["TIME(S)"] = pd.to_numeric(df["TIME(S)"], errors="coerce")
    df["PRES"] = pd.to_numeric(df["PRES"], errors="coerce")
    df["SAT_G"] = pd.to_numeric(df["SAT_G"], errors="coerce")
    df = df.dropna(subset=["TIME(S)", "PRES", "SAT_G"])

    label = os.path.basename(f).replace(".csv", "")

    ax1.plot(df["TIME(S)"], df["PRES"] / 1e6, label=label)
    ax2.plot(df["TIME(S)"], df["SAT_G"], label=label)

# =========================
# 2) Plot injection rate (same plot as pressure)
# =========================
rates = pd.read_csv(rate_file)
rates.columns = rates.columns.str.strip()

rates["TimeElapsed"] = pd.to_numeric(rates["TimeElapsed"], errors="coerce")
rates["GAS_INJEC"] = pd.to_numeric(rates["GAS_INJEC"], errors="coerce")
rates = rates.dropna(subset=["TimeElapsed", "GAS_INJEC"]).reset_index(drop=True)

ax1b = ax1.twinx()
ax1b.plot(
    rates["TimeElapsed"],
    rates["GAS_INJEC"],
    linestyle="--",
    linewidth=2,
    label="Injection rate"
)
ax1b.set_ylabel("Injection rate (kg/s)")

# =========================
# Formatting
# =========================
ax1.set_ylabel("Pressure (MPa)")
ax1.set_title("TIME vs PRES (all FOFT files) + Injection rate")
ax1.grid(True)
ax1.ticklabel_format(axis='y', style='plain', useOffset=False)

ax2.set_xlabel("Time (s)")
ax2.set_ylabel("Gas Saturation SAT_G (-)")
ax2.set_title("TIME vs SAT_G (all FOFT files)")
ax2.grid(True)

# Legend combine ax1 + ax1b
lines1, labels1 = ax1.get_legend_handles_labels()
linesb, labelsb = ax1b.get_legend_handles_labels()
ax1.legend(lines1 + linesb, labels1 + labelsb, fontsize=8, ncol=2)

ax2.legend(fontsize=8, ncol=2)

tmin = 1.5e7
tmax = 2e7   # example

ax1.set_xlim(tmin, tmax)   # sharex=True so this applies to both subplots

plt.tight_layout()
plt.show()
