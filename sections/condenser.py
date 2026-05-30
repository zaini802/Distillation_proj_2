"""sections/condenser.py — Condenser Design Module"""
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from calculations.distillation_calc import condenser_duty
from thermodynamics.thermo_engine import COMPONENT_DB
from sections.phase3_style import render_phase3_style


def render():
    st.markdown("""
    <div class="section-header">
        <h1>❄️ Condenser Design</h1>
        <p>Condenser heat duty, cooling water requirement, heat transfer area. Types: Total, Partial condenser.</p>
    </div>
    """, unsafe_allow_html=True)

    render_phase3_style()

    feed     = st.session_state.get("feed", {})
    shortcut = st.session_state.get("shortcut", {})
    thermo   = st.session_state.get("thermo", {})

    if not feed or not shortcut:
        st.warning("⚠️ Complete **Feed Specifications** and **Shortcut Design** first.")
        return

    R    = shortcut.get("R", 2.0)
    D_f  = shortcut.get("D", 50.0)
    V    = (R + 1) * D_f   # vapour to condenser
    dist_props = feed.get("distillate_props") or thermo.get("distillate_props") or {}

    tab1, tab2, tab3 = st.tabs(["❄️ Duty Calculation", "🔧 Type Selection", "📋 Summary"])

    with tab1:
        st.markdown("""
        <div class="formula-box">
          <div class="formula-title">Condenser Duty</div>
          Q<sub>cond</sub> = V × (λ + C<sub>p,L</sub>·ΔT) / η &nbsp;|&nbsp;
          ṁ<sub>CW</sub> = Q<sub>cond</sub> / (C<sub>p,water</sub> × ΔT<sub>CW</sub>)<br>
          Area = Q / (U × ΔT<sub>LM</sub>)
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="info-panel">
        📌 Vapour to condenser V = (R+1)×D = ({R:.3f}+1) × {D_f:.2f} = <strong>{V:.2f} kmol/h</strong>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            V_inp      = st.number_input("Vapour Flow to Condenser [kmol/h]",
                value=float(round(V, 2)), min_value=0.1, max_value=10000.0, step=0.5)
            lambda_vap = st.number_input("Latent Heat λ [J/mol]",
                value=float(feed.get("Hvap_distillate", thermo.get("Hvap_distillate", dist_props.get("Hvap", 30000.0)))),
                min_value=5000.0, max_value=100000.0, step=500.0,
                help="Default comes from Thermodynamics DB distillate mixture estimate.")
            Cp_L = st.number_input("Condensate Cp,L [J/mol·K]",
                value=float(feed.get("Cp_L_distillate", thermo.get("Cp_L_distillate", dist_props.get("Cp_L", 150.0)))),
                min_value=30.0, max_value=400.0, step=5.0)
        with c2:
            T_in   = st.number_input("Vapour Inlet Temp [°C]",
                value=float(thermo.get("T_bubble_D", 80.0)), min_value=0.0, max_value=300.0, step=1.0)
            T_out  = st.number_input("Condensate Outlet Temp [°C]",
                value=float(thermo.get("T_bubble_D", 80.0) - 5.0), min_value=0.0, max_value=300.0, step=1.0)
        with c3:
            cw_in  = st.number_input("Cooling Water Inlet [°C]",  value=25.0, min_value=5.0, max_value=40.0, step=1.0)
            cw_out = st.number_input("Cooling Water Outlet [°C]", value=35.0, min_value=10.0, max_value=60.0, step=1.0)
            U_cond = st.number_input("Overall U [W/m²·K]", value=700.0, min_value=100.0, max_value=3000.0, step=50.0,
                help="Water-cooled condenser: 500-1000 W/m²K")
            cond_eff = st.number_input("Condenser Efficiency", value=0.90, min_value=0.50, max_value=1.00, step=0.01)

        result = condenser_duty(V_inp, lambda_vap, T_in, T_out, Cp_L=Cp_L, efficiency=cond_eff)

        # LMTD for area
        dT1 = T_in  - cw_out
        dT2 = T_out - cw_in
        if dT1 <= 0 or dT2 <= 0:
            dT_LM = 10.0
        elif abs(dT1 - dT2) < 0.01:
            dT_LM = dT1
        else:
            dT_LM = (dT1 - dT2) / np.log(dT1 / dT2)

        A_cond = (result["Q_condenser_kW"] * 1000) / (U_cond * dT_LM)
        CW_m3h = result["cooling_water_kg_h"] / 1000  # m³/h (density ≈ 1000 kg/m³)
        min_approach = min(dT1, dT2)
        condenser_flux_kw_m2 = result["Q_condenser_kW"] / max(A_cond, 1e-9)
        approach_ok = min_approach >= 5

        st.markdown(f"""
        <div class="formula-box" style="border-left:4px solid #00b4d8;">
          <div class="formula-title">Step-by-step condenser calculation</div>
          <b>1. Vapour load:</b>
          V = (R+1)D = ({R:.3f}+1)×{D_f:.2f} = <b>{V:.2f} kmol/h</b><br>
          <div class="phase3-calc-separator"></div>
          <b>2. Total duty:</b>
          Q<sub>cond</sub> = latent + sensible = <b>{result['Q_condenser_kW']:.1f} kW</b>
          (latent {result['Q_latent_kW']:.1f} kW, sensible {result['Q_sensible_kW']:.1f} kW)<br>
          <b>3. Cooling-water flow:</b>
          ṁ<sub>CW</sub> = Q/(C<sub>p,w</sub>ΔT<sub>w</sub>)
          = <b>{result['cooling_water_kg_h']:.0f} kg/h</b> = <b>{CW_m3h:.2f} m³/h</b><br>
          <div class="phase3-calc-separator"></div>
          <b>4. LMTD:</b>
          ΔT<sub>1</sub> = T<sub>vap</sub>−T<sub>CW,out</sub> = {dT1:.2f} °C,
          ΔT<sub>2</sub> = T<sub>cond</sub>−T<sub>CW,in</sub> = {dT2:.2f} °C,
          ΔT<sub>LM</sub> = <b>{dT_LM:.2f} °C</b><br>
          <b>5. Heat-transfer area:</b>
          A = Q/(U×ΔT<sub>LM</sub>) = {result['Q_condenser_kW']:.1f}×1000 / ({U_cond:.0f}×{dT_LM:.2f})
          = <b>{A_cond:.2f} m²</b><br>
          <b>6. Heat flux:</b> q'' = Q/A = <b>{condenser_flux_kw_m2:.1f} kW/m²</b>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Condenser Duty Q_cond", f"{result['Q_condenser_kW']:.1f} kW")
        c2.metric("Latent Load", f"{result['Q_latent_kW']:.1f} kW")
        c3.metric("Sensible Load", f"{result['Q_sensible_kW']:.1f} kW")
        c4.metric("Cooling Water", f"{result['cooling_water_kg_h']:.0f} kg/h")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("CW Flow", f"{CW_m3h:.2f} m³/h")
        c2.metric("ΔT_LM", f"{dT_LM:.2f} °C")
        c3.metric("Overall U", f"{U_cond:.0f} W/m²·K")
        c4.metric("Heat Transfer Area", f"{A_cond:.2f} m²")

        st.markdown(f"""
        <div class="success-panel">
        ✅ <strong>Condenser Sizing:</strong> Q = {result['Q_condenser_kW']:.1f} kW &nbsp;|&nbsp;
        CW = {result['cooling_water_kg_h']:.0f} kg/h ({CW_m3h:.2f} m³/h) &nbsp;|&nbsp;
        Area = <strong>{A_cond:.2f} m²</strong> &nbsp;|&nbsp; ΔT_LM = {dT_LM:.2f} °C
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="{'success-panel' if approach_ok else 'warn-panel'}">
        {'✅' if approach_ok else '⚠️'} <strong>Cooling approach check:</strong>
        Minimum terminal approach = {min_approach:.2f} °C. Preliminary water-cooled exchangers usually prefer ≥ 5 °C.
        {'Thermal driving force is acceptable.' if approach_ok else 'Increase CW flow, reduce CW outlet temperature, or increase exchanger area.'}
        </div>
        """, unsafe_allow_html=True)

        fig_load = go.Figure(go.Bar(
            x=["Latent Load", "Sensible Load", "Total Duty"],
            y=[result["Q_latent_kW"], result["Q_sensible_kW"], result["Q_condenser_kW"]],
            marker_color=["#00b4d8", "#f59e0b", "#22c55e"],
            text=[f"{v:.0f} kW" for v in [result["Q_latent_kW"], result["Q_sensible_kW"], result["Q_condenser_kW"]]],
            textposition="outside"
        ))
        fig_load.update_layout(
            template="plotly_dark", paper_bgcolor="#0a0e14", plot_bgcolor="#111827",
            font=dict(family="Barlow", color="#e2e8f0"),
            title=dict(text="Condenser Duty Breakdown", font=dict(color="#f8d477", size=19)),
            xaxis=dict(gridcolor="#1e3a5f"),
            yaxis=dict(title="Duty [kW]", gridcolor="#1e3a5f"),
            height=340, margin=dict(t=48)
        )
        st.plotly_chart(fig_load, use_container_width=True)

    with tab2:
        st.markdown("### Condenser Type Selection")
        types_df = pd.DataFrame({
            "Type": ["Total Condenser", "Partial Condenser", "Air-cooled Condenser"],
            "Product": ["Liquid distillate", "Vapour + Liquid", "Liquid distillate"],
            "Cooling Medium": ["Cooling water", "Cooling water", "Ambient air"],
            "Best For": [
                "Standard service — produces reflux + liquid distillate product",
                "When vapour product needed, or at high pressures",
                "Remote locations, water scarce, high-temp condenser (>60°C approach)"
            ]
        })
        st.dataframe(types_df, use_container_width=True, hide_index=True)

    with tab3:
        st.markdown("### 📋 Condenser Design Summary")
        df = pd.DataFrame({
            "Parameter": ["Vapour to condenser V", "Latent heat λ", "Condensate Cp,L",
                           "Inlet temp T_in", "Outlet temp T_out",
                           "CW inlet", "CW outlet",
                           "Q_cond (total)", "Q_latent", "Q_sensible",
                           "Cooling water flow", "ΔT_LM", "Overall U",
                           "Heat transfer area"],
            "Value": [f"{V_inp:.2f}", f"{lambda_vap:.0f}", f"{Cp_L:.1f}",
                       f"{T_in:.1f}", f"{T_out:.1f}",
                       f"{cw_in:.1f}", f"{cw_out:.1f}",
                       f"{result['Q_condenser_kW']:.2f}", f"{result['Q_latent_kW']:.2f}",
                       f"{result['Q_sensible_kW']:.2f}",
                       f"{result['cooling_water_kg_h']:.1f}", f"{dT_LM:.3f}",
                       f"{U_cond:.0f}", f"{A_cond:.3f}"],
            "Unit": ["kmol/h", "J/mol", "J/mol·K", "°C", "°C", "°C", "°C",
                      "kW", "kW", "kW", "kg/h", "°C", "W/m²·K", "m²"]
        })
        st.dataframe(df, use_container_width=True, hide_index=True)

    # ── Save ──────────────────────────────────────────────────
    st.markdown("<div class='eng-divider'></div>", unsafe_allow_html=True)
    if st.button("💾 Save Condenser Results", type="primary"):
        st.session_state.condenser = {
            "Q_cond_kW": result["Q_condenser_kW"],
            "Q_condenser_kW": result["Q_condenser_kW"],
            "Q_latent_kW": result["Q_latent_kW"],
            "Q_sensible_kW": result["Q_sensible_kW"],
            "cooling_water_kg_h": result["cooling_water_kg_h"],
            "CW_m3h": round(CW_m3h, 3),
            "A_cond_m2": round(A_cond, 3),
            "heat_flux_kW_m2": round(condenser_flux_kw_m2, 2),
            "min_approach_C": round(min_approach, 2),
            "delta_T_LM": round(dT_LM, 3),
            "U_cond": U_cond,
            "V_condenser": V_inp,
            "lambda_vap": lambda_vap,
            "Cp_L": Cp_L,
        }
        st.success(f"✅ Condenser saved: Q = {result['Q_condenser_kW']:.1f} kW, A = {A_cond:.2f} m². Proceed to **Mechanical Design**.")
