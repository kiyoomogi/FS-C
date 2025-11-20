try:
    import itasca as it
except ImportError:
    pass

import os

from . import tough_io

__all__ = [
    "import_",
    "import_mesh",
    "import_flac",
    "import_tough_save",
    "import_tough_output",
]


def _get_open_filename(caption, ext=None, selected_ext=None):
    """Open a PySide Qt open dialog window."""
    try:
        from PySide2.QtWidgets import QFileDialog
    except ImportError:
        from PySide.QtGui import QFileDialog
    filename = QFileDialog.getOpenFileName(
        caption=caption, filter=ext, selectedFilter=selected_ext,
    )
    return str(filename[0])


def import_(filename=None, file_format=None, **kwargs):
    """
    Import external mesh file in FLAC3D.

    Parameters
    ----------
    filename : str or None, default None
        Input file name. If `None`, a file dialog window will be opened.
    file_format : str or None, optional, default None
        Input file format. If `None`, it will be guessed from file's extension. Importing non-FLAC3D grids requires :mod:`toughio`.

    Note
    ----
    1. The trailing underscore in the function name has been added because `import` is already a keyword in Python,
    2. When importing non-FLAC3D grid, :mod:`toughio` writes a temporary f3grid file that is then imported using FLAC3D :command:`zone import`.

    """
    if not filename:
        caption = "Open a mesh file"
        filename = _get_open_filename(caption)
        if not filename:
            return

    if file_format.startswith("flac3d"):
        it.command("zone import '{}'".format(filename))
    else:
        # Read mesh using toughio
        try:
            import toughio
        except ImportError:
            raise ImportError(
                "Importing external formats requires toughio to be installed."
            )
        mesh = toughio.read_mesh(filename, file_format, **kwargs)

        # Import mesh as an external f3grid file
        filename = os.path.split(filename)[1]
        import_mesh(
            mesh, meshname=filename.split(".")[0], prune_duplicates=True,
        )


def import_mesh(mesh, meshname=None, prune_duplicates=False):
    """
    Import meshio.Mesh object as FLAC3D grid.

    This function requires :mod:`toughio` to be installed.

    Parameters
    ----------
    mesh : toughio.Mesh
        Mesh to import.
    meshname : str or None, optional, default None
        Mesh name displayed in FLAC3D project.
    prune_duplicates : bool, optional, default False
        Delete duplicate gridpoints and zones. `Requires numpy >= 1.13.0`.

    """
    try:
        import toughio
    except ImportError:
        raise ImportError(
            "Importing toughio.Mesh object requires toughio to be installed."
        )
    if not isinstance(mesh, toughio.Mesh):
        raise TypeError("mesh must be a toughio.Mesh object.")

    # Initialize temporary file
    import tempfile

    dirname = tempfile.mkdtemp().replace("\\", "/")
    meshname = meshname if meshname else "mesh"
    filename = "{}/{}.f3grid".format(dirname, meshname)

    # Prune duplicate points and cells if needed
    if prune_duplicates:
        mesh.prune_duplicates(mesh)

    # Export grid as f3grid file and import using itasca
    mesh.write(filename, file_format="flac3d", binary=True)
    it.command("zone import '{}'".format(filename))

    # Tidy up
    os.remove(filename)
    os.rmdir(dirname)


def import_flac(filename=None, binary=False):
    """
    Import f3grid file in FLAC3D.

    Parameters
    ----------
    filename : str or None, default None
        Input file name. If `None`, a file dialog window will be opened.
    binary : bool, optional, default False
        If `True`, read input file as binary.

    """
    if not filename:
        caption = "Open a FLAC3D mesh file"
        filename = _get_open_filename(caption)
        if not filename:
            return

    if binary:
        import_(filename, file_format="flac3d-binary")
    else:
        import_(filename, file_format="flac3d-ascii")


def import_tough_save(filename=None):
    """
    Import TOUGH SAVE file as FLAC3D extra variables.

    Primary variables are saved in slots 2 to N+1. Porosity is saved in slot 1.

    Parameters
    ----------
    filename : str or None, default None
        Input file name. If `None`, a file dialog window will be opened.

    """
    if not filename:
        caption = "Open TOUGH SAVE file"
        filename = _get_open_filename(caption)
        if not filename:
            return
    tough_io.read_save(filename)


def import_tough_output(filename=None):
    """
    Import TOUGH output file for each time step.

    Parameters
    ----------
    filename : str or None, default None
        Input file name. If `None`, a file dialog window will be opened.

    Returns
    -------
    dict
        TOUGH output with one item per variable as an array of shape (nt, nzone).
    array_like
        Time steps array.

    """
    if not filename:
        caption = "Open TOUGH output file"
        filename = _get_open_filename(caption)
        if not filename:
            return
    return tough_io.read_output(filename)
