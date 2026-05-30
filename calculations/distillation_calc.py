"""
calculations/distillation_calc.py
─────────────────────────────────────────────────────────────────────
All core distillation engineering calculations:
  • Material balance
  • Fenske equation (Nmin)
  • Underwood equation (Rmin)
  • Gilliland correlation (N vs R)
  • Kirkbride equation (feed tray)
  • Operating lines
  • McCabe-Thiele stage stepping
  • Column diameter (Fair method)
  • Column height
  • Reboiler & condenser duties
  • Mechanical shell thickness (ASME)
─────────────────────────────────────────────────────────────────────
"""

import numpy as np
from typing import Tuple, List, Dict
from thermodynamics.thermo_engine import y_from_x, x_from_y, feed_q_value


# ═══════════════════════════════════════════════════════════════
#  1.  MATERIAL BALANCE
# ═══════════════════════════════════════════════════════════════
def material_balance(F: float, z_F: float,
                     x_D: float, x_B: float) -> Dict:
    """
    Overall and component balance for binary system.
    F = feed flow  [kmol/h]
    z_F = feed mole fraction of light component
    x_D = distillate mole fraction (light)
    x_B = bottoms mole fraction (light)
    """
    # F = D + B
    # F·zF = D·xD + B·xB
    D = F * (z_F - x_B) / (x_D - x_B)
    B = F - D
    recovery_D = D * x_D / (F * z_F) * 100
    recovery_B = B * (1 - x_B) / (F * (1 - z_F)) * 100

    return {
        "F": round(F, 4),
        "D": round(D, 4),
        "B": round(B, 4),
        "z_F": z_F,
        "x_D": x_D,
        "x_B": x_B,
        "recovery_distillate_pct": round(recovery_D, 2),
        "recovery_bottoms_pct": round(recovery_B, 2),
        "D_over_F": round(D/F, 4),
        "B_over_F": round(B/F, 4),
    }


# ═══════════════════════════════════════════════════════════════
#  2.  FENSKE EQUATION — Minimum Stages
# ═══════════════════════════════════════════════════════════════
def fenske(x_D: float, x_B: float, alpha: float) -> Dict:
    """
    N_min = log[(xD/(1-xD)) · ((1-xB)/xB)] / log(α)
    Returns minimum theoretical stages (includes reboiler).
    """
    if alpha <= 1:
        raise ValueError("Relative volatility must be > 1")
    numerator = np.log((x_D / (1 - x_D)) * ((1 - x_B) / x_B))
    N_min = numerator / np.log(alpha)
    return {
        "N_min": round(N_min, 3),
        "N_min_excl_reboiler": round(N_min - 1, 3),
        "alpha": round(alpha, 4),
    }


# ═══════════════════════════════════════════════════════════════
#  3.  UNDERWOOD EQUATION — Minimum Reflux Ratio
# ═══════════════════════════════════════════════════════════════
def underwood(alpha: float, z_F: float, q: float,
              x_D: float) -> Dict:
    """
    Underwood method for binary system.
    Solves: α·zF/(α-θ) + 1·(1-zF)/(1-θ) = 1 - q
    Then: Rmin + 1 = α·xD/(α-θ) + 1·(1-xD)/(1-θ)
    """
    from scipy.optimize import brentq

    def underwood_eq(theta):
        return (alpha * z_F / (alpha - theta) +
                1.0 * (1 - z_F) / (1.0 - theta) - (1 - q))

    # θ must lie between 1 and α
    try:
        theta = brentq(underwood_eq, 1.0001, alpha - 0.0001)
    except ValueError:
        theta = (1.0 + alpha) / 2  # fallback midpoint

    V_min = (alpha * x_D / (alpha - theta) +
             1.0 * (1 - x_D) / (1.0 - theta))
    R_min = V_min - 1.0

    return {
        "R_min": round(R_min, 4),
        "V_min": round(V_min, 4),
        "theta": round(theta, 6),
        "q": round(q, 4),
    }


