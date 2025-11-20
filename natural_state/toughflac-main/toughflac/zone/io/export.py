try:
    import itasca as it
    from itasca import zonearray as za
    from itasca import gridpointarray as gpa
except ImportError:
    pass

import numpy

from ..._common import key_to_slot
from . import tough_io

__all__ = [
    "export",
    "export_tough",
    "export_flac",
    "export_mesh",
    "export_time_series",
]


npts_to_meshio_type = {
    4: "tetra",
    5: "pyramid",
    6: "wedge",
    7: "hexahedron",
    8: "hexahedron",
}


flac3d_to_meshio_order = {
    "tetra": [0, 1, 2, 3],
    "pyramid": [0, 2, 4, 1, 3],
    "wedge": [0, 1, 3, 2, 4, 5],
    "hexahedron": [0, 2, 4, 1, 3, 5, 7, 6],
}


def export(filename, file_format="flac3d", **kwargs):
    """
    Export current FLAC3D grid.

    Parameters
    ----------
    filename : str
        Output file name.
    file_format : str, optional, default 'flac3d'
        Output file format.

    Other Parameters
    ----------------
    nodal_distance : str ('line' or 'orthogonal'), optional, default 'line'
        Only if ``file_format = "tough"``. Method to calculate connection nodal distances:
        - 'line': distance between node and common face along connecting line (distance is not normal),
        - 'orthogonal' : distance between node and its orthogonal projection onto common face (shortest distance).
    porosity : array_like, callable or None, optional, default None
        Only if ``file_format = "tough"``. Porosity array (nzone,) or function to calculate porosity (with input :class:`itasca.Zone`).
    permeability : array_like, callable or None, optional, default None
        Only if ``file_format = "tough"``. Permeability modifiers array (nzone,) or (nzone, 3) or function to calculate permeability modifiers (with input :class:`itasca.Zone`).
    group_name : dict or None, default None
        Only if ``file_format = "tough"``. Rename zone group.
    group_end : str, array_like or None, default None
        Only if ``file_format = "tough"``. Move elements to bottom of block 'ELEME' if they belong to a group in `group_end`.
    slot : str or None, default None
        Only if ``file_format = "tough"``. Slot in which to get group name. If `None`, group names are retrieved from slot 'Default'.
    incon : bool, optional, default False
        Only if ``file_format = "tough"``. If `True`, initial conditions will be written in file `INCON`.

    """
    if not isinstance(filename, str):
        raise TypeError("filename must be a string.")

    if file_format in ["flac3d", "flac3d-ascii"]:
        it.command("zone export '{}'".format(filename))
    elif file_format == "flac3d-binary":
        it.command("zone export '{}' binary".format(filename))
    elif file_format == "tough":
        tough_io.write(filename, **kwargs)
    else:
        try:
            mesh = export_mesh(filename=None, **kwargs)
            mesh.write(filename, file_format=file_format)
        except Exception as e:
            raise NotImplementedError(
                "Exporting to '{}' format is not supported: {}.".format(file_format, e)
            )


