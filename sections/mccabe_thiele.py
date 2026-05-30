"""sections/mccabe_thiele.py - Interactive McCabe-Thiele Diagram"""
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from calculations.distillation_calc import mccabe_thiele_stages


def _metric_cards_html(cards):
    html_cards = []
    for label, value, unit in cards:
        unit_html = f'<span class="mccabe-metric-unit">{unit}</span>' if unit else ""
        html_cards.append(
            '<div class="mccabe-metric-card">'
            f'<div class="mccabe-metric-label">{label}</div>'
            f'<div class="mccabe-metric-value">{value}{unit_html}</div>'
            '</div>'
        )
    return '<div class="mccabe-metric-grid">' + ''.join(html_cards) + '</div>'


def _context_box(title, body, tone="info"):
    colors = {
        "info": "#00b4d8",
        "warn": "#f8d477",
        "success": "#22c55e",
        "danger": "#ff5b6e",
    }
    color = colors.get(tone, colors["info"])
    return (
        f'<div class="mccabe-context-box" style="border-left-color:{color};">'
        f'<div class="mccabe-context-title" style="color:{color};">{title}</div>'
        f'{body}'
        '</div>'
    )


def _calc_box(title, body, border="#00b4d8"):
    return (
        f'<div class="formula-box mccabe-calc-box" style="border-left-color:{border} !important;">'
        f'<div class="formula-title">{title}</div>'
        f'{body}'
        '</div><div class="mccabe-calc-separator"></div>'
    )


def _stage_table_html(stages):
    rows = []
    for row in stages:
        rows.append(
            "<tr>"
            f"<td>{row['stage']}</td>"
            f"<td>{row['x']:.6f}</td>"
            f"<td>{row['y']:.6f}</td>"
            f"<td>{row['section'].title()}</td>"
            "</tr>"
        )
    return (
        '<table class="mccabe-stage-table">'
        '<thead><tr><th>Stage No.</th><th>x liquid</th><th>y vapour</th><th>Section</th></tr></thead>'
        '<tbody>' + ''.join(rows) + '</tbody></table>'
    )


