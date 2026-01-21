@permeability
def rinaldi2019(group, k0, phi0, n, w, br, bmax, alpha, n_vector, joint=False):
    """
    After Rinaldi et al. (2019)

    Parameters
    ----------
    group : array-like
        Mask array for queried group
    k0 : scalar
  Stress-free permeability (actually initial permeability)
    phi0 : scalar
  Stress-free porosity (not used)
    n : integer
        Number of fractures within the width w of the fracture zone
    w : scalar
        Width of the fracture zone
    br : scalar
        Residual fracture aperture
    bmax : scalar
        Maximum fracture aperture
    alpha : alpha
        Stress-dependency parameter (in MPa^-1)
    n_vector : array_like
        Unit normal vector (3 components). Unit normal vector of the fault.
    joint : bool, optional, default False
        If `True` shear and tensile strains as well as dilation angle are read from joint values

    Returns
    -------
    array_like
        New permeability array for queried group
    array_like
        New porosity array for queried group
    """
    # read the time step from the global variable defined before
    from .io import tstep
    if tstep==1:
        global eff_n_stress_init, k0_, phi0_
        # get initial effective normal stress
        #stress_tensor_init = numpy.array([-z.stress_effective() for z, g in zip(it.zone.list(), group) if g])
        #pp_init = numpy.array([z.pp() for z, g in zip(it.zone.list(), group) if g])
        #eff_n_stress_init = normal_stress(stress_tensor_init, n_vector)
        # get initial permeability
        k0_ = za.extra(11) # this was the initial line! 

        # get initial porosity
        phi0_ = za.extra(13)
        # Alternatively:
        # get the pore pressure
        #pp = numpy.array([z.pp() for z, g in zip(it.zone.list(), group) if g])
        # or:
        pp = za.extra(15)
        # get stress tensor
        stresses = za.stress_flat()
        stress_tensor = []
        for i in range(len(stresses)):
            stress_tensor.append(numpy.asarray([[stresses[i][0], stresses[i][3], stresses[i][5]],
                                                [stresses[i][3], stresses[i][1], stresses[i][4]],
                                                [stresses[i][5], stresses[i][4], stresses[i][2]]]))
        stress_tensor = numpy.asarray(stress_tensor)

        # get the normal effective stress from the stress tensor and the normal to the fault plane subtracted by the pore pressure
        eff_n_stress_init = normal_stress(-stress_tensor, n_vector) - pp # negative stress tensor for compression

        #raise ValueError()

    # get array of cell ids within group (this stopped working at some point instead of using group)
    #group_ids = numpy.where(za.in_group(group)==True)[0]

    # get plastic shear and tensile strain
    suffix = "-joint" if joint else ""
    strain_shear = za.prop_scalar("strain-shear-plastic{}".format(suffix))[group]
    strain_tensile = za.prop_scalar("strain-tensile-plastic{}".format(suffix))[group]
    # and the dilation angle
    psi = za.prop_scalar("dilation{}".format(suffix))[group]

    # get pore pressure
    #pp = numpy.array([z.pp() for z, g in zip(it.zone.list(), group) if g])
    # or:
    pp = za.extra(15)[group]

    # get effective normal stress
    # first get the stress tensor(s)
    stresses = za.stress_flat()[group]
    stress_tensor = []
    for i in range(len(stresses)):
        stress_tensor.append(numpy.asarray([[stresses[i][0], stresses[i][3], stresses[i][5]],
                                            [stresses[i][3], stresses[i][1], stresses[i][4]],
                                            [stresses[i][5], stresses[i][4], stresses[i][2]]]))
    stress_tensor = numpy.asarray(stress_tensor)

    # get the normal effective stress from the stress tensor and the normal to the fault plane subtracted by the pore pressure
    eff_n_stress = normal_stress(-stress_tensor, n_vector) - pp # negative stress tensor for compression
    # or:
    #stress_tensor = numpy.array([-z.stress_effective() for z, g in zip(it.zone.list(), group) if g])
    #eff_n_stress = normal_stress(stress_tensor, n_vector)

    # calculate the fracture spacing
    sf = n/w

    # calculate the initial fracture aperture
    #eff_n_stress_i = sign0 * (1.0e6)
    alpha = alpha / (1.0e6)
    bi = br + bmax * numpy.exp(-alpha*eff_n_stress_init[group])

    # calculate the fracture aperture shear shift
    bshear = strain_shear * numpy.tan(numpy.deg2rad(psi)) / sf

    # calculate the fracture aperture by tensile strain
    bop = strain_tensile * w

    # calculate the elastic fracture aperture
    bel = br + bmax * numpy.exp(-alpha*eff_n_stress)

    # calculate total fracture aperture
    b = bel + bshear + bop
   # b = bel

    # calculate porosity change due to plastic deformation
    dphi = strain_tensile + strain_shear * numpy.tan(numpy.deg2rad(psi))

    # calculate new porosity array
    phi = phi0_[group] + dphi

    # calculate new permeability array
    kf = b / bi # ratio of fracture aperture vs initial fracture aperture
    k = numpy.einsum("ij, i->ij", k0_[group], kf * kf * kf)

    # ---- cap maximum permeability ----
    k_max = 5e-12
    k = numpy.clip(k, a_min=None, a_max=k_max)


#    print("=== aperure values in permeability function ===")
#    print("max b_el = ", numpy.amax(bel))
#    print("max b = ", numpy.amax(b))
#    print("min b = ", numpy.amin(b))
#    print("=== === === ===")

    return k, phi