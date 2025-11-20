from __future__ import division

from functools import wraps

import numpy

from .. import zonearray as tza
from ..utils import normal_stress

try:
    import itasca as it
    from itasca import zonearray as za
except ImportError:
    pass


__all__ = [
    "permeability",
    "constant",
    "chin2000",
    "rutqvist2002",
    "minkoff2004",
    "hsiung2005",
]


def permeability(func):
    """Decorate permeability model functions."""

    @wraps(func)
    def decorator(group, k0, phi0, *args, **kwargs):
        # Number of zones in current group
        nzone = group.sum()

        # Dimensionality of input permeability
        ndim = numpy.ndim(k0)

        # Check that inputs are correctly defined
        isscalar = ndim == 0 and not isinstance(k0, str)
        isarray = isinstance(k0, (list, tuple, numpy.ndarray))
        if not (isscalar or isarray):
            raise ValueError()
        if isarray:
            if ndim not in {1, 2}:
                raise ValueError()
            if not (len(k0) == 3 if ndim == 1 else numpy.shape(k0) == (nzone, 3)):
                raise ValueError()
        if not (not isinstance(phi0, str) and numpy.ndim(phi0) == 0):
            raise ValueError()

        # Reshape permeability as a (nzone, 3) array
        k0 = (
            numpy.full((nzone, 3), k0)
            if ndim == 0
            else numpy.tile(k0, (nzone, 1))
            if ndim == 1
            else k0
        )

        # Update permeability and check outputs
        k, phi = func(group, k0, phi0, *args, **kwargs)
        if not (isinstance(k, numpy.ndarray) and numpy.shape(k0) == (nzone, 3)):
            raise ValueError()
        if not (isinstance(phi, numpy.ndarray) and numpy.shape(phi) == (nzone,)):
            raise ValueError()

        return k, phi

    return decorator


@permeability
def constant(group, k0, phi0):
    """
    No mechanical-induced permeability change.

    Parameters
    ----------
    group : array_like
        Mask array for queried group.
    k0 : scalar
        Stress-free permeability.
    phi0 : scalar
        Stress-free porosity.

    Returns
    -------
    array_like
        New permeability array for queried group.
    array_like
        New porosity array for queried group.

    Note
    ----
    This function is only provided for completeness. It is recommended to directly use permeability model identifier 1 in block 'FLAC'.

    """
    # Number of zones in group
    n = group.sum()

    # New porosity and permeability arrays
    phi = numpy.full(n, phi0, dtype=numpy.float64)
    k = numpy.asarray(k0)

    return k, phi


@permeability
def chin2000(group, k0, phi0, ke=5.6):
    """
    After Chin et al. (2000).

    Parameters
    ----------
    group : array_like
        Mask array for queried group.
    k0 : scalar
        Stress-free permeability.
    phi0 : scalar
        Stress-free porosity.
    ke : scalar, optional, default 5.6
        Permeability exponent.

    Returns
    -------
    array_like
        New permeability array for queried group.
    array_like
        New porosity array for queried group.

    """
    # Volumetric strain
    strain_vol = tza.strain_vol()[group]

    # New porosity and permeability arrays
    phi = 1.0 - (1.0 - phi0) * numpy.exp(-strain_vol)
    kf = numpy.power(phi / phi0, ke)
    k = numpy.einsum("ij, i-> ij", k0, kf)

    return k, phi


@permeability
def rutqvist2002(group, k0, phi0, phir=0.0, ke=22.2, phie=5.0e-8):
    """
    After Rutqvist and Tsang (2002).

    Parameters
    ----------
    group : array_like
        Mask array for queried group.
    k0 : scalar
        Stress-free permeability.
    phi0 : scalar
        Stress-free porosity.
    phir : scalar, optional, default 0.0
        Residual porosity.
    ke : scalar, optional, default 22.2
        Permeability exponent.
    phie : scalar, optional, default 5.0e-8
        Porosity exponent.

    Returns
    -------
    array_like
        New permeability array for queried group.
    array_like
        New porosity array for queried group.

    """
    # Pore pressure
    pp = numpy.array([z.pp() for z, g in zip(it.zone.list(), group) if g])

    # Mean effective stress
    stress_mean = za.stress_flat()[group, :3].mean(axis=1) + pp

    # New porosity and permeability arrays
    phi = (phi0 - phir) * numpy.exp(phie * stress_mean) + phir
    kf = numpy.exp(ke * (phi / phi0 - 1.0))
    k = numpy.einsum("ij, i-> ij", k0, kf)

    return k, phi


@permeability
def minkoff2004(group, k0, phi0, ke):
    """
    After Minkoff et al. (2004).

    Parameters
    ----------
    group : array_like
        Mask array for queried group.
    k0 : scalar
        Stress-free permeability.
    phi0 : scalar
        Stress-free porosity.
    ke : scalar
        Permeability exponent.

    Returns
    -------
    array_like
        New permeability array for queried group.
    array_like
        New porosity array for queried group.

    """
    # Volumetric strain
    strain_vol = tza.strain_vol()[group]

    # New porosity and permeability arrays
    phi = numpy.full_like(strain_vol, phi0)
    kf = numpy.exp(ke * strain_vol)
    k = numpy.einsum("ij, i-> ij", tza.permeability()[group], kf)

    return k, phi


@permeability
def hsiung2005(group, k0, phi0, n, psi, a, sig0, joint=False):
    """
    After Hsiung et al. (2005).

    Parameters
    ----------
    group : array_like
        Mask array for queried group.
    k0 : scalar
        Stress-free permeability.
    phi0 : scalar
        Stress-free porosity.
    n : array_like
        Unit normal vector (3 components).
    psi : scalar
        Dilation angle.
    a : scalar
        Inverse of stiffness.
    sig0 : array_like
        Initial normal effective stress. Compressions are positive.
    joint : bool, optional, default False
        If `True`, shear and tensile strains are read from joint values.

    Returns
    -------
    array_like
        New permeability array for queried group.
    array_like
        New porosity array for queried group.

    """
    # Plastic shear strain and tensile
    suffix = "-joint" if joint else ""
    strain_shear = za.prop_scalar("strain-shear-plastic{}".format(suffix))[group]
    strain_tensile = za.prop_scalar("strain-tensile-plastic{}".format(suffix))[group]

    # Effective stress
    stress = numpy.array(
        [-z.stress_effective() for z, g in zip(it.zone.list(), group) if g]
    )

    # Effective normal stresses
    sig = normal_stress(stress, n)

    # Porosity change
    br = (12.0 * k0 / phi0) ** 0.5
    c = 0.5 * (-1.0 + (1.0 + 4.0 * sig0 * a / br) ** 0.5) / sig0
    dphi = strain_tensile + strain_shear * numpy.tan(numpy.deg2rad(psi))

    # Permeability factor
    kf = a / c / (1.0 + c * sig) / br + dphi / phi0

    # New porosity and permeability arrays
    phi = phi0 + dphi
    k = numpy.einsum("ij, i-> ij", k0, kf * kf * kf)

    return k, phi
