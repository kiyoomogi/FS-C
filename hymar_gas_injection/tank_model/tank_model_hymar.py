# -*- coding: utf-8 -*-
"""
Created on Thu Apr 10 11:51:01 2025

@author: matthijs
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np 
import toughio 


interface_area = 1.26E-5

rates_dummy = pd.read_csv(
    "/Users/matthijsnuus/Desktop/FS-C/model/hymar_gas_injection/tank_model/filtered_water_pressure_rate.csv"
)

# Clean column names (just in case)
rates_dummy.columns = rates_dummy.columns.str.strip()

# Rename your rate column so your model always uses "Rate"
rates_dummy = rates_dummy.rename(columns={
    "Water Injection Rate (kg/s)": "Rate",
    "Gas Pressure (MPa)": "GasPressure_MPa"
})


starttimes = {1:[rates_dummy['TimeElapsed'].values[0], 8.80613e+06],    #refill
              2:[8.80613e+06, 1.15730e+07],
              }

time_zero = 203 * (60 * 60 * 24)
time_final = rates_dummy['TimeElapsed'].iloc[-2]

parameters = {
    "title": "meshmaker-dummy",
    "eos": "eos5",
    "isothermal": True,
    "start": True,
    "times": list(np.linspace(time_zero,time_final,400))}




a = {
    "type": "nx",
    "n_increment": 1,
    "sizes": 0.0669,
}
b = {
    "type": "ny",
    "n_increment": 1,
    "sizes": 0.0669,
}
c = {
    "type": "nz",
    "n_increment": 1,
    "sizes": 0.0669,
}
d = {
    "type": "nx",
    "n_increment": 1,
    "sizes": 0.02,
}


parameters['meshmaker'] = {
    "type": "xyz",
    "parameters": [a,d,b,c],
    "angle": 0.,
}

toughio.write_input("/Users/matthijsnuus/Desktop/FS-C/model/hymar_gas_injection/tank_model/meshmaker", parameters)
mesh = toughio.meshmaker.from_meshmaker("/Users/matthijsnuus/Desktop/FS-C/model/hymar_gas_injection/tank_model/meshmaker", material='dfalt')
mesh.write_tough("/Users/matthijsnuus/Desktop/FS-C/model/hymar_gas_injection/tank_model/MESH")

del parameters['meshmaker']


mesh.cell_data['material'] = [1,2] 
mesh.add_material("TANK", 1)
mesh.add_material("INJEC", 2)
materials = mesh.materials

#INITIAL CONDITIONS 
temperature = 19. #°C, (1)


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

ini_pres = 2.101e6 


#Rock parameters
parameters["rocks"] = {

    "INJEC": {
        "initial_condition": [ini_pres,1,temperature],
        "compressibility": 0,
        "relative_permeability": {
            "id": 3, #van genuchten 
            "parameters": [0,1],
        },
        "capillarity": {
            "id": 8, #van genuchten 
            "parameters": []
        },
    },
    "TANK": { 
        "initial_condition": [ini_pres, 1,15],
        "specific_heat":920e20, #constant temperature in injection well by making heat capacity huge
        "relative_permeability": {
            "id": 5, #van genuchten 
            "parameters": [],
        },
        "capillarity": {
            "id": 8, #van genuchten 
            "parameters": []
        },
    }
}

parameters["options"] = {
    "n_cycle": -19,
    "n_cycle_print": 9999,
    "t_ini": time_zero,
    "t_max": time_final,
    "t_steps": 6,
    "t_step_max": 120,
    
    "t_reduce_factor": 4,
    "eps1": 1.0e-6,
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

parameters['more_options'] = {
        1: 2
}


labels = mesh.labels
mask = materials == "TANK"
indexes = np.where(mask)[0]

    
def generators():

    parameters['generators'] = []    
    for i in range(len(labels)-1): 
        print(labels[i])

        rates = (rates_dummy['Rate'] * (1) ).to_list()
        times = rates_dummy['TimeElapsed'].to_list()

        generator = {
            "label": labels[i],  # Use labels[i] instead of labels
            "type": "COM1",
            "times": times,   # Use times[i] instead of times
            "rates": rates,  # Use rates[i] instead of rates
            "specific_enthalpy": list(np.zeros(len(times))),
        }
        parameters['generators'].append(generator)

    return rates, times


rates, times = generators() 


#Output parameters
parameters["output"] = {
    "variables": [
        {"name": "saturation", "options": 0},
        {"name": "coordinate"},
        {"name": "pressure", "options": 0},
        {"name": "capillary", "options": 1},
        {"name": "density", "options": 0},
        {"name": "viscosity", "options": 0},
        {"name": "flow rate", "options":[1,2]},
        {"name": "flow rate", "options":[2,1]}
    ],
}       



parameters["element_history"] = list(labels)


mesh.write("/Users/matthijsnuus/Desktop/FS-C/model/hymar_gas_injection/tank_model/model_run/mesh.pickle")
mesh.write("/Users/matthijsnuus/Desktop/FS-C/model/hymar_gas_injection/tank_model/model_run/mesh.vtk")
toughio.write_input("/Users/matthijsnuus/Desktop/FS-C/model/hymar_gas_injection/tank_model/model_run/INFILE", parameters)  
mesh.write_tough("/Users/matthijsnuus/Desktop/FS-C/model/hymar_gas_injection/tank_model/model_run/MESH")

mesh_dict = toughio.read_input("/Users/matthijsnuus/Desktop/FS-C/model/hymar_gas_injection/tank_model/model_run/MESH")
mesh_dict["connections"]['A11 0A11 1']['interface_area'] = interface_area

toughio.write_input("/Users/matthijsnuus/Desktop/FS-C/model/hymar_gas_injection/tank_model/model_run/MESH", mesh_dict)  

