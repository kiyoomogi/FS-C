import toughflac as tf
import os

# Grid
dx = [
    113255.0,   78894.0,    52596.0,    35064.0,    23376.0,    15584.0,    10389.0,    6926.0,
    4617.0,     3078.0,     2052.0,     1368.0,     912.0,      608.0,      405.0,      270.0,
    180.0,      120.0,      80.0,       53.0,       35.0,       23.0,       15.0,       10.0,
    10.0,       10.0,       10.0,       10.0,       10.0,       10.0,       10.0,       10.0,
    10.0,       10.0,       10.0,       10.0,       10.0,       10.0,       10.0,       10.0,
    10.0,       10.0,       10.0,       15.0,       23.0,       35.0,       53.0,       80.0,
    120.0,      180.0,      270.0,      405.0,      608.0,      912.0,      1368.0,     2052.0,
    3078.0,     4617.0,     6926.0,     10389.0,    15584.0,    23376.0,    35064.0,    52596.0,
    78894.0,    113255.0,
]
dy = [1.0]
dz = [
    0.1,    250.0,  250.0,  194.0,  180.0,  120.0,  80.0,   53.0,
    35.0,   23.0,   15.0,   10.0,   10.0,   10.0,   10.0,   10.0,
    10.0,   10.0,   10.0,   10.0,   10.0,   15.0,   20.0,   35.0,
    50.0,   50.0,   20.0,   10.0,   10.0,   15.0,   25.0,   50.0,
    100.0,  200.0,  400.0,  700.0,  0.1,
][::-1]  # Grid is built from bottom to top in a right-handed coordinate system
point_0 = [-350000.0, -0.5, -3000.1]

# Create grid
tf.model.new()
tf.zone.create.tartan_brick(dx, dy, dz, point_0=point_0)

# Assign groups
tf.zone.group("ATMOS", range_z=(0.0, 1.0))
tf.zone.group("UPPER", range_z=(-1200.0, 0.0))
tf.zone.group("CAPRO", range_z=(-1300.0, -1200.0))
tf.zone.group("AQFER", range_z=(-1500.0, -1300.0))
tf.zone.group("BASEM", range_z=(-3000.0, -1500.0))
tf.zone.group("BOTOM", range_z=(-3001.0, -3000.0))

# Define boundary conditions
tf.zone.set_dirichlet_bc("ATMOS")

# Define initial conditions
tf.zone.initialize_pvariables(
    x1=lambda z: 1.0e5 - 9810.0 * z,
    x2=lambda z: 0.05,
    x3=lambda z: 0.0,
    x4=lambda z: 10.0 - 0.025 * z,
)

# Export MESH and INCON. Absolute path for MESH is needed
tf.zone.export_tough("/TOUGH-FLAC/tough3-flac3dv7/toughflac-master/examples/2dldV6/MESH", incon=True)

# Export to f3grid
tf.zone.export_flac("../mesh.f3grid", binary=True)
