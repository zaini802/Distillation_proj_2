"""pages/energy_economics.py — Energy Optimization & Economics"""
import streamlit as st
import numpy as np
import plotly.graph_objects as go

import pandas as pd
from sections.phase3_style import render_phase3_style


def render():
    st.markdown("""
    <div class="section-header">
        <h1>💰 Energy & Economics</h1>
        <p>Steam/cooling water consumption, heat integration, CAPEX/OPEX estimation, and payback analysis.</p>
    </div>
    """, unsafe_allow_html=True)

    render_phase3_style()

    feed      = st.session_state.get("feed", {})
    shortcut  = st.session_state.get("shortcut", {})
    diameter  = st.session_state.get("diameter", {})
    height    = st.session_state.get("height", {})
    reboiler  = st.session_state.get("reboiler", {})
    condenser = st.session_state.get("condenser", {})
    mechanical= st.session_state.get("mechanical", {})

    D_col   = diameter.get("D_column_std_m", 1.2)
    H_total = height.get("total_height_m", 15.0)
    Q_reb   = reboiler.get("Q_reb_kW", 500.0)
    Q_cond  = condenser.get("Q_cond_kW", 450.0)
    F       = feed.get("F", 100.0)
    N_act   = shortcut.get("N_actual_int", 20)

    tab1, tab2, tab3, tab4 = st.tabs([
        "⚡ Energy Analysis", "💵 CAPEX Estimation", "📊 OPEX & Utilities", "📈 Payback Analysis"
    ])

    # ── TAB 1: Energy Analysis ────────────────────────────────
    with tab1:
        st.markdown("### Energy Consumption Analysis")
        st.markdown("""
        <div class="formula-box">
          <div class="formula-title">Steam & Cooling Water Requirements (Perry's Handbook)</div>
          Steam Rate = Q_reb / λ_steam [kg/h]<br>
          Cooling Water Rate = Q_cond / (Cp_w × ΔT_w) [kg/h]<br>
          Specific Energy = (Q_reb + Q_cond) / F_feed [kJ/kmol]
        </div>""", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Reboiler (Steam Side)")
            steam_pressure_bar = st.selectbox("Steam Grade", [
                "Low Pressure Steam (3.5 bar, 138°C, λ=2148 kJ/kg)",
                "Medium Pressure Steam (10 bar, 180°C, λ=2000 kJ/kg)",
                "High Pressure Steam (30 bar, 234°C, λ=1795 kJ/kg)",
            ])
            lambda_vals = {"Low": 2148, "Medium": 2000, "High": 1795}
            steam_key = steam_pressure_bar.split()[0]
            lambda_steam = lambda_vals.get(steam_key, 2000)
            Q_reb_input = st.number_input("Reboiler Duty Q_reb [kW]", value=float(max(Q_reb, 100)), min_value=10.0, step=10.0)

        with c2:
            st.markdown("#### Condenser (Cooling Water Side)")
            delta_T_cw = st.number_input("Cooling Water ΔT [°C]", value=10.0, min_value=5.0, max_value=20.0, step=1.0)
            Cp_water   = 4.18  # kJ/(kg·°C)
            Q_cond_input = st.number_input("Condenser Duty Q_cond [kW]", value=float(max(Q_cond, 100)), min_value=10.0, step=10.0)

        # Calculations
        Q_reb_kJh   = Q_reb_input * 3600
        Q_cond_kJh  = Q_cond_input * 3600
        steam_rate  = Q_reb_kJh / lambda_steam          # kg/h
        cw_rate     = Q_cond_kJh / (Cp_water * delta_T_cw) / 1000  # t/h
        total_energy_kW = Q_reb_input + Q_cond_input
        spec_energy = (total_energy_kW * 3600) / (F * 1000) if F > 0 else 0  # kJ/kmol approx
        pinch_potential = min(Q_reb_input, Q_cond_input) * 0.20
        steam_savings_kg_h = pinch_potential * 3600 / lambda_steam

        st.markdown(f"""
        <div class="formula-box" style="border-left:4px solid #f59e0b;">
          <div class="formula-title">Step-by-step utility calculation</div>
          <b>1. Steam rate:</b>
          ṁ<sub>steam</sub> = Q<sub>reb</sub>/λ<sub>steam</sub>
          = {Q_reb_input:.1f}×3600/{lambda_steam:.0f}
          = <b>{steam_rate:,.0f} kg/h</b><br>
          <b>2. Cooling water:</b>
          ṁ<sub>CW</sub> = Q<sub>cond</sub>/(C<sub>p,w</sub>ΔT)
          = {Q_cond_input:.1f}×3600/(4.18×{delta_T_cw:.1f})
          = <b>{cw_rate:.1f} t/h</b><br>
          <div class="phase3-calc-separator"></div>
          <b>3. Specific energy:</b>
          (Q<sub>reb</sub>+Q<sub>cond</sub>)/F = {total_energy_kW:.1f}×3600/({F:.1f}×1000)
          = <b>{spec_energy:,.0f} kJ/kmol</b><br>
          <b>4. Heat integration potential:</b>
          20% × min(Q<sub>reb</sub>, Q<sub>cond</sub>) = <b>{pinch_potential:,.0f} kW</b>,
          possible steam saving ≈ <b>{steam_savings_kg_h:,.0f} kg/h</b>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Steam Rate [kg/h]", f"{steam_rate:,.0f}")
        c2.metric("Cooling Water [t/h]", f"{cw_rate:.1f}")
        c3.metric("Total Energy [kW]", f"{total_energy_kW:,.0f}")
        c4.metric("Spec. Energy [kJ/kmol]", f"{spec_energy:,.0f}")

        # Energy Sankey-style bar
        fig_energy = go.Figure(go.Bar(
            x=["Reboiler Duty\n(Q_reb)", "Condenser Duty\n(Q_cond)", "Total Column\nEnergy"],
            y=[Q_reb_input, Q_cond_input, total_energy_kW],
            marker_color=["#f59e0b", "#00b4d8", "#22c55e"],
            text=[f"{v:,.0f} kW" for v in [Q_reb_input, Q_cond_input, total_energy_kW]],
            textposition="outside"
        ))
        fig_energy.update_layout(
            title=dict(text="Energy Distribution", font=dict(color="#f8d477", size=19)),
            paper_bgcolor="#0d1520", plot_bgcolor="#0d1520",
            font_color="#e2e8f0", yaxis_title="Energy [kW]", height=350
        )
        st.plotly_chart(fig_energy, use_container_width=True)

        # Heat integration potential
        st.markdown("#### Heat Integration Opportunities")
        st.info(f"""
        **Pinch Analysis (Rule of Thumb):**
        - Estimated heat integration potential: **{pinch_potential:,.0f} kW** (~20% of smaller duty)
        - Recommended: Feed-Effluent Heat Exchanger (FEHE) preheating feed with hot bottoms stream
        - Potential steam savings: **{steam_savings_kg_h:,.0f} kg/h**
        """)

    # ── TAB 2: CAPEX Estimation ───────────────────────────────
    with tab2:
        st.markdown("### Capital Cost Estimation (Lang Factor Method)")
        st.markdown("""
        <div class="formula-box">
          <div class="formula-title">Lang Factor Method (Towler & Sinnott, Chem Eng Design)</div>
          Total Installed Cost (TIC) = f_Lang × Σ(Equipment Cost)<br>
          Lang Factor: 4.74 for fluid processing plants<br>
          Equipment costs indexed to CEPCI base year
        </div>""", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            cepci_base = st.number_input("CEPCI Base Year Index (2001=394)", value=394.0, step=1.0)
            cepci_curr = st.number_input("CEPCI Current Index (~2024=800)", value=800.0, step=1.0)
            lang_factor = st.number_input("Lang Factor", value=4.74, min_value=2.0, max_value=7.0, step=0.01)
            col_mat = st.selectbox("Column Material", ["Carbon Steel", "SS 304", "SS 316L", "Alloy 625"])
        with c2:
            hx_area_reb  = st.number_input("Reboiler Heat Transfer Area [m²]", value=float(reboiler.get("A_reb_m2", 20.0)), min_value=1.0, step=1.0)
            hx_area_cond = st.number_input("Condenser Heat Transfer Area [m²]", value=float(condenser.get("A_cond_m2", 18.0)), min_value=1.0, step=1.0)

        # Cost index correction
        ci = cepci_curr / cepci_base

        # Column shell cost (Coulson & Richardson correlation)
        # C_vessel = a * (W_shell)^b  — simplified mass-based
        V_shell  = np.pi * D_col**2 / 4 * H_total
        rho_steel = 7850  # kg/m³
        t_shell   = 0.01  # assume 10 mm
        W_shell   = rho_steel * np.pi * D_col * H_total * t_shell
        mat_factors = {"Carbon Steel": 1.0, "SS 304": 2.0, "SS 316L": 2.5, "Alloy 625": 6.5}
        f_mat = mat_factors.get(col_mat, 1.0)
        C_column = ci * f_mat * (17640 + 79.4 * W_shell)  # USD

        # Heat exchanger costs (simple Kern correlation)
        C_reboiler  = ci * 1.35 * (10000 + 500 * hx_area_reb**0.85)
        C_condenser = ci * 1.20 * (10000 + 500 * hx_area_cond**0.85)

        # Internals and misc
        C_internals = C_column * 0.15
        C_instrumentation = C_column * 0.20
        C_piping     = C_column * 0.30
        C_electrical = C_column * 0.10
        C_civil      = C_column * 0.15

        C_equipment_total = C_column + C_reboiler + C_condenser + C_internals
        TIC = lang_factor * C_equipment_total

        costs = {
            "Column Shell": C_column,
            "Reboiler": C_reboiler,
            "Condenser": C_condenser,
            "Column Internals": C_internals,
            "Instrumentation": C_instrumentation,
            "Piping": C_piping,
            "Electrical": C_electrical,
            "Civil/Structural": C_civil,
        }
        cost_df = pd.DataFrame({"Item": costs.keys(), "Cost [USD]": [f"${v:,.0f}" for v in costs.values()]})
        st.dataframe(cost_df, use_container_width=True)

        st.markdown(f"""
        <div class="formula-box" style="border-left:4px solid #00b4d8;">
          <div class="formula-title">CAPEX calculation basis</div>
          <b>Cost index factor:</b> CEPCI ratio = {cepci_curr:.0f}/{cepci_base:.0f} = <b>{ci:.3f}</b><br>
          <b>Column shell cost:</b> material factor {f_mat:.2f}, estimated shell mass {W_shell:,.0f} kg
          → <b>${C_column:,.0f}</b><br>
          <b>Bare equipment cost:</b> column + reboiler + condenser + internals = <b>${C_equipment_total:,.0f}</b><br>
          <b>Total installed cost:</b> Lang factor × bare equipment = {lang_factor:.2f} × ${C_equipment_total:,.0f}
          = <b>${TIC:,.0f}</b>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("Bare Equipment Cost [USD]", f"${C_equipment_total:,.0f}")
        c2.metric("Lang Factor TIC [USD]", f"${TIC:,.0f}")
        c3.metric("TIC in Million USD", f"${TIC/1e6:.2f} M")

        # Pie chart
        fig_pie = go.Figure(go.Pie(
            labels=list(costs.keys()),
            values=list(costs.values()),
            hole=0.4,
            marker_colors=["#0077b6","#00b4d8","#90e0ef","#f59e0b","#22c55e","#ef4444","#a855f7","#64748b"]
        ))
        fig_pie.update_layout(
            title=dict(text="CAPEX Breakdown", font=dict(color="#f8d477", size=19)),
            paper_bgcolor="#0d1520", font_color="#e2e8f0", height=380
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # ── TAB 3: OPEX & Utilities ───────────────────────────────
    with tab3:
        st.markdown("### Operating Cost (OPEX) Estimation")

        c1, c2 = st.columns(2)
        with c1:
            hours_pa  = st.number_input("Operating Hours per Year [h/yr]", value=8000, min_value=1000, max_value=8760, step=100)
            steam_cost = st.number_input("Steam Cost [USD/ton]", value=25.0, min_value=5.0, max_value=100.0, step=1.0)
            cw_cost    = st.number_input("Cooling Water Cost [USD/m³]", value=0.05, min_value=0.01, max_value=0.5, step=0.01)
        with c2:
            elec_cost  = st.number_input("Electricity Cost [USD/kWh]", value=0.08, min_value=0.01, max_value=0.5, step=0.01)
            labor_cost = st.number_input("Labor Cost [USD/yr]", value=150000.0, min_value=10000.0, step=10000.0)
            maint_pct  = st.number_input("Maintenance [% of TIC/yr]", value=3.0, min_value=1.0, max_value=10.0, step=0.5)

        # OPEX calculations
        steam_rate_tyr = steam_rate / 1000 * hours_pa  # ton/yr
        cw_rate_m3yr   = cw_rate * hours_pa             # m³/yr (approx)
        pump_power_kW  = 5.0  # assume 5 kW pumps

        cost_steam   = steam_rate_tyr * steam_cost
        cost_cw      = cw_rate_m3yr * cw_cost
        cost_elec    = pump_power_kW * hours_pa * elec_cost
        cost_labor   = labor_cost
        cost_maint   = TIC * maint_pct / 100
        cost_overhead = (cost_steam + cost_cw + cost_elec + cost_labor) * 0.10

        total_opex = cost_steam + cost_cw + cost_elec + cost_labor + cost_maint + cost_overhead

        opex_items = {
            "Steam": cost_steam,
            "Cooling Water": cost_cw,
            "Electricity": cost_elec,
            "Labor": cost_labor,
            "Maintenance": cost_maint,
            "Overhead (10%)": cost_overhead,
        }

        c1, c2 = st.columns(2)
        with c1:
            for k, v in opex_items.items():
                st.metric(k, f"${v:,.0f}/yr")
        with c2:
            fig_opex = go.Figure(go.Bar(
                x=list(opex_items.keys()),
                y=list(opex_items.values()),
                marker_color=["#f59e0b","#00b4d8","#22c55e","#a855f7","#ef4444","#64748b"],
                text=[f"${v:,.0f}" for v in opex_items.values()],
                textposition="outside"
            ))
            fig_opex.update_layout(
                title=dict(text="Annual OPEX Breakdown [USD/yr]", font=dict(color="#f8d477", size=19)),
                paper_bgcolor="#0d1520", plot_bgcolor="#0d1520",
                font_color="#e2e8f0", height=350, showlegend=False,
                yaxis_title="Cost [USD/yr]"
            )
            st.plotly_chart(fig_opex, use_container_width=True)

        st.metric("**Total Annual OPEX [USD/yr]**", f"${total_opex:,.0f}")

    # ── TAB 4: Payback Analysis ───────────────────────────────
    with tab4:
        st.markdown("### Economic Payback Analysis")

        c1, c2 = st.columns(2)
        with c1:
            annual_revenue = st.number_input("Annual Revenue [USD/yr]", value=float(total_opex * 2.5), min_value=1000.0, step=10000.0)
            discount_rate  = st.number_input("Discount Rate (WACC) [%]", value=10.0, min_value=1.0, max_value=30.0, step=0.5) / 100
            project_life   = st.number_input("Project Life [years]", value=20, min_value=5, max_value=40, step=1)
        with c2:
            working_capital_pct = st.number_input("Working Capital [% of TIC]", value=10.0, min_value=5.0, max_value=30.0, step=1.0) / 100
            contingency_pct     = st.number_input("Contingency [% of TIC]", value=15.0, min_value=5.0, max_value=30.0, step=1.0) / 100

        total_investment = TIC * (1 + working_capital_pct + contingency_pct)
        annual_profit    = annual_revenue - total_opex
        simple_payback   = total_investment / annual_profit if annual_profit > 0 else float('inf')

        # NPV & IRR calculation
        cash_flows = [-total_investment] + [annual_profit] * int(project_life)
        years_arr  = np.arange(0, project_life + 1)
        npv        = sum(cf / (1 + discount_rate)**t for t, cf in enumerate(cash_flows))
        cumulative = np.cumsum(cash_flows)

        # IRR via Newton
        from scipy.optimize import brentq
        try:
            irr = brentq(lambda r: sum(cf / (1 + r)**t for t, cf in enumerate(cash_flows)), 0.001, 5.0)
        except Exception:
            irr = 0.0

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Investment [USD]", f"${total_investment/1e6:.2f}M")
        c2.metric("Simple Payback [yrs]", f"{simple_payback:.1f}" if simple_payback != float('inf') else "N/A")
        c3.metric("NPV [USD]", f"${npv/1e6:.2f}M", delta="Positive ✅" if npv > 0 else "Negative ❌")
        c4.metric("IRR [%]", f"{irr*100:.1f}%" if irr > 0 else "N/A")

        # Cumulative cash flow chart
        fig_cf = go.Figure()
        fig_cf.add_trace(go.Scatter(
            x=years_arr, y=cumulative / 1e6,
            mode='lines+markers', line=dict(color="#22c55e", width=3.2),
            marker=dict(size=6, color="#f59e0b", line=dict(color="#f8fbff", width=1)),
            fill='tozeroy',
            fillcolor='rgba(34,197,94,0.15)',
            name="Cumulative Cash Flow"
        ))
        fig_cf.add_hline(y=0, line_dash="dash", line_color="#ef4444", line_width=3, annotation_text="Break-even")
        fig_cf.update_layout(
            title=dict(text="Cumulative Cash Flow Over Project Life", font=dict(color="#f8d477", size=19)),
            paper_bgcolor="#0d1520", plot_bgcolor="#0d1520",
            font_color="#e2e8f0", height=380,
            xaxis_title="Year", yaxis_title="Cumulative Cash Flow [M USD]"
        )
        st.plotly_chart(fig_cf, use_container_width=True)

        # Save to session
        st.session_state["energy"] = {
            "Q_reb_kW": round(Q_reb_input, 2),
            "Q_cond_kW": round(Q_cond_input, 2),
            "steam_rate_kg_h": round(steam_rate, 1),
            "cw_rate_t_h": round(cw_rate, 2),
            "CAPEX_USD": round(TIC, 0),
            "OPEX_USD_yr": round(total_opex, 0),
            "NPV_USD": round(npv, 0),
            "IRR_pct": round(irr * 100, 2),
            "simple_payback_yrs": round(simple_payback, 2) if simple_payback != float('inf') else None,
        }
        st.success("✅ Energy & economics results saved.")
