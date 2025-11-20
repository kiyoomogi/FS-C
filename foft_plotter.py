from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

folder = Path("/Users/matthijsnuus/Desktop/FS-C/model/injection_model")
foft_files = sorted(folder.glob("FOFT*.csv"))  # e.g., FOFT_A*.csv

# --- measured series (unchanged)
rates_csv = pd.read_csv(
    "/Users/matthijsnuus/Desktop/FS-C/model/injection_rates/filtered_FSC_injecrates.csv",
    delimiter=",", index_col=0
)
date_series = pd.to_datetime(rates_csv["UTC"].str.slice(0, 19), utc=True, errors="coerce")
rates_csv["new dates"] = date_series

# FOFT time zero (same as before)
start_utc = rates_csv["new dates"].iloc[0]

# --- figure with two subplots (share x for aligned time axis)
fig, (ax_top, ax_bot) = plt.subplots(2, 1, sharex=True, figsize=(10, 7), dpi=150)

# ----- TOP: measured rates + all FOFTs except FOFT_A3G38
ax_top.plot(date_series, rates_csv.iloc[:, 3] * 1000, ".-", label="Measured rate (kPa equiv?)")

for f in foft_files:
    df = pd.read_csv(f)
    if df.shape[1] < 2:
        continue
    secs  = pd.to_numeric(df.iloc[:, 0], errors="coerce")
    p_kPa = pd.to_numeric(df.iloc[:, 1], errors="coerce") * 1e-3  # Pa -> kPa
    t_utc = start_utc + pd.to_timedelta(secs, unit="s")
    m = secs.notna() & p_kPa.notna() & t_utc.notna()

    if f.stem == "FOFT_A3Q85":
        # skip here; plot on bottom
        pass
    else:
        ax_top.plot(t_utc[m], p_kPa[m], "-", lw=1, alpha=0.9, label=f.stem)

ax_top.set_ylabel("Pressure [kPa]")
ax_top.set_ylim(0, 14000)
ax_top.legend(loc="upper right", ncol=2, fontsize=8)
ax_top.set_title("FOFTs (except A3Q85) + measured")

# ----- BOTTOM: FOFT_A3G38 + BFSB1_meas.csv (4th column)
# Plot FOFT_A3G38 if present
for f in foft_files:
    if f.stem == "FOFT_A6O67":
        df = pd.read_csv(f)
        if df.shape[1] >= 2:
            secs  = pd.to_numeric(df.iloc[:, 0], errors="coerce")
            p_kPa = pd.to_numeric(df.iloc[:, 1], errors="coerce") * 1e-3
            t_utc = start_utc + pd.to_timedelta(secs, unit="s")
            m = secs.notna() & p_kPa.notna() & t_utc.notna()
            ax_bot.plot(t_utc[m], p_kPa[m], "-", lw=1.2, alpha=0.95, label="FOFT_A3G38")
        break  # only one file expected with this name

# Plot BFSB1_meas.csv 4th column (iloc[:,3]) vs its timestamp (assume col0 is time)
bfsb1_path = Path("/Users/matthijsnuus/Desktop/FS-C/model/previous_fofts/BFSB1_meas.csv")
bfsb1 = pd.read_csv(bfsb1_path, delimiter=",")

# time parse (assumes first column is timestamp)
t_col = bfsb1.columns[0]
t_bfs = pd.to_datetime(bfsb1[t_col].astype(str).str.slice(0, 26), utc=True, errors="coerce")

# 4th column in BAR  → convert to kPa
y_bfs_bar = pd.to_numeric(bfsb1.iloc[:, 4], errors="coerce")
y_bfs_kPa = y_bfs_bar * 100.0   # 1 bar = 100 kPa

m_bfs = t_bfs.notna() & y_bfs_kPa.notna()
ax_bot.plot(t_bfs[m_bfs], y_bfs_kPa[m_bfs], ".-", lw=0.8, label="BFSB1_meas (kPa)")

ax_bot.set_xlabel("Date")
ax_bot.set_ylabel("Pressure [kPa]")
ax_bot.set_ylim(0, 2500)
ax_bot.legend(loc="upper right", ncol=2, fontsize=8)
ax_bot.set_title("FOFT_A3G38 + BFSB1_meas (4th column)")

# --- tidy up
fig.autofmt_xdate()
plt.tight_layout()
out_png = folder / "results_two_panel.png"
plt.savefig(out_png, bbox_inches="tight")
plt.show()
print("Saved:", out_png)
