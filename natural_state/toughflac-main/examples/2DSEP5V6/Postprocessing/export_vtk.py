import toughflac as tf

# Save file to export
tf.model.restore("3_THM/f3out/tf_fi.f3sav")

# Attributes to export
attributes = [
    "group",
    "disp_x",
    "disp_z",
    "disp_mag",
]

# Other attributes to export
extra_func = {
    "pp": lambda z: z.pp(),
}

# Export to VTK
tf.zone.export_mesh(
    filename="2DSEP5V6.vtk",
    attribute=attributes,
    extra_func=extra_func,
)