def render():
    st.markdown("""
    <div class="section-header">
        <h1>📈 McCabe-Thiele Method</h1>
        <p>Interactive x-y equilibrium diagram — common for both Tray &amp; Packed columns.
        Tray column: N_theoretical ÷ efficiency = actual trays.
        Packed column: N_theoretical × HETP = packing height.</p>
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
    .mccabe-tab-heading {
        color: #f8d477 !important;
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 2.05rem !important;
        font-weight: 900 !important;
        letter-spacing: 0;
        line-height: 1.12;
        margin: 0.45rem 0 1rem 0;
        text-shadow: 0 0 14px rgba(248, 212, 119, 0.24);
    }
    .mccabe-input-label {
        color: #ff5b6e !important;
        font-weight: 900 !important;
        letter-spacing: 0.2px;
        margin: 0 0 0.42rem 0.05rem;
        text-shadow: 0 0 10px rgba(239, 68, 68, 0.22);
    }
    .mccabe-live-note {
        color: #dbeafe;
        background: linear-gradient(135deg, rgba(8, 14, 24, 0.98), rgba(15, 23, 42, 0.94));
        border: 1px solid rgba(0, 180, 216, 0.42);
        border-left: 4px solid #22c55e;
        border-radius: 8px;
        padding: 0.78rem 1rem;
        margin: -0.25rem 0 0.9rem 0;
        font-weight: 800;
        line-height: 1.55;
        box-shadow: 0 10px 24px rgba(0,0,0,0.15);
    }
    .mccabe-live-note strong {
        color: #22c55e;
        font-weight: 900;
    }
    .mccabe-context-box {
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
    .mccabe-context-title {
        color: #f8d477;
        font-weight: 900;
        margin-bottom: 0.35rem;
    }
    .mccabe-calc-box {
        color: #eaf6ff !important;
        background: linear-gradient(135deg, rgba(8, 14, 24, 0.99), rgba(15, 23, 42, 0.97)) !important;
        border: 1px solid rgba(0, 180, 216, 0.44) !important;
        border-left: 4px solid #00b4d8 !important;
        box-shadow: 0 0 0 1px rgba(255,255,255,0.03), 0 12px 28px rgba(0,0,0,0.18);
        font-size: 1.02rem !important;
        line-height: 1.75;
    }
    .mccabe-calc-box b,
    .mccabe-calc-box strong {
        color: #ffffff !important;
        font-weight: 900 !important;
    }
    .mccabe-calc-box .formula-title {
        color: #f8d477 !important;
        font-size: 1.08rem !important;
        font-weight: 900 !important;
        letter-spacing: 0.2px;
        margin-bottom: 0.55rem;
    }
    .mccabe-calc-line {
        margin: 0.28rem 0;
        padding: 0.46rem 0.62rem;
        border-radius: 6px;
        border-left: 3px solid rgba(148, 163, 184, 0.35);
        background: rgba(255, 255, 255, 0.025);
    }
    .mccabe-calc-note {
        color: #dbeafe;
        font-weight: 750;
    }
    .mccabe-calc-equation {
        color: #38bdf8;
        border-left-color: #38bdf8;
        font-family: 'Share Tech Mono', monospace;
        font-weight: 900;
    }
    .mccabe-calc-substitution {
        color: #f8d477;
        border-left-color: #f8d477;
        font-family: 'Share Tech Mono', monospace;
        font-weight: 900;
    }
    .mccabe-calc-result {
        color: #22c55e;
        border-left-color: #22c55e;
        font-weight: 900;
    }
    .mccabe-calc-label {
        color: #ff5b6e;
        font-weight: 900;
    }
    .mccabe-calc-value {
        color: #f8d477;
        font-weight: 900;
    }
    .mccabe-calc-final {
        color: #22c55e;
        font-weight: 900;
    }
    .mccabe-calc-box .mccabe-calc-line strong {
        color: inherit !important;
    }
    .mccabe-calc-separator {
        border-top: 2px dotted rgba(248, 212, 119, 0.58);
        margin: 1.15rem 0 1.35rem 0;
        height: 1px;
    }
    .mccabe-metric-grid {
        display: grid;
        grid-template-columns: repeat(5, minmax(0, 1fr));
        gap: 1rem;
        margin: 1.05rem 0 1.35rem 0;
    }
    .mccabe-metric-card {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.98), rgba(8, 14, 24, 0.98));
        border: 1px solid rgba(0, 180, 216, 0.48);
        border-radius: 8px;
        padding: 1rem 1.05rem;
        min-height: 118px;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.04), 0 10px 24px rgba(0,0,0,0.16);
    }
    .mccabe-metric-label {
        color: #ff5b6e !important;
        font-size: 0.94rem;
        font-weight: 900;
        line-height: 1.3;
        margin-bottom: 0.55rem;
        text-shadow: 0 0 10px rgba(239, 68, 68, 0.24);
    }
    .mccabe-metric-value {
        color: #00d4ff;
        font-family: 'Share Tech Mono', monospace;
        font-size: clamp(1.55rem, 2.2vw, 2.3rem);
        font-weight: 900;
        letter-spacing: 0;
        line-height: 1.05;
        word-break: break-word;
        text-shadow: 0 0 14px rgba(0, 180, 216, 0.18);
    }
    .mccabe-metric-unit {
        color: #dbeafe;
        font-family: 'Barlow', sans-serif;
        font-size: 0.86rem;
        font-weight: 800;
        margin-left: 0.2rem;
    }
    .mccabe-stage-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        margin-top: 0.5rem;
        overflow: hidden;
        border: 1px solid rgba(0, 180, 216, 0.45);
        border-radius: 8px;
        background: #071018;
        color: #f8fbff;
        font-size: 0.96rem;
    }
    .mccabe-stage-table th {
        background: #1b2028;
        color: #f8d477;
        font-weight: 900;
        text-align: left;
        padding: 0.74rem 0.7rem;
        border-bottom: 1px solid rgba(148, 163, 184, 0.25);
    }
    .mccabe-stage-table td {
        padding: 0.68rem 0.7rem;
        border-bottom: 1px solid rgba(148, 163, 184, 0.14);
        color: #f8fbff;
    }
    .mccabe-stage-table tr:last-child td {
        border-bottom: 0;
    }
    .mccabe-stage-table td:first-child,
    .mccabe-stage-table td:last-child {
        color: #00d4ff;
        font-weight: 900;
    }
    div[role="checkbox"] label p {
        color: #f8fbff !important;
        font-weight: 900 !important;
    }
    @media (max-width: 1100px) {
        .mccabe-metric-grid {
            grid-template-columns: repeat(3, minmax(0, 1fr));
        }
    }
    @media (max-width: 700px) {
        .mccabe-metric-grid {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    col_type = st.session_state.get("column_type", None)
    if col_type == "tray":
        st.markdown(_context_box(
            "Tray Column mode",
            "N_theoretical from this diagram ÷ tray efficiency gives <strong>actual trays</strong>. "
            "This value is used in Tray Design and Column Height.",
            "info",
        ), unsafe_allow_html=True)
    elif col_type == "packed":
        shortcut_tmp = st.session_state.get("shortcut", {})
        N_tmp = shortcut_tmp.get("N_actual_int", "—")
        st.markdown(_context_box(
            "Packed Column mode",
            f"N_theoretical from this diagram × HETP gives <strong>packed bed height</strong>. "
            f"Current shortcut N = <strong>{N_tmp}</strong> stages.",
            "success",
        ), unsafe_allow_html=True)
    else:
        st.markdown(_context_box(
            "Column type not selected yet",
            "Select column type first to see how N_theoretical is converted into trays or packed height.",
            "warn",
        ), unsafe_allow_html=True)

    feed = st.session_state.get("feed", {})
    thermo = st.session_state.get("thermo", {})
    shortcut = st.session_state.get("shortcut", {})

    if not feed:
        st.warning("⚠️ Complete **Feed Specifications** first.")
        return

    x_D = feed["x_D"]
    x_B = feed["x_B"]
    z_F = feed["z_F"]
    light = feed.get("light", "Light")
    heavy = feed.get("heavy", "Heavy")
    alpha = shortcut.get("alpha") or thermo.get("alpha_avg", 2.5)
    q = shortcut.get("q", feed.get("q", 1.0))
    R_def = shortcut.get("R", shortcut.get("R_min", 1.5) * 1.2) if shortcut else 2.0

    control_defaults = {
        "mccabe_alpha_control": float(round(alpha, 4)),
        "mccabe_R_control": float(round(R_def, 4)),
        "mccabe_q_control": float(round(q, 4)),
        "mccabe_show_stage_numbers": True,
    }
    for key, value in control_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    alpha_inp = float(st.session_state["mccabe_alpha_control"])
    R_inp = float(st.session_state["mccabe_R_control"])
    q_inp = float(st.session_state["mccabe_q_control"])
    show_stages = bool(st.session_state["mccabe_show_stage_numbers"])

    result = mccabe_thiele_stages(alpha_inp, R_inp, x_D, x_B, z_F, q_inp)
    stages = result["stages"]
    n_stages = result["n_stages"]
    x_int = result["x_int"]
    y_int = result["y_int"]

    x_eq_arr = np.linspace(0, 1, 500)
    y_eq = x_eq_arr * alpha_inp / (1 + (alpha_inp - 1) * x_eq_arr)

    slope_rect = R_inp / (R_inp + 1)
    intercept_rect = x_D / (R_inp + 1)
    x_rect_full = np.array([0.0, x_D])
    y_rect_full = slope_rect * x_rect_full + intercept_rect

    if abs(q_inp - 1.0) < 0.001:
        x_qline = [z_F, z_F]
        y_qline = [0.0, 1.0]
        q_line_text = f"q = 1 saturated liquid → vertical q-line at x = zF = {z_F:.4f}"
        q_slope_text = "vertical"
        q_intercept_text = "—"
    else:
        slope_q = q_inp / (q_inp - 1)
        intercept_q = -z_F / (q_inp - 1)
        x_at_y0 = -intercept_q / slope_q if slope_q != 0 else 0
        x_at_y1 = (1 - intercept_q) / slope_q if slope_q != 0 else z_F
        x_start = max(0.0, min(x_at_y0, x_at_y1) - 0.05)
        x_end = min(1.0, max(x_at_y0, x_at_y1) + 0.05)
        x_qline = np.linspace(x_start, x_end, 200)
        y_qline = slope_q * x_qline + intercept_q
        mask = (y_qline >= 0.0) & (y_qline <= 1.0)
        x_qline = x_qline[mask]
        y_qline = y_qline[mask]
        if len(x_qline) > 0:
            x_qline = np.concatenate([[(-intercept_q / slope_q)], x_qline, [(1 - intercept_q) / slope_q]])
            y_qline = np.concatenate([[0.0], y_qline, [1.0]])
            mask2 = (x_qline >= 0) & (x_qline <= 1) & (y_qline >= 0) & (y_qline <= 1)
            x_qline = x_qline[mask2]
            y_qline = y_qline[mask2]
        q_line_text = f"y = [{q_inp:.4f}/({q_inp:.4f}−1)]x − [{z_F:.4f}/({q_inp:.4f}−1)]"
        q_slope_text = f"{slope_q:.4f}"
        q_intercept_text = f"{intercept_q:.4f}"

    if abs(x_int - x_B) > 1e-6:
        slope_strip = (y_int - x_B) / (x_int - x_B)
        intercept_strip = x_B - slope_strip * x_B
        x_strip_full = np.array([0.0, x_int])
        y_strip_full = np.clip(slope_strip * x_strip_full + intercept_strip, 0, 1)
    else:
        slope_strip = result["slope_stripping"]
        intercept_strip = x_B * (1 - slope_strip)
        x_strip_full = np.array([x_B, x_int])
        y_strip_full = np.array([x_B, y_int])

    stage_x = [x_D]
    stage_y = [x_D]
    for i, s in enumerate(stages):
        stage_x.append(s["x"])
        stage_y.append(s["y"])
        if i == len(stages) - 1:
            break
        next_s = stages[i + 1]
        stage_x.append(s["x"])
        stage_y.append(next_s["y"] if i + 1 < len(stages) else x_B)

    st.markdown('<h3 class="mccabe-tab-heading">Required Calculations Before Graph</h3>', unsafe_allow_html=True)
    st.markdown(_context_box(
        "Design basis",
        f"Components: <strong>{light} / {heavy}</strong> &nbsp;|&nbsp; "
        f"xD = <strong>{x_D:.4f}</strong> &nbsp;|&nbsp; "
        f"xB = <strong>{x_B:.4f}</strong> &nbsp;|&nbsp; "
        f"zF = <strong>{z_F:.4f}</strong> &nbsp;|&nbsp; "
        f"α = <strong>{alpha_inp:.4f}</strong> &nbsp;|&nbsp; "
        f"R = <strong>{R_inp:.4f}</strong> &nbsp;|&nbsp; "
        f"q = <strong>{q_inp:.4f}</strong>",
        "info",
    ), unsafe_allow_html=True)

    st.markdown(_calc_box(
        "1. Equilibrium Curve",
        '<div class="mccabe-calc-line mccabe-calc-note">'
        '<span class="mccabe-calc-label">Basis:</span> constant relative volatility model</div>'
        '<div class="mccabe-calc-line mccabe-calc-equation">'
        'Equation: y = αx / [1 + (α − 1)x]</div>'
        f'<div class="mccabe-calc-line mccabe-calc-substitution">'
        f'Substitute: α = {alpha_inp:.4f} → y = {alpha_inp:.4f}x / [1 + ({alpha_inp:.4f} − 1)x]</div>'
        '<div class="mccabe-calc-line mccabe-calc-result">'
        'Result used: equilibrium curve for horizontal stage steps</div>',
    ), unsafe_allow_html=True)

    st.markdown(_calc_box(
        "2. Rectifying Operating Line",
        '<div class="mccabe-calc-line mccabe-calc-equation">'
        'Equation: y = [R/(R+1)]x + xD/(R+1)</div>'
        f'<div class="mccabe-calc-line mccabe-calc-substitution">'
        f'Substitute: R = {R_inp:.4f}, xD = {x_D:.4f}</div>'
        f'<div class="mccabe-calc-line mccabe-calc-substitution">'
        f'Slope = R/(R+1) = {R_inp:.4f}/({R_inp:.4f}+1) = {slope_rect:.4f}</div>'
        f'<div class="mccabe-calc-line mccabe-calc-substitution">'
        f'Intercept = xD/(R+1) = {x_D:.4f}/({R_inp:.4f}+1) = {intercept_rect:.4f}</div>'
        f'<div class="mccabe-calc-line mccabe-calc-result">'
        f'Final line used: y = {slope_rect:.4f}x + {intercept_rect:.4f}</div>',
        "#22c55e",
    ), unsafe_allow_html=True)

    st.markdown(_calc_box(
        "3. Feed q-line and Operating-Line Intersection",
        '<div class="mccabe-calc-line mccabe-calc-equation">'
        'Equation: y = [q/(q−1)]x − zF/(q−1)</div>'
        f'<div class="mccabe-calc-line mccabe-calc-substitution">'
        f'Substitute: q = {q_inp:.4f}, zF = {z_F:.4f}</div>'
        f'<div class="mccabe-calc-line mccabe-calc-substitution">{q_line_text}</div>'
        f'<div class="mccabe-calc-line mccabe-calc-substitution">'
        f'q-line slope = {q_slope_text}, intercept = {q_intercept_text}</div>'
        '<div class="mccabe-calc-line mccabe-calc-note">'
        'Intersection is found by solving q-line = rectifying line.</div>'
        f'<div class="mccabe-calc-line mccabe-calc-result">'
        f'Feed switch point: (x_int, y_int) = ({x_int:.4f}, {y_int:.4f})</div>',
        "#c084fc",
    ), unsafe_allow_html=True)

    st.markdown(_calc_box(
        "4. Stripping Operating Line",
        '<div class="mccabe-calc-line mccabe-calc-note">'
        'Line passes through bottoms point (xB, xB) and feed intersection point.</div>'
        '<div class="mccabe-calc-line mccabe-calc-equation">'
        'Slope = (y_int − xB)/(x_int − xB)</div>'
        f'<div class="mccabe-calc-line mccabe-calc-substitution">'
        f'Substitute: ({y_int:.4f} − {x_B:.4f}) / ({x_int:.4f} − {x_B:.4f}) = {slope_strip:.4f}</div>'
        f'<div class="mccabe-calc-line mccabe-calc-substitution">'
        f'Intercept = xB − slope×xB = {x_B:.4f} − ({slope_strip:.4f}×{x_B:.4f}) = {intercept_strip:.4f}</div>'
        f'<div class="mccabe-calc-line mccabe-calc-result">'
        f'Final line used: y = {slope_strip:.4f}x + {intercept_strip:.4f}</div>',
        "#f59e0b",
    ), unsafe_allow_html=True)

    st.markdown(_metric_cards_html([
        ("Estimated theoretical stages", f"{n_stages}", ""),
        ("Rectifying stages", f"{result['n_rectifying']}", ""),
        ("Stripping stages", f"{result['n_stripping']}", ""),
        ("Feed switch point", f"({x_int:.3f}, {y_int:.3f})", ""),
        ("R / α / q", f"{R_inp:.2f} / {alpha_inp:.2f} / {q_inp:.2f}", ""),
    ]), unsafe_allow_html=True)

    st.markdown('<h3 class="mccabe-tab-heading">McCabe-Thiele Diagram</h3>', unsafe_allow_html=True)
    st.markdown(
        '<div class="mccabe-live-note"><strong>Live simulation controls:</strong> '
        'adjust α, reflux ratio R, feed q-value, or stage labels here and the diagram below updates instantly.</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<h3 class="mccabe-tab-heading">Diagram Controls</h3>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown('<div class="mccabe-input-label">Relative Volatility α</div>', unsafe_allow_html=True)
        alpha_inp = st.number_input(
            "Relative Volatility α",
            min_value=1.05,
            max_value=20.0,
            step=0.01,
            format="%.4f",
            key="mccabe_alpha_control",
            label_visibility="collapsed",
        )
    with c2:
        st.markdown('<div class="mccabe-input-label">Reflux Ratio R</div>', unsafe_allow_html=True)
        R_inp = st.number_input(
            "Reflux Ratio R",
            min_value=0.01,
            max_value=50.0,
            step=0.05,
            format="%.4f",
            key="mccabe_R_control",
            label_visibility="collapsed",
        )
    with c3:
        st.markdown('<div class="mccabe-input-label">Feed q-value</div>', unsafe_allow_html=True)
        q_inp = st.number_input(
            "Feed q-value",
            min_value=-2.0,
            max_value=3.0,
            step=0.05,
            format="%.4f",
            key="mccabe_q_control",
            label_visibility="collapsed",
        )
    with c4:
        st.markdown('<div class="mccabe-input-label">Stage Labels</div>', unsafe_allow_html=True)
        show_stages = st.checkbox("Show Stage Numbers", key="mccabe_show_stage_numbers")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[0, 1], y=[0, 1], mode="lines",
        name="y = x (diagonal)",
        line=dict(color="#e2e8f0", dash="dash", width=3.2),
        opacity=0.78,
    ))
    fig.add_trace(go.Scatter(
        x=x_eq_arr, y=y_eq, mode="lines",
        name=f"Equilibrium curve (α={alpha_inp:.3f})",
        line=dict(color="#00b4d8", width=3.3),
    ))
    fig.add_trace(go.Scatter(
        x=x_rect_full, y=y_rect_full, mode="lines",
        name=f"Rectifying OL slope={slope_rect:.3f}",
        line=dict(color="#22c55e", width=3),
    ))
    fig.add_trace(go.Scatter(
        x=x_strip_full, y=y_strip_full, mode="lines",
        name=f"Stripping OL slope={result['slope_stripping']:.3f}",
        line=dict(color="#f59e0b", width=3),
    ))
    fig.add_trace(go.Scatter(
        x=x_qline, y=y_qline, mode="lines",
        name=f"q-line (q={q_inp:.2f})",
        line=dict(color="#c084fc", width=3, dash="dot"),
    ))
    fig.add_trace(go.Scatter(
        x=stage_x, y=stage_y, mode="lines",
        name=f"Stages ({n_stages} theoretical)",
        line=dict(color="#ff5b6e", width=2.6),
    ))
    fig.add_trace(go.Scatter(
        x=[x_D, x_B, z_F, x_int],
        y=[x_D, x_B, z_F, y_int],
        mode="markers+text",
        name="Key Points",
        marker=dict(
            color=["#22c55e", "#ef4444", "#f8d477", "#c084fc"],
            size=[13, 13, 13, 11], symbol="circle",
            line=dict(width=1.5, color="#fff"),
        ),
        text=[f"x_D={x_D:.3f}", f"x_B={x_B:.3f}", f"z_F={z_F:.3f}", f"P({x_int:.3f},{y_int:.3f})"],
        textposition=["top right", "bottom left", "top center", "top right"],
        textfont=dict(size=11, color="#e2e8f0"),
    ))

    if show_stages:
        for i, s in enumerate(stages):
            fig.add_annotation(
                x=s["x"], y=s["y"], text=str(i + 1), showarrow=False,
                font=dict(size=9, color="#f8d477"),
                bgcolor="rgba(0,0,0,0.62)", borderpad=2,
            )

    for xval, label, color in [
        (x_D, f"x_D={x_D:.3f}", "#22c55e"),
        (x_B, f"x_B={x_B:.3f}", "#ef4444"),
        (z_F, f"z_F={z_F:.3f}", "#c084fc"),
    ]:
        fig.add_shape(
            type="line", x0=xval, x1=xval, y0=0, y1=xval,
            line=dict(color=color, width=2.4, dash="dot"),
            layer="below",
        )
        fig.add_annotation(
            x=xval, y=-0.01, text=label, showarrow=False,
            font=dict(size=10, color=color),
            xanchor="center", yanchor="top",
        )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0a0e14",
        plot_bgcolor="#0d1520",
        font=dict(family="Barlow, sans-serif", color="#e2e8f0"),
        xaxis=dict(
            title=f"x — liquid mole fraction ({light})",
            range=[-0.01, 1.01],
            gridcolor="#1e3a5f", zeroline=True,
            zerolinecolor="#64748b", zerolinewidth=1.5,
            tickformat=".2f",
        ),
        yaxis=dict(
            title=f"y — vapour mole fraction ({light})",
            range=[-0.01, 1.01],
            gridcolor="#1e3a5f", zeroline=True,
            zerolinecolor="#64748b", zerolinewidth=1.5,
            tickformat=".2f",
        ),
        legend=dict(
            bgcolor="#111827", bordercolor="#1e3a5f",
            font=dict(size=11), x=0.01, y=0.99,
            xanchor="left", yanchor="top",
        ),
        height=620,
        margin=dict(t=20, b=50, l=60, r=20),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='eng-divider'></div>", unsafe_allow_html=True)
    st.markdown(_metric_cards_html([
        ("Theoretical Stages", f"{n_stages}", ""),
        ("Rectifying Stages", f"{result['n_rectifying']}", ""),
        ("Stripping Stages", f"{result['n_stripping']}", ""),
        ("Reflux Ratio R", f"{R_inp:.3f}", ""),
        ("Intersection (x,y)", f"({x_int:.3f}, {y_int:.3f})", ""),
    ]), unsafe_allow_html=True)

    if col_type == "tray":
        eff = st.session_state.get("tray_design", {}).get("tray_efficiency", 0.7)
        n_actual = int(np.ceil(n_stages / eff)) if eff > 0 else "—"
        st.markdown(_context_box(
            "Tray Column result",
            f"N_theoretical = <strong>{n_stages}</strong> ÷ tray efficiency "
            f"<strong>{eff:.0%}</strong> → <strong>{n_actual} actual trays</strong>",
            "info",
        ), unsafe_allow_html=True)
    elif col_type == "packed":
        hetp = st.session_state.get("packing_design", {}).get("HETP", None)
        if hetp:
            z = round(n_stages * hetp, 2)
            body = (
                f"N_theoretical = <strong>{n_stages}</strong> × HETP "
                f"<strong>{hetp} m</strong> → <strong>{z} m packing height</strong>"
            )
        else:
            body = (
                f"N_theoretical = <strong>{n_stages}</strong>. "
                "Set HETP in Packing Design to calculate packed height."
            )
        st.markdown(_context_box("Packed Column result", body, "success"), unsafe_allow_html=True)

    with st.expander("📋 Stage-by-Stage Table"):
        st.markdown(_stage_table_html(result["stages"]), unsafe_allow_html=True)

    if shortcut and shortcut.get("N_actual_int"):
        diff = abs(n_stages - shortcut["N_actual_int"])
        if diff <= 2:
            st.markdown(_context_box(
                "Consistency check",
                f"McCabe-Thiele (<strong>{n_stages}</strong>) agrees with Gilliland shortcut "
                f"(<strong>{shortcut['N_actual_int']}</strong>) — Δ = {diff} stage(s).",
                "success",
            ), unsafe_allow_html=True)
        else:
            st.markdown(_context_box(
                "Consistency check",
                f"McCabe-Thiele ({n_stages}) differs from Gilliland ({shortcut['N_actual_int']}). "
                "Check α or R for consistency.",
                "warn",
            ), unsafe_allow_html=True)

    st.markdown("<div class='eng-divider'></div>", unsafe_allow_html=True)
    if st.button("💾 Save McCabe-Thiele Results", type="primary"):
        st.session_state.mccabe = {
            "n_stages": n_stages,
            "n_rectifying": result["n_rectifying"],
            "n_stripping": result["n_stripping"],
            "R": R_inp,
            "alpha": alpha_inp,
            "q": q_inp,
            "stages": result["stages"],
            "x_int": result["x_int"],
            "y_int": result["y_int"],
        }
        st.success("✅ McCabe-Thiele saved! Now proceed to Tray Design or Packing Design.")
