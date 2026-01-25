#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import matplotlib.pyplot as plt

# =========================
# 1) Read OUTPUT_CONNE.csv → Gas injection rate
# =========================
file_path = "/Users/matthijsnuus/Desktop/FS-C/model/hymar_gas_injection/tank_model/model_run/OUTPUT_CONNE.csv"

df = pd.read_csv(file_path, skiprows=1)

df = df.rename(columns=lambda x: x.strip())

# Shift first column down by 1 and drop NaNs
df.iloc[:, 0] = df.iloc[:, 0].shift(1)
df = df.dropna().reset_index(drop=True)

# Keep only: first column (time) and second-to-last column (rate)
df = df.iloc[:, [0, -2]].copy()

# Convert time column (take last token)
df.iloc[:, 0] = df.iloc[:, 0].astype(str).str.split().str[-1]
df.iloc[:, 0] = pd.to_numeric(df.iloc[:, 0], errors="coerce")

# Convert rate column to numeric
df.iloc[:, 1] = pd.to_numeric(df.iloc[:, 1], errors="coerce")

df = df.dropna().reset_index(drop=True)

df = df.rename(columns={df.columns[0]: "TimeElapsed", df.columns[1]: "GAS_INJEC"})
df["GAS_INJEC"] = df["GAS_INJEC"] * -1
df = df.sort_values("TimeElapsed").reset_index(drop=True)

# Save filtered rate CSV
out_path = "/Users/matthijsnuus/Desktop/FS-C/model/hymar_gas_injection/tank_model/model_run/filtered_gasrate_from_conne.csv"
df.to_csv(out_path, index=False)
print("Saved:", out_path)

# =========================
# 2) Read filtered_water_pressure_rate.csv → Gas pressure
# =========================
rates_dummy = pd.read_csv(
    "/Users/matthijsnuus/Desktop/FS-C/model/hymar_gas_injection/tank_model/filtered_water_pressure_rate.csv"
)

rates_dummy.columns = rates_dummy.columns.str.strip()

rates_dummy["TimeElapsed"] = pd.to_numeric(rates_dummy["TimeElapsed"], errors="coerce")
rates_dummy["Gas Pressure (MPa)"] = pd.to_numeric(rates_dummy["Gas Pressure (MPa)"], errors="coerce")

rates_dummy = rates_dummy.dropna(subset=["TimeElapsed", "Gas Pressure (MPa)"]).reset_index(drop=True)

# =========================
# 3) Plot both on same figure (two y-axes)
# =========================
fig, ax1 = plt.subplots(figsize=(10, 6))

# Left axis = injection rate
ax1.plot(df["TimeElapsed"], df["GAS_INJEC"], "-o", color="blue", label="Gas injection rate")
ax1.set_xlabel("Time Elapsed [s]")
ax1.set_ylabel("Gas Injection Rate (kg/s)", color="blue")
ax1.tick_params(axis="y", colors="blue")
ax1.grid(True)

# Right axis = pressure
ax2 = ax1.twinx()
ax2.plot(rates_dummy["TimeElapsed"], rates_dummy["Gas Pressure (MPa)"], "--s",
         color="green", label="Gas pressure (MPa)")
ax2.set_ylabel("Gas Pressure (MPa)", color="green")
ax2.tick_params(axis="y", colors="green")

# Combine legends
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="best")

plt.title("Gas Injection Rate + Gas Pressure vs Time")
plt.tight_layout()
plt.show()
