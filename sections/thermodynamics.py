"""sections/thermodynamics.py — Thermodynamics Database & VLE"""
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from sections.ai_assistant import _call_groq_chat
from thermodynamics.thermo_engine import (
    COMPONENT_DB, antoine_pvap, relative_volatility,
    avg_relative_volatility, generate_xy_curve,
    bubble_point_T, dew_point_T, y_from_x, vle_raoult,
    antoine_range_status, binary_mixture_props
)

VLE_MODELS = ["Raoult's Law", "Modified Raoult's Law", "Wilson Model", "NRTL Model"]

HYDROCARBONS = {
    "Methane", "Ethane", "Propane", "n-Butane", "n-Pentane", "n-Hexane",
    "n-Heptane", "n-Octane", "Benzene", "Toluene", "o-Xylene",
    "Ethylbenzene", "Cyclohexane"
}
ALCOHOLS = {"Methanol", "Ethanol", "n-Propanol", "Isopropanol"}
AQUEOUS = {"Water"}
SLIGHTLY_NONIDEAL = {
    "Acetone", "Ethyl Acetate", "Diethyl Ether", "Chloroform",
    "Carbon Tetra.", "Acetic Acid"
}


def _pair_key(light, heavy):
    return frozenset([light, heavy])


def _model_advisor(light, heavy):
    pair = {light, heavy}
    if pair <= HYDROCARBONS:
        return {
            "model": "Raoult's Law",
            "level": "Low",
            "color": "#22c55e",
            "reason": "Both components are non-polar hydrocarbons, so the liquid phase is close to ideal.",
        }
    if "Water" in pair and pair & ALCOHOLS:
        return {
            "model": "Wilson Model",
            "level": "High",
            "color": "#ef4444",
            "reason": "Alcohol-water pairs are highly non-ideal because hydrogen bonding changes liquid-phase activity.",
        }
    if "Water" in pair:
        return {
            "model": "NRTL Model",
            "level": "High",
            "color": "#ef4444",
            "reason": "Aqueous mixtures often show strong local-composition effects and may form azeotropes.",
        }
    if pair & SLIGHTLY_NONIDEAL or pair & ALCOHOLS:
        return {
            "model": "Modified Raoult's Law",
            "level": "Medium",
            "color": "#f59e0b",
            "reason": "At least one component is polar or associating, so activity coefficients should be included.",
        }
    return {
        "model": "Modified Raoult's Law",
        "level": "Medium",
        "color": "#f59e0b",
        "reason": "The pair is not clearly ideal; use activity coefficients for safer preliminary design.",
    }


def _default_model_params(light, heavy):
    defaults = {
        "A12": 0.25, "A21": 0.25,
        "L12": 0.90, "L21": 1.10,
        "tau12": 0.30, "tau21": 0.10, "alpha_nrtl": 0.30,
    }
    common = {
        _pair_key("Ethanol", "Water"): {
            "A12": 1.70, "A21": 0.95, "L12": 0.22, "L21": 0.60,
            "tau12": 1.20, "tau21": -0.25, "alpha_nrtl": 0.30,
        },
        _pair_key("Methanol", "Water"): {
            "A12": 1.25, "A21": 0.75, "L12": 0.34, "L21": 0.72,
            "tau12": 0.85, "tau21": -0.10, "alpha_nrtl": 0.30,
        },
        _pair_key("Acetone", "Water"): {
            "A12": 1.90, "A21": 1.10, "L12": 0.18, "L21": 0.75,
            "tau12": 1.35, "tau21": 0.20, "alpha_nrtl": 0.35,
        },
        _pair_key("Benzene", "Toluene"): {
            "A12": 0.04, "A21": 0.03, "L12": 0.98, "L21": 1.02,
            "tau12": 0.03, "tau21": 0.02, "alpha_nrtl": 0.30,
        },
    }
    return {**defaults, **common.get(_pair_key(light, heavy), {})}


def _activity_coefficients(x, model, params):
    x1 = np.clip(np.asarray(x, dtype=float), 1e-6, 1 - 1e-6)
    x2 = 1 - x1
    if model == "Raoult's Law":
        return np.ones_like(x1), np.ones_like(x1)

    if model == "Modified Raoult's Law":
        A12 = params.get("A12", 0.25)
        A21 = params.get("A21", 0.25)
        ln_g1 = x2**2 * (A12 + 2 * (A21 - A12) * x1)
        ln_g2 = x1**2 * (A21 + 2 * (A12 - A21) * x2)
        return np.exp(ln_g1), np.exp(ln_g2)

    if model == "Wilson Model":
        L12 = max(params.get("L12", 0.90), 1e-5)
        L21 = max(params.get("L21", 1.10), 1e-5)
        d = L12 / (x1 + L12 * x2) - L21 / (x2 + L21 * x1)
        ln_g1 = -np.log(x1 + L12 * x2) + x2 * d
        ln_g2 = -np.log(x2 + L21 * x1) - x1 * d
        return np.exp(ln_g1), np.exp(ln_g2)

    tau12 = params.get("tau12", 0.30)
    tau21 = params.get("tau21", 0.10)
    alpha = params.get("alpha_nrtl", 0.30)
    G12 = np.exp(-alpha * tau12)
    G21 = np.exp(-alpha * tau21)
    ln_g1 = x2**2 * (
        tau21 * (G21 / (x1 + x2 * G21))**2
        + tau12 * G12 / (x2 + x1 * G12)**2
    )
    ln_g2 = x1**2 * (
        tau12 * (G12 / (x2 + x1 * G12))**2
        + tau21 * G21 / (x1 + x2 * G21)**2
    )
    return np.exp(ln_g1), np.exp(ln_g2)


def _vle_model_curve(light, heavy, T_C, P_mmHg, model, params, x_arr):
    P1 = antoine_pvap(light, T_C)
    P2 = antoine_pvap(heavy, T_C)
    g1, g2 = _activity_coefficients(x_arr, model, params)
    numerator = x_arr * g1 * P1
    denominator = numerator + (1 - x_arr) * g2 * P2
    y = np.divide(numerator, denominator, out=np.zeros_like(x_arr), where=denominator > 0)
    alpha_eff = (g1 * P1) / np.maximum(g2 * P2, 1e-12)
    return np.clip(y, 0, 1), alpha_eff, g1, g2


