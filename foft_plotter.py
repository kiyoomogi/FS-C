from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

# ---------------- basic style ----------------
mpl.rcParams.update({"font.size": 14})

# ---------------- paths ----------------
#folder   = Path("/Users/matthijsnuus/Desktop/FS-C/model/coupled_model/3_THM/")
folder = Path("/Users/matthijsnuus/Desktop/FS-C/model/coarse_model/coupled_model/3_THM/")
foft_dir = Path("/Users/matthijsnuus/Desktop/FS-C/model/previous_fofts")

bfsb1_path  = foft_dir / "BFSB1_meas.csv"
bfsb12_path = foft_dir / "BFSB12_meas.csv"
bfsb2_path  = foft_dir / "BFSB2_meas.csv"

foft_files = sorted(folder.glob("FOFT*.csv"))

# special FOFTs
special_mid_stem = "FOFT_A2598"
special_bot_stem = "FOFT_A2635"

# ---------------- measured injection series (rates) ----------------
rates_csv1 = pd.read_csv(
    "/Users/matthijsnuus/Desktop/FS-C/model/injection_rates/filtered_FSC_injecrates.csv",
    delimiter=",",
    index_col=0,
)

rates_csv1["new dates"] = pd.to_datetime(
    rates_csv1["UTC"].astype(str).str.slice(0, 19),
    utc=True,
    errors="coerce",
)

# FOFT time zero (UTC-aware)
start_utc = rates_csv1["new dates"].iloc[0]

# ---------------- helpers ----------------
def load_foft_to_mpa(path: Path, start_time) -> pd.DataFrame:
    """Load a single FOFT CSV, convert seconds→UTC and Pa→MPa."""
    df = pd.read_csv(path)
    if df.shape[1] < 2:
        return pd.DataFrame(columns=["t_utc", "p_MPa"])

    secs = pd.to_numeric(df.iloc[:, 0], errors="coerce")
    p_MPa = pd.to_numeric(df.iloc[:, 1], errors="coerce") / 1e6  # Pa -> MPa
    t_utc = start_time + pd.to_timedelta(secs, unit="s")

    m = secs.notna() & p_MPa.notna() & t_utc.notna()
    return pd.DataFrame({"t_utc": t_utc[m], "p_MPa": p_MPa[m]})


def normalize_by_reference_time(t, y, ref_time):
    """
    Normalize y by subtracting the y-value at the sample whose time is closest to ref_time.
    This keeps normalization fixed even if you later change xlim.
    """
    t = pd.Series(t).reset_index(drop=True)
    y = pd.Series(y).reset_index(drop=True)

    # Find index closest to ref_time (works for datetime64)
    idx = (t - ref_time).abs().idxmin()
    return y - y.iloc[idx]


# ---------------- load measured pressure series (for TOP) ----------------
rates_csv = pd.read_csv(
    "/Users/matthijsnuus/Desktop/FS-C/model/injection_rates/FSC_injecrates.csv",
    delimiter=",",
    index_col=0,
)

# Make datetime tz-naive (still UTC numerically) to simplify matplotlib alignment
rates_csv["UTC"] = pd.to_datetime(rates_csv["UTC"], utc=True, errors="coerce").dt.tz_localize(None)
dates = rates_csv["UTC"]

# Choose your plotting window (this does NOT affect normalization)
xmin = dates.iloc[92200]
xmax = dates.iloc[115900]

# Fixed normalization reference index/time (this is what you asked for)
ref_index = 92200
ref_time = dates.iloc[ref_index]

# ---------------- figure ----------------
fig, (ax_top, ax_mid, ax_bot) = plt.subplots(3, 1, sharex=True, figsize=(10, 9), dpi=150)

# ---------------- TOP: measured ΔP + FOFT ΔP ----------------
p_meas = pd.to_numeric(rates_csv.iloc[:, 1], errors="coerce")  # measured pressure column (assumed MPa)
m_meas = dates.notna() & p_meas.notna()

dates_meas = dates[m_meas]
p_meas = p_meas[m_meas]

p_meas_norm = normalize_by_reference_time(dates_meas, p_meas, ref_time)

ax_top.plot(dates_meas, p_meas_norm, ".-", color="grey", label="Measured (ΔP)")

# Twin axis: injection rates
ax_top2 = ax_top.twinx()
ax_top2.plot(
    rates_csv1["new dates"].dt.tz_localize(None),
    pd.to_numeric(rates_csv1.iloc[:, 1], errors="coerce"),
    ":",
    color="black",
    alpha=0.5,
)
ax_top2.set_ylabel("Injection rate")

# FOFT curves normalized at the SAME ref_time (index 92200)
for f in foft_files:
    stem = f.stem
    if stem in (special_mid_stem, special_bot_stem):
        continue

    df_foft = load_foft_to_mpa(f, start_utc)
    if df_foft.empty:
        continue

    t_foft = df_foft["t_utc"].dt.tz_localize(None)
    p_foft = df_foft["p_MPa"]

    p_foft_norm = normalize_by_reference_time(t_foft, p_foft, ref_time)

    ax_top.plot(t_foft, p_foft_norm, "-", lw=3.0, alpha=0.9, label=stem)