def export_tough(
    filename="MESH",
    nodal_distance="line",
    porosity=None,
    permeability=None,
    group_name=None,
    group_end=None,
    slot=None,
    incon=False,
    label_length=None,
):
    """
    Write TOUGH input MESH file consistent with current FLAC3D grid.

    If `incon` is `True`, also write TOUGH input `INCON` file if initial conditions have been set using :func:`toughflac.zone.initialize_pvariables` with the correct number of primary variables (no check is performed). Porosity and permeability modifiers can also be exported in columns 16-60 of `INCON`.

    Parameters
    ----------
    filename : str, optional, default `MESH`
        Output file name.
    nodal_distance : str ('line' or 'orthogonal'), optional, default 'line'
        Method to calculate connection nodal distances:
        - 'line': distance between node and common face along connecting line (distance is not normal),
        - 'orthogonal' : distance between node and its orthogonal projection onto common face (shortest distance).
    porosity : array_like, callable or None, optional, default None
        Porosity array (nzone,) or function to calculate porosity (with input :class:`itasca.Zone`).
    permeability : array_like, callable or None, optional, default None
        Permeability modifiers array (nzone,) or (nzone, 3) or function to calculate permeability modifiers (with input :class:`itasca.Zone`).
    group_name : dict or None, default None
        Rename zone group.
    group_end : str, array_like or None, default None
        Move elements to bottom of block 'ELEME' if they belong to a group in `group_end`.
    slot : str or None, default None
        Slot in which to get group name. If `None`, group names are retrieved from slot 'Default'.
    incon : bool, optional, default False
        If `True`, initial conditions will be written in file `INCON`.
    label_length : int or None, optional, default None
        Number of characters in cell labels.

    Note
    ----
    This function is a shortcut for ``toughflac.zone.export(filename, file_format = "tough", **kwargs)``.

    """
    export(
        filename,
        file_format="tough",
        nodal_distance=nodal_distance,
        porosity=porosity,
        permeability=permeability,
        group_name=group_name,
        group_end=group_end,
        slot=slot,
        incon=incon,
        label_length=label_length,
    )


def export_flac(filename, binary=False):
    """
    Export current FLAC3D grid to a f3grid file.

    Parameters
    ----------
    filename : str
        Output file name.
    binary : bool, optional, default False
        If `True`, export as binary file.

    Note
    ----
    This function calls FLAC3D :command:`zone export filename b`.

    """
    if binary:
        export(filename, file_format="flac3d-binary")
    else:
        export(filename, file_format="flac3d-ascii")


def export_mesh(
    filename=None,
    attribute=None,
    file_format=None,
    interpolate_cell_data=False,
    n_phase=None,
    extra_func=None,
):
    """
    Export queried attributes to external mesh.

    This function requires :mod:`toughio` to be installed.

    Parameters
    ----------
    filename : str or None, default None
        Output file name. If `None`, returns a :class:`toughio.Mesh` object.
    attribute : str, list of str or None, default None
        Attribute or list of attributes (available in :mod:`itasca`) to export.
    file_format : str or None, optional, default None
        Input file format. If `None`, it will be guessed from file's extension.
    interpolate_cell_data : bool, optional, default False
        If `True`, cell data are interpolated onto grid points using volumetric averaging.
    n_phase : int or None, optional, default None
        Number of phases (for attributes 'saturation' and 'pcap').
    extra_func : dict or None, optional, default None
        Extra variables to export with custom functions (zone only).

    Returns
    -------
    toughio.Mesh
        Only if ``filename == None``. Output mesh.

    """
    try:
        import toughio
    except ImportError:
        raise ImportError("Exporting mesh requires toughio to be installed.")

    if not (filename is None or isinstance(filename, str)):
        raise TypeError()
    if not (attribute is None or isinstance(attribute, (str, list, tuple))):
        raise TypeError()
    if not (file_format is None or isinstance(file_format, str)):
        raise TypeError()
    if not (n_phase is None or isinstance(n_phase, int)):
        raise TypeError()

    attributes = (
        [attribute]
        if isinstance(attribute, str)
        else []
        if not attribute
        else attribute
    )
    extra_func = extra_func if extra_func else {}

    # Check n_phase if saturation or pcap are to be exported
    for attribute in attributes:
        cond1 = attribute.startswith("saturation_")
        cond2 = attribute.startswith("pcap_")
        if not n_phase and (cond1 or cond2):
            raise ValueError("n_phase must be a positive integer.")

    # Check extra_func
    for attribute, func in extra_func.items():
        if attribute in attributes:
            raise ValueError()
        if not hasattr(func, "__call__"):
            raise TypeError()

    # Extract points and cells from current model
    cell_types = _get_cell_types()
    points, cells = _get_points_cells(cell_types)

    # Extract point and cell data
    if interpolate_cell_data:
        point_data, cell_data = _get_point_data(attributes, n_phase, extra_func), {}
    else:
        point_data, cell_data = _get_point_cell_data(
            attributes, cell_types, n_phase, extra_func
        )

    # Create a toughio.Mesh
    mesh = toughio.Mesh(points, cells, point_data)
    for k, v in cell_data.items():
        mesh.add_cell_data(k, v)

    # Return or export
    if filename:
        mesh.write(filename, file_format)
    else:
        return mesh


