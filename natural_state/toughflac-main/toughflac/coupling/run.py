try:
    import itasca as it

    it.command("python-reset-state false")
except ImportError:
    pass

import os

import numpy

from ._logging import logged
from .io import flac_tough, savefile, tough_flac

__all__ = [
    "run",
]


def run(
    model_save=None,
    deterministic=False,
    damping="combined",
    mechanical_ratio=1.0e-5,
    n_threads=None,
    thermal=True,
    biot_func=None,
    permeability_func=None,
    callback_tough=None,
    callback_flac=None,
    history_func=None,
    history=None,
    savedir=None,
    save_python=False,
):
    """
    Run TOUGH-FLAC coupled simulation.

    Parameters
    ----------
    model_save : str or None, optional, default None
        FLAC3D save file to restore before simulation. It should contain
        zone grid and model configuration.
    deterministic : bool, optional, default False
        If `True`, set deterministic mode.
    damping : str ('local' or 'combined'), optional, default 'combined'
        Set damping for static mechanical process.
    mechanical_ratio : scalar, optional, default 1.0e-5
        FLAC3D mechanical convergence criterion.
    n_threads : int or None, optional, default None
        Number of threads. If `None`, `n_threads` is imported from :mod:`itasca`.
    thermal : bool, optional, default True
        If `True`, activate FLAC3D thermal module.
    biot_func : callable or None, optional, default None
        Function to update Biot's coefficient for each zone.
    permeability_func : dict or None, optional, default None
        Custom permeability models for every keys in `permeability_func`.
    callback_tough : list of callable or None, optional, default None
        List of additional Python functions to run (after reading TOUGH file, before mechanical analysis).
    callback_flac : list of callable or None, optional, default None
        List of additional Python functions to run (after mechanical analysis).
    history_func : dict or None, optional, default None
        Functions for custom history variables in `history`.
    history : dict or None, optional, default None
        Save history variables in different files for every keys in `history`. Each subdictionaries should contain keywords describing variables to export and values defining which points to save. See examples for more details.
    savedir : str or None, optional, default None
        Output directory in which FLAC3D save and history files are exported.
    save_python : bool, optional, default False
        If `True`, Python variables are also exported when saving FLAC3D state.

    Examples
    --------
    History variables that have to be saved during a coupled simulation at each TOUGH time step can be defined using a dictionary, for instance:

    >>> history = {
    >>>     "hist1": {
    >>>         "disp_z" = [
    >>>             [0.0, 0.0, 0.0],
    >>>             [0.0, 0.0, -10.0],
    >>>         ],
    >>>         "disp_x" = [
    >>>             [10.0, 0.0, 0.0],
    >>>         ],
    >>>     },
    >>>     "hist2": {
    >>>         "pp" = [
    >>>             [0.0, 0.0, 0.0],
    >>>         ],
    >>>         "temp" = [
    >>>             [0.0, 0.0, 0.0],
    >>>         ],
    >>>     },
    >>> }

    This will save for each TOUGH time step, the vertical displacement at points ``[0.0, 0.0, 0.0]`` and ``[0.0, 0.0, -10.0]`` and the horizontal displacement at point ``[10.0, 0.0, 0.0]`` in file `hist1.csv`, and the pore pressure and temperature at point ``[0.0, 0.0, 0.0]`` in file `hist2.csv`.

    This dictionary can now be passed to the argument `history` of :func:`run`.

    Warning
    -------
    The user should never have to call this function. It should only be called and executed within the script `flac3d.py` provided for the coupling.

    """
    ierr = _run(
        model_save,
        deterministic,
        damping,
        mechanical_ratio,
        n_threads,
        thermal,
        biot_func,
        permeability_func,
        callback_tough,
        callback_flac,
        history_func,
        history,
        savedir,
        save_python,
    )
    
    if ierr:
        _write_flag("FLAG_FLAC", "1")
    else:
        try:
            savefile("tf_fi.f3sav", dirname=savedir, save_python=save_python)
        except Exception:
            _write_flag("FLAG_FLAC", "1")

    it.command("exit")


