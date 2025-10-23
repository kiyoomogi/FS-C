from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

folder = Path("/Users/matthijsnuus/Desktop/FS-C/model/injection_model")
foft_files = sorted(folder.glob("FOFT*.csv"))  # FOFT_A*.csv etc.

# --- measured series (unchanged)
rates_csv = pd.read_csv(
    "/Users/matthijsnuus/Desktop/FS-C/model/injection_rates/filtered_FSC_injecrates.csv",
    delimiter=",", index_col=0
)
date_series = pd.Series(str(np.zeros(len(rates_csv['UTC']))))
for i in range(len(rates_csv['UTC'])):
    date_series[i] = rates_csv['UTC'][i][0:19]
rates_csv['new dates'] = date_series
date_series = pd.to_datetime(rates_csv["new dates"], utc=True, errors="coerce")

# start time for FOFT time zero (kept consistent with your code)
start_utc = pd.to_datetime(rates_csv['new dates'].iloc[0], utc=True, errors='coerce')

fig, ax = plt.subplots()

# --- plot each FOFT file
for f in foft_files:
    df = pd.read_csv(f)
    if df.shape[1] < 2:
        continue
    secs  = pd.to_numeric(df.iloc[:, 0], errors="coerce")
    p_kPa = pd.to_numeric(df.iloc[:, 1], errors="coerce") * 1e-3  # Pa -> kPa
    t_utc = start_utc + pd.to_timedelta(secs, unit="s")

    # drop rows that failed to parse
    m = secs.notna() & p_kPa.notna() & t_utc.notna()
    ax.plot(t_utc[m], p_kPa[m], "-", lw=1, alpha=0.9, label=f.stem)

# --- measured data (unchanged)
ax.plot(date_series, rates_csv.iloc[:, 3] * 1000, ".-", label="Measured")

#ax2.plot(date_series, rates_csv.iloc[:, 1], ".-", label="kg/s")
ax.set_ylim(0,9000)
ax.set_xlabel("Date")
ax.set_ylabel("Pressure [kPa]")
ax.legend(ncol=2, fontsize=8)
fig.autofmt_xdate()
plt.savefig('/Users/matthijsnuus/Desktop/FS-C/model/injection_model/results.png', bbox_inches='tight')
plt.show()
