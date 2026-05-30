"""
thermodynamics/thermo_engine.py
─────────────────────────────────────────────────────────────────────
Core thermodynamic engine:
  • Antoine equation for vapour pressure
  • Raoult's Law VLE (ideal / modified)
  • Relative volatility calculation
  • Bubble-point / dew-point iterations
  • Built-in component database (20+ common chemicals)
─────────────────────────────────────────────────────────────────────
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Optional, Dict, Tuple

# ───────────────────────────────────────────────────────────────
#  Component Database  (Antoine constants in log10, P in mmHg,
#  T in °C — classic Perry's format)
#  ln P(mmHg) = A – B/(C+T°C)   [log10 form]
# ───────────────────────────────────────────────────────────────
COMPONENT_DB: Dict[str, dict] = {
    # Light hydrocarbons
    "Methane":       {"A":6.61184,  "B":389.93,  "C":266.0,  "MW":16.04,  "Tb":-161.5, "Tc":190.6,  "Pc":46.1,  "omega":0.011},
    "Ethane":        {"A":6.80896,  "B":656.40,  "C":256.0,  "MW":30.07,  "Tb":-88.6,  "Tc":305.3,  "Pc":48.7,  "omega":0.099},
    "Propane":       {"A":6.82973,  "B":813.20,  "C":248.0,  "MW":44.10,  "Tb":-42.1,  "Tc":369.8,  "Pc":42.5,  "omega":0.153},
    "n-Butane":      {"A":6.82485,  "B":943.453, "C":239.711,"MW":58.12,  "Tb":-0.5,   "Tc":425.1,  "Pc":37.9,  "omega":0.200},
    "n-Pentane":     {"A":6.85221,  "B":1064.63, "C":232.0,  "MW":72.15,  "Tb":36.1,   "Tc":469.7,  "Pc":33.7,  "omega":0.252},
    "n-Hexane":      {"A":6.87601,  "B":1171.17, "C":224.41, "MW":86.18,  "Tb":68.7,   "Tc":507.6,  "Pc":30.2,  "omega":0.301},
    "n-Heptane":     {"A":6.89385,  "B":1264.37, "C":216.64, "MW":100.21, "Tb":98.4,   "Tc":540.2,  "Pc":27.4,  "omega":0.349},
    "n-Octane":      {"A":6.91868,  "B":1351.99, "C":209.155,"MW":114.23, "Tb":125.7,  "Tc":568.8,  "Pc":24.9,  "omega":0.400},
    # Aromatics
    "Benzene":       {"A":6.89272,  "B":1203.531,"C":219.888,"MW":78.11,  "Tb":80.1,   "Tc":562.2,  "Pc":48.9,  "omega":0.212},
    "Toluene":       {"A":6.95464,  "B":1344.800,"C":219.482,"MW":92.14,  "Tb":110.6,  "Tc":591.8,  "Pc":41.0,  "omega":0.263},
    "o-Xylene":      {"A":7.00154,  "B":1476.393,"C":213.872,"MW":106.17, "Tb":144.4,  "Tc":630.4,  "Pc":37.3,  "omega":0.310},
    "Ethylbenzene":  {"A":6.95719,  "B":1424.255,"C":213.206,"MW":106.17, "Tb":136.2,  "Tc":617.2,  "Pc":36.0,  "omega":0.302},
    # Alcohols
    "Methanol":      {"A":7.87863,  "B":1473.11, "C":230.0,  "MW":32.04,  "Tb":64.7,   "Tc":512.6,  "Pc":80.9,  "omega":0.559},
    "Ethanol":       {"A":8.04494,  "B":1554.3,  "C":222.65, "MW":46.07,  "Tb":78.4,   "Tc":513.9,  "Pc":61.4,  "omega":0.645},
    "n-Propanol":    {"A":7.74416,  "B":1437.686,"C":198.463,"MW":60.10,  "Tb":97.2,   "Tc":536.8,  "Pc":51.7,  "omega":0.629},
    "Isopropanol":   {"A":7.74021,  "B":1359.517,"C":197.527,"MW":60.10,  "Tb":82.4,   "Tc":508.3,  "Pc":47.6,  "omega":0.665},
    # Ketones / esters / ethers
    "Acetone":       {"A":7.02447,  "B":1161.0,  "C":224.0,  "MW":58.08,  "Tb":56.1,   "Tc":508.2,  "Pc":47.0,  "omega":0.307},
    "Ethyl Acetate": {"A":7.09808,  "B":1238.71, "C":217.0,  "MW":88.11,  "Tb":77.1,   "Tc":523.3,  "Pc":38.8,  "omega":0.366},
    "Diethyl Ether": {"A":6.92032,  "B":1064.07, "C":228.8,  "MW":74.12,  "Tb":34.6,   "Tc":466.7,  "Pc":36.4,  "omega":0.281},
    # Water & common
    "Water":         {"A":8.07131,  "B":1730.63, "C":233.426,"MW":18.02,  "Tb":100.0,  "Tc":647.1,  "Pc":220.6, "omega":0.345},
    "Acetic Acid":   {"A":7.38782,  "B":1533.313,"C":222.309,"MW":60.05,  "Tb":117.9,  "Tc":591.7,  "Pc":57.9,  "omega":0.467},
    "Chloroform":    {"A":6.79350,  "B":1163.03, "C":227.4,  "MW":119.38, "Tb":61.2,   "Tc":536.4,  "Pc":54.7,  "omega":0.218},
    "Carbon Tetra.": {"A":6.84083,  "B":1177.910,"C":220.576,"MW":153.82, "Tb":76.7,   "Tc":556.4,  "Pc":45.6,  "omega":0.193},
    "Cyclohexane":   {"A":6.84498,  "B":1203.526,"C":222.863,"MW":84.16,  "Tb":80.7,   "Tc":553.6,  "Pc":40.8,  "omega":0.212},
}


# ───────────────────────────────────────────────────────────────
#  Advanced Physical Properties
#  Values are engineering defaults for early-stage design:
#  liquid properties are near 20-25 °C where practical; Hvap is a
#  representative normal-boiling latent heat. They are meant to give
#  better first estimates than hard-coded generic defaults, while still
#  allowing user override in detailed design sections.
# ───────────────────────────────────────────────────────────────
_ADVANCED_PROPS: Dict[str, dict] = {
    # Tmin/Tmax are practical Antoine-use ranges in °C for UI warnings.
    "Methane":       {"Tmin":-182.0, "Tmax": -82.0, "rho_L":422.0,  "mu_L":0.11, "Cp_L":75.0,  "Hvap":8170.0,  "sigma":0.012},
    "Ethane":        {"Tmin":-172.0, "Tmax":  32.0, "rho_L":544.0,  "mu_L":0.10, "Cp_L":110.0, "Hvap":14700.0, "sigma":0.017},
    "Propane":       {"Tmin":-188.0, "Tmax":  96.0, "rho_L":493.0,  "mu_L":0.20, "Cp_L":98.0,  "Hvap":19000.0, "sigma":0.016},
    "n-Butane":      {"Tmin":-135.0, "Tmax": 152.0, "rho_L":584.0,  "mu_L":0.20, "Cp_L":133.0, "Hvap":22400.0, "sigma":0.014},
    "n-Pentane":     {"Tmin": -50.0, "Tmax": 200.0, "rho_L":626.0,  "mu_L":0.24, "Cp_L":167.0, "Hvap":25800.0, "sigma":0.016},
    "n-Hexane":      {"Tmin": -25.0, "Tmax": 220.0, "rho_L":655.0,  "mu_L":0.30, "Cp_L":198.0, "Hvap":28900.0, "sigma":0.018},
    "n-Heptane":     {"Tmin":   0.0, "Tmax": 250.0, "rho_L":684.0,  "mu_L":0.39, "Cp_L":225.0, "Hvap":31700.0, "sigma":0.020},
    "n-Octane":      {"Tmin":  20.0, "Tmax": 300.0, "rho_L":703.0,  "mu_L":0.54, "Cp_L":255.0, "Hvap":34900.0, "sigma":0.0218},
    "Benzene":       {"Tmin":  10.0, "Tmax": 200.0, "rho_L":879.0,  "mu_L":0.60, "Cp_L":136.0, "Hvap":30720.0, "sigma":0.0289},
    "Toluene":       {"Tmin":  10.0, "Tmax": 230.0, "rho_L":867.0,  "mu_L":0.59, "Cp_L":157.0, "Hvap":35100.0, "sigma":0.0285},
    "o-Xylene":      {"Tmin":  30.0, "Tmax": 260.0, "rho_L":880.0,  "mu_L":0.81, "Cp_L":182.0, "Hvap":41300.0, "sigma":0.0300},
    "Ethylbenzene":  {"Tmin":  30.0, "Tmax": 260.0, "rho_L":867.0,  "mu_L":0.67, "Cp_L":182.0, "Hvap":35800.0, "sigma":0.0290},
    "Methanol":      {"Tmin":  10.0, "Tmax": 150.0, "rho_L":792.0,  "mu_L":0.54, "Cp_L":81.0,  "Hvap":35200.0, "sigma":0.0226},
    "Ethanol":       {"Tmin":   0.0, "Tmax": 170.0, "rho_L":789.0,  "mu_L":1.07, "Cp_L":112.0, "Hvap":38600.0, "sigma":0.0223},
    "n-Propanol":    {"Tmin":  20.0, "Tmax": 190.0, "rho_L":803.0,  "mu_L":1.96, "Cp_L":145.0, "Hvap":47000.0, "sigma":0.0237},
    "Isopropanol":   {"Tmin":   0.0, "Tmax": 160.0, "rho_L":785.0,  "mu_L":2.04, "Cp_L":154.0, "Hvap":44000.0, "sigma":0.0217},
    "Acetone":       {"Tmin": -20.0, "Tmax": 160.0, "rho_L":785.0,  "mu_L":0.32, "Cp_L":126.0, "Hvap":29100.0, "sigma":0.0237},
    "Ethyl Acetate": {"Tmin": -10.0, "Tmax": 180.0, "rho_L":902.0,  "mu_L":0.43, "Cp_L":170.0, "Hvap":31900.0, "sigma":0.0239},
    "Diethyl Ether": {"Tmin": -40.0, "Tmax": 120.0, "rho_L":713.0,  "mu_L":0.22, "Cp_L":172.0, "Hvap":26300.0, "sigma":0.0170},
    "Water":         {"Tmin":   1.0, "Tmax": 100.0, "rho_L":997.0,  "mu_L":0.89, "Cp_L":75.3,  "Hvap":40650.0, "sigma":0.0720},
    "Acetic Acid":   {"Tmin":  20.0, "Tmax": 200.0, "rho_L":1049.0, "mu_L":1.22, "Cp_L":123.0, "Hvap":23500.0, "sigma":0.0276},
    "Chloroform":    {"Tmin": -10.0, "Tmax": 150.0, "rho_L":1490.0, "mu_L":0.54, "Cp_L":116.0, "Hvap":29200.0, "sigma":0.0267},
    "Carbon Tetra.": {"Tmin": -20.0, "Tmax": 170.0, "rho_L":1590.0, "mu_L":0.97, "Cp_L":132.0, "Hvap":29900.0, "sigma":0.0269},
    "Cyclohexane":   {"Tmin":  10.0, "Tmax": 200.0, "rho_L":779.0,  "mu_L":0.89, "Cp_L":156.0, "Hvap":30000.0, "sigma":0.0255},
}

for _name, _props in _ADVANCED_PROPS.items():
    if _name in COMPONENT_DB:
        COMPONENT_DB[_name].update({
            **_props,
            "source": "Built-in engineering defaults; verify for final design",
            "data_quality": "estimate",
            "prop_ref_C": 25.0,
        })


def antoine_range_status(component: str, T_C: float) -> Dict:
    """Return a light-weight range check for the component Antoine constants."""
    c = COMPONENT_DB.get(component, {})
    Tmin, Tmax = c.get("Tmin"), c.get("Tmax")
    if Tmin is None or Tmax is None:
        return {"ok": None, "message": "No Antoine range stored."}
    ok = Tmin <= T_C <= Tmax
    return {
        "ok": ok,
        "Tmin": Tmin,
        "Tmax": Tmax,
        "message": "Inside stored Antoine range." if ok else f"Outside stored Antoine range ({Tmin} to {Tmax} °C).",
    }


def mixture_mw(light: str, heavy: str, x_light: float) -> float:
    """Mole-fraction average molecular weight [g/mol]."""
    p1, p2 = COMPONENT_DB[light], COMPONENT_DB[heavy]
    return x_light * p1["MW"] + (1 - x_light) * p2["MW"]


def liquid_density_mixture(light: str, heavy: str, x_light: float) -> float:
    """Ideal molar-volume liquid density estimate [kg/m³]."""
    p1, p2 = COMPONENT_DB[light], COMPONENT_DB[heavy]
    mw_mix = mixture_mw(light, heavy, x_light)
    v_mix = x_light * p1["MW"] / p1["rho_L"] + (1 - x_light) * p2["MW"] / p2["rho_L"]
    return round(mw_mix / v_mix, 2)


def liquid_viscosity_mixture(light: str, heavy: str, x_light: float) -> float:
    """Log-mixing liquid viscosity estimate [mPa·s]."""
    p1, p2 = COMPONENT_DB[light], COMPONENT_DB[heavy]
    mu = np.exp(x_light * np.log(p1["mu_L"]) + (1 - x_light) * np.log(p2["mu_L"]))
    return round(float(mu), 4)


def liquid_cp_mixture(light: str, heavy: str, x_light: float) -> float:
    """Mole-fraction average liquid heat capacity [J/mol·K]."""
    p1, p2 = COMPONENT_DB[light], COMPONENT_DB[heavy]
    return round(x_light * p1["Cp_L"] + (1 - x_light) * p2["Cp_L"], 2)


def latent_heat_mixture(light: str, heavy: str, x_light: float) -> float:
    """Mole-fraction average latent heat [J/mol]."""
    p1, p2 = COMPONENT_DB[light], COMPONENT_DB[heavy]
    return round(x_light * p1["Hvap"] + (1 - x_light) * p2["Hvap"], 1)


def surface_tension_mixture(light: str, heavy: str, x_light: float) -> float:
    """Mole-fraction average surface tension [N/m]."""
    p1, p2 = COMPONENT_DB[light], COMPONENT_DB[heavy]
    return round(x_light * p1["sigma"] + (1 - x_light) * p2["sigma"], 5)


def binary_mixture_props(light: str, heavy: str, x_light: float) -> Dict:
    """Return commonly used liquid-mixture properties for design defaults."""
    return {
        "MW": round(mixture_mw(light, heavy, x_light), 2),
        "rho_L": liquid_density_mixture(light, heavy, x_light),
        "mu_L": liquid_viscosity_mixture(light, heavy, x_light),
        "Cp_L": liquid_cp_mixture(light, heavy, x_light),
        "Hvap": latent_heat_mixture(light, heavy, x_light),
        "sigma": surface_tension_mixture(light, heavy, x_light),
    }


# ───────────────────────────────────────────────────────────────
#  Antoine Equation
# ───────────────────────────────────────────────────────────────
def antoine_pvap(component: str, T_C: float) -> float:
    """
    Return vapour pressure [mmHg] using Antoine equation.
    log10(P) = A – B / (C + T)  where T in °C, P in mmHg
    """
    if component not in COMPONENT_DB:
        raise ValueError(f"Component '{component}' not in database.")
    c = COMPONENT_DB[component]
    log_P = c["A"] - c["B"] / (c["C"] + T_C)
    return 10 ** log_P  # mmHg


def pvap_to_atm(P_mmHg: float) -> float:
    return P_mmHg / 760.0


def pvap_to_bar(P_mmHg: float) -> float:
    return P_mmHg * 0.00133322


# ───────────────────────────────────────────────────────────────
#  Relative Volatility
# ───────────────────────────────────────────────────────────────
def relative_volatility(light: str, heavy: str, T_C: float) -> float:
    """α = P_light* / P_heavy*  (Raoult's law, ideal)"""
    P_light = antoine_pvap(light, T_C)
    P_heavy = antoine_pvap(heavy, T_C)
    return P_light / P_heavy


def avg_relative_volatility(light: str, heavy: str,
                             T_top: float, T_feed: float, T_bot: float) -> float:
    """Geometric mean of α at top, feed, and bottom temperatures."""
    a1 = relative_volatility(light, heavy, T_top)
    a2 = relative_volatility(light, heavy, T_feed)
    a3 = relative_volatility(light, heavy, T_bot)
    return (a1 * a2 * a3) ** (1/3)


# ───────────────────────────────────────────────────────────────
#  VLE — Raoult's Law (binary)
# ───────────────────────────────────────────────────────────────
def vle_raoult(light: str, heavy: str,
               T_C: float, P_total_mmHg: float) -> Tuple[float, float]:
    """
    Given T and P, compute equilibrium compositions (x, y) for binary.
    Returns x (liquid) and y (vapour) of light component.
    This solves for the bubble-point COMPOSITION at given T,P using:
        y_i = x_i * P_i* / P
    For a specified x, returns y.
    """
    P1 = antoine_pvap(light, T_C)
    P2 = antoine_pvap(heavy, T_C)
    # x1 from overall pressure: P = x1*P1 + (1-x1)*P2
    x1 = (P_total_mmHg - P2) / (P1 - P2)
    x1 = max(0.0, min(1.0, x1))
    y1 = x1 * P1 / P_total_mmHg
    y1 = max(0.0, min(1.0, y1))
    return x1, y1


def y_from_x(x: float, alpha: float) -> float:
    """y = α·x / (1 + (α-1)·x) — constant relative volatility VLE"""
    return alpha * x / (1 + (alpha - 1) * x)


def x_from_y(y: float, alpha: float) -> float:
    """Inverse: x = y / (α - (α-1)·y)"""
    return y / (alpha - (alpha - 1) * y)


def generate_xy_curve(alpha: float, n: int = 100) -> Tuple[np.ndarray, np.ndarray]:
    """Generate full x-y equilibrium curve for given α."""
    x = np.linspace(0, 1, n)
    y = y_from_x(x, alpha)
    return x, y


# ───────────────────────────────────────────────────────────────
#  Bubble-point & Dew-point Temperature
# ───────────────────────────────────────────────────────────────
def bubble_point_T(light: str, heavy: str,
                   x_light: float, P_mmHg: float,
                   T_init: Optional[float] = None) -> float:
    """
    Find bubble-point temperature for binary mixture.
    Convergence by successive substitution.
    """
    db_light = COMPONENT_DB[light]
    db_heavy = COMPONENT_DB[heavy]
    # Initial guess: weighted Tb
    if T_init is None:
        T = x_light * db_light["Tb"] + (1 - x_light) * db_heavy["Tb"]
    else:
        T = T_init

    for _ in range(100):
        P1 = antoine_pvap(light, T)
        P2 = antoine_pvap(heavy, T)
        P_calc = x_light * P1 + (1 - x_light) * P2
        if abs(P_calc - P_mmHg) / P_mmHg < 1e-6:
            break
        # Newton correction (dP/dT ≈ ΔH_vap/RT² × P — simplified)
        T += (P_mmHg - P_calc) / (P_calc * 0.04)  # empirical step

    return round(T, 3)


def dew_point_T(light: str, heavy: str,
                y_light: float, P_mmHg: float,
                T_init: Optional[float] = None) -> float:
    """Find dew-point temperature for binary mixture."""
    db_light = COMPONENT_DB[light]
    db_heavy = COMPONENT_DB[heavy]
    if T_init is None:
        T = y_light * db_light["Tb"] + (1 - y_light) * db_heavy["Tb"]
    else:
        T = T_init

    for _ in range(100):
        P1 = antoine_pvap(light, T)
        P2 = antoine_pvap(heavy, T)
        sum_y_over_p = y_light / P1 + (1 - y_light) / P2
        P_calc = 1.0 / sum_y_over_p
        if abs(P_calc - P_mmHg) / P_mmHg < 1e-6:
            break
        T += (P_mmHg - P_calc) / (P_calc * 0.04)

    return round(T, 3)


# ───────────────────────────────────────────────────────────────
#  Feed Condition — q value
# ───────────────────────────────────────────────────────────────
def feed_q_value(feed_condition: str,
                 T_feed: float = None,
                 T_bubble: float = None,
                 T_dew: float = None,
                 Cp_L: float = 150.0,    # J/mol·K  (approximate)
                 lambda_vap: float = 30000.0) -> float:  # J/mol
    """
    q = heat required to vaporize 1 mol feed / molar latent heat
    q > 1 : sub-cooled liquid
    q = 1 : saturated liquid (bubble point)
    0<q<1 : partial vapour
    q = 0 : saturated vapour (dew point)
    q < 0 : super-heated vapour
    """
    conditions = {
        "Saturated Liquid":      1.0,
        "Saturated Vapor":       0.0,
        "Subcooled Liquid":      None,   # computed below
        "Superheated Vapor":     None,
        "Partial Vapor (50%)":   0.5,
    }
    if feed_condition in conditions and conditions[feed_condition] is not None:
        return conditions[feed_condition]

    if feed_condition == "Subcooled Liquid" and T_feed is not None and T_bubble is not None:
        q = 1 + Cp_L * (T_bubble - T_feed) / lambda_vap
        return round(q, 4)
    if feed_condition == "Superheated Vapor" and T_feed is not None and T_dew is not None:
        q = -Cp_L * (T_feed - T_dew) / lambda_vap
        return round(q, 4)

    return 1.0  # default: saturated liquid


# ───────────────────────────────────────────────────────────────
#  Helper: get component properties dict
# ───────────────────────────────────────────────────────────────
def get_component_props(name: str) -> dict:
    if name not in COMPONENT_DB:
        return {}
    return COMPONENT_DB[name].copy()


def list_components() -> list:
    return sorted(COMPONENT_DB.keys())
