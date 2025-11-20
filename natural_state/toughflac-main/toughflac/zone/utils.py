try:
    import itasca as it
    from itasca import zonearray as za
    from itasca import gridpointarray as gpa
except ImportError:
    pass

import numpy

__all__ = [
    "in_group",
    "near",
    "group",
    "set_dirichlet_bc",
    "initialize_pvariables",
]


def in_group(group, slot=None):
    """
    Return zone group membership as a bool array. Support multiple groups.

    Parameters
    ----------
    group : str or array_like
        Group or list of groups to query.
    slot : str or None, default None
        Slot in which to get group name. If `None`, group names are retrieved from slot 'Default'.

    Returns
    -------
    array_like
        Group membership as a bool array.

    """
    if not isinstance(group, (str, list, tuple)):
        raise TypeError()
    if not (slot is None or isinstance(slot, str)):
        raise TypeError()
    group = [group] if isinstance(group, str) else group
    slot = slot if slot else "Default"

    mask = numpy.zeros(it.zone.count(), dtype=bool)
    for g in group:
        numpy.logical_or(mask, za.in_group(g, slot), out=mask)
    return mask


def near(point, group=None, return_id=False, return_neighbors=False, slot=None):
    """
    Return element name (in MESH file) nearest to query point.

    Parameters
    ----------
    point : array_like
        Coordinates of point to query.
    group : str, array_like or None, optional, default None
        Group or list of groups in which nearest zone is looked for.
    return_id : bool, optional, False
        If `True`, also return zone ID.
    return_neighbors : bool, optional, default False
        If `True`, also return labels of connected elements with their positions.
    slot : str or None, default None
        Slot in which to get group name. If `None`, group names are retrieved from slot 'Default'.

    Returns
    -------
    label : str
        Queried point label.
    id : int
        Queried point ID. Only if ``return_id == True``.
    neighbors : dict, optional
        Queried point neighbors labels and positions. Only if ``return_neighbors == True``.

    """
    if not isinstance(point, (list, tuple, numpy.ndarray)):
        raise TypeError("point must be array-like.")
    if len(point) != 3:
        raise ValueError("point must have 3 coordinates.")

    # Local function
    def zid_to_idx(zid, zids):
        return numpy.where(zids == zid)[0][0]

    # Get nearest point ID
    if group:
        mask = in_group(group, slot)
        if mask.any():
            pos = za.pos()[mask]
            idx = numpy.arange(it.zone.count())[mask]
            idx = idx[numpy.argmin(numpy.linalg.norm(pos - point, axis=1))]
        else:
            raise ValueError("Input groups do not exist.")
    else:
        z = it.zone.near(point)
        idx = zid_to_idx(z.id(), za.ids())

    # Get corresponding label in exported TOUGH MESH
    from toughio._mesh._common import labeler

    label = labeler(idx + 1)[-1]

    # Multiple returns
    out = [str(label)]
    if return_id:
        out.append(int(za.ids()[idx]))
    if return_neighbors:
        z = it.zone.find(za.ids()[idx])
        neighbors = {
            labeler(zid_to_idx(zn.id(), za.ids())): zn.pos()
            for zn in z.adjacent_zones()
            if zn
        }
        out.append(neighbors)
    return out[0] if len(out) == 1 else out


def group(name, range_x=None, range_y=None, range_z=None):
    """
    Assign zone within `range_x`, `range_y` and `range_z` to group `name`.

    Parameters
    ----------
    name : str
        Group name.
    range_x : array_like or None, optional, default None
        Minimum and maximum values in X direction.
    range_y : array_like or None, optional, default None
        Minimum and maximum values in Y direction.
    range_z : array_like or None, optional, default None
        Minimum and maximum values in Z direction.

    Note
    ----
    This function calls FLAC3D :command:`zone group s range`.

    """
    if not isinstance(name, str):
        raise TypeError()
    if not (range_x or range_y or range_z):
        raise ValueError()
    if not (range_x is None or len(range_x) == 2):
        raise ValueError()
    if not (range_y is None or len(range_y) == 2):
        raise ValueError()
    if not (range_z is None or len(range_z) == 2):
        raise ValueError()

    if range_x or range_y or range_z:
        cmd = "zone group '{}' range".format(name)
        if range_x:
            cmd = "{} position-x {} {}".format(cmd, min(range_x), max(range_x))
        if range_y:
            cmd = "{} position-y {} {}".format(cmd, min(range_y), max(range_y))
        if range_z:
            cmd = "{} position-z {} {}".format(cmd, min(range_z), max(range_z))
        it.command(cmd)


