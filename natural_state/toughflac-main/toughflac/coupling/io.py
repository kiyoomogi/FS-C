"""
FLAC3D main Python module for TOUGH3-FLAC coupling.

Originally written in FISH by Jonny Rutqvist (LBNL), August 2005. Modified by Laura
Blanco Martin (LBNL), Fall 2012. Updated by Antonio Pio Rinaldi (SED/LBNL) for FLAC3D
v6, July 2018. Adapted and packaged into Python by Keurfon Luu (LBNL), July 2019.

"""

from __future__ import division, print_function, with_statement

import os

import numpy

from .. import model
from .. import zonearray as tza
from .history import histsav

try:
    import itasca as it
    from itasca import zonearray as za
    from itasca import gridpointarray as gpa
except ImportError:
    pass


__all__ = [
    "tough_flac",
    "flac_tough",
    "savefile",
    "extra_variables",
]


extra_variables = {
    "porosity": False,
    "porosity_delta": False,
    "pp": False,
    "pp_equivalent": False,
    "pp_delta": False,
    "temperature": False,
    "temperature_delta": False,
    "stress_delta": False,
    "stress_delta_prin": False,
    "density": False,
    "biot": False,
    "therm_coeff": False,
    "saturation": False,
    "pcap": False,
}


def ini_thm_save():
    """
    Function to save initial stresses, temperature and pressure.

    Note
    ----
    inistre, initemp and inipp are global variables.

    """
    global inistre, initemp, inipp
    inistre = numpy.hstack(
        (
            za.stress_flat(),  # Sxx, Syy, Szz, Sxy, Syz, Sxz
            [z.stress_prin() for z in it.zone.list()],  # S1, S2, S3
        )
    )
    initemp = za.temperature()
    inipp = numpy.array([z.pp() for z in it.zone.list()])


def del_THM(biot_func):
    """Function to calculate state changes, including changes in stress, temperature,
    and pressure relative to initial state."""
    global inistre, initemp, inipp
    if extra_variables["stress_delta"]:
        delstre = za.stress_flat() - inistre[:, :6]
        tza._set_stress_delta_flat(delstre)
    if extra_variables["stress_delta_prin"]:
        delstre = [z.stress_prin() for z in it.zone.list()] - inistre[:, 6:]
        tza._set_stress_delta_prin_x(delstre[:, 0])
        tza._set_stress_delta_prin_y(delstre[:, 1])
        tza._set_stress_delta_prin_z(delstre[:, 2])
    if extra_variables["temperature_delta"]:
        deltemp = za.temperature() - initemp
        tza._set_temperatura_delta(deltemp)
    if extra_variables["pp_delta"]:
        delpp = numpy.array([z.pp() for z in it.zone.list()]) - inipp
        tza._set_pp_delta(delpp)
    if extra_variables["biot"]:
        tza._set_biot(biot_update(biot_func))
    if extra_variables["therm_coeff"]:
        tza._set_therm_coeff(3.0 * thexp() * deltemp)


def savefile(filename=None, dirname=None, save_python=False):
    """Function to save FLAC state for later print at times defined in TOUGH input
    file."""
    global tought, tstep, nph
    if save_python:
        python_variables = {
            "tought": tought,
            "tstep": tstep,
            "nph": nph,
        }
    else:
        python_variables = None

    if tstep > 1:
        global inistre, initemp, inipp
        if save_python:
            python_variables.update(
                {"inistre": inistre, "initemp": initemp, "inipp": inipp,}
            )

    if not filename:
        if tought < 3600.0:
            filename = "f{:.3f}s.f3sav".format(tought)
        elif tought < 86400.0:
            filename = "f{:.3f}h.f3sav".format(tought / 3600.0)
        elif tought < 31536000.0:
            filename = "f{:.3f}d.f3sav".format(tought / 86400.0)
        else:
            filename = "f{:.3f}y.f3sav".format(tought / 31536000.0)

    filename = "{}/{}".format(dirname, filename) if dirname else filename
    model.save(filename, python_variables)


def zerodisp():
    """Loop over grid points and zero displacements."""
    gpa.set_disp(numpy.zeros((it.gridpoint.count(), 3)))


def histfile(history, history_func, dirname=None):
    """
    Print history array into a file.

    Note
    ----
    In Python < 3.7, dictionaries do not preserve order of keys. History array are saved as CSV files with header. Points in lists are ordered as defined.

    """
    global tought, tstep, nph

    for filename, hist in history.items():
        # History file name
        filename = "{}/{}".format(dirname, filename) if dirname else filename

        # Current file records
        if tstep == 1:
            header = [h for k, v in hist.items() for h in ["{}".format(k)] * len(v)]
            records = ["tought, {}\n".format(", ".join(header))]
        else:
            with open("{}.csv".format(filename), "r") as f:
                records = f.readlines()

        # New record
        record = [
            histsav(point, k, history_func, nph) for k, v in hist.items() for point in v
        ]
        record = ", ".join(str(i) for i in record)
        record = "{}, {}\n".format(tought, record)

        # Append if new time step, overwrite otherwise
        if len(records) == tstep:
            records += [record]
        else:
            records[-1] = record

        # Write file
        with open("{}.csv".format(filename), "w") as f:
            f.write("".join(records))


