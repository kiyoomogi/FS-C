#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import glob
import pandas as pd
import matplotlib.pyplot as plt

folder = "/Users/matthijsnuus/Desktop/FS-C/model/hymar_gas_injection/3_THM"

pressure_file = "/Users/matthijsnuus/Desktop/FS-C/model/hymar_gas_injection/tank_model/filtered_water_pressure_rate.csv"

SEC_PER_DAY = 86400.0
FS = 18  # fontsize

files = sorted(glob.glob(os.path.join(folder, "FOFT*.csv")))
if not files:
    raise FileNotFoundError(f"No FOFT*.csv files found in: {folder}")

fig, (ax1, ax2) = plt.subplots(
    2, 1, figsize=(10, 8), sharex=True,
    gridspec_kw={"height_ratios": [2, 1]}
)

tmin_s = None
tmax_s = None

inj_df = None  # store FOFT_A1367

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

    # global time range
    this_min = df["TIME(S)"].min()
    this_max = df["TIME(S)"].max()
    tmin_s = this_min if tmin_s is None else min(tmin_s, this_min)
    tmax_s = this_max if tmax_s is None else max(tmax_s, this_max)

    label = os.path.basename(f).replace(".csv", "")

    # Save FOFT_A1367 for last (on top)
    if label == "FOFT_A1367":
        inj_df = df.copy()
        continue

    # Plot all other FOFT curves WITHOUT legend entries
    ax1.plot(df["TIME(S)"] / SEC_PER_DAY, df["PRES"] / 1e6, color="0.7", zorder=1)
    ax2.plot(df["TIME(S)"] / SEC_PER_DAY, df["SAT_G"], color="0.7", zorder=1)

# Plot injection filter ON TOP + legend label
if inj_df is not None:
    ax1.plot(
        inj_df["TIME(S)"] / SEC_PER_DAY,
        inj_df["PRES"] / 1e6,
        label="Injection Filter",
        linewidth=3,
        zorder=10
    )
    ax2.plot(
        inj_df["TIME(S)"] / SEC_PER_DAY,
        inj_df["SAT_G"],
        label="Injection Filter",
        linewidth=3,
        zorder=10
    )

# =========================
# 2) Plot tank pressure
# =========================
tank = pd.read_csv(pressure_file)
tank.columns = tank.columns.str.strip()

tank["TimeElapsed"] = pd.to_numeric(tank["TimeElapsed"], errors="coerce")
tank["Gas Pressure (MPa)"] = pd.to_numeric(tank["Gas Pressure (MPa)"], errors="coerce")
tank = tank.dropna(subset=["TimeElapsed", "Gas Pressure (MPa)"]).reset_index(drop=True)

ax1.plot(
    tank["TimeElapsed"] / SEC_PER_DAY,
    tank["Gas Pressure (MPa)"],
    marker="x",
    linestyle="None",
    markersize=8,
    label="Tank Pressure (MPa)",
    zorder=2
)

# =========================
# Formatting
# =========================
ax1.set_ylabel("Pressure (MPa)", fontsize=FS)
ax1.grid(True)
ax1.ticklabel_format(axis="y", style="plain", useOffset=False)
ax1.tick_params(axis="both", labelsize=FS)

ax2.set_xlabel("Time (days)", fontsize=FS)
ax2.set_ylabel("Gas Saturation SAT_G (-)", fontsize=FS)
ax2.grid(True)
ax2.set_yscale("log")
ax2.tick_params(axis="both", labelsize=FS)

# Only show legend entries for Injection Filter + Tank Pressure
ax1.legend(fontsize=FS)
ax2.legend(fontsize=FS)

# xlim from FOFT range
if tmin_s is not None and tmax_s is not None:
    ax1.set_xlim(tmin_s / SEC_PER_DAY, tmax_s / SEC_PER_DAY)

ax1.set_ylim(1.99, 5.7)

plt.tight_layout()
plt.show()
