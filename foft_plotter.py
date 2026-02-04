from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

# ---------------- basic style ----------------
mpl.rcParams.update({"font.size": 14})

# ---------------- paths ----------------
folder   = Path("/Users/matthijsnuus/Desktop/FS-C/model/coupled_model/3_THM/")
#folder   = Path("/Users/matthijsnuus/Desktop/FS-C/model/injection_model/")
foft_dir = Path("/Users/matthijsnuus/Desktop/FS-C/model/previous_fofts")

bfsb1_path  = foft_dir / "BFSB1_meas.csv"
bfsb12_path = foft_dir / "BFSB12_meas.csv"
bfsb2_path = foft_dir / "BFSB2_meas.csv"


foft_files = sorted(folder.glob("FOFT*.csv"))  # e.g. FOFT_A*.csv

# special FOFTs
special_mid_stem = "FOFT_A2818"  # goes to middle panel
special_bot_stem = "FOFT_AEN57"  # goes to bottom panel

# ---------------- measured injection series ----------------
rates_csv1 = pd.read_csv(
    "/Users/matthijsnuus/Desktop/FS-C/model/injection_rates/filtered_FSC_injecrates.csv",
    delimiter=",", index_col=0
)

date_series = pd.to_datetime(
    rates_csv1["UTC"].str.slice(0, 19),
    utc=True,
    errors="coerce"
)
rates_csv1["new dates"] = date_series

# FOFT time zero
start_utc = rates_csv1["new dates"].iloc[0]


def load_foft_to_kpa(path: Path, start_time) -> pd.DataFrame:
    """Load a single FOFT CSV, convert seconds→UTC and Pa→kPa."""
    df = pd.read_csv(path)
    if df.shape[1] < 2:
        return pd.DataFrame(columns=["t_utc", "p_kPa"])

    secs  = pd.to_numeric(df.iloc[:, 0], errors="coerce")
    p_kPa = pd.to_numeric(df.iloc[:, 1], errors="coerce") / 1e6  # Pa -> kPa
    p_norm = p_kPa - p_kPa[0]
    t_utc = start_time + pd.to_timedelta(secs, unit="s")
    m = secs.notna() & p_kPa.notna() & t_utc.notna()

    return pd.DataFrame({"t_utc": t_utc[m], "p_kPa": p_kPa[m], "p_norm": p_norm[m]})


# ---------------- figure with three subplots ----------------
fig, (ax_top, ax_mid, ax_bot) = plt.subplots(
    3, 1, sharex=True, figsize=(10, 9), dpi=150
)



# ---------------- TOP: measured + all FOFTs except A5Y21 & A6O67 ----------------
rates_csv = pd.read_csv(
    "/Users/matthijsnuus/Desktop/FS-C/model/injection_rates/FSC_injecrates.csv",
    delimiter=",",
    index_col=0,
) 

# Parse to datetime and remove timezone info (keep it in UTC numerically)
rates_csv["UTC"] = pd.to_datetime(rates_csv["UTC"], utc=True, errors="coerce").dt.tz_localize(None)

dates = rates_csv["UTC"]  # already datetime, no need to convert again

xmin = dates[92200]
xmax = dates[93350]

def normalize_by_first_visible(t, y, xmin):
    """
    Normalize y by subtracting the first y-value whose time t is >= xmin.
    t and y are 1D arrays/Series already filtered for NaNs.
    """
    t = pd.Series(t).reset_index(drop=True)
    y = pd.Series(y).reset_index(drop=True)

    idx = (t >= xmin).idxmax()  # index of first True
    if not (t >= xmin).any():
        # If nothing is inside the window, return unchanged
        return y

    return y - y.iloc[idx]

 
# ---------------- TOP: measured + FOFTs as ΔP ----------------

# Measured series (absolute pressure) -> normalize to ΔP
rates_csv["UTC"] = pd.to_datetime(rates_csv["UTC"], utc=True, errors="coerce").dt.tz_localize(None)
dates = rates_csv["UTC"]

p_meas = pd.to_numeric(rates_csv.iloc[:, 1], errors="coerce")  # measured pressure column
m_meas = dates.notna() & p_meas.notna()

dates_meas = dates[m_meas]
p_meas = p_meas[m_meas]

# normalize by first visible point (so ΔP=0 at xmin)
p_meas_norm = normalize_by_first_visible(dates_meas, p_meas, xmin)

ax_top.plot(
    dates_meas,
    p_meas_norm,
    ".-",
    color="grey",
    label="Measured (ΔP)"
)

# OPTIONAL: if you want to keep injection rates on the twin axis, keep this block
ax_top2 = ax_top.twinx()
ax_top2.plot(
    date_series.dt.tz_localize(None),   # make tz-naive to match dates_meas
    pd.to_numeric(rates_csv1.iloc[:, 1], errors="coerce"),
    ":",
    color="black",
    label="Injection rates",
    alpha=0.5
)
ax_top2.set_ylabel("Injection rate")  # adjust if units known