def export_time_series(
    filename,
    savefiles,
    attribute,
    time_steps=None,
    interpolate_cell_data=False,
    n_phase=None,
    extra_func=None,
):
    """
    Export FLAC3D save files as XDMF time series (can be visualized with ParaView).

    This function requires :mod:`toughio` to be installed.

    Parameters
    ----------
    filename : str
        Output file name.
    savefiles : list of str
        List of FLAC3D save files to export for each time step.
    attribute : str, list of str or None, default None
        Attribute or list of attributes (available in :mod:`itasca`) to export.
    time_steps : array_like or None, optional, default None
        List of time steps (in seconds). The order of `time_steps` must be consistent with `savefiles`.
    interpolate_cell_data : bool, optional, default False
        If `True`, cell data are interpolated onto grid points using volumetric averaging.
    n_phase : int or None, optional, default None
        Number of phases (for attributes 'saturation' and 'pcap').
    extra_func : dict or None, optional, default None
        Extra variables to export with custom functions (zone only).

    """
    try:
        import toughio
    except ImportError:
        raise ImportError("Exporting time series requires toughio to be installed.")

    if not isinstance(filename, str):
        raise TypeError()
    if not isinstance(savefiles, (list, tuple)):
        raise TypeError()
    if not all(isinstance(savefile, str) for savefile in savefiles):
        raise TypeError()
    if not (
        time_steps is None
        or isinstance(time_steps, (list, tuple, numpy.ndarray))
        or len(time_steps) == len(savefiles)
    ):
        raise TypeError()
    if not (attribute is None or isinstance(attribute, (str, list, tuple))):
        raise TypeError()
    if not (n_phase is None or isinstance(n_phase, int)):
        raise TypeError()

    attributes = (
        [attribute]
        if isinstance(attribute, str)
        else []
        if not attribute
        else attribute
    )
    extra_func = extra_func if extra_func else {}

    # Check that there is at least one attribute to export
    if not (attributes or extra_func):
        raise ValueError()

    # Check n_phase if saturation or pcap are to be exported
    for attribute in attributes:
        cond1 = attribute.startswith("saturation_")
        cond2 = attribute.startswith("pcap_")
        if not n_phase and (cond1 or cond2):
            raise ValueError("n_phase must be a positive integer.")

    # Check extra_func
    for attribute, func in extra_func.items():
        if attribute in attributes:
            raise ValueError()
        if not hasattr(func, "__call__"):
            raise TypeError()

    # Check if all files exist
    import os

    for savefile in savefiles:
        if not os.path.isfile(savefile):
            raise ValueError("Cannot find save file '{}'.".format(savefile))

    # Sort time steps
    if time_steps:
        time_steps = sorted(time_steps)
        savefiles = [s for _, s in sorted(zip(time_steps, savefiles))]
    else:
        time_steps = numpy.arange(len(savefiles)) + 1

    # Import first model
    it.command("python-reset-state false")
    it.command("model restore '{}'".format(savefiles[0]))

    # Extract points and cells from first model
    cell_types = _get_cell_types()
    points, cells = _get_points_cells(cell_types)

    # Extract data from save files
    point_data, cell_data = {}, {}
    for i, savefile in enumerate(savefiles):
        # First model is already imported
        if i:
            it.command("model restore '{}'".format(savefile))

        # Get point and cell data
        if interpolate_cell_data:
            pdata, cdata = _get_point_data(attributes, n_phase, extra_func), {}
        else:
            pdata, cdata = _get_point_cell_data(
                attributes, cell_types, n_phase, extra_func
            )
        point_data[savefile] = pdata
        cell_data[savefile] = cdata

    # Write XDMF
    toughio.write_time_series(
        filename=filename,
        points=points,
        cells=cells,
        point_data=[point_data[savefile] for savefile in savefiles],
        cell_data=[cell_data[savefile] for savefile in savefiles],
        time_steps=time_steps,
    )


