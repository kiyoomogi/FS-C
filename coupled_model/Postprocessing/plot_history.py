import matplotlib.pyplot as plt
import toughflac as tf

plt.style.use("ggplot")

tf.plot.history(
    filename="/TOUGH-FLAC/tough3-flac3dv7/toughflac-master/examples/2dldV6/3_THM/f3out/hist1.csv",
    time_unit="year",
    ylabel="Vertical displacement (m)",
    plt_kws={
        "linewidth": [2, 2, 2, 2],
        "label": ["0 m", "-1200 m", "-1300 m", "-1500 m"],
    },
    legend_kws={
        "title": "Depth",
        "fontsize": 12,
        "loc": "lower center",
        "bbox_to_anchor": (0.5, 0.98),
        "ncol": 4,
        "frameon": False,
    },
)

plt.show()
