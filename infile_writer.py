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


stage = 0 #0, 1, 2
sec_stage_2 = 67

if stage == 0: 
    time_zero = 0 
    time_final = 32480 + 67
    time_step = 1
    time_max = 60
elif stage == 1:
    time_zero =  32480 + sec_stage_2
    time_final = 47567  #rates_csv["TimeElapsed"].iloc[-1] 
    time_step = 1
    time_max = 60
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
    "permeability": [1e-18,1e-18,1e-18], #m2  
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
        "permeability": [1e-13, 1e-13,1e-13],
        "specific_heat":920e20, #constant temperature in injection well by making heat capacity huge
        "compressibility": 1e-99,             #Pa^-1
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
        #"compressibility": 8e-9,             #Pa^-1
        #"permeability": [2.5e-14, 2.5e-14, 2.5e-14]
        "permeability": [1e-15,1e-15,1e-15]
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
    "t_steps": time_step,
    "t_step_max":  time_max,
    
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


def conne_fault():
    mesh = toughio.read_input("/Users/matthijsnuus/Desktop/FS-C/model/injection_model/MESH")
    elements    = mesh["elements"]
    connections = mesh["connections"]

    # INJEC element names
    injec = {ename for ename, edata in elements.items() if edata.get("material") == "INJEC"}
    fault = {ename for ename, edata in elements.items() if edata.get("material") == "FAULT"}

    # element-name length (TOUGH classic: 5)
    elem_len = len(next(iter(elements)))
    e1_list = []
    for cname, cdata in connections.items():
        if len(cname) < 2*elem_len:   # skip weird keys
            continue
        e1 = cname[:elem_len]
        e2 = cname[elem_len:2*elem_len]

        if (e1 in injec) and (e2 in fault) or (e1 in fault) and (e2 in injec) or (e1 in injec) and (e2 in injec):
            e1_list.append(str(e2))
            
    return e1_list

e1_list = conne_fault()

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

sum(rel_volumes)
def generators():


    parameters['generators'] = []
    
    rates = None  # Initialize rates
    times = None  # Initialize times

    for i in range(len(rel_volumes)): 
        rel_vol = rel_volumes[i]
        rates = (rates_csv['net flow [kg/s]'] * rel_vol).to_list()
        rates_co2 = (rates_csv['CO2 rate [kg/s]'] * rel_vol).to_list()
        times = rates_csv['TimeElapsed'].to_list()

        generator = {
            "label": e1_list[i],
            "type": "COM1",
            "times": times,
            "rates": rates,
            "specific_enthalpy": list(np.zeros(len(times))),
        }
        parameters['generators'].append(generator)
        
        generator = {
            "label": e1_list[i],
            "type": "COM3",
            "times": times,
            "rates": rates_co2,
            "specific_enthalpy": list(np.zeros(len(times))),
        }
        parameters['generators'].append(generator)

    return rates, times

rates, times = generators() 

ref_points = injec_labels[::40]
ref_points.append(str(mesh.labels[mesh.near((14.668, 4.132, -3.507))]))
ref_points.append(str(mesh.labels[mesh.near((10.789, 4.052, -1.099))]))


parameters["element_history"] = ref_points

#label = mesh.labels[mesh.near((10.576, 8.696, -1.559))]


toughio.write_input("/Users/matthijsnuus/Desktop/FS-C/model/injection_model/INFILE", parameters)  
 

