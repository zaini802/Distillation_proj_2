"""Design validation, sensitivity analysis, and saved case management."""
import json
import math
import os
import re
from copy import deepcopy
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from sections.phase3_style import render_phase3_style


APP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CASE_DIR = os.path.join(APP_ROOT, "saved_cases")
CASE_KEYS = [
    "feed",
    "thermo",
    "column_type",
    "shortcut",
    "mccabe",
    "rigorous",
    "tray_design",
    "packing_design",
    "diameter",
    "height",
    "reboiler",
    "condenser",
    "pressure_drop",
    "mechanical",
    "internals",
    "instrumentation",
    "energy",
]


def render():
    render_phase3_style()
    _render_manager_style()

    st.markdown(
        """
        <div class="section-header">
            <h1>Design Manager</h1>
            <p>Final design health check, reflux sensitivity/optimization, and save/load case management.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tabs = st.tabs(["Design Health Check", "Sensitivity & Optimization", "Save / Load Cases"])
    with tabs[0]:
        _render_health_check()
    with tabs[1]:
        _render_sensitivity()
    with tabs[2]:
        _render_case_manager()


def evaluate_design_health(session_state=None):
    """Return health-score, detailed checks, and completion summary for current design."""
    s = session_state or st.session_state
    feed = s.get("feed", {})
    thermo = s.get("thermo", {})
    shortcut = s.get("shortcut", {})
    col_type = s.get("column_type", None)
    diameter = s.get("diameter", {})
    height = s.get("height", {})
    tray = s.get("tray_design", {})
    packing = s.get("packing_design", {})
    reboiler = s.get("reboiler", {})
    condenser = s.get("condenser", {})
    pressure = s.get("pressure_drop", {})
    mech = s.get("mechanical", {})
    energy = s.get("energy", {})

    checks = []

    def add(category, check, status, value, recommendation, severity="medium"):
        checks.append(
            {
                "Category": category,
                "Check": check,
                "Status": status,
                "Value": value,
                "Recommendation": recommendation,
                "Severity": severity,
            }
        )

    required = [
        ("Feed Specifications", bool(feed)),
        ("Thermodynamics", bool(thermo)),
        ("Column Type", col_type is not None),
        ("Shortcut Design", bool(shortcut)),
        ("McCabe-Thiele", bool(s.get("mccabe", {}))),
        ("Column Diameter", bool(diameter)),
        ("Column Height", bool(height)),
        ("Reboiler", bool(reboiler)),
        ("Condenser", bool(condenser)),
        ("Pressure Drop", bool(pressure)),
        ("Mechanical", bool(mech)),
        ("Energy & Economics", bool(energy)),
    ]
    for name, done in required:
        add(
            "Completeness",
            name,
            "Pass" if done else "Fail",
            "Complete" if done else "Missing",
            "Proceed" if done else f"Complete the {name} section.",
            "high" if not done else "low",
        )

    if feed:
        zf = _to_float(feed.get("z_F"))
        xd = _to_float(feed.get("x_D"))
        xb = _to_float(feed.get("x_B"))
        valid_bounds = all(v is not None and 0 < v < 1 for v in [zf, xd, xb])
        ordering_ok = valid_bounds and xb < zf < xd
        add(
            "Process basis",
            "Composition order xB < zF < xD",
            "Pass" if ordering_ok else "Fail",
            _format_triplet("xB/zF/xD", xb, zf, xd),
            "Keep bottoms leaner than feed and distillate richer than feed.",
            "high",
        )

    alpha = _to_float(shortcut.get("alpha", thermo.get("alpha_avg")))
    if alpha is not None:
        if alpha <= 1.05:
            status = "Fail"
            rec = "Relative volatility is too close to 1. Check VLE model or consider special distillation."
        elif alpha < 1.5:
            status = "Warn"
            rec = "Separation is difficult; expect high stages/reflux and verify VLE carefully."
        else:
            status = "Pass"
            rec = "Relative volatility is acceptable for conventional distillation."
        add("Thermodynamics", "Relative volatility", status, f"{alpha:.3f}", rec, "high")

    r_min = _to_float(shortcut.get("R_min"))
    r = _to_float(shortcut.get("R"))
    if r_min is not None and r is not None:
        ratio = r / max(r_min, 1e-9)
        if r <= r_min:
            status = "Fail"
            rec = "Operating reflux must be greater than Rmin."
        elif ratio < 1.1:
            status = "Warn"
            rec = "Reflux is very close to Rmin; stage count and control sensitivity may be high."
        elif ratio > 2.0:
            status = "Warn"
            rec = "Reflux is high; check energy cost, condenser duty, reboiler duty, and flooding risk."
        else:
            status = "Pass"
            rec = "R/Rmin is in a practical preliminary design range."
        add("Shortcut design", "Operating reflux ratio", status, f"R/Rmin = {ratio:.2f}", rec, "high")

    n_actual = _to_float(shortcut.get("N_actual_int", shortcut.get("N_actual")))
    if n_actual is not None:
        if n_actual < 3:
            add("Shortcut design", "Stage count", "Warn", f"{n_actual:.1f}", "Very low stage count; verify specs and VLE.", "medium")
        elif n_actual > 80:
            add("Shortcut design", "Stage count", "Warn", f"{n_actual:.1f}", "Very high stage count; consider pressure, entrainer, or different separation route.", "medium")
        else:
            add("Shortcut design", "Stage count", "Pass", f"{n_actual:.1f}", "Stage count is within a normal screening range.", "low")

    d_col = _to_float(diameter.get("D_column_std_m", diameter.get("D_column_m")))
    h_total = _to_float(height.get("total_height_m"))
    if d_col is not None:
        add(
            "Column sizing",
            "Column diameter",
            "Pass" if d_col > 0 else "Fail",
            f"{d_col:.3f} m",
            "Diameter is available for downstream checks." if d_col > 0 else "Run column diameter sizing.",
            "high",
        )
    if d_col and h_total:
        hd = h_total / d_col
        if hd < 8:
            status = "Warn"
            rec = "H/D is low; check stage count, disengagement spaces, and mechanical assumptions."
        elif hd > 35:
            status = "Warn"
            rec = "H/D is high; consider larger diameter, split tower, or mechanical wind/seismic review."
        else:
            status = "Pass"
            rec = "H/D is within a reasonable preliminary range."
        add("Column sizing", "H/D ratio", status, f"{hd:.2f}", rec, "medium")

    flood_fraction = _to_float(diameter.get("flood_fraction", tray.get("flood_frac")))
    if flood_fraction is not None:
        if flood_fraction < 0.55:
            status = "Warn"
            rec = "Operating far below flooding; check weeping/turndown."
        elif flood_fraction > 0.85:
            status = "Warn"
            rec = "Operating too close to flooding; increase diameter or reduce vapor load."
        else:
            status = "Pass"
            rec = "Flooding fraction is in a practical design range."
        add("Hydraulics", "Flooding fraction", status, f"{flood_fraction:.2f}", rec, "high")

    if col_type == "tray" and tray:
        add(
            "Tray hydraulics",
            "Weeping check",
            "Pass" if tray.get("weeping_ok", True) else "Fail",
            "OK" if tray.get("weeping_ok", True) else "Risk",
            "Tray vapor velocity should stay above weeping velocity.",
            "high",
        )
    if col_type == "packed" and packing:
        dp = _to_float(packing.get("dP_tot_Pa"))
        if dp is not None:
            add(
                "Packed hydraulics",
                "Packing pressure drop",
                "Pass" if dp < 25000 else "Warn",
                f"{dp:.0f} Pa",
                "Check packing factor and gas load if pressure drop is high.",
                "medium",
            )

    q_reb = _to_float(reboiler.get("Q_reb_kW", energy.get("Q_reb_kW")))
    q_cond = _to_float(condenser.get("Q_cond_kW", energy.get("Q_cond_kW")))
    if q_reb is not None and q_cond is not None:
        ratio = q_reb / max(q_cond, 1e-9)
        add(
            "Energy",
            "Reboiler/condenser duty balance",
            "Pass" if 0.5 <= ratio <= 2.0 else "Warn",
            f"Qreb/Qcond = {ratio:.2f}",
            "Large mismatch may be justified, but verify latent heat and heat losses.",
            "medium",
        )

    if mech:
        t_shell = _to_float(mech.get("t_shell_mm"))
        add(
            "Mechanical",
            "Shell thickness",
            "Pass" if t_shell and t_shell > 0 else "Fail",
            f"{t_shell:.2f} mm" if t_shell else "Missing",
            "ASME shell thickness should be positive and include corrosion allowance.",
            "high",
        )

    score = _health_score(checks)
    completion = sum(done for _, done in required)
    return {
        "score": score,
        "checks": checks,
        "completion": completion,
        "total_required": len(required),
        "critical_count": sum(1 for c in checks if c["Status"] == "Fail"),
        "warning_count": sum(1 for c in checks if c["Status"] == "Warn"),
    }


def _render_health_check():
    result = evaluate_design_health()
    score = result["score"]
    badge = "Excellent" if score >= 85 else "Needs Review" if score >= 65 else "Incomplete"
    color = "#22c55e" if score >= 85 else "#f8d477" if score >= 65 else "#ff5b6e"

    st.markdown(
        f"""
        <div class="manager-hero" style="border-left-color:{color};">
            <div>
                <span>Design Health Score</span>
                <strong style="color:{color};">{score:.0f}%</strong>
            </div>
            <div>
                <span>Status</span>
                <strong style="color:{color};">{badge}</strong>
            </div>
            <div>
                <span>Completion</span>
                <strong>{result['completion']}/{result['total_required']}</strong>
            </div>
            <div>
                <span>Warnings / Critical</span>
                <strong>{result['warning_count']} / {result['critical_count']}</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    checks_df = pd.DataFrame(result["checks"])
    status_filter = st.multiselect(
        "Filter checks",
        ["Pass", "Warn", "Fail"],
        default=["Pass", "Warn", "Fail"],
    )
    filtered = checks_df[checks_df["Status"].isin(status_filter)]
    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Status": st.column_config.TextColumn("Status"),
            "Recommendation": st.column_config.TextColumn("Engineering recommendation"),
        },
    )

    st.markdown("### Action List")
    action_items = checks_df[checks_df["Status"].isin(["Warn", "Fail"])]
    if action_items.empty:
        st.success("All major validation checks are passing. The design is ready for report/export review.")
    else:
        for _, row in action_items.iterrows():
            st.markdown(
                f"""
                <div class="manager-action manager-{row['Status'].lower()}">
                    <b>{row['Category']} - {row['Check']}</b><br>
                    <span>{row['Recommendation']}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _render_sensitivity():
    feed = st.session_state.get("feed", {})
    shortcut = st.session_state.get("shortcut", {})
    thermo = st.session_state.get("thermo", {})
    energy = st.session_state.get("energy", {})
    diameter = st.session_state.get("diameter", {})
    height = st.session_state.get("height", {})

    if not feed or not shortcut:
        st.warning("Complete Feed Specifications and Shortcut Design first to run sensitivity analysis.")
        return

    r_min = max(_to_float(shortcut.get("R_min"), 0.4), 0.01)
    r_base = max(_to_float(shortcut.get("R"), r_min * 1.35), r_min * 1.01)
    alpha = max(_to_float(shortcut.get("alpha", thermo.get("alpha_avg")), 2.5), 1.01)
    n_min = max(_to_float(shortcut.get("N_min"), 3.0), 0.5)
    n_base = max(_to_float(shortcut.get("N_actual_int", shortcut.get("N_actual")), n_min + 2), n_min + 0.1)
    q_reb = max(_to_float(energy.get("Q_reb_kW"), _to_float(st.session_state.get("reboiler", {}).get("Q_reb_kW"), 500.0)), 1.0)
    q_cond = max(_to_float(energy.get("Q_cond_kW"), _to_float(st.session_state.get("condenser", {}).get("Q_cond_kW"), 450.0)), 1.0)
    d_base = max(_to_float(diameter.get("D_column_std_m", diameter.get("D_column_m")), 1.2), 0.1)
    h_base = max(_to_float(height.get("total_height_m"), 15.0), 0.1)
    capex = max(_to_float(energy.get("CAPEX_USD"), 500000.0), 1.0)
    opex = max(_to_float(energy.get("OPEX_USD_yr"), 150000.0), 1.0)

    c1, c2, c3 = st.columns(3)
    with c1:
        r_low = st.number_input("R/Rmin low", min_value=1.02, max_value=1.80, value=1.05, step=0.01)
    with c2:
        r_high = st.number_input("R/Rmin high", min_value=1.10, max_value=4.00, value=2.20, step=0.05)
    with c3:
        samples = st.slider("Cases", 8, 40, 18)
    if r_high <= r_low:
        st.warning("High R/Rmin must be greater than low R/Rmin.")
        return

    rows = []
    for ratio in np.linspace(r_low, r_high, samples):
        r_value = ratio * r_min
        n_est = _estimate_stages_from_gilliland(n_min, r_min, r_value)
        if not math.isfinite(n_est):
            n_est = n_base
        vapor_ratio = (r_value + 1.0) / (r_base + 1.0)
        stage_ratio = max(n_est, 1.0) / max(n_base, 1.0)
        q_reb_est = q_reb * vapor_ratio
        q_cond_est = q_cond * vapor_ratio
        d_est = d_base * math.sqrt(max(vapor_ratio, 0.05))
        h_est = h_base * stage_ratio
        capex_est = capex * (d_est / d_base) ** 1.15 * (h_est / h_base) ** 0.45
        opex_est = opex * vapor_ratio
        annualized = 0.18 * capex_est + opex_est
        rows.append(
            {
                "R/Rmin": ratio,
                "R": r_value,
                "Stages": n_est,
                "Qreb kW": q_reb_est,
                "Qcond kW": q_cond_est,
                "Diameter m": d_est,
                "Height m": h_est,
                "CAPEX USD": capex_est,
                "OPEX USD/yr": opex_est,
                "Annualized Cost": annualized,
            }
        )

    df = pd.DataFrame(rows)
    best_idx = df["Annualized Cost"].idxmin()
    best = df.loc[best_idx]
    st.markdown(
        f"""
        <div class="manager-hero">
            <div><span>Recommended R/Rmin</span><strong>{best['R/Rmin']:.2f}</strong></div>
            <div><span>Estimated stages</span><strong>{best['Stages']:.1f}</strong></div>
            <div><span>Reboiler duty</span><strong>{best['Qreb kW']:.0f} kW</strong></div>
            <div><span>Annualized cost</span><strong>${best['Annualized Cost']:,.0f}/yr</strong></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["R/Rmin"], y=df["Stages"], name="Stages", mode="lines+markers", line=dict(color="#00d4ff", width=3)))
    fig.add_trace(go.Scatter(x=df["R/Rmin"], y=df["Qreb kW"], name="Reboiler duty [kW]", mode="lines+markers", yaxis="y2", line=dict(color="#ff5b6e", width=3)))
    fig.add_vline(x=float(best["R/Rmin"]), line_dash="dash", line_color="#22c55e", annotation_text="best")
    fig.update_layout(
        title=dict(text="Reflux Sensitivity: Stage Count vs Energy Duty", font=dict(color="#f8d477")),
        paper_bgcolor="#0a0e14",
        plot_bgcolor="#0d1520",
        font_color="#eaf6ff",
        xaxis=dict(title="R/Rmin", gridcolor="#1e3a5f"),
        yaxis=dict(title="Theoretical stages", gridcolor="#1e3a5f"),
        yaxis2=dict(title="Reboiler duty [kW]", overlaying="y", side="right", gridcolor="#1e3a5f"),
        height=480,
        legend=dict(bgcolor="#0a0e14"),
    )
    st.plotly_chart(fig, use_container_width=True)

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df["R/Rmin"], y=df["CAPEX USD"], name="CAPEX", mode="lines+markers", line=dict(color="#f8d477", width=3)))
    fig2.add_trace(go.Scatter(x=df["R/Rmin"], y=df["OPEX USD/yr"], name="OPEX", mode="lines+markers", line=dict(color="#22c55e", width=3)))
    fig2.add_trace(go.Scatter(x=df["R/Rmin"], y=df["Annualized Cost"], name="Annualized cost", mode="lines+markers", line=dict(color="#00b4d8", width=3)))
    fig2.add_vline(x=float(best["R/Rmin"]), line_dash="dash", line_color="#22c55e")
    fig2.update_layout(
        title=dict(text="Economic Sensitivity", font=dict(color="#f8d477")),
        paper_bgcolor="#0a0e14",
        plot_bgcolor="#0d1520",
        font_color="#eaf6ff",
        xaxis=dict(title="R/Rmin", gridcolor="#1e3a5f"),
        yaxis=dict(title="USD / yr equivalent", gridcolor="#1e3a5f"),
        height=430,
        legend=dict(bgcolor="#0a0e14"),
    )
    st.plotly_chart(fig2, use_container_width=True)

    with st.expander("View sensitivity table", expanded=True):
        view_df = df.copy()
        for col in ["R/Rmin", "R", "Stages", "Qreb kW", "Qcond kW", "Diameter m", "Height m"]:
            view_df[col] = view_df[col].round(3)
        for col in ["CAPEX USD", "OPEX USD/yr", "Annualized Cost"]:
            view_df[col] = view_df[col].round(0)
        st.dataframe(view_df, use_container_width=True, hide_index=True)


