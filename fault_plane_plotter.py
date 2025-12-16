#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3D plot of boreholes B1, B2, B12 and a dipping plane that cuts B2 at
vertical depth = 40.5 m below B2 collar.

- X: Easting
- Y: Northing
- Z (plotted): vertical depth below B2 collar (D), positive downward
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# -------------------------------------------------------------------
# Load data
# -------------------------------------------------------------------
b1_df  = pd.read_csv('/Users/matthijsnuus/Desktop/FS-C/borehole_locations/B1_location.csv',  sep=r'\s+')
b2_df  = pd.read_csv('/Users/matthijsnuus/Desktop/FS-C/borehole_locations/B2_location.csv',  sep=r'\s+')
b12_df = pd.read_csv('/Users/matthijsnuus/Desktop/FS-C/borehole_locations/B12_location.csv', sep=r'\s+')

view_angle = -40  # azimuth angle for 3D view
MD_target_B1  = 42.2     # measured distance along B1 from collar [m]
MD_target_B12 = 43.565   # measured distance along B12 from collar [m]

# -------------------------------------------------------------------
# Define a common depth coordinate D = vertical depth below B2 collar
# -------------------------------------------------------------------
Z0 = b2_df["Z"].iloc[0]  # B2 collar elevation

for df in (b1_df, b2_df, b12_df):
    # Depth (m) below B2 collar, positive downward
    df["D"] = Z0 - df["Z"]

# Convenience aliases for plotting
b2x,  b2y,  b2z  = b2_df["X"],  b2_df["Y"],  b2_df["D"]
b1x,  b1y,  b1z  = b1_df["X"],  b1_df["Y"],  b1_df["D"]
b12x, b12y, b12z = b12_df["X"], b12_df["Y"], b12_df["D"]

# -------------------------------------------------------------------
# Plane definition: strike, dip, and target depth on B2
# -------------------------------------------------------------------
strike_deg   = 50.0   # from North, clockwise
dip_deg      = 55.0   # from horizontal, downward
target_depth = 40.97   # vertical depth below B2 collar (m), positive downward

phi = np.deg2rad(strike_deg)
dip = np.deg2rad(dip_deg)
tan_dip = np.tan(dip)

# -------------------------------------------------------------------
# Find point (x0, y0, D0) on B2 at vertical depth = target_depth
# -------------------------------------------------------------------
b2_sorted = b2_df.sort_values("D")
D_arr = b2_sorted["D"].to_numpy()
x_arr = b2_sorted["X"].to_numpy()
y_arr = b2_sorted["Y"].to_numpy()

D_min, D_max = D_arr.min(), D_arr.max()
D0 = np.clip(target_depth, D_min, D_max)

x0 = np.interp(D0, D_arr, x_arr)
y0 = np.interp(D0, D_arr, y_arr)

# -------------------------------------------------------------------
# Build plane grid in (X, Y, D)
# Plane equation in (E, N, depth D>0 downward):
#   D = D0 + tan(dip)*cos(strike)*(E - x0) - tan(dip)*sin(strike)*(N - y0)
# -------------------------------------------------------------------
halfspan = 20.0  # meters around (x0, y0)
nx, ny = 30, 30

Xg = np.linspace(x0 - halfspan, x0 + halfspan, nx)
Yg = np.linspace(y0 - halfspan, y0 + halfspan, ny)
Xg, Yg = np.meshgrid(Xg, Yg)

Dg = D0 + tan_dip * np.cos(phi) * (Xg - x0) - tan_dip * np.sin(phi) * (Yg - y0)

# -------------------------------------------------------------------
# Helper: plane residual and intersection finder
# -------------------------------------------------------------------
def plane_residual(x, y, D, x0=x0, y0=y0, D0=D0, tan_dip=tan_dip, phi=phi):
    """
    Residual f(x,y,D) = 0 when (x,y,D) lies on the plane.
    From plane equation:
      D = D0 + tan_dip*cos(phi)*(x-x0) - tan_dip*sin(phi)*(y-y0)
    => f = D - D0 - tan_dip*cos(phi)*(x-x0) + tan_dip*sin(phi)*(y-y0)
    """
    return D - D0 - tan_dip*np.cos(phi)*(x - x0) + tan_dip*np.sin(phi)*(y - y0)


