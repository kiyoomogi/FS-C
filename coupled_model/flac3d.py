from toughflac.coupling import extra, run
from toughflac.coupling.permeability import constant
from toughflac.coupling.permeability import nuus2025
from toughflac.coupling.permeability import rinaldi2019
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



def printer_function(
    tough_time,
    group_name="FAULT",
    *,
    joint=True,
):
    tought, tstep = tough_time

    group = za.in_group(group_name)  # boolean mask in global zonearray order
    if not np.any(group):
        print(f"[printer] no zones in group {group_name}")
        return

    # --- Read permeability currently stored in the model
    k_all = tza.permeability()       # (nzone_total, 3)
    k = k_all[group, :]              # (nzone_group, 3)

    # --- Read strains for this group
    suffix = "-joint" if joint else ""
    strain_shear   = za.prop_scalar(f"strain-shear-plastic{suffix}")[group]
    strain_tensile = za.prop_scalar(f"strain-tensile-plastic{suffix}")[group]
    failed_mask = strain_shear > 0.0

    # --- pore pressure for this group (Pa)
    edz_group = za.in_group("EDZ")
    pp_group = tza.pp()[edz_group]

    # --- Read porosity 
    phi = tza.porosity()[edz_group] 

    # ============================================================
    #   Existing diagnostics (your original stuff)
    # ============================================================

    k_col = k[:, 0]
    idx_sorted = np.argsort(k_col)[::-1]
    idx_second = int(idx_sorted[1]) if idx_sorted.size > 1 else int(idx_sorted[0])

    if np.any(failed_mask):
        failed_idx = np.nonzero(failed_mask)[0]
        idx_min_failed = int(failed_idx[np.argmin(k_col[failed_idx])])
    else:
        idx_min_failed = int(idx_sorted[-1])

    #pp_sorted = np.sort(pp_group)
    #pp_second = float(pp_sorted[-2]) if pp_sorted.size >= 2 else float(pp_sorted[-1])

    print(f"=== printer debug ({group_name}) tstep={tstep} t={tought} ===")
    print("porosity (highest)    :", float(np.amax(phi)))
    print("k (2nd highest)       :", k[idx_second, :])
    print("k (min, failed only)        :", k[idx_min_failed, :])
    print("strain_shear @min k failed  :", float(strain_shear[idx_min_failed]))
    print("Index (2nd max k)     :", idx_second)
    print("Index (min k failed)  :", idx_min_failed)
    print("strain_tens @2nd max  :", float(strain_tensile[idx_second]))
    print("strain_shear @2nd max :", float(strain_shear[idx_second]))
    print("strain_tens @min fail :", float(strain_tensile[idx_min_failed]))
    print("strain_shear@min fail :", float(strain_shear[idx_min_failed]))
    print("pp edz                : {:.3f} MPa".format(np.amax(pp_group * 1e-6)))
    print("failed zones          : {} / {}".format(np.count_nonzero(failed_mask), strain_shear.size))
    print("==============================================")

# Extra Python functions as a list of callables
python_func_tough = ()  # Before mechanical analysis
python_func_flac = (printer_function,) #(stress_on_plane,)  # After mechanical analysis

# Extra FISH functions as a list of strings
fish_func_tough = ()  # Before mechanical analysis
fish_func_flac = ()  # After mechanical analysis

k0_fault = np.array([5.0e-17, 5.0e-17, 1.0e-17], dtype=float)
k0_clay = np.array([5.0e-19, 5.0e-19, 1.0e-19], dtype=float)
k0_edz = np.array([1.0e-10, 1.0e-10, 1.0e-10], dtype=float)
k0_bnd = np.array([1.0e-18, 1.0e-18, 1.0e-18], dtype=float)

a_fault = 500

permeability_func = {
    "FAULT": lambda g: rinaldi2019(
        g,
        k0 = k0_fault,
        phi0 = 0.14,
        n = 1.0,
        w = 1.8,
        br = 22e-6,     #was 20e-6
        bmax = 38e-6,  #was 500e-6
        bshear_max = 100e-6,
        alpha = 1.0, 
        n_vector = np.array([0.47, -0.60, 0.64]),
        psi = 10,
        joint = True, 

    ),
    "EDZ": lambda g: constant(
        g,
        k0=k0_edz,
        phi0=0.95,
    ),
    "CLAY": lambda g: constant(
        g,
        k0=k0_clay,
        phi0=0.12,
    ),
    "BNDTO": lambda g: constant(
        g,
        k0=np.tile(k0_bnd, (g.sum(), 1)),
        phi0=0.12,   
    ),
    "BNDBO": lambda g: constant(
        g,
        k0=np.tile(k0_bnd, (g.sum(), 1)),
        phi0=0.12,    
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
