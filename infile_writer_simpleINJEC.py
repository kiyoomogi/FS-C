# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 16:48:54 2024

@author: matthijs
"""

import numpy as np
import pandas as pd
import toughio


incon = 'ns' #simulation_point or ns

rates_csv = pd.read_csv("/Users/matthijsnuus/Desktop/FS-C/model/injection_rates/filtered_FSC_injecrates.csv", delimiter=',', index_col=[0])
#rates_csv.loc[rates_csv.index[0], "net flow [kg/s]"] = 0.0

hydr_test = False
stage = 0 #0, 1, 2
sec_stage_1 = 15

if hydr_test == True and stage == 0:
        time_zero = 23620
        time_final = 23620 + 55 * 60
        time_step = 0.5
        time_max = 5
elif hydr_test == False and stage == 11:
        time_zero = 94878 
        time_final = 94933.0
        time_step = 0.8
        time_max = 1.3

elif stage == 0:
    time_zero =  94878 
    time_final = 94878 + 3600 * 4
    time_step = 0.5
    time_max = 2
elif stage == 2:
    time_zero =  47580
    time_final = 123574.7 + 20 #rates_csv["TimeElapsed"].iloc[-1] 
    time_step = 1
    time_max = 60
elif stage == 3:
    time_zero =  123574.7 + 20
    time_final =  142626.4 #rates_csv["TimeElapsed"].iloc[-1] 
    time_step = 0.5
    time_max = 10
elif stage == 4:
    time_zero =  142626.4
    time_final = rates_csv["TimeElapsed"].iloc[-1] 
    time_step = 1
    time_max = 60


if incon == 'ns': 
    ns = toughio.read_output(f"/Users/matthijsnuus/Desktop/FS-C/model/incons/SAVE{stage}")
    #ns.data['X1'][ns.data['porosity'] == 0.99] = 0.3e6
    incon1 = ns.data
    print()


#mesh = toughio.read_mesh("/Users/matthijsnuus/Desktop/FS-C/model/mesh/FSC_mesh_cyl.msh")
mesh = toughio.read_mesh("/Users/matthijsnuus/Desktop/FS-C/model/coupled_model/mesh.f3grid")



bot_BC_value = np.amax(incon1['X1'])
top_BC_value = np.amin(incon1['X1'])

#Add material
#mesh.add_material("EDZ  ", 1)
#mesh.add_material("CLAY ", 2)
#mesh.add_material("FAULT", 3)
#mesh.add_material("BNDTO", 4)
#mesh.add_material("BNDBO", 5)

if incon == 'ns':
    incon = np.full((len(incon1['X1']), 4), -1.0e9)
    incon[:, 0] = incon1['X1']
    incon[:, 1] = incon1['X2']
    incon[:, 2] = incon1['X3']
    incon[:, 3] = incon1['X4']
    mesh.add_cell_data("initial_condition", incon)


materials = (mesh.materials )
bcond = (materials == "BNDTO").astype(int) + (materials == "BNDBO").astype(int) 
mesh.add_cell_data("boundary_condition", bcond)


unique_materials = set((materials).tolist())


mesh.write_tough("/Users/matthijsnuus/Desktop/FS-C/model/injection_model/MESH", incon=True)
mesh.write("/Users/matthijsnuus/Desktop/FS-C/model/injection_model/mesh.pickle")

times_list1 = np.arange(time_zero, time_zero+30, 5)
times_list2 = np.arange(time_zero + 31, time_final, 240)
times_list = np.append(times_list1, times_list2)

parameters = {
    "title": "injection model",
    "eos": "eco2n",
    "isothermal": True,
    "start": True,
    #"times": times_list, 
}





#INITIAL CONDITIONS 
ini_pore_pressure = 0.45e6#0.432e6 #Pa, 
ini_NACL = 0.017203
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
icp11 = [1.67, 1.8e7, 0, 0.0, 0.0, 0.0, 0.01]
irp11 = [0.5, 0.0, 0]

parameters["default"] = {
    "density": 2500.,                     #kg/m3
    "porosity": 0.12 ,                    #- 
    "permeability": [3e-18,3e-18,3e-18], #m2  
    "conductivity": 2.0,                  #W/m/K
    "specific_heat": 920.,                #J/kg K
    "compressibility": 5e-9,             #Pa^-1
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
#    "INJEC": {
#        "density": 2500,
#        "porosity": 0.98, 
#        "permeability": [1e-13, 1e-13, 1e-13],
#        "specific_heat":920e20, #constant temperature in injection well by making heat capacity huge
        #"relative_permeability": {
        #    "id": 3, #van genuchten 
        #    "parameters": [1,0],
        #},
        #"capillarity": {
        #    "id": 8, #van genuchten 
        #    "parameters": []
        #},  
#    },
    "CLAY": {
        #"tortuosity": 0.8, #-, (4) 
        #"initial_condition": [ini_pore_pressure,ini_gas_content,temperature],
    },

    "EDZ": {
        "porosity": 0.14, #-, (4) 
        "permeability": [1e-13, 1e-13, 1e-13],
    },
    "FAULT": {
        "porosity": 0.14,
        #"compressibility": 8e-9,             #Pa^-1
        "permeability": [2e-14, 2e-15, 2e-14]
        #"permeability": [6.5e-17,5e-17,5e-17]
    },

    "BNDTO": {"initial_condition": [top_BC_value, ini_NACL, ini_gas_content, temperature]},
    "BNDBO": {"initial_condition": [bot_BC_value, ini_NACL, ini_gas_content, temperature]},

}

parameters["options"] = {
    "n_iteration": 9,
    "n_cycle": 9999,
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
        11: 2,   #0 or 2 
        12: 2,
        17: 9,
        21: 8
}

parameters["output"] = {
    "variables": [
        {"name": "absolute", "options": 0},
        {"name": "coordinate"},
    ],
}

mesh = toughio.read_mesh("/Users/matthijsnuus/Desktop/FS-C/model/injection_model/mesh.pickle")


def relative_volumes():
    idx = mesh.near((0, 0.1, 0))  # nearest cell in whole mesh

    if materials[idx] == 'EDZ':
        
        return mesh.labels[idx]

injec_label = relative_volumes()



def generators():


    parameters['generators'] = []
    
    rates = (rates_csv['net flow cor [kg/s]']).to_list()
    times = rates_csv['TimeElapsed'].to_list()

    generator = {
        "label": injec_label,
        "type": "COM1",
        "times": times,
        "rates": rates,
        "specific_enthalpy": list(np.zeros(len(times))),
    }
    parameters['generators'].append(generator)
    
    return rates, times

rates, times = generators() 

ref_points = [injec_label]
ref_points.append(str(mesh.labels[mesh.near((7.434, 8.137, -0.900))]))
ref_points.append(str(mesh.labels[mesh.near((1.904, 5.158, 7.779))]))


parameters["element_history"] = ref_points

toughio.write_input("/Users/matthijsnuus/Desktop/FS-C/model/injection_model/INFILE", parameters)  
 

