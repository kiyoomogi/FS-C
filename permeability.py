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
        #k = func(group, k0, phi0, *args, **kwargs)
        if not (isinstance(k, numpy.ndarray) and numpy.shape(k0) == (nzone, 3)):
            raise ValueError()
        if not (isinstance(phi, numpy.ndarray) and numpy.shape(phi) == (nzone,)):
            raise ValueError()

        return k , phi

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
    print("min strain: ",numpy.amin(strain_vol), "max strain: ", numpy.amax(strain_vol))
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
    print(numpy.amax(phi), numpy.amin(phi))
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

@permeability
def nuus(group, k0, phi0, phir=0.0, ke=22.2, phie=5.0e-8, pp_threshold=4.18e6, pp_injec_threshold=4.18e6):
    """
    Custom permeability and porosity function with a threshold pressure.
    In this function, the permeability can ONLY increase.


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
    pp_threshold : scalar, optional, default 4.1e6
        Threshold pore pressure for permeability and porosity change.
    a1 : scalar, optional, default 0.125
        Permeability coefficient for the first equation.
    a2 : scalar, optional, default 152
        Permeability coefficient for the second equation.

    Returns
    -------
    array_like
        New permeability array for queried group.
    array_like
        New porosity array for queried group.
    """

    # a1, a2
    a1 = 0.27
    a2 = 19

    # Pore pressure
    group_injec = it.zonearray.in_group("INJEC")
    pp_injec = tza.pp()[group_injec]
    sat_injec = tza.saturation(2)[group_injec]

    pp = tza.pp()[group]
    poros = tza.porosity()[group]
    perm = tza.permeability()[group]
    pcap = tza.pcap(2)[group].ravel()

    # Mean effective stress
    stress_mean = za.stress_flat()[group, :3].mean(axis=1) + pp

    pg = numpy.full_like(pp, pcap)

    # Update pg where pcap < 0.0
    pg[pcap < 0.0] = pp[pcap < 0.0] - pcap[pcap < 0.0]

    # Initialize new porosity array
    phi = numpy.full_like(pp, phi0)

    # Apply the threshold condition for porosity
    above_threshold2 = pg >= pp_threshold
    below_threshold2 = pg < pp_threshold
    below_threshold1 = pg < pp_injec_threshold

    phi_above_thres = pp >= pp_threshold
    phi_below_thres = pp < pp_threshold

    k_xu = numpy.full_like(k0, 1e-20)

    if not hasattr(nuus, "threshold_crossed"):
        nuus.threshold_crossed = False
    if numpy.amax(pp_injec) >= pp_injec_threshold:
        nuus.threshold_crossed = True

    if nuus.threshold_crossed:
        k_below_threshold = (1 + a1 * pg[below_threshold2][:, None] * 1e-6) * k_xu[below_threshold2, 0:2]
        k_above_threshold = (a2 * (pg[above_threshold2][:, None] * 1e-6 - pp_threshold * 1e-6) + 1 + (a1 * pp_threshold * 1e-6)) * k_xu[above_threshold2, 0:2]

        # Ensure k_xu[above_threshold2, 0:2] can only increase
        k_above_threshold = numpy.maximum(k_above_threshold, perm[above_threshold2, 0:2])

        k_xu[below_threshold2, 0:2] = k_below_threshold
        k_xu[above_threshold2, 0:2] = k_above_threshold

        phi[phi_below_thres] = (poros[phi_below_thres] - phir) * numpy.exp(1 * 5e-5 * phie * pp[phi_below_thres]) + phir
        phi[phi_above_thres] = (poros[phi_above_thres] - phir) * numpy.exp(4 * 5e-5 * phie * pp[phi_above_thres]) + phir

        print('threshold initiation')
    else:
        phi[below_threshold1] = (poros[below_threshold1] - phir) * numpy.exp(1 * 5e-5 * phie * pg[below_threshold1]) + phir
        k_xu[below_threshold1, 0:2] = (1 + a1 * pg[below_threshold1][:, None] * 1e-6) * k_xu[below_threshold1, 0:2]  # added a 0 here!
        print('no threshold initiation')

    k_xu[:, 2] = 0.3e-20

    k = k_xu
    print("max injec pressure:", numpy.amax(pp_injec))
    print("max/min permeability: ", numpy.amax(k), numpy.amin(k))
    print("max/min porosity: ", numpy.amax(phi[phi != 0.596]), numpy.amin(phi))

    return k, phi


