#%%
import pygmsh

# Variables
lc = 200.0

# Initialize geometry
geo = pygmsh.built_in.Geometry()

# Fault
topfc = geo.add_polygon(
    X=[
        [0.0, 0.0, 0.0],
        [25.0, 0.0, 0.0],
        [25.0, -10.0, 0.0],
        [0.0, -10.0, 0.0],
    ],
    lcar=lc,
)
geo.add_physical(entities=topfc.surface, label="TOPFC")

fault = geo.add_polygon(
    X=[
        [0.0, -10.0, 0.0],
        [25.0, -10.0, 0.0],
        [25.0, -300.0, 0.0],
        [25.0, -1790.0, 0.0],
        [0.0, -1790.0, 0.0],
        [0.0, -300.0, 0.0],
        [0.0, -10.0, 0.0],
    ],
    lcar=lc,
)
geo.add_physical(entities=fault.surface, label="FAULT")

botfc = geo.add_polygon(
    X=[
        [0.0, -1790.0, 0.0],
        [25.0, -1790.0, 0.0],
        [25.0, -1800.0, 0.0],
        [0.0, -1800.0, 0.0],
    ],
    lcar=lc,
)
geo.add_physical(entities=botfc.surface, label="BOTFC")

# Top boundary
topbc = geo.add_polygon(
    X=[
        [25.0, 0.0, 0.0],
        [1000.0, 0.0, 0.0],
        [3000.0, 0.0, 0.0],
        [5000.0, 0.0, 0.0],
        [7000.0, 0.0, 0.0],
        [9000.0, 0.0, 0.0],
        [9975.0, 0.0, 0.0],
        [10000.0, 0.0, 0.0],
        [10000.0, -10.0, 0.0],
        [9975.0, -10.0, 0.0],
        [9000.0, -10.0, 0.0],
        [7000.0, -10.0, 0.0],
        [5000.0, -10.0, 0.0],
        [3000.0, -10.0, 0.0],
        [1000.0, -10.0, 0.0],
        [25.0, -10.0, 0.0],
    ],
    lcar=lc,
)
geo.add_physical(entities=topbc.surface, label="TOPBC")

# Low vadose zone
lowvz = geo.add_polygon(
    X=[
        [25.0, -10.0, 0.0],
        [1000.0, -10.0, 0.0],
        [3000.0, -10.0, 0.0],
        [5000.0, -10.0, 0.0],
        [7000.0, -10.0, 0.0],
        [9000.0, -10.0, 0.0],
        [9975.0, -10.0, 0.0],
        [9975.0, -300.0, 0.0],
        [9000.0, -300.0, 0.0],
        [7000.0, -300.0, 0.0],
        [5000.0, -300.0, 0.0],
        [3000.0, -300.0, 0.0],
        [1000.0, -300.0, 0.0],
        [25.0, -300.0, 0.0],
    ],
    lcar=lc,
)
geo.add_physical(entities=lowvz.surface, label="LOWVZ")

# High vadose zone
higvz = geo.add_polygon(
    X=[
        [25.0, -300.0, 0.0],
        [1000.0, -300.0, 0.0],
        [3000.0, -300.0, 0.0],
        [5000.0, -300.0, 0.0],
        [7000.0, -300.0, 0.0],
        [9000.0, -300.0, 0.0],
        [9975.0, -300.0, 0.0],
        [9975.0, -1790.0, 0.0],
        [9000.0, -1790.0, 0.0],
        [7000.0, -1790.0, 0.0],
        [5000.0, -1790.0, 0.0],
        [3000.0, -1790.0, 0.0],
        [1000.0, -1790.0, 0.0],
        [25.0, -1790.0, 0.0],
    ],
    lcar=lc,
)
geo.add_physical(entities=higvz.surface, label="HIGVZ")

# Bottom boundary
botbc = geo.add_polygon(
    X=[
        [25.0, -1790.0, 0.0],
        [1000.0, -1790.0, 0.0],
        [3000.0, -1790.0, 0.0],
        [5000.0, -1790.0, 0.0],
        [7000.0, -1790.0, 0.0],
        [9000.0, -1790.0, 0.0],
        [9975.0, -1790.0, 0.0],
        [10000.0, -1790.0, 0.0],
        [10000.0, -1800.0, 0.0],
        [9975.0, -1800.0, 0.0],
        [9000.0, -1800.0, 0.0],
        [7000.0, -1800.0, 0.0],
        [5000.0, -1800.0, 0.0],
        [3000.0, -1800.0, 0.0],
        [1000.0, -1800.0, 0.0],
        [25.0, -1800.0, 0.0],
    ],
    lcar=lc,
)
geo.add_physical(entities=botbc.surface, label="BOTBC")

# Lateral boundary
latbc = geo.add_polygon(
    X=[
        [9975.0, -10.0, 0.0],
        [10000.0, -10.0, 0.0],
        [10000.0, -300.0, 0.0],
        [10000.0, -1790.0, 0.0],
        [9975.0, -1790.0, 0.0],
        [9975.0, -300.0, 0.0],
    ],
    lcar=lc,
)
geo.add_physical(entities=latbc.surface, label="LATBC")

# Write geo file
geo.add_raw_code("Coherence;")
with open("Preprocessing/gmsh/mesh.geo", "w") as f:
    f.write(geo.get_code())
