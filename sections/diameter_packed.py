"""sections/diameter_packed.py — Column Diameter for Packed Columns (GPDC method)"""
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd
from thermodynamics.thermo_engine import binary_mixture_props

PACKINGS = {
    "Raschig Rings 25mm":  {"Fp": 512, "HETP_base": 0.50},
    "Raschig Rings 50mm":  {"Fp": 187, "HETP_base": 0.70},
    "Pall Rings 25mm":     {"Fp": 157, "HETP_base": 0.35},
    "Pall Rings 50mm":     {"Fp":  66, "HETP_base": 0.50},
    "Berl Saddles 25mm":   {"Fp": 240, "HETP_base": 0.45},
    "Mellapak 250Y":       {"Fp":  33, "HETP_base": 0.25},
    "Mellapak 500Y":       {"Fp":  45, "HETP_base": 0.15},
    "Flexipac 2Y":         {"Fp":  29, "HETP_base": 0.28},
}

def render():
    st.markdown("""
    <div class="section-header">
        <h1>📐 Column Diameter — Packed Column</h1>
        <p>GPDC (Generalized Pressure Drop Correlation) method — flooding velocity and diameter for packed beds.</p>
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

    col_type = st.session_state.get("column_type", None)
    if col_type == "tray":
        st.markdown("""
        <div class="warn-panel">
        ⚠️ <strong>Tray Column selected.</strong>
        This section uses GPDC method for packed columns.
        For your tray column → use <b>📐 Column Diameter</b> (Fair method).
        <i>You can still view this section for reference or comparison.</i>
        </div>
        """, unsafe_allow_html=True)
    elif col_type == "packed":
        st.markdown("""
        <div class="success-panel">
        ✅ <strong>Packed Column selected</strong> — GPDC method is correct for your design.
        </div>
        """, unsafe_allow_html=True)

    feed     = st.session_state.get("feed", {})
    shortcut = st.session_state.get("shortcut", {})
    thermo   = st.session_state.get("thermo", {})
    if not feed or not shortcut:
        st.warning("⚠️ Complete Feed Specifications and Shortcut Design first.")
        return

    R     = shortcut.get("R", 2.0)
    D_mol = shortcut.get("D", feed.get("F", 100) * 0.5)
    V_mol = (R + 1) * D_mol   # kmol/h vapour flow
    light = feed.get("light", "Benzene")
    heavy = feed.get("heavy", "Toluene")
    x_D = feed.get("x_D", 0.95)
    dist_props = feed.get("distillate_props") or thermo.get("distillate_props") or binary_mixture_props(light, heavy, x_D)

    st.markdown("""
    <div class="formula-box">
        <div class="formula-title">GPDC Method — Packed Column Flooding Velocity</div>
        <b>Step 1</b> — Flow parameter: F_lv = (L/V) × √(ρ_V / ρ_L)<br>
        <b>Step 2</b> — From GPDC chart: read C_s at flooding<br>
        <b>Step 3</b> — u_flood = C_s × √[(ρ_L − ρ_V) / ρ_V] / √F_p<br>
        <b>Step 4</b> — u_op = f × u_flood &nbsp;|&nbsp; A_col = Q_V / u_op &nbsp;|&nbsp; D = √(4A/π)
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📐 Diameter Calculation", "📋 Summary"])

    with tab1:
        c1, c2, c3 = st.columns(3)
        with c1:
            packing = st.selectbox("Packing Type", list(PACKINGS.keys()))
            Fp = PACKINGS[packing]["Fp"]
            st.markdown(f'<div class="result-box"><div class="label">Packing Factor Fp</div>'
                        f'<span class="value">{Fp}</span><span class="unit"> m⁻¹</span></div>',
                        unsafe_allow_html=True)
        with c2:
            rho_L = st.number_input("Liquid Density ρ_L [kg/m³]",
                value=float(feed.get("rho_L_distillate", dist_props.get("rho_L", 850.0))),
                min_value=400.0, max_value=1500.0, step=5.0)
            MW_avg = st.number_input("Vapour MW avg [g/mol]",
                value=float(dist_props.get("MW", 80.0)), min_value=10.0, max_value=500.0, step=1.0)
        with c3:
            T_K   = st.number_input("Temperature [K]",
                value=float(round(thermo.get("T_bubble_D", feed.get("T_feed", 80.0)) + 273.15, 1)),
                min_value=200.0, max_value=700.0, step=1.0)
            P_bar = st.number_input("Pressure [bar]", value=float(feed.get("P_col_bar", 1.013)),
                                     min_value=0.01, max_value=100.0, step=0.01, format="%.4f")
            f_flood = st.slider("Flooding fraction f", 0.55, 0.80, 0.70, 0.01,
                                 help="Packed columns: 65–75% (lower than tray columns 75–85%)")

        # Vapour density
        rho_V = (P_bar * 1e5 * MW_avg / 1000) / (8.314 * T_K)

        # L/V ratio (molar) — approximate from R
        LV_ratio = R / (R + 1)

        # Flow parameter Flv
        Flv = LV_ratio * np.sqrt(rho_V / rho_L)

        # Cs from GPDC (simplified Leva-Strigle correlation)
        # log(Cs√Fp) vs log(Flv) — at flooding
        log_Flv = np.log10(max(Flv, 1e-4))
        # GPDC flooding line approx: log(Cs*sqrt(Fp)) = -1.668 - 1.085*Flv - 0.297*Flv^2
        log_CsFp05 = -1.668 - 1.085 * log_Flv - 0.297 * log_Flv**2
        Cs_flood_Fp = 10 ** log_CsFp05
        u_flood = Cs_flood_Fp / np.sqrt(Fp) * np.sqrt((rho_L - rho_V) / rho_V)
        u_op    = f_flood * u_flood

        # Volumetric vapour flow
        Q_V_m3s = (V_mol * MW_avg / 1000) / (rho_V * 3600)
        A_col   = Q_V_m3s / u_op
        D_calc  = np.sqrt(4 * A_col / np.pi)

        # Round to standard sizes
        std_sizes = [0.3,0.4,0.5,0.6,0.8,1.0,1.2,1.4,1.6,1.8,2.0,2.4,2.8,3.0,3.2,3.6,4.0]
        D_std = next((d for d in std_sizes if d >= D_calc), std_sizes[-1])

        st.markdown(f"""
        <div class="formula-box" style="border-left:4px solid #f59e0b;">
            <div class="formula-title">✏️ Sample Calculation — Step by Step</div>
            V = (R+1)×D = ({R:.3f}+1)×{D_mol:.2f} = <b>{V_mol:.2f} kmol/h</b><br>
            ρ_V = P×MW / (R_g×T) = {P_bar}×10⁵×{MW_avg}/1000 / (8.314×{T_K}) = <b>{rho_V:.4f} kg/m³</b><br>
            L/V = R/(R+1) = {R:.3f}/{R+1:.3f} = <b>{LV_ratio:.4f}</b><br>
            F_lv = (L/V)×√(ρ_V/ρ_L) = {LV_ratio:.4f}×√({rho_V:.4f}/{rho_L}) = <b>{Flv:.5f}</b><br>
            log(Cs√Fp) = −1.668 − 1.085×log(F_lv) − 0.297×log(F_lv)² = <b>{log_CsFp05:.4f}</b><br>
            u_flood = 10^{log_CsFp05:.4f} / √{Fp} × √((ρ_L−ρ_V)/ρ_V) = <b>{u_flood:.4f} m/s</b><br>
            u_op = {f_flood}×{u_flood:.4f} = <b>{u_op:.4f} m/s</b><br>
            Q_V = {V_mol:.2f}×{MW_avg}/1000 / ({rho_V:.4f}×3600) = <b>{Q_V_m3s:.5f} m³/s</b><br>
            A = Q_V/u_op = {Q_V_m3s:.5f}/{u_op:.4f} = <b>{A_col:.4f} m²</b><br>
            D = √(4×{A_col:.4f}/π) = <b>{D_calc:.4f} m</b> → Standard: <b>{D_std} m</b>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("ρ_V (vapour density)", f"{rho_V:.4f} kg/m³")
        c2.metric("F_lv (flow param)", f"{Flv:.5f}")
        c3.metric("u_flood", f"{u_flood:.4f} m/s")
        c4.metric("u_op", f"{u_op:.4f} m/s")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Q_V (vapour flow)", f"{Q_V_m3s:.5f} m³/s")
        c2.metric("Column Area A", f"{A_col:.4f} m²")
        c3.metric("D (calculated)", f"{D_calc:.4f} m")
        c4.metric("D (standard)", f"{D_std} m")

        # Sensitivity: D vs flooding fraction
        ff_arr = np.linspace(0.55, 0.80, 30)
        D_arr  = []
        for ff in ff_arr:
            u_op_i = ff * u_flood
            A_i    = Q_V_m3s / u_op_i
            D_arr.append(np.sqrt(4*A_i/np.pi))
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=ff_arr, y=D_arr, mode="lines+markers",
                                  line=dict(color="#22c55e", width=3.2),
                                  marker=dict(size=6, color="#f59e0b", line=dict(color="#f8fbff", width=1))))
        fig.add_vline(x=f_flood, line_dash="dot", line_color="#f59e0b", line_width=3,
                       annotation_text=f"f={f_flood}", annotation_font_color="#f59e0b")
        fig.update_layout(template="plotly_dark", paper_bgcolor="#0a0e14", plot_bgcolor="#111827",
                           font=dict(family="Barlow", color="#e2e8f0"),
                           xaxis=dict(title="Flooding fraction f", gridcolor="#1e3a5f"),
                           yaxis=dict(title="Column Diameter D [m]", gridcolor="#1e3a5f"),
                           title=dict(text="Packed Column Diameter vs Flooding Fraction",
                                      font=dict(color="#f8d477", size=19)),
                           height=340, margin=dict(t=48))
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        df = pd.DataFrame({
            "Parameter": ["Packing type","Packing factor Fp","V (vapour flow)","ρ_V","ρ_L",
                           "L/V ratio","Flow parameter F_lv","u_flood","Flooding fraction f",
                           "u_op","Q_V","Column area A","D (calculated)","D (standard)"],
            "Value":     [packing, f"{Fp}", f"{V_mol:.2f}", f"{rho_V:.4f}", f"{rho_L:.1f}",
                          f"{LV_ratio:.4f}", f"{Flv:.5f}", f"{u_flood:.4f}", f"{f_flood:.2f}",
                          f"{u_op:.4f}", f"{Q_V_m3s:.5f}", f"{A_col:.4f}",
                          f"{D_calc:.4f}", f"{D_std}"],
            "Unit":      ["—","m⁻¹","kmol/h","kg/m³","kg/m³",
                          "—","—","m/s","—","m/s","m³/s","m²","m","m"]
        })
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("<div class='eng-divider'></div>", unsafe_allow_html=True)
    if st.button("💾 Save Packed Diameter Results", type="primary"):
        st.session_state.diameter = {
            "D_column_std_m":   D_std,
            "D_column_m":       round(D_calc, 4),
            "u_flood_m_s":      round(u_flood, 4),
            "u_op_m_s":         round(u_op, 4),
            "A_col_m2":         round(A_col, 4),
            "rho_V":            round(rho_V, 4),
            "rho_L":            rho_L,
            "flood_fraction":   f_flood,
            "V_molar":          V_mol,
            "MW_avg":           MW_avg,
            "packing_type":     packing,
            "Fp":               Fp,
            "column_mode":      "packed",
        }
        st.success(f"✅ Packed diameter saved: D = {D_std} m. Proceed to 📏 Column Height (Packed).")