def tough_flac(biot_func, save_python, savedir, thermal):
    """Function to read parameters from a TOUGH exported file 'TOU_FLA' and interpolates
    parameter values from zone centers (TOUGH nodes) to gridpoints (FLAC3D grid points)
    and fix the new temperature at those grid points."""
    # Read TOUGH data
    print("\n\n--- Reading TOUGH data")
    nzone = it.zone.count()
    with open("TOU_FLA", "rb") as f:
        dt1 = numpy.dtype(
            [
                ("tought", 'float64'),
                ("tstep", 'int32'),
                ("nph", 'int32'),
                ("nk", 'int32'),
                ("ideos", 'int32'),
                ("savefi", 'int32'),
                ("ie_thm", 'int32'),
            ]
        )
        data_h = numpy.fromfile(f, dtype=dt1, count=1)
        data = numpy.fromfile(f, dtype='float64')
        ncol = 2 * data_h[0][2] + 7
        nrow = len(data) // ncol
        data = data.reshape((nrow, ncol))
        data = data[:nzone]
    global tought, tstep, nph, savefi, ie_thm
    tought, tstep, nph, _, _, savefi, ie_thm = data_h[0]
    it.fish.set("tought", tought)
    it.fish.set("tstep", int(tstep))

    # Pretty TOUGH time and time step
    if tought < 3600.0:
        time_str = "{} seconds".format(int(tought))
    elif tought < 86400.0:
        time_str = "{:.2f} hours".format(tought / 3600.0)
    elif tought < 31536000.0:
        time_str = "{:.2f} days".format(tought / 86400.0)
    else:
        time_str = "{:.2f} years".format(tought / 31536000.0)
    print("--- Time step {}: {}".format(tstep, time_str))

    # Initialization
    if tstep == 1:
        for z, X, alpha in zip(it.zone.list(), data, biot_update(biot_func)):
            z.set_pp(X[2 * nph + 2] * alpha)
            if thermal:
                z.set_temp(X[1])
        if extra_variables["porosity_delta"]:
            tza._set_porosity_initial(data[:, 2 * nph + 1])

    # Assign extra variables
    tza._set_permeability(data[:, 2 * nph + 4 :])
    if extra_variables["pp"]:
        tza._set_pp(data[:, 0])
    if extra_variables["temperature"]:
        tza._set_temperature(data[:, 1])
    if extra_variables["porosity"]:
        tza._set_porosity(data[:, 2 * nph + 1])
    if extra_variables["pp_equivalent"]:
        tza._set_pp_equivalent(data[:, 2 * nph + 2])
    if extra_variables["density"]:
        tza._set_density(data[:, 2 * nph + 3])
    if extra_variables["porosity_delta"]:
        tza._set_porosity_delta(data[:, 2 * nph + 1] - tza.porosity_initial())
    if extra_variables["saturation"]:
        tza._set_saturation(data[:, 2 : 2 + nph])
    if extra_variables["pcap"]:
        tza._set_pcap(data[:, 2 + nph : 1 + 2 * nph])

    # Assign pore pressure and temperature
    for z, X, alpha in zip(it.zone.list(), data, biot_update(biot_func)):
        z.set_pp(X[2 * nph + 2] * alpha)
        if thermal:
            z.set_temp(X[1])

    # Change in THM parameters
    if tstep > 1:
        del_THM(biot_func)

    # Save file
    if savefi:
        savefile(dirname=savedir, save_python=save_python)

    return tought, tstep


def flac_tough(permeability_func, history_func, biot_func, history, savedir):
    """Function to export parameters such as stress/strain to file 'fla_tou'."""
    global ie_thm, tstep

    # Set all displacements and strain to zero if first short time step
    if tstep == 1:
        zerodisp()
        ini_thm_save()
        del_THM(biot_func)

    # Volumetric strain
    #for debugging and testing:
    #tza._set_strain_vol(
    #    1.0e-4
    #    * numpy.int_(
    #        numpy.round(numpy.trace(za.strain(), axis1=1, axis2=2) * 1.0e5) / 10.0
    #    )
    #)
    tza._set_strain_vol(numpy.transpose(numpy.trace(za.strain(), axis1=1, axis2=2)))

    # Permeability
    permeability = tza.permeability()
    porosity = numpy.zeros(it.zone.count())
    for group, func in permeability_func.items():
        mask = za.in_group(group)
        permeability[mask], porosity[mask] = func(mask)

    # Define outputs
    #data_h = [it.zone.count(), 0, 0, it.threads()]
    data_h = numpy.array([it.zone.count(), 0, 0, it.threads()], dtype=numpy.int32)
    if ie_thm == 1:
        #ft = numpy.column_stack((permeability, porosity,))
        ft = numpy.column_stack((
                 numpy.array(permeability, dtype=numpy.float64),
                 numpy.array(porosity, dtype=numpy.float64),
             ))
    elif ie_thm == 2:
        #ft = numpy.column_stack(
        #    (permeability, bulk(), tza.strain_vol(), biot_update(biot_func),)
        #)
        ft = numpy.column_stack((
                 numpy.array(permeability, dtype=numpy.float64),
                 numpy.array(bulk(), dtype=numpy.float64),
                 numpy.array(tza.strain_vol(), dtype=numpy.float64),
                 numpy.array(za.fluid_prop('biot', 1.0), dtype=numpy.float64)
             ))

    else:
        ft = permeability

    # Write FLAC data
    print("--- Writing FLAC data")
    with open("fla_tou", "wb") as f:
        numpy.array(data_h).tofile(f)
        ft.tofile(f)

    # Save history variables
    if history:
        histfile(history, history_func, dirname=savedir)


def biot_update(biot_func):
    """Function to update Biot's coefficient for each zone."""
    if biot_func:
        return biot_func()
    else:
        return numpy.ones(it.zone.count())


def bulk():
    """Function to update bulk for each zone."""
    return za.prop_scalar("bulk", 0.0)


def density():
    """Function to update density for each zone."""
    return za.prop_scalar("density", -1.0e9)


def thexp():
    """Function to update thermal expansion for each zone."""
    return za.prop_scalar("thexp", 0.0)
