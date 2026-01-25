# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 16:48:54 2024

@author: matthijs
"""

import numpy as np
import pandas as pd
import toughio


rates_csv = pd.read_csv(
    "/Users/matthijsnuus/Desktop/FS-C/model/hymar_gas_injection/tank_model/model_run/filtered_gasrate_from_conne.csv"
)

rates_csv["TimeElapsed"] = pd.to_numeric(rates_csv["TimeElapsed"], errors="coerce")
rates_csv["GAS_INJEC"] = pd.to_numeric(rates_csv["GAS_INJEC"], errors="coerce")
rates_csv = rates_csv.dropna(subset=["TimeElapsed", "GAS_INJEC"]).reset_index(drop=True)

# sort + shift time to start at 0
rates_csv = rates_csv.sort_values("TimeElapsed").reset_index(drop=True)


time_zero =  rates_csv['TimeElapsed'][0]
time_final = rates_csv['TimeElapsed'].iloc[-2]

time_step = 5
time_max = 150

mesh = toughio.read_mesh("/Users/matthijsnuus/Desktop/FS-C/model/hymar_gas_injection/mesh stuff/gas_injec_tough.msh")


back_BC = 2e6 


materials = (mesh.materials )
bcond = (materials == "PRESB").astype(int)
mesh.add_cell_data("boundary_condition", bcond)



mesh.write_tough("/Users/matthijsnuus/Desktop/FS-C/model/hymar_gas_injection/2_TH/MESH") #, incon=True)
mesh.write("/Users/matthijsnuus/Desktop/FS-C/model/hymar_gas_injection/2_TH/mesh.pickle")

times_list = np.linspace(time_zero, time_final-10, 20)

parameters = {
    "title": "hymar gas",
    "eos": "eos5",
    "isothermal": True,
    "start": True,
    "times": times_list, 
}





#INITIAL CONDITIONS 
ini_pore_pressure = 2.1e6#0.432e6 #Pa, 
ini_gas_content = 0.0 #-, ...
temperature = 19 #°C, (1)

#CAPILLARY PRESSURE AND RELATIVE PERMEABILITY VARIABLES     
pore_size_distr_index =0.5 #-, (2), symbol: λ
S_lr = 0.01 #-, (2), total trapped water 
S_ls = 1 #-, (2), liquid saturation  
S_gr = 0.0 #-, Guess?, total trapped gas 
P0 = 18e6 #1.47e7 #Pa, R.Senger
Pmax = 1e12 #Pa, guessed from (2),

#values from Antonio for ICP & IRP
icp11 = [1.67, 1.8e7, 0, 0.0, 0.0, 0.0, 0.01]
irp11 = [0.5, 0.0, 0]


parameters["default"] = {
    "density": 2500.,                     #kg/m3
    "porosity": 0.12 ,                    #- 
    "permeability": [1e-20,1e-20,3e-20], #m2  
    "conductivity": 2.0,                  #W/m/K
    "specific_heat": 920.,                #J/kg K
    #"compressibility": 5e-9,             #Pa^-1
    "expansivity": 1.4e-5,                #°C^-1
    "conductivity_dry": 2.0,              #W/m/K

    "initial_condition": [ini_pore_pressure, ini_gas_content,temperature],
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
    "PPINJ": {
        "density": 2500,
        "porosity": 0.98, 
        "initial_condition": [ini_pore_pressure,1,temperature],
        "permeability": [1e-17, 1e-17, 1e-17],
        "specific_heat":920e20, #constant temperature in injection well by making heat capacity huge
        "relative_permeability": {
            "id": 3, #van genuchten 
            "parameters": [1,0],
        },
        "capillarity": {
            "id": 8, #van genuchten 
            "parameters": []
        },  
    },
    "PPOUT": {
        "porosity": 0.16, 
    
    },
    "CLAY": {
        "porosity": 0.16, 
    },    
    "STEEL": {
        "relative_permeability": {
            "id": 11, #Modified van genuchtn 
            "parameters": [0.5, 0.0, 0],
        },
        "capillarity": {
            "id": 11, #Modified van genuchten 
            "parameters": [1.67, 1.8e10, 0, 0.0, 0.0, 0.0, 0.01],
        },
    },

    "GRD_B": {
        "relative_permeability": {
            "id": 3, #van genuchten 
            "parameters": [0,1],
        },
        "capillarity": {
            "id": 8, #van genuchten 
            "parameters": []
        }, 
    },
    "GRD_T": {
        "relative_permeability": {
            "id": 3, #van genuchten 
            "parameters": [0,1],
        },
        "capillarity": {
            "id": 8, #van genuchten 
            "parameters": []
        }, 
    },
    "BUFFR": {
        "porosity": 0.14, #-, (4) 
        "permeability": [1e-13, 1e-13, 1e-13],
    },
    "PRESB": {
        "permeability": [1e-13, 1e-13, 1e-13],
        "initial_condition": [back_BC, ini_gas_content, temperature]
    },
    


}

parameters["options"] = {
    "n_iteration": 9,
    "n_cycle": -19,
    "n_cycle_print": 9999,
    "t_ini": time_zero,
    "t_max": time_final,
    "t_steps": time_step,
    "t_step_max":  time_max,
    
    "t_reduce_factor": 8,
    "eps1": 1.0e-8,
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

parameters["output"] = {
    "variables": [
        {"name": "absolute", "options": 0},
        {"name": "coordinate"},
        {"name": "pressure"},
        {"name": "saturation"},
    ],
}

mesh = toughio.read_mesh("/Users/matthijsnuus/Desktop/FS-C/model/hymar_gas_injection/2_TH/mesh.pickle")


def relative_volumes():
    idx = mesh.near((0, 0, 0))  # nearest cell in whole mesh

    if materials[idx] == 'PPINJ':
        
        return mesh.labels[idx]

injec_label = relative_volumes()



def generators():


    parameters['generators'] = []
    
    times = rates_csv["TimeElapsed"].to_list()
    rates = rates_csv["GAS_INJEC"].to_list()   # <-- from your new CSV


    generator = {
        "label": injec_label,
        "type": "COM2",
        "times": times,
        "rates": rates,
        "specific_enthalpy": list(np.zeros(len(times))),
    }
 
    
    parameters['generators'].append(generator)
    
    return rates, times

rates, times = generators() 

L = 0.074
z_vals = np.linspace(0.0, L, 12)[1:-1]  # 10 internal points
ref_points = [str(mesh.labels[mesh.near((0, 0, float(z)))]) for z in z_vals]
ref_points.append(str(injec_label))

parameters["element_history"] = ref_points

toughio.write_input("/Users/matthijsnuus/Desktop/FS-C/model/hymar_gas_injection/2_TH/INFILE", parameters)  