@logged
def _run(
    model_save,
    deterministic,
    damping,
    mechanical_ratio,
    n_threads,
    thermal,
    biot_func,
    permeability_func,
    callback_tough,
    callback_flac,
    history_func,
    history,
    savedir,
    save_python,
):
    """Check inputs and start coupled simulation."""

    def _read_flag(filename):
        """Read flag file."""
        return numpy.loadtxt(filename)

    # Check if savedir exists
    if savedir and not os.path.exists(savedir):
        os.makedirs(savedir)

    # Check additional Python functions
    callback_tough = callback_tough if callback_tough else ()
    for i, func in enumerate(callback_tough):
        if not hasattr(func, "__call__"):
            raise TypeError(
                "Element {} in callback_tough is not a Python function.".format(i)
            )

    callback_flac = callback_flac if callback_flac else ()
    for i, func in enumerate(callback_flac):
        if not hasattr(func, "__call__"):
            raise TypeError(
                "Element {} in callback_flac is not a Python function.".format(i)
            )

    # Check history
    history = history if history else {}
    history_func = history_func if history_func else {}
    for attribute, func in history_func.items():
        if not hasattr(func, "__call__"):
            raise TypeError(
                "Invalid history function for attribute '{}'.".format(attribute)
            )

    # Restore model
    if damping not in {"local", "combined"}:
        raise ValueError()
    if model_save:
        try:
            it.command("echo off")
            it.command("model restore '{}'".format(model_save))
        except RuntimeError:
            raise ValueError("Invalid FLAC3D save file '{}'.".format(model_save))
    else:
        if not it.zone.count():
            raise ValueError(
                "Restore a FLAC3D model first or provide a file to restore."
            )

    # Check permeability func
    permeability_func = permeability_func if permeability_func else {}
    for group, func in permeability_func.items():
        if not it.zonearray.in_group(group).sum():
            raise ValueError("Group '{}' does not exist.".format(group))
        if not hasattr(func, "__call__"):
            raise ValueError("Invalid permeability law for group '{}'.".format(group))

    # Apply FLAC3D options
    it.set_deterministic(deterministic)
    it.set_threads(n_threads if n_threads else it.threads())
    it.command("model mechanical active on")
    it.command("model fluid active off")
    it.command("model thermal active off")
    it.command("zone mechanical damping {}".format(damping))
    it.command("zone fluid zone-based-pp on")
    if thermal:
        it.command("zone thermal zone-based-temp on")
    it.command("zone gridpoint initialize displacement-x 0.0")
    it.command("zone gridpoint initialize displacement-y 0.0")
    it.command("zone gridpoint initialize displacement-z 0.0")

    # flag.txt contains string "2" after TOUGH3 has written TOU_FLA
    # FLAC sets flag to string "1" until TOUGH3 modifies it back
    flag = _read_flag("flag.txt")
    while flag < 3:
        if flag == 2:
            # Read TOUGH data
            args = (
                biot_func,
                save_python,
                savedir,
                thermal,
            )
            tough_time = tough_flac(*args)

            # Run additional Python functions
            for func in callback_tough:
                func(tough_time)

            # Quasi-static mechanical analysis
            it.command("model solve mech ratio {}".format(mechanical_ratio))

            # Run additional Python functions
            for func in callback_flac:
                func(tough_time)

            # Write FLAC data
            args = (
                permeability_func,
                history_func,
                biot_func,
                history,
                savedir,
            )
            flac_tough(*args)

            # Set flags
            _write_flag("flag.txt", "1")
            _write_flag("FLAG_FLAC", "0")
        flag = _read_flag("flag.txt")


def _write_flag(filename, flag):
    """Write flag file."""
    with open(filename, "w") as f:
        f.write(flag)
