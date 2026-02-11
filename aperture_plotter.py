#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 21 10:02:15 2026
@author: matthijsnuus

This code calculates the fracture aperture based on elastic, shear and tensile
contributions. It then calculates permeability based on the ratio between
initial aperture bi and updated aperture b:
    k = k0 * (b/bi)^3
"""

import numpy as np
import matplotlib.pyplot as plt

# -------------------------------------------------
# Inputs
# -------------------------------------------------
br = 20e-6              # m
bmax = 600e-6            # m
alpha = 0.8             # 1/MPa  (works with sigma in MPa)
sigma_n = np.linspace(0, 7.2, 100)  # MPa
sigma_ni = 4.2          # MPa  (initial effective normal stress)

e_pT = 0        # tensile plastic strain (scalar)
e_pS = np.array([0.0, 1e-4, 5e-4, 1e-3, 2.5e-3])  # shear plastic strain cases
psi = 10             # degrees
n = 1
w = 1.8                 # m
k0 = 5e-18           # m^2

sf = n / w              # fracture spacing factor

# -------------------------------------------------
# Initial + elastic aperture
# -------------------------------------------------
bi = br + bmax * np.exp(-alpha * sigma_ni)      # scalar (m)
bel = br + bmax * np.exp(-alpha * sigma_n)      # (100,) (m)

# -------------------------------------------------
# Tensile + shear aperture contributions
# -------------------------------------------------
bop = e_pT * w  # scalar (m)

# shear aperture shift for each e_pS in m
bsh = e_pS * np.tan(np.deg2rad(psi)) / sf  # (len(e_pS),)

# ---- cap shear aperture at 100 µm ----
bsh_max = 200e-6  # m
bsh = np.clip(bsh, 0.0, bsh_max)  # keep it non-negative and <= 100 µm


# -------------------------------------------------
# Total aperture for each shear case
# Make bel shape (1,100) and bsh shape (3,1)
# -------------------------------------------------
b = bel[None, :] + bsh[:, None] + bop           # (3,100)

# -------------------------------------------------
# Permeability update
# -------------------------------------------------
kf = b / bi                                     # (3,100)
k = k0 * (kf ** 3)                              # (3,100)

# Convert aperture to micrometers for plotting
b_um = b * 1e6                                  # (3,100)

# -------------------------------------------------
# Plot: 3x1
# -------------------------------------------------
plt.rcParams.update({"font.size": 17})  # global default

fig, ax = plt.subplots(1, 3, figsize=(13, 8), sharex=False)

for i, eps_s in enumerate(e_pS):
    label = f"εpS = {eps_s:.1e}"

    ax[0].plot(b_um[i, :], sigma_n, label=label, linewidth=2.5)
    ax[1].plot(b_um[i, :], k[i, :], label=label, linewidth=2.5)
    ax[2].plot(sigma_n, k[i, :], label=label, linewidth=2.5)

# ---- plot formatting ----
ax[0].invert_yaxis()
ax[0].set_xlabel("Aperture b (µm)")
ax[0].set_ylabel("Effective normal stress σ'n (MPa)")
ax[0].grid(True, linestyle=":")
ax[0].set_title("Aperture vs Effective Stress")

ax[1].set_xlabel("Aperture b (µm)")
ax[1].set_ylabel("Permeability k (m²)")
ax[1].set_yscale("log")
ax[1].grid(True, linestyle=":")
ax[1].set_title("Permeability vs Aperture")

ax[2].set_xlabel("Effective normal stress σ'n (MPa)")
ax[2].set_ylabel("Permeability k (m²)")
ax[2].set_yscale("log")
ax[2].grid(True, linestyle=":")
ax[2].set_title("Permeability vs Effective Stress")

for a in ax:
    a.legend(fontsize=17)  # keep legends consistent

plt.tight_layout()
