## Injecting fully saturated Pearson water with CO₂

This note documents how we determined the CO₂ solubility at Mont Terri conditions and how we convert the target **5.3 L/min** liquid injection into component mass rates for **TOUGH3/ECO2N**.

---

### Setup summary

- **Code:** `InjecINFILE.py`
- **Mesh:** 2 elements via `meshmaker` (domain 1 × 1 × 1 m)
- **Porosity:** 0.99 (nearly fully fluid-filled)
- **Material:** `TANK`
- **Initial conditions (flash cell to read solubility):**
  - Pressure = **3.5 MPa**
  - Temperature = **16.5 °C**
  - Liquid/gas saturations: **S<sub>L</sub> = 0.5**, **S<sub>G</sub> = 0.5**  *(two-phase so the liquid is at CO₂ solubility)*
  - NaCl mass fraction (brine, no CO₂ yet):  
    - From **0.3 M NaCl** (Pearson/OPA water):  
      \[ w_{\text{NaCl}} \approx \frac{0.3 \times 58.44\ \text{g/mol}}{ \rho \approx 1019\ \text{g/L} } \approx \mathbf{0.0172} \] (**1.72 wt%**)

- **Diffusion:** Not included.
- **Purpose of flash step:** With S<sub>L</sub> and S<sub>G</sub> both > 0, ECO2N “flashes” to equilibrium so **X_CO₂(L)** equals the **saturation limit** (mass fraction) at the given P–T–salinity.

---

### Flash results (two-phase equilibrium at 3.5 MPa, 16.5 °C)

Liquid-phase mass fractions (sum ≈ 1):

- **X_WATER_L = 0.939142**
- **X_NaCl_L  = 0.0164389**
- **X_CO₂_L   = 0.0444189**  ← **CO₂ solubility ~ 4.44 wt%**

Liquid density at these conditions:

- **DEN_L ≈ 1019.04 kg/m³**

---

### Converting the injection rate to component mass rates

**Given:** volumetric liquid rate **5.3 L/min**

1. Convert to m³/s:  
   \( Q = \frac{5.3\times10^{-3}\ \text{m}^3}{60\ \text{s}} = \mathbf{8.8333\times10^{-5}\ \text{m}^3/\text{s}} \)

2. Convert to total **mass** rate using the saturated-brine density:  
   \( \dot{m}_L = \rho_L\,Q = 1019.04 \times 8.8333\times10^{-5} \approx \mathbf{9.00149\times10^{-2}\ \text{kg/s}} \)

3. Split by the **liquid** mass fractions (from the flash):

- \( \dot{m}_{\text{H₂O}} = 0.939142 \times 0.0900149 \approx \mathbf{8.45368\times10^{-2}\ \text{kg/s}} \)
- \( \dot{m}_{\text{NaCl}} = 0.0164389 \times 0.0900149 \approx \mathbf{1.47974\times10^{-3}\ \text{kg/s}} \)
- \( \dot{m}_{\text{CO₂}} = 0.0444189 \times 0.0900149 \approx \mathbf{3.99837\times10^{-3}\ \text{kg/s}} \)

> These are the component **kg/s** rates to use in `GENER` if specifying per-component sources, or use the **total** \( \dot{m}_L \) with a **composition vector** (H₂O, NaCl, CO₂) if your build supports `COM`.

---

### Modeling intent

- For the **flash**: use a closed, two-phase cell (no injection) to read **X_CO₂(L)** at P–T–salinity (the saturation limit).
- For the **injection case** (full-scale model): inject **liquid only** with the above **mass fractions**, at **5.3 L/min**, for **4 hours** (14,400 s).  
  This represents **CO₂-saturated Pearson water** at Mont Terri conditions, avoiding a separate free CO₂ phase at the well (provided local pressure remains high enough).

---