def _model_formula_box(model, params):
    if model == "Raoult's Law":
        body = (
            "<b>Ideal liquid assumption:</b><br>"
            "γ<sub>1</sub> = γ<sub>2</sub> = 1<br>"
            "y<sub>1</sub> = x<sub>1</sub>P°<sub>1</sub> / "
            "[x<sub>1</sub>P°<sub>1</sub> + x<sub>2</sub>P°<sub>2</sub>]"
        )
    elif model == "Modified Raoult's Law":
        body = (
            "<b>Margules activity coefficients:</b><br>"
            "ln γ<sub>1</sub> = x<sub>2</sub>²[A12 + 2(A21 − A12)x<sub>1</sub>]<br>"
            "ln γ<sub>2</sub> = x<sub>1</sub>²[A21 + 2(A12 − A21)x<sub>2</sub>]<br>"
            f"A12 = <b>{params.get('A12', 0):.3f}</b>, "
            f"A21 = <b>{params.get('A21', 0):.3f}</b>"
        )
    elif model == "Wilson Model":
        body = (
            "<b>Wilson local-composition model:</b><br>"
            "ln γ<sub>1</sub> = −ln(x<sub>1</sub> + Λ12x<sub>2</sub>) "
            "+ x<sub>2</sub>[Λ12/(x<sub>1</sub>+Λ12x<sub>2</sub>) "
            "− Λ21/(x<sub>2</sub>+Λ21x<sub>1</sub>)]<br>"
            f"Λ12 = <b>{params.get('L12', 0):.3f}</b>, "
            f"Λ21 = <b>{params.get('L21', 0):.3f}</b>"
        )
    else:
        body = (
            "<b>Simplified NRTL model:</b><br>"
            "G12 = exp(−ατ12), G21 = exp(−ατ21), activity coefficients vary with liquid composition.<br>"
            f"τ12 = <b>{params.get('tau12', 0):.3f}</b>, "
            f"τ21 = <b>{params.get('tau21', 0):.3f}</b>, "
            f"α = <b>{params.get('alpha_nrtl', 0):.3f}</b>"
        )
    return (
        '<div class="formula-box thermo-calc-box">'
        f'<div class="formula-title">Selected VLE Model — {model}</div>'
        f'{body}<br><br>'
        '<b>Final VLE equation used in graph:</b><br>'
        'y<sub>1</sub> = x<sub>1</sub>γ<sub>1</sub>P°<sub>1</sub> / '
        '[x<sub>1</sub>γ<sub>1</sub>P°<sub>1</sub> + x<sub>2</sub>γ<sub>2</sub>P°<sub>2</sub>]'
        '</div><div class="thermo-calc-separator"></div>'
    )


def _merge_thermo_state(**updates):
    current = dict(st.session_state.get("thermo", {}))
    current.update(updates)
    st.session_state.thermo = current


def _metric_cards_html(cards, label_extra_class=""):
    html_cards = []
    for label, value, unit in cards:
        unit_html = f'<span class="thermo-metric-unit">{unit}</span>' if unit else ""
        html_cards.append(
            '<div class="thermo-metric-card">'
            f'<div class="thermo-metric-label {label_extra_class}">{label}</div>'
            f'<div class="thermo-metric-value">{value}{unit_html}</div>'
            '</div>'
        )
    return '<div class="thermo-metric-grid">' + ''.join(html_cards) + '</div>'


def _model_comparison_table_html(rows):
    body = []
    for row in rows:
        body.append(
            '<tr>'
            f'<td class="model-name">{row["Model"]}</td>'
            f'<td>{row["y @ x=0.3"]}</td>'
            f'<td>{row["y @ x=0.5"]}</td>'
            f'<td>{row["y @ x=0.7"]}</td>'
            f'<td class="suitable-system">{row["Suitable systems"]}</td>'
            '</tr>'
        )
    return (
        '<table class="thermo-model-table">'
        '<thead><tr>'
        '<th class="model-heading">Model</th>'
        '<th>y @ x=0.3</th>'
        '<th>y @ x=0.5</th>'
        '<th>y @ x=0.7</th>'
        '<th>Suitable systems</th>'
        '</tr></thead>'
        '<tbody>' + ''.join(body) + '</tbody></table>'
    )


