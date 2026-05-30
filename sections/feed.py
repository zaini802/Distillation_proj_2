"""sections/feed.py — Feed Specifications"""
import streamlit as st
import pandas as pd
from thermodynamics.thermo_engine import (
    list_components, get_component_props,
    bubble_point_T, dew_point_T, feed_q_value, antoine_pvap,
    binary_mixture_props
)
from calculations.distillation_calc import material_balance


def render():
    st.markdown("""
    <div class="section-header">
        <h1>📥 Feed Specifications</h1>
        <p>Define binary component system, feed conditions, product purity targets, and compute overall material balance.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <style>
    /* Feed page readability polish */
    .eng-card {
        background: linear-gradient(135deg, #0d1b2e 0%, #0a1422 100%) !important;
        border-color: rgba(125, 211, 252, 0.42) !important;
        box-shadow: inset 0 0 0 1px rgba(14,165,233,0.06), 0 10px 28px rgba(0,0,0,0.18);
    }
    .eng-card h3 {
        color: #f8d477 !important;
        text-shadow: 0 0 12px rgba(248, 212, 119, 0.22);
    }
    .result-box {
        background: linear-gradient(135deg, #102238 0%, #0a1626 100%) !important;
        border: 1px solid rgba(125, 211, 252, 0.48) !important;
        box-shadow: inset 0 0 0 1px rgba(14,165,233,0.05), 0 8px 20px rgba(0,0,0,0.16);
    }
    .result-box .label {
        color: #eaf6ff !important;
        opacity: 1 !important;
        font-size: 0.78rem !important;
        font-weight: 800 !important;
        letter-spacing: 1.4px !important;
    }
    .result-box .value {
        color: #22d3ee !important;
        text-shadow: 0 0 14px rgba(34,211,238,0.24);
    }
    .result-box .unit {
        color: #dbeafe !important;
        font-weight: 700 !important;
    }
    [data-testid="stWidgetLabel"] p,
    [data-testid="stNumberInput"] label p,
    [data-testid="stSelectbox"] label p {
        color: #dbeafe !important;
        font-weight: 700 !important;
    }
    div[data-baseweb="input"] input,
    div[data-baseweb="select"] div {
        color: #f8fafc !important;
        border-color: rgba(125,211,252,0.45) !important;
    }
    .success-panel,
    .info-panel {
        color: #d7fbe8 !important;
        border-color: rgba(74,222,128,0.42) !important;
    }
    .formula-box {
        color: #dbeafe !important;
        border-color: rgba(125,211,252,0.42) !important;
    }
    .formula-box .formula-title {
        color: #f8fafc !important;
        font-weight: 800 !important;
    }
    .calc-sheet {
        background:
            linear-gradient(135deg, rgba(15, 23, 42, 0.96), rgba(8, 16, 30, 0.98)),
            repeating-linear-gradient(0deg, transparent 0 31px, rgba(125,211,252,0.04) 32px);
        border: 1px solid rgba(125, 211, 252, 0.45) !important;
        border-left: 4px solid #22d3ee !important;
        border-radius: 10px !important;
        padding: 18px 20px !important;
        color: #dbeafe !important;
        font-family: 'Share Tech Mono', monospace;
    }
    .calc-title {
        color: #f8d477;
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 1.05rem;
        font-weight: 800;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 14px;
        padding-bottom: 8px;
        border-bottom: 1px solid rgba(125,211,252,0.24);
        text-shadow: 0 0 12px rgba(248, 212, 119, 0.22);
    }
    .calc-row {
        border-radius: 8px;
        padding: 10px 12px;
        margin: 9px 0;
        border: 1px solid rgba(148,163,184,0.18);
        line-height: 1.65;
    }
    .calc-formula { background: rgba(14,165,233,0.10); border-left: 3px solid #38bdf8; }
    .calc-given { background: rgba(168,85,247,0.10); border-left: 3px solid #c084fc; }
    .calc-work { background: rgba(148,163,184,0.08); border-left: 3px solid #94a3b8; }
    .calc-sub { background: rgba(245,158,11,0.10); border-left: 3px solid #fbbf24; }
    .calc-answer { background: rgba(34,197,94,0.12); border-left: 3px solid #22c55e; }
    .calc-verify { background: rgba(20,184,166,0.10); border-left: 3px solid #2dd4bf; }
    .calc-tag {
        display: inline-block;
        min-width: 118px;
        color: #f8fafc;
        font-family: 'Barlow Condensed', sans-serif;
        font-weight: 800;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    .calc-expr {
        color: #dbeafe;
        font-weight: 700;
    }
    .calc-line {
        color: #c7e5ff;
        margin: 3px 0 3px 32px;
    }
    .calc-equation {
        color: #7dd3fc;
        font-weight: 800;
    }
    .calc-number {
        color: #fbbf24;
        font-weight: 800;
    }
    .calc-final {
        color: #86efac;
        font-weight: 900;
        font-size: 1.05rem;
        text-shadow: 0 0 12px rgba(34,197,94,0.18);
    }
    </style>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["⚗️ Components & Feed", "🎯 Product Specifications", "📊 Material Balance"])

    components = list_components()

    # ── TAB 1: Components & Feed ──────────────────────────────
    with tab1:
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown('<div class="eng-card"><h3>🔵 Light Component (More Volatile)</h3>', unsafe_allow_html=True)
            light = st.selectbox("Light Component", components,
                                  index=components.index("Benzene") if "Benzene" in components else 0,
                                  key="feed_light_sel")
            props_l = get_component_props(light)
            if props_l:
                st.markdown(f"""
                <div class="result-box">
                    <div class="label">Molecular Weight</div>
                    <span class="value">{props_l['MW']}</span><span class="unit"> g/mol</span>
                </div>
                <div class="result-box">
                    <div class="label">Normal Boiling Point</div>
                    <span class="value">{props_l['Tb']}</span><span class="unit"> °C</span>
                </div>
                <div class="result-box">
                    <div class="label">Critical Temperature</div>
                    <span class="value">{props_l['Tc']}</span><span class="unit"> K</span>
                </div>
                <div class="result-box">
                    <div class="label">Critical Pressure</div>
                    <span class="value">{props_l['Pc']}</span><span class="unit"> bar</span>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_r:
            st.markdown('<div class="eng-card"><h3>🔴 Heavy Component (Less Volatile)</h3>', unsafe_allow_html=True)
            available_heavy = [c for c in components if c != light]
            default_heavy = "Toluene" if "Toluene" in available_heavy else available_heavy[0]
            heavy = st.selectbox("Heavy Component", available_heavy,
                                  index=available_heavy.index(default_heavy),
                                  key="feed_heavy_sel")
            props_h = get_component_props(heavy)
            if props_h:
                st.markdown(f"""
                <div class="result-box">
                    <div class="label">Molecular Weight</div>
                    <span class="value">{props_h['MW']}</span><span class="unit"> g/mol</span>
                </div>
                <div class="result-box">
                    <div class="label">Normal Boiling Point</div>
                    <span class="value">{props_h['Tb']}</span><span class="unit"> °C</span>
                </div>
                <div class="result-box">
                    <div class="label">Critical Temperature</div>
                    <span class="value">{props_h['Tc']}</span><span class="unit"> K</span>
                </div>
                <div class="result-box">
                    <div class="label">Critical Pressure</div>
                    <span class="value">{props_h['Pc']}</span><span class="unit"> bar</span>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<div class='eng-divider'></div>", unsafe_allow_html=True)
        st.markdown("### Feed Stream Conditions")

        c1, c2, c3 = st.columns(3)
        with c1:
            F     = st.number_input("Feed Flow Rate F [kmol/h]", min_value=1.0, max_value=10000.0, value=100.0, step=1.0)
            z_F   = st.number_input("Feed Mole Fraction zF (light)", min_value=0.01, max_value=0.99, value=0.50, step=0.01, format="%.3f")
        with c2:
            T_feed = st.number_input("Feed Temperature [°C]", min_value=-50.0, max_value=300.0, value=80.0, step=1.0)
            P_col_mmHg = st.number_input("Column Pressure [mmHg]", min_value=100.0, max_value=7600.0, value=760.0, step=10.0)
        with c3:
            feed_cond = st.selectbox("Feed Condition (q)", [
                "Saturated Liquid", "Saturated Vapor",
                "Subcooled Liquid", "Superheated Vapor", "Partial Vapor (50%)"
            ])
            P_col_bar = round(P_col_mmHg * 0.00133322, 4)
            st.markdown(f"""
            <div class="result-box">
                <div class="label">Column Pressure</div>
                <span class="value">{P_col_bar}</span><span class="unit"> bar</span>
            </div>
            <div class="result-box">
                <div class="label">Pressure in atm</div>
                <span class="value">{round(P_col_mmHg/760,4)}</span><span class="unit"> atm</span>
            </div>
            """, unsafe_allow_html=True)

        # Compute bubble/dew point at feed
        try:
            T_bub = bubble_point_T(light, heavy, z_F, P_col_mmHg)
            T_dew = dew_point_T(light, heavy, z_F, P_col_mmHg)
            mix_feed_props = binary_mixture_props(light, heavy, z_F)
            q_val = feed_q_value(
                feed_cond, T_feed, T_bub, T_dew,
                Cp_L=mix_feed_props["Cp_L"],
                lambda_vap=mix_feed_props["Hvap"],
            )
            st.markdown(f"""
            <div class="success-panel">
            ✅ <strong>Feed Thermodynamic State:</strong><br>
            Bubble Point = <strong>{T_bub:.2f} °C</strong> &nbsp;|&nbsp;
            Dew Point = <strong>{T_dew:.2f} °C</strong> &nbsp;|&nbsp;
            q-value = <strong>{q_val:.4f}</strong> ({feed_cond})
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <div class="info-panel">
            🧪 <strong>Database-based feed properties:</strong>
            ρL = <strong>{mix_feed_props['rho_L']} kg/m³</strong> &nbsp;|&nbsp;
            μL = <strong>{mix_feed_props['mu_L']} mPa·s</strong> &nbsp;|&nbsp;
            CpL = <strong>{mix_feed_props['Cp_L']} J/mol·K</strong> &nbsp;|&nbsp;
            Hvap = <strong>{mix_feed_props['Hvap']} J/mol</strong> &nbsp;|&nbsp;
            σ = <strong>{mix_feed_props['sigma']} N/m</strong>
            </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            T_bub, T_dew, q_val = T_feed, T_feed + 10, 1.0
            mix_feed_props = binary_mixture_props(light, heavy, z_F)
            st.warning(f"⚠️ Could not compute bubble/dew point: {e}")

    # ── TAB 2: Product Specifications ─────────────────────────
    with tab2:
        st.markdown("### 🎯 Separation Targets")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="eng-card"><h3>Distillate Specification (Top Product)</h3>', unsafe_allow_html=True)
            x_D = st.number_input("Distillate Purity xD (light)", min_value=0.50, max_value=0.9999, value=0.95, step=0.005, format="%.4f")
            st.markdown(f"""
            <div class="result-box">
                <div class="label">Heavy Component in Distillate</div>
                <span class="value">{round(1-x_D,4)}</span><span class="unit"> mol/mol</span>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="eng-card"><h3>Bottoms Specification (Bottom Product)</h3>', unsafe_allow_html=True)
            x_B = st.number_input("Bottoms Purity xB (light)", min_value=0.0001, max_value=0.50, value=0.05, step=0.005, format="%.4f")
            st.markdown(f"""
            <div class="result-box">
                <div class="label">Heavy Component in Bottoms</div>
                <span class="value">{round(1-x_B,4)}</span><span class="unit"> mol/mol</span>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Feasibility check
        st.markdown("### Feasibility Check")
        errs = []
        if x_D <= x_B:
            errs.append("xD must be greater than xB")
        if not (x_B < z_F < x_D):
            errs.append("Feed zF must be between xB and xD")
        if light == heavy:
            errs.append("Light and Heavy components must be different")
        try:
            alpha_check = antoine_pvap(light, T_feed) / antoine_pvap(heavy, T_feed)
            if alpha_check < 1.05:
                errs.append(f"Relative volatility α = {alpha_check:.3f} too low (< 1.05) — check component order")
        except:
            pass

        if errs:
            for e in errs:
                st.error(f"❌ {e}")
        else:
            st.markdown("""
            <div class="success-panel">
            ✅ <strong>All specifications are feasible.</strong> Separation is thermodynamically achievable.
            </div>
            """, unsafe_allow_html=True)

    # ── TAB 3: Material Balance ───────────────────────────────
    with tab3:
        try:
            if x_D > x_B and x_B < z_F < x_D:
                mb = material_balance(F, z_F, x_D, x_B)
                MW_l = props_l["MW"] if props_l else 78.0
                MW_h = props_h["MW"] if props_h else 92.0

                # ── Step-by-step formula display ──────────────
                st.markdown("### 📐 Step-by-Step Calculation")

                st.markdown(f"""
                <div class="formula-box calc-sheet">
                    <div class="calc-title">Step 1 — Overall Molar Balance</div>
                    <div class="calc-row calc-formula">
                        <span class="calc-tag">Formula</span>
                        <span class="calc-equation">F = D + B</span>
                    </div>
                    <div class="calc-row calc-given">
                        <span class="calc-tag">Given Data</span>
                        <span class="calc-expr">F = <span class="calc-number">{F}</span> kmol/h, zF = <span class="calc-number">{z_F}</span>, xD = <span class="calc-number">{x_D}</span>, xB = <span class="calc-number">{x_B}</span></span>
                    </div>
                    <div class="calc-row calc-work">
                        <span class="calc-tag">Derivation</span>
                        <div class="calc-line">F·zF = D·xD + B·xB</div>
                        <div class="calc-line">F·zF = D·xD + (F − D)·xB</div>
                        <div class="calc-line">F·zF − F·xB = D·(xD − xB)</div>
                        <div class="calc-line"><span class="calc-equation">D = F × (zF − xB) / (xD − xB)</span></div>
                    </div>
                    <div class="calc-row calc-sub">
                        <span class="calc-tag">Substitution</span>
                        <div class="calc-line">D = {F} × ({z_F} − {x_B}) / ({x_D} − {x_B})</div>
                        <div class="calc-line">D = {F} × <span class="calc-number">{round(z_F - x_B, 4)}</span> / <span class="calc-number">{round(x_D - x_B, 4)}</span></div>
                    </div>
                    <div class="calc-row calc-answer">
                        <span class="calc-tag">Final Answer</span>
                        <span class="calc-final">D = {mb['D']} kmol/h</span>
                        <div class="calc-line">B = F − D = {F} − {mb['D']} = <span class="calc-final">B = {mb['B']} kmol/h</span></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div class="formula-box calc-sheet">
                    <div class="calc-title">Step 2 — Component Balance Verification</div>
                    <div class="calc-row calc-formula">
                        <span class="calc-tag">Light Balance</span>
                        <span class="calc-equation">F·zF = D·xD + B·xB</span>
                    </div>
                    <div class="calc-row calc-sub">
                        <span class="calc-tag">Substitution</span>
                        <div class="calc-line">{F} × {z_F} = {mb['D']} × {x_D} + {mb['B']} × {x_B}</div>
                        <div class="calc-line"><span class="calc-number">{round(F*z_F,3)}</span> = {round(mb['D']*x_D,3)} + {round(mb['B']*x_B,3)}</div>
                    </div>
                    <div class="calc-row calc-verify">
                        <span class="calc-tag">Verified</span>
                        <span class="calc-final">{round(F*z_F,3)} = {round(mb['D']*x_D + mb['B']*x_B,3)} ✓</span>
                    </div>
                    <div class="calc-row calc-formula">
                        <span class="calc-tag">Heavy Balance</span>
                        <span class="calc-equation">F·(1 − zF) = D·(1 − xD) + B·(1 − xB)</span>
                    </div>
                    <div class="calc-row calc-sub">
                        <span class="calc-tag">Substitution</span>
                        <div class="calc-line">{F} × {round(1-z_F,4)} = {mb['D']} × {round(1-x_D,4)} + {mb['B']} × {round(1-x_B,4)}</div>
                        <div class="calc-line"><span class="calc-number">{round(F*(1-z_F),3)}</span> = {round(mb['D']*(1-x_D),3)} + {round(mb['B']*(1-x_B),3)}</div>
                    </div>
                    <div class="calc-row calc-verify">
                        <span class="calc-tag">Verified</span>
                        <span class="calc-final">{round(F*(1-z_F),3)} = {round(mb['D']*(1-x_D) + mb['B']*(1-x_B),3)} ✓</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div class="formula-box calc-sheet">
                    <div class="calc-title">Step 3 — Recovery Calculations</div>
                    <div class="calc-row calc-formula">
                        <span class="calc-tag">Distillate</span>
                        <span class="calc-equation">Recovery_D = (D × xD) / (F × zF) × 100</span>
                    </div>
                    <div class="calc-row calc-sub">
                        <span class="calc-tag">Substitution</span>
                        <div class="calc-line">Recovery_D = ({mb['D']} × {x_D}) / ({F} × {z_F}) × 100</div>
                        <div class="calc-line">Recovery_D = <span class="calc-number">{round(mb['D']*x_D,3)}</span> / <span class="calc-number">{round(F*z_F,3)}</span> × 100</div>
                    </div>
                    <div class="calc-row calc-answer">
                        <span class="calc-tag">Final Answer</span>
                        <span class="calc-final">{mb['recovery_distillate_pct']}% light component recovered in distillate</span>
                    </div>
                    <div class="calc-row calc-formula">
                        <span class="calc-tag">Bottoms</span>
                        <span class="calc-equation">Recovery_B = (B × (1 − xB)) / (F × (1 − zF)) × 100</span>
                    </div>
                    <div class="calc-row calc-sub">
                        <span class="calc-tag">Substitution</span>
                        <div class="calc-line">Recovery_B = ({mb['B']} × {round(1-x_B,4)}) / ({F} × {round(1-z_F,4)}) × 100</div>
                        <div class="calc-line">Recovery_B = <span class="calc-number">{round(mb['B']*(1-x_B),3)}</span> / <span class="calc-number">{round(F*(1-z_F),3)}</span> × 100</div>
                    </div>
                    <div class="calc-row calc-answer">
                        <span class="calc-tag">Final Answer</span>
                        <span class="calc-final">{mb['recovery_bottoms_pct']}% heavy component recovered in bottoms</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div class="formula-box calc-sheet">
                    <div class="calc-title">Step 4 — Mass Flow Rates (Molar → Mass)</div>
                    <div class="calc-row calc-formula">
                        <span class="calc-tag">Basis</span>
                        <span class="calc-equation">MW_avg = x·MW_light + (1 − x)·MW_heavy</span>
                    </div>
                    <div class="calc-row calc-given">
                        <span class="calc-tag">Mass Formula</span>
                        <span class="calc-equation">ṁ = Flow [kmol/h] × MW_avg [kg/kmol]</span>
                    </div>
                    <div class="calc-row calc-sub">
                        <span class="calc-tag">Feed</span>
                        <div class="calc-line">MW_F = {z_F} × {MW_l} + {round(1-z_F,4)} × {MW_h} = <span class="calc-number">{round(z_F*MW_l+(1-z_F)*MW_h,2)} g/mol</span></div>
                        <div class="calc-line">ṁ_F = {F} × {round(z_F*MW_l+(1-z_F)*MW_h,2)} = <span class="calc-final">{round(F*(z_F*MW_l+(1-z_F)*MW_h),1)} kg/h</span></div>
                    </div>
                    <div class="calc-row calc-sub">
                        <span class="calc-tag">Distillate</span>
                        <div class="calc-line">MW_D = {x_D} × {MW_l} + {round(1-x_D,4)} × {MW_h} = <span class="calc-number">{round(x_D*MW_l+(1-x_D)*MW_h,2)} g/mol</span></div>
                        <div class="calc-line">ṁ_D = {mb['D']} × {round(x_D*MW_l+(1-x_D)*MW_h,2)} = <span class="calc-final">{round(mb['D']*(x_D*MW_l+(1-x_D)*MW_h),1)} kg/h</span></div>
                    </div>
                    <div class="calc-row calc-sub">
                        <span class="calc-tag">Bottoms</span>
                        <div class="calc-line">MW_B = {x_B} × {MW_l} + {round(1-x_B,4)} × {MW_h} = <span class="calc-number">{round(x_B*MW_l+(1-x_B)*MW_h,2)} g/mol</span></div>
                        <div class="calc-line">ṁ_B = {mb['B']} × {round(x_B*MW_l+(1-x_B)*MW_h,2)} = <span class="calc-final">{round(mb['B']*(x_B*MW_l+(1-x_B)*MW_h),1)} kg/h</span></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # ── Results metrics ────────────────────────────
                st.markdown("### ⚖️ Results Summary")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Feed F", f"{mb['F']} kmol/h")
                c2.metric("Distillate D", f"{mb['D']} kmol/h")
                c3.metric("Bottoms B", f"{mb['B']} kmol/h")
                c4.metric("D/F Ratio", f"{mb['D_over_F']}")

                st.markdown(f"""
                <div class="success-panel">
                ✅ <strong>Balance Verified:</strong>
                D + B = {mb['D']} + {mb['B']} = {round(mb['D']+mb['B'],3)} kmol/h = F ✓<br>
                {light} recovery (distillate): <strong>{mb['recovery_distillate_pct']}%</strong> &nbsp;|&nbsp;
                {heavy} recovery (bottoms): <strong>{mb['recovery_bottoms_pct']}%</strong>
                </div>
                """, unsafe_allow_html=True)

                # ── Stream table ───────────────────────────────
                st.markdown("#### Stream Table")
                df = pd.DataFrame({
                    "Stream":              ["Feed (F)", "Distillate (D)", "Bottoms (B)"],
                    "Flow [kmol/h]":       [F, mb['D'], mb['B']],
                    f"x_{light} (light)":  [z_F, x_D, x_B],
                    f"x_{heavy} (heavy)":  [round(1-z_F,4), round(1-x_D,4), round(1-x_B,4)],
                    f"{light} [kmol/h]":   [round(F*z_F,3), round(mb['D']*x_D,3), round(mb['B']*x_B,3)],
                    f"{heavy} [kmol/h]":   [round(F*(1-z_F),3), round(mb['D']*(1-x_D),3), round(mb['B']*(1-x_B),3)],
                    "MW avg [g/mol]":      [round(z_F*MW_l+(1-z_F)*MW_h,2),
                                            round(x_D*MW_l+(1-x_D)*MW_h,2),
                                            round(x_B*MW_l+(1-x_B)*MW_h,2)],
                    "Mass Flow [kg/h]":    [round(F*(z_F*MW_l+(1-z_F)*MW_h),1),
                                            round(mb['D']*(x_D*MW_l+(1-x_D)*MW_h),1),
                                            round(mb['B']*(x_B*MW_l+(1-x_B)*MW_h),1)],
                })
                st.dataframe(df, use_container_width=True, hide_index=True)

            else:
                st.warning("⚠️ Fix specification errors in Tab 1 & 2 to compute material balance.")
        except Exception as e:
            st.error(f"Material balance error: {e}")

    # ── Save Button ────────────────────────────────────────────
    st.markdown("<div class='eng-divider'></div>", unsafe_allow_html=True)
    col_btn, col_info = st.columns([1, 3])
    with col_btn:
        if st.button("💾 Save Feed Specifications", type="primary", use_container_width=True):
            if x_D > x_B and x_B < z_F < x_D:
                mix_feed_props = binary_mixture_props(light, heavy, z_F)
                mix_dist_props = binary_mixture_props(light, heavy, x_D)
                mix_bot_props = binary_mixture_props(light, heavy, x_B)
                st.session_state.feed = {
                    # Component keys (both naming conventions for compatibility)
                    "light": light,       "heavy": heavy,
                    "light_comp": light,  "heavy_comp": heavy,
                    # Feed data
                    "F": F, "z_F": z_F, "x_D": x_D, "x_B": x_B,
                    "T_feed": T_feed,
                    "P_col_mmHg": P_col_mmHg, "P_col_bar": P_col_bar,
                    "feed_condition": feed_cond,
                    "q": q_val,
                    "T_bubble_F": T_bub,
                    "T_dew_F": T_dew,
                    # Component properties
                    "MW_light": props_l.get("MW", 78),
                    "MW_heavy": props_h.get("MW", 92),
                    "Tb_light": props_l.get("Tb", 80),
                    "Tb_heavy": props_h.get("Tb", 110),
                    "Tc_light": props_l.get("Tc", 562),
                    "Tc_heavy": props_h.get("Tc", 592),
                    # Database-based advanced mixture defaults
                    "feed_props": mix_feed_props,
                    "distillate_props": mix_dist_props,
                    "bottoms_props": mix_bot_props,
                    "rho_L_feed": mix_feed_props["rho_L"],
                    "mu_L_feed": mix_feed_props["mu_L"],
                    "Cp_L_feed": mix_feed_props["Cp_L"],
                    "Hvap_feed": mix_feed_props["Hvap"],
                    "sigma_feed": mix_feed_props["sigma"],
                    "rho_L_distillate": mix_dist_props["rho_L"],
                    "mu_L_distillate": mix_dist_props["mu_L"],
                    "Cp_L_distillate": mix_dist_props["Cp_L"],
                    "Hvap_distillate": mix_dist_props["Hvap"],
                    "sigma_distillate": mix_dist_props["sigma"],
                    "rho_L_bottoms": mix_bot_props["rho_L"],
                    "mu_L_bottoms": mix_bot_props["mu_L"],
                    "Cp_L_bottoms": mix_bot_props["Cp_L"],
                    "Hvap_bottoms": mix_bot_props["Hvap"],
                    "sigma_bottoms": mix_bot_props["sigma"],
                }
                st.success("✅ Feed specifications saved! Proceed to **Thermodynamics DB** → **Shortcut Design**.")
            else:
                st.error("❌ Fix specification errors before saving.")
    with col_info:
        if st.session_state.feed:
            fd = st.session_state.feed
            st.markdown(f"""
            <div class="info-panel">
            📌 <strong>Saved:</strong>
            {fd.get('light')} / {fd.get('heavy')} &nbsp;|&nbsp;
            F = {fd.get('F')} kmol/h &nbsp;|&nbsp;
            zF = {fd.get('z_F')} &nbsp;|&nbsp;
            xD = {fd.get('x_D')} &nbsp;|&nbsp;
            xB = {fd.get('x_B')} &nbsp;|&nbsp;
            P = {fd.get('P_col_mmHg')} mmHg &nbsp;|&nbsp;
            q = {fd.get('q', '—')}
            </div>
            """, unsafe_allow_html=True)
