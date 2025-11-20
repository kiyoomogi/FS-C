.. _zone-doc:

Zone
====

Submodule :mod:`zone` provides functions to facilitate pre-processing for coupled TOUGH-FLAC simulation and is organized as follow:

.. code-block:: text

    zone
     ├─import_
     ├─import_mesh
     ├─import_flac
     ├─import_tough_output
     ├─import_tough_save
     ├─export
     ├─export_tough
     ├─export_flac
     ├─export_mesh
     ├─export_time_series
     ├─in_group
     ├─near
     ├─group
     ├─set_dirichlet_bc
     ├─initialize_pvariables
     └─create
        └─tartan_brick


zone.import\_
-------------

.. autofunction:: toughflac.zone.import_


zone.import_mesh
----------------

.. autofunction:: toughflac.zone.import_mesh


zone.import_flac
----------------

.. autofunction:: toughflac.zone.import_flac


zone.import_tough_output
------------------------

.. autofunction:: toughflac.zone.import_tough_output


zone.import_tough_save
----------------------

.. autofunction:: toughflac.zone.import_tough_save


zone.export
-----------

.. autofunction:: toughflac.zone.export


zone.export_tough
-----------------

.. autofunction:: toughflac.zone.export_tough

    TOUGH input *MESH* file is composed of two blocks (``ELEME`` and ``CONNE``). All the parameters required to write the block ``ELEME`` are imported from FLAC3D (i.e. element material, volume and center). Connections between elements are reconstructed using the function :func:`itasca.zonearray.neighbors` and areas of common interfaces imported using function :func:`itasca.Zone.face_areas`.

    The line connecting the centers of two adjacent elements is usually not normal to their common interface as required by TOUGH3 and the finite-volume approach. This is only true with Voronoi tessellations and regular structured hexahedral meshes (e.g. TOUGH3 MeshMaker). Thus, the nodal distances can only be approximated for most types of meshes (e.g. tetrahedra). In the current version, two methods have been implemented which can be selected with the option ``nodal_distance``:
    
        1. Distance between node and common face along connecting line (default, Figure :numref:`%s <nodal-distance>` (right)),
        2. Distance between node and its orthogonal projection onto common face (default, Figure :numref:`%s <nodal-distance>` (middle)).

    .. figure:: ../figures/nodal_distance.*
        :name: nodal-distance
        :align: center

        2D view of calculation of nodal distances d\ :sub:`1` and d\ :sub:`2` as distances between nodes and (Left) center of common interface, (Middle) orthogonal projection onto common interface, and (Right) intersection point of line connecting the two nodes and common interface.

    For Dirichlet boundary elements, nodal distances are fixed to ``1.0e-9`` as recommended in TOUGH3 user guide.


zone.export_flac
----------------

.. autofunction:: toughflac.zone.export_flac


zone.export_mesh
----------------

.. autofunction:: toughflac.zone.export_mesh


zone.export_time_series
-----------------------

.. autofunction:: toughflac.zone.export_time_series


zone.in_group
-------------

.. autofunction:: toughflac.zone.in_group


zone.near
---------

.. autofunction:: toughflac.zone.near


zone.group
----------

.. autofunction:: toughflac.zone.group


zone.set_dirichlet_bc
---------------------

.. autofunction:: toughflac.zone.set_dirichlet_bc


zone.initialize_pvariables
--------------------------

.. autofunction:: toughflac.zone.initialize_pvariables


zone.create
-----------

zone.create.tartan_brick
************************

.. autofunction:: toughflac.zone.create.tartan_brick