def render():
    st.markdown("""
    <div class="section-header">
        <h1>🧪 Thermodynamics Database</h1>
        <p>Component properties, Antoine constants, VLE calculations, and relative volatility estimation.</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <style>
    .thermo-db-heading {
        color: #f8d477 !important;
        font-family: 'Barlow Condensed', sans-serif;
        font-weight: 900;
        letter-spacing: 0;
        text-shadow: 0 0 12px rgba(248, 212, 119, 0.22);
        margin: 0.35rem 0 1rem 0;
    }
    .thermo-component-label {
        color: #ff5b6e !important;
        font-weight: 900 !important;
        letter-spacing: 0.3px;
        margin: 0 0 0.4rem 0.1rem;
        text-shadow: 0 0 10px rgba(239, 68, 68, 0.22);
    }
    .thermo-vle-heading,
    .thermo-tab-heading {
        color: #f8d477 !important;
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 2.05rem !important;
        font-weight: 900 !important;
        letter-spacing: 0;
        line-height: 1.12;
        margin: 0.45rem 0 1rem 0;
        text-shadow: 0 0 14px rgba(248, 212, 119, 0.24);
    }
    .thermo-input-label {
        color: #ff5b6e !important;
        font-weight: 900 !important;
        letter-spacing: 0.2px;
        margin: 0 0 0.42rem 0.05rem;
        text-shadow: 0 0 10px rgba(239, 68, 68, 0.22);
    }
    .thermo-calc-box {
        color: #eaf6ff !important;
        background: linear-gradient(135deg, rgba(8, 14, 24, 0.99), rgba(15, 23, 42, 0.97)) !important;
        border: 1px solid rgba(0, 180, 216, 0.44) !important;
        border-left: 4px solid #00b4d8 !important;
        box-shadow: 0 0 0 1px rgba(255,255,255,0.03), 0 12px 28px rgba(0,0,0,0.18);
        font-size: 1.02rem !important;
        line-height: 1.75;
    }
    .thermo-calc-box b,
    .thermo-calc-box strong {
        color: #ffffff !important;
        font-weight: 900 !important;
    }
    .thermo-calc-box .formula-title {
        color: #f8d477 !important;
        font-size: 1.08rem !important;
        font-weight: 900 !important;
        letter-spacing: 0.2px;
        margin-bottom: 0.55rem;
    }
    .thermo-calc-box .thermo-model-title {
        color: #22c55e !important;
        text-shadow: 0 0 12px rgba(34, 197, 94, 0.24);
    }
    .thermo-calc-separator {
        border-top: 2px dotted rgba(248, 212, 119, 0.58);
        margin: 1.15rem 0 1.35rem 0;
        height: 1px;
    }
    .thermo-metric-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 1rem;
        margin: 1.05rem 0 0.3rem 0;
    }
    .thermo-metric-card {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.98), rgba(8, 14, 24, 0.98));
        border: 1px solid rgba(0, 180, 216, 0.48);
        border-radius: 8px;
        padding: 1rem 1.05rem;
        min-height: 118px;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.04), 0 10px 24px rgba(0,0,0,0.16);
    }
    .thermo-metric-label {
        color: #ffffff !important;
        font-size: 0.94rem;
        font-weight: 900;
        line-height: 1.3;
        margin-bottom: 0.55rem;
    }
    .thermo-metric-label-red {
        color: #ff5b6e !important;
        text-shadow: 0 0 10px rgba(239, 68, 68, 0.24);
    }
    .thermo-metric-value {
        color: #00d4ff;
        font-family: 'Share Tech Mono', monospace;
        font-size: clamp(1.7rem, 2.4vw, 2.55rem);
        font-weight: 900;
        letter-spacing: 0;
        line-height: 1.05;
        word-break: break-word;
        text-shadow: 0 0 14px rgba(0, 180, 216, 0.18);
    }
    .thermo-metric-unit {
        color: #dbeafe;
        font-family: 'Barlow', sans-serif;
        font-size: 0.86rem;
        font-weight: 800;
        margin-left: 0.2rem;
    }
    @media (max-width: 900px) {
        .thermo-metric-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
    }
    @media (max-width: 560px) {
        .thermo-metric-grid {
            grid-template-columns: 1fr;
        }
    }
    .thermo-model-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        margin-top: 1rem;
        overflow: hidden;
        border: 1px solid rgba(0, 180, 216, 0.45);
        border-radius: 8px;
        background: #071018;
        color: #f8fbff;
        font-size: 0.98rem;
    }
    .thermo-model-table th {
        background: #1b2028;
        color: #f8d477;
        font-weight: 900;
        text-align: left;
        padding: 0.78rem 0.75rem;
        border-bottom: 1px solid rgba(148, 163, 184, 0.25);
        border-right: 1px solid rgba(148, 163, 184, 0.18);
    }
    .thermo-model-table th.model-heading {
        color: #22c55e !important;
        text-shadow: 0 0 10px rgba(34, 197, 94, 0.22);
    }
    .thermo-model-table td {
        padding: 0.78rem 0.75rem;
        border-bottom: 1px solid rgba(148, 163, 184, 0.14);
        border-right: 1px solid rgba(148, 163, 184, 0.12);
        color: #f8fbff;
    }
    .thermo-model-table tr:last-child td {
        border-bottom: 0;
    }
    .thermo-model-table .model-name {
        color: #ffffff;
        font-weight: 900;
    }
    .thermo-model-table .suitable-system {
        color: #e7f0ff;
    }
    </style>
    """, unsafe_allow_html=True)

    feed = st.session_state.get("feed", {})
    if not feed:
        st.warning("⚠️ Complete **Feed Specifications** first to auto-load components.")
        light_default = "Benzene"; heavy_default = "Toluene"
    else:
        light_default = feed.get("light", "Benzene")
        heavy_default = feed.get("heavy", "Toluene")

    components = sorted(COMPONENT_DB.keys())
    P_mmHg = feed.get("P_col_mmHg", 760.0)
    T_feed  = feed.get("T_feed", 80.0)
    light = st.session_state.get("thermo_light", light_default)
    if light not in components:
        light = light_default if light_default in components else components[0]
    heavy = st.session_state.get("thermo_heavy", heavy_default)
    if heavy not in components or heavy == light:
        heavy = heavy_default if heavy_default in components and heavy_default != light else next(c for c in components if c != light)

    advisor = _model_advisor(light, heavy)
    _merge_thermo_state(
        light=light,
        heavy=heavy,
        suggested_vle_model=advisor["model"],
        nonideality_level=advisor["level"],
        model_advisor=advisor,
    )

    st.markdown(f"""
    <div class="formula-box" style="border-left:4px solid {advisor['color']}; background:linear-gradient(135deg, rgba(15,23,42,0.98), rgba(8,14,24,0.98));">
        <div class="formula-title">🧠 VLE Model Advisor — {light} / {heavy}</div>
        <b>Suggested model:</b> <span style="color:{advisor['color']}; font-weight:900;">{advisor['model']}</span>
        &nbsp;|&nbsp; <b>Non-ideality:</b> <span style="color:{advisor['color']}; font-weight:900;">{advisor['level']}</span><br>
        <b>Reason:</b> {advisor['reason']}
    </div>
    """, unsafe_allow_html=True)

    if st.button("Ask AI — Why this model?", key="thermo_ai_model_reason"):
        api_key = st.session_state.get("groq_api_key", "")
        if not api_key:
            st.warning("⚠️ Enter your Groq API key in the sidebar to activate this AI explanation.")
        else:
            prompt = (
                f"Explain in under 150 words why {advisor['model']} is appropriate for the "
                f"binary distillation pair {light}/{heavy}. Explain what non-ideality means "
                "physically for these components, and what happens if the wrong VLE model is chosen."
            )
            response = _call_groq_chat(
                api_key,
                [
                    {"role": "system", "content": "You are a concise chemical engineering VLE expert."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.35,
                max_tokens=220,
            )
            st.session_state["thermo_model_ai_response"] = response
            st.session_state["thermo_model_ai_pair"] = f"{light}/{heavy}"

    if st.session_state.get("thermo_model_ai_response") and st.session_state.get("thermo_model_ai_pair") == f"{light}/{heavy}":
        with st.expander("AI explanation — model selection", expanded=True):
            st.write(st.session_state["thermo_model_ai_response"])

    selected_vle_model = st.session_state.get("thermo_selected_vle_model", advisor["model"])
    if selected_vle_model == "Raoult's Law (Ideal)":
        selected_vle_model = "Raoult's Law"
    if selected_vle_model not in VLE_MODELS:
        selected_vle_model = advisor["model"]
    selected_model_params = _default_model_params(light, heavy)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Component Database", "📈 VLE Curve", "🌡️ Bubble/Dew Points", "⚡ Relative Volatility",
        "🌡️ T-x-y Diagram", "🧪 Models Comparison"
    ])

    # ── TAB 1: Component Database ─────────────────────────────
    with tab1:
        st.markdown('<h3 class="thermo-db-heading">🗄️ Built-in Component Database (24 Components)</h3>', unsafe_allow_html=True)
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown('<div class="thermo-component-label">Light Component</div>', unsafe_allow_html=True)
            light = st.selectbox("Light Component", components,
                                  index=components.index(light) if light in components else 0,
                                  key="thermo_light",
                                  label_visibility="collapsed")
        with col_r:
            heavy_opts = [c for c in components if c != light]
            default_h  = heavy if heavy in heavy_opts else heavy_opts[0]
            st.markdown('<div class="thermo-component-label">Heavy Component</div>', unsafe_allow_html=True)
            heavy = st.selectbox("Heavy Component", heavy_opts,
                                  index=heavy_opts.index(default_h),
                                  key="thermo_heavy",
                                  label_visibility="collapsed")

        c1, c2 = st.columns(2)
        for comp, col in [(light, c1), (heavy, c2)]:
            p = COMPONENT_DB[comp]
            with col:
                st.markdown(f"#### {comp}")
                props_df = pd.DataFrame({
                    "Property": ["Molecular Weight", "Normal Boiling Point", "Critical Temperature",
                                  "Critical Pressure", "Acentric Factor", "Liquid Density",
                                  "Liquid Viscosity", "Liquid Cp", "Latent Heat", "Surface Tension",
                                  "Antoine Tmin", "Antoine Tmax", "Antoine A", "Antoine B",
                                  "Antoine C", "Data Quality", "Source / Note"],
                    "Value": [p["MW"], p["Tb"], p["Tc"], p["Pc"], p["omega"], p["rho_L"],
                               p["mu_L"], p["Cp_L"], p["Hvap"], p["sigma"], p["Tmin"],
                               p["Tmax"], p["A"], p["B"], p["C"], p["data_quality"], p["source"]],
                    "Unit": ["g/mol", "°C", "K", "bar", "—", "kg/m³",
                              "mPa·s", "J/mol·K", "J/mol", "N/m", "°C", "°C",
                              "log10(mmHg)", "°C", "°C", "—", "—"]
                })
                st.dataframe(props_df, use_container_width=True, hide_index=True)
                st.markdown(f"""
                <div class="info-panel">
                🧪 <strong>Advanced design properties:</strong><br>
                ρL = <strong>{p['rho_L']} kg/m³</strong> &nbsp;|&nbsp;
                μL = <strong>{p['mu_L']} mPa·s</strong> &nbsp;|&nbsp;
                CpL = <strong>{p['Cp_L']} J/mol·K</strong><br>
                Hvap = <strong>{p['Hvap']} J/mol</strong> &nbsp;|&nbsp;
                σ = <strong>{p['sigma']} N/m</strong> &nbsp;|&nbsp;
                Antoine range = <strong>{p['Tmin']} to {p['Tmax']} °C</strong><br>
                Quality = <strong>{p['data_quality']}</strong>
                </div>
                """, unsafe_allow_html=True)

        mix_feed = binary_mixture_props(light, heavy, feed.get("z_F", 0.5) if feed else 0.5)
        st.markdown(f"""
        <div class="info-panel">
        📌 <strong>Mixture property estimate at feed composition:</strong>
        MW = <strong>{mix_feed['MW']} g/mol</strong> &nbsp;|&nbsp;
        ρL = <strong>{mix_feed['rho_L']} kg/m³</strong> &nbsp;|&nbsp;
        μL = <strong>{mix_feed['mu_L']} mPa·s</strong> &nbsp;|&nbsp;
        CpL = <strong>{mix_feed['Cp_L']} J/mol·K</strong> &nbsp;|&nbsp;
        Hvap = <strong>{mix_feed['Hvap']} J/mol</strong> &nbsp;|&nbsp;
        σ = <strong>{mix_feed['sigma']} N/m</strong>
        </div>
        """, unsafe_allow_html=True)

        # Full DB table
        with st.expander("📋 View Full Component Database"):
            rows = []
            for name, p in sorted(COMPONENT_DB.items()):
                rows.append({"Component": name, "MW": p["MW"], "Tb [°C]": p["Tb"],
                              "Tc [K]": p["Tc"], "Pc [bar]": p["Pc"], "ω": p["omega"],
                              "ρL [kg/m³]": p["rho_L"], "μL [mPa·s]": p["mu_L"],
                              "CpL [J/mol·K]": p["Cp_L"], "Hvap [J/mol]": p["Hvap"],
                              "σ [N/m]": p["sigma"], "Tmin [°C]": p["Tmin"],
                              "Tmax [°C]": p["Tmax"], "Antoine A": p["A"],
                              "Antoine B": p["B"], "Antoine C": p["C"],
                              "Quality": p["data_quality"], "Source / Note": p["source"]})
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # ── TAB 2: VLE Curve ──────────────────────────────────────
    with tab2:
        st.markdown('<h3 class="thermo-vle-heading">&#128200; Vapour-Liquid Equilibrium Curve</h3>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown('<div class="thermo-input-label">Temperature [&deg;C]</div>', unsafe_allow_html=True)
            T_vle = st.number_input("Temperature [°C]", value=float(T_feed), min_value=-50.0, max_value=300.0, step=1.0, label_visibility="collapsed")
        with c2:
            st.markdown('<div class="thermo-input-label">Pressure [mmHg]</div>', unsafe_allow_html=True)
            P_vle = st.number_input("Pressure [mmHg]", value=float(P_mmHg), min_value=100.0, max_value=7600.0, step=10.0, label_visibility="collapsed")
        with c3:
            st.markdown('<div class="thermo-input-label">Curve points</div>', unsafe_allow_html=True)
            n_pts = st.slider("Curve points", 50, 500, 200, label_visibility="collapsed")
        with c4:
            st.markdown('<div class="thermo-input-label">VLE Model</div>', unsafe_allow_html=True)
            selected_vle_model = st.selectbox(
                "VLE Model",
                VLE_MODELS,
                index=VLE_MODELS.index(selected_vle_model),
                key="thermo_selected_vle_model",
                label_visibility="collapsed",
            )

        pair_key = f"{light}_{heavy}".replace(" ", "_").replace(".", "")
        default_params = _default_model_params(light, heavy)
        selected_model_params = default_params.copy()

        if selected_vle_model == "Modified Raoult's Law":
            p1, p2 = st.columns(2)
            with p1:
                selected_model_params["A12"] = st.number_input(
                    "Margules A12", value=float(default_params["A12"]),
                    min_value=-5.0, max_value=5.0, step=0.05, key=f"margules_a12_{pair_key}"
                )
            with p2:
                selected_model_params["A21"] = st.number_input(
                    "Margules A21", value=float(default_params["A21"]),
                    min_value=-5.0, max_value=5.0, step=0.05, key=f"margules_a21_{pair_key}"
                )
        elif selected_vle_model == "Wilson Model":
            p1, p2 = st.columns(2)
            with p1:
                selected_model_params["L12"] = st.number_input(
                    "Wilson Λ12", value=float(default_params["L12"]),
                    min_value=0.01, max_value=10.0, step=0.05, key=f"wilson_l12_{pair_key}"
                )
            with p2:
                selected_model_params["L21"] = st.number_input(
                    "Wilson Λ21", value=float(default_params["L21"]),
                    min_value=0.01, max_value=10.0, step=0.05, key=f"wilson_l21_{pair_key}"
                )
        elif selected_vle_model == "NRTL Model":
            p1, p2, p3 = st.columns(3)
            with p1:
                selected_model_params["tau12"] = st.number_input(
                    "NRTL τ12", value=float(default_params["tau12"]),
                    min_value=-5.0, max_value=5.0, step=0.05, key=f"nrtl_tau12_{pair_key}"
                )
            with p2:
                selected_model_params["tau21"] = st.number_input(
                    "NRTL τ21", value=float(default_params["tau21"]),
                    min_value=-5.0, max_value=5.0, step=0.05, key=f"nrtl_tau21_{pair_key}"
                )
            with p3:
                selected_model_params["alpha_nrtl"] = st.number_input(
                    "NRTL α", value=float(default_params["alpha_nrtl"]),
                    min_value=0.10, max_value=0.80, step=0.05, key=f"nrtl_alpha_{pair_key}"
                )

        try:
            alpha_T = relative_volatility(light, heavy, T_vle)
            Psat_L  = antoine_pvap(light, T_vle)
            Psat_H  = antoine_pvap(heavy, T_vle)
            range_l = antoine_range_status(light, T_vle)
            range_h = antoine_range_status(heavy, T_vle)
            if range_l.get("ok") is False or range_h.get("ok") is False:
                st.warning(
                    f"⚠️ Antoine range check: {light}: {range_l.get('message')} | "
                    f"{heavy}: {range_h.get('message')} Use results as extrapolated estimates."
                )

            # ── Formulae explanation ───────────────────────────
            st.markdown(_model_formula_box(selected_vle_model, selected_model_params), unsafe_allow_html=True)

            # ── Sample point solved manually ───────────────────
            x_example = 0.40
            y_example_arr, alpha_example_arr, g1_example, g2_example = _vle_model_curve(
                light, heavy, T_vle, P_vle, selected_vle_model, selected_model_params, np.array([x_example])
            )
            y_example = round(float(y_example_arr[0]), 4)
            st.markdown(f"""
            <div class="formula-box thermo-calc-box" style="border-left:4px solid #f59e0b !important;">
                <div class="formula-title">✏️ Sample Point — Solved Example (x = {x_example})</div>
                <b>Antoine constants for {light}:</b>
                A={COMPONENT_DB[light]['A']}, B={COMPONENT_DB[light]['B']}, C={COMPONENT_DB[light]['C']}<br>
                <b>Antoine constants for {heavy}:</b>
                A={COMPONENT_DB[heavy]['A']}, B={COMPONENT_DB[heavy]['B']}, C={COMPONENT_DB[heavy]['C']}<br><br>
                At T = {T_vle}°C:<br>
                &nbsp;&nbsp; log₁₀(P°<sub>{light}</sub>) = {COMPONENT_DB[light]['A']} − {COMPONENT_DB[light]['B']} / ({COMPONENT_DB[light]['C']} + {T_vle}) = {round(COMPONENT_DB[light]['A'] - COMPONENT_DB[light]['B']/(COMPONENT_DB[light]['C']+T_vle),4)}<br>
                &nbsp;&nbsp; P°<sub>{light}</sub> = 10^{round(COMPONENT_DB[light]['A'] - COMPONENT_DB[light]['B']/(COMPONENT_DB[light]['C']+T_vle),4)} = <b>{Psat_L:.2f} mmHg</b><br><br>
                &nbsp;&nbsp; log₁₀(P°<sub>{heavy}</sub>) = {COMPONENT_DB[heavy]['A']} − {COMPONENT_DB[heavy]['B']} / ({COMPONENT_DB[heavy]['C']} + {T_vle}) = {round(COMPONENT_DB[heavy]['A'] - COMPONENT_DB[heavy]['B']/(COMPONENT_DB[heavy]['C']+T_vle),4)}<br>
                &nbsp;&nbsp; P°<sub>{heavy}</sub> = <b>{Psat_H:.2f} mmHg</b><br><br>
                &nbsp;&nbsp; γ<sub>{light}</sub> = <b>{float(g1_example[0]):.4f}</b>,
                γ<sub>{heavy}</sub> = <b>{float(g2_example[0]):.4f}</b><br>
                &nbsp;&nbsp; α<sub>eff</sub> = γ<sub>{light}</sub>P°<sub>{light}</sub> / γ<sub>{heavy}</sub>P°<sub>{heavy}</sub>
                = <b>{float(alpha_example_arr[0]):.4f}</b><br><br>
                At x = {x_example}:<br>
                &nbsp;&nbsp; y = xγ<sub>1</sub>P°<sub>1</sub> / [xγ<sub>1</sub>P°<sub>1</sub> + (1−x)γ<sub>2</sub>P°<sub>2</sub>]<br>
                &nbsp;&nbsp; <b>→ Point on graph: x = {x_example}, y = {y_example} ⭐</b>
            </div>
            <div class="thermo-calc-separator"></div>
            """, unsafe_allow_html=True)

            # ── Generate curve data ───────────────────────────
            x_arr = np.linspace(0.001, 0.999, n_pts)
            y_arr, alpha_eff, gamma_1, gamma_2 = _vle_model_curve(
                light, heavy, T_vle, P_vle, selected_vle_model, selected_model_params, x_arr
            )

            azeotrope_detected = bool(np.any(alpha_eff <= 1.05))
            azeotrope_x = azeotrope_y = None
            if azeotrope_detected:
                az_idx = int(np.argmin(alpha_eff))
                azeotrope_x = float(x_arr[az_idx])
                azeotrope_y = float(y_arr[az_idx])
                st.markdown(f"""
                <div class="warn-panel" style="border-left:4px solid #ef4444;">
                🚨 <strong>Possible azeotrope detected:</strong>
                α<sub>eff</sub> drops to {alpha_eff[az_idx]:.4f} near x = {azeotrope_x:.3f}.
                Conventional distillation cannot cross this point without pressure-swing,
                azeotropic, or extractive distillation.
                </div>
                """, unsafe_allow_html=True)

            T_range = np.linspace(COMPONENT_DB[heavy]["Tb"], COMPONENT_DB[light]["Tb"], 60)
            x_pts, y_pts = [], []
            for T in T_range:
                try:
                    x_t, y_t = vle_raoult(light, heavy, T, P_vle)
                    if 0 <= x_t <= 1 and 0 <= y_t <= 1:
                        x_pts.append(x_t); y_pts.append(y_t)
                except:
                    pass

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=[0,1], y=[0,1], mode="lines",
                                      name="y = x (diagonal)",
                                      line=dict(color="#e2e8f0", dash="dash", width=3.2),
                                      opacity=0.78))
            fig.add_trace(go.Scatter(x=x_arr, y=y_arr, mode="lines",
                                      name=f"{selected_vle_model}",
                                      line=dict(color="#00b4d8", width=3)))
            if x_pts:
                fig.add_trace(go.Scatter(x=x_pts, y=y_pts, mode="markers",
                                          name="Raoult's Law (T-x-y dots)",
                                          marker=dict(color="#f59e0b", size=6)))
            # Star marker for example point
            fig.add_trace(go.Scatter(
                x=[x_example], y=[y_example], mode="markers+text",
                name=f"Example point (x={x_example}, y={y_example})",
                marker=dict(color="#22c55e", size=14, symbol="star"),
                text=[f"  x={x_example}, y={y_example}"],
                textposition="middle right",
                textfont=dict(color="#22c55e", size=11)
            ))
            if azeotrope_detected:
                fig.add_trace(go.Scatter(
                    x=[azeotrope_x], y=[azeotrope_y], mode="markers+text",
                    name="Possible azeotrope",
                    marker=dict(color="#ef4444", size=16, symbol="star"),
                    text=[f"  azeotrope? x={azeotrope_x:.3f}"],
                    textposition="middle right",
                    textfont=dict(color="#ef4444", size=11)
                ))

            fig.update_layout(
                template="plotly_dark", paper_bgcolor="#0a0e14", plot_bgcolor="#111827",
                font=dict(family="Barlow", color="#e2e8f0"),
                xaxis=dict(title=f"x — Liquid mole fraction {light}",
                           range=[-0.02,1.02], gridcolor="#1e3a5f"),
                yaxis=dict(title=f"y — Vapour mole fraction {light}",
                           range=[-0.02,1.02], gridcolor="#1e3a5f"),
                height=480, margin=dict(t=20),
                legend=dict(bgcolor="#111827", bordercolor="#1e3a5f")
            )
            st.plotly_chart(fig, use_container_width=True)

            st.markdown(f"""
            <div class="thermo-metric-grid">
                <div class="thermo-metric-card">
                    <div class="thermo-metric-label">P&deg;({light}) at {T_vle:.1f}&deg;C</div>
                    <div class="thermo-metric-value">{Psat_L:.2f}<span class="thermo-metric-unit">mmHg</span></div>
                </div>
                <div class="thermo-metric-card">
                    <div class="thermo-metric-label">P&deg;({heavy}) at {T_vle:.1f}&deg;C</div>
                    <div class="thermo-metric-value">{Psat_H:.2f}<span class="thermo-metric-unit">mmHg</span></div>
                </div>
                <div class="thermo-metric-card">
                    <div class="thermo-metric-label">&alpha;<sub>eff</sub> at x = {x_example}</div>
                    <div class="thermo-metric-value">{float(alpha_example_arr[0]):.4f}</div>
                </div>
                <div class="thermo-metric-card">
                    <div class="thermo-metric-label">Example: y at x = {x_example}</div>
                    <div class="thermo-metric-value">{y_example}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            _merge_thermo_state(
                vle_model=selected_vle_model,
                vle_model_params=selected_model_params,
                alpha_avg=round(float(np.nanmean(alpha_eff)), 4),
                alpha_feed=round(float(np.interp(feed.get("z_F", 0.5), x_arr, alpha_eff)), 4),
                azeotrope_detected=azeotrope_detected,
                azeotrope_x=round(azeotrope_x, 4) if azeotrope_detected else None,
                azeotrope_y=round(azeotrope_y, 4) if azeotrope_detected else None,
                model_advisor=advisor,
                suggested_vle_model=advisor["model"],
                nonideality_level=advisor["level"],
            )

        except Exception as e:
            st.error(f"VLE error: {e}")

    # ── TAB 3: Bubble / Dew Points ────────────────────────────
    with tab3:
        st.markdown('<h3 class="thermo-tab-heading">&#127777;&#65039; Bubble Point & Dew Point Calculations</h3>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div class="thermo-input-label">Liquid mole fraction {light} (for bubble point)</div>', unsafe_allow_html=True)
            x_light_bp = st.slider(f"Liquid mole fraction {light} (for bubble point)", 0.01, 0.99, 0.50, 0.01, label_visibility="collapsed")
        with c2:
            st.markdown('<div class="thermo-input-label">Pressure [mmHg]</div>', unsafe_allow_html=True)
            P_bp = st.number_input("Pressure [mmHg]", value=float(P_mmHg), min_value=50.0, max_value=7600.0, step=10.0, key="bp_P", label_visibility="collapsed")

        try:
            T_bub = bubble_point_T(light, heavy, x_light_bp, P_bp)
            T_dew_val = dew_point_T(light, heavy, x_light_bp, P_bp)
            alpha_bub = relative_volatility(light, heavy, T_bub)

            st.markdown(_metric_cards_html([
                ("Bubble Point Temperature", f"{T_bub:.2f}", "&deg;C"),
                ("Dew Point Temperature", f"{T_dew_val:.2f}", "&deg;C"),
                ("&alpha; at Bubble Point", f"{alpha_bub:.4f}", ""),
            ]), unsafe_allow_html=True)

            # x-T diagram
            x_scan = np.linspace(0.01, 0.99, 60)
            T_bub_arr, T_dew_arr = [], []
            for xi in x_scan:
                try:
                    T_bub_arr.append(bubble_point_T(light, heavy, xi, P_bp))
                    T_dew_arr.append(dew_point_T(light, heavy, xi, P_bp))
                except:
                    T_bub_arr.append(np.nan); T_dew_arr.append(np.nan)

            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=x_scan, y=T_bub_arr, mode="lines", name="Bubble Point (Liquid)",
                                       line=dict(color="#00b4d8", width=2.5)))
            fig2.add_trace(go.Scatter(x=x_scan, y=T_dew_arr, mode="lines", name="Dew Point (Vapour)",
                                       line=dict(color="#f59e0b", width=2.5, dash="dash")))
            fig2.add_trace(go.Scatter(x=[x_light_bp], y=[T_bub], mode="markers",
                                       name=f"Current point ({x_light_bp:.2f})",
                                       marker=dict(color="#22c55e", size=12)))
            fig2.update_layout(
                template="plotly_dark", paper_bgcolor="#0a0e14", plot_bgcolor="#111827",
                font=dict(family="Barlow", color="#e2e8f0"),
                xaxis=dict(title=f"Liquid mole fraction {light}", gridcolor="#1e3a5f"),
                yaxis=dict(title="Temperature [°C]", gridcolor="#1e3a5f"),
                height=420, margin=dict(t=20)
            )
            st.plotly_chart(fig2, use_container_width=True)

        except Exception as e:
            st.error(f"Bubble/dew point error: {e}")

    # ── TAB 4: Relative Volatility ────────────────────────────
    with tab4:
        st.markdown('<h3 class="thermo-tab-heading">&#9889; Relative Volatility vs Temperature</h3>', unsafe_allow_html=True)
        try:
            Tb_l = COMPONENT_DB[light]["Tb"]
            Tb_h = COMPONENT_DB[heavy]["Tb"]
            T_range_alpha = np.linspace(min(Tb_l, Tb_h) - 10, max(Tb_l, Tb_h) + 20, 100)
            alpha_range = [relative_volatility(light, heavy, T) for T in T_range_alpha]

            T_top = feed.get("T_bubble_F", Tb_l) if feed else Tb_l
            T_bot = feed.get("T_bubble_F", Tb_h) if feed else Tb_h

            alpha_top  = relative_volatility(light, heavy, T_top)
            alpha_feed = relative_volatility(light, heavy, T_feed)
            alpha_bot  = relative_volatility(light, heavy, T_bot + 10)
            alpha_avg_geo = (alpha_top * alpha_feed * alpha_bot) ** (1/3)

            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(x=T_range_alpha, y=alpha_range, mode="lines",
                                       name="α vs T", line=dict(color="#00b4d8", width=2.5)))
            fig3.add_hline(y=alpha_avg_geo, line_dash="dot", line_color="#f8d477", line_width=3,
                            annotation_text=f"α_avg = {alpha_avg_geo:.3f}")
            fig3.add_hline(y=1.0, line_dash="dash", line_color="#ff5b6e", line_width=3,
                            annotation_text="α = 1 (no separation)")

            fig3.update_layout(
                template="plotly_dark", paper_bgcolor="#0a0e14", plot_bgcolor="#111827",
                font=dict(family="Barlow", color="#e2e8f0"),
                xaxis=dict(title="Temperature [°C]", gridcolor="#1e3a5f"),
                yaxis=dict(title="Relative Volatility α", gridcolor="#1e3a5f"),
                height=400, margin=dict(t=20)
            )
            st.plotly_chart(fig3, use_container_width=True)

            st.markdown(_metric_cards_html([
                ("&alpha; at Top (distillate T)", f"{alpha_top:.4f}", ""),
                ("&alpha; at Feed", f"{alpha_feed:.4f}", ""),
                ("&alpha; at Bottom", f"{alpha_bot:.4f}", ""),
                ("&alpha; avg (geometric mean)", f"{alpha_avg_geo:.4f}", ""),
            ], label_extra_class="thermo-metric-label-red"), unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Relative volatility error: {e}")

    # ── TAB 5: T-x-y Diagram ─────────────────────────────────
    with tab5:
        st.markdown('<h3 class="thermo-tab-heading">&#127777;&#65039; T-x-y Phase Diagram</h3>', unsafe_allow_html=True)
        st.markdown("""
        <div class="formula-box thermo-calc-box">
            <div class="formula-title">T-x-y Diagram — Bubble and Dew Curves</div>
            <b>Bubble curve:</b> solve Σx<sub>i</sub>P°<sub>i</sub>(T) = P for liquid composition x<br>
            <b>Dew curve:</b> solve 1 / Σ[y<sub>i</sub>/P°<sub>i</sub>(T)] = P for vapour composition y<br>
            The shaded region between curves is the two-phase vapour-liquid zone.
        </div>
        <div class="thermo-calc-separator"></div>
        """, unsafe_allow_html=True)

        try:
            x_phase = np.linspace(0.01, 0.99, 80)
            T_bubble_curve, T_dew_curve = [], []
            for xi in x_phase:
                try:
                    T_bubble_curve.append(bubble_point_T(light, heavy, float(xi), P_mmHg))
                    T_dew_curve.append(dew_point_T(light, heavy, float(xi), P_mmHg))
                except Exception:
                    T_bubble_curve.append(np.nan)
                    T_dew_curve.append(np.nan)

            fig_txy = go.Figure()
            fig_txy.add_trace(go.Scatter(
                x=x_phase, y=T_bubble_curve, mode="lines",
                name="Bubble point curve (liquid x)",
                line=dict(color="#00b4d8", width=3)
            ))
            fig_txy.add_trace(go.Scatter(
                x=x_phase, y=T_dew_curve, mode="lines",
                name="Dew point curve (vapour y)",
                line=dict(color="#f59e0b", width=3, dash="dash"),
                fill="tonexty", fillcolor="rgba(0,180,216,0.12)"
            ))

            markers = [
                ("Feed zF", feed.get("z_F"), "#22c55e"),
                ("Distillate xD", feed.get("x_D"), "#38bdf8"),
                ("Bottoms xB", feed.get("x_B"), "#f97316"),
            ]
            for label, value, color in markers:
                if value is not None:
                    fig_txy.add_vline(
                        x=float(value), line_dash="dash", line_color=color,
                        annotation_text=label, annotation_font_color=color
                    )

            fig_txy.update_layout(
                template="plotly_dark", paper_bgcolor="#0a0e14", plot_bgcolor="#111827",
                font=dict(family="Barlow", color="#e2e8f0"),
                xaxis=dict(title=f"Composition of {light}", range=[0, 1], gridcolor="#1e3a5f"),
                yaxis=dict(title="Temperature [°C]", gridcolor="#1e3a5f"),
                height=480, margin=dict(t=20),
                legend=dict(bgcolor="#111827", bordercolor="#1e3a5f")
            )
            st.plotly_chart(fig_txy, use_container_width=True)
        except Exception as e:
            st.error(f"T-x-y diagram error: {e}")

    # ── TAB 6: Models Comparison ──────────────────────────────
    with tab6:
        st.markdown('<h3 class="thermo-tab-heading">&#129514; VLE Models Comparison</h3>', unsafe_allow_html=True)
        st.markdown("""
        <div class="formula-box thermo-calc-box">
            <div class="formula-title thermo-model-title">Why compare models?</div>
            Raoult's Law assumes ideal liquid behaviour. Modified Raoult, Wilson, and NRTL
            add activity coefficients γ to represent liquid-phase non-ideality. Large curve
            separation means model choice can strongly affect McCabe-Thiele stages and reflux.
        </div>
        <div class="thermo-calc-separator"></div>
        """, unsafe_allow_html=True)

        try:
            x_cmp = np.linspace(0.001, 0.999, 240)
            styles = {
                "Raoult's Law": dict(color="#00b4d8", dash="solid"),
                "Modified Raoult's Law": dict(color="#f59e0b", dash="dash"),
                "Wilson Model": dict(color="#22c55e", dash="dot"),
                "NRTL Model": dict(color="#ef4444", dash="dashdot"),
            }
            suitability = {
                "Raoult's Law": "Non-polar, similar hydrocarbons; low-pressure ideal systems",
                "Modified Raoult's Law": "Mildly polar or slightly non-ideal binary pairs",
                "Wilson Model": "Alcohol-water and miscible polar systems",
                "NRTL Model": "Aqueous, highly non-ideal, local-composition systems",
            }

            fig_cmp = go.Figure()
            rows = []
            for model in VLE_MODELS:
                params = selected_model_params if model == selected_vle_model else _default_model_params(light, heavy)
                y_cmp, alpha_cmp, _, _ = _vle_model_curve(light, heavy, T_vle, P_vle, model, params, x_cmp)
                fig_cmp.add_trace(go.Scatter(
                    x=x_cmp, y=y_cmp, mode="lines", name=model,
                    line=dict(width=2.7, color=styles[model]["color"], dash=styles[model]["dash"])
                ))
                rows.append({
                    "Model": model,
                    "y @ x=0.3": round(float(np.interp(0.3, x_cmp, y_cmp)), 4),
                    "y @ x=0.5": round(float(np.interp(0.5, x_cmp, y_cmp)), 4),
                    "y @ x=0.7": round(float(np.interp(0.7, x_cmp, y_cmp)), 4),
                    "Suitable systems": suitability[model],
                })

            fig_cmp.add_trace(go.Scatter(
                x=[0, 1], y=[0, 1], mode="lines", name="y = x",
                line=dict(color="#e2e8f0", dash="dash", width=3.2),
                opacity=0.78
            ))
            fig_cmp.update_layout(
                template="plotly_dark", paper_bgcolor="#0a0e14", plot_bgcolor="#111827",
                font=dict(family="Barlow", color="#e2e8f0"),
                xaxis=dict(title=f"x — Liquid mole fraction {light}", range=[0, 1], gridcolor="#1e3a5f"),
                yaxis=dict(title=f"y — Vapour mole fraction {light}", range=[0, 1], gridcolor="#1e3a5f"),
                height=480, margin=dict(t=20),
                legend=dict(bgcolor="#111827", bordercolor="#1e3a5f")
            )
            st.plotly_chart(fig_cmp, use_container_width=True)
            st.markdown(_model_comparison_table_html(rows), unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Models comparison error: {e}")

    # ── Save ──────────────────────────────────────────────────
    st.markdown("<div class='eng-divider'></div>", unsafe_allow_html=True)
    if st.button("💾 Save Thermodynamic Data", type="primary"):
        try:
            alpha_avg = avg_relative_volatility(light, heavy,
                COMPONENT_DB[light]["Tb"], T_feed, COMPONENT_DB[heavy]["Tb"])
            T_bub_F = bubble_point_T(light, heavy, feed.get("z_F",0.5), P_mmHg) if feed else T_feed
            T_dew_F = dew_point_T(light, heavy, feed.get("z_F",0.5), P_mmHg) if feed else T_feed + 10
            T_bub_D = bubble_point_T(light, heavy, feed.get("x_D",0.95), P_mmHg) if feed else COMPONENT_DB[light]["Tb"]
            T_bub_B = bubble_point_T(light, heavy, feed.get("x_B",0.05), P_mmHg) if feed else COMPONENT_DB[heavy]["Tb"]
            props_F = binary_mixture_props(light, heavy, feed.get("z_F", 0.5) if feed else 0.5)
            props_D = binary_mixture_props(light, heavy, feed.get("x_D", 0.95) if feed else 0.95)
            props_B = binary_mixture_props(light, heavy, feed.get("x_B", 0.05) if feed else 0.05)

            st.session_state.thermo = {
                "light": light, "heavy": heavy,
                "alpha_avg": round(alpha_avg, 4),
                "alpha_top": round(relative_volatility(light, heavy, T_bub_D), 4),
                "alpha_feed": round(relative_volatility(light, heavy, T_feed), 4),
                "alpha_bot":  round(relative_volatility(light, heavy, T_bub_B), 4),
                "T_bubble_F": round(T_bub_F, 2),
                "T_dew_F":    round(T_dew_F, 2),
                "T_bubble_D": round(T_bub_D, 2),
                "T_bubble_B": round(T_bub_B, 2),
                "vle_model":  selected_vle_model,
                "vle_model_params": selected_model_params,
                "suggested_vle_model": advisor["model"],
                "nonideality_level": advisor["level"],
                "model_advisor": advisor,
                "P_mmHg": P_mmHg,
                "feed_props": props_F,
                "distillate_props": props_D,
                "bottoms_props": props_B,
                "rho_L_feed": props_F["rho_L"],
                "mu_L_feed": props_F["mu_L"],
                "Cp_L_feed": props_F["Cp_L"],
                "Hvap_feed": props_F["Hvap"],
                "rho_L_distillate": props_D["rho_L"],
                "Cp_L_distillate": props_D["Cp_L"],
                "Hvap_distillate": props_D["Hvap"],
                "rho_L_bottoms": props_B["rho_L"],
                "Cp_L_bottoms": props_B["Cp_L"],
                "Hvap_bottoms": props_B["Hvap"],
            }
            st.success(f"✅ Thermodynamic data saved! α_avg = {alpha_avg:.4f}. Proceed to **Shortcut Design**.")
        except Exception as e:
            st.error(f"Error saving thermodynamic data: {e}")