def _get_cell_types():
    """Return cell types in current grid geometry."""
    npts = numpy.sum(za.gridpoints() >= 0, axis=1)
    return [npts_to_meshio_type[n] for n in npts]


def _get_points_cells(cell_types):
    """Return points and cells from current grid geometry."""
    from toughio._mesh._mesh import CellBlock

    cells = []
    for cell_type, cell in zip(cell_types, za.gridpoints()):
        if len(cells) > 0 and cell_type == cells[-1][0]:
            cells[-1][1].append(cell)
        else:
            cells.append((cell_type, [cell]))

    return gpa.pos(), [CellBlock(k, numpy.array(v)[:, flac3d_to_meshio_order[k]]) for k, v in cells]


def _get_point_data(attributes, n_phase, extra_func):
    """
    Return queried attributes as point_data.

    Cell data are interpolated to grid points using volumetric averaging.

    """

    def volumetric_average(data, zones, weights):
        return numpy.array([numpy.dot(w, data[i]) for i, w in zip(zones, weights)])

    point_data = {}
    zones = [list(i) for i in it.gridpointarray.zones()]
    volumes = numpy.array([z.vol() for z in it.zone.list()])
    weights = [volumes[i] / volumes[i].sum() for i in zones]

    for attribute in attributes:
        source, data = _get_attribute(attribute, n_phase)
        # Point data if source is gridpoint array
        if source == "G":
            point_data[attribute] = data
        # Interpolate cell data if source is zone array
        else:
            point_data[attribute] = volumetric_average(data, zones, weights)

    for attribute, data in _get_extra_attributes(extra_func).items():
        point_data[attribute] = volumetric_average(data, zones, weights)
    return point_data


def _get_point_cell_data(attributes, cell_types, n_phase, extra_func):
    """Return queried attributes as point_data and cell_data dicts."""
    pdata, cdata = {}, {}
    for attribute in attributes:
        source, data = _get_attribute(attribute, n_phase)
        # Point data if source is gridpoint array
        if source == "G":
            pdata[attribute] = data
        # Cell data if source is zone array
        else:
            cdata[attribute] = data
    cdata.update(_get_extra_attributes(extra_func))
    return pdata, cdata


def _get_extra_attributes(extra_func):
    """Return a dict containing the calculated extra variables to export."""
    return {
        attribute: numpy.array([func(z) for z in it.zone.list()])
        for attribute, func in extra_func.items()
    }


