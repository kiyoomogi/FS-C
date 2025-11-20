from functools import wraps

import numpy

from .._common import key_to_slot

try:
    import itasca as it
except ImportError:
    pass

__all__ = [
    "Zone",
]


def flacmethod(func):
    """Decorate methods from :class:`itasca.Zone`."""

    @wraps(func)
    def decorator(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AttributeError:
            raise AttributeError(
                "Current version of FLAC3D does not support method '{}'.".format(func.__name__)
            )

    return decorator


class Zone(object):

    def __init__(self, zone):
        """
        toughflac Zone.

        This class does not inherit from :class:`itasca.zone.Zone`. Do not use.

        Parameters
        ----------
        zone : itasca.zone.Zone
            Input zone to wrap.
        
        """
        self._zone = zone

        excludes = {attr for attr in dir(self) if not attr.startswith("__")}
        attributes = [attr for attr in dir(zone) if not (attr.startswith("__") or attr in excludes)]
        for attribute in attributes:
            setattr(self, attribute, getattr(zone, attribute))

    def _get_extra(self, attribute):
        """Get the zone extra data for the given attribute."""
        return self._zone.extra(key_to_slot[attribute])

    def _set_extra(self, attribute, data):
        """Set the zone extra data for the given attribute."""
        self._zone.set_extra(key_to_slot[attribute], data)

    def permeability(self):
        """
        Get zone's permeability.
        
        Returns
        -------
        float or array_like
            Zone's permeability.
        
        """
        return self._get_extra("k")

    def porosity(self):
        """
        Get zone's porosity.
        
        Returns
        -------
        float
            Zone's porosity.
        
        """
        return self._get_extra("phi")

    def porosity_initial(self):
        """
        Get zone's initial porosity.
        
        Returns
        -------
        float
            Zone's initial porosity.
        
        """
        return self._get_extra("iphi")

    def porosity_delta(self):
        """
        Get zone's change in porosity.
        
        Returns
        -------
        float
            Zone's change in porosity.
        
        """
        return self._get_extra("dphi")

    def pp(self, source="tough"):
        """
        Get zone's pore pressure.

        Parameters
        ----------
        source : str ('tough' or 'flac'), default 'tough'
            Source of pore pressure value.

        Returns
        -------
        float
            Zone's pore pressure.
        
        """
        if source == "tough":
            return self._get_extra("pp")
        elif source == "flac":
            return self._zone.pp()
        else:
            raise ValueError()

    def pp_equivalent(self):
        """
        Get zone's equivalent pore pressure.

        Returns
        -------
        float
            Zone's equivalent pore pressure.
        
        """
        return self._get_extra("pp_eq")

    def pp_delta(self):
        """
        Get zone's change in pore pressure.

        Returns
        -------
        float
            Zone's change in pore pressure.
        
        """
        return self._get_extra("dpp")

    def temperature(self):
        """
        Get zone's temperature.

        Returns
        -------
        float
            Zone's temperature
        
        """
        return self._get_extra("temp")

    def temperature_delta(self):
        """
        Get zone's change in temperature.

        Returns
        -------
        float
            Zone's change in temperature.
        
        """
        return self._get_extra("dtemp")

    def strain_vol(self):
        """
        Get zone's volumetric strain.

        Returns
        -------
        float
            Zone's volumetric strain.
        
        """
        return self._get_extra("epsv")

    def stress_delta(self):
        """
        Get zone's change in stress (tensor).

        Returns
        -------
        array_like
            Zone's change in stress (tensor).
        
        """
        X = self.stress_delta_flat()[[0, 3, 5, 3, 1, 4, 5, 4, 2]]
        return X.reshape((3, 3))

    def stress_delta_flat(self):
        """
        Get zone's change in stress (flat).

        Returns
        -------
        array_like
            Zone's change in stress (flat).
        
        """
        attributes = ["dsxx", "dsyy", "dszz", "dsxy", "dsyz", "dsxz"]
        return numpy.array([self._get_extra(attribute) for attribute in attributes])

    def stress_delta_prin_x(self):
        """
        Get the x-component of the zone's change in principal stress.

        Returns
        -------
        float
            x-component of the zone's change in principal stress.
        
        """
        return self._get_extra("dsig1")

    def stress_delta_prin_y(self):
        """
        Get the y-component of the zone's change in principal stress.

        Returns
        -------
        float
            y-component of the zone's change in principal stress.
        
        """
        return self._get_extra("dsig2")

    def stress_delta_prin_z(self):
        """
        Get the z-component of the zone's change in principal stress.

        Returns
        -------
        float
            z-component of the zone's change in principal stress.
        
        """
        return self._get_extra("dsig3")

    def stress_delta_min(self):
        """
        Get zone's minimum change in principal stress.

        Returns
        -------
        float
            Zone's minimum change in principal stress.
        
        """
        return self.stress_delta_flat().min()

    def stress_delta_max(self):
        """
        Get zone's maximum change in principal stress.

        Returns
        -------
        float
            Zone's maximum change in principal stress.
        
        """
        return self.stress_delta_flat().max()

    def stress_delta_mean(self):
        """
        Get zone's average change in principal stress.

        Returns
        -------
        float
            Zone's average change in principal stress.
        
        """
        return self.stress_delta_flat().mean()

    def set_permeability(self, data):
        """
        Set zone's permeability.

        Parameters
        ----------
        data : float or array_like
            Zone's permeability.
        
        """
        self._set_extra("k", data)

    def set_porosity(self, data):
        """
        Set zone's porosity.

        Parameters
        ----------
        data : float
            Zone's porosity.
        
        """
        self._set_extra("phi", data)
    
    def set_porosity_initial(self, data):
        """
        Set zone's initial porosity.

        Parameters
        ----------
        data : float
            Zone's initial porosity.
        
        """
        self._set_extra("iphi", data)

    def set_porosity_delta(self, data):
        """
        Set zone's change in porosity.

        Parameters
        ----------
        data : float
            Zone's change in porosity.
        
        """
        self._set_extra("dphi", data)

    def set_pp(self, data):
        """
        Set zone's pore pressure.

        Parameters
        ----------
        data : float
            Zone's pore pressure.
        
        """
        self._set_extra("pp", data)

    def set_pp_equivalent(self, data):
        """
        Set zone's equivalent pore pressure.

        Parameters
        ----------
        data : float
            Zone's equivalent pore pressure.
        
        """
        self._set_extra("pp_eq", data)

    def set_pp_delta(self, data):
        """
        Set zone's change in pore pressure.

        Parameters
        ----------
        data : float
            Zone's change in pore pressure.
        
        """
        self._set_extra("dpp", data)

    def set_strain_vol(self, data):
        """
        Set zone's volumetric strain.

        Parameters
        ----------
        data : float
            Zone's volumetric strain.
        
        """
        self._set_extra("epsv", data)

    @flacmethod
    def adjacent_zones(self):
        """
        Get adjacent zones.

        Return a tuple of the zones adjacent to this zone via a topologically perfect face. If there is no face adjacent to face i the ith element of the tuple will be None.

        Returns
        -------
        tuple of toughflac.zone.Zone
            Zone's adjacent zones.
        
        """
        return tuple(Zone(z) if z is not None else None for z in self._zone.adjacent_zones())

    @flacmethod
    def aspect(self):
        """
        Get the measure of a zone's aspect ratio.
        
        Values near zero indicate a zone with a large aspect ratio. This is defined as the minimum ratio of smallest to largest edge length among adjacent edges of a zone.

        Returns
        -------
        float
            Zone's aspect ratio.
        
        """
        return self._zone.aspect()

    @flacmethod
    def condition(self):
        """
        Get the zone condition number.
        
        This is a general value indication how geometrically well formed the zone is. A value of 1.0 indicates a perfect cubical zone. A value of 0.0 indicates an unusable zone.

        Returns
        -------
        float
            Zone's condition number.
        """
        return self._zone.condition()

    @flacmethod
    def copy_to(self, destination):
        """
        Copy the zone state information from this zone to the destination zone.

        Parameters
        ----------
        destination : itasca.zone.Zone or toughflac.zone.Zone
            Destination zone.
        
        """
        if isinstance(destination, it.zone.Zone):
            self._zone.copy_to(destination)
        elif isinstance(destination, Zone):
            self._zone.copy_to(destination._zone)
        else:
            raise TypeError()

    @flacmethod
    def create_interface_element(self, face_index, interface_name):
        """
        Create new interface elements attached to the face given by face_index.
        
        face_index starts at 0. The newly created interface elements will be added to the interface given by interface_name. If this interface does not exist it will be created. The return value is the number of interface elements created. A value of zero is returned if the face already has an interface.

        Parameters
        ----------
        face_index : int
            Index of face.
        interace_name : str
            Name of interface.
        
        Returns
        -------
        int
            Number of interface elements created.
        
        """
        return self._zone.create_interface_element(face_index, interface_name)

    @flacmethod
    def density(self):
        """
        Get the zone zone density.
        
        Returns
        -------
        float
            Zone's density.
        
        """
        return self._zone.density()

    @flacmethod
    def extra(self, slot):
        """Get the zone extra data in the given slot."""
        return self._zone.extra(slot)

    @flacmethod
    def face_areas(self):
        """
        Get the area of the faces of this zone.
        
        Returns
        -------
        tuple of floats
            Zone's face areas.
        
        """
        return self._zone.face_areas()

    @flacmethod
    def face_extra(self, face_index, extra_index):
        """
        Get the value of the extra variable at the index extra_index associated with face_index.
        
        face_index starts at zero, extra_index starts at 1.

        Parameters
        ----------
        face_index : int
            Index of face.
        extra_index : int
            Index of extra.
        
        """
        return self._zone.face_extra(face_index, extra_index)