# ═══════════════════════════════════════════════════════════════
#  4.  GILLILAND CORRELATION — Actual Stages
# ═══════════════════════════════════════════════════════════════
def gilliland(N_min: float, R_min: float,
              R: float) -> Dict:
    """
    Molokanov approximation to Gilliland correlation:
    Y = 1 - exp[(1+54.4X)/(11+117.2X) · (X-1)/X^0.5]
    X = (R - Rmin) / (R + 1)
    Y = (N - Nmin) / (N + 1)
    """
    X = (R - R_min) / (R + 1)
    # Molokanov (1972)
    Y = 1 - np.exp((1 + 54.4*X) / (11 + 117.2*X) * (X - 1) / X**0.5)
    N = (Y + N_min) / (1 - Y)
    efficiency_factor = N_min / N  # theoretical / actual

    return {
        "N_actual": round(N, 2),
        "N_actual_int": int(np.ceil(N)),
        "N_min": round(N_min, 3),
        "R": round(R, 4),
        "R_min": round(R_min, 4),
        "X_gilliland": round(X, 6),
        "Y_gilliland": round(Y, 6),
        "R_over_Rmin": round(R / R_min, 4),
    }


# ═══════════════════════════════════════════════════════════════
#  5.  KIRKBRIDE EQUATION — Feed Tray Location
# ═══════════════════════════════════════════════════════════════
def kirkbride(N: float, z_F: float, x_D: float, x_B: float,
              B: float, D: float) -> Dict:
    """
    log(Nr/Ns) = 0.206 · log[(B/D)·(zF/xD)²·((1-xB)/(1-zF))·...]
    Nr = stages above feed (rectifying)
    Ns = stages below feed (stripping)
    Nr + Ns = N (total stages)
    """
    # Kirkbride (1944) standard form:
    # log(Nr/Ns) = 0.206 * log[(B/D) * (zF/xD)^2 * ((1-xB)/(1-zF))^2]
    log_ratio = 0.206 * np.log10(
        (B / D) * ((z_F / x_D) ** 2) * ((1 - x_B) / (1 - z_F)) ** 2
    )
    Nr_over_Ns = 10 ** log_ratio
    Ns = N / (1 + Nr_over_Ns)
    Nr = N - Ns
    feed_tray = int(np.ceil(Nr))

    return {
        "Nr": round(Nr, 2),
        "Ns": round(Ns, 2),
        "feed_tray_from_top": feed_tray,
        "Nr_over_Ns": round(Nr_over_Ns, 4),
    }


# ═══════════════════════════════════════════════════════════════
#  6.  OPERATING LINES
# ═══════════════════════════════════════════════════════════════
def rectifying_line(x: np.ndarray, R: float, x_D: float) -> np.ndarray:
    """y = (R/(R+1))·x + xD/(R+1)"""
    return (R / (R + 1)) * x + x_D / (R + 1)


def stripping_line(x: np.ndarray, L_prime: float, V_prime: float,
                   x_B: float) -> np.ndarray:
    """y = (L'/V')·x - (B/V')·xB    where B = L' - V'"""
    B = L_prime - V_prime
    return (L_prime / V_prime) * x - (B / V_prime) * x_B


def feed_line_q(x: np.ndarray, z_F: float, q: float) -> np.ndarray:
    """q-line: y = q/(q-1)·x - zF/(q-1)"""
    if abs(q - 1) < 1e-8:
        return np.full_like(x, np.nan)  # vertical feed line at x=zF
    return (q / (q - 1)) * x - z_F / (q - 1)


def operating_line_intersection(R: float, x_D: float,
                                 q: float, z_F: float) -> Tuple[float, float]:
    """Find intersection of rectifying line and q-line."""
    if abs(q - 1) < 1e-8:
        x_int = z_F
        y_int = R / (R + 1) * z_F + x_D / (R + 1)
    else:
        # q/(q-1)*x - zF/(q-1) = R/(R+1)*x + xD/(R+1)
        a1 = q / (q - 1) - R / (R + 1)
        b1 = x_D / (R + 1) + z_F / (q - 1)
        x_int = b1 / a1
        y_int = R / (R + 1) * x_int + x_D / (R + 1)
    return round(float(x_int), 6), round(float(y_int), 6)


