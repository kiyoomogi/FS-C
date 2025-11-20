.. _install:

Installation
============

.. _toughflac-install:

TOUGH-FLAC executables
----------------------

To install TOUGH-FLAC, the user only needs to replace few TOUGH3 source files with the modified Fortran files provided. Then, the user can follow the instructions to install TOUGH3 for Cygwin or Windows Subsystem for Linux (WSL):

* Cygwin: when configuring Cygwin, GNU compilers version 7.3.0 (*gcc-core*, *gcc-fortran*, *gcc-g++*) must be selected and *openssh* package installed in addition to the remaining packages required by TOUGH3. Besides, when compiling TOUGH3 for Cygwin, *compile_T3_cygwin.sh* script should **not** have ``--parallel=2`` option enabled,

* WSL: we recommend to use MPICH instead of OpenMPI. TOUGH3-FLAC can be compiled by running the script *compile_T3_Linux.sh*.

Once installed, TOUGH-FLAC executables can be called anywhere from Cygwin or WSL (only if the file *.bashrc* has been correctly modified) by typing ``tough3-eos filename`` where ``eos`` is the equation-of-state identifier (e.g. ``eco2n``) and ``filename`` the TOUGH3 input file (e.g. ``INFILE``). TOUGH(-FLAC) can also be run in parallel using MPI (for instance with 4 cores) by executing the command:

.. code-block:: bash
    
    mpiexec -n 4 tough3-eos filename


TOUGH-FLAC script
-----------------

The location of FLAC3D executable is not hard coded in TOUGH3-FLAC to allow the user to modify it if FLAC3D is not installed in its default location. Instead, TOUGH3-FLAC uses the Bash script *flac3d.sh* that detects the platform on which it is run (Cygwin or WSL) and calls the appropriate command to open FLAC3D console executable. This script should be callable by TOUGH3-FLAC when running a coupled simulation, i.e. it should either be in the current working directory or set in the ``PATH`` so that it can be called from anywhere. We recommend the user to put the script in the installation directory of TOUGH3 if the file *bashrc* has been correctly modified.

.. note::

    TOUGH3-FLAC will run the local script in priority if it is found in the current working directory. 


.. _toughflac-python-install:

TOUGH-FLAC Python module
------------------------

TOUGH-FLAC Python module :mod:`toughflac` provides submodules and functions for pre- and post-processing for TOUGH-FLAC coupled simulations. The FISH routines in the previous versions of TOUGH-FLAC have been translated into Python and packaged as a submodule :mod:`coupling`. FLAC3D offers the possibility to install external Python packages through the package manager associated to its Python environment. By default, it is located in:
 
.. code-block:: text
 
    C:/Program Files/Itasca/Flac3d600/exe64/python27/Scripts/pip.exe
    C:/Program Files/Itasca/FLAC3D700/exe64/python36/Scripts/pip.exe
    
and any package can be downloaded and installed from a Windows console:

.. code-block:: batch

    cmd /C ""path/to/flac3d/pip"" install packagename --user

For convenience, a single Batch script *setup.bat* is provided to install and uninstall :mod:`toughflac`. Once installed, :mod:`toughflac` can be imported into FLAC3D embedded IPython console or within a script without having the Python source files in the current working directory:

.. code-block:: python

    import toughflac as tf

.. note::

    The user may have to edit the path to Python package installer *pip* if FLAC3D is not installed in its default location.


.. _numpy-update:

Update NumPy (FLAC3D v6)
------------------------

Even though Python is usually faster than FISH (see Table :numref:`%s <itasca-python-speed>`), pure Python – as a high level interpreted language – is 1 to 2 order of magnitude slower when compared to lower level compiled languages such as C, C++ or Fortran. A simple trick is to compile computationally heavy functions and wrapping them in Python which then allows near optimal speed (minus inherent involved overheads). NumPy and most of optimized public scientific Python libraries rely on functions or libraries written in C or Fortran.

FLAC3D v6 embeds Python 2.7 with an outdated version of NumPy (1.9.3). To fully exploit NumPy vectorized array computation capabilities, it is recommended to update the package :mod:`numpy` embedded in FLAC3D:

.. code-block:: batch

    cmd /C ""path/to/flac3d/pip"" install -U numpy --user

.. note::

    *Microsoft Visual C++ Compiler for Python 2.7* (`http://aka.ms/vcpython27 <http://aka.ms/vcpython27>`_) must be installed beforehand.