def _get_attribute(attribute, n_phase):
    """Return queried attribute as an array and its source array."""
    if attribute == "disp_mag":
        return "G", numpy.linalg.norm(gpa.disp(), axis=1)
    elif attribute == "disp_x":
        return "G", gpa.disp()[:, 0]
    elif attribute == "disp_y":
        return "G", gpa.disp()[:, 1]
    elif attribute == "disp_z":
        return "G", gpa.disp()[:, 2]
    elif attribute == "temp":
        return "Z", za.temperature()
    elif attribute == "pp":
        return "Z", numpy.array([z.pp() for z in it.zone.list()])
    elif attribute == "stress_xx":
        return "Z", za.stress_flat()[:, 0]
    elif attribute == "stress_yy":
        return "Z", za.stress_flat()[:, 1]
    elif attribute == "stress_zz":
        return "Z", za.stress_flat()[:, 2]
    elif attribute == "stress_xy":
        return "Z", za.stress_flat()[:, 3]
    elif attribute == "stress_yz":
        return "Z", za.stress_flat()[:, 4]
    elif attribute == "stress_xz":
        return "Z", za.stress_flat()[:, 5]
    elif attribute == "stress_prin_x":
        return "Z", numpy.array([z.stress_prin_x() for z in it.zone.list()])
    elif attribute == "stress_prin_y":
        return "Z", numpy.array([z.stress_prin_y() for z in it.zone.list()])
    elif attribute == "stress_prin_z":
        return "Z", numpy.array([z.stress_prin_z() for z in it.zone.list()])
    elif attribute == "strain_xx":
        return "Z", za.strain_flat()[:, 0]
    elif attribute == "strain_yy":
        return "Z", za.strain_flat()[:, 1]
    elif attribute == "strain_zz":
        return "Z", za.strain_flat()[:, 2]
    elif attribute == "strain_xy":
        return "Z", za.strain_flat()[:, 3]
    elif attribute == "strain_yz":
        return "Z", za.strain_flat()[:, 4]
    elif attribute == "strain_xz":
        return "Z", za.strain_flat()[:, 5]
    elif attribute.startswith("extra_"):
        return "Z", za.extra(int(attribute.split("_")[-1]))
    elif attribute.startswith("prop_"):
        return "Z", za.prop_scalar("-".join(attribute.split("_")[1:]))
    elif attribute == "stress_delta_xx":
        return "Z", za.extra(key_to_slot["dsxx"])
    elif attribute == "stress_delta_yy":
        return "Z", za.extra(key_to_slot["dsyy"])
    elif attribute == "stress_delta_zz":
        return "Z", za.extra(key_to_slot["dszz"])
    elif attribute == "stress_delta_xy":
        return "Z", za.extra(key_to_slot["dsxy"])
    elif attribute == "stress_delta_yz":
        return "Z", za.extra(key_to_slot["dsyz"])
    elif attribute == "stress_delta_xz":
        return "Z", za.extra(key_to_slot["dsxz"])
    elif attribute == "stress_delta_xz":
        return "Z", za.extra(key_to_slot["dsxz"])
    elif attribute == "stress_delta_prin_x":
        return "Z", za.extra(key_to_slot["dsig1"])
    elif attribute == "stress_delta_prin_y":
        return "Z", za.extra(key_to_slot["dsig2"])
    elif attribute == "stress_delta_prin_z":
        return "Z", za.extra(key_to_slot["dsig3"])
    elif attribute == "temp_delta":
        return "Z", za.extra(key_to_slot["dtemp"])
    elif attribute == "pp_delta":
        return "Z", za.extra(key_to_slot["dpp"])
    elif attribute == "strain_vol":
        return "Z", za.extra(key_to_slot["epsv"])
    elif attribute == "pp_equivalent":
        return "Z", za.extra(key_to_slot["pp_eq"])
    elif attribute == "density":
        return "Z", za.extra(key_to_slot["rho"])
    elif attribute == "porosity":
        return "Z", za.extra(key_to_slot["phi"])
    elif attribute == "porosity_delta":
        return "Z", za.extra(key_to_slot["dphi"])
    elif attribute == "porosity_initial":
        return "Z", za.extra(key_to_slot["iphi"])
    elif attribute == "permeability":
        return "Z", za.extra(key_to_slot["k"])
    elif attribute == "biot":
        return "Z", za.extra(key_to_slot["biot"])
    elif attribute == "therm_coeff":
        return "Z", za.extra(key_to_slot["thexp"])
    elif attribute.startswith("saturation_"):
        i = int(attribute.split("_")[-1])
        if i > n_phase:
            raise ValueError()
        return "Z", za.extra(key_to_slot["nph"] + i - 1)
    elif attribute.startswith("pcap_"):
        j = int(attribute.split("_")[-1])
        if j >= n_phase:
            raise ValueError()
        return "Z", za.extra(key_to_slot["nph"] + n_phase + j - 1)
    elif attribute == "group":
        groups = [z.group() for z in it.zone.list()]
        names = {k: v + 1 for v, k in enumerate(set(groups))}
        return "Z", numpy.array([names[group] for group in groups])
    else:
        raise ValueError("Invalid attribute '{}'.".format(attribute))
