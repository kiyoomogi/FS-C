from __future__ import division

import matplotlib.pyplot as plt
import numpy
from matplotlib.axes import Axes

__all__ = [
    "gutenberg_richter",
]


def gutenberg_richter(magnitudes, n=50, cutoff=None, ax=None):
    """
    Plot Gutenberg-Richter plot.

    Parameters
    ----------
    magnitudes : array_like
        Magnitudes array.
    n : int, optional, default 50
        Number of intervals of magnitudes.
    cutoff : scalar or None, optional, default None
        Cutoff magnitude of completeness for regression (to fit b-value). If `None`, it is estimated using the maximum curvature method.
    ax : matplotlib.axes.Axes or None, optional, default None
        Matplotlib axes.

    Returns
    -------
    matplotlib.axes.Axes
        Matplotlib axes.

    """
    if not isinstance(magnitudes, (list, tuple, numpy.ndarray)):
        raise TypeError()
    if not (isinstance(n, int) and n > 0):
        raise ValueError()
    if not (cutoff is None or isinstance(cutoff, (int, float))):
        raise TypeError()
    if not (ax is None or isinstance(ax, Axes)):
        raise TypeError()

    if ax is None:
        fig = plt.figure(figsize=(8, 5), facecolor="white")
        ax1 = fig.add_subplot(1, 1, 1)
    else:
        ax1 = ax

    # Count number of events
    magnitudes = numpy.asarray(magnitudes)
    dmag = (magnitudes.max() - magnitudes.min()) / n
    mags = magnitudes.min() - 0.5 * dmag + dmag * numpy.arange(n + 1)
    count = [
        numpy.logical_and(m1 <= magnitudes, magnitudes < m2).sum()
        for m1, m2 in zip(mags[:-1], mags[1:])
    ]
    freq = numpy.cumsum(count[::-1])[::-1]
    mags = 0.5 * (mags[:-1] + mags[1:])

    # Fit b-value
    cutoff = cutoff if cutoff is not None else mags[numpy.argmin(numpy.diff(freq))]
    mask = mags >= cutoff
    x, y = mags[mask], freq[mask]
    b, a = numpy.polyfit(x, numpy.log10(y), 1)

    # Frequency-magnitude plot
    ax1.semilogy(
        mags,
        freq,
        linestyle="",
        marker="o",
        markerfacecolor="black",
        markeredgecolor="black",
    )

    # Plot linear regression
    ax1.plot(
        x, 10.0 ** (a + b * x), color="red", linewidth=2,
    )
    ax1.text(
        0.98,
        0.98,
        s="log(N) = {:.2f} - {:.2f}Mw\nMc = {:.2f}".format(a, -b, cutoff),
        color="black",
        fontsize=14,
        horizontalalignment="right",
        verticalalignment="top",
        transform=ax1.transAxes,
    )

    # Plot parameters
    ax1.grid(linestyle=":")
    ax1.set_xlabel("Magnitude")
    ax1.set_ylabel("Frequency")

    plt.draw()
    plt.show()
    return ax1
