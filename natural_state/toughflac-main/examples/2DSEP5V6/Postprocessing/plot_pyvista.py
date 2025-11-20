# This script cannot be run in FLAC3D due to a bug that causes FLAC3D
# to crash whenever PyVista's rendering window is closed.
#%%
import numpy
import pyvista

# Load mesh
mesh = pyvista.read("../2DSEP5V6.vtk")

# Create displacement vector (cm)
mesh["Displacement"] = 1.0e2 * numpy.column_stack((
    mesh["disp_x"],
    numpy.zeros(mesh.n_points),
    mesh["disp_z"],
))
arrows = mesh.glyph(
    orient="Displacement",
    scale="Displacement",
    factor=20.0,
)

# Plot
p = pyvista.Plotter(window_size=(1600, 800), notebook=False)
p.add_mesh(
    mesh,
    scalars=mesh["Displacement"][:, 2],
    stitle="Vertical displacement (cm)",
    cmap="coolwarm",
    n_colors=10,
    show_edges=True,
    edge_color=(0.5, 0.5, 0.5),
    scalar_bar_args={
        "height": 0.1,
        "width": 0.5,
        "position_x": 0.75,
        "position_y": 0.01,
        "vertical": False,
        "n_labels": 4,
        "fmt": "%.3f",
        "title_font_size": 20,
        "font_family": "arial",
        "shadow": True,
    },
)
p.add_mesh(
    arrows,
    color="black",
)
# p.show_axes()
p.show_grid(
    show_xaxis=True,
    show_yaxis=False,
    show_zaxis=True,
    xlabel="Distance (m)",
    zlabel="Elevation (m)",
    ticks="outside",
    font_family="arial",
    shadow=True,
)
p.camera_position = (
    (5000.0, -11000.0, -900.0),
    (5000.0, 0.0, -900.0),
    (0.0, 0.0, 1.0),
)
p.save_graphic("pyvista.pdf")
p.show()
