import toughio
import toughflac as tf

mesh = toughio.read_mesh("/home/manuus/Desktop/FS-C/model/mesh/FSC_coarse.msh")


# Import mesh
tf.model.new()
tf.zone.import_mesh(mesh) # , prune_duplicates=True)
tf.zone.export_flac("../mesh.f3grid")


# Export MESH and INCON
tf.zone.export_tough("/home/manuus/Desktop/FS-C/model/coarse_model/coupled_model/MESH")

# Export to f3grid
tf.zone.export_flac("../mesh.f3grid", binary=True)