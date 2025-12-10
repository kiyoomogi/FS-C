from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

# ---------------- basic style ----------------
mpl.rcParams.update({"font.size": 14})

# ---------------- paths ----------------
folder   = Path("/Users/matthijsnuus/Desktop/FS-C/model/coupled_model/3_THM")
foft_dir = Path("/Users/matthijsnuus/Desktop/FS-C/model/previous_fofts")

bfsb1_path  = foft_dir / "BFSB1_meas.csv"
bfsb12_path = foft_dir / "BFSB12_meas.csv"
bfsb2_path = foft_dir / "BFSB2_meas.csv"


foft_files = sorted(folder.glob("FOFT*.csv"))  # e.g. FOFT_A*.csv

# special FOFTs
special_bot_stem = "FOFT_ADS60"  # goes to middle panel
special_mid_stem = "FOFT_A9C47"  # goes to bottom panel

# ---------------- measured injection series ----------------
rates_csv = pd.read_csv(
    "/Users/matthijsnuus/Desktop/FS-C/model/injection_rates/filtered_FSC_injecrates.csv",
    delimiter=",", index_col=0
)

date_series = pd.to_datetime(
    rates_csv["UTC"].str.slice(0, 19),
    utc=True,
    errors="coerce"
)
rates_csv["new dates"] = date_series

# FOFT time zero
start_utc = rates_csv["new dates"].iloc[0]


def load_foft_to_kpa(path: Path, start_time) -> pd.DataFrame:
    """Load a single FOFT CSV, convert seconds→UTC and Pa→kPa."""
    df = pd.read_csv(path)
    if df.shape[1] < 2:
        return pd.DataFrame(columns=["t_utc", "p_kPa"])

    secs  = pd.to_numeric(df.iloc[:, 0], errors="coerce")
    p_kPa = pd.to_numeric(df.iloc[:, 1], errors="coerce") / 1e6  # Pa -> kPa
    t_utc = start_time + pd.to_timedelta(secs, unit="s")
    m = secs.notna() & p_kPa.notna() & t_utc.notna()

    return pd.DataFrame({"t_utc": t_utc[m], "p_kPa": p_kPa[m]})


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

ax_top.plot(
    dates,
    rates_csv.iloc[:, 1],
    ".-",
    color="grey",
    label="Measured",
)


for f in foft_files:
    stem = f.stem
    if stem in (special_mid_stem, special_bot_stem):
        continue  # skip; those go to mid/bot
    df_foft = load_foft_to_kpa(f, start_utc)
    if not df_foft.empty:
        ax_top.plot(
            df_foft["t_utc"],
            df_foft["p_kPa"],
            "-",
            lw=1.0,
            alpha=0.9,
            label=stem
        )

ax_top.set_ylabel("Pressure [MPa]")
ax_top.set_ylim(0, 50)
ax_top.legend(loc="upper right", ncol=2, fontsize=8)
ax_top.set_title("BFSB2")


# ---------------- MIDDLE: FOFT_A5Y21 + BFSB1_meas ----------------
# FOFT_A5Y21 modelled
for f in foft_files:
    if f.stem == special_mid_stem:
        df_mid = load_foft_to_kpa(f, start_utc)
        if not df_mid.empty:
            ax_mid.plot(
                df_mid["t_utc"],
                df_mid["p_kPa"],
                "-",
                lw=1.2,
                alpha=0.95,
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
ax_mid.plot(
    t_bfs1[m_bfs1],
    y_bfs1_kPa[m_bfs1],
    ".-",
    lw=0.8,
    color="grey",
    label="BFSB1 measured"
)

ax_mid.set_ylabel("Pressure [MPa]")
ax_mid.set_ylim(0, 4)
ax_mid.legend(loc="upper right", ncol=2, fontsize=8)
ax_mid.set_title("BFSB1")


# ---------------- BOTTOM: FOFT_A6O67 + BFSB12_meas ----------------
# FOFT_A6O67 modelled
for f in foft_files:
    if f.stem == special_bot_stem:
        df_bot = load_foft_to_kpa(f, start_utc)
        if not df_bot.empty:
            ax_bot.plot(
                df_bot["t_utc"],
                df_bot["p_kPa"],
                "-",
                lw=1.2,
                alpha=0.95,
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

ax_bot.plot(
    t12[m12],
    p12_kPa[m12],
    ".-",
    lw=0.9,
    color="grey",
    label="BFSB12 measured"
)

ax_bot.set_xlabel("Date")
ax_bot.set_ylabel("Pressure [MPa]")
ax_bot.set_ylim(0, 4)
ax_bot.legend(loc="upper right", ncol=2, fontsize=8)
ax_bot.set_title("BFSB12")


# ---------------- shared x-limits & tidy ----------------
xmin = date_series.min()
xmax = date_series.max()
xmin = dates[91000]
xmax = dates[118000]
ax_top.set_xlim(xmin, xmax)   # applies to all panels (sharex=True)

fig.autofmt_xdate()
plt.tight_layout()
out_png = folder / "results_three_panel_all_fofts.png"
plt.savefig(out_png, bbox_inches="tight")
plt.show()
print("Saved:", out_png)
