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
