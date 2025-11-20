.. _steps:

Steps for developing and running a coupled TOUGH3-FLAC3D simulation
===================================================================

A coupled TOUGH3 and FLAC3D analysis for a particular problem is typically developed according to the steps described in this section. The user would start by constructing the numerical grid and input data for TOUGH3 and FLAC3D according to the standard procedures for each code.


.. _steps-grid-generation:

Grid generation and basic input data preparation
------------------------------------------------

The geometry and element numbering should be consistent in TOUGH3 and FLAC3D for a particular problem. This can be achieved by generating the meshes using the standard MESHMAKER module attached to the TOUGH3 code and by a special FISH routine in FLAC3D that is programmed such that it produces the same mesh consistent with the MESHMAKER. Another possibility is to use an external mesh generator (e.g. FEM mesh generator) and routines that can translate this FEM mesh into TOUGH3 and FLAC3D meshes. In TOUGH3, the numerical grid is defined by finite volume elements with one node located within the element boundaries that is connected to neighboring elements center nodes. A FLAC3D numerical grid, on the other hand, corner nodes define the element shapes. With the numerical grids defined, input files are prepared for TOUGH3 and FLAC3D including material properties, boundary and initial conditions.

:mod:`toughflac` provides a submodule :mod:`zone` to facilitate the generation of TOUGH3 input files consistent with FLAC3D grids. This submodule allows the user to:

* Define initial conditions for all the elements or a group of elements (i.e. with the same rock type),
* Define time-independent Dirichlet boundary conditions for TOUGH3,
* Export MESH and INCON files for TOUGH3 guaranteed to be consistent with current FLAC3D grid (if conformal),
* Import external meshes (e.g. Gmsh) into FLAC3D (requires external library :mod:`toughio`).


.. _toughflac-tests:

Test simulations and establishment of initial conditions
--------------------------------------------------------

With the input files defined for both TOUGH3 and FLAC3D, analyses should first be conducted to assure that the problem can be solved and that the input data is correctly prepared. A TOUGH3 simulation may be conducted by running one steady state simulation to establish initial conditions, including pressure and thermal gradients, and perhaps saturation profiles. Similarly, a FLAC3D simulation may be conducted to establish initial mechanical stress profiles, if they cannot be exactly defined in the input data. Sometimes, it may be necessary to run a fully coupled TOUGH3 and FLAC3D simulation for establishing initial conditions.


.. _toughflac-setup:

Set-up of a coupled TOUGH-FLAC simulation
-----------------------------------------

The FLAC3D interactive simulation is prepared by:

1. Starting FLAC3D,
2. Calling the FLAC3D mesh and property file (e.g. call *initialize_model.f3dat*).

The FLAC3D state containing the problem specific grid, material properties and initial and boundary conditions is then saved to the file *tf_in.f3sav*. This will be the initial FLAC3D state when invoking the FLAC3D code for the first time in a coupled TOUGH3-FLAC3D simulation.


.. _toughflac-run:

Running a TOUGH-FLAC simulation
-------------------------------

To run a coupled TOUGH-FLAC simulation, a new block ``FLAC`` has been introduced and must be present in the TOUGH input file. The block ``FLAC`` introduces material parameters and coupling options. It must be specified **after** the block ``ROCKS`` and contain two records for each rock type in the same order as in the block ``ROCKS``, plus an additional record placed after the line containing the keyword ``FLAC``.

**Record FLAC.1**: format (16I5), IE_THM(I), I = 1, 16

.. list-table::
    :name: flac-record-1
    :widths: auto
    :header-rows: 1

    *   - 
        - Description
        - Options
    *   - IE_THM(1)
        - Select creep mode (not implemented yet)
        - * 0: default mode
          * 1: creep mode
    *   - IE_THM(2)
        - Select porosity evolution model
        - * 0: no mechanical-induced porosity change
          * 1: mechanical-induced porosity change
          * 2: porosity change as a function of volumetric strain
    *   - IE_THM(3)
        - Select FLAC3D version
        - * 6: call FLAC3D v6 from its default location
          * 7: call FLAC3D v7 from its default location
          * Any other integer: use version defined in coupling script *flac3d.sh*

**Record FLAC.2**: format (I10, 7E10.4), IHM, HM(I), I = 1, 7

.. list-table::
    :name: flac-record-2
    :widths: auto
    :header-rows: 1

    *   - 
        - Description
        - Options
    *   - IHM
        - Select permeability model
        - * 0: permeability models defined in the Python script *flac3d.py*
          * 1: no mechanical-induced permeability change
          * 2: Minkoff et al. (2004)
    *   - HM(I)
        - Parameter values for selected permeability model
        - 