def _render_case_manager():
    os.makedirs(CASE_DIR, exist_ok=True)
    cases = _list_cases()

    st.markdown("### Save Current Design Case")
    c1, c2 = st.columns([2, 1])
    with c1:
        default_name = _default_case_name()
        case_name = st.text_input("Case name", value=default_name)
        notes = st.text_area("Case notes", placeholder="Example: Benzene/Toluene tray column at 1 atm", height=88)
    with c2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Save Current Case", use_container_width=True):
            path = _save_case(case_name, notes)
            st.success(f"Saved case: {os.path.basename(path)}")
            st.rerun()

    st.download_button(
        "Download Current Case JSON",
        data=json.dumps(_case_payload(case_name or default_name, notes), indent=2, default=str).encode("utf-8"),
        file_name=f"{_slugify(case_name or default_name)}.json",
        mime="application/json",
        use_container_width=True,
    )

    st.markdown("### Load Saved Case")
    if cases:
        labels = [case["label"] for case in cases]
        selected = st.selectbox("Saved cases", labels)
        chosen = cases[labels.index(selected)]
        preview = _read_case(chosen["path"])
        st.markdown(_case_preview(preview), unsafe_allow_html=True)
        c_load, c_delete = st.columns(2)
        with c_load:
            if st.button("Load Selected Case", use_container_width=True):
                _apply_case(preview)
                st.success("Case loaded. All saved design data has been restored.")
                st.rerun()
        with c_delete:
            if st.button("Delete Selected Case", use_container_width=True):
                os.remove(chosen["path"])
                st.warning("Case deleted.")
                st.rerun()
    else:
        st.info("No saved cases yet. Save the current design to create your first case.")

    st.markdown("### Import Case JSON")
    uploaded = st.file_uploader("Upload a DistillAI case JSON", type=["json"])
    if uploaded is not None:
        try:
            payload = json.loads(uploaded.read().decode("utf-8"))
            st.markdown(_case_preview(payload), unsafe_allow_html=True)
            if st.button("Load Uploaded Case", use_container_width=True):
                _apply_case(payload)
                st.success("Uploaded case loaded.")
                st.rerun()
        except Exception as exc:
            st.error(f"Could not import case file: {exc}")