# ═══════════════════════════════════════════════════════════════
#  7.  McCABE-THIELE STAGE STEPPING
# ═══════════════════════════════════════════════════════════════
def mccabe_thiele_stages(alpha: float, R: float,
                          x_D: float, x_B: float,
                          z_F: float, q: float) -> Dict:
    """
    Step off stages graphically (numerically):
    Starting from xD, alternate between VLE curve and operating lines.
    Switches to stripping line after passing feed tray.
    Returns list of (x, y) points for each stage.
    """
    # Intersection of operating lines
    x_int, y_int = operating_line_intersection(R, x_D, q, z_F)

    # L', V' for stripping section
    # From material balance: L' = L + q*F,  V' = V - (1-q)*F
    # For unit feed (F=1): L = R*D = R/(R+1), V = (R+1)*D = 1/(R+1)*... 
    # Simplified: use slopes
    m_rect = R / (R + 1)
    b_rect = x_D / (R + 1)

    # Stripping line through (x_int, y_int) and (xB, xB)
    if abs(x_int - x_B) < 1e-10:
        m_strip = 1.5  # fallback
    else:
        m_strip = (y_int - x_B) / (x_int - x_B)
    b_strip = x_B - m_strip * x_B  # y = m*x + b  at (xB, xB)
    b_strip = x_B * (1 - m_strip)

    stages = []
    x_current = x_D
    y_current = x_D  # start on diagonal

    switched_to_strip = False
    max_stages = 100

    for stage_num in range(1, max_stages + 1):
        # Step horizontally to equilibrium curve: find x from y
        x_eq = x_from_y(y_current, alpha)
        stages.append({
            "stage": stage_num,
            "x": round(x_eq, 6),
            "y": round(y_current, 6),
            "section": "stripping" if switched_to_strip else "rectifying"
        })

        if x_eq <= x_B:
            break  # reached bottoms

        # Check if we should switch to stripping line
        if not switched_to_strip and x_eq <= x_int:
            switched_to_strip = True

        # Step down to operating line
        if switched_to_strip:
            y_next = m_strip * x_eq + b_strip
        else:
            y_next = m_rect * x_eq + b_rect

        y_current = y_next

        if y_current < x_B:
            break

    return {
        "stages": stages,
        "n_stages": len(stages),
        "n_rectifying": sum(1 for s in stages if s["section"] == "rectifying"),
        "n_stripping":  sum(1 for s in stages if s["section"] == "stripping"),
        "x_int": x_int,
        "y_int": y_int,
        "slope_rectifying": round(m_rect, 4),
        "slope_stripping":  round(m_strip, 4),
    }


