#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 24 08:41:29 2025

@author: matthijsnuus
"""

import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 

bfsb1 = pd.read_csv('/Users/matthijsnuus/Downloads/MtTerriInjectionMay2023_BFSB1_PT_1Hz.csv', sep=',').dropna()

utc = pd.to_datetime(bfsb1['UTC'])
pres29 =  bfsb1.iloc[:,1]
pres31 =  bfsb1.iloc[:,2]
pres35 =  bfsb1.iloc[:,3]
pres42 =  bfsb1.iloc[:,4]


fig, ax = plt.subplots(figsize=(9,5))
ax.plot(utc, pres42, label="42.2 m")
ax.plot(utc, pres35, label="34.9 m")
ax.plot(utc, pres31, label="31.0 m")
ax.plot(utc, pres29, label="29.0 m")
plt.legend()
ax.set_ylabel('Pressure [bar]')
plt.show()


print(pres42[10])