def _estimate_stages_from_gilliland(n_min, r_min, r_value):
    x = (r_value - r_min) / max(r_value + 1.0, 1e-9)
    x = float(np.clip(x, 0.001, 0.999))
    y = 1.0 - math.exp(((1.0 + 54.4 * x) / (11.0 + 117.2 * x)) * ((x - 1.0) / math.sqrt(x)))
    y = float(np.clip(y, 0.001, 0.95))
    return (n_min + y) / (1.0 - y)


def _health_score(checks):
    if not checks:
        return 0.0
    weights = {"high": 2.0, "medium": 1.25, "low": 0.75}
    values = {"Pass": 1.0, "Warn": 0.62, "Fail": 0.0}
    total_weight = sum(weights.get(c["Severity"], 1.0) for c in checks)
    score = sum(values.get(c["Status"], 0.0) * weights.get(c["Severity"], 1.0) for c in checks)
    return round(100.0 * score / max(total_weight, 1e-9), 1)


def _case_payload(name, notes=""):
    health = evaluate_design_health()
    session = {key: _to_jsonable(st.session_state.get(key)) for key in CASE_KEYS}
    feed = session.get("feed") or {}
    return {
        "metadata": {
            "name": name,
            "notes": notes,
            "saved_at": datetime.now().isoformat(timespec="seconds"),
            "app": "DistillAI",
            "version": "2026-05-28",
            "system": f"{feed.get('light', feed.get('light_comp', 'Light'))} / {feed.get('heavy', feed.get('heavy_comp', 'Heavy'))}",
            "column_type": session.get("column_type"),
            "health_score": health["score"],
        },
        "session": session,
    }


