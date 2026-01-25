#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import toughio

# --- read TOUGH MESH as input dict ---
mesh = toughio.read_input(
    "/Users/matthijsnuus/Desktop/FS-C/model/hymar_gas_injection/2_TH/MESH"
)

elements = mesh["elements"]

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
V_target_ml = 50.0
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
