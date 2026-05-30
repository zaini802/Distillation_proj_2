"""sections/diameter.py — Column Diameter Design (Fair Method)"""
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd
from calculations.distillation_calc import column_diameter_tray
from thermodynamics.thermo_engine import COMPONENT_DB, binary_mixture_props


def render():
    st.markdown("""
    <div class="section-header">
        <h1>📐 Column Diameter Design</h1>
        <p>Fair method — flooding velocity, Souders-Brown coefficient, net area calculation, standard diameter selection.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <style>
    .section-header h1 {
        color: #f8d477 !important;
        text-shadow: 0 0 16px rgba(248, 212, 119, 0.24);
    }
    .section-header p {
        color: #dbeafe !important;
        font-weight: 700;
    }
    div[data-testid="stMarkdownContainer"] h3,
    div[data-testid="stMarkdownContainer"] h4 {
        color: #f8d477 !important;
        font-family: 'Barlow Condensed', sans-serif;
        font-weight: 900 !important;
        letter-spacing: 0;
        text-shadow: 0 0 14px rgba(248, 212, 119, 0.20);
    }
    label p,
    div[data-testid="stWidgetLabel"] p {
        color: #ff5b6e !important;
        font-weight: 900 !important;
        text-shadow: 0 0 10px rgba(239, 68, 68, 0.22);
    }
    .formula-box {
        color: #eaf6ff !important;
        background: linear-gradient(135deg, rgba(8, 14, 24, 0.99), rgba(15, 23, 42, 0.97)) !important;
        border: 1px solid rgba(0, 180, 216, 0.44) !important;
        border-left: 4px solid #00b4d8 !important;
        border-radius: 8px !important;
        box-shadow: 0 0 0 1px rgba(255,255,255,0.03), 0 12px 28px rgba(0,0,0,0.18);
        font-size: 1.01rem !important;
        line-height: 1.75;
    }
    .formula-box .formula-title {
        color: #f8d477 !important;
        font-size: 1.05rem !important;
        font-weight: 900 !important;
        letter-spacing: 0.2px;
        margin-bottom: 0.55rem;
    }
    .formula-box b,
    .formula-box strong,
    .info-panel strong,
    .success-panel strong,
    .warn-panel strong {
        color: #22c55e !important;
        font-weight: 900 !important;
    }
    .info-panel,
    .success-panel,
    .warn-panel {
        color: #eaf6ff !important;
        font-size: 1rem !important;
        line-height: 1.65;
        background: linear-gradient(135deg, rgba(8, 14, 24, 0.98), rgba(15, 23, 42, 0.96)) !important;
        box-shadow: 0 10px 24px rgba(0,0,0,0.15);
    }
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.98), rgba(8, 14, 24, 0.98));
        border: 1px solid rgba(0, 180, 216, 0.48);
        border-radius: 8px;
        padding: 0.9rem 1rem;
        min-height: 112px;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.04), 0 10px 24px rgba(0,0,0,0.16);
    }
    div[data-testid="stMetricLabel"] p {
        color: #ff5b6e !important;
        font-weight: 900 !important;
        font-size: 0.95rem !important;
    }
    div[data-testid="stMetricValue"] {
        color: #00d4ff !important;
        font-family: 'Share Tech Mono', monospace;
        font-weight: 900 !important;
        text-shadow: 0 0 14px rgba(0, 180, 216, 0.18);
    }
    </style>
    """, unsafe_allow_html=True)

    feed     = st.session_state.get("feed", {})
    shortcut = st.session_state.get("shortcut", {})
    thermo   = st.session_state.get("thermo", {})

    col_type = st.session_state.get("column_type", None)
    if col_type == "packed":
        st.markdown("""
        <div class="warn-panel">
        ⚠️ <strong>Packed Column selected.</strong>
        This section uses the <b>Fair method for tray columns</b>.
        For your packed column → use <b>📐 Column Diameter (Packed)</b> (GPDC method).
        <i>You can still use this section for reference or comparison.</i>
        </div>
        """, unsafe_allow_html=True)
    elif col_type == "tray":
        st.markdown("""
        <div class="success-panel">
        ✅ <strong>Tray Column selected</strong> — Fair method is correct for your design.
        </div>
        """, unsafe_allow_html=True)

    if not feed or not shortcut:
        st.warning("⚠️ Complete **Feed Specifications** and **Shortcut Design** first.")
        return

    light = feed.get("light", "Benzene")
    heavy = feed.get("heavy", "Toluene")
    x_D   = feed.get("x_D", 0.95)
    F     = feed.get("F", 100.0)
    R     = shortcut.get("R", 2.0)
    D_mol = shortcut.get("D", F * 0.5)

    # Vapour flow in rectifying section: V = (R+1)*D
    V_molar = (R + 1) * D_mol
    dist_props = feed.get("distillate_props") or thermo.get("distillate_props") or binary_mixture_props(light, heavy, x_D)

    tab1, tab2, tab3 = st.tabs(["📐 Diameter Calculation", "📊 Sensitivity Analysis", "📋 Summary"])

    with tab1:
        st.markdown("""
        <div class="formula-box">
          <div class="formula-title">Fair Method — Column Diameter</div>
          u<sub>flood</sub> = C<sub>SB</sub> × √[(ρ<sub>L</sub> − ρ<sub>V</sub>) / ρ<sub>V</sub>]<br>
          u<sub>op</sub> = f × u<sub>flood</sub> &nbsp;|&nbsp;
          A<sub>net</sub> = Q<sub>V</sub> / u<sub>op</sub> &nbsp;|&nbsp;
          D = √(4·A<sub>total</sub>/π)
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### Design Inputs")
        c1, c2, c3 = st.columns(3)
        with c1:
            MW_avg = st.number_input("Average Vapour MW [g/mol]",
                value=float(dist_props.get("MW", round(x_D*COMPONENT_DB[light]["MW"] + (1-x_D)*COMPONENT_DB[heavy]["MW"], 2))),
                min_value=10.0, max_value=500.0, step=0.5)
            rho_L  = st.number_input("Liquid Density ρ_L [kg/m³]",
                value=float(feed.get("rho_L_distillate", dist_props.get("rho_L", 850.0))),
                min_value=400.0, max_value=1500.0, step=5.0)
        with c2:
            T_K    = st.number_input("Operating Temperature [K]",
                value=float(round(thermo.get("T_bubble_D", 80.0) + 273.15, 1)),
                min_value=200.0, max_value=700.0, step=1.0)
            P_bar  = st.number_input("Column Pressure [bar]",
                value=float(feed.get("P_col_bar", 1.013)),
                min_value=0.01, max_value=100.0, step=0.01, format="%.4f")
        with c3:
            tray_spacing   = st.slider("Tray Spacing [m]", 0.30, 0.90, 0.60, 0.05)
            flood_fraction = st.slider("Flooding Fraction f", 0.60, 0.90, 0.80, 0.01)

        st.markdown(f"""
        <div class="info-panel">
        📌 Vapour flow V = (R+1)×D = ({R:.3f}+1) × {D_mol:.2f} = <strong>{V_molar:.2f} kmol/h</strong>
        </div>
        """, unsafe_allow_html=True)

        # Calculate
        result = column_diameter_tray(V_molar, MW_avg, rho_L, None, T_K, P_bar, tray_spacing, flood_fraction)

        st.markdown(f"""
        <div class="formula-box" style="border-left-color:#22c55e !important;">
          <div class="formula-title">Step-by-step diameter calculation</div>
          <b>1. Vapour density:</b>
          Ï<sub>V</sub> = {result['rho_V_kg_m3']:.4f} kg/mÂ³ from ideal-gas estimate at T = {T_K:.1f} K and P = {P_bar:.4f} bar<br>
          <b>2. Flooding velocity:</b>
          u<sub>flood</sub> = C<sub>SB</sub> Ã— âˆš[(Ï<sub>L</sub>âˆ’Ï<sub>V</sub>)/Ï<sub>V</sub>]
          = {result['C_SB']:.5f} Ã— âˆš[({rho_L:.1f}âˆ’{result['rho_V_kg_m3']:.4f})/{result['rho_V_kg_m3']:.4f}]
          = <b>{result['u_flood_m_s']:.4f} m/s</b><br>
          <b>3. Operating velocity:</b>
          u<sub>op</sub> = f Ã— u<sub>flood</sub> = {flood_fraction:.2f} Ã— {result['u_flood_m_s']:.4f}
          = <b>{result['u_operating_m_s']:.4f} m/s</b><br>
          <b>4. Area and diameter:</b>
          A<sub>net</sub> = Q<sub>V</sub>/u<sub>op</sub> = <b>{result['A_net_m2']:.4f} mÂ²</b>,
          A<sub>total</sub> = <b>{result['A_total_m2']:.4f} mÂ²</b>,
          D = âˆš(4A/Ï€) = <b>{result['D_column_m']:.4f} m</b> â†’ standard <b>{result['D_column_std_m']:.2f} m</b>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### Results")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Column Diameter (calc)", f"{result['D_column_m']:.3f} m")
        c2.metric("Column Diameter (std)", f"{result['D_column_std_m']:.2f} m",
                   delta=f"+{round(result['D_column_std_m']-result['D_column_m'],3)} m (rounding)")
        c3.metric("Flooding Velocity u_flood", f"{result['u_flood_m_s']:.3f} m/s")
        c4.metric("Operating Velocity u_op", f"{result['u_operating_m_s']:.3f} m/s")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Net Area A_net", f"{result['A_net_m2']:.3f} m²")
        c2.metric("Total Area A_total", f"{result['A_total_m2']:.3f} m²")
        c3.metric("Vapour Density ρ_V", f"{result['rho_V_kg_m3']:.3f} kg/m³")
        c4.metric("C_SB coefficient", f"{result['C_SB']:.5f} m/s")

        # Visualize column cross-section
        D = result['D_column_std_m']
        fig_cs = go.Figure()
        theta = np.linspace(0, 2*np.pi, 200)
        fig_cs.add_trace(go.Scatter(x=np.cos(theta)*D/2, y=np.sin(theta)*D/2,
                                     mode="lines", line=dict(color="#00b4d8", width=3),
                                     name=f"Column wall (D={D} m)"))
        # Net area (excluding downcomer ~12%)
        A_frac = result['A_net_m2'] / result['A_total_m2']
        r_net = D/2 * np.sqrt(A_frac)
        fig_cs.add_trace(go.Scatter(x=np.cos(theta)*r_net, y=np.sin(theta)*r_net,
                                     mode="lines", line=dict(color="#22c55e", width=3, dash="dot"),
                                     name=f"Net area (A_net={result['A_net_m2']:.2f} m²)"))
        fig_cs.add_annotation(x=0, y=0, text=f"D = {D} m<br>A_net = {result['A_net_m2']:.2f} m²",
                               font=dict(size=14, color="#f8fbff"), showarrow=False)
        fig_cs.update_layout(template="plotly_dark", paper_bgcolor="#0a0e14", plot_bgcolor="#111827",
                              font=dict(family="Barlow", color="#e2e8f0"),
                              xaxis=dict(scaleanchor="y", gridcolor="#1e3a5f", title="m"),
                              yaxis=dict(gridcolor="#1e3a5f", title="m"),
                              height=380, margin=dict(t=20),
                              title=dict(text="Column Cross-Section", font=dict(color="#f8d477", size=20)))
        st.plotly_chart(fig_cs, use_container_width=True)

    with tab2:
        st.markdown("### 📊 Diameter vs Flooding Fraction")
        ff_range = np.linspace(0.55, 0.90, 40)
        D_range  = []
        for ff in ff_range:
            r = column_diameter_tray(V_molar, MW_avg, rho_L, None, T_K, P_bar, tray_spacing, ff)
            D_range.append(r["D_column_std_m"])

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=ff_range, y=D_range, mode="lines+markers",
                                   line=dict(color="#00b4d8", width=3.2),
                                   marker=dict(size=6, color="#f59e0b", line=dict(color="#f8fbff", width=1)),
                                   name="Column Diameter"))
        fig2.add_vline(x=flood_fraction, line_dash="dot", line_color="#f59e0b", line_width=3,
                        annotation_text=f"f = {flood_fraction}")
        fig2.update_layout(template="plotly_dark", paper_bgcolor="#0a0e14", plot_bgcolor="#111827",
                            font=dict(family="Barlow", color="#e2e8f0"),
                            xaxis=dict(title="Flooding Fraction f", gridcolor="#1e3a5f"),
                            yaxis=dict(title="Column Diameter [m]", gridcolor="#1e3a5f"),
                            height=380, margin=dict(t=20))
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        st.markdown("### 📋 Diameter Calculation Summary")
        df = pd.DataFrame({
            "Parameter": ["Vapour Flow V", "MW avg", "ρ_L", "ρ_V",
                           "Tray Spacing", "Flooding Fraction", "C_SB",
                           "u_flood", "u_op", "A_net", "A_total",
                           "D (calculated)", "D (standard)"],
            "Value": [f"{V_molar:.2f}", f"{MW_avg:.2f}", f"{rho_L:.1f}",
                       f"{result['rho_V_kg_m3']:.4f}",
                       f"{tray_spacing:.2f}", f"{flood_fraction:.2f}", f"{result['C_SB']:.5f}",
                       f"{result['u_flood_m_s']:.4f}", f"{result['u_operating_m_s']:.4f}",
                       f"{result['A_net_m2']:.4f}", f"{result['A_total_m2']:.4f}",
                       f"{result['D_column_m']:.4f}", f"{result['D_column_std_m']:.3f}"],
            "Unit": ["kmol/h", "g/mol", "kg/m³", "kg/m³",
                      "m", "—", "m/s", "m/s", "m/s",
                      "m²", "m²", "m", "m"]
        })
        st.dataframe(df, use_container_width=True, hide_index=True)

    # ── Save ──────────────────────────────────────────────────
    st.markdown("<div class='eng-divider'></div>", unsafe_allow_html=True)
    if st.button("💾 Save Diameter Results", type="primary"):
        st.session_state.diameter = {
            "D_column_m": result["D_column_m"],
            "D_column_std_m": result["D_column_std_m"],
            "u_flood_m_s": result["u_flood_m_s"],
            "u_flood_ms": result["u_flood_m_s"],
            "u_op_m_s": result["u_operating_m_s"],
            "u_op_ms": result["u_operating_m_s"],
            "A_net_m2": result["A_net_m2"],
            "A_total_m2": result["A_total_m2"],
            "rho_V": result["rho_V_kg_m3"],
            "rho_L": rho_L,
            "tray_spacing": tray_spacing,
            "flood_fraction": flood_fraction,
            "V_molar": V_molar,
            "MW_avg": MW_avg,
        }
        st.success(f"✅ Diameter saved: D = {result['D_column_std_m']} m. Proceed to **Column Height**.")