def find_intersections(x, y, D):
    """
    Given 1D arrays x, y, D along a polyline, find intersections
    with the plane by sign changes in the residual.
    Returns list of (xi, yi, Di, i, j, t).
    """
    f = plane_residual(x, y, D)

    idxs = []
    for i in range(len(f) - 1):
        fi, fj = f[i], f[i+1]
        if fi == 0.0:
            idxs.append((i, i))    # exact vertex on plane
        elif fi * fj < 0.0:
            idxs.append((i, i+1))  # sign change => crossing

    intersections = []
    for i, j in idxs:
        if i == j:
            # Vertex exactly lies on plane
            xi, yi, Di = x[i], y[i], D[i]
            t = 0.0
        else:
            fi, fj = f[i], f[j]
            t = fi / (fi - fj)     # fraction along segment i->j
            xi = x[i] + t * (x[j] - x[i])
            yi = y[i] + t * (y[j] - y[i])
            Di = D[i] + t * (D[j] - D[i])
        intersections.append((xi, yi, Di, i, j, t))

    return intersections

# -------------------------------------------------------------------
# Compute intersections: plane ∩ B1 and plane ∩ B12
# -------------------------------------------------------------------
# B1
b1_sorted = b1_df.sort_values("D")
x1  = b1_sorted["X"].to_numpy()
y1  = b1_sorted["Y"].to_numpy()
D1  = b1_sorted["D"].to_numpy()
ints_B1 = find_intersections(x1, y1, D1)

# B12
b12_sorted = b12_df.sort_values("D")
x12 = b12_sorted["X"].to_numpy()
y12 = b12_sorted["Y"].to_numpy()
D12 = b12_sorted["D"].to_numpy()
ints_B12 = find_intersections(x12, y12, D12)

# -------------------------------------------------------------------
# Plot
# -------------------------------------------------------------------
fig = plt.figure(figsize=(10, 8), dpi=150, constrained_layout=True)
ax = fig.add_subplot(projection='3d')

# Plane
ax.plot_surface(Xg, Yg, Dg, alpha=0.35, linewidth=0, antialiased=False, color='orange')

# Boreholes
ax.plot(b1x,  b1y,  b1z,  zdir='z', label='BFS-B1',  color='green')
ax.plot(b2x,  b2y,  b2z,  zdir='z', label='BFS-B2',  color='blue')
ax.plot(b12x, b12y, b12z, zdir='z', label='BFS-B12', color='red', linestyle='--')

# Mark B2 intersection at D0
ax.scatter([x0], [y0], [D0], s=60, color='blue')
#ax.text(
#    x0 - 15, y0, D0,
#    f"intersect B2 @{D0:.1f} m",
#    color="blue",
#    zdir=None,
#    bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.9)
#)

# Mark B1 intersections
if not ints_B1:
    print("No intersection: B1 does not cross the plane within its sampled interval.")
else:
    for (xi, yi, Di, i, j, t) in ints_B1:
        print(f"Plane ∩ B1 at X={xi:.3f}, Y={yi:.3f}, depth={Di:.3f} m "
              f"(segment {i}->{j}, t={t:.3f})")
        ax.scatter([xi], [yi], [Di], s=80, marker='o', color='green', zorder=5)
        #ax.text(
        #    xi + 3, yi, Di,
        #    f"intersect B1 @{Di:.1f} m",
        #    color="green",
        #    zdir=None,
        #    bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.9)
        #)

# Mark B12 intersections
if not ints_B12:
    print("No intersection: B12 does not cross the plane within its sampled interval.")