@permeability
def nuus2(group, k0, phi0, phir=0.0, ke=22.2, phie=5.0e-8, pp_threshold=4.18e6, pp_injec_threshold = 4.18e6):
    """
    Custom permeability and porosity function with a threshold pressure.
    This is the standard permeability function with gas pressure as input variable.

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
    pp_threshold : scalar, optional, default 4.1e6
        Threshold pore pressure for permeability and porosity change.
    a1 : scalar, optional, default 0.125
        Permeability coefficient for the first equation.
    a2 : scalar, optional, default 152
        Permeability coefficient for the second equation.

    Returns
    -------
    array_like
        New permeability array for queried group.
    array_like
        New porosity array for queried group.
    """

    #a1, a2
    a1 = 0.005
    a2 = 60
    a2_z = 10

    # Pore pressure
    group_injec = it.zonearray.in_group("INJEC")
    pp_injec = tza.pp()[group_injec]
    sat_injec = tza.saturation(2)[group_injec]

    pp = tza.pp()[group]
    poros = tza.porosity()[group]
    perm = tza.permeability()[group]
    pcap = tza.pcap(2)[group].ravel()

    # Mean effective stress
    stress_mean = za.stress_flat()[group, :3].mean(axis=1) + pp

    pg = numpy.full_like(pp, pcap)

    # Update pg where pcap < 0.0
    pg[pcap < 0.0] = pp[pcap < 0.0] - pcap[pcap < 0.0]

    # Initialize new porosity array
    phi_xu = numpy.full_like(pp, phi0)
    phi = numpy.full_like(pp, phi0)

    strain_vol = tza.strain_vol()[group]
    strain_shear = za.prop_scalar("strain-shear-plastic")[group]
    strain_tensile = za.prop_scalar("strain-tensile-plastic")[group]
    print("shear: ",numpy.amax(strain_shear), "tensile: ", numpy.amax(strain_tensile))
    print("shear shape: ",numpy.shape(strain_shear), "tensile shape: ", numpy.shape(strain_tensile))
    # Apply the threshold condition for porosity
    above_threshold2 = pg >= pp_threshold
    below_threshold2 = pg < pp_threshold
    below_threshold1 = pg < pp_injec_threshold 
    phi_above_thres = pp >= pp_threshold
    phi_below_thres = pp < pp_threshold


    k_xu = numpy.full_like(k0, 3e-20)
    k_xu[:,2] = 0.6e-20

    if not hasattr(nuus2, "threshold_crossed"):
        nuus2.threshold_crossed = False
    if numpy.amax(pp_injec) >= pp_injec_threshold:
        nuus2.threshold_crossed = True

    threshold_crossed = []
    if numpy.amax(pp_injec) >= pp_threshold:
        threshold_crossed.append(True)

    if nuus2.threshold_crossed:
        k_xu[below_threshold2, 0:2] = (1 + a1 * pg[below_threshold2][:, None] * 1e-6) * k_xu[below_threshold2, 0:2]
        k_xu[above_threshold2, 0:2] = (a2 * (pg[above_threshold2][:, None] * 1e-6  - pp_threshold * 1e-6) + 1 + (a1 * pp_threshold * 1e-6)) * k_xu[above_threshold2, 0:2]
        k_xu[above_threshold2, 2] = (a2_z * (pg[above_threshold2] * 1e-6  - pp_threshold * 1e-6) + 1 + (a1 * pp_threshold * 1e-6)) * k_xu[above_threshold2, 2]


        phi[phi_below_thres] = (phi_xu[phi_below_thres] - phir) * numpy.exp(1*5e-6 * phie * pg[phi_below_thres]) + phir #was 5e-5 before
        phi[phi_above_thres] = (phi_xu[phi_above_thres] - phir) * numpy.exp(1*5e-6 *phie * pg[phi_above_thres]) + phir #maybe 0.0003 works best

        print('threshold initation')
    else:
        phi[below_threshold1] = (phi_xu[below_threshold1] - phir) * numpy.exp(5e-6 * phie * pg[below_threshold1]) + phir
        k_xu[below_threshold1, 0:2] = (1 + a1 * pg[below_threshold1][:, None] * 1e-6) * k_xu[below_threshold1, 0:2]  #added a 0 here !
        print('no threshold initiation')


    k_xu[:,2] = 0.6e-20

    k = k_xu
    print("max injec pressure:", numpy.amax(pp_injec))
    print("max/min permeability: ", numpy.amax(k), numpy.amin(k))
    print("max/min porosity: ", numpy.amax(phi[phi != 0.644]), numpy.amin(phi))

    return k, phi

