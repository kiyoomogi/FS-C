#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt

FS = 18  # fontsize everywhere

# --------------------------
# Input data (MPa)
# --------------------------
data = {
    216: (2.38, 4.15),
    229: (2.24, 4.08),
    255: (2.18, 4.05),
    267: (2.13, 4.01),
    306: (1.97, 3.87),
}

theta_deg = 57.0
two_theta_rad = np.deg2rad(2 * theta_deg)  # 114 degrees

# Mohr-Coulomb parameters
c = 0.0  # MPa
phi_mc_deg = 18.0
phi_mc_rad = np.deg2rad(phi_mc_deg)

# Angle for TOP HALF of circle only (tau >= 0)
phi = np.linspace(0, np.pi, 400)

plt.figure(figsize=(13, 11))

# Track max sigma for setting envelope range nicely
sigma_max = 0.0

for day, (sig3, sig1) in data.items():
    center = 0.5 * (sig1 + sig3)
    radius = 0.5 * (sig1 - sig3)

    # Update max sigma (rightmost point of circle = sigma1)
    sigma_max = max(sigma_max, sig1)

    # Top half of Mohr circle
    sigma = center + radius * np.cos(phi)
    tau   = radius * np.sin(phi)

    # 2θ point
    sigma_pt = center + radius * np.cos(two_theta_rad)
    tau_pt   = radius * np.sin(two_theta_rad)

    # Plot circle and grab color
    line, = plt.plot(sigma, tau, linewidth=2, label=f"Day {day}")
    col = line.get_color()

    # Plot point in same color
    plt.plot(sigma_pt, tau_pt, "o", markersize=8, color=col)

# --------------------------
# Plot Mohr-Coulomb envelope
# τ = c + σ * tan(φ)
# --------------------------
sigma_env = np.linspace(0, sigma_max * 1.1, 300)
tau_env = c + sigma_env * np.tan(phi_mc_rad)

plt.plot(
    sigma_env,
    tau_env,
    "k--",
    linewidth=2,
    label=f"MC: c=0 MPa, φ={phi_mc_deg:.0f}°"
)

# --------------------------
# Formatting
# --------------------------
plt.xlabel(r"Effective normal stress $\sigma_n$ (MPa)", fontsize=FS)
plt.ylabel(r"Shear stress $\tau$ (MPa)", fontsize=FS)


plt.grid(True)
plt.legend(fontsize=FS)

ax = plt.gca()
ax.set_aspect("equal", adjustable="box")   # ✅ true circles
ax.tick_params(axis="both", labelsize=FS)

# ✅ x-axis must start at 0 MPa
ax.set_xlim(left=0-1)

plt.tight_layout()
plt.show()