def _save_case(name, notes):
    payload = _case_payload(name or _default_case_name(), notes)
    filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{_slugify(payload['metadata']['name'])}.json"
    path = os.path.join(CASE_DIR, filename)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, default=str)
    return path


def _list_cases():
    os.makedirs(CASE_DIR, exist_ok=True)
    cases = []
    for filename in sorted(os.listdir(CASE_DIR), reverse=True):
        if not filename.lower().endswith(".json"):
            continue
        path = os.path.join(CASE_DIR, filename)
        try:
            payload = _read_case(path)
            meta = payload.get("metadata", {})
            label = f"{meta.get('saved_at', filename)} | {meta.get('name', filename)} | {meta.get('system', 'system N/A')}"
            cases.append({"path": path, "label": label})
        except Exception:
            cases.append({"path": path, "label": filename})
    return cases


def _read_case(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _apply_case(payload):
    session = payload.get("session", payload)
    for key in CASE_KEYS:
        if key in session:
            st.session_state[key] = session[key]
    st.session_state["active_section"] = "🧭 Design Manager"


def _case_preview(payload):
    meta = payload.get("metadata", {})
    session = payload.get("session", payload)
    feed = session.get("feed", {})
    shortcut = session.get("shortcut", {})
    diameter = session.get("diameter", {})
    height = session.get("height", {})
    return f"""
    <div class="manager-case-preview">
        <b>{_escape(meta.get('name', 'Imported case'))}</b><br>
        System: <span>{_escape(meta.get('system', _default_system_text(feed)))}</span> |
        Type: <span>{_escape(str(meta.get('column_type', session.get('column_type', 'N/A'))))}</span> |
        Saved: <span>{_escape(meta.get('saved_at', 'N/A'))}</span><br>
        R = <span>{_escape(str(shortcut.get('R', 'N/A')))}</span> |
        Stages = <span>{_escape(str(shortcut.get('N_actual_int', shortcut.get('N_actual', 'N/A'))))}</span> |
        D = <span>{_escape(str(diameter.get('D_column_std_m', 'N/A')))} m</span> |
        H = <span>{_escape(str(height.get('total_height_m', 'N/A')))} m</span>
    </div>
    """


def _default_case_name():
    feed = st.session_state.get("feed", {})
    light = feed.get("light", feed.get("light_comp", "Light"))
    heavy = feed.get("heavy", feed.get("heavy_comp", "Heavy"))
    col_type = st.session_state.get("column_type") or "column"
    return f"{light}-{heavy}-{col_type}-case"


def _default_system_text(feed):
    return f"{feed.get('light', feed.get('light_comp', 'Light'))} / {feed.get('heavy', feed.get('heavy_comp', 'Heavy'))}"


def _slugify(text):
    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", str(text).strip())
    safe = re.sub(r"_+", "_", safe).strip("_")
    return safe[:80] or "distillai_case"


def _to_jsonable(value):
    if isinstance(value, dict):
        return {str(k): _to_jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_to_jsonable(v) for v in value]
    if isinstance(value, np.ndarray):
        return [_to_jsonable(v) for v in value.tolist()]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    try:
        return deepcopy(value)
    except Exception:
        return str(value)


def _to_float(value, default=None):
    if value in (None, "", "—", "N/A"):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _format_triplet(label, first, second, third):
    vals = ["N/A" if v is None else f"{v:.4f}" for v in [first, second, third]]
    return f"{label}: {vals[0]} / {vals[1]} / {vals[2]}"


def _escape(value):
    import html

    return html.escape(str(value))


def _render_manager_style():
    st.markdown(
        """
        <style>
        .manager-hero {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 12px;
            margin: 0.5rem 0 1.1rem;
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid rgba(0,180,216,.42);
            border-left: 5px solid #f8d477;
            background: linear-gradient(135deg, rgba(8,14,24,.99), rgba(15,23,42,.96));
            box-shadow: 0 14px 28px rgba(0,0,0,.18);
        }
        .manager-hero div {
            border: 1px solid rgba(0,180,216,.22);
            border-radius: 8px;
            padding: .8rem .9rem;
            background: rgba(8,14,24,.55);
        }
        .manager-hero span {
            display: block;
            color: #ff5b6e;
            font-weight: 900;
            margin-bottom: .35rem;
        }
        .manager-hero strong {
            color: #00d4ff;
            font-family: 'Share Tech Mono', monospace;
            font-size: 1.28rem;
        }
        .manager-action {
            color: #eaf6ff;
            border-radius: 8px;
            padding: .85rem 1rem;
            margin: .5rem 0;
            background: linear-gradient(135deg, rgba(8,14,24,.99), rgba(15,23,42,.96));
            border: 1px solid rgba(0,180,216,.35);
            line-height: 1.55;
        }
        .manager-action b { color: #f8d477; }
        .manager-action span { color: #dbeafe; font-weight: 760; }
        .manager-warn { border-left: 4px solid #f8d477; }
        .manager-fail { border-left: 4px solid #ff5b6e; }
        .manager-case-preview {
            color: #eaf6ff;
            line-height: 1.7;
            border-radius: 8px;
            padding: 1rem;
            margin: .7rem 0;
            border: 1px solid rgba(0,180,216,.38);
            border-left: 4px solid #22c55e;
            background: linear-gradient(135deg, rgba(8,14,24,.99), rgba(15,23,42,.96));
        }
        .manager-case-preview b { color: #f8d477; font-size: 1.05rem; }
        .manager-case-preview span { color: #00d4ff; font-weight: 900; }
        @media (max-width: 900px) {
            .manager-hero { grid-template-columns: 1fr; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
