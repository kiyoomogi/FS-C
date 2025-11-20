try:
    import itasca as it
except ImportError:
    pass

import logging
import os
import shelve

__all__ = [
    "new",
    "save",
    "restore",
    "save_python",
    "restore_python",
]


def new(reset_python=False):
    """
    Reset model state.

    Parameters
    ----------
    reset_python : bool, optional, default False
        If `True`, Python state will be reset.

    """
    if not reset_python:
        it.command("python-reset-state false")
    it.command("model new")
    try:
        from .input import reset_parameters

        reset_parameters()
    except ImportError:
        pass


def save(filename, python_variables=None):
    """
    Save FLAC3D model and Python variables.

    Parameters
    ----------
    filename : str
        Output file name.
    python_variables : dict or None, optional, default None
        Python variables to dump to `filename.pysav`. If `None`, only save FLAC3D state.

    """
    if not isinstance(filename, str):
        raise TypeError()
    if not (python_variables is None or isinstance(python_variables, dict)):
        raise TypeError()

    it.command("model save '{}'".format(filename))
    if python_variables:
        pysav_filename = _pysav_filename(filename)
        save_python(pysav_filename, python_variables)


def restore(filename, python=False, python_target=None):
    """
    Restore FLAC3D model and associated Python variables.

    Parameters
    ----------
    filename : str
        Input file name.
    python : bool, optional, default False
        If `True`, also restore associated Python variables.
    python_target : dict or None, optional, default None
        Dictionary in which Python variables will be restored. If `locals()` or `globals()`, Python variables are directly loaded in the current Python session (existing variables with the same name will be overwritten without any notice). If not `None`, restore associated Python variables even if ``python == False``.

    Returns
    -------
    dict
        Python variables in `filename.pysav`.

    """
    if not isinstance(filename, str):
        raise TypeError()
    if not (python_target is None or isinstance(python_target, dict)):
        raise TypeError()

    it.command("model restore '{}'".format(filename))
    if python or python_target is not None:
        pysav_filename = _pysav_filename(filename)
        return restore_python(pysav_filename, python_target)


def save_python(filename, variables):
    """
    Save Python variables.

    Parameters
    ----------
    filename : str
        Output file name.
    variables : dict
        Python variables to dump to `filename`.

    """
    if not isinstance(filename, str):
        raise TypeError()
    if not isinstance(variables, dict):
        raise TypeError()

    shelf = shelve.open(filename, flag="n", protocol=-1)
    for k, v in variables.items():
        try:
            shelf[k] = v
        except:
            logging.warning("\nUnable to shelve variable '{}'".format(k))
    shelf.close()


def restore_python(filename, target=None):
    """
    Restore Python variables.

    Parameters
    ----------
    filename : str
        Input file name.
    target : dict or None, optional, default None
        Dictionary in which Python variables will be restored. If `locals()` or `globals()`, Python variables are directly loaded in the current Python session (existing variables with the same name will be overwritten without any notice).

    Returns
    -------
    dict
        Python variables in `filename`.

    """
    if not isinstance(filename, str):
        raise TypeError()
    if not (target is None or isinstance(target, dict)):
        raise TypeError()

    shelf = shelve.open(filename)
    shelf_db = {k: v for k, v in shelf.items()}
    shelf.close()

    if target is not None:
        target.update(shelf_db)
    else:
        return shelf_db


def _pysav_filename(filename, keep_path=True):
    """Return Python save file name from FLAC3D save file name."""
    if not keep_path:
        _, filename = os.path.split(filename)
    filename, _ = os.path.splitext(filename)
    return "{}.pysav".format(filename)