ax_top.set_ylabel(r"$\Delta P$ [MPa]")
ax_top.set_title("BFSB2")
ax_top.grid(True)
ax_top.set_ylim(0, 15)
ax_top.set_xlim(xmin, xmax)
ax_top.legend(loc="upper right", ncol=2, fontsize=14)

# ---------------- MIDDLE: special FOFT + BFSB1 measured ----------------
# Modelled (special_mid_stem) normalized at ref_time
for f in foft_files:
    if f.stem == special_mid_stem:
        df_mid = load_foft_to_mpa(f, start_utc)
        if not df_mid.empty:
            t_mid = df_mid["t_utc"].dt.tz_localize(None)
            p_mid = df_mid["p_MPa"]
            p_mid_norm = normalize_by_reference_time(t_mid, p_mid, ref_time)

            ax_mid.plot(t_mid, p_mid_norm, "-", lw=3, alpha=0.95, color="green",
                        label=f"{special_mid_stem} (modelled)")
        break

# BFSB1 measured (bar -> MPa)
bfsb1 = pd.read_csv(bfsb1_path, delimiter=",")
t_col = bfsb1.columns[0]
t_bfs1 = pd.to_datetime(bfsb1[t_col].astype(str).str.slice(0, 26), utc=True, errors="coerce").dt.tz_localize(None)
p_bfs1_bar = pd.to_numeric(bfsb1.iloc[:, 4], errors="coerce")  # bar
p_bfs1_MPa = p_bfs1_bar * 0.1  # 1 bar = 0.1 MPa

m_bfs1 = t_bfs1.notna() & p_bfs1_MPa.notna()
t_plot = t_bfs1[m_bfs1]
y_plot = p_bfs1_MPa[m_bfs1]

y_plot_norm = normalize_by_reference_time(t_plot, y_plot, ref_time)

ax_mid.plot(t_plot, y_plot_norm, ".-", lw=0.8, color="grey", label="BFSB1 measured (ΔP)")
ax_mid.set_ylabel(r"$\Delta P$ [MPa]")
ax_mid.set_ylim(0, 8)
ax_mid.legend(loc="upper right", ncol=2, fontsize=14)
ax_mid.set_title("BFSB1")
ax_mid.grid(True)

# ---------------- BOTTOM: special FOFT + BFSB12 measured ----------------
# Modelled (special_bot_stem) normalized at ref_time
for f in foft_files:
    if f.stem == special_bot_stem:
        df_bot = load_foft_to_mpa(f, start_utc)
        if not df_bot.empty:
            t_bot = df_bot["t_utc"].dt.tz_localize(None)
            p_bot = df_bot["p_MPa"]
            p_bot_norm = normalize_by_reference_time(t_bot, p_bot, ref_time)

            ax_bot.plot(t_bot, p_bot_norm, "-", lw=3, alpha=0.95, color="red",
                        label=f"{special_bot_stem} (modelled)")
        break

# BFSB12 measured: downhole pressure [kPa] -> MPa
bfsb12 = pd.read_csv(bfsb12_path, delimiter=",")
t12 = pd.to_datetime(bfsb12["UTC"].astype(str).str.slice(0, 26), utc=True, errors="coerce").dt.tz_localize(None)
p12_MPa = pd.to_numeric(bfsb12["downhole pressure [kPa]"], errors="coerce") / 1000.0  # kPa -> MPa

m12 = t12.notna() & p12_MPa.notna()
t_plot = t12[m12]
y_plot = p12_MPa[m12]

y_plot_norm = normalize_by_reference_time(t_plot, y_plot, ref_time)

ax_bot.plot(t_plot, y_plot_norm, ".-", lw=0.9, color="grey", label="BFSB12 measured (ΔP)")
ax_bot.set_xlabel("Date")
ax_bot.set_ylabel(r"$\Delta P$ [MPa]")
ax_bot.set_ylim(0, 8)
ax_bot.legend(loc="upper right", ncol=2, fontsize=14)
ax_bot.set_title("BFSB12")
ax_bot.grid(True)

# ---------------- annotate & finalize ----------------
mark = (start_utc + pd.to_timedelta(1.151, unit="D")).tz_localize(None)
for a in (ax_top, ax_mid, ax_bot):
    a.axvline(mark, color="k", ls="--", lw=2, alpha=0.8)


# ---------------- extra timestamp: May 8th 16:52 (same year as data) ----------------
year = ref_time.year  # ensures same year as dataset
may_mark = pd.Timestamp(year=year, month=5, day=8, hour=16, minute=52)

for a in (ax_top, ax_mid, ax_bot):
    a.axvline(may_mark, color="blue", ls="--", lw=2, alpha=0.9)

fig.autofmt_xdate()
plt.tight_layout()

out_png = folder / "results_three_panel_all_fofts.png"
# plt.savefig(out_png, bbox_inches="tight")
plt.show()
print("Saved:", out_png)