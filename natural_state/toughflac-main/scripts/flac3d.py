from toughflac.coupling import extra, run

# FLAC3D solver parameters
model_save = "tf_in.f3sav"
deterministic = False
damping = "combined"
mechanical_ratio = 1.0e-5
n_threads = 8
thermal = True

# Output parameters
savedir = None
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

# Permeability functions as a dict of functions per group
permeability_func = {}

# History variables
history_func = {}
history = {}


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
