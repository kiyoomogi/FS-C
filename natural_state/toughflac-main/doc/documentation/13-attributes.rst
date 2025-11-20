.. _attributes-doc:

Attributes
==========

Table :numref:`%s <toughflac-attributes>` summarizes all the attributes that can be exported during the coupling (i.e., history variables) or with the functions :func:`toughflac.zone.export_mesh` and :func:`toughflac.zone.export_time_series`.
Some attributes internally computed by :mod:`toughflac` are assigned in FLAC3D extra slots (see column `Slot`). It is recommended **NOT** to overwrite these slots as the functions described in section :ref:`zonearray-doc` are statically linked to these reserved slots.

.. list-table:: List of available attributes in :mod:`toughflac`.
    :name: toughflac-attributes
    :widths: 1 3 1
    :header-rows: 1
    :align: center

    *   - Attribute
        - Description
        - Slot
    *   - ``"disp_mag"``
        - Magnitude of gridpoint displacement vector
        - N/A
    *   - ``"disp_x"``
        - x-component of gridpoint displacement vector
        - N/A
    *   - ``"disp_y"``
        - y-component of gridpoint displacement vector
        - N/A
    *   - ``"disp_z"``
        - z-component of gridpoint displacement vector
        - N/A
    *   - ``"temp"``
        - Zone temperature
        - N/A
    *   - ``"pp"``
        - Zone pore pressure
        - N/A
    *   - ``"stress_xx"``
        - xx-component of the stress tensor
        - N/A
    *   - ``"stress_yy"``
        - yy-component of the stress tensor
        - N/A
    *   - ``"stress_zz"``
        - zz-component of the stress tensor
        - N/A
    *   - ``"stress_xy"``
        - xy-component of the stress tensor
        - N/A
    *   - ``"stress_yz"``
        - yz-component of the stress tensor
        - N/A
    *   - ``"stress_xz"``
        - xz-component of the stress tensor
        - N/A
    *   - ``"stress_prin_x"``
        - x-component of the principal stress
        - N/A
    *   - ``"stress_prin_y"``
        - y-component of the principal stress
        - N/A
    *   - ``"stress_prin_z"``
        - z-component of the principal stress
        - N/A
    *   - ``"strain_xx"``
        - xx-component of the strain tensor
        - N/A
    *   - ``"strain_yy"``
        - yy-component of the strain tensor
        - N/A
    *   - ``"strain_zz"``
        - zz-component of the strain tensor
        - N/A
    *   - ``"strain_xy"``
        - xy-component of the strain tensor
        - N/A
    *   - ``"strain_yz"``
        - yz-component of the strain tensor
        - N/A
    *   - ``"strain_xz"``
        - xz-component of the strain tensor
        - N/A
    *   - ``"stress_delta_xx"``
        - xx-component of the change in stress tensor
        - 21
    *   - ``"stress_delta_yy"``
        - yy-component of the change in stress tensor
        - 22
    *   - ``"stress_delta_zz"``
        - zz-component of the change in stress tensor
        - 23
    *   - ``"stress_delta_xy"``
        - xy-component of the change in stress tensor
        - 24
    *   - ``"stress_delta_yz"``
        - yz-component of the change in stress tensor
        - 25
    *   - ``"stress_delta_xz"``
        - xz-component of the change in stress tensor
        - 26
    *   - ``"stress_delta_prin_x"``
        - x-component of the change in principal stress
        - 27
    *   - ``"stress_delta_prin_y"``
        - y-component of the change in principal stress
        - 28
    *   - ``"stress_delta_prin_z"``
        - z-component of the change in principal stress
        - 29
    *   - ``"temp_delta"``
        - Zone change in temperature
        - 19
    *   - ``"pp_delta"``
        - Zone change in pore pressure
        - 17
    *   - ``"strain_vol"``
        - Zone volumetric strain
        - 20
    *   - ``"pp_equivalent"``
        - Zone equivalent pore pressure
        - 16
    *   - ``"density"``
        - Zone density
        - 30
    *   - ``"porosity"``
        - Zone porosity
        - 12
    *   - ``"porosity_delta"``
        - Zone change in porosity
        - 14
    *   - ``"porosity_initial"``
        - Zone initial porosity
        - 13
    *   - ``"permeability"``
        - Zone permeability
        - 11
    *   - ``"biot"``
        - Zone Biot's coefficient
        - 31
    *   - ``"therm_coeff"``
        - Zone volumetric thermal expansion coefficient
        - 32
    *   - ``"saturation_i"``
        - Zone saturation for phase ``i`` (integer)
        - 32 + ``i``
    *   - ``"pcap_i"``
        - Zone capillary pressure for phase ``i`` (integer)
        - 32 + ``i`` + ``NPH``
    *   - ``"prop_s"``
        - Property ``s`` (string corresponding to a property available in FLAC3D)
        - N/A
    *   - ``"extra_i"``
        - Extra variable in slot ``i`` (integer from 1 to 128)
        - ``i``
