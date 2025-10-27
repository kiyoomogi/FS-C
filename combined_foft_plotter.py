#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 27 08:44:33 2025

@author: matthijsnuus
"""

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

folder = Path("/Users/matthijsnuus/Desktop/FS-C/model/injection_model")

# --- measured series (unchanged)
rates_csv = pd.read_csv(
    "/Users/matthijsnuus/Desktop/FS-C/model/injection_rates/filtered_FSC_injecrates.csv",
    delimiter=",", index_col=0
)
date_series = pd.to_datetime(rates_csv["UTC"].str.slice(0, 19), utc=True, errors="coerce")
rates_csv["new dates"] = date_series

start_utc = rates_csv["new dates"].iloc[0]  # FOFT time zero

fig, ax = plt.subplots()

# --- plot measured
ax.plot(date_series, rates_csv.iloc[:, 3] * 1000, ".-",color='grey',label="Measured")  # adjust col if needed

# --- COMBINE all FOFTs from the previous_fofts folder
foft_dir = Path("/Users/matthijsnuus/Desktop/FS-C/model/previous_fofts")
foft_files = sorted(foft_dir.glob("FOFT_*.csv"))  # e.g., FOFT_A11_0.csv, etc.

# ... your imports and earlier code unchanged ...

frames = []
periods = []   # <-- collect (t_start, t_end, name)

for f in foft_files:
    df = pd.read_csv(f)
    if df.shape[1] < 2:
        continue
    secs = pd.to_numeric(df.iloc[:, 0], errors="coerce")
    p_kPa = pd.to_numeric(df.iloc[:, 1], errors="coerce") * 1e-3  # Pa -> kPa
    t_utc = start_utc + pd.to_timedelta(secs, unit="s")
    m = secs.notna() & p_kPa.notna() & t_utc.notna()

    if m.any():
        frames.append(pd.DataFrame({"t_utc": t_utc[m], "p_kPa": p_kPa[m], "source": f.stem}))
        # --- record time window for this file
        t_start = t_utc[m].min()
        t_end   = t_utc[m].max()
        periods.append((t_start, t_end, f.stem))

if frames:
    foft_all = pd.concat(frames, ignore_index=True)
    foft_all.sort_values("t_utc", inplace=True)
    foft_all = foft_all.drop_duplicates(subset="t_utc", keep="last")
    ax.plot(foft_all["t_utc"], foft_all["p_kPa"], "-", lw=1.2, alpha=0.95, color='green', label="FOFT (combined)")

    # --- draw vertical dashed lines for each FOFT file's active period
    for i, (t0, t1, name) in enumerate(periods):
        ax.axvline(t0, color="0.8", linestyle="--", linewidth=1)
        ax.axvline(t1, color="0.8", linestyle="--", linewidth=1)

        # (optional) add a faint label at midpoint
        # t_mid = t0 + (t1 - t0) / 2
        # ax.text(t_mid, ax.get_ylim()[1]*0.98, name, ha="center", va="top",
        #         fontsize=7, color="0.5", rotation=0,
        #         bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.6))

else:
    print("No FOFT files found in", foft_dir)

# ... finishing touches unchanged ...


# --- finishing touches
ax.set_ylim(0, 10000)
ax.set_xlabel("Date")
ax.set_ylabel("Pressure [kPa]")
ax.legend(loc="upper right", ncol=2, fontsize=8)
fig.autofmt_xdate()
plt.savefig('/Users/matthijsnuus/Desktop/FS-C/model/injection_model/results_combined_foft.png',
            bbox_inches='tight', dpi=150)
plt.show()
