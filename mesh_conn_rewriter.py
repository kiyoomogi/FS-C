#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 11 09:29:26 2025

@author: matthijsnuus
"""

import numpy as np 
import toughio 



mesh = toughio.read_input("/Users/matthijsnuus/Desktop/FS-C/model/injection_model/MESH")

connections = mesh["connections"]

for conn in connections.values():
    if conn.get("permeability_direction") == 1:
        conn["permeability_direction"] = 3

# put it back (not strictly necessary, but explicit)
mesh["connections"] = connections

# write to a new MESH file so you keep the original safe
toughio.write_input(
    "/Users/matthijsnuus/Desktop/FS-C/model/injection_model/MESH_perm3",
    mesh,
)