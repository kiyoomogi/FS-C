import toughio
import toughflac as tf

# Import grid
mesh = toughio.read_mesh("Preprocessing/gmsh/mesh.msh")

# Process grid
mesh.points[:, [1, 2]] = mesh.points[:, [2, 1]]
mesh.extrude_to_3d(height = 1.0, axis = 1)

# Import mesh
tf.model.new()
tf.zone.import_mesh(mesh)

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
