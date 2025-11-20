import matplotlib.pyplot as plt
import numpy

__all__ = [
    "history",
]


def history(
    filename,
    columns=None,
    time_unit="second",
    yscale=None,
    ylabel=None,
    ax=None,
    figsize=None,
    show_legend=True,
    plot_type="default",
    plt_kws={},
    legend_kws={},
):
    """
    Plot history variables.

    Parameters
    ----------
    filename : str
        History file name.
    columns : int, array_like or None, optional, default None
        Columns to display. If `None`, all the columns > 0 are displayed.
    time_unit : str ('second', 'hour', 'day', 'year'), optional, default 'second'
        Time axis unit.
    yscale : scalar or None, optional, default None
        Scaling factor for y axis.
    ylabel : str or None, optional, default None
        Y axis label.
    ax : matplotlib.axes.Axes or None, optional, default None
        Matplotlib axes. If `None`, a new figure and axe is created.
    figsize : array_like or None, optional, default None
        New figure size if `ax` is `None`.
    show_legend : bool, optional, default True
        If `True`, show legend.
    plot_type : str ('default', 'semilogx', 'semiglogy' or 'loglog'), optional,
        default 'default'
        Plot axis type.
    plt_kws : dict, optional, default {}
        Additional keywords passed to :func:`plt.plot`. Values associated to keys must be array-like consistent with the columns to display.
    legend_kws : dict, optional
        Additional keywords passed to :meth:`ax.legend`.

    Returns
    -------
    matplotlib.axes.Axes
        Matplotlib axes.

    """
    if not isinstance(filename, str):
        raise TypeError()
    if not (columns is None or isinstance(columns, (int, tuple, list, numpy.ndarray))):
        raise TypeError()
    if time_unit not in {"second", "hour", "day", "year"}:
        raise ValueError()
    if not (yscale is None or isinstance(yscale, (int, float))):
        raise TypeError()
    if not (ylabel is None or isinstance(ylabel, str)):
        raise TypeError()
    if not (ax is None or isinstance(ax, plt.Axes)):
        raise TypeError()
    if not (figsize is None or isinstance(figsize, (tuple, list, numpy.ndarray))):
        raise TypeError()
    if not isinstance(show_legend, bool):
        raise TypeError()
    if plot_type not in {"default", "semilogx", "semilogy", "loglog"}:
        raise ValueError()
    if not isinstance(plt_kws, dict):
        raise TypeError()
    if not isinstance(legend_kws, dict):
        raise TypeError()

    # Load history file
    with open(filename, "r") as f:
        header = f.readline().rstrip().split(",")
        hist_file = numpy.loadtxt(f, delimiter=",")
    tought = hist_file[:, 0]
    columns = [columns] if isinstance(columns, int) else columns
    data = hist_file[:, columns].T if columns else hist_file[:, 1:].T

    # Define plotting parameters
    if plt_kws:
        plt_kws = {
            k: [v] if isinstance(v, (str, int)) else v for k, v in plt_kws.items()
        }
        for v in plt_kws.values():
            if len(v) != len(data):
                raise ValueError()
    else:
        plt_kws = {
            "label": [h for i, h in enumerate(header) if i in columns]
            if columns
            else header[1:]
        }

    # Initialize figure
    if ax:
        ax1 = ax
    else:
        figsize = figsize if figsize else (8, 5)
        fig = plt.figure(figsize=figsize, facecolor="white")
        ax1 = fig.add_subplot(1, 1, 1)

    # Apply correct time unit
    if time_unit == "second":
        xlabel = "Time (second)"
        time = tought
    elif time_unit == "hour":
        xlabel = "Time (hour)"
        time = tought / 3600.0
    elif time_unit == "day":
        xlabel = "Time (day)"
        time = tought / 86400.0
    elif time_unit == "year":
        xlabel = "Time (year)"
        time = tought / 31536000.0

    # Scale data if required
    if yscale:
        data *= yscale

    # Plot
    for i, hist in enumerate(data):
        if plot_type == "default":
            ax1.plot(time, hist, **{k: v[i] for k, v in plt_kws.items()})
        elif plot_type == "semilogx":
            ax1.semilogx(time, hist, **{k: v[i] for k, v in plt_kws.items()})
        elif plot_type == "semilogy":
            ax1.semilogy(time, hist, **{k: v[i] for k, v in plt_kws.items()})
        elif plot_type == "loglog":
            ax1.loglog(time, hist, **{k: v[i] for k, v in plt_kws.items()})

    # Plot parameters
    ax1.set_xlabel(xlabel)
    if ylabel:
        ax1.set_ylabel(ylabel)

    # Legend
    if show_legend:
        ax1.legend(**legend_kws)

    plt.draw()
    plt.show()
    return ax1