else:
    for (xi, yi, Di, i, j, t) in ints_B12:
        print(f"Plane ∩ B12 at X={xi:.3f}, Y={yi:.3f}, depth={Di:.3f} m "
              f"(segment {i}->{j}, t={t:.3f})")
        ax.scatter([xi], [yi], [Di], s=80, marker='x', color='red', zorder=5)
        #ax.text(
        #    xi + 3, yi, Di,
        #    f"intersect B12 @{Di:.1f} m",
        #    color="red",
        #    zdir=None,
        #    bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.9)
        #)


# -------------------------------------------------------------------
# Point 42.2 m along B1 (along borehole, not vertical)
# ------------------------------------------------------------------

# Sort B1 from top to bottom by depth D (you already defined D earlier)
b1_sorted_MD = b1_df.sort_values("D").reset_index(drop=True)

xB = b1_sorted_MD["X"].to_numpy()
yB = b1_sorted_MD["Y"].to_numpy()
zB = b1_sorted_MD["Z"].to_numpy()   # use true Z (elevation), not D, for geometry

# Segment lengths between consecutive points (3D Euclidean)
dx = np.diff(xB)
dy = np.diff(yB)
dz = np.diff(zB)
seg_len = np.sqrt(dx**2 + dy**2 + dz**2)

# Cumulative distance from collar along B1
cum_len = np.concatenate(([0.0], np.cumsum(seg_len)))

# Check range
total_len = cum_len[-1]
print(f"Total B1 length (from data) ≈ {total_len:.2f} m")


# -------------------------------------------------------------------
# Point 42.2 m along B1 (along borehole, not vertical)
# -------------------------------------------------------------------
b1_sorted_MD = b1_df.sort_values("D").reset_index(drop=True)

xB  = b1_sorted_MD["X"].to_numpy()
yB  = b1_sorted_MD["Y"].to_numpy()
zB  = b1_sorted_MD["Z"].to_numpy()  # true elevation

dx = np.diff(xB)
dy = np.diff(yB)
dz = np.diff(zB)
seg_len = np.sqrt(dx**2 + dy**2 + dz**2)

cum_len = np.concatenate(([0.0], np.cumsum(seg_len)))
total_len_B1 = cum_len[-1]
print(f"Total B1 length (from data) ≈ {total_len_B1:.2f} m")

if MD_target_B1 < 0 or MD_target_B1 > total_len_B1:
    print(f"Target MD={MD_target_B1} m is outside B1 length (0–{total_len_B1:.2f} m).")
else:
    i = np.searchsorted(cum_len, MD_target_B1) - 1
    i = max(0, min(i, len(seg_len)-1))

    L0 = cum_len[i]
    L1 = cum_len[i+1]
    t = 0.0 if L1 == L0 else (MD_target_B1 - L0) / (L1 - L0)

    x_MD  = xB[i]  + t * (xB[i+1]  - xB[i])
    y_MD  = yB[i]  + t * (yB[i+1]  - yB[i])
    z_MD  = zB[i]  + t * (zB[i+1]  - zB[i])
    D_MD  = Z0 - z_MD

    ax.scatter([x_MD], [y_MD], [D_MD], s=80, color="green", marker="*", zorder=10)
    ax.text(
        x_MD + 3, y_MD, D_MD + 8,
        "B1 @42.2 m",
        color="green",
        zdir=None,
        bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.9)
    )

    # origin-shifted coords with plane∩B2 as origin, same convention as intersections
    x_MD_loc = x_MD - x0
    y_MD_loc = y_MD - y0
    D_MD_loc = (D_MD - D0) * -1

    print(
        "B1 @42.2 m in origin-shifted coords (plane∩B2 as origin): "
        f"({x_MD_loc:.3f}, {y_MD_loc:.3f}, {D_MD_loc:.3f})"
    )

# -------------------------------------------------------------------
# Point 43.565 m along B12 (along borehole, not vertical)
# -------------------------------------------------------------------
b12_sorted_MD = b12_df.sort_values("D").reset_index(drop=True)

xB12 = b12_sorted_MD["X"].to_numpy()
yB12 = b12_sorted_MD["Y"].to_numpy()
zB12 = b12_sorted_MD["Z"].to_numpy()  # true elevation

