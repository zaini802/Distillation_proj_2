"""sections/mechanical.py — Mechanical Design (ASME UG-27)"""
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from calculations.distillation_calc import shell_thickness_asme
from sections.phase3_style import render_phase3_style


def render():
    st.markdown("""
    <div class="section-header">
        <h1>⚙️ Mechanical Design</h1>
        <p>ASME UG-27 shell thickness, material selection, nozzle sizing, support loads — industrial standard calculations.</p>
    </div>
    """, unsafe_allow_html=True)

    render_phase3_style()

    feed     = st.session_state.get("feed", {})
    diameter = st.session_state.get("diameter", {})
    height   = st.session_state.get("height", {})

    D_col_m  = diameter.get("D_column_std_m", 1.2)
    D_col_mm = D_col_m * 1000
    H_total  = height.get("total_with_skirt_m", 20.0)

    tab1, tab2, tab3 = st.tabs(["⚙️ Shell Thickness (ASME)", "🔧 Nozzle Sizing", "📋 Summary"])

    with tab1:
        st.markdown("""
        <div class="formula-box">
          <div class="formula-title">ASME UG-27 — Cylindrical Shell Thickness</div>
          t = P × R / (S × E − 0.6 × P) + CA<br>
          P [MPa], R [mm], S = allowable stress [MPa], E = joint efficiency, CA = corrosion allowance [mm]
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            P_design_bar = st.number_input("Design Pressure [bar(g)]",
                value=float(max(feed.get("P_col_bar", 1.013) * 1.1 + 1.0, 2.0)),
                min_value=0.5, max_value=200.0, step=0.5, format="%.2f",
                help="Typically operating pressure × 1.1 + 1 bar margin")
            D_inner_mm   = st.number_input("Inner Diameter D_i [mm]",
                value=float(round(D_col_mm, 0)), min_value=100.0, max_value=10000.0, step=50.0)
        with c2:
            material = st.selectbox("Shell Material", [
                "Carbon Steel A516-70 (S=138 MPa)",
                "Stainless Steel 304 (S=138 MPa)",
                "Stainless Steel 316L (S=115 MPa)",
                "Low Alloy Steel A387-11 (S=172 MPa)",
                "Duplex SS 2205 (S=172 MPa)",
            ])
            S_map = {
                "Carbon Steel A516-70 (S=138 MPa)": 138.0,
                "Stainless Steel 304 (S=138 MPa)": 138.0,
                "Stainless Steel 316L (S=115 MPa)": 115.0,
                "Low Alloy Steel A387-11 (S=172 MPa)": 172.0,
                "Duplex SS 2205 (S=172 MPa)": 172.0,
            }
            S_allow = S_map[material]
        with c3:
            E_weld = st.select_slider("Joint Efficiency E",
                options=[0.70, 0.85, 1.00],
                value=1.00,
                help="1.0 = full radiography, 0.85 = spot radiography, 0.7 = no examination")
            CA = st.number_input("Corrosion Allowance CA [mm]",
                value=3.0, min_value=0.0, max_value=10.0, step=0.5)

        result = shell_thickness_asme(D_inner_mm, P_design_bar, S_allow, E_weld, CA)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("t (calculated)",         f"{result['t_calculated_mm']:.2f} mm")
        c2.metric("t (+ corrosion allow.)", f"{result['t_with_CA_mm']:.2f} mm")
        c3.metric("t (standard plate)",     f"{result['t_standard_mm']} mm")
        c4.metric("Outer Diameter",         f"{result['D_outer_mm']:.1f} mm")

        # Shell weight estimate
        rho_steel = 7850  # kg/m³
        t_m = result["t_standard_mm"] / 1000
        D_mid_m = (D_inner_mm / 1000 + t_m)
        V_shell = np.pi * D_mid_m * t_m * H_total
        W_shell = V_shell * rho_steel
        t_available_mm = max(result["t_standard_mm"] - CA, 0.1)
        R_inner_mm = D_inner_mm / 2
        MAWP_MPa = (S_allow * E_weld * t_available_mm) / (R_inner_mm + 0.6 * t_available_mm)
        MAWP_bar = MAWP_MPa * 10
        pressure_util = P_design_bar / max(MAWP_bar, 1e-9) * 100
        util_ok = pressure_util <= 90

        st.markdown(f"""
        <div class="formula-box" style="border-left:4px solid #f59e0b;">
          <div class="formula-title">Step-by-step shell thickness check</div>
          <b>1. ASME UG-27 required shell:</b>
          t = PR/(SE − 0.6P) = <b>{result['t_calculated_mm']:.2f} mm</b><br>
          <b>2. Corrosion allowance:</b>
          t + CA = {result['t_calculated_mm']:.2f} + {CA:.1f}
          = <b>{result['t_with_CA_mm']:.2f} mm</b><br>
          <div class="phase3-calc-separator"></div>
          <b>3. Standard plate selected:</b>
          t<sub>std</sub> = <b>{result['t_standard_mm']} mm</b>,
          available pressure thickness = t<sub>std</sub> − CA = <b>{t_available_mm:.2f} mm</b><br>
          <b>4. MAWP estimate:</b>
          P = SEt/(R + 0.6t) = <b>{MAWP_bar:.2f} bar(g)</b><br>
          <b>5. Pressure utilisation:</b>
          P<sub>design</sub>/MAWP = {P_design_bar:.2f}/{MAWP_bar:.2f}
          = <b>{pressure_util:.1f}%</b>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Design Pressure", f"{P_design_bar:.2f} bar(g)")
        c2.metric("P in MPa", f"{result['P_design_MPa']:.4f} MPa")
        c3.metric("S allowable", f"{S_allow:.0f} MPa")
        c4.metric("Est. Shell Weight", f"{W_shell:.0f} kg")

        c1, c2 = st.columns(2)
        c1.metric("Estimated MAWP", f"{MAWP_bar:.2f} bar(g)")
        c2.metric("Pressure Utilisation", f"{pressure_util:.1f}%")

        st.markdown(f"""
        <div class="{'success-panel' if util_ok else 'warn-panel'}">
        {'✅' if util_ok else '⚠️'} <strong>Mechanical margin check:</strong>
        utilisation = {pressure_util:.1f}% of estimated MAWP.
        {'Plate selection has a reasonable preliminary pressure margin.' if util_ok else 'Consider a thicker standard plate or higher allowable-stress material.'}
        </div>
        """, unsafe_allow_html=True)

        # Wind load (simplified)
        st.markdown("### Wind & Earthquake Loads (Simplified)")
        c1, c2 = st.columns(2)
        with c1:
            wind_speed = st.number_input("Wind Speed [km/h]", value=120.0, min_value=50.0, max_value=300.0, step=5.0)
            P_wind_Pa  = 0.5 * 1.2 * (wind_speed / 3.6)**2  # ½ρv²
            F_wind     = P_wind_Pa * D_col_m * H_total  # N
            M_wind     = F_wind * H_total / 2 / 1000     # kN·m
            st.metric("Wind Force", f"{F_wind/1000:.1f} kN")
            st.metric("Bending Moment", f"{M_wind:.1f} kN·m")
        with c2:
            W_total_kN = (W_shell * 9.81) / 1000
            st.metric("Shell Weight", f"{W_shell:.0f} kg ({W_total_kN:.1f} kN)")
            st.markdown(f"""
            <div class="info-panel" style="margin-top:8px">
            📌 Foundation design load ≈ {W_total_kN*1.3:.0f} kN (shell + internals + liquid × 1.3 safety factor)
            </div>
            """, unsafe_allow_html=True)

    with tab2:
        st.markdown("### 🔧 Nozzle Sizing (API / ASME)")
        st.markdown("""
        <div class="info-panel">
        Nozzle sizing follows process flow rates. Typical velocities: Liquid 1–2 m/s, Vapour 15–30 m/s.
        </div>
        """, unsafe_allow_html=True)

        nozzle_data = []
        nozzle_defs = [
            ("Feed Inlet", "Liquid", 1.5),
            ("Distillate Outlet", "Liquid", 1.5),
            ("Bottoms Outlet", "Liquid", 1.5),
            ("Vapour Outlet (to condenser)", "Vapour", 20.0),
            ("Vapour Inlet (from reboiler)", "Vapour", 20.0),
            ("Reflux Return", "Liquid", 1.5),
            ("Manway", "—", 0.0),
            ("Instrument Connections (×4)", "—", 0.0),
        ]

        F      = feed.get("F", 100.0)
        D_mol  = shortcut_D = st.session_state.get("shortcut", {}).get("D", F * 0.5)
        B_mol  = F - D_mol
        rho_L  = diameter.get("rho_L", 850.0)
        rho_V  = diameter.get("rho_V", 3.0)
        MW_avg = diameter.get("MW_avg", 80.0)

        for name, phase, v_typ in nozzle_defs:
            if v_typ == 0:
                nozzle_data.append({"Nozzle": name, "Phase": phase,
                                    "Flow": "—", "Velocity": "—", "d [mm]": "600 (manway)" if "Manway" in name else "25 (¾\")"})
                continue
            if phase == "Liquid":
                Q_m3s = (F * MW_avg / 3600) / rho_L
                d_m   = np.sqrt(4 * Q_m3s / (np.pi * v_typ))
            else:
                Q_m3s = (F * MW_avg / 3600) / rho_V
                d_m   = np.sqrt(4 * Q_m3s / (np.pi * v_typ))
            d_mm = max(50, round(d_m * 1000 / 25) * 25)  # round to nearest 25 mm (std)
            nozzle_data.append({
                "Nozzle": name, "Phase": phase,
                "Velocity [m/s]": f"{v_typ:.1f}",
                "Calc d [mm]": f"{d_m*1000:.1f}",
                "Std d [mm]": f"{d_mm}"
            })

        st.dataframe(pd.DataFrame(nozzle_data), use_container_width=True, hide_index=True)

    with tab3:
        st.markdown("### 📋 Mechanical Design Summary")
        df = pd.DataFrame({
            "Parameter": ["Inner Diameter D_i", "Outer Diameter D_o",
                           "Design Pressure P_des", "Allowable Stress S",
                           "Joint Efficiency E", "Corrosion Allowance CA",
                           "t_calculated", "t (+ CA)", "t_standard (plate)",
                           "Shell Height H", "Est. Shell Weight",
                           "Material", "Design Code"],
            "Value": [f"{D_inner_mm:.0f}", f"{result['D_outer_mm']:.1f}",
                       f"{P_design_bar:.2f}", f"{S_allow:.0f}",
                       f"{E_weld:.2f}", f"{CA:.1f}",
                       f"{result['t_calculated_mm']:.3f}", f"{result['t_with_CA_mm']:.3f}",
                       f"{result['t_standard_mm']}",
                       f"{H_total:.2f}", f"{W_shell:.0f}",
                       material.split(" (")[0], "ASME BPVC Sec. VIII Div. 1"],
            "Unit": ["mm", "mm", "bar(g)", "MPa", "—", "mm",
                      "mm", "mm", "mm", "m", "kg", "—", "—"]
        })
        st.dataframe(df, use_container_width=True, hide_index=True)

    # ── Save ──────────────────────────────────────────────────
    st.markdown("<div class='eng-divider'></div>", unsafe_allow_html=True)
    if st.button("💾 Save Mechanical Design", type="primary"):
        st.session_state.mechanical = {
            "t_shell_mm": result["t_standard_mm"],
            "t_calculated_mm": result["t_calculated_mm"],
            "D_inner_mm": D_inner_mm,
            "D_outer_mm": result["D_outer_mm"],
            "P_design_bar": P_design_bar,
            "S_allowable_MPa": S_allow,
            "E_weld": E_weld,
            "CA_mm": CA,
            "material": material.split(" (")[0],
            "W_shell_kg": round(W_shell, 0),
            "MAWP_bar_g": round(MAWP_bar, 3),
            "pressure_utilization_pct": round(pressure_util, 1),
            "design_code": "ASME BPVC Sec. VIII Div. 1",
        }
        st.success(f"✅ Mechanical design saved: t = {result['t_standard_mm']} mm, Material = {material.split('(')[0].strip()}.")
