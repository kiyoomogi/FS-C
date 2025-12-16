#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 15 17:58:40 2025

@author: matthijsnuus
"""

import toughio 

mesh = toughio.read_mesh("/Users/matthijsnuus/Desktop/FS-C/model/mesh/FSC_mesh_cyl.msh")

materials = mesh.materials 

toughio.write_mesh("/Users/matthijsnuus/Desktop/FS-C/model/coupled_model/mesh.f3grid", mesh, file_format="flac3d", binary=True)