manuus@geomech01:/opt/itascasoftware/subscription/python310/lib/python3.10/site-packages/toughflac/coupling$ cat permeability.py
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
    "rinaldi2014",
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

    # Pore pressure
    pp = tza.pp()

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
    br = (12.0 * k0[:,0] / phi0) ** 0.5
    c = 0.5 * (-1.0 + (1.0 + 4.0 * sig0 * a / br) ** 0.5) / sig0
    dphi = strain_tensile + strain_shear * numpy.tan(numpy.deg2rad(psi))

    # Permeability factor
    kf = a / c / (1.0 + c * sig) / br + dphi / phi0

    # New porosity and permeability arrays
    phi = phi0 + dphi
    #k = numpy.einsum("ij, i-> ij", k0, kf * kf * kf)

    k = k0 * kf**3
    print(numpy.shape(k), "shape k0: ", numpy.shape(k0), " shape kf: ", numpy.shape(kf))
    # Use the first column (k is isotropic if k0 is isotropic)
    k_col = k[:, 0]

    idx_max = numpy.argmax(k_col)
    k_max   = k_col[idx_max]

    print("=== Hsiung2005 debug (FAULT group) ===")
    print("Max k       :", k_max)
    print("Index       :", idx_max)
    print("k0 at idx   :", k0[idx_max, :])
    print("phi0        :", phi0)
    print("phi at idx  :", phi[idx_max])
    print("sig  at idx :", sig[idx_max])
    print("sig0 at idx :", sig0[idx_max])
    print("strain_tens :", strain_tensile[idx_max])
    print("strain_shear:", strain_shear[idx_max])
    print("psi (deg)   :", psi)
    print("a           :", a)
    print("br at idx   :", br[idx_max])
    print("c  at idx   :", c[idx_max])
    print("kf at idx   :", kf[idx_max])
    print("pp max      :", numpy.amax(pp)*1e-6), " MPa"
    print("======================================")


    return k, phi

@permeability
def rinaldi2014(
    group,
    k0,
    phi0,
    phir=0.0,
    ke=22.2,
    phie=5.0e-8,
    pp_threshold=4.18e6,
    pp_injec_threshold=4.18e6,
):
    # --- 1. Normal effective stress on the plane (ALL zones) ---
    zones = list(it.zone.list())
    n = numpy.asarray([0.50432, -0.645501, 0.573576])

    # Effective stress tensor for all zones: (N_all, 3, 3)
    sigma_eff_all = numpy.array([-z.stress_effective() for z in zones])

    # Traction & normal stress for all zones
    T_all = numpy.einsum("ijk,k->ij", sigma_eff_all, n)   # (N_all, 3)
    sigma_n_all = numpy.einsum("ij,j->i", T_all, n)       # (N_all,)

    # Restrict to group
    sigma_n_g = sigma_n_all[group]                        # (nzone,)

    # --- 2. Store initial σ′ₙ (for ALL zones) once and reuse ---
    if not hasattr(rinaldi2014, "sigma_n0_all"):
        # First call: store initial σ′ₙ for every zone
        rinaldi2014.sigma_n0_all = sigma_n_all.copy()

    sigma_n0_all = rinaldi2014.sigma_n0_all               # (N_all,)
    sigma_n0_g   = sigma_n0_all[group]                    # (nzone,)

    nzone = sigma_n_g.shape[0]

    # --- 3. k0, phi0 for the group ---
    # k0 is already (nzone, 3) because of the decorator
    k0_g = k0                                            # (nzone, 3)

    # phi0 is scalar → make a (nzone,) array
    phi0_g = numpy.full(nzone, phi0, dtype=float)        # (nzone,)

    # --- 4. Strain terms and parameters ---
    e_pts = za.prop_scalar("strain-tensile-plastic-1")[group]   # (nzone,)
    e_pss = za.prop_scalar("strain-shear-plastic-1")[group]     # (nzone,)

    dil = numpy.deg2rad(1.0)
    a   = 1e3

    # --- 5. Rinaldi 2014 formula ---
    # Use, e.g., only the first permeability direction for the geometric factor
    root_phi = numpy.sqrt(phi0_g / (12.0 * k0_g[:, 0]))        # (nzone,)

    # c = (-1 + sqrt(1 + 4 σ'_n a sqrt(phi0/(12 k0)))) / (2 σ'_{n0})
    c = (-1.0 + numpy.sqrt(1.0 + 4.0 * sigma_n_g * a * root_phi)) / (2.0 * sigma_n0_g)

    term1 = a / (c * (c * sigma_n_g + 1.0)) * root_phi         # (nzone,)
    term2 = (e_pts + e_pss * numpy.tan(dil)) / phi0_g          # (nzone,)

    # Permeability factor per zone
    factor = (term1 + term2) ** 3                              # (nzone,)

    # Scale the 3D permeability per zone; factor[:,None] → (nzone, 1)
    k   = k0_g * factor[:, None]                               # (nzone, 3)
    phi = phi0_g                                               # (nzone,)

    # Debug output
    idx_min = numpy.argmin(sigma_n_g)   # returns an integer index

    # Use that index to extract corresponding values
    sigma_n_min   = sigma_n_g[idx_min]
    sigma_n0_min  = sigma_n0_g[idx_min]
    e_pts_min     = e_pts[idx_min]
    e_pss_min     = e_pss[idx_min]
    k_min         = k[idx_min, :]       # this is a 3-component vector

    print("Index of min normal stress      =", idx_min)
    print("Min current normal stress       =", sigma_n_min)
    print("Initial normal stress at that   =", sigma_n0_min)
    print("Permeability at that (k1,k2,k3) =", k_min)
    print("Tensile strain at that          =", e_pts_min)
    print("Shear strain at that            =", e_pss_min)

    return k, phi