@permeability
def nuus_strain(group, k0, phi0, phir=0.0, ke=22.2, phie=5.0e-8, pp_threshold=4.18e6, pp_injec_threshold = 4.18e6):
    """
    Custom permeability and porosity function with a threshold pressure.
    This is the standard permeability function with gas pressure as input variable.

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
    pp_threshold : scalar, optional, default 4.1e6
        Threshold pore pressure for permeability and porosity change.
    a1 : scalar, optional, default 0.125
        Permeability coefficient for the first equation.
    a2 : scalar, optional, default 152
        Permeability coefficient for the second equation.

    Returns
    -------
    array_like
        New permeability array for queried group.
    array_like
        New porosity array for queried group.
    """
    file_path = r"C:\Users\matthijs\simple_model\coupled\strain_values.txt"


    #a1, a47000
    b1x = 5000   #plastic permeability modifier for x-direction
    b1y = 5000   #plastic permeability modifier for y-direction (no really necessary since all horizontal permeability is assigned "x-direction"-value)
    b1z = 1000    #plastic permeability modifier for z-direction
    b2 = 20       #elastic permeability modifier dilation
    b3 = 5        #elastic permeability modifier compaction

    # Pore pressure
    group_injec = it.zonearray.in_group("INJEC") #boolean for INJEC elements
    pp_injec = tza.pp()[group_injec]             #find pore pressure for all INJEC elements 

    pp = tza.pp()[group]                         #pore pressure for materials chosen in flac3d.py (in this case only "CLAY ")
    poros = tza.porosity()[group]                #porosity ""
    perm = tza.permeability()[group]             #permeability ""
    pcap = tza.pcap(2)[group].ravel()            #capillary pressure ""

    # Mean effective stress
    stress_mean = za.stress_flat()[group, :3].mean(axis=1) + pp
    pg = numpy.full_like(pp, pcap)                        #set up array for gas pressure (here with just capillary pressure)

    # Update pg where pcap < 0.0
    pg[pcap < 0.0] = pp[pcap < 0.0] - pcap[pcap < 0.0]    #calculate the gas pressure by subtracting capillary pressure from total pore pressure

    # Initialize new porosity array
    phi_xu = numpy.full_like(pp, phi0)                    #set up array for porosity with initial porosity values 

    k_xu = numpy.full_like(k0, k0[0,0])                   #set up array for permeability with initial permeability values  
    k_xu[:,2] = k0[0,0] / 5                               #set the permeability in z-direction to 0.2e-20 m2

    strain_vol1 = tza.strain_vol()[group]                                           #get volumetric strain for material chosen in flac3d.py (in this case only "CLAY ")
    #strain_vol = numpy.column_stack((strain_vol1,strain_vol1))
    strain_shear1 = za.prop_scalar("strain-shear-plastic")[group]                   #get plastic shear strain ""
    #strain_shear = numpy.column_stack((strain_shear1,strain_shear1))
    strain_tensile1 = za.prop_scalar("strain-tensile-plastic")[group]               #get plastic tensile strain ""
    #strain_tensile = numpy.column_stack((strain_tensile1,strain_tensile1))

    strain_shear1_joint = za.prop_scalar("strain-shear-plastic-joint")[group]               #get joint plastic shear strain ""
    #strain_shear_joint = numpy.column_stack((strain_shear1_joint,strain_shear1_joint))
    strain_tensile1_joint = za.prop_scalar("strain-tensile-plastic-joint")[group]           #get joint plastic tensile strain ""
    #strain_tensile_joint = numpy.column_stack((strain_tensile1_joint,strain_tensile1_joint))

    k_xu[:,0] = numpy.where(strain_shear1_joint > 0, k0[0,0]*100, k_xu[:,0])
    print(k0[0,0]*100)
    #equation to update permeability. the first value is the maximum boundary of the permeability. 
    k_xu[:,0] = numpy.minimum(1e-16, 10**(numpy.where(strain_vol1 < 0, (b3) * strain_vol1, (b2) * strain_vol1)) * numpy.exp((b1x) * (strain_shear1_joint + strain_tensile1_joint)) * k_xu[:, 0])
    k_xu[:,1] = numpy.minimum(5e-17, 10**(numpy.where(strain_vol1 < 0, (b3) * strain_vol1, (b2) * strain_vol1)) * numpy.exp((b1y) * (strain_shear1_joint + strain_tensile1_joint)) * k_xu[:, 1])
    k_xu[:,2] = numpy.minimum(1e-17, 10**(numpy.where(strain_vol1 < 0, (b3) * strain_vol1, (b2) * strain_vol1)) * numpy.exp((b1z) * (strain_shear1_joint + strain_tensile1_joint)) * k_xu[:, 2])
    

    phi = (phi_xu - phir) * numpy.exp(1*5e-6 * phie * pg) + phir #update porosity, but currently update minimally 
    k = k_xu
    print "max injec pressure:", (numpy.amax(pp_injec))
    print "max/min permeability: ", numpy.amax(k), numpy.amin(k)
    print "max/min porosity: ", numpy.amax(phi), numpy.amin(phi)


    return k, phi

