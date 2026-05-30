"""sections/shortcut.py - Shortcut Distillation Design"""
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from calculations.distillation_calc import (
    fenske, underwood, gilliland, kirkbride, material_balance
)
from thermodynamics.thermo_engine import avg_relative_volatility, COMPONENT_DB


def _metric_cards_html(cards):
    html_cards = []
    for label, value, unit in cards:
        unit_html = f'<span class="shortcut-metric-unit">{unit}</span>' if unit else ""
        html_cards.append(
            '<div class="shortcut-metric-card">'
            f'<div class="shortcut-metric-label">{label}</div>'
            f'<div class="shortcut-metric-value">{value}{unit_html}</div>'
            '</div>'
        )
    return '<div class="shortcut-metric-grid">' + ''.join(html_cards) + '</div>'


def _formula_box(title, body, border="#00b4d8"):
    return (
        f'<div class="formula-box shortcut-calc-box" style="border-left-color:{border} !important;">'
        f'<div class="formula-title">{title}</div>'
        f'{body}'
        '</div><div class="shortcut-calc-separator"></div>'
    )


def _context_box(title, body, tone="info"):
    colors = {
        "info": "#00b4d8",
        "warn": "#f8d477",
        "success": "#22c55e",
        "danger": "#ff5b6e",
    }
    color = colors.get(tone, colors["info"])
    return (
        f'<div class="shortcut-context-box" style="border-left-color:{color};">'
        f'<div class="shortcut-context-title" style="color:{color};">{title}</div>'
        f'{body}'
        '</div>'
    )


def _summary_table_html(summary):
    rows = []
    for param, value in zip(summary["Parameter"], summary["Value"]):
        if str(param).startswith("---"):
            rows.append(f'<tr class="shortcut-section-row"><td colspan="2">{param.strip("- ")}</td></tr>')
        else:
            rows.append(f"<tr><td>{param}</td><td>{value}</td></tr>")
    return (
        '<table class="shortcut-summary-table">'
        '<thead><tr><th>Parameter</th><th>Value</th></tr></thead>'
        '<tbody>' + ''.join(rows) + '</tbody></table>'
    )


