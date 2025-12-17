import toughio
import toughflac as tf



mesh = toughio.read_mesh("/home/manuus/Desktop/FS-C/model/mesh/FSC_mesh_cyl.msh")
#mesh = toughio.read_mesh("/home/TOUGH3-FLAC3D/toughflac/examples/2DSEP5V6/Preprocessing/gmsh/mesh.msh")
#mesh.cell_data['material'] = mesh.cell_data['material'].ravel()



# Import mesh
tf.model.new()
tf.zone.import_mesh(mesh, prune_duplicates=True)

# Define boundary conditions
#tf.zone.set_dirichlet_bc("BDNTO")
#tf.zone.set_dirichlet_bc("BDNBO")


# Export MESH
#tf.zone.export_tough("/home/manuus/Desktop/FS-C/model/coupled_model/MESH")

# Export to f3grid
#tf.zone.export_flac("../mesh.f3grid")