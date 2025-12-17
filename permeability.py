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
    "nuus2025",
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

                print("ndim:", ndim)
                print("nzone (decorator):", nzone)
                print("k0 type:", type(k0))
                print("k0 shape:", getattr(k0, "shape", None))
                print("len(k0):", len(k0))

                
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
    """

    # Pore pressure
    pp = tza.pp()

    # Plastic shear strain and tensile
    suffix = "-joint" if joint else ""
    strain_shear = za.prop_scalar("strain-shear-plastic{}".format(suffix))[group]
    strain_tensile = za.prop_scalar("strain-tensile-plastic{}".format(suffix))[group]

    # Effective stress tensor for grouped zones
    stress = numpy.array(
        [-z.stress_effective() for z, g in zip(it.zone.list(), group) if g]
    )

    # Effective normal stresses on plane n
    sig = normal_stress(stress, n)   # shape (nzone,)

    # ----- Porosity change -----
    br = (12.0 * k0[:, 0] / phi0) ** 0.5
    dphi = strain_tensile + strain_shear * numpy.tan(numpy.deg2rad(psi))

    # ----- Two possible c-values (± in the square root) -----
    # sqrt term
    disc = numpy.sqrt(1.0 + 4.0 * sig0 * a / br)

    # c_plus = (-1 + sqrt(...)) / (2 sig0)
    c_plus  = 0.5 * (-1.0 + disc) / sig0
    # c_minus = (-1 - sqrt(...)) / (2 sig0)
    c_minus = 0.5 * (-1.0 - disc) / sig0

    # ----- Permeability factor kf for both branches -----
    # kf = a / (c * (1 + c*sig) * br) + dphi / phi0
    kf_plus  = a / (c_plus  * (1.0 + c_plus  * sig) * br) + dphi / phi0
    kf_minus = a / (c_minus * (1.0 + c_minus * sig) * br) + dphi / phi0

    # ----- New porosity -----
    phi = phi0 + dphi

    # ----- Compute k for each branch and choose the larger -----
    # Raw updated permeability (scalar per zone) for each branch
    k_temp_plus  = k0[:, 0] * (kf_plus  ** 3)
    k_temp_minus = k0[:, 0] * (kf_minus ** 3)

    # Per-zone max of the two branches
    k_temp = numpy.maximum(k_temp_plus, k_temp_minus)

    k_temp = numpy.abs(k_temp)

    # Upper cap only (no lower bound at k0 anymore)
    k_max_cap = 5e-13
    k_temp = numpy.minimum(k_temp, k_max_cap)

    # Make it isotropic (3 components equal)
    k_temp = k_temp.reshape(-1, 1)
    k = numpy.concatenate((k_temp, k_temp, k_temp), axis=1)

    # For debug / max search
    k_col = k[:, 0]
    idx_sorted  = numpy.argsort(k_col)[::-1]
    idx_max     = idx_sorted[0]
    idx_second  = idx_sorted[1]
    idx_min     = idx_sorted[-1]
    k_max       = k_col[idx_max]
    k_second    = k_col[idx_second]

    print("=== Hsiung2005 debug (FAULT group) ===")
    print("Max k 2      :", k[idx_second, :])
    print("Min k        :", k[idx_min, :])
    print("Index       :", idx_second)
    print("k0 at idx   :", k0[idx_second, :])
    print("phi0        :", phi0)
    print("phi at idx  :", phi[idx_second])
    print("sig  at idx :", sig[idx_second])
    print("sig0 at idx :", sig0[idx_second])
    print("strain_tens :", strain_tensile[idx_second])
    print("strain_shear:", strain_shear[idx_second])
    print("psi (deg)   :", psi)
    print("a           :", a)
    print("br at idx   :", br[idx_second])
    print("c+ at idx   :", c_plus[idx_second])
    print("c- at idx   :", c_minus[idx_second])
    print("kf+ at idx  :", kf_plus[idx_second])
    print("kf- at idx  :", kf_minus[idx_second])
    print("pp max      :", numpy.amax(pp)*1e-6, " MPa")
    print("======================================")

    return k, phi

@permeability
def nuus2025(group, k0, phi0, a,k_jump_factor, joint=False):
    """
    Simple strain-driven permeability model (Nuus 2025).

    k = k0 * exp(a * eps_eq)

    where eps_eq is an 'equivalent' plastic strain built from
    tensile and shear plastic strains on the fault.

    Parameters
    ----------
    group : array_like
        Mask array for queried group.
    k0 : array_like, shape (nzone, 3)
        Initial permeability tensor (from decorator).
    phi0 : scalar
        Initial porosity.
    n, psi, sig0 : unused in this simplified model.
        Kept only for API compatibility.
    a : scalar
        Sensitivity of permeability to equivalent plastic strain.
        Larger a -> faster permeability growth with strain.
    joint : bool, optional
        If True, read joint plastic strains; otherwise zone plastic strains.
    """

    # --- Plastic shear and tensile strain ---
    suffix = "-joint" if joint else ""
    strain_shear   = za.prop_scalar("strain-shear-plastic{}".format(suffix))[group]
    strain_tensile = za.prop_scalar("strain-tensile-plastic{}".format(suffix))[group]
    failed_mask = strain_shear > 0.0      # or > threshold if you prefer

    # --- Equivalent plastic strain eps_eq ---
    # eps_eq = sqrt( eps_tens^2 + (2/3)*gamma_shear^2 )
    eps_eq = numpy.sqrt(
        strain_tensile**2 + (2.0 / 3.0) * strain_shear**2
    )

    # --- Permeability update: k_scalar = k0 * exp(a * eps_eq) ---
    # --- build multiplicative factor per zone (nzone,)
    mult = numpy.exp(a * eps_eq)
    mult[failed_mask] *= k_jump_factor

    # --- apply to each component of k0 (preserves anisotropy), result (nzone, 3)
    k = k0 * mult[:, None]

    # Always use non-negative permeability (component-wise)
    k = numpy.abs(k)

    # Cap permeability (component-wise)
    k_max_cap = 1.0e-12
    k = numpy.minimum(k, k_max_cap)

    # Porosity: simplest choice -> constant phi0 for all zones
    nzone = group.sum()
    phi = numpy.full(nzone, phi0, dtype=float)

    # ----------------- DEBUG BLOCK -----------------
    k_col = k[:, 0]   # representative component

    idx_sorted  = numpy.argsort(k_col)[::-1]
    idx_max     = idx_sorted[0]
    idx_second  = idx_sorted[1]

    # --- minimum k among FAILED zones only ---
    if numpy.any(failed_mask):
        # indices of failed zones in this group
        failed_indices = numpy.nonzero(failed_mask)[0]        # e.g. [3, 7, 12, ...]
        # corresponding k values
        k_failed = k_col[failed_indices]
        # index (within k_failed) of the minimum k
        rel_idx_min_failed = numpy.argmin(k_failed)
        # map back to the original indexing
        idx_min_failed = failed_indices[rel_idx_min_failed]
    else:
        # no failed zones → fall back to global minimum
        idx_min_failed = idx_sorted[-1]

    # Pore pressure for this group only
    pp_all   = tza.pp()          # all zones
    pp_group = pp_all[group]     # just FAULT (or whatever group)
    pp_sorted = numpy.sort(pp_group)

    if pp_sorted.size >= 2:
        pp_max      = pp_sorted[-1]
        pp_second   = pp_sorted[-2]
    else:
        pp_max    = pp_sorted[-1]
        pp_second = pp_sorted[-1]

    # -------- failure statistics (based on shear plastic strain) --------
    # Define "failed" zones as those with positive plastic shear strain
    failed_mask = strain_shear > 0.0

    n_failed = numpy.count_nonzero(failed_mask)
    n_total  = strain_shear.size

    # Optionally: fraction of failed zones
    frac_failed = n_failed / n_total if n_total > 0 else 0.0

    print(f"=== nuus2025 debug ({group_name}) ===")
    print("k (2nd highest)       :", k[idx_second, :])
    print("k (min, failed only)  :", k[idx_min_failed, :])
    print("Index (2nd max k)     :", idx_second)
    print("Index (min k failed)  :", idx_min_failed)
    print("k0 at idx (2nd max)   :", k0[idx_second, :])
    print("phi0                  :", phi0)
    print("phi at idx (2nd max)  :", phi[idx_second])
    print("strain_tens @2nd max  :", strain_tensile[idx_second])
    print("strain_shear @2nd max :", strain_shear[idx_second])
    print("strain_tens @min fail :", strain_tensile[idx_min_failed])
    print("strain_shear@min fail :", strain_shear[idx_min_failed])
    print("a (sensitiv.)         :", a)
    print("pp 2nd max            : {:.3f} MPa".format(pp_second * 1e-6))
    print("failed zones          : {} / {}"
          .format(numpy.count_nonzero(failed_mask), strain_shear.size))
    print("====================================")

    return k, phi
