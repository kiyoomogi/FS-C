from __future__ import division, unicode_literals, with_statement

import logging
import os

import numpy
import toughio
from toughio._mesh._common import labeler
from toughio._mesh.tough._tough import check_incon, write_incon, write_mesh

try:
    import itasca as it
    from itasca import zonearray as za
    from itasca import gridpointarray as gpa
except ImportError:
    pass


__all__ = [
    "read_save",
    "read_output",
    "write",
]


def read_save(filename):
    """Read TOUGH SAVE file."""
    if it.zone.count() <= 0:
        raise ValueError("Zone is empty.")

    # Read TOUGH SAVE file using toughio.read_save
    labels, data = toughio.read_output(filename)
    if len(labels) < it.zone.count():
        raise ValueError()

    # Load data into FLAC3D
    mapper = {k: v for v, k in enumerate(labels)}
    idx = [mapper[label] for label in labeler(it.zone.count())]

    for i, k in enumerate(sorted(key for key in data.keys() if key.startswith("X"))):
        za.set_extra(i + 2, data[k][idx])
    if "porosity" in data.keys():
        za.set_extra(1, data["porosity"][idx])


def read_output(filename):
    """Read TOUGH output file for each time step."""
    if it.zone.count() <= 0:
        raise ValueError("Zone is empty.")

    # Read TOUGH output using toughio.read_output
    output = toughio.read_output(filename)
    times = [out.time for out in output]
    labels = output[0].labels
    headers = output[0].data.keys()
    if len(labels) < it.zone.count():
        raise ValueError()

    # Reorder data
    mapper = {k: v for v, k in enumerate(labels)}
    idx = [mapper[label] for label in labeler(it.zone.count())]

    return (
        {k: numpy.vstack([out.data[k][idx] for out in output]) for k in headers},
        numpy.array(times),
    )


def write(
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
    """Export current zone geometry to a TOUGH MESH file."""
    if it.zone.count() <= 0:
        raise ValueError("Zone is empty.")
    if nodal_distance not in {"line", "orthogonal"}:
        raise ValueError()
    if not (group_name is None or isinstance(group_name, dict)):
        raise TypeError()
    if not (group_end is None or isinstance(group_end, (str, list, tuple))):
        raise TypeError()
    if not (slot is None or isinstance(slot, str)):
        raise TypeError()
    if not isinstance(incon, bool):
        raise TypeError()

    slot = slot if slot else "Default"

    # Set gravity
    if not numpy.linalg.norm(it.gravity()):
        it.set_gravity((0.0, 0.0, -9.81))
        logging.warning("Gravity has been set to: (0.0, 0.0, -9.81).")

    # Required variables for blocks ELEME and CONNE
    num_cells = it.zone.count()
    labels = labeler(num_cells, label_length)
    nodes = za.pos()
    materials = [z.group() for z in it.zone.list()]
    volumes = numpy.array([z.vol() for z in it.zone.list()])
    try:
        boundary_conditions = za.extra(1)
    except AssertionError:
        boundary_conditions = numpy.zeros(num_cells, dtype=int)
    points = gpa.pos()
    connections = za.neighbors()
    gravity = it.gravity() / numpy.linalg.norm(it.gravity())

    # Define parameters related to faces
    faces = za.faces()
    face_areas = numpy.zeros((it.zone.count(), 6), dtype=float)
    face_normals = numpy.zeros((it.zone.count(), 6, 3), dtype=float)
    for iz, (zone, face) in enumerate(zip(it.zone.list(), faces)):
        idx = [i for i, fc in enumerate(face) if any(gp >= 0 for gp in fc)]
        face_areas[iz, idx] = zone.face_areas()
        face_normals[iz, idx] = zone.face_normals()

    # Required variables for block INCON
    primary_variables, porosities, permeabilities = init_incon(
        num_cells, porosity, permeability
    )
    incon = check_incon(incon, primary_variables, porosities, permeabilities, None, num_cells, None)

    # Write MESH file
    write_mesh(
        filename,
        num_cells,
        labels,
        nodes,
        materials,
        volumes,
        boundary_conditions,
        points,
        connections,
        gravity,
        faces,
        face_normals,
        face_areas,
        nodal_distance,
        group_name,
        group_end,
        coord=False,
    )

    # Write INCON file
    if incon:
        head = os.path.split(filename)[0]
        write_incon(
            os.path.join(head, "INCON") if head else "INCON",
            labels,
            primary_variables,
            porosities,
            permeabilities,
            None,
            None
        )

    # Show warning when groups are appended to the end of block ELEME
    if group_end:
        group_end = [group_end] if isinstance(group_end, str) else group_end
        cmd = ["\tzone delete range group '{}'".format(group) for group in group_end]
        logging.warning(
            (
                "\nSome elements have been moved to the bottom of block 'ELEME'."
                "\nYou may want to execute the following FLAC3D commands to preserve mesh consistency between TOUGH and FLAC3D:\n{}"
            ).format("\n".join(cmd))
        )


def init_incon(num_cells, porosity, permeability):
    """Initialize primary variables, porosity and permeability arrays."""
    primary_variables = numpy.full((num_cells, 4), -1.0e9)
    for i in range(4):
        try:
            primary_variables[:, i] = za.extra(i + 2)
        except AssertionError:
            continue

    if porosity is not None:
        porosities = (
            numpy.array([porosity(z) for z in it.zone.list()])
            if hasattr(porosity, "__call__")
            else numpy.asarray(porosity)
        )
    else:
        porosities = None

    if permeability is not None:
        permeabilities = (
            numpy.array([permeability(z) for z in it.zone.list()])
            if hasattr(permeability, "__call__")
            else numpy.asarray(permeability)
        )
    else:
        permeabilities = None

    return primary_variables, porosities, permeabilities
