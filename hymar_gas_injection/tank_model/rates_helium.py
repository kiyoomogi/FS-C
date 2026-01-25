#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import matplotlib.pyplot as plt

# --- path to your file ---
path = "/Users/matthijsnuus/Desktop/FS-C/model/hymar_gas_injection/smaller_excel_hymar.xlsx"

SECONDS_PER_DAY = 86400.0
rho_water = 1006.0      # kg/m3
ml_to_m3 = 1e-6

# =========================
# 1) Read Excel (skip units row)
# =========================
df = pd.read_excel(path, skiprows=[1])

# Column names (from your file)
time_col  = "TIME"                                 # Days elapsed
water_col = "Water pumped into interface vessel"   # ml (cumulative)
pres_col  = "Injection pressure"                   # kPa

# Convert needed columns to numeric
df[time_col]  = pd.to_numeric(df[time_col], errors="coerce")
df[water_col] = pd.to_numeric(df[water_col], errors="coerce")
df[pres_col]  = pd.to_numeric(df[pres_col], errors="coerce")

# Drop rows where TIME is invalid
df = df.dropna(subset=[time_col]).reset_index(drop=True)

t1, t2 = 205.0, 390.0

mask_zoom = (df[time_col] >= t1) & (df[time_col] <= t2)

df_zoom  = df.loc[mask_zoom].iloc[::50].copy()
df_other = df.loc[~mask_zoom].iloc[::1000].copy()

df_ds = pd.concat([df_other, df_zoom]).sort_values(by=time_col)

# force keep first + last of original dataframe
df_ds = pd.concat([df.iloc[[0]], df_ds, df.iloc[[-1]]]).drop_duplicates().sort_values(by=time_col)

df = df_ds.reset_index(drop=True)


# =========================
# 2) Build time columns
# TIME is already elapsed days → just convert to seconds
# =========================
df["TimeElapsed_days"] = df[time_col]
df["TimeElapsed_s"] = df[time_col] * SECONDS_PER_DAY

# =========================
# 3) Compute injected water mass and rate
# =========================
df["WaterVolume_m3"] = df[water_col] * ml_to_m3
df["WaterMass_kg"] = df["WaterVolume_m3"] * rho_water

df["WaterRate_kg_s"] = df["WaterMass_kg"].diff() / df["TimeElapsed_s"].diff()
df["WaterRate_kg_s"] = df["WaterRate_kg_s"].fillna(0.0)

# Optional: remove negative rates
df = df[df["WaterRate_kg_s"] >= 0].reset_index(drop=True)

# =========================
# 4) Convert pressure units
# =========================
df["InjectionPressure_MPa"] = df[pres_col] / 1000.0  # kPa -> MPa

# =========================
# 5) Plot: Water pumped + Pressure + Rate
# =========================
fig, ax1 = plt.subplots(figsize=(10, 6))

# --- Left axis: cumulative water injected (ml) ---
ax1.plot(df["TimeElapsed_days"], df[water_col], "-o", label="Water pumped (ml)", color='red')
ax1.set_xlabel("Time elapsed (days)")
ax1.set_ylabel("Water pumped (ml)", color='red')
ax1.tick_params(axis="y", colors="red")   #left ticks red
ax1.grid(True)

# --- Right axis: injection pressure (MPa) ---
ax2 = ax1.twinx()
ax2.plot(df["TimeElapsed_days"], df["InjectionPressure_MPa"], "--s",
         label="Injection pressure (MPa)", color='green')
ax2.set_ylabel("Injection pressure (MPa)", color="green")
ax2.tick_params(axis="y", colors="green")  #right ticks green

# --- Third axis: water injection rate (kg/s) ---
ax3 = ax1.twinx()
ax3.spines["right"].set_position(("outward", 60))
ax3.plot(df["TimeElapsed_days"], df["WaterRate_kg_s"], ":^",
         label="Water rate (kg/s)", color='blue')
ax3.set_ylabel("Water injection rate (kg/s)", color="blue")
ax3.tick_params(axis="y", colors="blue")   #outer-right ticks blue
ax3.spines["right"].set_color("blue")      #spine blue (nice touch)


ax1.set_xlim(200, 250)   # applies to both because sharex=True (or same x-axis)
plt.tight_layout()
plt.show()

# =========================
# 6) Export filtered data to CSV
# =========================
df_out = df[["TimeElapsed_days", "TimeElapsed_s", "InjectionPressure_MPa", "WaterRate_kg_s"]].copy()

df_out = df_out.rename(columns={
    "TimeElapsed_days": "Time (days)",
    "TimeElapsed_s": "TimeElapsed",
    "InjectionPressure_MPa": "Gas Pressure (MPa)",
    "WaterRate_kg_s": "Water Injection Rate (kg/s)"
})

out_path = "/Users/matthijsnuus/Desktop/FS-C/model/hymar_gas_injection/tank_model/filtered_water_pressure_rate.csv"
df_out.to_csv(out_path, index=False)

print("Saved filtered CSV:", out_path)
