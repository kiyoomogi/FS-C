import toughio
import toughflac as tf



mesh = toughio.read_mesh("/home/manuus/Desktop/FS-C/model/mesh/FSC_mesh_cyl.msh")
#mesh.cell_data['material'] = mesh.cell_data['material'].ravel()


# Import mesh
tf.model.new()
tf.zone.import_mesh(mesh)

# Define boundary conditions
tf.zone.set_dirichlet_bc("BDNTO")
tf.zone.set_dirichlet_bc("BDNBO")


# Export MESH
#tf.zone.export_tough("/home/manuus/Desktop/FS-C/model/coupled_model/MESH")

# Export to f3grid
tf.zone.export_flac("../mesh.f3grid", binary=True)