.. _coupling-doc:

Coupling
========

Submodule :mod:`coupling` provides functions required to run a coupled TOUGH-FLAC simulation and is organized as follow:

.. code-block:: text

    coupling
     ├─extra
     ├─run
     └─permeability
        ├─permeability
        ├─constant
        ├─chin2000
        ├─rutqvist2002
        ├─minkoff2004
        └─hsiung2005

.. note::

    The original FISH routines in the previous versions of TOUGH-FLAC have been translated into Python in a private file named `io.py`. The user does not need to have access to the content of this file.


coupling.run
------------

.. autofunction:: toughflac.coupling.run


coupling.permeability
---------------------

Several permeability models have been implemented in TOUGH-FLAC Python module. The user can also implement new permeability model taking these functions as examples: the first argument of such function **must** be a mask array ``group`` and return permeability and porosity arrays only for current group (if permeability is not affected by porosity change, the porosity array can be whatever array of same size e.g. zeros).


coupling.permeability.permeability
**********************************

.. autofunction:: toughflac.coupling.permeability.permeability


coupling.permeability.constant
******************************

.. autofunction:: toughflac.coupling.permeability.constant


coupling.permeability.chin2000
******************************

.. autofunction:: toughflac.coupling.permeability.chin2000


coupling.permeability.rutqvist2002
**********************************

.. autofunction:: toughflac.coupling.permeability.rutqvist2002


coupling.permeability.minkoff2004
*********************************

.. autofunction:: toughflac.coupling.permeability.minkoff2004


coupling.permeability.hsiung2005
********************************

.. autofunction:: toughflac.coupling.permeability.hsiung2005
