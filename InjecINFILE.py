#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  8 15:27:52 2025

@author: matthijsnuus
"""


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np 
import toughio 


time_zero = 0
time_final = 3600 * 24 * 100 

diffusion = np.array([
    [0, 0],    # Water: [gas, aqueous]
    [3.5e-2, 3.5e-2],    # Helium: [gas, aqueous]
    [1e-2, 1e-2]    # Helium: [gas, aqueous]
])

parameters = {
    "title": "InjectionCO2",
    "isothermal": True,
    "eos":"eco2n",
    "start": True,
    "times": list(np.linspace(time_zero,time_final,100)),
    "diffusion": diffusion}


a = {
    "type": "nx",
    "n_increment": 1,
    "sizes": 0.5,
}
b = {
    "type": "ny",
    "n_increment": 1,
    "sizes": 1,
}
c = {
    "type": "nz",
    "n_increment": 1,
    "sizes": 1,
}
d = {
    "type": "nx",
    "n_increment": 1,
    "sizes": 0.5,
}


parameters['meshmaker'] = {
    "type": "xyz",
    "parameters": [a,d,b,c],
    "angle": 0.,
}

toughio.write_input("/Users/matthijsnuus/Desktop/FS-C/InjectionRates/meshmaker", parameters)
mesh = toughio.meshmaker.from_meshmaker("/Users/matthijsnuus/Desktop/FS-C/InjectionRates/meshmaker", material='dfalt')
mesh.write_tough("/Users/matthijsnuus/Desktop/FS-C/InjectionRates/MESH")

del parameters['meshmaker']


mesh.cell_data['material'] = [1,1] 
mesh.add_material("TANK", 1)
materials = mesh.materials

#INITIAL CONDITIONS 
temperature = 15. #°C, (1)


parameters["default"] = {
    "density": 2700.,                #kg/m3, (1), LBNL value
    "porosity": 0.99 ,              #-, (1), LBNL value
    "permeability": [1e-5,1e-5,1e-5],    #based on hydraulic  test value 2.17956; otherwise: 5e-20 m2, (1,2), LBNL value 
    "conductivity": 2.0,            #W/m/K, (2)
    "specific_heat": 920.,           #J/kg K, (3)
    "compressibility": 0,        #Pa^-1
    "expansivity": 1.4e-5,          #°C^-1, (2)
    "conductivity_dry": 2.0,        #W/m/K, (2)

}

ini_pres = 3.5e6 


#Rock parameters
parameters["rocks"] = {
    "TANK": { 
        "initial_condition": [ini_pres,0.01735, 10.5,15],  #pressure of 3.5 MPa, NaCl mass fraction of 1.735% (Pearson), half saturated gas and 15°C. 
        "specific_heat":920e20, #constant temperature in injection well by making heat capacity huge
       # "relative_permeability": {
            "id": 5, #van genuchten 
            "parameters": [],
        },
        "capillarity": {
            "id": 8, #van genuchten 
            "parameters": []
        },
    }


parameters["options"] = {
    "n_cycle": -19,
    "n_cycle_print": 9999,
    "t_ini": time_zero,
    "t_max": time_final,
    "t_steps": 6,
    "t_step_max": 120,
    
    "t_reduce_factor": 4,
    "eps1": 1.0e-8,
    "gravity": 9.8,
}




parameters['extra_options'] = {
        1: 1,
        2: 2,
        3: 1,
        4: 1,
        5: 5,
        11: 0,
        12: 2,
        17: 9,
        21: 8
}



labels = mesh.labels
mask = materials == "TANK"
indexes = np.where(mask)[0]

    
def generators():

    parameters['generators'] = []    
    for i in range(len(labels)-1): 
        print(labels[i])

        rates = [1e-8, 1e-8]
        times = [time_zero, time_final]

        generator = {
            "label": labels[i],  # Use labels[i] instead of labels
            "type": "COM3",
            "times": times,   # Use times[i] instead of times
            "rates": rates,  # Use rates[i] instead of rates
            "specific_enthalpy": list(np.zeros(len(times))),
        }
        parameters['generators'].append(generator)

    return rates, times


#rates, times = generators() 


#Output parameters
#parameters["output"] = {
#    "variables": [
#        {"name": "saturation", "options": 0},
#        {"name": "coordinate"},
#        {"name": "pressure", "options": 0},
#        {"name": "capillary", "options": 1},
#        {"name": "density", "options": 0},
#        {"name": "viscosity", "options": 0},
#        {"name": "flow rate", "options":[1,2]},
#        {"name": "flow rate", "options":[2,1]}
#    ],
#}       


parameters["element_history"] = list(labels)

mesh.write("/Users/matthijsnuus/Desktop/FS-C/InjectionRates/mesh.pickle")
toughio.write_input("/Users/matthijsnuus/Desktop/FS-C/InjectionRates/INFILE", parameters)  
mesh.write_tough("/Users/matthijsnuus/Desktop/FS-C/InjectionRates/MESH", incon=True)
mesh.write("/Users/matthijsnuus/Desktop/FS-C/InjectionRates/mesh.vtk")
    