# ═══════════════════════════════════════════════════════════════
#  8.  COLUMN DIAMETER — Fair Method
# ═══════════════════════════════════════════════════════════════
def column_diameter_tray(V_molar: float,       # vapour flow [kmol/h]
                          MW_avg: float,         # average MW [g/mol]
                          rho_L: float,          # liquid density [kg/m³]
                          rho_V: float = None,   # vapour density [kg/m³]
                          T_K: float = 350.0,    # temperature [K]
                          P_bar: float = 1.013,  # pressure [bar]
                          tray_spacing: float = 0.6,  # [m]
                          flooding_fraction: float = 0.80) -> Dict:
    """
    Fair method for tray column diameter.
    Uses Smith-Dresser-Ohlswager capacity chart approximation.
    """
    R_gas = 8314  # J/(kmol·K)

    # Vapour density from ideal gas if not given
    if rho_V is None:
        rho_V = (P_bar * 1e5 * MW_avg) / (R_gas * T_K)  # kg/m³

    V_kg_h = V_molar * MW_avg        # kg/h
    V_m3_s = V_kg_h / (3600 * rho_V) # m³/s

    # Flow parameter (simplified)
    FLV = 0.1  # typical; would need liquid flow for exact value

    # Souders-Brown coefficient C_SB from tray spacing (approximate)
    # Based on Fair's chart regression
    C_SB = 0.04 + 0.16 * tray_spacing  # m/s  (simplified linear fit)
    C_SB = min(C_SB, 0.12)

    # Flooding velocity
    u_flood = C_SB * ((rho_L - rho_V) / rho_V) ** 0.5  # m/s

    # Operating velocity
    u_op = flooding_fraction * u_flood

    # Net area required
    A_net = V_m3_s / u_op  # m²

    # Column diameter (assuming downcomer takes 12% of total area)
    A_total = A_net / 0.88
    D_col = np.sqrt(4 * A_total / np.pi)

    # Round up to nearest 0.05 m (standard shell increment)
    D_col_std = np.ceil(D_col / 0.05) * 0.05

    return {
        "D_column_m": round(D_col, 4),
        "D_column_std_m": round(D_col_std, 3),
        "u_flood_m_s": round(u_flood, 4),
        "u_operating_m_s": round(u_op, 4),
        "A_net_m2": round(A_net, 4),
        "A_total_m2": round(A_total, 4),
        "rho_V_kg_m3": round(rho_V, 4),
        "rho_L_kg_m3": round(rho_L, 2),
        "C_SB": round(C_SB, 5),
        "flooding_fraction": flooding_fraction,
    }


# ═══════════════════════════════════════════════════════════════
#  9.  COLUMN HEIGHT
# ═══════════════════════════════════════════════════════════════
def column_height_tray(N_actual: int,
                        tray_spacing: float = 0.6,    # m
                        tray_efficiency: float = 0.70,
                        top_disengagement: float = 1.5,  # m
                        bottom_sump: float = 2.0,        # m
                        skirt_height: float = 3.0) -> Dict:  # m
    """Total column height for tray column."""
    N_actual_trays = int(np.ceil(N_actual / tray_efficiency))
    active_section = N_actual_trays * tray_spacing
    total_height = active_section + top_disengagement + bottom_sump
    total_with_skirt = total_height + skirt_height

    return {
        "N_theoretical": N_actual,
        "N_actual_trays": N_actual_trays,
        "tray_efficiency": tray_efficiency,
        "tray_spacing_m": tray_spacing,
        "active_section_m": round(active_section, 2),
        "top_disengagement_m": top_disengagement,
        "bottom_sump_m": bottom_sump,
        "total_height_m": round(total_height, 2),
        "total_with_skirt_m": round(total_with_skirt, 2),
        "H_over_D": None,  # filled after diameter calc
    }


# ═══════════════════════════════════════════════════════════════
#  10.  REBOILER DUTY
# ═══════════════════════════════════════════════════════════════
def reboiler_duty(V_prime: float,         # vapour from reboiler [kmol/h]
                  lambda_vap: float = 30000.0,  # latent heat [J/mol]
                  efficiency: float = 0.85) -> Dict:
    """
    Q_reb = V' × λ / efficiency
    V' = vapour flow in stripping section [kmol/h]
    """
    Q_W = V_prime * 1000 * lambda_vap / 3600  # W
    Q_MW = Q_W / 1e6
    Q_kW = Q_W / 1e3

    # Steam requirement (assuming 150°C steam, λ_steam ≈ 2114 kJ/kg)
    lambda_steam = 2114e3  # J/kg
    steam_kg_h = (Q_W / efficiency) / lambda_steam * 3600

    return {
        "Q_reboiler_kW": round(Q_kW, 2),
        "Q_reboiler_MW": round(Q_MW, 4),
        "steam_consumption_kg_h": round(steam_kg_h, 2),
        "V_prime_kmol_h": round(V_prime, 3),
        "efficiency": efficiency,
    }


