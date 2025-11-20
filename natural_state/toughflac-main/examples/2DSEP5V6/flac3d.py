from toughflac.coupling import extra, run

# FLAC3D solver parameters
model_save = "tf_in.f3sav"
deterministic = False
damping = "combined"
mechanical_ratio = 1.0e-8
n_threads = 12
thermal = True

# Output parameters
savedir = "f3out"

# Extra variables to save
extra["saturation"] = True

# History variables
history = {
    "hist1": {
        "disp_z": [
            [0.0, 0.0, -10.0],
            [0.0, 0.0, -50.0],
            [0.0, 0.0, -1000.0],
        ],
        "disp_x": [
            [100.0, 0.0, -10.0],
        ],
    },
}


if __name__ == "__main__":
    run(
        model_save=model_save,
        deterministic=deterministic,
        damping=damping,
        mechanical_ratio=mechanical_ratio,
        n_threads=n_threads,
        thermal=thermal,
        history=history,
        savedir=savedir,
    )
