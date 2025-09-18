import toughio

mesh1 = toughio.read_mesh("/Users/matthijsnuus/Desktop/FS-C/model/mesh/FSC_mesh_simple.msh")
mesh1.write_tough("/Users/matthijsnuus/Desktop/FS-C/model/injection_model/MESH")


mesh = toughio.read_input("/Users/matthijsnuus/Desktop/FS-C/model/injection_model/MESH")
elements    = mesh["elements"]
connections = mesh["connections"]

# INJEC element names
injec = {ename for ename, edata in elements.items() if edata.get("material") == "INJEC"}

# element-name length (TOUGH classic: 5)
elem_len = len(next(iter(elements)))

updated = []  # will collect: (conn_name, elem1, elem2, old_kdir, new_kdir)

for cname, cdata in connections.items():
    if len(cname) < 2*elem_len:   # skip weird keys
        continue
    e1 = cname[:elem_len]
    e2 = cname[elem_len:2*elem_len]

    old = cdata.get("permeability_direction")
    if (e1 in injec) and (e2 in injec) and old != 2:
        cdata["permeability_direction"] = 2
        updated.append((cname, e1, e2, old, 2))

print(f"Connections updated now: {len(updated)}")
for row in updated[:20]:  # preview first 20
    print(f"{row[0]} : {row[1]}–{row[2]}  {row[3]} -> {row[4]}")

# optional: save the list
# import pandas as pd
# pd.DataFrame(updated, columns=["connection","elem1","elem2","old_kdir","new_kdir"])\
#   .to_csv("/Users/matthijsnuus/Desktop/FS-C/model/injection_model/updated_connections.csv", index=False)

# optional: write mesh back
toughio.write_input("/Users/matthijsnuus/Desktop/FS-C/model/injection_model/MESH", mesh)
