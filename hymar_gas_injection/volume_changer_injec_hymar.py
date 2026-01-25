#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import toughio

# --- read TOUGH MESH as input dict ---
mesh = toughio.read_input(
    "/Users/matthijsnuus/Desktop/FS-C/model/hymar_gas_injection/2_TH/MESH"
)

elements = mesh["elements"]
connections = mesh["connections"]

# -------------------------
# 1) Collect element labels by material
# -------------------------
ppinj_elems = [e for e, info in elements.items() if info.get("material") == "PPINJ"]
steel_elems = [e for e, info in elements.items() if info.get("material") == "STEEL"]

print(f"Number of PPINJ elements: {len(ppinj_elems)}")
print(f"Number of STEEL elements: {len(steel_elems)}")

ppinj_set = set(ppinj_elems)
steel_set = set(steel_elems)

# -------------------------
# 2) Find + count PPINJ–STEEL connections
# -------------------------
to_remove = []

for key in connections.keys():

    # Typical TOUGH connection key = 2 element names concatenated
    # Example: "A1A10A1A11" -> e1="A1A10", e2="A1A11"
    e1 = key[:5]
    e2 = key[5:10]

    # Check if it's between PPINJ and STEEL (either direction)
    is_ppinj_steel = ((e1 in ppinj_set and e2 in steel_set) or
                      (e2 in ppinj_set and e1 in steel_set))

    if is_ppinj_steel:
        to_remove.append(key)

print(f"Connections PPINJ <-> STEEL found: {len(to_remove)}")

# -------------------------
# 3) Remove them from dictionary
# -------------------------
for k in to_remove:
    del connections[k]

print(f"Removed {len(to_remove)} connections.")
print(f"Remaining connections: {len(connections)}")



# --- collect PPINJ element labels + volumes ---
ppinj_labels = []
ppinj_volumes = []

for label, edata in elements.items():
    if edata.get("material") == "PPINJ":
        ppinj_labels.append(label)
        ppinj_volumes.append(edata.get("volume", 0.0))

# --- sums ---
V_current = sum(ppinj_volumes)  # m³
V_current_ml = V_current * 1e6  # mL

print(f"Number of PPINJ elements: {len(ppinj_labels)}")
print(f"Current total PPINJ volume = {V_current:.6e} m³ ({V_current_ml:.6f} mL)")

# --- target volume = 300 mL ---
V_target_ml = 35
V_target = V_target_ml * 1e-6  # m³

# --- scale factor ---
if V_current <= 0:
    raise ValueError("Current PPINJ volume sum is zero (cannot scale).")

scale = V_target / V_current
print(f"Scale factor = {scale:.6f}")

# --- scale all PPINJ element volumes ---
for label in ppinj_labels:
    elements[label]["volume"] *= scale

# --- check new sum ---
V_new = sum(elements[label]["volume"] for label in ppinj_labels)
V_new_ml = V_new * 1e6

print(f"New total PPINJ volume = {V_new:.6e} m³ ({V_new_ml:.6f} mL)")

# --- Optional: write new mesh file ---
out_mesh_path = "/Users/matthijsnuus/Desktop/FS-C/model/hymar_gas_injection/2_TH/MESH_scaled_300ml"
toughio.write_input(out_mesh_path, mesh)

print("Saved scaled mesh to:", out_mesh_path)
