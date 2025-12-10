from toughflac.coupling import extra, run
from toughflac.coupling.permeability import rutqvist2002
from toughflac.coupling.permeability import constant

# FLAC3D solver parameters
model_save = "tf_in.f3sav"
deterministic = False
damping = "combined"
mechanical_ratio = 1.0e-8
n_threads = 12
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

# Extra Python functions as a list of callables
python_func_tough = ()  # Before mechanical analysis
python_func_flac = ()  # After mechanical analysis

# Extra FISH functions as a list of strings
fish_func_tough = ()  # Before mechanical analysis
fish_func_flac = ()  # After mechanical analysis

# Permeability functions as a dict of functions per group
permeability_func = {
    "FAULT": lambda g: constant(g, k0 = 2.0e-14, phi0 = 0.12),
    #"FLT_M": lambda g: rutqvist2002(g, k0 = 1.0e-15, phi0 = 0.01, phir = 0.009),
}

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