In the current version, only one permeability model has been implemented in the Fortran source code. This model (IHM = 2) is only provided as a basis to implement additional case-specific models. Nevertheless, several permeability models have been implemented in :mod:`toughflac`, and beginners are advised to implement new models directly in Python (IHM = 0).

**Record FLAC.3**: format (I5, 5X, 7E10.4), ICP_THM, CP_THM(I)

.. list-table::
    :name: flac-record-3
    :widths: auto
    :header-rows: 1

    *   - 
        - Description
        - Options
    *   - ICP
        - Select equivalent pore pressure model (Coussy, 2004)
        - * 3: Integral term is zero

An example of block ``FLAC`` for an input file with three different rock types is given below:

.. code-block:: text

    FLAC ----1----*----2----*----3----*----4----*----5----*----6----*----7----*----8
        0    1    7
             1       0.0       0.0       0.0       0.0       0.0       0.0       0.0
        3            0.0       0.0       0.0       0.0       0.0       0.0       0.0
             1       0.0       0.0       0.0       0.0       0.0       0.0       0.0
        3            0.0       0.0       0.0       0.0       0.0       0.0       0.0
             1       0.0       0.0       0.0       0.0       0.0       0.0       0.0
        3            0.0       0.0       0.0       0.0       0.0       0.0       0.0

If the block ``FLAC`` is not present in the TOUGH3 input file, TOUGH-FLAC will perform a TOUGH3 simulation only (for instance to calculate the steady state before running a coupled simulation as explained in Section :ref:`toughflac-tests`).

In general, the coupled TOUGH3-FLAC3D analysis is executed by running the TOUGH3 code and at desired instances calling FLAC3D to perform a quasi-static mechanical analysis. When calling the FLAC3D code from TOUGH3, the FLAC3D code is activated and automatically looks for an initiation file called *flac3d.dat* that simply calls the Python script *flac3d.py*. The latter script import the function :func:`run` of the submodule :mod:`coupling` in which the user can define the main parameters for the coupling. Below is an example of coupling parameters in *flac3d.py*:

.. code-block:: python

    run(
        model_save="tf_in.f3sav",
        deterministic=False,
        damping="combined",
        mechanical_ratio=1.0e-7,
        n_threads=8,
    )

In this case, the FLAC3D convergence criterion or mechanical ratio was set to ``1.0e-7`` down from the default value of ``1.0e-5``. Using more stringent criterion leads to longer simulation runs, but is more accurate.

The FLAC3D code then conducts a few sequential commands, the first one is to restore the current geomechanical conditions stored in a file called *tf_in.f3sav*, thereafter a number of Python functions are invoked which have all been installed in the private submodule :mod:`coupling.io`. The final FLAC3D state is saved into *tf_fi.f3sav*.

The following files should reside in the current working directory:

* The TOUGH3 problem specific input file with block ``FLAC`` correctly defined,
* A file named *tf_in.f3sav* (consistent with the one associated to argument `model_save` in :func:`run`),
* A Python script *flac3d.py* that calls the function :func:`run` from the submodule :mod:`coupling` with some coupling parameters.


Optionally:

* *MESH* if the blocks ``ELEME`` and ``CONNE`` are not included in TOUGH3 input file,
* *INCON* if initial conditions are available (e.g. *SAVE* file from steady state calculation run),
* Additional files required by equation-of-state (e.g. *CO2TAB* for equations-of-state ECO2N, ECO2N v2 and ECO2M).

The TOUGH-FLAC simulation is then started by the usual command as explained in Section :ref:`toughflac-install`. For instance, for equation of state ECO2N:

.. code-block:: bash

    tough3-eco2n INFILE

with ``INFILE`` the TOUGH input file name, or

.. code-block:: bash

    mpiexec -n 4 tough3-eco2n INFILE

to run TOUGH(-FLAC) in parallel using 4 MPI processes.


.. _toughflac-outputs:

TOUGH and FLAC outputs
----------------------

Outputs from TOUGH3 and FLAC3D are printed and saved at desired times, or time step numbers, as defined in the TOUGH3 input file (in block ``TIMES``). When TOUGH3 simulation outputs are printed to the TOUGH3 output file, the current FLAC3D state is saved at the same time to save file named *ftime.f3sav*, where *time* is the current simulation time. This file can later be restored in FLAC3D for plotting and printing. Moreover, a *SAVE* file is written which can be used to restart a TOUGH-FLAC simulation.


.. _toughflac-restart:

Restart of coupled TOUGH-FLAC simulation
----------------------------------------

A restart of a coupled TOUGH-FLAC simulation is conducted in the same way as a restart of a TOUGH3 simulation. That is, using the conditions from the *SAVE* file as initial conditions in *INCON*. The FLAC3D save state to restore is the one in *flac3d.py*.
