"""sections/pressure_drop.py — Column Pressure Drop Analysis"""
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sections.phase3_style import render_phase3_style


def render():
    st.markdown("""
    <div class="section-header">
        <h1>📉 Pressure Drop Analysis</h1>
        <p>Complete column pressure profile — per tray / per metre packing, total column ΔP,
           pressure at each stage, vacuum/atmospheric feasibility check.</p>
    </div>
    """, unsafe_allow_html=True)

    render_phase3_style()

    feed      = st.session_state.get("feed", {})
    shortcut  = st.session_state.get("shortcut", {})
    diameter  = st.session_state.get("diameter", {})
    height    = st.session_state.get("height", {})
    tray_d    = st.session_state.get("tray_design", {})
    pack_d    = st.session_state.get("packing_design", {})
    col_type  = st.session_state.get("column_type", None)

    if not feed or not shortcut:
        st.warning("⚠️ Complete Feed Specifications and Shortcut Design first.")
        return

    P_top_mmHg = feed.get("P_col_mmHg", 760.0)
    P_top_bar  = feed.get("P_col_bar", 1.013)
    N_theor    = shortcut.get("N_actual_int", 15)
    R          = shortcut.get("R", 2.0)
    D_f        = shortcut.get("D", 50.0)
    rho_L      = diameter.get("rho_L", 850.0)
    rho_V      = diameter.get("rho_V", 3.0)
    D_col      = diameter.get("D_column_std_m", 1.2)

    # ── Tabs ──────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs([
        "📉 Tray Column ΔP" if col_type != "packed" else "📉 Packed Column ΔP",
        "📊 Pressure Profile",
        "📋 Summary"
    ])

    # ═══════════════════════════════════════════════════
    # TAB 1 — ΔP Calculation
    # ═══════════════════════════════════════════════════
    with tab1:

        if col_type == "packed":
            # ── PACKED COLUMN ──────────────────────────────────
            st.markdown("""
            <div class="formula-box">
                <div class="formula-title">Packed Column Pressure Drop — Leva / GPDC Correlation</div>
                ΔP/Z = C₁ × Fₚ × ρᵥ × u²_op / ρ_L &nbsp;&nbsp; [Pa/m]<br>
                ΔP_total = ΔP/Z × Z_packed &nbsp;&nbsp; [Pa]<br>
                Typical design target: <b>&lt; 42 Pa/m</b> for atmospheric,
                <b>&lt; 8 Pa/m</b> for vacuum service
            </div>
            """, unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            with c1:
                Fp     = st.number_input("Packing factor Fₚ [m⁻¹]",
                    value=float(pack_d.get("Fp", 33)), min_value=5.0, max_value=600.0, step=1.0,
                    help="From packing datasheet: Mellapak 250Y=33, Pall 25mm=157")
                Z_pack = st.number_input("Packed bed height Z [m]",
                    value=float(height.get("H_packed_total_m", N_theor * 0.35)),
                    min_value=0.5, max_value=50.0, step=0.1)
            with c2:
                u_op   = st.number_input("Operating velocity u_op [m/s]",
                    value=float(diameter.get("u_op_m_s", 1.5)),
                    min_value=0.1, max_value=10.0, step=0.05, format="%.3f")
                packing_sel = pack_d.get("packing", "")
                is_structured = any(x in packing_sel for x in ["Mellapak", "Flexipac"])
                C1_default = 120.0 if is_structured else 200.0
                C1     = st.number_input("Correlation constant C₁",
                    value=C1_default, min_value=50.0, max_value=500.0, step=10.0,
                    help="Leva correlation: ~200 for random packing, ~120 for structured packing (auto-set)")
            with c3:
                rho_V_in = st.number_input("Vapour density ρᵥ [kg/m³]",
                    value=float(rho_V), min_value=0.01, max_value=50.0, step=0.01, format="%.4f")
                rho_L_in = st.number_input("Liquid density ρ_L [kg/m³]",
                    value=float(rho_L), min_value=100.0, max_value=1500.0, step=5.0)

            dP_per_m   = C1 * Fp * rho_V_in * u_op**2 / rho_L_in
            dP_total   = dP_per_m * Z_pack
            dP_total_mmHg = dP_total / 133.322
            dP_total_bar  = dP_total / 1e5
            P_bot_bar     = P_top_bar + dP_total_bar
            P_bot_mmHg    = P_top_mmHg + dP_total_mmHg

            st.markdown(f"""
            <div class="formula-box" style="border-left:4px solid #f59e0b;">
                <div class="formula-title">✏️ Calculation — Step by Step</div>
                ΔP/Z = {C1} × {Fp} × {rho_V_in:.4f} × {u_op:.3f}² / {rho_L_in}<br>
                &nbsp;&nbsp; = {C1} × {Fp} × {rho_V_in:.4f} × {u_op**2:.4f} / {rho_L_in}<br>
                &nbsp;&nbsp; = <b>{dP_per_m:.2f} Pa/m</b><br><br>
                ΔP_total = {dP_per_m:.2f} × {Z_pack} = <b>{dP_total:.1f} Pa
                ({dP_total_mmHg:.2f} mmHg | {dP_total_bar*1000:.2f} mbar)</b><br><br>
                P_bottom = P_top + ΔP = {P_top_bar:.4f} + {dP_total_bar:.5f}
                = <b>{P_bot_bar:.4f} bar ({P_bot_mmHg:.1f} mmHg)</b>
            </div>
            """, unsafe_allow_html=True)

            # Design check
            limit = 8.0 if P_top_mmHg < 200 else 42.0
            service = "vacuum" if P_top_mmHg < 200 else "atmospheric"
            ok = dP_per_m <= limit
            st.markdown(f"""
            <div class="{'success-panel' if ok else 'warn-panel'}">
            {'✅' if ok else '⚠️'} ΔP/m = <b>{dP_per_m:.2f} Pa/m</b>
            {'≤' if ok else '>'} {limit} Pa/m limit for {service} service.
            {'Design OK.' if ok else 'Consider reducing operating velocity or using lower-Fp structured packing.'}
            </div>
            """, unsafe_allow_html=True)

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("ΔP / metre",   f"{dP_per_m:.2f} Pa/m")
            c2.metric("Total ΔP",     f"{dP_total:.1f} Pa")
            c3.metric("Total ΔP",     f"{dP_total_mmHg:.2f} mmHg")
            c4.metric("P_bottom",     f"{P_bot_bar:.4f} bar")

            # Sensitivity
            u_range  = np.linspace(0.3, min(u_op * 1.8, 5.0), 60)
            dP_range = C1 * Fp * rho_V_in * u_range**2 / rho_L_in * Z_pack

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=u_range, y=dP_range, mode="lines",
                                      line=dict(color="#f59e0b", width=3.2), name="Total ΔP"))
            fig.add_vline(x=u_op, line_dash="dot", line_color="#00b4d8", line_width=3,
                           annotation_text=f"u_op={u_op:.2f} m/s")
            fig.add_hline(y=limit * Z_pack, line_dash="dot", line_color="#ef4444", line_width=3,
                           annotation_text=f"Limit {limit} Pa/m × Z")
            fig.update_layout(
                template="plotly_dark", paper_bgcolor="#0a0e14", plot_bgcolor="#111827",
                font=dict(family="Barlow", color="#e2e8f0"),
                title=dict(text="Packed Column Pressure Drop Sensitivity",
                           font=dict(color="#f8d477", size=19)),
                xaxis=dict(title="Operating velocity u_op [m/s]", gridcolor="#1e3a5f"),
                yaxis=dict(title="Total ΔP [Pa]", gridcolor="#1e3a5f"),
                height=340, margin=dict(t=48))
            st.plotly_chart(fig, use_container_width=True)

            # Store for tab2
            dP_stage  = dP_per_m * (Z_pack / N_theor)   # Pa per theoretical stage
            N_stages  = N_theor
            mode      = "packed"

        else:
            # ── TRAY COLUMN ─────────────────────────────────────
            st.markdown("""
            <div class="formula-box">
                <div class="formula-title">Tray Column Pressure Drop — Francis Weir + Dry Tray</div>
                h_dry  = 51 × (u_h)² × ρᵥ / ρ_L &nbsp;&nbsp; [mm liquid]<br>
                h_weir = h_w + 0.666 × (Q_L / l_w)^(2/3) &nbsp;&nbsp; [mm liquid] — Francis weir<br>
                ΔP_tray = (h_dry + h_weir) × ρ_L × g / 1000 &nbsp;&nbsp; [Pa/tray]<br>
                ΔP_column = N_actual_trays × ΔP_tray
            </div>
            """, unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            with c1:
                tray_spacing = st.number_input("Tray spacing [m]",
                    value=float(tray_d.get("tray_spacing", 0.6)),
                    min_value=0.15, max_value=1.2, step=0.05)
                weir_h_mm  = st.number_input("Weir height [mm]",
                    value=float(tray_d.get("weir_height_mm", 50)),
                    min_value=10.0, max_value=150.0, step=5.0)
                hole_dia_mm = st.number_input("Hole diameter [mm]",
                    value=float(tray_d.get("hole_dia_mm", 5)),
                    min_value=2.0, max_value=25.0, step=0.5)
            with c2:
                tray_eff   = st.slider("Tray efficiency E_o", 0.40, 0.90,
                    float(tray_d.get("tray_efficiency", 0.70)), 0.01)
                N_actual_trays = st.number_input("N actual trays",
                    value=int(np.ceil(N_theor / tray_eff)),
                    min_value=1, max_value=200, step=1)
                dc_frac = st.number_input("Downcomer fraction",
                    value=0.12, min_value=0.05, max_value=0.25, step=0.01)
            with c3:
                rho_V_in = st.number_input("ρᵥ [kg/m³]",
                    value=float(rho_V), min_value=0.01, max_value=50.0,
                    step=0.01, format="%.4f")
                rho_L_in = st.number_input("ρ_L [kg/m³]",
                    value=float(rho_L), min_value=100.0, max_value=1500.0, step=5.0)
                V_mol = (R + 1) * D_f
                MW_avg = diameter.get("MW_avg", 80.0)
                V_m3_s = (V_mol * MW_avg / 1000) / (rho_V_in * 3600)

            # Geometry
            A_total  = np.pi * D_col**2 / 4
            A_net    = A_total * (1 - dc_frac)
            A_active = A_total * (1 - 2 * dc_frac)
            A_holes  = A_active * 0.12
            u_h      = V_m3_s / A_holes      # hole velocity
            u_op_tray= V_m3_s / A_net

            # ΔP components
            h_dry   = 51 * u_h**2 * rho_V_in / rho_L_in       # mm liquid
            l_w     = 0.73 * D_col                              # weir length approx
            Q_L     = V_mol * 0.05 / 3600                       # approx liquid flow m³/s
            h_weir  = weir_h_mm + 750 * (Q_L / l_w)**(2/3)     # mm liquid
            h_total_mm = h_dry + h_weir
            dP_tray = h_total_mm * rho_L_in * 9.81 / 1000      # Pa per tray
            dP_col  = N_actual_trays * dP_tray
            dP_col_mmHg = dP_col / 133.322
            dP_col_bar  = dP_col / 1e5
            P_bot_bar   = P_top_bar + dP_col_bar
            P_bot_mmHg  = P_top_mmHg + dP_col_mmHg

            st.markdown(f"""
            <div class="formula-box" style="border-left:4px solid #00b4d8;">
                <div class="formula-title">✏️ Calculation — Step by Step</div>
                u_hole = V_vol / A_holes = {V_m3_s:.5f} / {A_holes:.5f}
                = <b>{u_h:.3f} m/s</b><br>
                h_dry = 51 × {u_h:.3f}² × {rho_V_in:.3f} / {rho_L_in}
                = <b>{h_dry:.2f} mm liquid</b><br>
                h_weir (Francis) = {weir_h_mm:.0f} + 750 × ({Q_L:.5f}/{l_w:.3f})^(2/3)
                = <b>{h_weir:.2f} mm liquid</b><br>
                h_total = {h_dry:.2f} + {h_weir:.2f} = <b>{h_total_mm:.2f} mm liquid</b><br><br>
                ΔP_tray = {h_total_mm:.2f} × {rho_L_in} × 9.81 / 1000
                = <b>{dP_tray:.1f} Pa/tray</b><br>
                ΔP_column = {N_actual_trays} × {dP_tray:.1f}
                = <b>{dP_col:.0f} Pa ({dP_col_mmHg:.1f} mmHg | {dP_col_bar*1000:.1f} mbar)</b><br>
                P_bottom = {P_top_bar:.4f} + {dP_col_bar:.5f}
                = <b>{P_bot_bar:.4f} bar ({P_bot_mmHg:.1f} mmHg)</b>
            </div>
            """, unsafe_allow_html=True)

            # Design checks
            ok_dp   = dP_tray <= 1000
            ok_back = h_weir <= 0.5 * tray_spacing * 1000
            ok_weep = u_h >= 5.0

            for label, val, unit, ok, note in [
                ("ΔP per tray",   dP_tray,    "Pa",      ok_dp,   "< 1000 Pa recommended"),
                ("Downcomer backup h_weir", h_weir, "mm liq", ok_back, f"< 50% tray spacing ({tray_spacing*500:.0f} mm)"),
                ("Hole velocity u_h",       u_h,    "m/s",   ok_weep, "> 5 m/s to avoid weeping"),
            ]:
                color = "#22c55e" if ok else "#f59e0b"
                icon  = "✅" if ok else "⚠️"
                st.markdown(f"""
                <div class="phase3-check-row" style="border-color:{color}88;">
                  <span class="phase3-check-label">{icon} {label}</span>
                  <span class="phase3-check-value" style="color:{color};">{val:.2f} {unit} — {note}</span>
                </div>""", unsafe_allow_html=True)

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("ΔP / tray",    f"{dP_tray:.1f} Pa")
            c2.metric("Total ΔP",     f"{dP_col:.0f} Pa")
            c3.metric("Total ΔP",     f"{dP_col_mmHg:.1f} mmHg")
            c4.metric("P_bottom",     f"{P_bot_bar:.4f} bar")

            dP_stage  = dP_tray
            N_stages  = N_actual_trays
            mode      = "tray"

    # ═══════════════════════════════════════════════════
    # TAB 2 — Pressure Profile along column
    # ═══════════════════════════════════════════════════
    with tab2:
        st.markdown("### 📊 Pressure Profile Along Column Height")

        try:
            stages = np.arange(0, N_stages + 1)
            P_bar_arr    = [P_top_bar + i * (dP_stage / 1e5) for i in stages]
            P_mmHg_arr   = [P_top_mmHg + i * (dP_stage / 133.322) for i in stages]
            P_kPa_arr    = [p * 100 for p in P_bar_arr]

            if mode == "tray":
                y_labels = [f"Tray {i}" for i in stages]
                y_label  = "Tray number (top=0)"
            else:
                H_per_stage = height.get("H_per_bed_m", Z_pack / N_stages)
                y_labels = [f"z={i*H_per_stage:.1f}m" for i in stages]
                y_label  = "Height from top [m]"

            fig = make_subplots(rows=1, cols=2,
                                subplot_titles=["Pressure [bar]", "Pressure [mmHg]"])
            fig.add_trace(go.Scatter(
                x=P_bar_arr, y=stages, mode="lines+markers",
                line=dict(color="#00b4d8", width=3.2),
                marker=dict(size=6, color="#00d4ff", line=dict(color="#f8fbff", width=1)), name="P [bar]"), row=1, col=1)
            fig.add_trace(go.Scatter(
                x=P_mmHg_arr, y=stages, mode="lines+markers",
                line=dict(color="#f59e0b", width=3.2),
                marker=dict(size=6, color="#f59e0b", line=dict(color="#f8fbff", width=1)), name="P [mmHg]"), row=1, col=2)

            fig.update_yaxes(autorange="reversed", title_text=y_label,
                              gridcolor="#1e3a5f")
            fig.update_xaxes(gridcolor="#1e3a5f")
            fig.update_layout(
                template="plotly_dark", paper_bgcolor="#0a0e14",
                plot_bgcolor="#111827",
                font=dict(family="Barlow", color="#e2e8f0"),
                title=dict(text="Column Pressure Profile", font=dict(color="#f8d477", size=20)),
                height=470, margin=dict(t=58), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

            # Table
            df = pd.DataFrame({
                "Stage/Position": y_labels,
                "P [bar]":   [f"{p:.5f}" for p in P_bar_arr],
                "P [mmHg]":  [f"{p:.2f}" for p in P_mmHg_arr],
                "P [kPa]":   [f"{p:.3f}" for p in P_kPa_arr],
                "ΔP from top [Pa]": [f"{i*dP_stage:.1f}" for i in stages],
            })
            with st.expander("📋 Full pressure table"):
                st.dataframe(df, use_container_width=True, hide_index=True)

        except Exception as e:
            st.error(f"Profile error: {e}")

    # ═══════════════════════════════════════════════════
    # TAB 3 — Summary
    # ═══════════════════════════════════════════════════
    with tab3:
        st.markdown("### 📋 Pressure Drop Summary")
        try:
            summary_rows = {
                "Column type":            col_type or "not selected",
                "Top pressure P_top":     f"{P_top_bar:.4f} bar ({P_top_mmHg:.1f} mmHg)",
                "Service":                "Vacuum (<0.1 bar)" if P_top_bar < 0.1 else "Atmospheric/elevated",
            }
            if mode == "packed":
                summary_rows.update({
                    "Packing factor Fₚ":      f"{Fp} m⁻¹",
                    "Packed bed height Z":     f"{Z_pack:.2f} m",
                    "Operating velocity":      f"{u_op:.3f} m/s",
                    "ΔP per metre":            f"{dP_per_m:.2f} Pa/m",
                    "Total column ΔP":         f"{dP_total:.1f} Pa  |  {dP_total_mmHg:.2f} mmHg",
                    "P_bottom":                f"{P_bot_bar:.4f} bar ({P_bot_mmHg:.1f} mmHg)",
                    "Design check (Pa/m)":     f"{'PASS ✅' if dP_per_m<=limit else 'FAIL ⚠️'} (limit {limit} Pa/m)",
                })
            else:
                summary_rows.update({
                    "N actual trays":          f"{N_actual_trays}",
                    "Tray spacing":            f"{tray_spacing} m",
                    "Weir height":             f"{weir_h_mm:.0f} mm",
                    "Hole velocity u_h":       f"{u_h:.3f} m/s",
                    "h_dry":                   f"{h_dry:.2f} mm liquid",
                    "h_weir (Francis)":        f"{h_weir:.2f} mm liquid",
                    "ΔP per tray":             f"{dP_tray:.1f} Pa",
                    "Total column ΔP":         f"{dP_col:.0f} Pa  |  {dP_col_mmHg:.1f} mmHg",
                    "P_bottom":                f"{P_bot_bar:.4f} bar ({P_bot_mmHg:.1f} mmHg)",
                    "Weeping check":           f"{'OK ✅' if ok_weep else 'RISK ⚠️'}",
                    "Downcomer backup":        f"{'OK ✅' if ok_back else 'HIGH ⚠️'}",
                })
            df2 = pd.DataFrame({"Parameter": list(summary_rows.keys()),
                                 "Value": list(summary_rows.values())})
            st.dataframe(df2, use_container_width=True, hide_index=True)
        except:
            st.info("Complete the calculation in Tab 1 first.")

    # ── Save ──────────────────────────────────────────────────────────
    st.markdown("<div class='eng-divider'></div>", unsafe_allow_html=True)
    if st.button("💾 Save Pressure Drop Results", type="primary"):
        try:
            st.session_state["pressure_drop"] = {
                "col_type":      col_type,
                "P_top_bar":     P_top_bar,
                "P_top_mmHg":    P_top_mmHg,
                "dP_stage_Pa":   dP_stage,
                "dP_total_Pa":   dP_stage * N_stages,
                "dP_total_mmHg": dP_stage * N_stages / 133.322,
                "P_bot_bar":     P_top_bar + dP_stage * N_stages / 1e5,
                "N_stages":      N_stages,
            }
            st.success("✅ Pressure drop results saved!")
        except Exception as e:
            st.error(f"Save error: {e}")
