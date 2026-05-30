"""sections/instrumentation.py — Advanced Instrumentation & Control Design"""
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sections.phase3_style import render_phase3_style


def render():
    st.markdown("""
    <div class="section-header">
        <h1>🎛️ Instrumentation & Control</h1>
        <p>Advanced control loops, safety layer analysis, PSV sizing (API 520), SIL assessment, P&ID schematic, and full instrument index.</p>
    </div>
    """, unsafe_allow_html=True)

    render_phase3_style()

    feed      = st.session_state.get("feed", {})
    shortcut  = st.session_state.get("shortcut", {})
    diameter  = st.session_state.get("diameter", {})
    height    = st.session_state.get("height", {})
    reboiler  = st.session_state.get("reboiler", {})
    condenser = st.session_state.get("condenser", {})
    thermo    = st.session_state.get("thermo", {})
    mccabe    = st.session_state.get("mccabe", {})

    P_col   = feed.get("P_col_bar", 1.013)
    F       = feed.get("F", 100.0)
    x_D     = feed.get("x_D", 0.95)
    x_B     = feed.get("x_B", 0.05)
    z_F     = feed.get("z_F", 0.50)
    T_feed  = feed.get("T_feed", 80.0)
    light   = feed.get("light", "Light Component")
    heavy   = feed.get("heavy", "Heavy Component")
    D_col   = diameter.get("D_column_std_m", 1.2)
    H_col   = height.get("total_height_m", 20.0)
    Q_reb   = reboiler.get("Q_reb_kW", 500.0)
    Q_cond  = condenser.get("Q_cond_kW", 450.0)
    R       = shortcut.get("R", 2.0)
    N       = shortcut.get("N_actual_int", 20)
    N_feed  = shortcut.get("feed_tray", int(N * 0.4))
    alpha   = thermo.get("alpha_avg", 2.5)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📐 Control Strategy", "🖥️ P&ID Schematic", "⚠️ Safety & Alarms",
        "🛡️ PSV Sizing", "📊 Control Tuning", "📋 Instrument Index"
    ])

    # ══════════════════════════════════════════════════════════════
    # TAB 1 — CONTROL STRATEGY
    # ══════════════════════════════════════════════════════════════
    with tab1:
        st.markdown("### Control Philosophy Selection")
        st.markdown("""
        <div class="formula-box">
        <div class="formula-title">Distillation Column Degrees of Freedom (DOF)</div>
        For a binary distillation column with total condenser:<br>
        &nbsp;&nbsp; DOF = 2 (two product purities to control)<br>
        &nbsp;&nbsp; Manipulated Variables available: L (reflux), V (boilup/steam), D (distillate), B (bottoms)<br>
        &nbsp;&nbsp; Since D + B = F (material balance), only 4 independent MVs available<br>
        &nbsp;&nbsp; Standard: Control pressure + level + 2 compositions = 4 loops
        </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            philosophy = st.selectbox("Primary Control Philosophy", [
                "L-V Control (Most Common — Reflux & Boilup)",
                "D-V Control (Distillate flow & Boilup)",
                "L-B Control (Reflux & Bottoms flow)",
                "D-B Control (Both product flows)",
                "L/D-V/B Ratio Control (Ratio schemes)"
            ])
            comp_control = st.selectbox("Composition Control Method", [
                "Temperature-based (Inferential) — Tray temperature as proxy",
                "Analyzer-based (GC/IR) — Direct composition measurement",
                "Dual Composition (Both xD and xB controlled)",
                "Single-end control (Distillate only)",
            ])
        with c2:
            feedforward = st.checkbox("Feed-forward Control on Feed Disturbances", value=True)
            ratio_control = st.checkbox("Reflux Ratio (L/D) Override Control", value=True)
            override_control = st.checkbox("Override / Select Controls (High/Low selectors)", value=True)
            cascade_control = st.checkbox("Cascade Control on Reboiler (T→Steam flow)", value=True)

        st.markdown("<div class='eng-divider'></div>", unsafe_allow_html=True)
        st.markdown("### 🔄 Primary Control Loops")

        # Derive setpoints from design
        D_flow = shortcut.get("D", F * 0.4)
        B_flow = shortcut.get("B", F * 0.6)
        L_flow = R * D_flow
        V_flow = (R + 1) * D_flow
        T_top  = thermo.get("T_bubble_D", 80.0)
        T_bot  = thermo.get("T_bubble_B", 110.0)

        loops = [
            ("PC-101", "Pressure Control", "Column overhead pressure",
             "Condenser CW valve / Hot vapor bypass", f"{P_col:.3f} bar",
             f"{P_col*0.95:.3f} / {P_col*1.05:.3f} bar", "PID", "1–5 min"),
            ("LC-101", "Reflux Drum Level", "Reflux drum liquid level",
             "Distillate product valve (D)", "50% NLL",
             "30% / 70%", "P-only (Level)", "Fast ~30s"),
            ("LC-102", "Column Sump Level", "Column base liquid level",
             "Bottoms product valve (B)", "50% NLL",
             "20% / 80%", "P-only (Level)", "Fast ~30s"),
            ("FC-101", "Reflux Flow Control", f"Reflux flow L = {L_flow:.1f} kmol/h",
             "Reflux return control valve", f"{L_flow:.1f} kmol/h",
             f"{L_flow*0.8:.1f} / {L_flow*1.2:.1f} kmol/h", "PID", "10–30s"),
            ("FC-102", "Steam/Boilup Control", f"Steam to reboiler (V={V_flow:.1f} kmol/h)",
             "Steam control valve FV-102", "Design steam rate",
             "±20% of design", "PID (cascade outer)", "30–90s"),
            ("FC-103", "Feed Flow Control", f"Feed F = {F:.1f} kmol/h",
             "Feed control valve FV-103", f"{F:.1f} kmol/h",
             f"{F*0.7:.1f} / {F*1.3:.1f} kmol/h", "PID", "10–30s"),
            ("TC-102", "Reboiler Temperature", f"Column base T ≈ {T_bot:.1f}°C",
             "Cascade master → FC-102 setpoint", f"{T_bot:.1f} °C",
             f"{T_bot-3:.1f} / {T_bot+3:.1f} °C", "PID cascade", "5–15 min"),
            ("TC-103", "Sensitive Tray Temp", f"Tray {N_feed} temperature (feed zone)",
             "Reflux ratio L/D adjustment", "Derived from VLE",
             "±2°C", "PID", "10–30 min"),
            ("AC-101", "Distillate Composition", f"xD = {x_D:.3f} {light}",
             "Reflux L adjustment (or D)", f"xD ≥ {x_D:.3f}",
             f"xD ≥ {x_D-0.01:.3f}", "PID (slow)", "30–120 min"),
            ("AC-102", "Bottoms Composition", f"xB = {x_B:.3f} {light}",
             "Reboiler duty V adjustment", f"xB ≤ {x_B:.3f}",
             f"xB ≤ {x_B+0.005:.3f}", "PID (slow)", "30–120 min"),
        ]

        df = pd.DataFrame(loops, columns=[
            "Tag", "Loop Name", "Controlled Variable",
            "Manipulated Variable", "Setpoint", "Allowable Range",
            "Control Mode", "Response Time"
        ])
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.markdown(f"""
        <div class="formula-box" style="border-left:4px solid #22c55e;">
        <div class="formula-title">Control narrative checklist</div>
        <b>Pressure safety:</b> PC-101 manipulates condenser-side cooling or bypass to hold {P_col:.3f} bar.<br>
        <b>Material inventory:</b> LC-101 handles reflux drum level through D, LC-102 handles base level through B.<br>
        <b>Separation quality:</b> AC-101 trims reflux for xD ≥ {x_D:.3f}; AC-102 trims boilup for xB ≤ {x_B:.3f}.<br>
        <b>Disturbance rejection:</b> Feed-forward and reflux-ratio override keep operation stable during feed-flow swings.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div class='eng-divider'></div>", unsafe_allow_html=True)
        st.markdown("### 📊 Control Loop Interaction (Relative Gain Array — RGA)")
        st.markdown("""
        <div class="formula-box">
        <div class="formula-title">RGA Analysis — Bristol Method (for 2×2 system: xD & xB)</div>
        For L-V control pairing:<br>
        &nbsp;&nbsp; λ₁₁ = 1 / (1 − (∂xD/∂V)·(∂xB/∂L) / (∂xD/∂L)·(∂xB/∂V))<br>
        &nbsp;&nbsp; If λ₁₁ ≈ 1 → L controls xD, V controls xB (good pairing)<br>
        &nbsp;&nbsp; If λ₁₁ > 1 → Interaction present but L-V pairing still acceptable<br>
        &nbsp;&nbsp; If λ₁₁ < 0 → Unstable — consider alternate pairing
        </div>
        """, unsafe_allow_html=True)

        # Estimate RGA from relative volatility
        # Simplified: for high alpha systems, L-V is strongly decoupled
        rga_11 = min(5.0, max(0.3, alpha / (alpha - 1) * 0.7))
        rga_12 = 1 - rga_11
        rga_21 = rga_12
        rga_22 = rga_11

        fig_rga = go.Figure(data=go.Heatmap(
            z=[[rga_11, rga_12], [rga_21, rga_22]],
            x=["L (Reflux)", "V (Boilup)"],
            y=["xD (Distillate purity)", "xB (Bottoms purity)"],
            text=[[f"{rga_11:.3f}", f"{rga_12:.3f}"],
                  [f"{rga_21:.3f}", f"{rga_22:.3f}"]],
            texttemplate="%{text}", textfont={"size": 18},
            colorscale=[[0, "#0d1520"], [0.5, "#0056b3"], [1, "#00b4d8"]],
            showscale=True,
            colorbar=dict(title="λ value", tickfont=dict(color="#e2e8f0"))
        ))
        fig_rga.update_layout(
            template="plotly_dark", paper_bgcolor="#0a0e14", plot_bgcolor="#111827",
            font=dict(color="#e2e8f0", family="Barlow"),
            height=260, margin=dict(t=30, b=60),
            title=dict(text=f"RGA Matrix — L-V Pairing (α={alpha:.3f})",
                       font=dict(color="#f8d477", size=19))
        )
        st.plotly_chart(fig_rga, use_container_width=True)

        if rga_11 > 0.5:
            st.markdown(f'<div class="success-panel">✅ <strong>RGA λ₁₁ = {rga_11:.3f}</strong> — L-V pairing is recommended. Reflux L controls xD, Boilup V controls xB.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="warn-panel">⚠️ <strong>RGA λ₁₁ = {rga_11:.3f}</strong> — Strong interaction. Consider D-V or alternative pairing scheme.</div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════
    # TAB 2 — P&ID SCHEMATIC
    # ══════════════════════════════════════════════════════════════
    with tab2:
        st.markdown("### 🖥️ P&ID Control Schematic — Industrial Level")
        st.markdown("""
        <div class="info-panel">
        📌 This P&ID follows ISA-5.1 symbol conventions. Instrument bubbles show Tag-Number format.
        Lines show signal types: solid = process pipe, dashed = instrument signal.
        </div>
        """, unsafe_allow_html=True)

        pid_detail = st.radio("Schematic Detail Level", ["Standard P&ID", "Simplified Process Flow"], horizontal=True)
        _render_advanced_pid(P_col, F, D_col, H_col, N, N_feed, R, Q_reb, Q_cond, x_D, x_B, z_F, T_feed, light, heavy, pid_detail)

        st.markdown("### 🌡️ Temperature Profile Along Column")
        _render_temperature_profile(N, N_feed, thermo)

    # ══════════════════════════════════════════════════════════════
    # TAB 3 — SAFETY & ALARMS
    # ══════════════════════════════════════════════════════════════
    with tab3:
        st.markdown("### ⚠️ Alarm & Safety System Design (IEC 61511 / OSHA PSM)")

        st.markdown("""
        <div class="formula-box">
        <div class="formula-title">Safety Instrumented System (SIS) — Layer of Protection Analysis (LOPA)</div>
        Independent Protection Layers (IPL) for column overpressure scenario:<br>
        &nbsp;&nbsp; IPL-1: BPCS Pressure Controller (PC-101) — PFD = 0.1<br>
        &nbsp;&nbsp; IPL-2: Operator Response to PAHH alarm — PFD = 0.1<br>
        &nbsp;&nbsp; IPL-3: SIS / ESD trip on PAHH-101 — PFD = 0.01 (SIL-2)<br>
        &nbsp;&nbsp; IPL-4: PSV mechanical relief — PFD = 0.01<br>
        &nbsp;&nbsp; Mitigated event frequency = Initiating cause freq × product of IPL PFDs
        </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            P_design = st.number_input("Design Pressure [bar(g)]", value=float(P_col * 1.1), step=0.1)
            P_MAWP   = st.number_input("MAWP [bar(g)]", value=float(P_col * 1.15), step=0.1)
        with c2:
            T_design = st.number_input("Design Temperature [°C]", value=150.0, step=5.0)
            SIL_req  = st.selectbox("Required SIL Level (from LOPA)", ["SIL-1 (PFD 0.1–0.01)", "SIL-2 (PFD 0.01–0.001)", "SIL-3 (PFD 0.001–0.0001)"])

        st.markdown("<div class='eng-divider'></div>", unsafe_allow_html=True)

        # Alarm setpoints table
        st.markdown("#### 🔔 Complete Alarm Schedule")
        alarms = [
            # Tag, Description, Location, Priority, Setpoint, Action
            ("PAHH-101", "Pressure High-High", "Column Overhead", "CRITICAL", f"{P_design:.3f} bar(g)", "ESD Trip — close feed SDV-101, trip steam SDV-102"),
            ("PAH-101",  "Pressure High",      "Column Overhead", "HIGH",     f"{P_col*1.05:.3f} bar(g)", "Operator alert — check condenser CW flow"),
            ("PAL-101",  "Pressure Low",        "Column Overhead", "HIGH",     f"{P_col*0.95:.3f} bar(g)", "Operator alert — check feed flow, reboiler duty"),
            ("PALL-101", "Pressure Low-Low",    "Column Overhead", "CRITICAL", f"{P_col*0.90:.3f} bar(g)", "ESD Trip — potential vacuum collapse"),
            ("TAHH-102", "Reboiler Temp HH",    "Column Base",     "CRITICAL", f"{T_design:.0f} °C",       "Trip steam supply SDV-102"),
            ("TAH-102",  "Reboiler Temp High",  "Column Base",     "HIGH",     f"{T_design-5:.0f} °C",     "Reduce steam — alert operator"),
            ("LAHH-101", "Reflux Drum Level HH","Reflux Drum",    "CRITICAL", "85% NLL",                   "Stop distillate pump, alert operator"),
            ("LAL-101",  "Reflux Drum Level LL","Reflux Drum",    "HIGH",     "15% NLL",                   "Increase reflux, alert operator"),
            ("LAHH-102", "Sump Level HH",        "Column Base",    "CRITICAL", "85% NLL",                   "Open bottoms valve fully — flood protection"),
            ("LALL-102", "Sump Level LL",        "Column Base",    "CRITICAL", "10% NLL",                   "Trip reboiler — dry-out protection"),
            ("FAHH-103", "Feed Flow High-High",  "Feed Line",      "HIGH",     f"{F*1.25:.0f} kmol/h",     "Partially close FV-103 feed valve"),
            ("FALL-103", "Feed Flow Low-Low",    "Feed Line",      "HIGH",     f"{F*0.5:.0f} kmol/h",      "Operator alert — check upstream feed supply"),
            ("AAH-101",  "Distillate Comp High", "Distillate",    "HIGH",     f"xD < {x_D-0.02:.3f}",     "Increase reflux ratio L/D"),
            ("AAH-102",  "Bottoms Comp High",    "Bottoms",       "HIGH",     f"xB > {x_B+0.01:.3f}",     "Increase reboiler duty (V/F ratio)"),
        ]

        alarm_df = pd.DataFrame(alarms, columns=["Tag", "Description", "Location", "Priority", "Setpoint", "Required Action"])

        # Color-code priority
        def priority_color(val):
            if val == "CRITICAL":
                return "background-color: #2d0808; color: #fca5a5"
            elif val == "HIGH":
                return "background-color: #1c1400; color: #fde68a"
            return ""

        st.dataframe(alarm_df.style.map(priority_color, subset=["Priority"]),
                     use_container_width=True, hide_index=True)

        st.markdown("<div class='eng-divider'></div>", unsafe_allow_html=True)

        # ESD Logic
        st.markdown("#### 🔴 Emergency Shutdown (ESD) Cause & Effect Matrix")
        _render_esd_matrix()

        st.markdown("<div class='eng-divider'></div>", unsafe_allow_html=True)

        # SIL Assessment
        st.markdown("#### 🛡️ SIL Verification — LOPA Summary")
        init_freq = st.number_input("Initiating event frequency [per year]", value=0.1, min_value=0.001, max_value=10.0, step=0.01, format="%.3f")
        tolerable_risk = st.number_input("Tolerable risk frequency [per year]", value=1e-5, min_value=1e-8, max_value=1e-3, step=1e-6, format="%.2e")

        pfd_bpcs = 0.1; pfd_op = 0.1; pfd_psv = 0.01
        pfd_sis_needed = tolerable_risk / (init_freq * pfd_bpcs * pfd_op * pfd_psv)

        residual_no_sis = init_freq * pfd_bpcs * pfd_op * pfd_psv
        residual_sil1   = residual_no_sis * 0.1
        residual_sil2   = residual_no_sis * 0.01

        c1, c2, c3 = st.columns(3)
        c1.metric("Residual risk (no SIS)", f"{residual_no_sis:.2e} /yr")
        c2.metric("Residual risk (SIL-1 SIS)", f"{residual_sil1:.2e} /yr")
        c3.metric("Residual risk (SIL-2 SIS)", f"{residual_sil2:.2e} /yr")

        if residual_sil2 <= tolerable_risk:
            st.markdown(f'<div class="success-panel">✅ <strong>SIL-2 SIS sufficient.</strong> Residual risk {residual_sil2:.2e}/yr ≤ tolerable {tolerable_risk:.2e}/yr. ESD system meets LOPA requirements.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="warn-panel">⚠️ <strong>SIL-3 or additional IPL required.</strong> Review LOPA with process safety engineer.</div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════
    # TAB 4 — PSV SIZING
    # ══════════════════════════════════════════════════════════════
    with tab4:
        st.markdown("### 🛡️ Pressure Safety Valve Sizing — API 520 / API 521")
        st.markdown("""
        <div class="formula-box">
        <div class="formula-title">API 520 Part 1 — Required Orifice Area (Gas/Vapor Service)</div>
        A = W / (C × K_d × P₁ × K_b × K_c) × √(T × Z / M)<br><br>
        Where:<br>
        &nbsp;&nbsp; A = Required orifice area [mm²]<br>
        &nbsp;&nbsp; W = Required relieving capacity [kg/h]<br>
        &nbsp;&nbsp; C = Gas constant = 520 × √(k × (2/(k+1))^((k+1)/(k-1)))<br>
        &nbsp;&nbsp; K_d = Effective discharge coefficient (0.975 per API 526)<br>
        &nbsp;&nbsp; P₁ = Upstream relieving pressure = P_set × 1.1 + 101.325 [kPa abs]<br>
        &nbsp;&nbsp; T = Relieving temperature [K] | Z = compressibility | M = mol. weight
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### PSV Design Basis")
            relief_scenario = st.selectbox("Governing Relief Scenario (API 521)", [
                "Fire Case — external pool fire",
                "Blocked Outlet — condenser failure",
                "Control Valve Failure — FV-102 fails open",
                "Reflux Failure — LC-101 failure",
                "Utility Failure — cooling water loss",
                "Runaway Reaction (if applicable)"
            ])
            W_relief  = st.number_input("Required relief capacity W [kg/h]",
                value=max(500.0, Q_reb * 3.6 / 2.0), min_value=50.0, step=50.0,
                help="For fire case: from API 521 Eq. or heat input method")
            P_set_barg = st.number_input("PSV Set Pressure [bar(g)]",
                value=float(round(P_col * 1.1, 2)), min_value=0.1, step=0.05)
            overpressure_pct = st.selectbox("Allowable Overpressure [%]", [10, 16, 21], index=0,
                help="API 520: 10% for non-fire, 16% for fire+blocked, 21% for supplemental")
            T_reliev = st.number_input("Relieving Temperature [°C]",
                value=float(thermo.get("T_bubble_B", 110.0) + 20), min_value=20.0, step=5.0)

        with col2:
            st.markdown("#### Fluid & Valve Properties")
            MW_vap = st.number_input("Vapour MW [g/mol]",
                value=float((feed.get("MW_light", 78) + feed.get("MW_heavy", 92)) / 2),
                min_value=2.0, max_value=400.0, step=1.0)
            gamma  = st.number_input("Cp/Cv ratio γ (isentropic exponent)", value=1.3, min_value=1.05, max_value=2.0, step=0.05)
            Z_comp = st.number_input("Compressibility factor Z", value=0.97, min_value=0.5, max_value=1.0, step=0.01)
            Kd     = st.number_input("Discharge coefficient K_d", value=0.975, min_value=0.5, max_value=1.0, step=0.005)
            Kb     = st.number_input("Back-pressure correction K_b", value=1.0, min_value=0.5, max_value=1.0, step=0.01)
            Kc     = st.number_input("Rupture disc combination K_c", value=1.0, min_value=0.5, max_value=1.0, step=0.01)
            n_valves = st.selectbox("Number of PSVs (parallel)", [1, 2, 3], index=0)

        # API 520 Calculation
        P1_kPa_abs = (P_set_barg * (1 + overpressure_pct/100) + 1.01325) * 100
        T_K = T_reliev + 273.15
        C_const = 520 * np.sqrt(gamma * (2 / (gamma + 1)) ** ((gamma + 1) / (gamma - 1)))
        A_req_mm2 = (W_relief / n_valves / (C_const * Kd * P1_kPa_abs * Kb * Kc)) * np.sqrt(T_K * Z_comp / MW_vap) * 1e6

        # API 526 standard orifice sizes
        api_orifices = [
            ("D", 71), ("E", 126), ("F", 198), ("G", 325), ("H", 506),
            ("J", 830), ("K", 1186), ("L", 1840), ("M", 2323),
            ("N", 2800), ("P", 4116), ("Q", 7129), ("R", 10322)
        ]
        selected = next((o for o in api_orifices if o[1] >= A_req_mm2), api_orifices[-1])
        oversize_pct = (selected[1] / A_req_mm2 - 1) * 100 if A_req_mm2 > 0 else 0

        st.markdown("<div class='eng-divider'></div>", unsafe_allow_html=True)
        st.markdown("#### Sizing Results")

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("C constant", f"{C_const:.1f}")
        m2.metric("P₁ relieving", f"{P1_kPa_abs:.1f} kPa abs")
        m3.metric("Required Area", f"{A_req_mm2:.2f} mm²")
        m4.metric("Selected Orifice", f"Type {selected[0]}")
        m5.metric("Selected Area", f"{selected[1]} mm²")

        if oversize_pct < 30:
            st.markdown(f'<div class="success-panel">✅ <strong>PSV-101 — API 526 Type {selected[0]}</strong> selected. Area = {selected[1]} mm² ≥ Required {A_req_mm2:.2f} mm² ({oversize_pct:.1f}% oversize — within 30% guideline). Relief scenario: {relief_scenario}.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="warn-panel">⚠️ Next larger orifice is {oversize_pct:.1f}% oversized. Consider splitting into {n_valves+1} smaller PSVs or verify relief rate.</div>', unsafe_allow_html=True)

        # PSV Data Sheet
        st.markdown("#### 📋 PSV Data Sheet")
        psv_data = {
            "Item": ["Tag Number", "Service", "Relief Scenario", "Inlet Size (est.)", "Outlet Size (est.)",
                     "Set Pressure", "Overpressure Allowed", "Relieving Pressure P₁", "Relieving Temperature",
                     "Fluid", "Phase", "MW", "Required Capacity", "Orifice Designation", "Orifice Area",
                     "Discharge Coefficient K_d", "Back-pressure Correction K_b"],
            "Value": ["PSV-101", f"{light}/{heavy} Overhead Vapor", relief_scenario,
                      f"{max(1, int(np.sqrt(A_req_mm2/50)))}\"-150# RF", f"{max(2, int(np.sqrt(A_req_mm2/30)))}\"-150# RF",
                      f"{P_set_barg:.2f} bar(g)", f"{overpressure_pct}%",
                      f"{P1_kPa_abs/100:.3f} bar abs ({P1_kPa_abs:.1f} kPa abs)",
                      f"{T_reliev:.1f} °C ({T_K:.1f} K)",
                      f"{light} / {heavy}", "Vapour / Gas",
                      f"{MW_vap:.1f} g/mol", f"{W_relief:.0f} kg/h",
                      f"Type {selected[0]} (API 526)", f"{selected[1]} mm² ({selected[1]/100:.2f} cm²)",
                      f"{Kd:.3f}", f"{Kb:.3f}"]
        }
        st.dataframe(pd.DataFrame(psv_data), use_container_width=True, hide_index=True)

        # Orifice size chart
        st.markdown("#### API 526 Orifice Selection Chart")
        areas = [o[1] for o in api_orifices]
        labels = [o[0] for o in api_orifices]
        colors = ["#22c55e" if o[0] == selected[0] else "#1e3a5f" for o in api_orifices]

        fig_psv = go.Figure()
        fig_psv.add_trace(go.Bar(x=labels, y=areas, marker_color=colors,
                                  text=[f"{a}" for a in areas], textposition="outside",
                                  textfont=dict(color="#e2e8f0", size=10)))
        fig_psv.add_hline(y=A_req_mm2, line_dash="dash", line_color="#ef4444", line_width=3,
                           annotation_text=f"Required: {A_req_mm2:.1f} mm²",
                           annotation_font=dict(color="#ef4444"))
        fig_psv.update_layout(
            template="plotly_dark", paper_bgcolor="#0a0e14", plot_bgcolor="#111827",
            font=dict(color="#e2e8f0", family="Barlow"),
            title=dict(text="API 526 PSV Orifice Selection", font=dict(color="#f8d477", size=19)),
            xaxis=dict(title="API 526 Orifice Designation", gridcolor="#1e3a5f"),
            yaxis=dict(title="Orifice Area [mm²]", gridcolor="#1e3a5f"),
            height=360, margin=dict(t=20),
            showlegend=False
        )
        st.plotly_chart(fig_psv, use_container_width=True)

        st.session_state["instrumentation"] = {
            "philosophy": philosophy if "philosophy" in dir() else "L-V",
            "PSV_tag": "PSV-101",
            "PSV_orifice": selected[0],
            "PSV_area_mm2": selected[1],
            "PSV_set_bar_g": round(P_set_barg, 3),
            "PSV_scenario": relief_scenario,
            "n_control_loops": 10,
            "SIL_level": "SIL-2",
        }

    # ══════════════════════════════════════════════════════════════
    # TAB 5 — CONTROL TUNING
    # ══════════════════════════════════════════════════════════════
    with tab5:
        st.markdown("### 📊 Controller Tuning — IMC / Ziegler-Nichols Method")
        st.markdown("""
        <div class="formula-box">
        <div class="formula-title">IMC-Based PID Tuning (Seborg et al., Process Dynamics & Control)</div>
        For first-order + dead time (FOPDT) process: G(s) = K_p·e^(−θs) / (τs + 1)<br>
        &nbsp;&nbsp; IMC filter: λ = desired closed-loop time constant (tuning parameter)<br>
        &nbsp;&nbsp; Kc = τ / (K_p × (λ + θ)) &nbsp;&nbsp; τ_I = τ &nbsp;&nbsp; τ_D = θ/2 (if τ_D used)
        </div>
        """, unsafe_allow_html=True)

        loop_sel = st.selectbox("Select Loop to Tune", [
            "PC-101 — Pressure Control",
            "TC-102 — Reboiler Temperature",
            "FC-101 — Reflux Flow",
            "LC-101 — Reflux Drum Level",
            "AC-101 — Distillate Composition",
        ])

        # Default FOPDT parameters per loop type
        defaults = {
            "PC-101": (0.8, 2.0, 0.5),
            "TC-102": (0.5, 15.0, 3.0),
            "FC-101": (1.2, 0.5, 0.1),
            "LC-101": (0.9, 10.0, 0.5),
            "AC-101": (0.3, 60.0, 10.0),
        }
        key = loop_sel.split("—")[0].strip()
        Kp_def, tau_def, theta_def = defaults.get(key, (1.0, 5.0, 1.0))

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            Kp = st.number_input("Process Gain K_p", value=Kp_def, step=0.05, format="%.3f")
        with c2:
            tau = st.number_input("Time Constant τ [min]", value=tau_def, min_value=0.1, step=0.5)
        with c3:
            theta = st.number_input("Dead Time θ [min]", value=theta_def, min_value=0.01, step=0.1)
        with c4:
            lam = st.number_input("IMC λ (≥ θ, smaller = faster)", value=max(theta_def, theta_def * 1.5), min_value=0.01, step=0.1)

        # IMC tuning
        Kc_imc = tau / (Kp * (lam + theta))
        ti_imc = tau
        td_imc = theta / 2

        # Z-N tuning (ultimate gain method estimates)
        Ku = 1.6 / (Kp * (theta / tau) * np.exp(-1))
        Pu = 2 * np.pi * tau / np.sqrt((tau/theta)**2 - 1) if tau > theta else tau * 4
        Kc_zn = 0.6 * Ku
        ti_zn = Pu / 2
        td_zn = Pu / 8

        st.markdown("#### Tuning Parameters Comparison")
        tuning_df = pd.DataFrame({
            "Method": ["IMC (Recommended)", "Ziegler-Nichols (Aggressive)", "Conservative (λ×3)"],
            "Kc (Proportional Gain)": [f"{Kc_imc:.4f}", f"{Kc_zn:.4f}", f"{Kc_imc/3:.4f}"],
            "τ_I (Integral Time) [min]": [f"{ti_imc:.3f}", f"{ti_zn:.3f}", f"{ti_imc*2:.3f}"],
            "τ_D (Derivative Time) [min]": [f"{td_imc:.3f}", f"{td_zn:.3f}", "—"],
            "Closed-loop speed": ["Moderate", "Fast (oscillatory risk)", "Slow (robust)"]
        })
        st.dataframe(tuning_df, use_container_width=True, hide_index=True)

        # Step response simulation
        st.markdown("#### Step Response Simulation")
        t_sim = np.linspace(0, min(tau * 8, 300), 500)
        setpoint_step = 1.0

        # Closed-loop response approximation (FOPDT with PID)
        tau_cl = lam
        y_cl = setpoint_step * (1 - np.exp(-t_sim / tau_cl) * (np.cos(t_sim / tau_cl * 0.3) + 0.3 * np.sin(t_sim / tau_cl * 0.3)))
        y_cl = np.clip(y_cl, 0, 1.3)

        # Open-loop step response
        y_ol = np.zeros_like(t_sim)
        dead_idx = int(theta / (t_sim[-1] / len(t_sim)))
        for i in range(dead_idx, len(t_sim)):
            t_eff = t_sim[i] - theta
            y_ol[i] = Kp * setpoint_step * (1 - np.exp(-t_eff / tau))

        fig_tune = go.Figure()
        fig_tune.add_trace(go.Scatter(x=t_sim, y=[1.0]*len(t_sim), mode="lines",
                                       name="Setpoint", line=dict(color="#e2e8f0", dash="dash", width=2.5)))
        fig_tune.add_trace(go.Scatter(x=t_sim, y=y_cl, mode="lines",
                                       name=f"Closed-loop (IMC λ={lam:.1f} min)",
                                       line=dict(color="#00b4d8", width=3.2)))
        fig_tune.add_trace(go.Scatter(x=t_sim, y=y_ol, mode="lines",
                                       name="Open-loop (no control)",
                                       line=dict(color="#f59e0b", width=3, dash="dot")))
        fig_tune.add_hline(y=1.05, line_dash="dot", line_color="#ef4444", line_width=3, annotation_text="+5% overshoot limit")
        fig_tune.update_layout(
            template="plotly_dark", paper_bgcolor="#0a0e14", plot_bgcolor="#111827",
            font=dict(color="#e2e8f0", family="Barlow"),
            title=dict(text="Control Step Response", font=dict(color="#f8d477", size=19)),
            xaxis=dict(title="Time [min]", gridcolor="#1e3a5f"),
            yaxis=dict(title="Normalized Response", gridcolor="#1e3a5f"),
            height=380, margin=dict(t=20),
            legend=dict(bgcolor="#111827", bordercolor="#1e3a5f")
        )
        st.plotly_chart(fig_tune, use_container_width=True)

        c1, c2, c3 = st.columns(3)
        rise_time = lam * 2.2
        settling_time = lam * 4.0
        c1.metric("Rise Time (10→90%)", f"{rise_time:.1f} min")
        c2.metric("Settling Time (±5%)", f"{settling_time:.1f} min")
        c3.metric("Closed-loop τ_cl", f"{lam:.1f} min")

    # ══════════════════════════════════════════════════════════════
    # TAB 6 — INSTRUMENT INDEX
    # ══════════════════════════════════════════════════════════════
    with tab6:
        st.markdown("### 📋 Complete Instrument Index (IID)")

        instruments = [
            # Tag, Type, Service, Location, Technology, Range, Signal, Material, Mfr
            ("FT-101",  "Flow Transmitter",        "Feed flow",              "Feed line upstream of FV-103",     "Coriolis mass flow",        f"0–{F*1.5:.0f} kmol/h",    "4–20mA HART",       "316L SS",    "Emerson"),
            ("FV-103",  "Control Valve",            "Feed flow control",      "Feed line",                        "Globe valve, fail-close",   f"Cv ~ {F*0.5:.0f}",        "4–20mA + positioner","CF8M SS",  "Fisher"),
            ("FT-102",  "Flow Transmitter",        "Reflux flow L",          "Reflux return line",               "Magnetic flow (MFM)",       f"0–{L_flow*1.5:.0f} kmol/h","4–20mA HART",      "316L SS",    "Endress+Hauser"),
            ("FV-102",  "Control Valve",            "Steam to reboiler",      "Steam supply line",                "Globe valve, fail-close",   "Cv per steam calc",        "4–20mA + positioner","WCB CS",   "Emerson"),
            ("FT-103",  "Flow Transmitter",        "Steam flow to reboiler", "Steam supply",                     "Vortex flow meter",         "0–2× design steam",        "4–20mA HART",       "WCB CS",     "Yokogawa"),
            ("PT-101",  "Pressure Transmitter",    "Column overhead P",      "Top nozzle, upstream condenser",   "Diaphragm seal gauge",      f"0–{P_col*2:.2f} bar",     "4–20mA HART",       "316L SS",    "Rosemount"),
            ("PT-102",  "Pressure Transmitter",    "Column base pressure",   "Bottom nozzle above reboiler",     "Remote seal DP cell",       f"0–{P_col*2.5:.2f} bar",   "4–20mA HART",       "316L SS",    "Rosemount"),
            ("PDT-101", "Differential Pressure",   "Column total ΔP",        "Top to bottom tapping",            "DP transmitter",            "0–1000 mmH₂O",             "4–20mA HART",       "316L SS",    "Honeywell"),
            ("TT-101",  "Temperature Transmitter", "Feed tray temperature",  f"Tray {N_feed} thermowell",        "RTD PT-100, 4-wire",        "0–200°C",                  "4–20mA",            "316L SS",    "Wika"),
            ("TT-102",  "Temperature Transmitter", "Reboiler outlet T",      "Reboiler outlet nozzle",           "RTD PT-100 (dual)",         "0–250°C",                  "4–20mA",            "316L SS",    "Endress+Hauser"),
            ("TT-103",  "Temperature Transmitter", "Condenser outlet T",     "Condenser outlet nozzle",          "RTD PT-100",                "0–150°C",                  "4–20mA",            "316L SS",    "Wika"),
            ("TT-104",  "Temperature Transmitter", "Column top temp",        "Top tray thermowell",              "Thermocouple K-type",       "0–200°C",                  "4–20mA",            "Inconel 600","Omega"),
            ("TT-105",  "Temperature Profile",     "Mid-column profile",     f"Every 5 trays (4 pts)",           "Thermocouple K-type MUX",   "0–200°C",                  "Fieldbus/Modbus",   "316L SS",    "Yokogawa"),
            ("LT-101",  "Level Transmitter",       "Reflux drum level",      "Reflux drum side nozzles",         "Guided Wave Radar (GWR)",   "0–100% NLL",               "HART",              "316L SS",    "Emerson"),
            ("LT-102",  "Level Transmitter",       "Column sump level",      "Column base side nozzles",         "Differential pressure cell","0–100% NLL",               "4–20mA HART",       "316L SS",    "Rosemount"),
            ("LG-101",  "Level Gauge",             "Reflux drum visual",     "Reflux drum",                      "Magnetic level gauge",      "Full range",               "Local visual",      "CS w/ 316L","Magnetrol"),
            ("AT-101",  "Composition Analyzer",    f"Distillate xD",         "Distillate sample point",          "Online GC / Near-IR",       f"0–100% {light}",          "Modbus RS-485",     "316L SS",    "Siemens"),
            ("AT-102",  "Composition Analyzer",    f"Bottoms xB",            "Bottoms sample point",             "Online GC / Near-IR",       f"0–100% {light}",          "Modbus RS-485",     "316L SS",    "Siemens"),
            ("PSV-101", "Safety Relief Valve",     "Column overpressure",    "Column top nozzle",                "Spring-loaded, balanced bellow",f"Set: {P_col*1.1:.2f} bar(g)","Mechanical","Alloy steel", "Emerson"),
            ("SDV-101", "Shutdown Valve",          "Feed ESD isolation",     "Feed line upstream FT-101",        "Ball valve, fail-close",    "Full bore",                "24VDC solenoid",    "CF8M SS",    "Valtek"),
            ("SDV-102", "Shutdown Valve",          "Steam ESD isolation",    "Steam supply to reboiler",         "Gate valve, fail-close",    "Full bore",                "24VDC solenoid",    "WCB CS",     "Valtek"),
            ("SDV-103", "Shutdown Valve",          "Distillate ESD block",   "Distillate outlet",                "Ball valve, fail-close",    "Full bore",                "24VDC solenoid",    "CF8M SS",    "Valtek"),
            ("CV-101",  "Check Valve",             "Reflux anti-backflow",   "Reflux line",                      "Swing check",               "Full bore",                "Mechanical",        "316L SS",    "Crane"),
            ("XY-101",  "ESD Logic Solver",        "Column ESD system",      "Control room / MCC",               "SIL-2 logic controller",    "8 in / 8 out",             "Hardwired + Profibus","N/A",    "Hima"),
        ]

        filter_type = st.multiselect("Filter by Instrument Type",
            options=sorted(set(i[1] for i in instruments)),
            default=[], placeholder="Show all types...")

        disp = instruments if not filter_type else [i for i in instruments if i[1] in filter_type]

        inst_df = pd.DataFrame(disp, columns=[
            "Tag", "Type", "Service", "Location",
            "Technology", "Range", "Signal/Actuation", "Material", "Manufacturer"
        ])
        st.dataframe(inst_df, use_container_width=True, hide_index=True)
        st.info(f"📊 Total instruments: **{len(instruments)}** | Shown: **{len(disp)}**")

        if st.button("💾 Save Instrumentation Data", type="primary"):
            st.session_state["instrumentation"] = {
                "n_instruments": len(instruments),
                "n_control_loops": 10,
                "PSV_tag": "PSV-101",
                "ESD_valves": 3,
                "SIL_level": "SIL-2",
                "control_philosophy": "L-V Control",
            }
            st.success("✅ Instrumentation data saved! 24 instruments, 10 control loops, SIL-2 ESD system documented.")


# ══════════════════════════════════════════════════════════════════════
# HELPER: ADVANCED P&ID
# ══════════════════════════════════════════════════════════════════════
def _render_advanced_pid(P_col, F, D_col, H_col, N, N_feed, R, Q_reb, Q_cond, x_D, x_B, z_F, T_feed, light, heavy, detail):
    fig = go.Figure()
    W = 18; H_plot = 14

    # ── Column shell ──────────────────────────────────────────────
    fig.add_shape(type="rect", x0=6, y0=1.5, x1=9, y1=13,
                  line=dict(color="#00b4d8", width=3), fillcolor="rgba(0,30,50,0.6)")
    fig.add_annotation(x=7.5, y=7.2, text=f"DISTILLATION\nCOLUMN\nD={D_col:.2f}m H={H_col:.1f}m\nN={N} trays",
                       font=dict(color="#00b4d8", size=9), showarrow=False, align="center")

    # Feed tray indicator
    feed_y = 1.5 + (N_feed / N) * 11.5
    fig.add_shape(type="line", x0=5.5, x1=6, y0=feed_y, y1=feed_y,
                  line=dict(color="#f59e0b", width=2, dash="dot"))
    fig.add_annotation(x=5.8, y=feed_y + 0.3, text=f"Feed tray {N_feed}",
                       font=dict(color="#f59e0b", size=8), showarrow=False)

    # ── Condenser (top right) ─────────────────────────────────────
    fig.add_shape(type="rect", x0=11, y0=11, x1=14, y1=13,
                  line=dict(color="#90e0ef", width=2), fillcolor="rgba(0,50,80,0.6)")
    fig.add_annotation(x=12.5, y=12, text=f"CONDENSER\nQ={Q_cond:.0f} kW\n(E-101)",
                       font=dict(color="#90e0ef", size=8), showarrow=False)
    # vapor line to condenser
    fig.add_shape(type="line", x0=9, x1=11, y0=12.5, y1=12.5,
                  line=dict(color="#e2e8f0", width=2))
    fig.add_annotation(x=10, y=12.8, text="Overhead Vapor", font=dict(color="#94a3b8", size=7.5), showarrow=False)

    # ── Reflux drum ───────────────────────────────────────────────
    fig.add_shape(type="rect", x0=11, y0=8.5, x1=14, y1=10.2,
                  line=dict(color="#22c55e", width=2), fillcolor="rgba(0,40,20,0.6)")
    fig.add_annotation(x=12.5, y=9.35, text="REFLUX DRUM\n(V-101)\nLT-101 / LC-101",
                       font=dict(color="#22c55e", size=8), showarrow=False)
    # condenser to reflux drum
    fig.add_shape(type="line", x0=12.5, x1=12.5, y0=11, y1=10.2,
                  line=dict(color="#e2e8f0", width=2))

    # ── Reboiler ──────────────────────────────────────────────────
    fig.add_shape(type="rect", x0=10, y0=0.2, x1=13.5, y1=1.8,
                  line=dict(color="#f59e0b", width=2), fillcolor="rgba(50,30,0,0.6)")
    fig.add_annotation(x=11.75, y=1.0, text=f"REBOILER\nQ={Q_reb:.0f} kW (E-102)\nKettle type",
                       font=dict(color="#f59e0b", size=8), showarrow=False)
    # column to reboiler
    fig.add_shape(type="line", x0=9, x1=10, y0=1.5, y1=1.0,
                  line=dict(color="#e2e8f0", width=2))
    # reboiler vapor return
    fig.add_shape(type="line", x0=10, x1=9, y0=1.5, y1=2.2,
                  line=dict(color="#e2e8f0", width=2, dash="dot"))
    fig.add_annotation(x=9.5, y=2.5, text="Vapor return", font=dict(color="#94a3b8", size=7), showarrow=False)

    # ── Process lines ─────────────────────────────────────────────
    # Feed line
    fig.add_annotation(x=6, y=feed_y, ax=3.5, ay=feed_y,
                       text="", arrowcolor="#f59e0b", arrowwidth=2.5, arrowhead=3)
    fig.add_annotation(x=2.5, y=feed_y + 0.3, text=f"FEED\nF={F:.0f} kmol/h\nzF={z_F:.3f}\n{light}/{heavy}",
                       font=dict(color="#f59e0b", size=8), showarrow=False)

    # Distillate line
    fig.add_annotation(x=16.5, y=9.35, ax=14, ay=9.35,
                       text="", arrowcolor="#22c55e", arrowwidth=2.5, arrowhead=3)
    fig.add_annotation(x=17, y=9.7, text=f"DISTILLATE\nxD={x_D:.3f}",
                       font=dict(color="#22c55e", size=8), showarrow=False)

    # Reflux line back to column
    fig.add_shape(type="line", x0=11, x1=9, y0=9.35, y1=12.0,
                  line=dict(color="#00b4d8", width=1.5, dash="dash"))
    fig.add_annotation(x=10, y=10.8, text="Reflux L", font=dict(color="#00b4d8", size=7.5), showarrow=False)

    # Bottoms line
    fig.add_annotation(x=7.5, y=-0.5, ax=7.5, ay=1.5,
                       text="", arrowcolor="#ef4444", arrowwidth=2.5, arrowhead=3)
    fig.add_annotation(x=7.5, y=-0.8, text=f"BOTTOMS\nxB={x_B:.3f}",
                       font=dict(color="#ef4444", size=8), showarrow=False)

    # Steam to reboiler
    fig.add_annotation(x=11.75, y=0.2, ax=11.75, ay=-0.5,
                       text="", arrowcolor="#fbbf24", arrowwidth=2, arrowhead=3)
    fig.add_annotation(x=11.75, y=-0.7, text="STEAM", font=dict(color="#fbbf24", size=8), showarrow=False)

    # CW to condenser
    fig.add_annotation(x=14, y=11.8, ax=15.5, ay=11.8,
                       text="", arrowcolor="#60a5fa", arrowwidth=2, arrowhead=3)
    fig.add_annotation(x=15.8, y=11.8, text="CW IN", font=dict(color="#60a5fa", size=8), showarrow=False)
    fig.add_annotation(x=14, y=12.3, ax=15.5, ay=12.3,
                       text="", arrowcolor="#60a5fa", arrowwidth=2, arrowhead=3)
    fig.add_annotation(x=15.8, y=12.3, text="CW OUT", font=dict(color="#60a5fa", size=8), showarrow=False)

    if detail == "Standard P&ID":
        # ── Instrument bubbles ─────────────────────────────────────
        instruments_pid = [
            # (x, y, tag, signal_color)
            (9.8, 12.5,  "PT-101\nPC-101", "#c084fc"),
            (9.8, 11.0,  "TT-104\nTC-104", "#f87171"),
            (9.8, feed_y,"TT-101\nTC-101", "#f87171"),
            (9.8, 2.5,   "TT-102\nTC-102", "#f87171"),
            (14, 9.7,    "FT-102\nFC-101", "#34d399"),
            (4.0, feed_y+0.5, "FT-103\nFC-103", "#34d399"),
            (12.5, 10.5, "LT-101\nLC-101", "#60a5fa"),
            (5.5, 1.0,   "LT-102\nLC-102", "#60a5fa"),
            (14.5, 12.5, "AT-101\nAC-101", "#fb923c"),
            (5.5, 0.5,   "AT-102\nAC-102", "#fb923c"),
            (9.0, 13.5,  "PSV-101", "#ef4444"),
            (3.2, feed_y-0.8, "SDV-101", "#f87171"),
        ]

        for ix, iy, tag, clr in instruments_pid:
            fig.add_shape(type="circle", x0=ix-0.55, y0=iy-0.5, x1=ix+0.55, y1=iy+0.5,
                          line=dict(color=clr, width=1.5), fillcolor="rgba(10,14,20,0.9)")
            fig.add_annotation(x=ix, y=iy, text=tag, font=dict(color=clr, size=6.5),
                               showarrow=False, align="center")

        # Signal lines (dashed) from instruments to column
        for ix, iy, tag, clr in instruments_pid[:4]:
            fig.add_shape(type="line", x0=9, x1=ix-0.55, y0=iy, y1=iy,
                          line=dict(color=clr, width=0.8, dash="dashdot"))

    fig.update_layout(
        xaxis=dict(range=[-0.5, W+0.5], showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(range=[-1.5, H_plot+0.5], showgrid=False, zeroline=False, showticklabels=False),
        paper_bgcolor="#070c12", plot_bgcolor="#070c12",
        height=600, margin=dict(l=5, r=5, t=35, b=5),
        title=dict(text=f"P&ID — {light}/{heavy} Distillation Column (ISA-5.1 Style)",
                   font=dict(color="#e2e8f0", size=13))
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_temperature_profile(N, N_feed, thermo):
    T_top = thermo.get("T_bubble_D", 80.0)
    T_bot = thermo.get("T_bubble_B", 110.0)
    stages = np.arange(1, N + 1)
    T_prof = T_bot - (T_bot - T_top) * (stages - 1) / (N - 1)
    # Add slight S-curve inflection at feed tray
    for i, s in enumerate(stages):
        if s <= N_feed:
            T_prof[i] = T_bot - (T_bot - (T_top + T_bot) / 2) * (s - 1) / (N_feed - 1) if N_feed > 1 else T_bot
        else:
            T_prof[i] = (T_top + T_bot) / 2 - ((T_top + T_bot) / 2 - T_top) * (s - N_feed) / (N - N_feed) if N > N_feed else T_top

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=T_prof, y=stages, mode="lines+markers",
        line=dict(color="#f59e0b", width=2.5),
        marker=dict(size=4, color="#f59e0b"),
        name="Temperature Profile"
    ))
    fig.add_hline(y=N_feed, line_dash="dot", line_color="#22c55e",
                  annotation_text=f"Feed tray {N_feed}", annotation_font=dict(color="#22c55e"))
    fig.add_vline(x=T_top, line_dash="dash", line_color="#90e0ef",
                  annotation_text=f"T_top={T_top:.1f}°C", annotation_font=dict(color="#90e0ef", size=10))
    fig.add_vline(x=T_bot, line_dash="dash", line_color="#ef4444",
                  annotation_text=f"T_bot={T_bot:.1f}°C", annotation_font=dict(color="#ef4444", size=10))
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="#0a0e14", plot_bgcolor="#111827",
        font=dict(color="#e2e8f0", family="Barlow"),
        xaxis=dict(title="Temperature [°C]", gridcolor="#1e3a5f"),
        yaxis=dict(title="Stage Number (1=top)", gridcolor="#1e3a5f", autorange="reversed"),
        height=380, margin=dict(t=20),
        legend=dict(bgcolor="#111827")
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_esd_matrix():
    causes = ["PAHH-101 (P High-High)", "LALL-102 (Sump LL)", "LAHH-101 (Drum HH)", "TAHH-102 (Reb T HH)", "Manual ESD"]
    effects = ["SDV-101\nFeed Close", "SDV-102\nSteam Close", "SDV-103\nDistil Close", "FV-103\nFeed Throttle", "PC-101\nVent Open", "Alarm\nHorn/Light"]

    # 1=act, 0=no action
    matrix = [
        [1, 1, 0, 1, 1, 1],  # PAHH
        [0, 1, 0, 0, 0, 1],  # LALL sump
        [0, 0, 1, 0, 0, 1],  # LAHH drum
        [0, 1, 0, 0, 0, 1],  # TAHH reb
        [1, 1, 1, 1, 0, 1],  # Manual ESD
    ]

    colorscale = [[0, "#0a0e14"], [1, "#ef4444"]]
    fig = go.Figure(data=go.Heatmap(
        z=matrix, x=effects, y=causes,
        text=[["CLOSE" if v else "—" for v in row] for row in matrix],
        texttemplate="%{text}", textfont={"size": 11, "color": "white"},
        colorscale=colorscale, showscale=False,
        xgap=3, ygap=3
    ))
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="#0a0e14", plot_bgcolor="#111827",
        font=dict(color="#e2e8f0", family="Barlow", size=11),
        height=280, margin=dict(t=20, b=60, l=160),
        xaxis=dict(side="top"),
    )
    st.plotly_chart(fig, use_container_width=True)
