#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import matplotlib.pyplot as plt

# --- path to your file ---
path = "/Users/matthijsnuus/Desktop/FS-C/model/hymar_gas_injection/tank_model/water_into_tank.csv"

SECONDS_PER_DAY = 86400.0

# =========================
# 1) Read and clean the CSV
# =========================
df = pd.read_csv(path)

# Convert TIME column
time_col = "TIME (DAYS)"
df[time_col] = pd.to_numeric(df[time_col], errors="coerce")
df = df.dropna(subset=[time_col]).reset_index(drop=True)

# Create TimeElapsed in seconds
df["TimeElapsed"] = df[time_col] * SECONDS_PER_DAY
df["TimeElapsed"] = pd.to_numeric(df["TimeElapsed"], errors="coerce")

# Second column = cumulative amount (water in tank)
val_col = df.columns[1]
df[val_col] = pd.to_numeric(df[val_col], errors="coerce")

# Keep first row even if it contains NaNs, drop NaNs in the rest
df = pd.concat([
    df.iloc[[0]],
    df.iloc[1:].dropna(subset=["TimeElapsed", val_col])
]).reset_index(drop=True)

# =========================
# 2) Downsample
# =========================
df_ds = df.iloc[::800].copy()
if df_ds.index[-1] != df.index[-1]:
    df_ds = pd.concat([df_ds, df.iloc[[-1]]], ignore_index=True)

df_ds = df_ds.reset_index(drop=True)

# Shift time so it starts at 0
df_ds["TimeElapsed"] = df_ds["TimeElapsed"] - df_ds["TimeElapsed"].iloc[0]

# =========================
# 3) Compute rate of second column per second
# =========================
rho_water = 1006.0  # kg/m3
ml_to_m3 = 1e-6

# cumulative injected volume in m3
df_ds["WaterVolume_m3"] = df_ds[val_col] * ml_to_m3

# cumulative injected mass in kg
df_ds["WaterMass_kg"] = df_ds["WaterVolume_m3"] * rho_water

# mass injection rate [kg/s]
df_ds["WaterRate_kg_s"] = df_ds["WaterMass_kg"].diff() / df_ds["TimeElapsed"].diff()
df_ds["WaterRate_kg_s"] = df_ds["WaterRate_kg_s"].fillna(0.0)

# optional: remove negative rates
df_ds = df_ds[df_ds["WaterRate_kg_s"] >= 0].reset_index(drop=True)

# =========================
# 4) Plot
# =========================
# Add elapsed time in days (starting at 0)
df_ds["TimeElapsed_days"] = df_ds[time_col] - df_ds[time_col].iloc[0]

plt.figure(figsize=(8, 5))
plt.plot(df_ds["TimeElapsed_days"], df_ds["WaterRate_kg_s"], marker="o", linestyle="-")
plt.xlabel("TimeElapsed (days)")
plt.ylabel("Water injection rate (kg/s)")
plt.title("Water injection rate into vessel vs Time")
plt.grid(True)
plt.tight_layout()
plt.show()



# =========================
# 5) Export filtered rates
# =========================
df_out = df_ds[["TimeElapsed", "WaterRate_kg_s"]].copy()
out_path = "/Users/matthijsnuus/Desktop/FS-C/model/hymar_gas_injection/tank_model/filtered_water_rate_kgs.csv"
df_out.to_csv(out_path, index=False)


print("Saved:", out_path)
print("Used value column:", val_col)
