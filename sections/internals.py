"""pages/internals.py — Column Internals Design"""
import streamlit as st
import numpy as np
import plotly.graph_objects as go
from sections.phase3_style import render_phase3_style


def render():
    st.markdown("""
    <div class="section-header">
        <h1>🔧 Column Internals</h1>
        <p>Design of liquid distributors, redistributors, mist eliminators, support plates and chimney trays.</p>
    </div>
    """, unsafe_allow_html=True)

    render_phase3_style()

    diameter  = st.session_state.get("diameter", {})
    height    = st.session_state.get("height", {})
    feed      = st.session_state.get("feed", {})
    col_type  = st.session_state.get("column_type", "packed")

    D_col     = diameter.get("D_column_std_m", 1.2)
    H_total   = height.get("total_height_m", 15.0)
    F         = feed.get("F", 100.0)

    tab1, tab2, tab3, tab4 = st.tabs([
        "💧 Liquid Distributor", "♻️ Redistributors", "🌫️ Mist Eliminator", "🏗️ Support Plates"
    ])

    # ── TAB 1: Liquid Distributor ──────────────────────────────
    with tab1:
        st.markdown("### Liquid Distributor Design")
        st.markdown("""
        <div class="formula-box">
          <div class="formula-title">Distributor Design Basis</div>
          Irrigation Density (L_d) = L_vol / A_col &nbsp;[m³/m²·h]<br>
          Orifice Drip Points: n = L_d × A_col / q_orifice<br>
          Drip Point Density: ≥ 40–100 points/m² for good distribution
        </div>""", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            dist_type = st.selectbox("Distributor Type", [
                "Orifice Pan Distributor",
                "Pipe Arm (Header-Lateral) Distributor",
                "Notched Trough Distributor",
                "Spray Nozzle Distributor",
            ])
            L_vol = st.number_input("Liquid Volumetric Flow [m³/h]", value=5.0, min_value=0.1, step=0.5)
            drip_density = st.number_input("Target Drip Point Density [pts/m²]", value=60.0, min_value=20.0, max_value=200.0, step=5.0)

        with c2:
            d_orifice_mm = st.number_input("Orifice Diameter [mm]", value=6.0, min_value=2.0, max_value=20.0, step=0.5)
            h_weir_mm    = st.number_input("Weir Height above Orifice [mm]", value=50.0, min_value=10.0, max_value=200.0, step=5.0)

        A_col = np.pi * D_col**2 / 4
        irrig_density = L_vol / A_col  # m³/m²·h
        n_drip_pts    = int(drip_density * A_col)
        d_orifice_m   = d_orifice_mm / 1000
        A_orifice     = np.pi * d_orifice_m**2 / 4
        Cd            = 0.62
        g             = 9.81
        h_weir        = h_weir_mm / 1000
        q_orifice_m3h = Cd * A_orifice * np.sqrt(2 * g * h_weir) * 3600
        n_orifice_calc = L_vol / q_orifice_m3h if q_orifice_m3h > 0 else 0
        recommended_orifices = max(n_drip_pts, int(np.ceil(n_orifice_calc)))
        drip_density_actual = recommended_orifices / A_col if A_col > 0 else 0

        st.markdown(f"""
        <div class="formula-box" style="border-left:4px solid #22c55e;">
          <div class="formula-title">Step-by-step distributor calculation</div>
          <b>1. Column area:</b>
          A = πD²/4 = π({D_col:.2f})²/4 = <b>{A_col:.3f} m²</b><br>
          <b>2. Irrigation density:</b>
          L<sub>d</sub> = L/A = {L_vol:.2f}/{A_col:.3f} = <b>{irrig_density:.2f} m³/m²·h</b><br>
          <div class="phase3-calc-separator"></div>
          <b>3. Orifice flow:</b>
          q = C<sub>d</sub>A<sub>o</sub>√(2gh) = <b>{q_orifice_m3h:.5f} m³/h per orifice</b><br>
          <b>4. Orifice count:</b>
          N = max(target drip points, flow/orifice) = max({n_drip_pts}, {n_orifice_calc:.1f})
          = <b>{recommended_orifices}</b><br>
          <b>5. Actual drip density:</b>
          {recommended_orifices}/{A_col:.3f} = <b>{drip_density_actual:.1f} points/m²</b>
        </div>
        """, unsafe_allow_html=True)

        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Column Cross-Section [m²]", f"{A_col:.3f}")
        col_b.metric("Irrigation Density [m³/m²·h]", f"{irrig_density:.2f}")
        col_c.metric("Drip Points Required", f"{n_drip_pts}")

        col_d, col_e, col_f = st.columns(3)
        col_d.metric("Flow per Orifice [m³/h]", f"{q_orifice_m3h:.5f}")
        col_e.metric("Orifices by Flow Calc", f"{int(n_orifice_calc)}")
        col_f.metric("Recommended Orifices", f"{recommended_orifices}")

        quality = "✅ Excellent (>80/m²)" if drip_density >= 80 else \
                  "✅ Good (40–80/m²)" if drip_density >= 40 else \
                  "⚠️ Poor (<40/m²) — Risk of maldistribution"
        quality_ok = drip_density_actual >= 40
        st.markdown(f"""
        <div class="{'success-panel' if quality_ok else 'warn-panel'}">
        {'✅' if quality_ok else '⚠️'} <strong>Distribution quality:</strong>
        {quality}. Actual drip density = {drip_density_actual:.1f} points/m².
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="result-box">
          <div class="label">Distributor Type Selected</div>
          <span class="value" style="font-size:1rem">{dist_type}</span>
        </div>""", unsafe_allow_html=True)

    # ── TAB 2: Redistributors ──────────────────────────────────
    with tab2:
        st.markdown("### Liquid Redistributor Design")
        st.markdown("""
        <div class="formula-box">
          <div class="formula-title">Redistribution Guideline (Seader & Henley)</div>
          Bed Height between Redistributors: 3–8 m (random) | 5–10 m (structured)<br>
          Redistributor needed every: 5–6 m of packing height<br>
          Collector tray collects liquid then redistributes uniformly
        </div>""", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            pack_height = st.number_input("Total Packing Height [m]", value=float(H_total * 0.6), min_value=1.0, step=0.5)
            max_bed_height = st.number_input("Max Bed Height before Redistribution [m]", value=5.0, min_value=1.0, max_value=10.0, step=0.5)
        with c2:
            redist_type = st.selectbox("Redistributor Type", [
                "Chimney (Cap) Tray Collector + Orifice Redistributor",
                "Total Draw-Off Collector Tray",
                "Vane-Type Redistributor",
                "Ring-Type Redistributor"
            ])

        n_redist = int(pack_height / max_bed_height)
        beds      = n_redist + 1
        bed_h     = pack_height / beds if beds > 0 else pack_height

        c1, c2, c3 = st.columns(3)
        c1.metric("Number of Redistributors", f"{n_redist}")
        c2.metric("Number of Packing Beds", f"{beds}")
        c3.metric("Height per Bed [m]", f"{bed_h:.2f}")

        # Bed layout chart
        fig = go.Figure()
        y_pos = 0
        colors = ["#0077b6", "#00b4d8"]
        for i in range(beds):
            fig.add_trace(go.Bar(
                x=[bed_h], y=[f"Bed {i+1}"],
                orientation='h',
                marker_color=colors[i % 2],
                name=f"Bed {i+1}",
                text=f"{bed_h:.1f} m",
                textposition='inside'
            ))
            y_pos += bed_h
            if i < beds - 1:
                fig.add_trace(go.Bar(
                    x=[0.3], y=[f"Bed {i+1}"],
                    orientation='h',
                    marker_color="#f59e0b",
                    name="Redistributor",
                    showlegend=(i == 0),
                    text="Redist.",
                    textposition='inside'
                ))

        fig.update_layout(
            title=dict(text="Packing Bed Layout with Redistributors",
                       font=dict(color="#f8d477", size=19)),
            paper_bgcolor="#0d1520", plot_bgcolor="#0d1520",
            font_color="#e2e8f0", barmode='stack',
            height=300,
            xaxis_title="Height [m]"
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── TAB 3: Mist Eliminator ────────────────────────────────
    with tab3:
        st.markdown("### Mist Eliminator / Demister Design")
        st.markdown("""
        <div class="formula-box">
          <div class="formula-title">Souders-Brown Criterion for Demister</div>
          u_max = K_d × √[(ρ_L − ρ_V) / ρ_V]<br>
          K_d = 0.107 m/s (wire mesh, standard)<br>
          Minimum Pad Area = V_vol / u_max
        </div>""", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            mist_type = st.selectbox("Mist Eliminator Type", [
                "Wire Mesh Pad (most common)",
                "Vane-Type Demister",
                "Knitted Mesh + Vane Combo",
                "Cyclonic Separator"
            ])
            rho_L = st.number_input("Liquid Density [kg/m³]", value=750.0, min_value=400.0, max_value=1500.0, step=10.0)
            rho_V = st.number_input("Vapor Density [kg/m³]", value=3.5, min_value=0.5, max_value=50.0, step=0.1)
        with c2:
            V_vol_m3s = st.number_input("Vapor Volumetric Flow [m³/s]", value=0.5, min_value=0.01, max_value=20.0, step=0.05)
            Kd_vals = {"Wire Mesh Pad (most common)": 0.107, "Vane-Type Demister": 0.15,
                       "Knitted Mesh + Vane Combo": 0.12, "Cyclonic Separator": 0.20}
            Kd = Kd_vals.get(mist_type, 0.107)
            st.metric("K_d Factor [m/s]", f"{Kd:.3f}")

        u_max = Kd * np.sqrt((rho_L - rho_V) / rho_V)
        A_min = V_vol_m3s / u_max
        D_min = np.sqrt(4 * A_min / np.pi)

        st.markdown(f"""
        <div class="formula-box" style="border-left:4px solid #f59e0b;">
          <div class="formula-title">Mist eliminator sizing calculation</div>
          u<sub>max</sub> = K<sub>d</sub>√[(ρ<sub>L</sub>−ρ<sub>V</sub>)/ρ<sub>V</sub>]
          = {Kd:.3f}√[({rho_L:.1f}−{rho_V:.1f})/{rho_V:.1f}]
          = <b>{u_max:.3f} m/s</b><br>
          A<sub>min</sub> = V/u<sub>max</sub> = {V_vol_m3s:.3f}/{u_max:.3f}
          = <b>{A_min:.3f} m²</b><br>
          D<sub>min</sub> = √(4A/π) = <b>{D_min:.3f} m</b>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("Max Velocity u_max [m/s]", f"{u_max:.3f}")
        c2.metric("Min Pad Area [m²]", f"{A_min:.3f}")
        c3.metric("Min Pad Diameter [m]", f"{D_min:.3f}")

        if D_col < D_min:
            st.error(f"⚠️ Column diameter ({D_col:.2f} m) < Minimum pad diameter ({D_min:.2f} m). Consider enlarging column.")
        else:
            st.success(f"✅ Column diameter ({D_col:.2f} m) ≥ Minimum pad diameter ({D_min:.2f} m). Mist eliminator fits.")

        pad_thickness = {"Wire Mesh Pad (most common)": "100–150 mm",
                         "Vane-Type Demister": "200–300 mm",
                         "Knitted Mesh + Vane Combo": "200–250 mm",
                         "Cyclonic Separator": "400–600 mm"}
        st.info(f"**Recommended Pad Thickness:** {pad_thickness.get(mist_type, '100–150 mm')}")

    # ── TAB 4: Support Plates ────────────────────────────────
    with tab4:
        st.markdown("### Packing Support Plate & Column Internals Summary")
        st.markdown("""
        <div class="formula-box">
          <div class="formula-title">Support Plate Design (Coulson & Richardson Vol. 2)</div>
          Free Area of Support Plate ≥ 50–70% of column cross-section<br>
          Pressure Drop across Support: ΔP = ρ_L × g × h_liquid<br>
          Material: SS 304/316 grating or perforated plate
        </div>""", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            support_type = st.selectbox("Support Type", [
                "Gas Injection Support Plate (GISP)",
                "Multi-Beam Support Plate",
                "Grid Support Plate",
                "Perforated Plate Support"
            ])
            free_area_pct = st.slider("Free Area [%]", min_value=40, max_value=80, value=60)
        with c2:
            n_support = st.number_input("Number of Support Plates", value=int(max(1, n_redist + 1)), min_value=1, max_value=20)
            mat_support = st.selectbox("Material", ["SS 304", "SS 316L", "Carbon Steel", "Alloy 625"])

        A_support = A_col * free_area_pct / 100
        A_blocked = A_col - A_support
        support_ok = free_area_pct >= 50

        c1, c2, c3 = st.columns(3)
        c1.metric("Total Support Area [m²]", f"{A_col:.3f}")
        c2.metric("Free Flow Area [m²]", f"{A_support:.3f}")
        c3.metric("Number of Supports", f"{int(n_support)}")

        st.markdown(f"""
        <div class="{'success-panel' if support_ok else 'warn-panel'}">
        {'✅' if support_ok else '⚠️'} <strong>Support plate free-area check:</strong>
        Free area = {free_area_pct}% ({A_support:.3f} m²), blocked area = {A_blocked:.3f} m².
        {'Meets the usual 50-70% open-area guideline.' if support_ok else 'Increase free area to reduce support pressure drop.'}
        </div>
        """, unsafe_allow_html=True)

        # Summary card
        st.markdown("---")
        st.markdown("### 📋 Column Internals Summary")
        summary_data = {
            "Internal": ["Liquid Distributor", "Redistributors", "Mist Eliminator", "Support Plates"],
            "Quantity": [1, int(n_redist), 1, int(n_support)],
            "Type": [dist_type.split()[0], redist_type.split()[0], mist_type.split()[0], support_type.split()[0]],
            "Material": [mat_support] * 4
        }
        import pandas as pd
        df = pd.DataFrame(summary_data)
        st.dataframe(df, use_container_width=True)

        st.session_state["internals"] = {
            "n_distributors": 1,
            "n_redistributors": int(n_redist),
            "n_support_plates": int(n_support),
            "mist_eliminator_type": mist_type,
            "drip_density": drip_density,
            "recommended_orifices": recommended_orifices,
            "actual_drip_density": round(drip_density_actual, 1),
            "u_max_ms": round(u_max, 4),
        }
        st.success("✅ Column internals design saved to session state.")
