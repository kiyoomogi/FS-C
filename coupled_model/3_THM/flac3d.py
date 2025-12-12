from toughflac.coupling import extra, run
from toughflac.coupling.permeability import rutqvist2002
from toughflac.coupling.permeability import constant
from toughflac.coupling.permeability import hsiung2005
import itasca as it

from toughflac.coupling import extra, run
from itasca import zonearray as za
import toughflac.zonearray as tza
import itasca as it
import numpy as np
import csv 

# FLAC3D solver parameters
model_save = "tf_in.f3sav"
deterministic = False
damping = "combined"
mechanical_ratio = 1.0e-7
n_threads = 20
thermal = True

# Output parameters
savedir = "f3out"
save_python = False

# Extra variables to save
extra["porosity"] = True
extra["porosity_delta"] = True
extra["pp"] = True
extra["pp_equivalent"] = True
extra["pp_delta"] = True
extra["temperature"] = True
extra["temperature_delta"] = True
extra["stress_delta"] = True
extra["stress_delta_prin"] = True
extra["density"] = True
extra["biot"] = True
extra["therm_coeff"] = True
extra["saturation"] = True
extra["pcap"] = True

def stress_on_plane(tough_time):
    """
    Function to calculate effective normal stress on plane 
    """
    global init_pp, init_ss, init_sn

    # Unpack time info
    tought, tstep = tough_time

    # Get all zones once and reuse
    zones = list(it.zone.list())
    num_zones = len(zones)

    # Normal vector to the plane
    n = np.asarray([0.50432, -0.645501, 0.573576])

    # Pore pressure per zone
    pp = np.asarray([z.pp() for z in zones])

    # Effective stress tensor per zone (3x3)
    eff_stress = np.array([-z.stress_effective() for z in zones])  # shape (N, 3, 3)
    if eff_stress.shape[0] != num_zones:
        raise ValueError("Stress array must be of the same length as number of zones.")

    # Traction vector on the plane for each zone: T_i = σ_eff_i · n
    T = np.einsum('ijk,k->ij', eff_stress, n)  # shape (N, 3)

    # Normal stress: sn = T · n
    sn = np.einsum('ij,j->i', T, n)  # shape (N,)

    # Shear stress magnitude: |T|^2 - sn^2
    ss = np.sqrt(np.einsum('ij,ij->i', T, T) - sn**2)

    # Store initial values at first timestep
    if tstep == 1:
        init_pp, init_ss, init_sn = pp, ss, sn

    # Boolean mask for 'FAULT' cells
    fault_bool = za.in_group('FAULT')  # shape (N,)
    valid_idx = np.where(fault_bool)[0]  # indices of FAULT cells

    # Subset values for FAULT cells
    pp_injec = pp[valid_idx]
    sn_injec = sn[valid_idx]
    ss_injec = ss[valid_idx]

    # Principal stresses for FAULT cells
    prin_stresses_all = np.linalg.eigvalsh(eff_stress)  # shape (N, 3)
    prin_stresses = prin_stresses_all[valid_idx]        # shape (N_fault, 3)

    # If you only want max principal stress, uncomment:
    # s1_injec = prin_stresses[:, -1]

    # File path
    csv_file_path = r"/home/manuus/Desktop/FS-C/model/traction_file.csv"

    # Text mode for Python 3 CSV
    mode = "w" if tstep == 1 else "a"
    with open(csv_file_path, mode, newline="") as csvfile:
        writer = csv.writer(csvfile)

        # Header on first timestep
        if tstep == 1:
            writer.writerow([
                "Time_Step",
                "Zone_ID",
                "Pore_Pressure(MPa)",
                "Normal_Stress(MPa)",
                "Shear_Stress(MPa)",
                "Principal_Stresses(MPa)",  # or "S1(MPa)" if you pick one
                "TOUGH_time"
            ])

        # Write data for each FAULT cell
        for i, zone_id in enumerate(valid_idx):
            writer.writerow([
                tstep,
                zone_id,
                pp_injec[i],
                sn_injec[i],
                ss_injec[i],
                prin_stresses[i],  # or prin_stresses[i, -1] for max principal
                tought
            ])

    return


# Extra Python functions as a list of callables
python_func_tough = ()  # Before mechanical analysis
python_func_flac = () #(stress_on_plane,)  # After mechanical analysis

# Extra FISH functions as a list of strings
fish_func_tough = ()  # Before mechanical analysis
fish_func_flac = ()  # After mechanical analysis


n_fault   = np.array([0.50432, -0.645501, 0.573576])  # unit normal to plane
psi_fault = 5.0    # dilation angle [deg] – adjust as you like
a_fault   = 5e-12    # inverse stiffness – adjust as you like
sig0_val  = 4.965794e6  # Pa, initial normal effective stress

permeability_func = {
    "FAULT": lambda g: hsiung2005(
        g,
        k0   = 5.0e-17,
        phi0 = 0.14,
        n    = n_fault,
        psi  = psi_fault,
        a    = a_fault,
        # make sig0 an array of length = number of zones in this group
        sig0 = np.full(g.sum(), sig0_val),
        joint=True,
    ),
}

#permeability_func = {
#    "FAULT": lambda g: rutqvist2002(
#        g,
#        k0   = 1.0e-16,
#        phi0 = 0.12,
#    ),
#}


# History variables
history_func = {}
history_attributes = [
    "temp",
    "pp",
    "stress_prin_x",
    "stress_prin_y",
    "stress_prin_z",
    "stress_xx",
    "stress_yy",
    "stress_zz",
]
history = {
    "hist1": {
        "disp_z": [
            [0.0, 0.0, 0.0],
            [0.0, 0.0, -1200.0],
            [0.0, 0.0, -1300.0],
            [0.0, 0.0, -1500.0],
        ],
    },
    "hist2": {k: [[0.0, 0.0, -1450.0]] for k in history_attributes},
    "hist3": {k: [[0.0, 0.0, -1290.0]] for k in history_attributes},
}


if __name__ == "__main__":
    run(
        model_save=model_save,
        deterministic=deterministic,
        damping=damping,
        mechanical_ratio=mechanical_ratio,
        n_threads=n_threads,
        thermal=thermal,
        permeability_func=permeability_func,
        callback_tough=python_func_tough,
        callback_flac=python_func_flac,
        history_func=history_func,
        history=history,
        savedir=savedir,
        save_python=save_python,
    )