@permeability
def rinaldi2014(
    group,
    k0,                  # initial κ0 (scalar or array)
    phi0,                # initial porosity (scalar or array)
    phir=0.0,
    ke=22.2,
    phie=5.0e-8,
    pp_threshold=4.18e6,
    pp_injec_threshold=4.18e6,
):
    """
    Permeability update according to Rinaldi et al. (2014).
    `group` is typically a zone mask / indices where this applies.
    """


    # --- 1. Normal effective stress on the plane ---
    zones = list(it.zone.list())
    # Normal vector to the plane
    n = numpy.asarray([0.50432, -0.645501, 0.573576])
    # Full effective stress tensor per zone (N, 3, 3)
    sigma_eff = numpy.array([-z.stress_effective() for z in zones])
    # Traction on the plane: T_i = σ_eff_i · n   -> shape (N, 3)
    T = numpy.einsum("ijk,k->ij", sigma_eff, n)
    # Normal effective stress: σ'_n = T · n     -> shape (N,)
    sigma_n = numpy.einsum("ij,j->i", T, n)
    # Restrict to the group if `group` is a mask / indices
    sigma_n_g = sigma_n[group]

    # --- 2. Store initial σ'_n once and reuse every call ---
    if not hasattr(rinaldi2014, "sigma_n0"):
        # First call: store initial σ'_n for this group
        rinaldi2014.sigma_n0 = sigma_n_g.copy()
    sigma_n0_g = rinaldi2014.sigma_n0

    # --- 3. Build k0, phi0 arrays for the group ---
    # k0 and phi0 may be scalars or arrays; broadcast them to sigma_n_g's shape
    k0_g   = k0
    phi0_g = numpy.full_like(sigma_n, phi0)[group]

    # --- 4. Strain terms and parameters ---
    e_pts = za.prop_scalar("strain-tensile-plastic-1")[group]  # plastic normal strain
    e_pss = za.prop_scalar("strain-shear-plastic-1")[group]    # plastic shear strain
    dil = numpy.deg2rad(1.0)   # dilation angle ψ in radians
    a   = 1e8               # empirical constant ~ 1/K

    # --- 5. Rinaldi 2014 formula ---
    root_phi = numpy.sqrt(phi0_g / (12.0 * k0_g))
    # c = (-1 + sqrt(1 + 4 σ'_n a sqrt(phi0/(12 k0)))) / (2 σ'_{n0})
    c = (-1.0 + numpy.sqrt(1.0 + 4.0 * sigma_n_g * a * root_phi)) / (2.0 * sigma_n0_g)

    term1 = a / (c * (c * sigma_n_g + 1.0)) * root_phi
    term2 = (e_pts + e_pss * numpy.tan(dil)) / phi0_g

    k = k0_g * (term1 + term2) ** 3
    phi = phi0_g
    print("shape k = ",numpy.shape(k))
    print("shape phi = ",numpy.shape(phi))

    return k, phi 