dx12 = np.diff(xB12)
dy12 = np.diff(yB12)
dz12 = np.diff(zB12)
seg_len_12 = np.sqrt(dx12**2 + dy12**2 + dz12**2)

cum_len_12 = np.concatenate(([0.0], np.cumsum(seg_len_12)))
total_len_B12 = cum_len_12[-1]
print(f"Total B12 length (from data) ≈ {total_len_B12:.2f} m")

if MD_target_B12 < 0 or MD_target_B12 > total_len_B12:
    print(f"Target MD={MD_target_B12} m is outside B12 length (0–{total_len_B12:.2f} m).")
else:
    i12 = np.searchsorted(cum_len_12, MD_target_B12) - 1
    i12 = max(0, min(i12, len(seg_len_12)-1))

    L0_12 = cum_len_12[i12]
    L1_12 = cum_len_12[i12+1]
    t12   = 0.0 if L1_12 == L0_12 else (MD_target_B12 - L0_12) / (L1_12 - L0_12)

    x_MD12 = xB12[i12] + t12 * (xB12[i12+1] - xB12[i12])
    y_MD12 = yB12[i12] + t12 * (yB12[i12+1] - yB12[i12])
    z_MD12 = zB12[i12] + t12 * (zB12[i12+1] - zB12[i12])
    D_MD12 = Z0 - z_MD12

    # plot on existing 3D plot
    ax.scatter([x_MD12], [y_MD12], [D_MD12], s=80, color="magenta", marker="*", zorder=10)
    ax.text(
        x_MD12 + 3, y_MD12, D_MD12,
        f"B12 @{MD_target_B12} m",
        color="magenta",
        zdir=None,
        bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.9)
    )

    # origin-shifted coords with plane∩B2 as origin
    x_MD12_loc  = x_MD12 - x0
    y_MD12_loc  = y_MD12 - y0
    D_MD12_loc  = (D_MD12 - D0) * -1

    print(
        f"B12 @{MD_target_B12} m in origin-shifted coords (plane∩B2 as origin): "
        f"({x_MD12_loc:.3f}, {y_MD12_loc:.3f}, {D_MD12_loc:.3f})"
    )




# Axes labels & view
ax.legend()
ax.set_xlabel('X (East)')
ax.set_ylabel('Y (North)')
ax.set_zlabel('Depth [m] (below B2 collar)')

# Depth positive downward, so invert Z axis for usual "top at top" view
ax.invert_zaxis()

ax.view_init(elev=0., azim=-view_angle, roll=0)

plt.savefig('/Users/matthijsnuus/Desktop/FS-C/borehole_locations/boreholes_locations.png',
            bbox_inches="tight", pad_inches=0.2, dpi=200)
plt.show()

# -------------------------------------------------------------------
# Local coordinates of first B1 intersection in origin-shifted frame
# where plane∩B2 is (0,0,0)
# -------------------------------------------------------------------
if ints_B1:
    xi, yi, Di, *_ = ints_B1[0]
    xi_loc = xi - x0
    yi_loc = yi - y0
    Di_loc = (Di - D0) *-1
    print(
        "B1 intersection in origin-shifted coords (plane∩B2 as origin): "
        f"({xi_loc:.3f}, {yi_loc:.3f}, {Di_loc:.3f})"
    )

# -------------------------------------------------------------------
# Local coordinates of first B12 intersection in origin-shifted frame
# where plane∩B2 is (0,0,0)
# -------------------------------------------------------------------
if ints_B12:
    xi12, yi12, D12i, *_ = ints_B12[0]
    xi12_loc = xi12 - x0
    yi12_loc = yi12 - y0
    D12i_loc = (D12i - D0) * -1
    print(
        "B12 intersection in origin-shifted coords (plane∩B2 as origin): "
        f"({xi12_loc:.3f}, {yi12_loc:.3f}, {D12i_loc:.3f})"
    )



