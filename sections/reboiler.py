"""sections/reboiler.py — Reboiler Design Module"""
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd
from calculations.distillation_calc import reboiler_duty
from thermodynamics.thermo_engine import COMPONENT_DB
from sections.phase3_style import render_phase3_style


def render():
    st.markdown("""
    <div class="section-header">
        <h1>♨️ Reboiler Design</h1>
        <p>Heat duty calculation, steam consumption, heat transfer area sizing. Types: Kettle, Thermosyphon, Forced Circulation.</p>
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
    B_f  = shortcut.get("B", 50.0)
    light = feed.get("light", "Benzene")
    heavy = feed.get("heavy", "Toluene")
    bottoms_props = feed.get("bottoms_props") or thermo.get("bottoms_props") or {}

    # V' (vapour from reboiler) = V - (1-q)*F ≈ (R+1)*D for sat liquid feed
    q    = feed.get("q", 1.0)
    F    = feed.get("F", 100.0)
    V    = (R + 1) * D_f
    V_prime = V - (1 - q) * F  # stripping section vapour

    tab1, tab2, tab3 = st.tabs(["♨️ Duty Calculation", "🔧 Type Selection", "📋 Summary"])

    with tab1:
        st.markdown("""
        <div class="formula-box">
          <div class="formula-title">Reboiler Duty</div>
          Q<sub>reb</sub> = V' × λ &nbsp;|&nbsp; V' = L' − B &nbsp;(vapour from reboiler, stripping section)<br>
          Steam rate = Q<sub>reb</sub> / λ<sub>steam</sub> &nbsp;|&nbsp; Area = Q / (U × ΔTLM)
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="info-panel">
        📌 V = (R+1)×D = {V:.2f} kmol/h &nbsp;|&nbsp; V' (stripping vapour) = <strong>{V_prime:.2f} kmol/h</strong>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            lambda_vap  = st.number_input("Latent Heat of Vaporisation λ [J/mol]",
                value=float(feed.get("Hvap_bottoms", thermo.get("Hvap_bottoms", bottoms_props.get("Hvap", 30000.0)))),
                min_value=5000.0, max_value=100000.0, step=500.0,
                help="Default comes from Thermodynamics DB mixture estimate; override for final design.")
            reb_eff     = st.number_input("Reboiler Efficiency", value=0.85, min_value=0.50, max_value=1.00, step=0.01)
        with c2:
            steam_temp  = st.number_input("Steam Temperature [°C]", value=150.0, min_value=100.0, max_value=300.0, step=5.0)
            T_bot       = st.number_input("Bottoms Temperature [°C]",
                value=float(thermo.get("T_bubble_B", 110.0)), min_value=20.0, max_value=350.0, step=1.0)
        with c3:
            U_reb       = st.number_input("Overall U [W/m²·K]", value=800.0, min_value=100.0, max_value=3000.0, step=50.0,
                help="Kettle: 500-1000, Thermosyphon: 700-1500, Forced: 1000-3000 W/m²K")
            V_prime_inp = st.number_input("V' Stripping Vapour [kmol/h]",
                value=float(round(max(V_prime, 1.0), 2)), min_value=0.1, max_value=10000.0, step=0.5)

        result = reboiler_duty(V_prime_inp, lambda_vap, reb_eff)

        # Area calculation
        delta_T_LM = steam_temp - T_bot
        if delta_T_LM <= 0:
            delta_T_LM = 10.0
        A_reb = (result["Q_reboiler_kW"] * 1000) / (U_reb * delta_T_LM)
        heat_flux_kw_m2 = result["Q_reboiler_kW"] / max(A_reb, 1e-9)
        ua_kw_k = U_reb * A_reb / 1000
        flux_ok = 10 <= heat_flux_kw_m2 <= 80

        st.markdown(f"""
        <div class="formula-box" style="border-left:4px solid #f59e0b;">
          <div class="formula-title">Step-by-step reboiler calculation</div>
          <b>1. Stripping vapour:</b>
          V' = V - (1-q)F = {V:.2f} - (1-{q:.2f})×{F:.2f} = <b>{V_prime:.2f} kmol/h</b><br>
          <div class="phase3-calc-separator"></div>
          <b>2. Heat duty:</b>
          Q<sub>reb</sub> = V'×λ/η = {V_prime_inp:.2f}×{lambda_vap:.0f}/({reb_eff:.2f})
          = <b>{result['Q_reboiler_kW']:.1f} kW</b><br>
          <b>3. Steam consumption:</b>
          ṁ<sub>steam</sub> = Q/λ<sub>steam</sub> = <b>{result['steam_consumption_kg_h']:.1f} kg/h</b><br>
          <div class="phase3-calc-separator"></div>
          <b>4. Heat-transfer area:</b>
          A = Q/(U×ΔT<sub>LM</sub>) = {result['Q_reboiler_kW']:.1f}×1000 / ({U_reb:.0f}×{delta_T_LM:.1f})
          = <b>{A_reb:.2f} m²</b><br>
          <b>5. Heat flux:</b>
          q'' = Q/A = {result['Q_reboiler_kW']:.1f}/{A_reb:.2f}
          = <b>{heat_flux_kw_m2:.1f} kW/m²</b>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Reboiler Duty Q_reb", f"{result['Q_reboiler_kW']:.1f} kW")
        c2.metric("Steam Consumption", f"{result['steam_consumption_kg_h']:.1f} kg/h")
        c3.metric("ΔT_LM (steam-process)", f"{delta_T_LM:.1f} °C")
        c4.metric("Heat Transfer Area", f"{A_reb:.2f} m²")

        c1, c2 = st.columns(2)
        c1.metric("UA", f"{ua_kw_k:.2f} kW/K")
        c2.metric("Heat Flux", f"{heat_flux_kw_m2:.1f} kW/m²")

        st.markdown(f"""
        <div class="success-panel">
        ✅ <strong>Reboiler Sizing:</strong> Q = {result['Q_reboiler_kW']:.1f} kW
        ({result['Q_reboiler_MW']:.3f} MW) &nbsp;|&nbsp;
        Steam @ {steam_temp}°C: {result['steam_consumption_kg_h']:.1f} kg/h &nbsp;|&nbsp;
        Area: <strong>{A_reb:.2f} m²</strong>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="{'success-panel' if flux_ok else 'warn-panel'}">
        {'✅' if flux_ok else '⚠️'} <strong>Heat flux check:</strong>
        q'' = {heat_flux_kw_m2:.1f} kW/m². Typical preliminary kettle/thermosyphon range is about 10-80 kW/m².
        {'Looks reasonable for preliminary design.' if flux_ok else 'Review U, ΔT, fouling allowance, or select a different reboiler type.'}
        </div>
        """, unsafe_allow_html=True)

        steam_range = np.linspace(max(T_bot + 5, 105), max(T_bot + 25, 220), 50)
        area_range = (result["Q_reboiler_kW"] * 1000) / (U_reb * np.maximum(steam_range - T_bot, 1))
        fig_area = go.Figure()
        fig_area.add_trace(go.Scatter(
            x=steam_range, y=area_range, mode="lines",
            line=dict(color="#f59e0b", width=3.2),
            name="Required area"
        ))
        fig_area.add_vline(x=steam_temp, line_dash="dot", line_color="#00b4d8", line_width=3,
                           annotation_text=f"Selected {steam_temp:.0f}°C",
                           annotation_font_color="#00d4ff")
        fig_area.update_layout(
            template="plotly_dark", paper_bgcolor="#0a0e14", plot_bgcolor="#111827",
            font=dict(family="Barlow", color="#e2e8f0"),
            title=dict(text="Reboiler Area Sensitivity vs Steam Temperature",
                       font=dict(color="#f8d477", size=19)),
            xaxis=dict(title="Steam Temperature [°C]", gridcolor="#1e3a5f"),
            yaxis=dict(title="Required Area [m²]", gridcolor="#1e3a5f"),
            height=340, margin=dict(t=48)
        )
        st.plotly_chart(fig_area, use_container_width=True)

    with tab2:
        st.markdown("### Reboiler Type Selection Guide")
        types_data = {
            "Type": ["Kettle Reboiler", "Thermosyphon (Vertical)", "Thermosyphon (Horizontal)", "Forced Circulation"],
            "U [W/m²·K]": ["500–1000", "700–1200", "800–1500", "1000–3000"],
            "Best For": [
                "Small duty, clean service, vacuum/low pressure",
                "Moderate duty, wide turndown, most common industrial choice",
                "High viscosity, fouling service, moderate duty",
                "High viscosity, fouling, cracking service, exact flow control",
            ],
            "Limitations": [
                "Large footprint, high inventory, limited turndown",
                "Cannot handle high viscosity or heavy fouling",
                "More expensive, requires pump",
                "Highest cost, requires pump, complex control",
            ]
        }
        st.dataframe(pd.DataFrame(types_data), use_container_width=True, hide_index=True)

        Q_kW = result["Q_reboiler_kW"]
        if Q_kW < 500:
            rec = "**Kettle Reboiler** — low duty, simple installation"
        elif Q_kW < 2000:
            rec = "**Vertical Thermosyphon** — most common industrial choice for moderate duty"
        else:
            rec = "**Horizontal Thermosyphon or Forced Circulation** — high duty application"
        st.markdown(f'<div class="info-panel">📌 Recommended for Q = {Q_kW:.0f} kW: {rec}</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown("### 📋 Reboiler Design Summary")
        df = pd.DataFrame({
            "Parameter": ["V' (stripping vapour)", "Latent heat λ", "Reboiler efficiency",
                           "Reboiler duty Q_reb", "Steam temperature", "Bottoms temperature",
                           "ΔT_LM", "Overall U", "Heat transfer area",
                           "Steam consumption (150°C LP steam)"],
            "Value": [f"{V_prime_inp:.2f}", f"{lambda_vap:.0f}", f"{reb_eff:.2f}",
                       f"{result['Q_reboiler_kW']:.2f}", f"{steam_temp:.1f}", f"{T_bot:.1f}",
                       f"{delta_T_LM:.1f}", f"{U_reb:.0f}", f"{A_reb:.3f}",
                       f"{result['steam_consumption_kg_h']:.2f}"],
            "Unit": ["kmol/h", "J/mol", "—", "kW", "°C", "°C",
                      "°C", "W/m²·K", "m²", "kg/h"]
        })
        st.dataframe(df, use_container_width=True, hide_index=True)

    # ── Save ──────────────────────────────────────────────────
    st.markdown("<div class='eng-divider'></div>", unsafe_allow_html=True)
    if st.button("💾 Save Reboiler Results", type="primary"):
        st.session_state.reboiler = {
            "Q_reb_kW": result["Q_reboiler_kW"],
            "Q_reboiler_kW": result["Q_reboiler_kW"],
            "Q_reboiler_MW": result["Q_reboiler_MW"],
            "steam_kg_h": result["steam_consumption_kg_h"],
            "steam_consumption_kg_h": result["steam_consumption_kg_h"],
            "A_reb_m2": round(A_reb, 3),
            "heat_flux_kW_m2": round(heat_flux_kw_m2, 2),
            "UA_kW_K": round(ua_kw_k, 3),
            "V_prime": V_prime_inp,
            "lambda_vap": lambda_vap,
            "delta_T_LM": delta_T_LM,
            "U_reb": U_reb,
        }
        st.success(f"✅ Reboiler saved: Q = {result['Q_reboiler_kW']:.1f} kW, A = {A_reb:.2f} m². Proceed to **Condenser Design**.")
