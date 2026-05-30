"""pages/packing_design.py — Packed Column Design Module"""
import streamlit as st
import numpy as np
import plotly.graph_objects as go
from thermodynamics.thermo_engine import binary_mixture_props

PACKINGS = {
    "Raschig Rings 25mm":   {"Fp": 512, "a": 190, "eps": 0.73, "HETP_base": 0.50},
    "Raschig Rings 50mm":   {"Fp": 187, "a": 95,  "eps": 0.78, "HETP_base": 0.70},
    "Pall Rings 25mm":      {"Fp": 157, "a": 205, "eps": 0.94, "HETP_base": 0.35},
    "Pall Rings 50mm":      {"Fp": 66,  "a": 112, "eps": 0.95, "HETP_base": 0.50},
    "Berl Saddles 25mm":    {"Fp": 240, "a": 250, "eps": 0.68, "HETP_base": 0.45},
    "Intalox Saddles 25mm": {"Fp": 145, "a": 255, "eps": 0.71, "HETP_base": 0.40},
    "Intalox Saddles 50mm": {"Fp": 92,  "a": 118, "eps": 0.74, "HETP_base": 0.55},
    "Mellapak 250Y":        {"Fp": 33,  "a": 250, "eps": 0.97, "HETP_base": 0.25},
    "Mellapak 500Y":        {"Fp": 45,  "a": 500, "eps": 0.95, "HETP_base": 0.15},
    "Flexipac 2Y":          {"Fp": 29,  "a": 233, "eps": 0.97, "HETP_base": 0.28},
}

