from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

# One line to scale EVERYTHING text-related
mpl.rcParams.update({"font.size": 14})   # pick your size


# --- paths
folder = Path("/Users/matthijsnuus/Desktop/FS-C/model/injection_model")
foft_dir = Path("/Users/matthijsnuus/Desktop/FS-C/model/previous_fofts")
bfsb1_path = foft_dir / "BFSB1_meas.csv"

# --- measured series
rates_csv = pd.read_csv(
    "/Users/matthijsnuus/Desktop/FS-C/model/injection_rates/filtered_FSC_injecrates.csv",
    delimiter=",", index_col=0
)
date_series = pd.to_datetime(rates_csv["UTC"].str.slice(0, 19), utc=True, errors="coerce")
rates_csv["new dates"] = date_series
start_utc = rates_csv["new dates"].iloc[0]  # FOFT time zero

def load_and_combine_foft(pattern: str) -> pd.DataFrame:
    """Load all FOFT CSVs matching pattern under foft_dir,
    convert seconds→UTC and Pa→kPa, combine & sort."""
    frames = []
    for f in sorted(foft_dir.glob(pattern)):
        df = pd.read_csv(f)
        if df.shape[1] < 2:
            continue
        secs  = pd.to_numeric(df.iloc[:, 0], errors="coerce")
        p_kPa = pd.to_numeric(df.iloc[:, 1], errors="coerce") * 1e-3  # Pa -> kPa
        t_utc = start_utc + pd.to_timedelta(secs, unit="s")
        m = secs.notna() & p_kPa.notna() & t_utc.notna()
        if m.any():
            frames.append(pd.DataFrame({"t_utc": t_utc[m], "p_kPa": p_kPa[m]}))
    if not frames:
        return pd.DataFrame(columns=["t_utc", "p_kPa"])
    out = pd.concat(frames, ignore_index=True)
    out.sort_values("t_utc", inplace=True)
    out = out.drop_duplicates(subset="t_utc", keep="last")  # if overlaps exist
    return out

# --- combine groups
foft_A11 = load_and_combine_foft("FOFT_A11_0_*.csv")
foft_A3  = load_and_combine_foft("FOFT_A3Q85_*.csv")

# --- figure with two subplots
fig, (ax_top, ax_bot) = plt.subplots(2, 1, sharex=True, figsize=(10, 7), dpi=150)

# TOP: measured + combined A11

if not foft_A11.empty:
    ax_top.plot(foft_A11["t_utc"], foft_A11["p_kPa"], "-", lw=2, alpha=0.95,color="green",label="Modelled BFSB2 (40.5 m)" )
ax_top.plot(date_series, rates_csv.iloc[:, 3] * 1000, ".-", color="grey",label="Measured")  # adjust col if needed
ax_top.set_ylabel("Pressure [kPa]")
ax_top.set_ylim(0, 14000)
ax_top.legend(loc="upper right", ncol=2)

# BOTTOM: combined A3G38 + BFSB1_meas (4th column in bar -> kPa)
if not foft_A3.empty:
    ax_bot.plot(foft_A3["t_utc"], foft_A3["p_kPa"], "-", lw=2,color="orange", alpha=0.95, label="Modelled BFSB1 (42.2 m)")

# BFSB1_meas: parse time (first column), take 4th column, bar->kPa
bfsb1 = pd.read_csv(bfsb1_path, delimiter=",")
t_col = bfsb1.columns[0]
t_bfs = pd.to_datetime(bfsb1[t_col].astype(str).str.slice(0, 26), utc=True, errors="coerce")
y_bfs_bar = pd.to_numeric(bfsb1.iloc[:, 4], errors="coerce")   # 4th column = index 3
y_bfs_kPa = y_bfs_bar * 100.0
m_bfs = t_bfs.notna() & y_bfs_kPa.notna()
ax_bot.plot(t_bfs[m_bfs], y_bfs_kPa[m_bfs], ".-", lw=0.9, color="grey",label="Measured")

ax_bot.set_xlabel("Date")
ax_bot.set_ylabel("Pressure [kPa]")
ax_bot.set_ylim(0, 2500)
ax_bot.legend(loc="upper right", ncol=2)

# tidy & save
fig.autofmt_xdate()
plt.tight_layout()
out_png = folder / "results_two_panel_combined_groups.png"
plt.savefig(out_png, bbox_inches="tight")
plt.show()
print("Saved:", out_png)
