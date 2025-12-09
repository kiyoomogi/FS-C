#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 16 08:28:43 2025

@author: matthijsnuus
"""

import numpy as np
import pandas as pd
import toughio
import matplotlib.pyplot as plt 


rates_csv = pd.read_csv("/Users/matthijsnuus/Desktop/FS-C/model/injection_rates/filtered_FSC_injecrates.csv", delimiter=',', index_col=[0])

time_zero =  0
time_final = 3600 * 24 * 365 * 50



#mesh = toughio.read_mesh("/Users/matthijsnuus/Desktop/FS-C/model/mesh/FSC_mesh_2fault.msh")
mesh = toughio.read_mesh("/Users/matthijsnuus/Desktop/FS-C/model/mesh/FSC_mesh_cyl.msh")
mesh.cell_data['material'] = mesh.cell_data['material'].ravel()

z_centers = mesh.centers[:,2]
z_top = np.amax(z_centers)
z_bot = np.amin(z_centers)

p0 = rates_csv['zone P [MPa]'][0] * 1e6

#p0 = 1.298302 * 100000
z_bfsb1 = 0

dist_top = z_top - z_bfsb1
dist_bot = abs(z_bot - z_bfsb1)

bot_BC_value = p0 + 1000 * 9.81 * dist_bot
top_BC_value = p0 - 1000 * 9.81 * dist_top


#Add material
mesh.add_material("CLAY ", 1)
mesh.add_material("FAULT", 2)
mesh.add_material("INJEC", 3)
mesh.add_material("BNDTO", 4)
mesh.add_material("BNDBO", 5)


materials = (mesh.materials )
bcond = (materials == "BNDTO").astype(int) #+ (materials == "BNDBO").astype(int) 
mesh.add_cell_data("boundary_condition", bcond)


unique_materials = set((materials).tolist())


mesh.write_tough("/Users/matthijsnuus/Desktop/FS-C/model/natural_state/MESH", incon=True)
mesh.write("/Users/matthijsnuus/Desktop/FS-C/model/natural_state/mesh.pickle")


parameters = {
    "title": "natural state",
    "eos": "eco2n",
    "isothermal": True,
    "start": True,
    "times": (list(np.linspace(time_zero, time_final, 20))), 
}


#INITIAL CONDITIONS 
ini_pore_pressure = 0.1e6#0.432e6 #Pa,
ini_NACL = 0 #0.017203 
ini_gas_content = 0.0 #-, ...
temperature = 16.5 #°C, (1)

#CAPILLARY PRESSURE AND RELATIVE PERMEABILITY VARIABLES     
pore_size_distr_index =0.5 #-, (2), symbol: λ
S_lr = 0.01 #-, (2), total trapped water 
S_ls = 1 #-, (2), liquid saturation  
S_gr = 0.0 #-, Guess?, total trapped gas 
P0 = 18e6 #1.47e7 #Pa, R.Senger
Pmax = 1e12 #Pa, guessed from (2),

#values from Antonio for ICP & IRP
icp11 = [1.67, 1.5e7, 0, 0.0, 0.0, 0.0, 0.01]
irp11 = [0.5, 0.0, 0]

icp7 = [pore_size_distr_index, (S_lr - 0.001), 1/P0, Pmax, S_ls]
irp7 = [pore_size_distr_index, S_lr, S_ls, S_gr]

parameters["default"] = {
    "density": 2500.,                     #kg/m3
    "porosity": 0.14 ,                    #- 
    "permeability": [1e-15, 1e-15,1e-15], #m2  
    "conductivity": 2.0,                  #W/m/K
    "specific_heat": 920.,                #J/kg K
    "compressibility": 1e-99,             #Pa^-1
    "expansivity": 1.4e-5,                #°C^-1
    "conductivity_dry": 2.0,              #W/m/K

    "initial_condition": [ini_pore_pressure,ini_NACL, ini_gas_content,temperature],
    "relative_permeability": {
        "id": 11, #Modified van genuchtn 
        "parameters": irp11,
    },
    "capillarity": {
        "id": 11, #Modified van genuchten 
        "parameters": icp11,
    },
}

#Rock parameters
parameters["rocks"] = {
    "INJEC": {
        "density": 2500,
        "porosity": 0.99, 
        "permeability": [5.0e-16,5.0e-16,1.0e-17],
        "specific_heat":920e20, #constant temperature in injection well by making heat capacity huge
        "compressibility": 1e-99, #2.94e-7,
        "relative_permeability": {
            "id": 3, #van genuchten 
            "parameters": [1,0],
        },
        "capillarity": {
            "id": 8, #van genuchten 
            "parameters": []
        },  
    },
    "CLAY ": {
        "tortuosity": 0.8, #-, (4) 
        #"initial_condition": [ini_pore_pressure,ini_gas_content,temperature],
    },
    "FAULT": {
        "porosity": 0.14,
    },

    "BNDTO": {"initial_condition": [top_BC_value, ini_NACL, ini_gas_content, temperature]},
    "BNDBO": {"initial_condition": [bot_BC_value, ini_NACL, ini_gas_content, temperature]},
}

parameters["options"] = {
    #"n_iteration": 9,
    "n_cycle": 9999,
    "n_cycle_print": 9999,
    "t_ini": time_zero,
    "t_max": time_final,
    "t_steps": 1 * 3600,
    "t_step_max":  2 * 24 * 3600,
    
    "t_reduce_factor": 4,
    "eps1": 1.0e-7,
    #"eps2": 100.0,
    "gravity": 9.8,
}



parameters['extra_options'] = {
        1: 1,
        2: 2,
        3: 1,
        4: 1,
        5: 5,
        11: 0,   #0 or 2 
        12: 2,
        17: 9,
        21: 8
}



parameters['elements'] = {}
#Output parameters




toughio.write_input("/Users/matthijsnuus/Desktop/FS-C/model/natural_state/INFILE", parameters)  
 