def render():
    st.markdown("""
    <div class="section-header">
        <h1>◎ Packing Design Module</h1>
        <p>Random and structured packing selection, HETP, pressure drop, and flooding calculations.</p>
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
    .formula-box,
    .result-box {
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
    .result-box .value,
    .info-panel strong,
    .success-panel strong,
    .warn-panel strong {
        color: #22c55e !important;
        font-weight: 900 !important;
    }
    .result-box .label {
        color: #ff5b6e !important;
        font-weight: 900 !important;
    }
    .result-box .unit {
        color: #dbeafe !important;
        font-weight: 800 !important;
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
    .packed-calc-separator {
        border-top: 1px dashed rgba(248, 212, 119, 0.48);
        margin: 0.85rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

    feed     = st.session_state.get("feed", {})
    shortcut = st.session_state.get("shortcut", {})
    thermo   = st.session_state.get("thermo", {})

    if not feed:
        st.warning("⚠️ Complete Feed Specifications and Shortcut Design first.")
        return

    col_type = st.session_state.get("column_type", None)
    if col_type == "tray":
        st.markdown("""
        <div class="warn-panel">
        ⚠️ <strong>Tray Column selected.</strong>
        HETP and packing hydraulics apply to packed columns only.
        For tray column → use <b>▦ Tray Design</b> section.
        <i>You can still view this section for reference or comparison.</i>
        </div>
        """, unsafe_allow_html=True)
    elif col_type == "packed":
        st.markdown("""
        <div class="success-panel">
        ✅ <strong>Packed Column selected</strong> — this section is fully applicable to your design.
        </div>
        """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📦 Packing Selection", "📐 Column Sizing", "📋 Summary"])

    R      = shortcut.get("R", 2.0)
    D_flow = shortcut.get("D", feed.get("F", 100) * 0.5)
    V_mol  = (R + 1) * D_flow
    N_theor= shortcut.get("N_actual_int", 15)
    light  = feed.get("light", "Benzene")
    heavy  = feed.get("heavy", "Toluene")
    x_D    = feed.get("x_D", 0.95)
    dist_props = feed.get("distillate_props") or thermo.get("distillate_props") or binary_mixture_props(light, heavy, x_D)
    MW_avg = dist_props.get("MW", (feed.get("MW_light", 78) + feed.get("MW_heavy", 92)) / 2)

    # ── Key concept explanation ────────────────────────────────────────
    st.markdown(f"""
    <div class="formula-box">
        <div class="formula-title">📌 N_theoretical in Packed Column</div>
        From Shortcut Design (Gilliland): <b>N_theoretical = {N_theor} stages</b><br><br>
        Packed columns have <b>no physical stages</b> — liquid & vapor contact continuously.
        We use "theoretical stages" as a mathematical equivalent:<br><br>
        &nbsp;&nbsp; <b>Packed Height = N_theoretical × HETP</b><br><br>
        HETP = height of packing that gives same separation as one theoretical stage.
        Select packing below → get HETP → packed bed height is calculated automatically.
    </div>
    """, unsafe_allow_html=True)

    with tab1:
        st.markdown("### Packing Type Selection")
        cat = st.radio("Packing Category", ["Random Packing", "Structured Packing"], horizontal=True)
        if cat == "Random Packing":
            options = [k for k in PACKINGS if "Raschig" in k or "Pall" in k or "Berl" in k]
        else:
            options = [k for k in PACKINGS if "Mellapak" in k or "Flexipac" in k]

        packing_sel = st.selectbox("Select Packing", options)
        pk = PACKINGS[packing_sel]

        st.markdown(f"""
        <div class="formula-box" style="border-left:4px solid #22c55e;">
        <div class="formula-title">Selected Packing Properties</div>
        <b>Packing factor F<sub>p</sub>:</b> {pk['Fp']} m⁻¹ — lower F<sub>p</sub> usually gives higher capacity and lower pressure drop.<br>
        <div class="packed-calc-separator"></div>
        <b>Specific surface area a:</b> {pk['a']} m²/m³ — higher area improves mass-transfer contact.<br>
        <div class="packed-calc-separator"></div>
        <b>Void fraction ε:</b> {pk['eps']} — higher void fraction reduces resistance to vapour flow.<br>
        <div class="packed-calc-separator"></div>
        <b>Base HETP:</b> {pk['HETP_base']} m/stage — lower HETP means less packing height for the same separation.
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("Packing Factor Fp", f"{pk['Fp']} m⁻¹")
        c2.metric("Specific Surface a", f"{pk['a']} m²/m³")
        c3.metric("Void Fraction ε", f"{pk['eps']}")

        st.markdown(f"""
        <div class="info-panel">
        📌 <b>Packing: {packing_sel}</b><br>
        Category: {cat} | Base HETP ≈ {pk['HETP_base']} m
        </div>
        """, unsafe_allow_html=True)

        # Packing comparison table
        st.markdown("### Packing Comparison")
        import pandas as pd
        df = pd.DataFrame([
            {"Packing": k, "Category": "Random" if any(x in k for x in ["Raschig","Pall","Berl"]) else "Structured",
             "Fp [1/m]": v["Fp"], "Surface [m²/m³]": v["a"],
             "Void ε": v["eps"], "Base HETP [m]": v["HETP_base"]}
            for k, v in PACKINGS.items()
        ])
        st.dataframe(df, use_container_width=True, hide_index=True)

    with tab2:
        st.markdown("### Column Sizing — GPDC Method")
        c1, c2 = st.columns(2)
        with c1:
            T_K   = st.number_input("Operating Temperature [K]", 300.0, 500.0,
                                     float(round(thermo.get("T_bubble_D", feed.get("T_feed", 80.0)) + 273.15, 1)), 5.0)
            P_bar = feed.get("P_col_bar", 1.013)
            rho_L = st.number_input("Liquid Density ρL [kg/m³]", 500.0, 1200.0,
                                     float(feed.get("rho_L_distillate", dist_props.get("rho_L", 820.0))), 10.0)
            mu_L  = st.number_input("Liquid Viscosity μL [mPa·s]", 0.1, 10.0,
                                     float(feed.get("mu_L_distillate", dist_props.get("mu_L", 0.5))), 0.1)
        with c2:
            flood_frac = st.slider("Design Flooding Fraction", 0.60, 0.85, 0.75, 0.01)
            HETP_corr  = st.number_input("HETP Correction Factor", 0.8, 1.5, 1.0, 0.05)

        R_gas = 8314
        # Real gas correction — compressibility factor Z (Pitzer correlation simple form)
        # Z ≈ 1 for low/moderate pressure; user can override
        Z_factor = st.number_input(
            "Compressibility factor Z (1.0 = ideal gas)",
            value=1.0, min_value=0.50, max_value=1.20, step=0.01,
            help="Z < 1 for high pressure or polar systems. Use 1.0 for atmospheric/low pressure."
        )
        rho_V = (P_bar * 1e5 * MW_avg) / (Z_factor * R_gas * T_K)
        V_kg_h = V_mol * MW_avg
        V_m3_s = V_kg_h / (3600 * rho_V)

        # Eckert GPDC flooding velocity (simplified)
        Fp    = pk["Fp"]
        u_flood = 1.2 * ((rho_L - rho_V) / (Fp * rho_V)) ** 0.5 * (mu_L / 1.0) ** (-0.05)
        u_op    = flood_frac * u_flood

        A_col   = V_m3_s / u_op
        D_col   = np.sqrt(4 * A_col / np.pi)
        D_std   = np.ceil(D_col / 0.05) * 0.05

        # HETP and packing height
        HETP    = pk["HETP_base"] * HETP_corr
        Z_pack  = N_theor * HETP

        # Pressure drop (Leva correlation simplified)
        dP_m    = 200 * Fp * rho_V * u_op**2 / rho_L  # Pa/m approx
        dP_tot  = dP_m * Z_pack

        # Total column height
        H_top   = 1.5   # disengagement
        H_bot   = 2.0   # sump
        H_redis = int(Z_pack / 5.0) * 0.3  # redistributors every 5m
        H_total = Z_pack + H_top + H_bot + H_redis

        st.markdown("<div class='eng-divider'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="formula-box" style="border-left:4px solid #f59e0b;">
        <div class="formula-title">Step-by-step packed sizing calculation</div>
        <b>1. Vapour flow:</b>
        V = (R+1)D = ({R:.3f}+1) × {D_flow:.2f} = <b>{V_mol:.2f} kmol/h</b><br>
        <div class="packed-calc-separator"></div>
        <b>2. Vapour density:</b>
        ρ<sub>V</sub> = PMW/(ZRT) = <b>{rho_V:.4f} kg/m³</b>
        at T = {T_K:.1f} K, P = {P_bar:.4f} bar, Z = {Z_factor:.2f}<br>
        <div class="packed-calc-separator"></div>
        <b>3. Flooding velocity:</b>
        u<sub>flood</sub> = 1.2√[(ρ<sub>L</sub>−ρ<sub>V</sub>)/(F<sub>p</sub>ρ<sub>V</sub>)]μ<sub>L</sub><sup>-0.05</sup>
        = <b>{u_flood:.4f} m/s</b><br>
        <b>4. Operating velocity:</b>
        u<sub>op</sub> = {flood_frac:.2f} × {u_flood:.4f} = <b>{u_op:.4f} m/s</b><br>
        <div class="packed-calc-separator"></div>
        <b>5. Column area and diameter:</b>
        A = Q<sub>V</sub>/u<sub>op</sub> = <b>{A_col:.4f} m²</b>,
        D = √(4A/π) = <b>{D_col:.4f} m</b> → standard <b>{D_std:.2f} m</b><br>
        <div class="packed-calc-separator"></div>
        <b>6. Packed height:</b>
        Z = N<sub>theoretical</sub> × HETP = {N_theor} × {HETP:.3f} = <b>{Z_pack:.2f} m</b><br>
        <b>7. Pressure drop:</b>
        ΔP = {dP_m:.0f} Pa/m × {Z_pack:.2f} m = <b>{dP_tot:.0f} Pa</b><br>
        <b>8. Total height:</b>
        H = Z + H<sub>top</sub> + H<sub>bottom</sub> + H<sub>redistributor</sub>
        = {Z_pack:.2f} + {H_top:.1f} + {H_bot:.1f} + {H_redis:.2f}
        = <b>{H_total:.2f} m</b>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### Results")

        m1,m2,m3,m4 = st.columns(4)
        m1.metric("Column Diameter", f"{D_std:.2f} m")
        m2.metric("HETP", f"{HETP:.3f} m")
        m3.metric("Packing Height Z", f"{Z_pack:.2f} m")
        m4.metric("Total Column Height", f"{H_total:.2f} m")

        m5,m6,m7,m8 = st.columns(4)
        m5.metric("Flood Velocity", f"{u_flood:.3f} m/s")
        m6.metric("Operating Velocity", f"{u_op:.3f} m/s")
        m7.metric("ΔP per meter", f"{dP_m:.0f} Pa/m")
        m8.metric("Total ΔP", f"{dP_tot:.0f} Pa")

        # Sensitivity: HETP vs reflux ratio
        st.markdown("#### HETP vs Flooding Fraction — Sensitivity")
        ff_range = np.linspace(0.50, 0.90, 50)
        dP_range = [200 * Fp * rho_V * (f * u_flood)**2 / rho_L * Z_pack for f in ff_range]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=ff_range*100, y=dP_range, mode="lines+markers",
                                  name="Total ΔP [Pa]",
                                  line=dict(color="#f59e0b", width=3.2),
                                  marker=dict(size=5, color="#00d4ff", line=dict(color="#f8fbff", width=1))))
        fig.add_vline(x=flood_frac*100, line_dash="dash", line_color="#00b4d8", line_width=3,
                       annotation_text=f"Design {flood_frac*100:.0f}%",
                       annotation_font_color="#00d4ff")
        fig.update_layout(
            template="plotly_dark", paper_bgcolor="#0a0e14", plot_bgcolor="#111827",
            font=dict(color="#e2e8f0"), height=340,
            xaxis=dict(title="Flooding Fraction [%]", gridcolor="#1e3a5f"),
            yaxis=dict(title="Total Pressure Drop [Pa]", gridcolor="#1e3a5f"),
            title=dict(text="Packed Bed Pressure Drop vs Flooding Fraction",
                       font=dict(color="#f8d477", size=19)),
            margin=dict(t=48)
        )
        st.plotly_chart(fig, use_container_width=True)

        if st.button("💾 Save Packing Design", type="primary"):
            st.session_state["packing_design"] = {
                "packing": packing_sel, "HETP": HETP, "Z_pack": Z_pack,
                "D_col": D_std, "u_flood": u_flood, "u_op": u_op,
                "H_total": H_total, "dP_tot_Pa": dP_tot,
            }
            st.success("✅ Packing design saved!")

    with tab3:
        st.markdown("### Complete Packing Design Summary")
        import pandas as pd
        data = {
            "Parameter": ["Packing Type","Packing Factor Fp","Specific Surface",
                          "Void Fraction","HETP","Packing Height Z",
                          "Column Diameter","Flood Velocity","Operating Velocity",
                          "ΔP per meter","Total ΔP","Total Column Height"],
            "Value": [packing_sel, f"{pk['Fp']} m⁻¹", f"{pk['a']} m²/m³",
                      f"{pk['eps']}", f"{pk['HETP_base']*HETP_corr:.3f} m",
                      f"{pk['HETP_base']*HETP_corr*N_theor:.2f} m",
                      f"{D_std:.2f} m", f"{u_flood:.3f} m/s", f"{u_op:.3f} m/s",
                      f"{dP_m:.0f} Pa/m", f"{dP_tot:.0f} Pa", f"{H_total:.2f} m"],
            "Reference": ["Perry's 14-48","Perry's Table 14-13","Perry's 14-49",
                          "Manufacturer data","Seader & Henley","N_theor × HETP",
                          "GPDC method","Eckert","Design × flood",
                          "Leva correlation","ΔP/m × Z","Z + disengagement"]
        }
        st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
