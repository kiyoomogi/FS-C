import matplotlib.pyplot as plt
import numpy
from matplotlib.axes import Axes

__all__ = [
    "mohr_diagram",
    "stress_polygon",
]


def mohr_diagram(
    sig1,
    sig2=None,
    sig3=None,
    pp=0.0,
    friction=0.6,
    cohesion=0.0,
    unit=None,
    fill=True,
    ax=None,
):
    """
    Mohr-Coulomb stress diagram.

    Parameters
    ----------
    sig1 : scalar
        Maximum principal stress.
    sig2 : scalar or None, optional, default None
        Intermediate principal stress.
    sig3 : scalar or None, optional, default None
        Minimum principal stress. If `None`, the minimum horizontal stress is calculated using `sig1`.
    pp : scalar, optional, default 0.
        Pore pressure.
    friction : scalar, optional, default 0.6
        Coefficient of friction.
    cohesion : scalar, optional, default 0.
        Coefficient of cohesion.
    unit : str or None, optional, default None
        Axes unit. If `None`, unit is not displayed in axis labels.
    fill : bool, optional, default True
        If `True`, shade area of allowable stress components.
    ax : matplotlib.axes.Axes or None, optional, default None
        Matplotlib axes.

    Returns
    -------
    matplotlib.axes.Axes
        Matplotlib axes.

    Note
    ----
    Compressive stresses are positive.

    """

    def half_circle(xmin, xmax, nx=200):
        """Return scatter coordinates of half-circle."""
        r = 0.5 * (xmax - xmin)
        xm = 0.5 * (xmin + xmax)
        x = numpy.linspace(xmin, xmax, nx)
        y = (numpy.abs(r ** 2 - (x - xm) ** 2)) ** 0.5
        return x, y

    if cohesion < 0.0:
        raise ValueError()
    if not (unit is None or isinstance(unit, str)):
        raise TypeError()
    if not (ax is None or isinstance(ax, Axes)):
        raise TypeError()

    if ax is None:
        fig = plt.figure(figsize=(8, 5), facecolor="white")
        ax1 = fig.add_subplot(1, 1, 1)
    else:
        ax1 = ax

    # Effective stresses
    fmu = ((friction ** 2 + 1.0) ** 0.5 + friction) ** 2
    sig1_eff = sig1 - pp
    sig2_eff = sig2 - pp if sig2 else None
    sig3_eff = sig3 - pp if sig3 else sig1_eff / fmu + pp

    # Principal Mohr circle
    x1, y1 = half_circle(sig3_eff, sig1_eff)
    ax1.plot(
        x1, y1, color="black", linewidth=2, zorder=-1,
    )

    # Intermediate Mohr circles
    if sig2:
        x2, y2 = half_circle(sig3_eff, sig2_eff)
        ax1.plot(
            x2, y2, color="black", linewidth=2, linestyle=":", zorder=-1,
        )

        x3, y3 = half_circle(sig2_eff, sig1_eff)
        ax1.plot(
            x3, y3, color="black", linewidth=2, linestyle=":", zorder=-1,
        )

        if fill:
            x4 = numpy.concatenate((x2, x3, x1[::-1]))
            y4 = numpy.concatenate((y2, y3, y1[::-1]))
            ax1.fill(x4, y4, "gray", alpha=0.25, zorder=-1)

    # Frictional failure line
    x = numpy.linspace(0.0, sig1_eff, 10)
    y = cohesion + friction * x
    ax1.plot(
        x, y, color="red", linewidth=3,
    )

    # Plot parameters
    unit = " ({})".format(unit) if unit else ""
    ax1.set_xlabel("Effective normal stress{}".format(unit))
    ax1.set_ylabel("Shear stress{}".format(unit))

    ax1.grid(linestyle=":")
    ax1.set_xlim(0.0, ax1.get_xlim()[1])
    ax1.set_ylim(0.0, ax1.get_ylim()[1])
    ax1.set_aspect("equal", adjustable="box")

    plt.draw()
    plt.show()
    return ax1


def stress_polygon(stress_vertical, pp=0.0, friction=0.6, unit=None, ax=None):
    """
    Plot stress polygon (a.k.a. Zobackogram).

    Parameters
    ----------
    stress_vertical : scalar
        Vertical stress (overburden).
    pp : scalar, optional, default 0.
        Pore pressure.
    friction : scalar, optional, default 0.6
        Coefficient of friction.
    unit : str or None, optional, default None
        Axes unit. If `None`, unit is not displayed in axis labels.
    ax : matplotlib.axes.Axes or None, optional, default None
        Matplotlib axes.

    Returns
    -------
    matplotlib.axes.Axes
        Matplotlib axes.

    Note
    ----
    Compressive stresses are positive.

    """
    if not (unit is None or isinstance(unit, str)):
        raise TypeError()
    if not (ax is None or isinstance(ax, Axes)):
        raise TypeError()

    if ax is None:
        fig = plt.figure(figsize=(8, 8), facecolor="white")
        ax1 = fig.add_subplot(1, 1, 1)
    else:
        ax1 = ax

    # Horizontal stresses
    fmu = ((friction ** 2 + 1.0) ** 0.5 + friction) ** 2
    stress_horizontal_min = (stress_vertical - pp) / fmu + pp
    stress_horizontal_max = fmu * (stress_vertical - pp) + pp

    # Define the 5 points of the polygon
    points = numpy.array(
        [
            [stress_horizontal_min, stress_horizontal_min],
            [stress_vertical, stress_vertical],
            [stress_horizontal_max, stress_horizontal_max],
            [stress_horizontal_min, stress_vertical],
            [stress_vertical, stress_horizontal_max],
        ]
    )

    # Define the 3 polygons
    polygons = {
        "NF": [0, 1, 3],
        "SS": [3, 1, 4],
        "RF": [1, 2, 4],
    }
    colors = {
        "NF": [226.0 / 255.0, 24.0 / 255.0, 51.0 / 255.0],
        "SS": [52.0 / 255.0, 138.0 / 255.0, 189.0 / 255.0],
        "RF": [152.0 / 255.0, 142.0 / 255.0, 213.0 / 255.0],
    }

    # Draw all the polygons
    for label, polygon in polygons.items():
        x, y = points[polygon].mean(axis=0)
        p1, p2 = points[polygon].T
        ax1.fill(p1, p2, color=colors[label], edgecolor="white", zorder=-1)
        ax1.text(
            x,
            y,
            s=label,
            color="white",
            fontsize=16,
            horizontalalignment="center",
            verticalalignment="center",
        )

    # Vertical stress
    x, y = points[1]
    ax1.text(
        x,
        y,
        s="Sv",
        color="black",
        fontsize=16,
        horizontalalignment="left",
        verticalalignment="top",
    )

    # Plot parameters
    unit = " ({})".format(unit) if unit else ""
    ax1.set_xlabel("Shmin{}".format(unit))
    ax1.set_ylabel("SHmax{}".format(unit))

    ax1.grid(linestyle=":")

    plt.draw()
    plt.show()
    return ax1
