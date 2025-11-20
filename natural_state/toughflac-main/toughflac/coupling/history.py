try:
    import itasca as it
    from itasca import zonearray as za
    from itasca import gridpointarray as gpa
except ImportError:
    pass

import numpy as np

from .._common import key_to_slot

__all__ = [
    "histsav",
]


def histsav(point, attribute, history_func, n_phase):
    """Save history output as function of TOUGH time in an array."""
    if attribute == "disp_mag":
        g = _get_gridpoint(point)
        return np.linalg.norm(g.disp())
    elif attribute == "disp_x":
        g = _get_gridpoint(point)
        return g.disp_x()
    elif attribute == "disp_y":
        g = _get_gridpoint(point)
        return g.disp_y()
    elif attribute == "disp_z":
        g = _get_gridpoint(point)
        return g.disp_z()
    elif attribute == "temp":
        z = _get_zone(point)
        return z.temp()
    elif attribute == "pp":
        z = _get_zone(point)
        return z.pp()
    elif attribute == "stress_xx":
        z = _get_zone(point)
        return z.stress()[0, 0]
    elif attribute == "stress_yy":
        z = _get_zone(point)
        return z.stress()[1, 1]
    elif attribute == "stress_zz":
        z = _get_zone(point)
        return z.stress()[2, 2]
    elif attribute == "stress_xy":
        z = _get_zone(point)
        return z.stress()[0, 1]
    elif attribute == "stress_yz":
        z = _get_zone(point)
        return z.stress()[1, 2]
    elif attribute == "stress_xz":
        z = _get_zone(point)
        return z.stress()[0, 2]
    elif attribute == "stress_prin_x":
        z = _get_zone(point)
        return z.stress_prin_x()
    elif attribute == "stress_prin_y":
        z = _get_zone(point)
        return z.stress_prin_y()
    elif attribute == "stress_prin_z":
        z = _get_zone(point)
        return z.stress_prin_z()
    elif attribute == "strain_xx":
        z = _get_zone(point)
        return z.strain()[0, 0]
    elif attribute == "strain_yy":
        z = _get_zone(point)
        return z.strain()[1, 1]
    elif attribute == "strain_zz":
        z = _get_zone(point)
        return z.strain()[2, 2]
    elif attribute == "strain_xy":
        z = _get_zone(point)
        return z.strain()[0, 1]
    elif attribute == "strain_yz":
        z = _get_zone(point)
        return z.strain()[1, 2]
    elif attribute == "strain_xz":
        z = _get_zone(point)
        return z.strain()[0, 2]
    elif attribute.startswith("extra_"):
        z = _get_zone(point)
        return z.extra(int(attribute.split("_")[-1]))
    elif attribute.startswith("prop_"):
        z = _get_zone(point)
        return z.prop("-".join(attribute.split("_")[1:]))
    elif attribute == "stress_delta_xx":
        z = _get_zone(point)
        return z.extra(key_to_slot["dsxx"])
    elif attribute == "stress_delta_yy":
        z = _get_zone(point)
        return z.extra(key_to_slot["dsyy"])
    elif attribute == "stress_delta_zz":
        z = _get_zone(point)
        return z.extra(key_to_slot["dszz"])
    elif attribute == "stress_delta_xy":
        z = _get_zone(point)
        return z.extra(key_to_slot["dsxy"])
    elif attribute == "stress_delta_yz":
        z = _get_zone(point)
        return z.extra(key_to_slot["dsyz"])
    elif attribute == "stress_delta_xz":
        z = _get_zone(point)
        return z.extra(key_to_slot["dsxz"])
    elif attribute == "stress_delta_xz":
        z = _get_zone(point)
        return z.extra(key_to_slot["dsxz"])
    elif attribute == "stress_delta_prin_x":
        z = _get_zone(point)
        return z.extra(key_to_slot["dsig1"])
    elif attribute == "stress_delta_prin_y":
        z = _get_zone(point)
        return z.extra(key_to_slot["dsig2"])
    elif attribute == "stress_delta_prin_z":
        z = _get_zone(point)
        return z.extra(key_to_slot["dsig3"])
    elif attribute == "temp_delta":
        z = _get_zone(point)
        return z.extra(key_to_slot["dtemp"])
    elif attribute == "pp_delta":
        z = _get_zone(point)
        return z.extra(key_to_slot["dpp"])
    elif attribute == "strain_vol":
        z = _get_zone(point)
        return z.extra(key_to_slot["epsv"])
    elif attribute == "pp_equivalent":
        z = _get_zone(point)
        return z.extra(key_to_slot["pp_eq"])
    elif attribute == "density":
        z = _get_zone(point)
        return z.extra(key_to_slot["rho"])
    elif attribute == "porosity":
        z = _get_zone(point)
        return z.extra(key_to_slot["phi"])
    elif attribute == "porosity_delta":
        z = _get_zone(point)
        return z.extra(key_to_slot["dphi"])
    elif attribute == "porosity_initial":
        z = _get_zone(point)
        return z.extra(key_to_slot["iphi"])
    # Alias for permeability_x (for backward compatibility)
    elif attribute == "permeability":
        z = _get_zone(point)
        return z.extra(key_to_slot["k"])[0]
    elif attribute == "permeability_x":
        z = _get_zone(point)
        return z.extra(key_to_slot["k"])[0]
    elif attribute == "permeability_y":
        z = _get_zone(point)
        return z.extra(key_to_slot["k"])[1]
    elif attribute == "permeability_z":
        z = _get_zone(point)
        return z.extra(key_to_slot["k"])[2]
    elif attribute == "biot":
        z = _get_zone(point)
        return z.extra(key_to_slot["biot"])
    elif attribute == "therm_coeff":
        z = _get_zone(point)
        return z.extra(key_to_slot["thexp"])
    elif attribute.startswith("saturation_"):
        z = _get_zone(point)
        i = int(attribute.split("_")[-1])
        if i > n_phase:
            raise ValueError()
        return z.extra(key_to_slot["nph"] + i - 1)
    elif attribute.startswith("pcap_"):
        z = _get_zone(point)
        j = int(attribute.split("_")[-1])
        if j >= n_phase:
            raise ValueError()
        return z.extra(key_to_slot["nph"] + n_phase + j - 1)
    else:
        z = _get_zone(point)
        try:
            return history_func[attribute](z)
        except KeyError:
            raise ValueError("Invalid history variable '{}'.".format(attribute))


def _get_zone(point):
    """Return zone given point coordinate (array-like) or ID (integer)."""
    return it.zone.find(point) if isinstance(point, int) else it.zone.near(point)


def _get_gridpoint(point):
    """Return grid point given point coordinate (array-like) or ID (integer)."""
    return (
        it.gridpoint.find(point) if isinstance(point, int) else it.gridpoint.near(point)
    )
