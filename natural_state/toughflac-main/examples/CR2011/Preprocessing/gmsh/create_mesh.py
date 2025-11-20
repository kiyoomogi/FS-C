#%%
import pygmsh

# Variables
xmin, xmax = 0.0, 2000.0
zmin, zmax = -500.0, -2500.0
bnd_thick = 10.0

# Initialize geometry
geo = pygmsh.built_in.Geometry()

# Aquifer left to fault
cenaq = geo.add_polygon(
    X=[
        [xmin, -1450.0, 0.0],
        [xmax, -1450.0, 0.0],
        [xmax, -1550.0, 0.0],
        [xmin, -1550.0, 0.0],
    ],
    lcar=20.0,
)

capro_top = geo.add_polygon(
    X=[
        [xmin, -1300.0, 0.0],
        [xmax, -1300.0, 0.0],
        [xmax, -1450.0, 0.0],
        [xmin, -1450.0, 0.0],
    ],
    lcar=[50.0, 100.0, 100.0, 50.0],
)

capro_bot = geo.add_polygon(
    X=[
        [xmin, -1550.0, 0.0],
        [xmax, -1550.0, 0.0],
        [xmax, -1700.0, 0.0],
        [xmin, -1700.0, 0.0],
    ],
    lcar=[50.0, 100.0, 100.0, 50.0],
)

uppaq = geo.add_polygon(
    X=[
        [xmin, zmin, 0.0],
        [xmax, zmin, 0.0],
        [xmax, -1300.0, 0.0],
        [xmin, -1300.0, 0.0],
    ],
    lcar=500.0,
)

basaq = geo.add_polygon(
    X=[
        [xmin, -1700.0, 0.0],
        [xmax, -1700.0, 0.0],
        [xmax, zmax, 0.0],
        [xmin, zmax, 0.0],
    ],
    lcar=500.0,
)

# Boundary elements
bound_left = geo.add_polygon(
    X=[
        [xmin, zmin, 0.0],
        [xmin - bnd_thick, zmin, 0.0],
        [xmin - bnd_thick, zmax, 0.0],
        [xmin, zmax, 0.0],
        [xmin, -1700.0, 0.0],
        [xmin, -1550.0, 0.0],
        [xmin, -1450.0, 0.0],
        [xmin, -1300.0, 0.0],
    ],
    lcar=100.0,
)

bound_right = geo.add_polygon(
    X=[
        [xmax, zmin, 0.0],
        [xmax + bnd_thick, zmin, 0.0],
        [xmax + bnd_thick, zmax, 0.0],
        [xmax, zmax, 0.0],
        [xmax, -1700.0, 0.0],
        [xmax, -1550.0, 0.0],
        [xmax, -1450.0, 0.0],
        [xmax, -1300.0, 0.0],
    ],
    lcar=100.0,
)

bound_top = geo.add_polygon(
    X=[
        [xmin, zmin, 0.0],
        [xmax, zmin, 0.0],
        [xmax + bnd_thick, zmin, 0.0],
        [xmax + bnd_thick, zmin + bnd_thick, 0.0],
        [xmin, zmin + bnd_thick, 0.0],
    ],
    lcar=100.0,
)

bound_bot = geo.add_polygon(
    X=[
        [xmin, zmax, 0.0],
        [xmax, zmax, 0.0],
        [xmax + bnd_thick, zmax, 0.0],
        [xmax + bnd_thick, zmax - bnd_thick, 0.0],
        [xmin, zmax - bnd_thick, 0.0],
    ],
    lcar=100.0,
)

# Define physical groups
geo.add_physical(
    entities=uppaq.surface, label="UPPAQ",
)
geo.add_physical(
    entities=[capro_top.surface, capro_bot.surface,], label="CAPRO",
)
geo.add_physical(
    entities=cenaq.surface, label="CENAQ",
)
geo.add_physical(
    entities=basaq.surface, label="BASAQ",
)
geo.add_physical(
    entities=[
        bound_left.surface,
        bound_right.surface,
        bound_top.surface,
        bound_bot.surface,
    ],
    label="BOUND",
)

# Write mesh file
geo.add_raw_code("Coherence;")
pygmsh.generate_mesh(
    geo,
    dim=2,
    prune_vertices=True,
    remove_faces=True,
    geo_filename="mesh.geo",
    msh_filename="mesh.msh",
    mesh_file_type="msh4",
    extra_gmsh_arguments=[
        # "-algo", "del2d",
        "-smooth",
        "2",
        "-optimize_netgen",
    ],
)
