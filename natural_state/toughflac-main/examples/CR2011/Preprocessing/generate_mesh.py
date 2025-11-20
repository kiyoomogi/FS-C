import numpy
import toughflac as tf

# Grid
bnd_thick = 10.0

dx = numpy.diff(numpy.logspace(numpy.log10(100.0), numpy.log10(1100.0), 30))
dx = numpy.append(dx, bnd_thick)                # Right boundary
dx = numpy.concatenate((dx[::-1], dx))

zaq = [143.0, 127.0, 111.0, 96.0, 81.0, 67.0, 52.0, 36.0, 27.0]
dz = [bnd_thick]                                # Top boundary
dz += zaq + 6 * [10.0]                          # Upper aquifer
dz += 10 * [10.0] + 4 * [12.5]                  # Upper caprock
dz += 5 * [20.0]                                # Central aquifer
dz += 4 * [12.5] + 10 * [10.0]                  # Basal caprock
dz += 6 * [10.0] + zaq[::-1]                    # Basal aquifer
dz += [bnd_thick]                               # Bottom boundary
point_0 = [-bnd_thick, 0.0, -2500.0 - bnd_thick]

# Create grid
tf.model.new()
tf.zone.create.tartan_brick(dx, [1.0], dz, point_0=point_0, group="BOUND")

# Assign groups
tf.zone.group("UPPAQ", range_x=(0.0, 2000.0), range_z=(-500.0, -1300.0))
tf.zone.group("CAPRO", range_x=(0.0, 2000.0), range_z=(-1300.0, -1450.0))
tf.zone.group("CENAQ", range_x=(0.0, 2000.0), range_z=(-1450.0, -1550.0))
tf.zone.group("CAPRO", range_x=(0.0, 2000.0), range_z=(-1550.0, -1700.0))
tf.zone.group("BASAQ", range_x=(0.0, 2000.0), range_z=(-1700.0, -2500.0))

# Define boundary conditions
tf.zone.set_dirichlet_bc("BOUND")
    
# Define initial conditions
tf.zone.initialize_pvariables(
    x1=lambda z: 1.0e5 - 9810.0 * z,
    x2=lambda z: 0.05,
    x3=lambda z: 0.0,
    x4=lambda z: 10.0 - 0.025 * z,
)

# Export MESH and INCON
tf.zone.export_tough(
    "MESH",
    permeability=lambda zone: [1.0e-13, 1.0e-13, 1.0e-15] if zone.group() == "CENAQ" else [-1.0, -1.0, -1.0],
    group_end="BOUND",
    incon=True,
)

# Export to f3grid
tf.zone.export_flac("../mesh.f3grid", binary=True)
