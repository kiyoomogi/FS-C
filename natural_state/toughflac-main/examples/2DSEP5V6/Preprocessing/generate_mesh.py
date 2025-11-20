import toughflac as tf

# Grid
dx = [
    25.0,       35.0,       49.0,       68.6,       96.0,       134.5,      188.2,      263.5,
    368.9,      516.5,      723.1,      1012.4,     1417.3,     1984.3,     3092.7,     25.,
]
dy = [1.0]
dz = [
    10.0,   40.0,   50.0,   50.0,   50.0,   50.0,   50.0,   50.0,
    150.0,  150.0,  150.0,  150.0,  150.0,  150.0,  150.0,  150.0,
    150.0,  90.0,   10.0,
][::-1]  # Grid is built from bottom to top in a right-handed coordinate system
point_0 = [0.0, 0.0, -1800.0]

# Create grid
tf.model.new()
tf.zone.create.tartan_brick(dx, dy, dz, point_0=point_0)

# Assign groups: vadose zone (x > 25)
tf.zone.group("LOWVZ",range_x=(25.0, 10000.0))
tf.zone.group("HIGVZ",range_x=(25.0, 10000.0), range_z=(-300.0, -1790.0))
tf.zone.group("LATBC",range_x=(9975.0, 10000.0))
tf.zone.group("TOPBC",range_x=(25.0, 10000.0), range_z=(-10.0, 0.0))
tf.zone.group("BOTBC",range_x=(25.0, 10000.0), range_z=(-1800.0, -1790.0))

# Assign groups: fault (x < 25)
tf.zone.group("FAULT", range_x=(0.0, 25.0))
tf.zone.group("TOPFC", range_x=(0.0, 25.0), range_z=(-10.0, 0.0))
tf.zone.group("BOTFC", range_x=(0.0, 25.0), range_z=(-1800.0, -1790.0))

# Define boundary conditions
tf.zone.set_dirichlet_bc("TOPBC")
tf.zone.set_dirichlet_bc("TOPFC")

# Define initial conditions
tf.zone.initialize_pvariables(
    x1=lambda z: 1.5e5,
    x2=lambda z: 0.3e-2,
    x3=lambda z: 0.0,
    x4=lambda z: 8.0,
    group = ["TOPBC", "TOPFC"],
)
tf.zone.initialize_pvariables(
    x1=lambda z: 1.77e6,
    x2=lambda z: 0.3e-2,
    x3=lambda z: 0.0,
    x4=lambda z: 98.0,
    group = ["BOTBC", "BOTFC"],
)

# Export MESH
tf.zone.export_tough("MESH", incon=True)

# Export to f3grid
tf.zone.export_flac("../mesh.f3grid", binary=True)