# FOFT curves: use p_norm instead of p_kPa
for f in foft_files:
    stem = f.stem
    if stem in (special_mid_stem, special_bot_stem):
        continue

    df_foft = load_foft_to_kpa(f, start_utc)  # returns p_kPa and p_norm
    if not df_foft.empty:
        ax_top.plot(
            df_foft["t_utc"].dt.tz_localize(None),  # make tz-naive to match axis
            df_foft["p_norm"],
            "-",
            lw=3.0,
            alpha=0.9,
            label=stem
        )

ax_top.set_ylabel("ΔP [MPa]")
ax_top.set_title("BFSB2")
ax_top.grid(True)

# pick sensible y-lims for ΔP (change as you like)
ax_top.set_ylim(0, 15)

# keep your xlim window
ax_top.set_xlim(xmin, xmax)

# legend: only for ax_top (not the twin axis)
ax_top.legend(loc="upper right", ncol=2, fontsize=14)



# ---------------- MIDDLE: FOFT_A5Y21 + BFSB1_meas ----------------
# FOFT_A5Y21 modelled
for f in foft_files:
    if f.stem == special_mid_stem:
        df_mid = load_foft_to_kpa(f, start_utc)
        if not df_mid.empty:
            ax_mid.plot(
                df_mid["t_utc"],
                df_mid["p_norm"],
                "-",
                lw=3,
                alpha=0.95,
                color='green',
                label=f"{special_mid_stem} (modelled)"
            )
        break

# BFSB1_meas (4th or 5th column? you used iloc[:,4] before)
bfsb1 = pd.read_csv(bfsb1_path, delimiter=",")
t_col = bfsb1.columns[0]
t_bfs1 = pd.to_datetime(
    bfsb1[t_col].astype(str).str.slice(0, 26),
    utc=True,
    errors="coerce"
)
y_bfs1_bar = pd.to_numeric(bfsb1.iloc[:, 4], errors="coerce")  # bar
y_bfs1_kPa = y_bfs1_bar / 10

m_bfs1 = t_bfs1.notna() & y_bfs1_kPa.notna()
# Make timezone consistent with "dates" (tz-naive)
t_bfs1_naive = t_bfs1.dt.tz_localize(None)

t_plot = t_bfs1_naive[m_bfs1]
y_plot = y_bfs1_kPa[m_bfs1]

y_plot_norm = normalize_by_first_visible(t_plot, y_plot, xmin)

ax_mid.plot(
    t_plot,
    y_plot_norm,
    ".-",
    lw=0.8,
    color="grey",
    label="BFSB1 measured (normalized)"
)


ax_mid.set_ylabel("$\Delta$P [MPa]")
ax_mid.set_ylim(0, 8)
ax_mid.legend(loc="upper right", ncol=2, fontsize=14)
ax_mid.set_title("BFSB1")


# ---------------- BOTTOM: FOFT_A6O67 + BFSB12_meas ----------------
# FOFT_A6O67 modelled
for f in foft_files:
    if f.stem == special_bot_stem:
        df_bot = load_foft_to_kpa(f, start_utc)
        if not df_bot.empty:
            ax_bot.plot(
                df_bot["t_utc"],
                df_bot["p_norm"],
                "-",
                lw=3,
                alpha=0.95,
                color='red',
                label=f"{special_bot_stem} (modelled)"
            )
        break

# BFSB12_meas (downhole pressure [kPa])
bfsb12 = pd.read_csv(bfsb12_path, delimiter=",")
t12 = pd.to_datetime(
    bfsb12["UTC"].astype(str).str.slice(0, 26),
    utc=True,
    errors="coerce"
)
p12_kPa = pd.to_numeric(bfsb12["downhole pressure [kPa]"], errors="coerce") /1e3
m12 = t12.notna() & p12_kPa.notna()

t12_naive = t12.dt.tz_localize(None)

t_plot = t12_naive[m12]
y_plot = p12_kPa[m12]

y_plot_norm = normalize_by_first_visible(t_plot, y_plot, xmin)

ax_bot.plot(
    t_plot,
    y_plot_norm,
    ".-",
    lw=0.9,
    color="grey",
    label="BFSB12 measured (normalized)"
)


ax_bot.set_xlabel("Date")
ax_bot.set_ylabel("$\Delta$P [MPa]")
ax_bot.set_ylim(0, 8)
ax_bot.legend(loc="upper right", ncol=2, fontsize=14)
ax_bot.set_title("BFSB12")


# ---------------- shared x-limits & tidy ----------------
#xmin = date_series.min()
#xmax = date_series.max()

ax_top.set_xlim(xmin, xmax)   # applies to all panels (sharex=True)

mark = (start_utc + pd.to_timedelta(1.099, unit="D")).tz_localize(None)
# or explicitly: mark = pd.Timestamp("2023-05-08 11:02:43.700000")

for a in (ax_top, ax_mid, ax_bot):
    a.axvline(mark, color="k", ls="--", lw=2, alpha=0.8)
    # optional label:
    # a.text(mark, a.get_ylim()[1]*0.95, "day 1.113", rotation=90, va="top")

fig.autofmt_xdate()
plt.tight_layout()
out_png = folder / "results_three_panel_all_fofts.png"
plt.savefig(out_png, bbox_inches="tight")
plt.show()
print("Saved:", out_png)
