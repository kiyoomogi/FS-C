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

time_zero =  0
time_final = rates_csv["TimeElapsed"].iloc[-1] 


if incon == 'ns': 
    ns = toughio.read_output("/Users/matthijsnuus/Desktop/FS-C/model/natural_state/SAVE")
    incon1 = ns.data

mesh = toughio.read_mesh("/Users/matthijsnuus/Desktop/FS-C/model/mesh/FSC_mesh_simple.msh")
mesh.cell_data['material'] = mesh.cell_data['material'].ravel()

z_centers = mesh.centers[:,2]
z_top = np.amax(z_centers)
z_bot = np.amin(z_centers)

p0 = rates_csv['zone P [MPa]'][0]

top_BC_value = p0 * 1e6 - 1000 * 9.81 * z_top - 165000  #slightly lower initial conditions due to initial injection
bot_BC_value = p0 * 1e6 + 1000 * 9.81 * z_top - 165000


#Add material
mesh.add_material("CLAY ", 1)
mesh.add_material("FAULT", 2)
mesh.add_material("INJEC", 3)
mesh.add_material("BNDTO", 4)
mesh.add_material("BNDBO", 5)

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


parameters = {
    "title": "injection model",
    "eos": "eco2n",
    "isothermal": True,
    "start": True,
    #"times": (list(np.linspace(time_zero, time_final, 100))), 
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
    "permeability": [6e-17, 6e-17, 6e-17], #m2  
    "conductivity": 2.0,                  #W/m/K
    "specific_heat": 920.,                #J/kg K
    "compressibility": 2e-9,             #Pa^-1
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
        "porosity": 0.999, 
        "permeability": [1e-15,1e-14,1e-15],
        "specific_heat":920e20, #constant temperature in injection well by making heat capacity huge
        #"compressibility": 0e-10, #2.94e-7,
        #"relative_permeability": {
        #    "id": 3, #van genuchten 
        #    "parameters": [1,0],
        #},
        #"capillarity": {
        #    "id": 8, #van genuchten 
        #    "parameters": []
        #},  
    },
    "CLAY ": {
        #"tortuosity": 0.8, #-, (4) 
        #"initial_condition": [ini_pore_pressure,ini_gas_content,temperature],
    },
    "FAULT": {
        "porosity": 0.12,
        "compressibility": 8e-9,             #Pa^-1
        "permeability": [6e-17, 6e-17, 6e-17]
    },
    "BNDTO": {"initial_condition": [top_BC_value, 0.017203, ini_gas_content, temperature]},
    "BNDBO": {"initial_condition": [bot_BC_value, 0.017203, ini_gas_content, temperature]},

}

parameters["options"] = {
    #"n_iteration": 9,
    "n_cycle": 9999,
    "n_cycle_print": 9999,
    "t_ini": time_zero,
    "t_max": time_final,
    "t_steps": 1,
    "t_step_max":  60 * 5,
    
    "t_reduce_factor": 4,
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



mesh = toughio.read_mesh("/Users/matthijsnuus/Desktop/FS-C/model/injection_model/mesh.pickle")

def relative_volumes():
    injec_labels = []
    volume_list = []
    for i in (range(len(materials))):
        if materials[i] == 'INJEC':
            label = mesh.labels[i]
            volume = mesh.volumes[i]
            injec_labels.append(str(label))
            volume_list.append(volume)
        
    rel_volumes =   np.array(volume_list) / sum(volume_list)  

    return rel_volumes,injec_labels, volume_list

rel_volumes,injec_labels, volume_list = relative_volumes()


def generators():


    parameters['generators'] = []
    
    rates = None  # Initialize rates
    times = None  # Initialize times

    for i in range(len(rel_volumes)): 
        rel_vol = rel_volumes[i]
        rates = (rates_csv['net flow [kg/s]'] * 1* (rel_vol)).to_list()
        #rates_co2 = (rates_csv['CO2 rate [kg/s]'] * 1 * (rel_vol)).to_list()
        times = rates_csv['TimeElapsed'].to_list()

        generator = {
            "label": injec_labels[i],
            "type": "COM1",
            "times": times,
            "rates": rates,
            "specific_enthalpy": list(np.zeros(len(times))),
        }
        parameters['generators'].append(generator)
        
        #generator = {
        #    "label": labels[i],
        #    "type": "COM3",
        #    "times": times,
        #    "rates": rates_co2,
        #    "specific_enthalpy": list(np.zeros(len(times))),
        #}
        #parameters['generators'].append(generator)

    return rates, times

rates, times = generators() 

ref_points = injec_labels[::30]
parameters["element_history"] = ref_points

toughio.write_input("/Users/matthijsnuus/Desktop/FS-C/model/injection_model/INFILE", parameters)  
 

