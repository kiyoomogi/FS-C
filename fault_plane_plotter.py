#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 23 09:30:53 2025

@author: matthijsnuus
"""

import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt


b1_df = pd.read_csv('/Users/matthijsnuus/Desktop/FS-C/borehole_locations/B1_location.csv' , sep='\s+')
b2_df = pd.read_csv('/Users/matthijsnuus/Desktop/FS-C/borehole_locations/B2_location.csv' ,sep='\s+')

view_angle = 60


fig = plt.figure(figsize=(10, 8), dpi=150, constrained_layout=True)
ax = fig.add_subplot(projection='3d')

# Plot a sin curve using the x and y axes.
b2x = b2_df['X']
b2y = b2_df['Y']
b2z = b2_df['depths'] 

b1x = b1_df['X']
b1y = b1_df['Y']
b1z = b1_df['depths'] 

# ---- Add a dipping plane that cuts B2 at depth = 40.5 m
strike_deg = 46     # from North, clockwise
dip_deg    = 55.0      # from horizontal, downward
target_depth = 40.5    # meters, positive downward

phi = np.deg2rad(strike_deg)
dip = np.deg2rad(dip_deg)

# Ensure B2 is sorted by depth and get (x0,y0) at z0=target_depth via interpolation
b2_sorted = b2_df.sort_values("depths")
z_arr = b2_sorted["depths"].to_numpy()
x_arr = b2_sorted["X"].to_numpy()
y_arr = b2_sorted["Y"].to_numpy()

# If B2 is vertical, x and y are constant; interpn still works
# Clip target into data range to avoid NaNs
z_min, z_max = z_arr.min(), z_arr.max()
z0 = np.clip(target_depth, z_min, z_max)

# 1D interpolation of x(z) and y(z)
x0 = np.interp(z0, z_arr, x_arr)
y0 = np.interp(z0, z_arr, y_arr)

# Build a grid around (x0,y0) — adjust 'halfspan' to taste
halfspan = 20.0  # meters
nx, ny = 30, 30  # grid resolution
Xg = np.linspace(x0 - halfspan, x0 + halfspan, nx)
Yg = np.linspace(y0 - halfspan, y0 + halfspan, ny)
Xg, Yg = np.meshgrid(Xg, Yg)

# Plane formula in (E,N,Depth) with Z positive downward
tan_dip = np.tan(dip)
Zg = z0 + tan_dip * np.cos(phi) * (Xg - x0) - tan_dip * np.sin(phi) * (Yg - y0)

# Plot the plane
ax.plot_surface(Xg, Yg, Zg, alpha=0.35, linewidth=0, antialiased=False, color='orange')

# ---- Intersect plane with B1 polyline
# Ensure B1 is ordered by depth (z) so segments are well-behaved
b1_sorted = b1_df.sort_values("depths")
x1 = b1_sorted["X"].to_numpy()
y1 = b1_sorted["Y"].to_numpy()
z1 = b1_sorted["depths"].to_numpy()

# Plane residual f(x,y,z) = 0 when point lies on the plane
# From: z = z0 + tan_dip*cos(phi)*(x-x0) - tan_dip*sin(phi)*(y-y0)
# => f = z - z0 - tan_dip*cos(phi)*(x-x0) + tan_dip*sin(phi)*(y-y0)
def plane_residual(x, y, z, x0=x0, y0=y0, z0=z0, tan_dip=tan_dip, phi=phi):
    return z - z0 - tan_dip*np.cos(phi)*(x - x0) + tan_dip*np.sin(phi)*(y - y0)

f = plane_residual(x1, y1, z1)

# Find segments where f changes sign (or hits zero) => intersection(s)
idxs = []
for i in range(len(f)-1):
    fi, fj = f[i], f[i+1]
    if fi == 0.0:
        idxs.append((i, i))        # vertex exactly on plane
    elif fi * fj < 0.0:
        idxs.append((i, i+1))      # sign change -> crosses between i and i+1

intersections = []
for i, j in idxs:
    if i == j:
        # Point i lies exactly on the plane
        xi, yi, zi = x1[i], y1[i], z1[i]
        t = 0.0
    else:
        # Linear interpolation on segment i->j using residuals
        fi, fj = f[i], f[j]
        t = fi / (fi - fj)  # fraction from i to j
        xi = x1[i] + t*(x1[j] - x1[i])
        yi = y1[i] + t*(y1[j] - y1[i])
        zi = z1[i] + t*(z1[j] - z1[i])
    intersections.append((xi, yi, zi, i, j, t))

if not intersections:
    print("No intersection: B1 does not cross the plane within its sampled interval.")
else:
    for (xi, yi, zi, i, j, t) in intersections:
        print(f"Plane ∩ B1 at X={xi:.3f}, Y={yi:.3f}, depth={zi:.3f} m "
              f"(segment {i}->{j}, t={t:.3f})")
        # Plot it
        ax.scatter([xi], [yi], [zi], s=80, marker='o', color='green', zorder=5)
        #ax.text(xi+2, yi, zi, f"intersect B1 @{zi:.1f}", color='green', zdir=None)
        ax.text(
            xi+3, yi, zi,
            f"intersect B1 @{zi:.1f} m",
            color="green",
            zdir=None,
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.9)
        )


# Mark the intersection point on B2 at 40.5 m
ax.scatter([x0], [y0], [z0], s=60, color='blue')
ax.text(
    x0-15, y0, z0,
    "intersect B2 @40.5 m",
    color="blue",
    zdir=None,
    bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.9)
)

ax.plot(b1x, b1y, b1z, zdir='z', label='BFS-B1', color='green')
ax.plot(b2x, b2y, b2z, zdir='z', label='BFS-B2', color='blue')



# Make legend, set axes limits and labels
ax.legend()
ax.set_xlabel('X (East)')
ax.set_ylabel('Y (North)')
ax.set_zlabel('Z (Depth)')

ax.invert_zaxis()

# Customize the view angle so it's easier to see that the scatter points lie
# on the plane y=0
ax.view_init(elev=15., azim=-view_angle, roll=0)

plt.savefig('/Users/matthijsnuus/Desktop/FS-C/borehole_locations/boreholes_locations.png', bbox_inches="tight", pad_inches=0.2, dpi=200)
plt.show()


# After you compute an intersection on B1 as (xi, yi, zi) ...

# Put the plane∩B2 point at the origin (0,0,0)
xi_loc = xi - x0
yi_loc = yi - y0
zi_loc = zi - z0

print(f"B1 intersection in origin-shifted coords: ({xi_loc:.3f}, {yi_loc:.3f}, {zi_loc:.3f})")
