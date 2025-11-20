import matplotlib.pyplot as plt
import toughflac as tf

plt.style.use("ggplot")

tf.plot.history(
    filename="3_THM/f3out/hist1.csv",
    columns=[1, 3, 4],
    time_unit="year",
    ylabel="Displacement (m)",
    plt_kws={
        "linewidth": [2, 2, 2],
        "label": ["z (0, 0, -10)", "z (0, 0, -1000)", "z (100, 0, -10)"],
    },
    legend_kws = {
        "fontsize": 12,
        "loc": "lower center",
        "bbox_to_anchor": (0.5, 0.98),
        "ncol": 4,
        "frameon": False,
    },
)

plt.show()
