#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import glob
import pandas as pd
import matplotlib.pyplot as plt

folder = "/Users/matthijsnuus/Desktop/FS-C/model/hymar_gas_injection/2_TH"

rate_file = "/Users/matthijsnuus/Desktop/FS-C/model/hymar_gas_injection/tank_model/model_run/filtered_gasrate_from_conne.csv"
pressure_file = "/Users/matthijsnuus/Desktop/FS-C/model/hymar_gas_injection/tank_model/filtered_water_pressure_rate.csv"

SEC_PER_DAY = 86400.0

files = sorted(glob.glob(os.path.join(folder, "FOFT*.csv")))
if not files:
    raise FileNotFoundError(f"No FOFT*.csv files found in: {folder}")

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

# Track global FOFT time range
tmin_s = None
tmax_s = None

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

    if df.empty:
        continue

    # Update global time range
    this_min = df["TIME(S)"].min()
    this_max = df["TIME(S)"].max()
    tmin_s = this_min if tmin_s is None else min(tmin_s, this_min)
    tmax_s = this_max if tmax_s is None else max(tmax_s, this_max)

    label = os.path.basename(f).replace(".csv", "")

    ax1.plot(df["TIME(S)"] / SEC_PER_DAY, df["PRES"] / 1e6, label=label)
    ax2.plot(df["TIME(S)"] / SEC_PER_DAY, df["SAT_G"], label=label)

# =========================
# 2) Plot tank pressure (from filtered_water_pressure_rate.csv)
# =========================
tank = pd.read_csv(pressure_file)
tank.columns = tank.columns.str.strip()

# expected columns: "TimeElapsed" (seconds) and "Gas Pressure (MPa)"
tank["TimeElapsed"] = pd.to_numeric(tank["TimeElapsed"], errors="coerce")
tank["Gas Pressure (MPa)"] = pd.to_numeric(tank["Gas Pressure (MPa)"], errors="coerce")
tank = tank.dropna(subset=["TimeElapsed", "Gas Pressure (MPa)"]).reset_index(drop=True)

ax1.plot(
    tank["TimeElapsed"] / SEC_PER_DAY,
    tank["Gas Pressure (MPa)"],
    marker="x",
    linestyle="None",
    markersize=6,
    label="Tank Pressure (MPa)"
)

# =========================
# 3) Plot injection rate (twin axis)
# =========================
rates = pd.read_csv(rate_file)
rates.columns = rates.columns.str.strip()

rates["TimeElapsed"] = pd.to_numeric(rates["TimeElapsed"], errors="coerce")
rates["GAS_INJEC"] = pd.to_numeric(rates["GAS_INJEC"], errors="coerce")
rates = rates.dropna(subset=["TimeElapsed", "GAS_INJEC"]).reset_index(drop=True)

#ax1b = ax1.twinx()
#ax1b.plot(
#    rates["TimeElapsed"] / SEC_PER_DAY,
#    rates["GAS_INJEC"],
#    linestyle="--",
#    linewidth=2,
#    label="Injection rate"
#)
#ax1b.set_ylabel("Injection rate (kg/s)")

# =========================
# Formatting
# =========================
ax1.set_ylabel("Pressure (MPa)")
ax1.set_title("PRES vs Time (days) + Tank Pressure + Injection rate")
ax1.grid(True)
ax1.ticklabel_format(axis='y', style='plain', useOffset=False)

ax2.set_xlabel("Time (days)")
ax2.set_ylabel("Gas Saturation SAT_G (-)")
ax2.set_title("SAT_G vs Time (days)")
ax2.grid(True)

# Legend combine ax1 + ax1b
lines1, labels1 = ax1.get_legend_handles_labels()
#linesb, labelsb = ax1b.get_legend_handles_labels()
ax1.legend(lines1 , labels1 , fontsize=8, ncol=2)

ax2.legend(fontsize=8, ncol=2)

# =========================
# 4) xlim based on FOFT time range
# =========================
if tmin_s is not None and tmax_s is not None:
    ax1.set_xlim(tmin_s / SEC_PER_DAY, tmax_s / SEC_PER_DAY)

ax1.set_ylim(1.5,4.7)
plt.tight_layout()
plt.show()
