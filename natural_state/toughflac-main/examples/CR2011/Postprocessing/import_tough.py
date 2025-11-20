import itasca as it
import toughflac as tf

# Import model and save file
tf.model.new()
tf.zone.import_flac("../mesh.f3grid")
data, _ = tf.zone.import_tough_output("2_TH/OUTPUT_ELEME.csv")

# Extract pressure change and gas saturation at last time step
dpp = data["PRES"][-1] - 1.0e5 + 9810.0 * it.zonearray.pos()[:, 2]
sg = data["SAT_G"][-1]

# Set pressure change and gas saturation in extra arrays
it.zonearray.set_extra(2, dpp)
it.zonearray.set_extra(4, sg)

# Remove boundary elements for visualization
it.command("zone delete range group 'BOUND'")
