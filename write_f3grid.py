#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 15 17:58:40 2025

@author: matthijsnuus
"""

import toughio 

mesh = toughio.read_mesh("/Users/matthijsnuus/Desktop/FS-C/model/mesh/FSC_mesh_cyl.msh")

materials = mesh.materials 

mesh.write_tough("/Users/matthijsnuus/Desktop/FS-C/model/coupled_model/MESH")
mesh.write("/Users/matthijsnuus/Desktop/FS-C/model/natural_state/mesh.pickle")


toughio.write_mesh("/Users/matthijsnuus/Desktop/FS-C/model/coupled_model/mesh.f3grid", mesh, file_format="flac3d")



mesh = toughio.read_mesh("/Users/matthijsnuus/Desktop/FS-C/model/natural_state/mesh.pickle")
mesh.read_output("/Users/matthijsnuus/Desktop/FS-C/model/natural_state/OUTPUT_ELEME.csv", time_step=-1)