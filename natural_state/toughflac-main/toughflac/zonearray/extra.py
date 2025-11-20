try:
    import itasca as it
    from itasca import zonearray as za
except ImportError:
    pass

import numpy

from .._common import key_to_slot

__all__ = [
    "permeability",
    "porosity",
    "porosity_initial",
    "porosity_delta",
    "pp",
    "pp_equivalent",
    "pp_delta",
    "temperature",
    "temperature_delta",
    "strain_vol",
    "stress_delta",
    "stress_delta_flat",
    "stress_delta_prin_x",
    "stress_delta_prin_y",
    "stress_delta_prin_z",
    "stress_delta_min",
    "stress_delta_max",
    "stress_delta_mean",
    "density",
    "biot",
    "therm_coeff",
    "saturation",
    "pcap",
]


def permeability():
    """Get an array of the zone permeabilities."""
    return _get_extra("k")


def porosity():
    """Get an array of the zone porosities."""
    return _get_extra("phi")


def porosity_initial():
    """Get an array of the zone initial porosities."""
    return _get_extra("iphi")


def porosity_delta():
    """Get an array of the zone changes in porosity."""
    return _get_extra("dphi")


def pp():
    """
    Get an array of the zone pore pressures.

    Note
    ----
    Zone pore pressures in :mod:`itasca` are equivalent pore pressures scaled by Biot coefficients.

    """
    return _get_extra("pp")


def pp_equivalent():
    """Get an array of the zone equivalent pore pressures."""
    return _get_extra("pp_eq")


def pp_delta():
    """Get an array of the zone changes in pore pressure."""
    return _get_extra("dpp")


def temperature():
    """Get an array of the zone temperatures."""
    return _get_extra("temp")


def temperature_delta():
    """Get an array of the zone changes in temperature."""
    return _get_extra("dtemp")


def strain_vol():
    """Get an array of the zone volumetric strains."""
    return _get_extra("epsv")


def stress_delta():
    """Get an array of the zone changes in stress."""
    X = stress_delta_flat()[:, [0, 3, 5, 3, 1, 4, 5, 4, 2]]
    return X.reshape((len(X), 3, 3))


def stress_delta_flat():
    """
    Get an array of the zone changes in stress.

    The return value is a 2D array where the component ordering is xx, yy, zz, xy, yz,
    xz.

    """
    attributes = ["dsxx", "dsyy", "dszz", "dsxy", "dsyz", "dsxz"]
    return numpy.vstack([_get_extra(attribute) for attribute in attributes]).T


def stress_delta_prin_x():
    """Get an array of the x-component of the zone changes in principal stress."""
    return _get_extra("dsig1")


def stress_delta_prin_y():
    """Get an array of the y-component of the zone changes in principal stress."""
    return _get_extra("dsig2")


def stress_delta_prin_z():
    """Get an array of the z-component of the zone changes in principal stress."""
    return _get_extra("dsig3")


def stress_delta_min():
    """Get an array of the zone minimum changes in principal stress."""
    return stress_delta_flat()[:, :3].min(axis=1)


def stress_delta_max():
    """Get an array of the zone maximum changes in principal stress."""
    return stress_delta_flat()[:, :3].max(axis=1)


def stress_delta_mean():
    """Get an array of the zone average changes in stress."""
    return stress_delta_flat()[:, :3].mean(axis=1)


def density():
    """Get an array of the zone densities."""
    return _get_extra("rho")


def biot():
    """Get an array of the zone Biot coefficients."""
    return _get_extra("biot")


def therm_coeff():
    """Get an array of the zone volumetric thermal expansion coefficients."""
    return _get_extra("thexp")


def saturation(n_phase):
    """
    Get an array of the zone saturations for each phase.

    Parameters
    ----------
    n_phase: int
        Number of phases.

    """
    if not (isinstance(n_phase, int) and n_phase > 0):
        raise ValueError()
    return numpy.vstack([za.extra(key_to_slot["nph"] + i) for i in range(n_phase)]).T


def pcap(n_phase):
    """
    Get an array of the zone capillary pressures for each phase.

    Parameters
    ----------
    n_phase : int
        Number of phases.

    """
    if not (isinstance(n_phase, int) and n_phase > 0):
        raise ValueError()
    return numpy.vstack(
        [za.extra(key_to_slot["nph"] + n_phase + j) for j in range(n_phase - 1)]
    ).T


def _get_extra(attribute):
    """Get the zone extra data for the given attribute as an array."""
    return za.extra(key_to_slot[attribute])


def _set_permeability(data):
    """Set the zone permeabilities."""
    _set_extra("k", data)


def _set_porosity(data):
    """Set the zone porosities."""
    _set_extra("phi", data)


def _set_porosity_initial(data):
    """Set the zone initial porosities."""
    _set_extra("iphi", data)


def _set_porosity_delta(data):
    """Set the zone changes in porosities."""
    _set_extra("dphi", data)


def _set_pp(data):
    """Set the zone pore pressures."""
    _set_extra("pp", data)


def _set_pp_equivalent(data):
    """Set the zone equivalent pore pressures."""
    _set_extra("pp_eq", data)


def _set_pp_delta(data):
    """Set the zone changes in pore pressure."""
    _set_extra("dpp", data)


def _set_temperature(data):
    """Set the zone temperatures."""
    _set_extra("temp", data)


def _set_temperatura_delta(data):
    """Set the zone changes in temperature."""
    _set_extra("dtemp", data)


def _set_strain_vol(data):
    """Set the zone volumetric strains."""
    _set_extra("epsv", data)


def _set_stress_delta(data):
    """Set the zone changes in stress."""
    X = data.reshape((it.zone.count(), 9))[:, [0, 4, 8, 1, 5, 2]]
    _set_stress_delta_flat(X)


def _set_stress_delta_flat(data):
    """Set the zone changes in stress."""
    attributes = ["dsxx", "dsyy", "dszz", "dsxy", "dsyz", "dsxz"]
    for attribute, X in zip(attributes, data.T):
        _set_extra(attribute, X)


def _set_stress_delta_prin_x(data):
    """Set the x-component of the zone changes in principal stress."""
    _set_extra("dsig1", data)


def _set_stress_delta_prin_y(data):
    """Set the y-component of the zone changes in principal stress."""
    _set_extra("dsig2", data)


def _set_stress_delta_prin_z(data):
    """Set the z-component of the zone changes in principal stress."""
    _set_extra("dsig3", data)


def _set_density(data):
    """Set the zone densities."""
    _set_extra("rho", data)


def _set_biot(data):
    """Set the zone Biot coefficients."""
    _set_extra("biot", data)


def _set_therm_coeff(data):
    """Set the zone volumetric thermal expansion coefficients."""
    _set_extra("thexp", data)


def _set_saturation(data):
    """Set the zone saturations for each phase."""
    for i, X in enumerate(data.T):
        za.set_extra(key_to_slot["nph"] + i, X)


def _set_pcap(data):
    """Set the zone capillary pressures for each phase."""
    n_phase = data.shape[1] + 1
    for j, X in enumerate(data.T):
        za.set_extra(key_to_slot["nph"] + n_phase + j, X)


def _set_extra(attribute, data):
    """Set the zone extra data for the given attribute with an array."""
    za.set_extra(key_to_slot[attribute], data)