def set_dirichlet_bc(group, slot=None):
    """
    Set time-independent Dirichlet boundary conditions for TOUGH elements.

    Parameters
    ----------
    group : str
        Group name.
    slot : str or None, default None
        Slot in which to get group name. If `None`, group names are retrieved from slot 'Default'.

    Note
    ----
    This function creates an extra array in slot 1. This extra array is imported by :func:`toughflac.zone.export_tough`.

    """
    try:
        bc = za.extra(1)
    except AssertionError:
        bc = numpy.zeros(it.zone.count())
    bc[in_group(group, slot)] = 1.0
    za.set_extra(1, bc)


def initialize_pvariables(x1=None, x2=None, x3=None, x4=None, group=None, slot=None):
    """
    Initialize primary variables for `INCON`.

    Parameters
    ----------
    x1 : callable or None, optional, default None
        Function to initialize primary variable X1.
    x2 : callable or None, optional, default None
        Function to initialize primary variable X2.
    x3 : callable or None, optional, default None
        Function to initialize primary variable X3.
    x4 : callable or None, optional, default None
        Function to initialize primary variable X4.
    group : str, tuple, list or None, optional, default None
        Group(s) to which initial conditions are applied. If `None`, initial conditions are applied to all zones.
    slot : str or None, default None
        Slot in which to get group name. If `None`, group names are retrieved from slot 'Default'.

    Note
    ----
    1. This function creates extra arrays in slots 2, 3, 4 and 5, which means that initial conditions are calculated and applied at the time this function is called. These extra arrays are imported by :func:`toughflac.zone.export_tough` if `incon` is `True`,
    2. Currently, only four primary variables are supported.

    Examples
    --------
    Input functions should have 1 argument corresponding to the depth of the zones (even for constant initial conditions). For instance, the user can initialize the four primary variables of equation-of-state ECO2N for the whole grid using anonymous functions `lambda`:

    >>> tf.zone.initialize_pvariables(
    >>>     x1=lambda z: 1.0e5 - 9810.0 * z,
    >>>     x2=lambda z: 0.05,
    >>>     x3=lambda z: 0.0,
    >>>     x4=lambda z: 10.0 - 0.025 * z,
    >>> )

    This will initialize the pressure (X1) at hydrostatic pressure and the temperature (X4) with a thermal gradient of 25 deg/km (1e5 Pa pressure and 10 deg temperature at z = 0). The other two primary variables X2 and X3 are constant.

    Initial conditions can also be applied for specific groups using the argument `group`:

    >>> tf.zone.initialize_pvariables(
    >>>     x1=lambda z: 1.5e5,
    >>>     x2=lambda z: 0.3e-2,
    >>>     x3=lambda z: 0.0,
    >>>     x4=lambda z: 8.0,
    >>>     group=["TOPBC", "TOPFC"],
    >>> )
    >>> tf.zone.initialize_pvariables(
    >>>     x1=lambda z: 1.77e6,
    >>>     x2=lambda z: 0.3e-2,
    >>>     x3=lambda z: 0.0,
    >>>     x4=lambda z: 98.0,
    >>>     group="BOTBC",
    >>> )

    Note that this particular example is no different from setting 'INDOM' in TOUGH input file, but this approach can also be used to apply gradient initial conditions for a specific group.

    """
    X = (x1, x2, x3, x4)
    if not all(x is None or hasattr(x, "__call__") for x in X):
        raise TypeError()
    if all(x is None for x in X):
        raise ValueError()
    if not (group is None or isinstance(group, (str, tuple, list))):
        raise TypeError()

    group = [group] if isinstance(group, str) else group
    mask = in_group(group, slot) if group else numpy.ones(it.zone.count(), dtype=bool)

    for i, x in enumerate(X):
        if x:
            _initialize(i + 1, x, mask)


def _initialize(pvar, func, mask):
    """Initialize primary variable `pvar` in slot `pvar+1`."""
    try:
        x = za.extra(pvar + 1)
    except AssertionError:
        x = numpy.full(it.zone.count(), -1.0e9)
    x[mask] = func(za.pos()[mask, 2])
    za.set_extra(pvar + 1, x)