# ═══════════════════════════════════════════════════════════════
#  11.  CONDENSER DUTY
# ═══════════════════════════════════════════════════════════════
def condenser_duty(V_molar: float,           # vapour to condenser [kmol/h]
                   lambda_vap: float = 30000.0,  # J/mol
                   T_in: float = 80.0,       # vapour inlet temp [°C]
                   T_out: float = 40.0,      # condensate outlet [°C]
                   Cp_L: float = 150.0,      # J/mol·K
                   efficiency: float = 0.90) -> Dict:
    """Condenser heat duty calculation."""
    # Latent heat removal
    Q_latent = V_molar * 1000 * lambda_vap / 3600  # W
    # Sensible heat (sub-cooling)
    delta_T = T_in - T_out
    Q_sensible = V_molar * 1000 * Cp_L * delta_T / 3600
    Q_total = (Q_latent + Q_sensible) / efficiency

    Q_kW = Q_total / 1e3

    # Cooling water requirement (ΔT = 10°C, Cp_water = 4186 J/kg·K)
    CW_kg_h = Q_total / (4186 * 10) * 3600

    return {
        "Q_condenser_kW": round(Q_kW, 2),
        "Q_latent_kW": round(Q_latent / 1e3, 2),
        "Q_sensible_kW": round(Q_sensible / 1e3, 2),
        "cooling_water_kg_h": round(CW_kg_h, 2),
        "V_condenser_kmol_h": round(V_molar, 3),
        "efficiency": efficiency,
    }


# ═══════════════════════════════════════════════════════════════
#  12.  MECHANICAL — Shell Thickness (ASME UG-27)
# ═══════════════════════════════════════════════════════════════
def shell_thickness_asme(D_i: float,          # inner diameter [mm]
                          P_design: float,     # design pressure [bar(g)]
                          S_allowable: float = 138.0,  # MPa  (CS A516-70)
                          E_weld: float = 1.0,          # joint efficiency
                          CA: float = 3.0) -> Dict:    # corrosion allowance [mm]
    """
    ASME UG-27 cylindrical shell thickness:
    t = P·R / (S·E - 0.6·P) + CA
    P in MPa, R in mm
    """
    P_MPa = P_design * 0.1  # bar → MPa
    R = D_i / 2  # mm

    t_calc = (P_MPa * R) / (S_allowable * E_weld - 0.6 * P_MPa)
    t_total = t_calc + CA

    # Round up to nearest 1 mm standard plate
    t_std = np.ceil(t_total)

    return {
        "t_calculated_mm": round(t_calc, 3),
        "t_with_CA_mm": round(t_total, 3),
        "t_standard_mm": int(t_std),
        "D_inner_mm": D_i,
        "D_outer_mm": round(D_i + 2 * t_std, 1),
        "P_design_bar": P_design,
        "P_design_MPa": round(P_MPa, 4),
        "S_allowable_MPa": S_allowable,
        "corrosion_allowance_mm": CA,
        "joint_efficiency": E_weld,
    }


# ═══════════════════════════════════════════════════════════════
#  13.  ENERGY ECONOMICS (quick estimate)
# ═══════════════════════════════════════════════════════════════
def energy_economics(Q_reb_kW: float, Q_cond_kW: float,
                     steam_cost: float = 15.0,    # USD/GJ
                     cw_cost: float = 0.05,        # USD/GJ
                     op_hours: float = 8000.0) -> Dict:
    """Annual utility cost estimation."""
    Q_reb_GJ_yr  = Q_reb_kW  * 3600 * op_hours / 1e9
    Q_cond_GJ_yr = Q_cond_kW * 3600 * op_hours / 1e9

    steam_cost_yr = Q_reb_GJ_yr  * steam_cost
    cw_cost_yr    = Q_cond_GJ_yr * cw_cost
    total_opex    = steam_cost_yr + cw_cost_yr

    return {
        "Q_reboiler_GJ_yr": round(Q_reb_GJ_yr, 2),
        "Q_condenser_GJ_yr": round(Q_cond_GJ_yr, 2),
        "steam_cost_USD_yr": round(steam_cost_yr, 0),
        "cooling_water_cost_USD_yr": round(cw_cost_yr, 0),
        "total_opex_USD_yr": round(total_opex, 0),
        "op_hours": op_hours,
    }