def render():
    st.markdown("""
    <div class="section-header">
        <h1>⚡ Shortcut Distillation Design</h1>
        <p>Fenske (N<sub>min</sub>) → Underwood (R<sub>min</sub>) → Gilliland (N actual) → Kirkbride (Feed Tray Location)</p>
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
    .shortcut-tab-heading {
        color: #f8d477 !important;
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 2.05rem !important;
        font-weight: 900 !important;
        letter-spacing: 0;
        line-height: 1.12;
        margin: 0.45rem 0 1rem 0;
        text-shadow: 0 0 14px rgba(248, 212, 119, 0.24);
    }
    .shortcut-input-label {
        color: #ff5b6e !important;
        font-weight: 900 !important;
        letter-spacing: 0.2px;
        margin: 0 0 0.42rem 0.05rem;
        text-shadow: 0 0 10px rgba(239, 68, 68, 0.22);
    }
    .shortcut-context-box {
        background: linear-gradient(135deg, rgba(8, 14, 24, 0.99), rgba(15, 23, 42, 0.97));
        border: 1px solid rgba(0, 180, 216, 0.44);
        border-left: 4px solid #00b4d8;
        border-radius: 8px;
        color: #eaf6ff;
        padding: 1rem 1.1rem;
        margin: 0.6rem 0 1rem 0;
        line-height: 1.65;
        box-shadow: 0 10px 24px rgba(0,0,0,0.15);
    }
    .shortcut-context-title {
        color: #f8d477;
        font-weight: 900;
        margin-bottom: 0.35rem;
    }
    .shortcut-calc-box {
        color: #eaf6ff !important;
        background: linear-gradient(135deg, rgba(8, 14, 24, 0.99), rgba(15, 23, 42, 0.97)) !important;
        border: 1px solid rgba(0, 180, 216, 0.44) !important;
        border-left: 4px solid #00b4d8 !important;
        box-shadow: 0 0 0 1px rgba(255,255,255,0.03), 0 12px 28px rgba(0,0,0,0.18);
        font-size: 1.02rem !important;
        line-height: 1.75;
    }
    .shortcut-calc-box b,
    .shortcut-calc-box strong {
        color: #ffffff !important;
        font-weight: 900 !important;
    }
    .shortcut-calc-box .formula-title {
        color: #f8d477 !important;
        font-size: 1.08rem !important;
        font-weight: 900 !important;
        letter-spacing: 0.2px;
        margin-bottom: 0.55rem;
    }
    .shortcut-calc-separator {
        border-top: 2px dotted rgba(248, 212, 119, 0.58);
        margin: 1.15rem 0 1.35rem 0;
        height: 1px;
    }
    .shortcut-metric-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 1rem;
        margin: 1.05rem 0 1.35rem 0;
    }
    .shortcut-metric-card {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.98), rgba(8, 14, 24, 0.98));
        border: 1px solid rgba(0, 180, 216, 0.48);
        border-radius: 8px;
        padding: 1rem 1.05rem;
        min-height: 118px;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.04), 0 10px 24px rgba(0,0,0,0.16);
    }
    .shortcut-metric-label {
        color: #ff5b6e !important;
        font-size: 0.94rem;
        font-weight: 900;
        line-height: 1.3;
        margin-bottom: 0.55rem;
        text-shadow: 0 0 10px rgba(239, 68, 68, 0.24);
    }
    .shortcut-metric-value {
        color: #00d4ff;
        font-family: 'Share Tech Mono', monospace;
        font-size: clamp(1.7rem, 2.4vw, 2.55rem);
        font-weight: 900;
        letter-spacing: 0;
        line-height: 1.05;
        word-break: break-word;
        text-shadow: 0 0 14px rgba(0, 180, 216, 0.18);
    }
    .shortcut-metric-unit {
        color: #dbeafe;
        font-family: 'Barlow', sans-serif;
        font-size: 0.86rem;
        font-weight: 800;
        margin-left: 0.2rem;
    }
    .shortcut-summary-table {
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
    .shortcut-summary-table th {
        background: #1b2028;
        color: #f8d477;
        font-weight: 900;
        text-align: left;
        padding: 0.78rem 0.75rem;
        border-bottom: 1px solid rgba(148, 163, 184, 0.25);
    }
    .shortcut-summary-table td {
        padding: 0.72rem 0.75rem;
        border-bottom: 1px solid rgba(148, 163, 184, 0.14);
        color: #f8fbff;
    }
    .shortcut-summary-table tr:last-child td {
        border-bottom: 0;
    }
    .shortcut-summary-table td:first-child {
        color: #dbeafe;
        font-weight: 800;
    }
    .shortcut-summary-table td:last-child {
        color: #00d4ff;
        font-weight: 900;
    }
    .shortcut-section-row td {
        color: #22c55e !important;
        background: rgba(34, 197, 94, 0.08);
        font-weight: 900 !important;
        text-transform: uppercase;
        letter-spacing: 0.4px;
    }
    @media (max-width: 900px) {
        .shortcut-metric-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
    }
    @media (max-width: 560px) {
        .shortcut-metric-grid {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    feed = st.session_state.get("feed", {})
    thermo = st.session_state.get("thermo", {})
    col_type = st.session_state.get("column_type", None)

    if not feed:
        st.warning("⚠️ Complete **Feed Specifications** first.")
        return

    if col_type == "tray":
        st.markdown(_context_box(
            "Tray Column selected",
            "N_actual_int from this section will be used in:<br>"
            "&nbsp;&nbsp;→ <b>McCabe-Thiele</b> graphical stage stepping on x-y diagram<br>"
            "&nbsp;&nbsp;→ <b>Column Height</b>: N_actual_trays = N_theoretical / tray_efficiency, then × tray spacing",
            "info",
        ), unsafe_allow_html=True)
    elif col_type == "packed":
        st.markdown(_context_box(
            "Packed Column selected",
            "N_actual_int from this section = <b>theoretical stages</b>.<br>"
            "&nbsp;&nbsp;→ Packed bed height = N_theoretical × HETP<br>"
            "&nbsp;&nbsp;→ HETP is selected in <b>Packing Design</b><br>"
            "&nbsp;&nbsp;→ McCabe-Thiele is not used as a physical tray count for packed columns",
            "info",
        ), unsafe_allow_html=True)
    else:
        st.markdown(_context_box(
            "Column type not selected yet",
            "Complete <b>Column Type</b> first so the correct tray or packed next steps are shown after shortcut design.",
            "warn",
        ), unsafe_allow_html=True)

    light = feed["light"]
    heavy = feed["heavy"]
    x_D = feed["x_D"]
    x_B = feed["x_B"]
    z_F = feed["z_F"]
    F = feed["F"]
    T_feed = feed["T_feed"]
    feed_cond = feed.get("feed_condition", "Saturated Liquid")
    q_saved = feed.get("q", 1.0)

    if thermo.get("alpha_avg"):
        alpha = float(thermo["alpha_avg"])
    else:
        try:
            alpha = avg_relative_volatility(
                light, heavy,
                COMPONENT_DB[light]["Tb"], T_feed, COMPONENT_DB[heavy]["Tb"])
        except Exception:
            alpha = 2.5
            st.warning("⚠️ Using default α = 2.5. Complete Thermodynamics section for accurate value.")

    q = q_saved

    tab1, tab2, tab3 = st.tabs(["🔢 Calculations", "📊 Gilliland Chart", "📋 Summary Table"])

    with tab1:
        st.markdown(_context_box(
            "System basis",
            f"System: <strong>{light} / {heavy}</strong> &nbsp;|&nbsp; "
            f"α = <strong>{alpha:.4f}</strong> &nbsp;|&nbsp; "
            f"xD = <strong>{x_D}</strong> &nbsp;|&nbsp; "
            f"xB = <strong>{x_B}</strong> &nbsp;|&nbsp; "
            f"zF = <strong>{z_F}</strong> &nbsp;|&nbsp; "
            f"q = <strong>{q:.4f}</strong> ({feed_cond})",
            "info",
        ), unsafe_allow_html=True)

        st.markdown('<h3 class="shortcut-tab-heading">1. Fenske Equation — Minimum Theoretical Stages</h3>', unsafe_allow_html=True)
        st.markdown(_formula_box(
            "Fenske Equation (1932)",
            "N<sub>min</sub> = log[(x<sub>D</sub>/(1−x<sub>D</sub>)) × "
            "((1−x<sub>B</sub>)/x<sub>B</sub>)] / log(α)",
        ), unsafe_allow_html=True)

        fen = fenske(x_D, x_B, alpha)
        st.markdown(_metric_cards_html([
            ("N_min (incl. reboiler)", f"{fen['N_min']:.3f}", ""),
            ("N_min (excl. reboiler)", f"{fen['N_min_excl_reboiler']:.3f}", ""),
            ("Relative Volatility α", f"{fen['alpha']:.4f}", ""),
        ]), unsafe_allow_html=True)

        st.markdown('<h3 class="shortcut-tab-heading">2. Underwood Equation — Minimum Reflux Ratio</h3>', unsafe_allow_html=True)
        st.markdown(_formula_box(
            "Underwood Equation — Binary System",
            "Step 1: Solve for θ: &nbsp; α·z<sub>F</sub>/(α−θ) + "
            "(1−z<sub>F</sub>)/(1−θ) = 1 − q<br>"
            "Step 2: R<sub>min</sub> = α·x<sub>D</sub>/(α−θ) + "
            "(1−x<sub>D</sub>)/(1−θ) − 1",
        ), unsafe_allow_html=True)

        und = underwood(alpha, z_F, q, x_D)
        st.markdown(_metric_cards_html([
            ("R_min", f"{und['R_min']:.4f}", ""),
            ("V_min (internal vapour)", f"{und['V_min']:.4f}", ""),
            ("θ (Underwood root)", f"{und['theta']:.6f}", ""),
        ]), unsafe_allow_html=True)

        st.markdown('<h3 class="shortcut-tab-heading">3. Select Operating Reflux Ratio</h3>', unsafe_allow_html=True)
        st.markdown(_context_box(
            "Industrial practice",
            f"R = 1.1–1.5 × R<sub>min</sub><br>"
            f"R<sub>min</sub> = {und['R_min']:.4f} → recommended range: "
            f"<strong>{round(1.1 * und['R_min'], 3)}</strong> to "
            f"<strong>{round(1.5 * und['R_min'], 3)}</strong>",
            "info",
        ), unsafe_allow_html=True)

        st.markdown('<div class="shortcut-input-label">R / R_min multiplier</div>', unsafe_allow_html=True)
        R_mult = st.slider(
            "R / R_min multiplier",
            min_value=1.05, max_value=2.50, value=1.20, step=0.05,
            label_visibility="collapsed",
        )
        R = round(R_mult * und["R_min"], 6)
        st.markdown(_context_box(
            "Operating reflux ratio",
            f"<strong>R = {R:.4f}</strong> = {R_mult} × R<sub>min</sub> = {R_mult} × {und['R_min']:.4f}",
            "success",
        ), unsafe_allow_html=True)

        st.markdown('<h3 class="shortcut-tab-heading">4. Gilliland Correlation — Actual Theoretical Stages</h3>', unsafe_allow_html=True)
        st.markdown(_formula_box(
            "Gilliland Correlation — Molokanov (1972) approximation",
            "X = (R − R<sub>min</sub>) / (R + 1)<br>"
            "Y = 1 − exp[(1 + 54.4X) / (11 + 117.2X) × (X − 1) / X<sup>0.5</sup>]<br>"
            "N = (Y + N<sub>min</sub>) / (1 − Y)",
        ), unsafe_allow_html=True)

        gil = gilliland(fen["N_min"], und["R_min"], R)
        st.markdown(_metric_cards_html([
            ("N actual (theoretical)", f"{gil['N_actual']:.2f}", ""),
            ("N actual (rounded up)", f"{gil['N_actual_int']}", ""),
            ("X (Gilliland parameter)", f"{gil['X_gilliland']:.4f}", ""),
            ("Y (Gilliland parameter)", f"{gil['Y_gilliland']:.4f}", ""),
        ]), unsafe_allow_html=True)

        st.markdown('<h3 class="shortcut-tab-heading">5. Kirkbride Equation — Feed Tray Location</h3>', unsafe_allow_html=True)
        st.markdown(_formula_box(
            "Kirkbride Equation",
            "log(N<sub>r</sub>/N<sub>s</sub>) = 0.206 × log[(B/D) × "
            "(x<sub>B</sub>/x<sub>D</sub>)² × ((1−x<sub>D</sub>)/(1−x<sub>B</sub>))]<br>"
            "N<sub>r</sub> = rectifying stages above feed &nbsp;|&nbsp; "
            "N<sub>s</sub> = stripping stages below feed",
        ), unsafe_allow_html=True)

        mb = material_balance(F, z_F, x_D, x_B)
        kirk = kirkbride(gil["N_actual_int"], z_F, x_D, x_B, mb["B"], mb["D"])
        st.markdown(_metric_cards_html([
            ("Rectifying Stages (Nr)", f"{kirk['Nr']:.1f}", ""),
            ("Stripping Stages (Ns)", f"{kirk['Ns']:.1f}", ""),
            ("Feed Tray (from top)", f"{kirk['feed_tray_from_top']}", ""),
            ("Nr/Ns ratio", f"{kirk['Nr_over_Ns']:.3f}", ""),
        ]), unsafe_allow_html=True)

        st.markdown(_context_box(
            "Shortcut Design Results",
            f"• N_min = <strong>{fen['N_min']:.2f}</strong> &nbsp;|&nbsp; "
            f"R_min = <strong>{und['R_min']:.4f}</strong><br>"
            f"• Operating R = <strong>{R:.4f}</strong> ({R_mult}× R_min)<br>"
            f"• N_actual = <strong>{gil['N_actual_int']} theoretical stages</strong> "
            f"({gil['N_actual']:.2f} exact)<br>"
            f"• Feed tray = Stage <strong>{kirk['feed_tray_from_top']}</strong> from top "
            f"({kirk['Nr']:.0f} rectifying + {kirk['Ns']:.0f} stripping)",
            "success",
        ), unsafe_allow_html=True)

    with tab2:
        st.markdown('<h3 class="shortcut-tab-heading">Gilliland Correlation — Interactive Chart</h3>', unsafe_allow_html=True)
        R_min_val = und["R_min"]
        mult_range = np.linspace(1.01, 3.5, 300)
        R_range, N_range = [], []
        for m in mult_range:
            try:
                g = gilliland(fen["N_min"], R_min_val, m * R_min_val)
                R_range.append(m * R_min_val)
                N_range.append(g["N_actual"])
            except Exception:
                pass

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=R_range, y=N_range, mode="lines",
            name="Gilliland Curve",
            line=dict(color="#00b4d8", width=3.2),
        ))
        fig.add_trace(go.Scatter(
            x=[R], y=[gil["N_actual"]],
            mode="markers", name=f"Design Point (R={R:.3f}, N={gil['N_actual']:.1f})",
            marker=dict(color="#f8d477", size=16, symbol="star", line=dict(color="#ffffff", width=1)),
        ))
        fig.add_vline(
            x=R_min_val, line_dash="dot", line_color="#ff5b6e", line_width=3,
            annotation_text=f"Rmin={R_min_val:.3f}", annotation_font_color="#ff5b6e",
        )
        fig.add_hline(
            y=fen["N_min"], line_dash="dot", line_color="#f8d477", line_width=3,
            annotation_text=f"Nmin={fen['N_min']:.2f}", annotation_font_color="#f8d477",
        )
        fig.add_vrect(
            x0=R_min_val * 1.1, x1=R_min_val * 1.5,
            fillcolor="rgba(34,197,94,0.10)", line_width=0,
            annotation_text="Recommended R/Rmin range", annotation_position="top left",
        )

        fig.update_layout(
            template="plotly_dark", paper_bgcolor="#0a0e14", plot_bgcolor="#111827",
            font=dict(family="Barlow", color="#e2e8f0"),
            xaxis=dict(title="Reflux Ratio R", gridcolor="#1e3a5f"),
            yaxis=dict(title="Number of Theoretical Stages N", gridcolor="#1e3a5f"),
            legend=dict(bgcolor="#111827", bordercolor="#1e3a5f"),
            height=460, margin=dict(t=20, b=50),
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(_context_box(
            "Reading the chart",
            "As R increases beyond R<sub>min</sub>, fewer stages are required but operating cost "
            "increases. A practical R is usually 1.1–1.5× R<sub>min</sub>, where the curve bends "
            "and balances capital cost against utilities.",
            "info",
        ), unsafe_allow_html=True)

    with tab3:
        st.markdown('<h3 class="shortcut-tab-heading">Complete Shortcut Calculation Summary</h3>', unsafe_allow_html=True)
        summary = {
            "Parameter": [
                "Light Component", "Heavy Component",
                "Relative Volatility α (avg)", "Feed Condition", "Feed q-value",
                "--- Fenske ---", "Minimum Stages N_min (incl. reboiler)", "Minimum Stages N_min (excl. reboiler)",
                "--- Underwood ---", "Underwood root θ", "Minimum Reflux Ratio R_min", "Minimum Vapour Rate V_min",
                "--- Gilliland ---", "R/R_min multiplier", "Operating Reflux Ratio R",
                "Gilliland X parameter", "Gilliland Y parameter",
                "Actual Theoretical Stages N (exact)", "Actual Theoretical Stages N (rounded)",
                "--- Kirkbride ---", "Rectifying Stages Nr", "Stripping Stages Ns",
                "Feed Tray from Top (Nf)", "Nr/Ns ratio",
                "--- Material Balance ---", "Distillate Flow D [kmol/h]", "Bottoms Flow B [kmol/h]",
                "D/F ratio", "B/F ratio",
            ],
            "Value": [
                light, heavy,
                f"{alpha:.4f}", feed_cond, f"{q:.4f}",
                "—", f"{fen['N_min']:.3f}", f"{fen['N_min_excl_reboiler']:.3f}",
                "—", f"{und['theta']:.6f}", f"{und['R_min']:.4f}", f"{und['V_min']:.4f}",
                "—", f"{R_mult}", f"{R:.4f}",
                f"{gil['X_gilliland']:.5f}", f"{gil['Y_gilliland']:.5f}",
                f"{gil['N_actual']:.3f}", f"{gil['N_actual_int']}",
                "—", f"{kirk['Nr']:.2f}", f"{kirk['Ns']:.2f}",
                f"{kirk['feed_tray_from_top']}", f"{kirk['Nr_over_Ns']:.4f}",
                "—", f"{mb['D']:.3f}", f"{mb['B']:.3f}",
                f"{mb['D_over_F']:.4f}", f"{mb['B_over_F']:.4f}",
            ],
        }
        st.markdown(_summary_table_html(summary), unsafe_allow_html=True)

    st.markdown("<div class='eng-divider'></div>", unsafe_allow_html=True)
    if st.button("💾 Save Shortcut Results", type="primary", use_container_width=False):
        mb2 = material_balance(F, z_F, x_D, x_B)
        R2 = round(R_mult * und["R_min"], 6)
        gil2 = gilliland(fen["N_min"], und["R_min"], R2)
        kirk2 = kirkbride(gil2["N_actual_int"], z_F, x_D, x_B, mb2["B"], mb2["D"])

        st.session_state.shortcut = {
            "alpha": alpha, "q": q, "R_min": und["R_min"],
            "R": R2, "R_mult": R_mult,
            "N_min": fen["N_min"],
            "N_min_excl_reboiler": fen["N_min_excl_reboiler"],
            "N_actual": gil2["N_actual"],
            "N_actual_int": gil2["N_actual_int"],
            "X_gilliland": gil2["X_gilliland"],
            "Y_gilliland": gil2["Y_gilliland"],
            "Nr": kirk2["Nr"], "Ns": kirk2["Ns"],
            "feed_tray": kirk2["feed_tray_from_top"],
            "NF": kirk2["feed_tray_from_top"],
            "D": mb2["D"], "B": mb2["B"],
            "theta": und["theta"],
            "V_min": und["V_min"],
        }

        col_type_saved = st.session_state.get("column_type", None)
        if col_type_saved == "tray":
            st.success(
                f"✅ Shortcut saved! N = {gil2['N_actual_int']} theoretical stages. "
                "Next → McCabe-Thiele → Tray Design → Column Diameter → Column Height"
            )
        elif col_type_saved == "packed":
            HETP_example = 0.35
            H_example = round(gil2["N_actual_int"] * HETP_example, 2)
            st.success(
                f"✅ Shortcut saved! N_theoretical = {gil2['N_actual_int']} stages. "
                f"For packed column: Packed height = {gil2['N_actual_int']} × HETP. "
                f"Example with HETP=0.35 m: height ≈ {H_example} m. "
                "Next → Packing Design → Column Diameter (Packed) → Column Height (Packed)"
            )
        else:
            st.success(
                f"✅ Shortcut saved! N = {gil2['N_actual_int']} theoretical stages. "
                "Select column type, then proceed to column-specific sections."
            )
