.. _why-python:

Why Python instead of FISH?
===========================

In this version of TOUGH-FLAC, coupling has been done using Python. According to `Itasca <http://www.itascacg.com/software/python-scripting-1>`_, the benefits of using Python instead of FISH are twofold:

1. Easier scripting using popular scientific numerical computing Python libraries (e.g. NumPy and SciPy included in FLAC3D),
2. Faster computation, especially thanks to vectorized array calculation with NumPy (see :numref:`itasca-python-speed`).

In addition, thanks to its large community (`second most active on GitHub in 2019 <https://github.com/benfred/github-analysis>`_), users can easily find help online.

In previous versions of TOUGH-FLAC, data between TOUGH and FLAC3D were exchanged by the mean of external ASCII files written by FISH. In TOUGH3-FLAC3D, I/O has been improved by reading and writing TOUGH3 and FLAC3D data as binary files using Python (unformatted files that are faster to read and write).

:mod:`toughflac` has been designed to make coupled simulations more user-friendly by extensively using Python capabilities. The package is organized as submodules and functions consistent with FLAC3D own Python module :mod:`itasca` in terms of hierarchy and naming. It allows pre- and post-processing for TOUGH-FLAC to be (almost) fully done in FLAC3D.

.. list-table:: Speed up comparison between FISH and Python (according to `Itasca <http://www.itascacg.com/software/python-scripting-1>`_).
    :name: itasca-python-speed
    :widths: auto
    :header-rows: 1
    :align: center

    *   -
        - FISH
        - Python
        - NumPy
    *   - Zone loop
        - 1
        - 2.5
        - 34
    *   - Gridpoint loop
        - 1
        - 2.5
        - 19
    *   - Stress count
        - 1
        - 1.8
        - 2.9
    *   - Set extra
        - 1
        - 1.3
        - 6.4
    *   - Integer sum
        - 1
        - 4.8
        - 27

.. note::

    FLAC3D v6 embeds Python 2.7 which is no longer maintained and supported by most Python libraries. Some functionalities of :mod:`toughflac` (e.g. mesh import/export) depends on such external open-source libraries. Therefore, we recommend the user to upgrade to FLAC3D v7 (if possible) that embeds Python 3.6 to be able to use all of its capabilities.
