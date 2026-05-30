"""pages/report.py — Professional Engineering Report Generator"""
import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime
import html
import io
import textwrap
import zipfile

from sections.design_manager import evaluate_design_health
from sections.phase3_style import render_phase3_style


def _fmt_money(value, unit="USD"):
    if value in (None, "", "â€”", "—"):
        return "â€”"
    suffix = f" {unit}" if unit else ""
    try:
        return f"${float(value):,.0f}{suffix}"
    except (TypeError, ValueError):
        return f"{value}{suffix}"


def render():
    render_phase3_style()
    _render_report_visibility_style()

    st.markdown("""
    <div class="section-header">
        <h1>📋 Report Generator</h1>
        <p>Generate professional engineering design reports from your completed distillation column design.</p>
    </div>
    """, unsafe_allow_html=True)

    # Gather all session data
    feed       = st.session_state.get("feed", {})
    thermo     = st.session_state.get("thermo", {})
    col_type   = st.session_state.get("column_type", "tray")
    shortcut   = st.session_state.get("shortcut", {})
    mccabe     = st.session_state.get("mccabe", {})
    rigorous   = st.session_state.get("rigorous", {})
    diameter   = st.session_state.get("diameter", {})
    height     = st.session_state.get("height", {})
    reboiler   = st.session_state.get("reboiler", {})
    condenser  = st.session_state.get("condenser", {})
    mechanical = st.session_state.get("mechanical", {})
    energy     = st.session_state.get("energy", {})
    internals  = st.session_state.get("internals", {})
    instrum    = st.session_state.get("instrumentation", {})
    health     = evaluate_design_health()

    tab1, tab2, tab3, tab4 = st.tabs(["Report Preview", "Validation Summary", "Report Settings", "Export"])

    # ── TAB 1: Report Preview ─────────────────────────────────
    with tab1:
        st.markdown("### Engineering Design Report Preview")

        # Design completeness check
        completed = []
        missing   = []
        checks = [
            ("Feed Specifications", bool(feed)),
            ("Thermodynamics", bool(thermo)),
            ("Shortcut Design", bool(shortcut)),
            ("Column Sizing (Diameter)", bool(diameter)),
            ("Column Height", bool(height)),
            ("Reboiler Design", bool(reboiler)),
            ("Condenser Design", bool(condenser)),
            ("Mechanical Design", bool(mechanical)),
            ("Energy & Economics", bool(energy)),
        ]
        for name, done in checks:
            (completed if done else missing).append(name)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**✅ Completed Sections:**")
            for s in completed:
                st.markdown(f"  ✅ {s}")
        with c2:
            st.markdown("**⭕ Pending Sections:**")
            for s in missing:
                st.markdown(f"  ⭕ {s}")

        progress = len(completed) / len(checks)
        st.progress(progress, text=f"Design Progress: {len(completed)}/{len(checks)} sections complete")

        st.markdown("---")
        _render_health_strip(health)
        _render_report_preview(feed, thermo, col_type, shortcut, diameter, height,
                                reboiler, condenser, mechanical, energy)

    # ── TAB 2: Report Settings ────────────────────────────────
    with tab2:
        st.markdown("### Final Design Validation Summary")
        _render_health_strip(health)
        st.dataframe(pd.DataFrame(health["checks"]), use_container_width=True, hide_index=True)

    with tab3:
        st.markdown("### Report Configuration")

        c1, c2 = st.columns(2)
        with c1:
            project_title   = st.text_input("Project Title", value="Binary Distillation Column Design")
            project_no      = st.text_input("Project Number", value="DISTILL-AI-001")
            engineer_name   = st.text_input("Engineer Name", value="Zunair Shahzad")
            company_name    = st.text_input("Company/University", value="Chemical Engineering - UET Lahore New Campus")
        with c2:
            client_name     = st.text_input("Client / Department", value="")
            revision        = st.text_input("Revision", value="A")
            report_date     = st.date_input("Report Date", value=datetime.today())
            confidential    = st.checkbox("Mark as CONFIDENTIAL", value=False)

        st.session_state.report_settings = {
            "project_title": project_title,
            "project_no": project_no,
            "engineer_name": engineer_name,
            "company_name": company_name,
            "client_name": client_name,
            "revision": revision,
            "report_date": report_date,
            "confidential": confidential,
        }

        sections_to_include = st.multiselect(
            "Sections to Include in Report",
            ["Executive Summary", "Feed & Process Specifications", "Thermodynamic Data",
             "Shortcut Design Calculations", "McCabe-Thiele Analysis", "Column Sizing",
             "Reboiler & Condenser Design", "Mechanical Design", "Column Internals",
             "Instrumentation & Control", "Energy & Economics", "Design Summary Table",
             "References & Standards"],
            default=["Executive Summary", "Feed & Process Specifications", "Thermodynamic Data",
                     "Shortcut Design Calculations", "Column Sizing",
                     "Reboiler & Condenser Design", "Design Summary Table", "References & Standards"]
        )

    # ── TAB 3: Export ─────────────────────────────────────────
    with tab4:
        st.markdown("### Export Report")

        st.info("""
        **Available Export Formats:**
        - **PDF Engineering Report** - final industrial report for submission/review
        - **DOCX Editable Report** - Microsoft Word format for editing and formatting
        - 📄 **Markdown Report** — Clean text report, viewable in any editor
        - 📋 **CSV Data Export** — All calculated values in tabular format
        - 🔢 **JSON Data Export** — Complete session data for further processing
        """)

        pdf_col, docx_col = st.columns(2)
        with pdf_col:
            st.markdown("#### PDF Engineering Report")
            st.caption("Final locked report format, best for industrial-style submission.")
            st.download_button(
                label="Download PDF Report",
                data=_generate_pdf_report(
                    feed, thermo, col_type, shortcut, diameter, height,
                    reboiler, condenser, mechanical, energy, health
                ),
                file_name=f"DistillAI_Engineering_Report_{datetime.today().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        with docx_col:
            st.markdown("#### DOCX Editable Report")
            st.caption("Editable Word report for teacher, supervisor, or client revisions.")
            st.download_button(
                label="Download DOCX Report",
                data=_generate_docx_report(
                    feed, thermo, col_type, shortcut, diameter, height,
                    reboiler, condenser, mechanical, energy, health
                ),
                file_name=f"DistillAI_Engineering_Report_{datetime.today().strftime('%Y%m%d')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )

        st.markdown("---")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("#### 📄 Markdown Report")
            if st.button("Generate Markdown Report", use_container_width=True):
                report_text = _generate_markdown_report(
                    feed, thermo, col_type, shortcut, diameter, height,
                    reboiler, condenser, mechanical, energy, health
                )
                st.download_button(
                    label="⬇️ Download .md Report",
                    data=report_text.encode("utf-8"),
                    file_name=f"DistillAI_Report_{datetime.today().strftime('%Y%m%d')}.md",
                    mime="text/markdown",
                    use_container_width=True
                )

        with col2:
            st.markdown("#### 📊 CSV Data Export")
            if st.button("Generate CSV Data", use_container_width=True):
                csv_data = _generate_csv(feed, thermo, shortcut, diameter, height,
                                          reboiler, condenser, mechanical, energy)
                st.download_button(
                    label="⬇️ Download .csv",
                    data=csv_data,
                    file_name=f"DistillAI_Data_{datetime.today().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

        with col3:
            st.markdown("#### 🔢 JSON Data Export")
            if st.button("Generate JSON Export", use_container_width=True):
                import json
                all_data = {
                    "project": "DistillAI Design Report",
                    "date": datetime.today().isoformat(),
                    "feed": feed, "thermo": thermo,
                    "column_type": col_type, "shortcut": shortcut,
                    "diameter": diameter, "height": height,
                    "reboiler": reboiler, "condenser": condenser,
                    "mechanical": mechanical, "energy": energy,
                }
                json_str = json.dumps(all_data, indent=2, default=str)
                st.download_button(
                    label="⬇️ Download .json",
                    data=json_str,
                    file_name=f"DistillAI_Data_{datetime.today().strftime('%Y%m%d')}.json",
                    mime="application/json",
                    use_container_width=True
                )

        st.markdown("---")
        st.markdown("### 📋 Design Summary Table")
        _render_summary_table(feed, thermo, shortcut, diameter, height, reboiler, condenser, mechanical, energy)


def _render_health_strip(health):
    score = health.get("score", 0)
    color = "#22c55e" if score >= 85 else "#f8d477" if score >= 65 else "#ff5b6e"
    status = "Ready for review" if score >= 85 else "Engineering review needed" if score >= 65 else "Incomplete"
    st.markdown(
        f"""
        <div class="report-health-strip" style="border-left-color:{color};">
            <div><span>Design Health</span><strong style="color:{color};">{score:.0f}%</strong></div>
            <div><span>Status</span><strong>{status}</strong></div>
            <div><span>Completion</span><strong>{health.get('completion', 0)}/{health.get('total_required', 0)}</strong></div>
            <div><span>Warnings / Critical</span><strong>{health.get('warning_count', 0)} / {health.get('critical_count', 0)}</strong></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_report_visibility_style():
    st.markdown(
        """
        <style>
        .phase4-report-preview {
            color: #eaf6ff !important;
            background: linear-gradient(135deg, rgba(8, 14, 24, 0.99), rgba(15, 23, 42, 0.96)) !important;
            border: 1px solid rgba(0, 180, 216, 0.44) !important;
            box-shadow: 0 14px 32px rgba(0,0,0,0.18);
        }
        .phase4-report-preview h2,
        .phase4-report-preview h3 {
            color: #f8d477 !important;
            border-color: rgba(248, 212, 119, 0.58) !important;
            font-weight: 900 !important;
            text-shadow: 0 0 14px rgba(248, 212, 119, 0.20);
        }
        .phase4-report-preview h3 {
            margin-top: 1.45rem !important;
        }
        .phase4-report-preview p,
        .phase4-report-preview li,
        .phase4-report-preview td {
            color: #eaf6ff !important;
            font-weight: 700 !important;
            line-height: 1.65;
        }
        .phase4-report-preview th {
            color: #ff5b6e !important;
            font-weight: 900 !important;
            background: rgba(8, 14, 24, 0.98) !important;
        }
        .phase4-report-preview td,
        .phase4-report-preview th {
            border-color: rgba(0, 180, 216, 0.34) !important;
        }
        .phase4-report-preview tr[style*="background"] {
            background: rgba(30, 58, 95, 0.32) !important;
        }
        .report-health-strip {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 12px;
            margin: 0.6rem 0 1rem;
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid rgba(0, 180, 216, 0.42);
            border-left: 5px solid #f8d477;
            background: linear-gradient(135deg, rgba(8, 14, 24, 0.99), rgba(15, 23, 42, 0.96));
            box-shadow: 0 14px 28px rgba(0,0,0,0.18);
        }
        .report-health-strip div {
            border: 1px solid rgba(0, 180, 216, 0.22);
            border-radius: 8px;
            padding: 0.75rem 0.85rem;
            background: rgba(8, 14, 24, 0.52);
        }
        .report-health-strip span {
            display: block;
            color: #ff5b6e;
            font-weight: 900;
            margin-bottom: 0.3rem;
        }
        .report-health-strip strong {
            color: #00d4ff;
            font-family: 'Share Tech Mono', monospace;
            font-size: 1.16rem;
            font-weight: 900;
        }
        @media (max-width: 900px) {
            .report-health-strip {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_report_preview(feed, thermo, col_type, shortcut, diameter, height,
                            reboiler, condenser, mechanical, energy):
    """Render HTML report preview"""
    now = datetime.today().strftime("%B %d, %Y")
    capex_text = _fmt_money(energy.get("CAPEX_USD"))
    opex_text = _fmt_money(energy.get("OPEX_USD_yr"), "USD/yr")
    npv_text = _fmt_money(energy.get("NPV_USD"))

    st.markdown(f"""
    <div class="phase4-report-preview" style="background:#0d1520;border:1px solid #1e3a5f;border-radius:8px;padding:30px;font-family:'Barlow',sans-serif;">

    <div style="text-align:center;border-bottom:2px solid #00b4d8;padding-bottom:20px;margin-bottom:25px;">
        <h2 style="color:#00b4d8;margin:0;">⚗️ DISTILLATION COLUMN DESIGN REPORT</h2>
        <h3 style="color:#e2e8f0;margin:8px 0;">AI-Powered Industrial Design System</h3>
        <p style="color:#64748b;margin:4px 0;">Generated by DistillAI | {now}</p>
    </div>

    <h3 style="color:#00b4d8;border-bottom:1px solid #1e3a5f;padding-bottom:8px;">1. EXECUTIVE SUMMARY</h3>
    <p style="color:#e2e8f0;">
    This report presents the complete engineering design of a binary component distillation column.
    The design covers process specifications, shortcut calculations (Fenske-Underwood-Gilliland method),
    McCabe-Thiele graphical analysis, column hydraulics, heat exchanger sizing, mechanical design,
    and economic evaluation, following industrial standards including ASME, API, and process engineering
    references (McCabe Smith Harriott, Seader Henley, Coulson Richardson).
    </p>

    <h3 style="color:#00b4d8;border-bottom:1px solid #1e3a5f;padding-bottom:8px;margin-top:25px;">2. PROCESS SPECIFICATIONS</h3>
    <table style="width:100%;border-collapse:collapse;color:#e2e8f0;">
    <tr style="background:#0d2040;">
        <th style="padding:8px;border:1px solid #1e3a5f;text-align:left;">Parameter</th>
        <th style="padding:8px;border:1px solid #1e3a5f;text-align:left;">Value</th>
        <th style="padding:8px;border:1px solid #1e3a5f;text-align:left;">Unit</th>
    </tr>
    <tr><td style="padding:6px;border:1px solid #1e3a5f;">Feed Flow Rate (F)</td><td style="padding:6px;border:1px solid #1e3a5f;">{feed.get('F','—')}</td><td style="padding:6px;border:1px solid #1e3a5f;">kmol/h</td></tr>
    <tr style="background:#0d2040;"><td style="padding:6px;border:1px solid #1e3a5f;">Light Component</td><td style="padding:6px;border:1px solid #1e3a5f;">{feed.get('light_comp','—')}</td><td style="padding:6px;border:1px solid #1e3a5f;">—</td></tr>
    <tr><td style="padding:6px;border:1px solid #1e3a5f;">Heavy Component</td><td style="padding:6px;border:1px solid #1e3a5f;">{feed.get('heavy_comp','—')}</td><td style="padding:6px;border:1px solid #1e3a5f;">—</td></tr>
    <tr style="background:#0d2040;"><td style="padding:6px;border:1px solid #1e3a5f;">Feed Mole Fraction (zF)</td><td style="padding:6px;border:1px solid #1e3a5f;">{feed.get('z_F','—')}</td><td style="padding:6px;border:1px solid #1e3a5f;">mol/mol</td></tr>
    <tr><td style="padding:6px;border:1px solid #1e3a5f;">Distillate Purity (xD)</td><td style="padding:6px;border:1px solid #1e3a5f;">{feed.get('x_D','—')}</td><td style="padding:6px;border:1px solid #1e3a5f;">mol/mol</td></tr>
    <tr style="background:#0d2040;"><td style="padding:6px;border:1px solid #1e3a5f;">Bottoms Purity (xB)</td><td style="padding:6px;border:1px solid #1e3a5f;">{feed.get('x_B','—')}</td><td style="padding:6px;border:1px solid #1e3a5f;">mol/mol</td></tr>
    <tr><td style="padding:6px;border:1px solid #1e3a5f;">Operating Pressure</td><td style="padding:6px;border:1px solid #1e3a5f;">{feed.get('P_col_bar','—')}</td><td style="padding:6px;border:1px solid #1e3a5f;">bar</td></tr>
    </table>

    <h3 style="color:#00b4d8;border-bottom:1px solid #1e3a5f;padding-bottom:8px;margin-top:25px;">3. SHORTCUT DESIGN RESULTS</h3>
    <table style="width:100%;border-collapse:collapse;color:#e2e8f0;">
    <tr style="background:#0d2040;"><th style="padding:8px;border:1px solid #1e3a5f;">Parameter</th><th style="padding:8px;border:1px solid #1e3a5f;">Value</th><th style="padding:8px;border:1px solid #1e3a5f;">Method</th></tr>
    <tr><td style="padding:6px;border:1px solid #1e3a5f;">Minimum Stages (N_min)</td><td style="padding:6px;border:1px solid #1e3a5f;">{shortcut.get('N_min','—')}</td><td style="padding:6px;border:1px solid #1e3a5f;">Fenske Equation</td></tr>
    <tr style="background:#0d2040;"><td style="padding:6px;border:1px solid #1e3a5f;">Minimum Reflux (R_min)</td><td style="padding:6px;border:1px solid #1e3a5f;">{shortcut.get('R_min','—')}</td><td style="padding:6px;border:1px solid #1e3a5f;">Underwood Equation</td></tr>
    <tr><td style="padding:6px;border:1px solid #1e3a5f;">Actual Stages (N)</td><td style="padding:6px;border:1px solid #1e3a5f;">{shortcut.get('N_actual','—')}</td><td style="padding:6px;border:1px solid #1e3a5f;">Gilliland Correlation</td></tr>
    <tr style="background:#0d2040;"><td style="padding:6px;border:1px solid #1e3a5f;">Operating Reflux (R)</td><td style="padding:6px;border:1px solid #1e3a5f;">{shortcut.get('R','—')}</td><td style="padding:6px;border:1px solid #1e3a5f;">R = 1.3 × R_min</td></tr>
    <tr><td style="padding:6px;border:1px solid #1e3a5f;">Feed Stage (NF)</td><td style="padding:6px;border:1px solid #1e3a5f;">{shortcut.get('NF','—')}</td><td style="padding:6px;border:1px solid #1e3a5f;">Kirkbride Equation</td></tr>
    </table>

    <h3 style="color:#00b4d8;border-bottom:1px solid #1e3a5f;padding-bottom:8px;margin-top:25px;">4. COLUMN SIZING</h3>
    <table style="width:100%;border-collapse:collapse;color:#e2e8f0;">
    <tr style="background:#0d2040;"><th style="padding:8px;border:1px solid #1e3a5f;">Parameter</th><th style="padding:8px;border:1px solid #1e3a5f;">Value</th><th style="padding:8px;border:1px solid #1e3a5f;">Unit</th></tr>
    <tr><td style="padding:6px;border:1px solid #1e3a5f;">Column Diameter (D)</td><td style="padding:6px;border:1px solid #1e3a5f;">{diameter.get('D_column_std_m','—')}</td><td style="padding:6px;border:1px solid #1e3a5f;">m</td></tr>
    <tr style="background:#0d2040;"><td style="padding:6px;border:1px solid #1e3a5f;">Total Column Height (H)</td><td style="padding:6px;border:1px solid #1e3a5f;">{height.get('total_height_m','—')}</td><td style="padding:6px;border:1px solid #1e3a5f;">m</td></tr>
    <tr><td style="padding:6px;border:1px solid #1e3a5f;">Reboiler Duty (Q_reb)</td><td style="padding:6px;border:1px solid #1e3a5f;">{reboiler.get('Q_reb_kW','—')}</td><td style="padding:6px;border:1px solid #1e3a5f;">kW</td></tr>
    <tr style="background:#0d2040;"><td style="padding:6px;border:1px solid #1e3a5f;">Condenser Duty (Q_cond)</td><td style="padding:6px;border:1px solid #1e3a5f;">{condenser.get('Q_cond_kW','—')}</td><td style="padding:6px;border:1px solid #1e3a5f;">kW</td></tr>
    </table>

    <h3 style="color:#00b4d8;border-bottom:1px solid #1e3a5f;padding-bottom:8px;margin-top:25px;">5. ECONOMIC SUMMARY</h3>
    <table style="width:100%;border-collapse:collapse;color:#e2e8f0;">
    <tr style="background:#0d2040;"><th style="padding:8px;border:1px solid #1e3a5f;">Economic Parameter</th><th style="padding:8px;border:1px solid #1e3a5f;">Value</th></tr>
    <tr><td style="padding:6px;border:1px solid #1e3a5f;">CAPEX (Installed Cost)</td><td style="padding:6px;border:1px solid #1e3a5f;">{capex_text}</td></tr>
    <tr style="background:#0d2040;"><td style="padding:6px;border:1px solid #1e3a5f;">Annual OPEX</td><td style="padding:6px;border:1px solid #1e3a5f;">{opex_text}</td></tr>
    <tr><td style="padding:6px;border:1px solid #1e3a5f;">Simple Payback</td><td style="padding:6px;border:1px solid #1e3a5f;">{energy.get('simple_payback_yrs','—')} years</td></tr>
    <tr style="background:#0d2040;"><td style="padding:6px;border:1px solid #1e3a5f;">NPV</td><td style="padding:6px;border:1px solid #1e3a5f;">{npv_text}</td></tr>
    <tr><td style="padding:6px;border:1px solid #1e3a5f;">IRR</td><td style="padding:6px;border:1px solid #1e3a5f;">{energy.get('IRR_pct','—')} %</td></tr>
    </table>

    <h3 style="color:#00b4d8;border-bottom:1px solid #1e3a5f;padding-bottom:8px;margin-top:25px;">6. REFERENCES & STANDARDS</h3>
    <ol style="color:#94a3b8;line-height:1.8;">
        <li>McCabe, W.L., Smith, J.C., Harriott, P. — <em>Unit Operations of Chemical Engineering</em>, 8th Ed., McGraw-Hill</li>
        <li>Seader, J.D., Henley, E.J., Roper, D.K. — <em>Separation Process Principles</em>, 3rd Ed., Wiley</li>
        <li>Coulson, J.M., Richardson, J.F. — <em>Chemical Engineering Vol. 2</em>, 5th Ed., Butterworth-Heinemann</li>
        <li>Perry, R.H., Green, D.W. — <em>Perry's Chemical Engineers' Handbook</em>, 9th Ed., McGraw-Hill</li>
        <li>Towler, G., Sinnott, R. — <em>Chemical Engineering Design</em>, 2nd Ed., Elsevier</li>
        <li>Fair, J.R. — <em>Tray Hydraulics: Perforated Trays</em>, AIChE</li>
        <li>ASME Boiler & Pressure Vessel Code — Section VIII, Division 1</li>
        <li>API Standard 520 — Sizing, Selection, and Installation of Pressure-Relieving Devices</li>
    </ol>

    <div style="text-align:center;border-top:1px solid #1e3a5f;margin-top:30px;padding-top:15px;color:#475569;font-size:0.8rem;">
        Generated by DistillAI — Industrial Distillation Column Design System | {now}
    </div>
    </div>
    """, unsafe_allow_html=True)


def _clean_report_value(value, fallback="-"):
    if value is None:
        return fallback
    if isinstance(value, float):
        if np.isnan(value) or np.isinf(value):
            return fallback
        return f"{value:.5g}"
    text = str(value).strip()
    if not text or text in {"-", "--", "None", "nan"}:
        return fallback
    return text


def _safe_report_text(value):
    text = _clean_report_value(value)
    replacements = {
        "\u03b1": "alpha",
        "\u0394": "Delta",
        "\u03b8": "theta",
        "\u00b2": "^2",
        "\u00b3": "^3",
        "\u00b0": " deg",
        "\u2014": "-",
        "\u2013": "-",
        "\u00d7": "x",
        "\u00b7": "*",
        "\u00e2\u20ac\u201d": "-",
        "\u00c2\u00b2": "^2",
        "\u00ce\u00b1": "alpha",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.encode("latin-1", "replace").decode("latin-1")


def _report_row(label, value, unit=""):
    value_text = _clean_report_value(value)
    unit_text = f" {unit}" if unit else ""
    return f"{label}: {value_text}{unit_text}"


def _build_report_items(feed, thermo, col_type, shortcut, diameter, height,
                        reboiler, condenser, mechanical, energy, health=None):
    health = health or evaluate_design_health()
    now = datetime.today().strftime("%B %d, %Y")
    capex_text = _fmt_money(energy.get("CAPEX_USD"))
    opex_text = _fmt_money(energy.get("OPEX_USD_yr"), "USD/yr")
    npv_text = _fmt_money(energy.get("NPV_USD"))

    items = [
        ("title", "DISTILLATION COLUMN DESIGN REPORT"),
        ("subtitle", "AI-Powered Industrial Design System - DistillAI"),
        ("meta", f"Generated: {now}"),
        ("space", ""),
        ("section", "1. Executive Summary"),
        ("text", "This report presents the engineering design summary for a binary distillation column. The package includes process specifications, thermodynamic basis, shortcut design, column sizing, heat duties, mechanical checks, economics, and final validation."),
        ("row", _report_row("Final Design Health Score", f"{health.get('score', 0):.0f}%")),
        ("row", _report_row("Completed Sections", f"{health.get('completion', 0)}/{health.get('total_required', 0)}")),
        ("row", _report_row("Warnings / Critical Issues", f"{health.get('warning_count', 0)} / {health.get('critical_count', 0)}")),
        ("space", ""),
        ("section", "2. Process Specifications"),
        ("row", _report_row("Feed Flow Rate F", feed.get("F"), "kmol/h")),
        ("row", _report_row("Light Component", feed.get("light_comp"))),
        ("row", _report_row("Heavy Component", feed.get("heavy_comp"))),
        ("row", _report_row("Feed Mole Fraction zF", feed.get("z_F"), "mol/mol")),
        ("row", _report_row("Distillate Composition xD", feed.get("x_D"), "mol/mol")),
        ("row", _report_row("Bottoms Composition xB", feed.get("x_B"), "mol/mol")),
        ("row", _report_row("Operating Pressure", feed.get("P_col_bar"), "bar")),
        ("row", _report_row("Column Type", col_type)),
        ("space", ""),
        ("section", "3. Thermodynamic Basis"),
        ("row", _report_row("Selected VLE Model", thermo.get("vle_model", thermo.get("selected_model")))),
        ("row", _report_row("Relative Volatility alpha", thermo.get("alpha_avg"))),
        ("row", _report_row("Non-ideality Level", thermo.get("non_ideality_level"))),
        ("space", ""),
        ("section", "4. Shortcut Design Results"),
        ("row", _report_row("Minimum Stages N_min", shortcut.get("N_min"), "stages")),
        ("row", _report_row("Minimum Reflux Ratio R_min", shortcut.get("R_min"))),
        ("row", _report_row("Actual Stages N", shortcut.get("N_actual"), "stages")),
        ("row", _report_row("Operating Reflux Ratio R", shortcut.get("R"))),
        ("row", _report_row("R / R_min", shortcut.get("R_over_Rmin"))),
        ("row", _report_row("Feed Stage NF", shortcut.get("NF"))),
        ("space", ""),
        ("section", "5. Column Sizing"),
        ("row", _report_row("Column Diameter", diameter.get("D_column_std_m"), "m")),
        ("row", _report_row("Flooding Velocity", diameter.get("u_flood_ms"), "m/s")),
        ("row", _report_row("Operating Velocity", diameter.get("u_op_ms"), "m/s")),
        ("row", _report_row("Total Column Height", height.get("total_height_m"), "m")),
        ("row", _report_row("Active Section Height", height.get("active_height_m"), "m")),
        ("space", ""),
        ("section", "6. Reboiler and Condenser"),
        ("row", _report_row("Reboiler Duty", reboiler.get("Q_reb_kW"), "kW")),
        ("row", _report_row("Reboiler Area", reboiler.get("A_reb_m2"), "m2")),
        ("row", _report_row("Condenser Duty", condenser.get("Q_cond_kW"), "kW")),
        ("row", _report_row("Condenser Area", condenser.get("A_cond_m2"), "m2")),
        ("space", ""),
        ("section", "7. Mechanical Design"),
        ("row", _report_row("Shell Thickness", mechanical.get("t_shell_mm"), "mm")),
        ("row", _report_row("Design Pressure", mechanical.get("P_design_bar"), "bar")),
        ("row", _report_row("Material", mechanical.get("material"))),
        ("row", _report_row("Shell Weight", mechanical.get("W_shell_kg"), "kg")),
        ("space", ""),
        ("section", "8. Energy and Economics"),
        ("row", _report_row("CAPEX", capex_text)),
        ("row", _report_row("Annual OPEX", opex_text)),
        ("row", _report_row("Steam Rate", energy.get("steam_rate_kg_h"), "kg/h")),
        ("row", _report_row("Cooling Water Rate", energy.get("cw_rate_t_h"), "t/h")),
        ("row", _report_row("Simple Payback", energy.get("simple_payback_yrs"), "years")),
        ("row", _report_row("NPV", npv_text)),
        ("row", _report_row("IRR", energy.get("IRR_pct"), "%")),
        ("space", ""),
        ("section", "9. Final Design Validation"),
    ]

    checks = health.get("checks", [])
    if checks:
        for check in checks:
            items.append((
                "row",
                f"{_clean_report_value(check.get('Category'))} - "
                f"{_clean_report_value(check.get('Check'))}: "
                f"{_clean_report_value(check.get('Status'))} | "
                f"{_clean_report_value(check.get('Value'))} | "
                f"{_clean_report_value(check.get('Recommendation'))}"
            ))
    else:
        items.append(("text", "No validation checks are available yet."))

    items.extend([
        ("space", ""),
        ("section", "10. References and Standards"),
        ("text", "McCabe, Smith and Harriott - Unit Operations of Chemical Engineering."),
        ("text", "Seader, Henley and Roper - Separation Process Principles."),
        ("text", "Coulson and Richardson - Chemical Engineering, Volume 2."),
        ("text", "Perry's Chemical Engineers' Handbook."),
        ("text", "Towler and Sinnott - Chemical Engineering Design."),
        ("text", "ASME BPVC Section VIII Division 1; API 520; TEMA Standards."),
        ("space", ""),
        ("meta", f"Generated by DistillAI - Industrial Distillation Column Design System | {now}"),
    ])
    return items


def _pdf_escape(text):
    return _safe_report_text(text).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _pdf_style(kind):
    if kind == "title":
        return "F2", 16, 22, "0.00 0.70 0.85 rg"
    if kind == "subtitle":
        return "F2", 11, 16, "0.95 0.78 0.28 rg"
    if kind == "section":
        return "F2", 12, 18, "0.95 0.78 0.28 rg"
    if kind == "meta":
        return "F1", 8, 12, "0.42 0.47 0.55 rg"
    return "F1", 9, 12, "0.07 0.10 0.16 rg"


def _generate_pdf_report(feed, thermo, col_type, shortcut, diameter, height,
                         reboiler, condenser, mechanical, energy, health=None) -> bytes:
    items = _build_report_items(feed, thermo, col_type, shortcut, diameter, height,
                                reboiler, condenser, mechanical, energy, health)

    page_width, page_height = 595, 842
    margin_x, top_y, bottom_y = 48, 792, 48
    pages = [[]]
    y = top_y

    for kind, text in items:
        if kind == "space":
            y -= 8
            continue
        wrap_width = 72 if kind in {"title", "subtitle", "section"} else 92
        wrapped = textwrap.wrap(_safe_report_text(text), width=wrap_width) or [""]
        for index, line in enumerate(wrapped):
            line_kind = kind if index == 0 else "text"
            font, size, leading, color = _pdf_style(line_kind)
            if y - leading < bottom_y:
                pages.append([])
                y = top_y
            pages[-1].append((line, font, size, color, margin_x, y))
            y -= leading
        if kind == "section":
            y -= 3

    objects = [None]

    def add_object(obj):
        objects.append(obj)
        return len(objects) - 1

    add_object("<< /Type /Catalog /Pages 2 0 R >>")
    add_object("")
    regular_font_id = add_object("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    bold_font_id = add_object("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
    page_ids = []

    for page_lines in pages:
        commands = [
            "0.96 0.98 1.00 rg",
            f"0 0 {page_width} {page_height} re f",
            "0.00 0.40 0.55 RG",
            "0.8 w",
            f"{margin_x} 818 {page_width - (2 * margin_x)} 0 l S",
        ]
        for line, font, size, color, x, line_y in page_lines:
            commands.append(color)
            commands.append(f"BT /{font} {size} Tf 1 0 0 1 {x} {line_y} Tm ({_pdf_escape(line)}) Tj ET")
        stream = "\n".join(commands).encode("latin-1", "replace")
        content_id = add_object(
            b"<< /Length " + str(len(stream)).encode("ascii") +
            b" >>\nstream\n" + stream + b"\nendstream"
        )
        page_id = add_object(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {page_width} {page_height}] "
            f"/Resources << /Font << /F1 {regular_font_id} 0 R /F2 {bold_font_id} 0 R >> >> "
            f"/Contents {content_id} 0 R >>"
        )
        page_ids.append(page_id)

    objects[2] = f"<< /Type /Pages /Kids [{' '.join(f'{pid} 0 R' for pid in page_ids)}] /Count {len(page_ids)} >>"

    pdf = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for obj_id, obj in enumerate(objects[1:], start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{obj_id} 0 obj\n".encode("ascii"))
        if isinstance(obj, bytes):
            pdf.extend(obj)
        else:
            pdf.extend(str(obj).encode("latin-1", "replace"))
        pdf.extend(b"\nendobj\n")

    xref_start = len(pdf)
    pdf.extend(f"xref\n0 {len(objects)}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        f"trailer\n<< /Size {len(objects)} /Root 1 0 R >>\nstartxref\n{xref_start}\n%%EOF".encode("ascii")
    )
    return bytes(pdf)


def _docx_run(text, size=20, bold=False, color="EAF6FF"):
    bold_xml = "<w:b/>" if bold else ""
    text_xml = html.escape(_safe_report_text(text), quote=True)
    return (
        f"<w:r><w:rPr>{bold_xml}<w:color w:val=\"{color}\"/>"
        f"<w:sz w:val=\"{size}\"/><w:szCs w:val=\"{size}\"/>"
        f"<w:rFonts w:ascii=\"Aptos\" w:hAnsi=\"Aptos\"/>"
        f"</w:rPr><w:t xml:space=\"preserve\">{text_xml}</w:t></w:r>"
    )


def _docx_paragraph(text, kind="text"):
    if kind == "space":
        return "<w:p/>"
    styles = {
        "title": (34, True, "00B4D8", 220),
        "subtitle": (22, True, "F8D477", 120),
        "section": (24, True, "F8D477", 160),
        "meta": (17, False, "64748B", 80),
        "row": (19, False, "111827", 70),
        "text": (19, False, "111827", 90),
    }
    size, bold, color, after = styles.get(kind, styles["text"])
    border = ""
    if kind == "section":
        border = (
            "<w:pBdr><w:bottom w:val=\"single\" w:sz=\"8\" "
            "w:space=\"4\" w:color=\"00B4D8\"/></w:pBdr>"
        )
    return (
        f"<w:p><w:pPr><w:spacing w:after=\"{after}\"/>{border}</w:pPr>"
        f"{_docx_run(text, size=size, bold=bold, color=color)}</w:p>"
    )


def _generate_docx_report(feed, thermo, col_type, shortcut, diameter, height,
                          reboiler, condenser, mechanical, energy, health=None) -> bytes:
    items = _build_report_items(feed, thermo, col_type, shortcut, diameter, height,
                                reboiler, condenser, mechanical, energy, health)
    body = "\n".join(_docx_paragraph(text, kind) for kind, text in items)
    document_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    {body}
    <w:sectPr>
      <w:pgSz w:w="11906" w:h="16838"/>
      <w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134" w:header="708" w:footer="708" w:gutter="0"/>
    </w:sectPr>
  </w:body>
</w:document>"""
    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""
    rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as docx:
        docx.writestr("[Content_Types].xml", content_types)
        docx.writestr("_rels/.rels", rels)
        docx.writestr("word/document.xml", document_xml)
    return output.getvalue()


def _generate_markdown_report(feed, thermo, col_type, shortcut, diameter, height,
                               reboiler, condenser, mechanical, energy, health=None) -> str:
    now = datetime.today().strftime("%B %d, %Y")
    capex_text = _fmt_money(energy.get("CAPEX_USD"))
    opex_text = _fmt_money(energy.get("OPEX_USD_yr"), "USD/yr")
    npv_text = _fmt_money(energy.get("NPV_USD"))
    health = health or evaluate_design_health()
    health_rows = "\n".join(
        f"| {c['Category']} | {c['Check']} | {c['Status']} | {c['Value']} | {c['Recommendation']} |"
        for c in health.get("checks", [])
    )
    report = f"""# DISTILLATION COLUMN DESIGN REPORT
### AI-Powered Industrial Design System — DistillAI
**Date:** {now}  
**Prepared by:** DistillAI Engineering Platform

---

## 1. EXECUTIVE SUMMARY

This report presents the complete engineering design of a binary component distillation column.
Design methodology follows Fenske-Underwood-Gilliland shortcut calculations with McCabe-Thiele
graphical verification, column hydraulic sizing (Fair method), heat exchanger design, ASME
mechanical design, and Lang factor economic evaluation.

**Final Design Health Score:** {health.get('score', 0):.0f}%  
**Completed Sections:** {health.get('completion', 0)}/{health.get('total_required', 0)}  
**Warnings / Critical Issues:** {health.get('warning_count', 0)} / {health.get('critical_count', 0)}

---

## 2. PROCESS SPECIFICATIONS

| Parameter | Value | Unit |
|-----------|-------|------|
| Feed Flow Rate (F) | {feed.get('F','—')} | kmol/h |
| Light Component | {feed.get('light_comp','—')} | — |
| Heavy Component | {feed.get('heavy_comp','—')} | — |
| Feed Mole Fraction (zF) | {feed.get('z_F','—')} | mol/mol |
| Distillate Purity (xD) | {feed.get('x_D','—')} | mol/mol |
| Bottoms Purity (xB) | {feed.get('x_B','—')} | mol/mol |
| Operating Pressure | {feed.get('P_col_bar','—')} | bar |
| Column Type | {col_type if col_type else '—'} | — |

---

## 3. THERMODYNAMIC DATA

| Parameter | Value |
|-----------|-------|
| Relative Volatility (α) | {thermo.get('alpha_avg','—')} |
| VLE Model | {thermo.get('vle_model','—')} |

---

## 4. SHORTCUT DESIGN CALCULATIONS

### 4.1 Fenske Equation — Minimum Stages
N_min = log[(xD/(1-xD)) · ((1-xB)/xB)] / log(α)

| Parameter | Value |
|-----------|-------|
| N_min (Fenske) | {shortcut.get('N_min','—')} |
| N_min excl. reboiler | {shortcut.get('N_min_excl_reboiler','—')} |

### 4.2 Underwood Equation — Minimum Reflux
α·zF/(α-θ) + (1-zF)/(1-θ) = 1 - q

| Parameter | Value |
|-----------|-------|
| R_min (Underwood) | {shortcut.get('R_min','—')} |

### 4.3 Gilliland Correlation — Actual Stages
| Parameter | Value |
|-----------|-------|
| Actual Stages (N) | {shortcut.get('N_actual','—')} |
| Operating Reflux (R) | {shortcut.get('R','—')} |
| R/R_min | {shortcut.get('R_over_Rmin','—')} |
| Feed Stage (NF, Kirkbride) | {shortcut.get('NF','—')} |

---

## 5. COLUMN SIZING

| Parameter | Value | Unit |
|-----------|-------|------|
| Column Diameter (D) | {diameter.get('D_column_std_m','—')} | m |
| Flooding Velocity | {diameter.get('u_flood_ms','—')} | m/s |
| Operating Velocity | {diameter.get('u_op_ms','—')} | m/s |
| Total Column Height (H) | {height.get('total_height_m','—')} | m |
| Active Section Height | {height.get('active_height_m','—')} | m |

---

## 6. HEAT EXCHANGER DESIGN

### 6.1 Reboiler
| Parameter | Value | Unit |
|-----------|-------|------|
| Reboiler Duty | {reboiler.get('Q_reb_kW','—')} | kW |
| Heat Transfer Area | {reboiler.get('A_reb_m2','—')} | m² |

### 6.2 Condenser
| Parameter | Value | Unit |
|-----------|-------|------|
| Condenser Duty | {condenser.get('Q_cond_kW','—')} | kW |
| Heat Transfer Area | {condenser.get('A_cond_m2','—')} | m² |

---

## 7. MECHANICAL DESIGN (ASME UG-27)

| Parameter | Value | Unit |
|-----------|-------|------|
| Shell Thickness | {mechanical.get('t_shell_mm','—')} | mm |
| Design Pressure | {mechanical.get('P_design_bar','—')} | bar |
| Material | {mechanical.get('material','—')} | — |
| Shell Weight | {mechanical.get('W_shell_kg','—')} | kg |

---

## 8. ECONOMIC EVALUATION

| Economic Parameter | Value |
|-------------------|-------|
| CAPEX (TIC) | {capex_text} |
| Annual OPEX | {opex_text} |
| Steam Rate | {energy.get('steam_rate_kg_h','—')} kg/h |
| Cooling Water | {energy.get('cw_rate_t_h','—')} t/h |
| Simple Payback | {energy.get('simple_payback_yrs','—')} years |
| NPV | {npv_text} |
| IRR | {energy.get('IRR_pct','—')} % |

---

## 9. FINAL DESIGN VALIDATION

| Category | Check | Status | Value | Recommendation |
|----------|-------|--------|-------|----------------|
{health_rows}

---

## 10. REFERENCES & STANDARDS

1. McCabe, Smith & Harriott — *Unit Operations of Chemical Engineering*, 8th Ed., McGraw-Hill
2. Seader, Henley & Roper — *Separation Process Principles*, 3rd Ed., Wiley
3. Coulson & Richardson — *Chemical Engineering Vol. 2*, 5th Ed., Butterworth-Heinemann
4. Perry's Chemical Engineers' Handbook, 9th Ed., McGraw-Hill
5. Towler & Sinnott — *Chemical Engineering Design*, 2nd Ed., Elsevier
6. Fair, J.R. — *Tray Hydraulics: Perforated Trays*, AIChE
7. ASME Boiler & Pressure Vessel Code — Section VIII, Division 1
8. API Standard 520 — Sizing, Selection, and Installation of Pressure-Relieving Devices

---
*Generated by DistillAI — Industrial Distillation Column Design System*  
*{now}*
"""
    return report


def _generate_csv(feed, thermo, shortcut, diameter, height,
                   reboiler, condenser, mechanical, energy) -> str:
    rows = [
        "Section,Parameter,Value,Unit",
        f"Feed,Flow Rate F,{feed.get('F','')},kmol/h",
        f"Feed,Light Component,{feed.get('light_comp','')},—",
        f"Feed,Heavy Component,{feed.get('heavy_comp','')},—",
        f"Feed,zF,{feed.get('z_F','')},mol/mol",
        f"Feed,xD,{feed.get('x_D','')},mol/mol",
        f"Feed,xB,{feed.get('x_B','')},mol/mol",
        f"Feed,Pressure,{feed.get('P_col_bar','')},bar",
        f"Thermo,Relative Volatility α,{thermo.get('alpha_avg','')},—",
        f"Shortcut,N_min,{shortcut.get('N_min','')},stages",
        f"Shortcut,R_min,{shortcut.get('R_min','')},—",
        f"Shortcut,N_actual,{shortcut.get('N_actual','')},stages",
        f"Shortcut,R,{shortcut.get('R','')},—",
        f"Shortcut,Feed Stage NF,{shortcut.get('NF','')},—",
        f"Sizing,Diameter D,{diameter.get('D_column_std_m','')},m",
        f"Sizing,Total Height H,{height.get('total_height_m','')},m",
        f"HeatEx,Reboiler Duty,{reboiler.get('Q_reb_kW','')},kW",
        f"HeatEx,Condenser Duty,{condenser.get('Q_cond_kW','')},kW",
        f"HeatEx,Reboiler Area,{reboiler.get('A_reb_m2','')},m²",
        f"HeatEx,Condenser Area,{condenser.get('A_cond_m2','')},m²",
        f"Mechanical,Shell Thickness,{mechanical.get('t_shell_mm','')},mm",
        f"Economics,CAPEX,{energy.get('CAPEX_USD','')},USD",
        f"Economics,OPEX,{energy.get('OPEX_USD_yr','')},USD/yr",
        f"Economics,Steam Rate,{energy.get('steam_rate_kg_h','')},kg/h",
        f"Economics,Payback,{energy.get('simple_payback_yrs','')},years",
        f"Economics,NPV,{energy.get('NPV_USD','')},USD",
        f"Economics,IRR,{energy.get('IRR_pct','')},pct",
    ]
    return "\n".join(rows)


def _render_summary_table(feed, thermo, shortcut, diameter, height,
                           reboiler, condenser, mechanical, energy):
    import pandas as pd
    data = {
        "Parameter": [
            "Feed Flow (F)", "Feed xF (zF)", "Distillate xD", "Bottoms xB",
            "Relative Volatility (α)", "N_min (Fenske)", "R_min (Underwood)",
            "N_actual", "R_actual", "Feed Stage", "Column Diameter",
            "Column Height", "Reboiler Duty", "Condenser Duty",
            "Shell Thickness", "CAPEX", "OPEX/yr", "Payback"
        ],
        "Value": [
            feed.get("F","—"), feed.get("z_F","—"), feed.get("x_D","—"), feed.get("x_B","—"),
            thermo.get("alpha_avg","—"), shortcut.get("N_min","—"), shortcut.get("R_min","—"),
            shortcut.get("N_actual","—"), shortcut.get("R","—"), shortcut.get("NF","—"),
            diameter.get("D_column_std_m","—"),
            height.get("total_height_m","—"),
            reboiler.get("Q_reb_kW","—"), condenser.get("Q_cond_kW","—"),
            mechanical.get("t_shell_mm","—"),
            _fmt_money(energy.get("CAPEX_USD"), ""),
            _fmt_money(energy.get("OPEX_USD_yr"), ""),
            f"{energy.get('simple_payback_yrs','—')} yrs",
        ],
        "Unit": [
            "kmol/h","mol/mol","mol/mol","mol/mol",
            "—","stages","—","stages","—","—",
            "m","m","kW","kW","mm","USD","USD/yr","years"
        ]
    }
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)


# ============================================================================
# FINAL PROFESSIONAL REPORT ENGINE
# These definitions intentionally override the compact report helpers above.
# ============================================================================

def _report_defaults():
    return {
        "project_title": "Binary Distillation Column Design",
        "project_no": "DISTILL-AI-001",
        "engineer_name": "Zunair Shahzad",
        "company_name": "Chemical Engineering - UET Lahore New Campus",
        "client_name": "",
        "revision": "A",
        "report_date": datetime.today(),
        "confidential": False,
    }


def _session_dict(key):
    try:
        value = st.session_state.get(key, {})
    except Exception:
        value = {}
    return value if isinstance(value, dict) else {}


def _report_settings():
    defaults = _report_defaults()
    try:
        saved = st.session_state.get("report_settings", {})
    except Exception:
        saved = {}
    if isinstance(saved, dict):
        defaults.update(saved)
    date_value = defaults.get("report_date", datetime.today())
    defaults["report_date_text"] = date_value.strftime("%B %d, %Y") if hasattr(date_value, "strftime") else str(date_value)
    return defaults


def _to_float(value, default=None):
    try:
        if value in (None, "", "-", "--", "—"):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _fmt_value(value, unit="", digits=4):
    if value in (None, "", "-", "--", "—"):
        return "-"
    if isinstance(value, bool):
        text = "Yes" if value else "No"
    else:
        numeric = _to_float(value, None)
        if numeric is not None:
            if abs(numeric) >= 1000:
                text = f"{numeric:,.2f}".rstrip("0").rstrip(".")
            else:
                text = f"{numeric:.{digits}g}"
        else:
            text = str(value)
    return f"{text} {unit}".strip()


def _ctx(feed, thermo, col_type, shortcut, diameter, height, reboiler, condenser,
         mechanical, energy, health=None):
    return {
        "settings": _report_settings(),
        "feed": feed or {},
        "thermo": thermo or {},
        "column_type": col_type or "Not selected",
        "shortcut": shortcut or {},
        "mccabe": _session_dict("mccabe"),
        "diameter": diameter or {},
        "height": height or {},
        "tray_design": _session_dict("tray_design"),
        "packing_design": _session_dict("packing_design"),
        "pressure_drop": _session_dict("pressure_drop"),
        "reboiler": reboiler or {},
        "condenser": condenser or {},
        "mechanical": mechanical or {},
        "internals": _session_dict("internals"),
        "instrumentation": _session_dict("instrumentation"),
        "energy": energy or {},
        "rigorous": _session_dict("rigorous"),
        "health": health or evaluate_design_health(),
    }


def _material_balance_rows(feed, shortcut):
    F = _to_float(feed.get("F"), None)
    zF = _to_float(feed.get("z_F"), None)
    xD = _to_float(feed.get("x_D"), None)
    xB = _to_float(feed.get("x_B"), None)
    D = _to_float(shortcut.get("D"), None)
    B = _to_float(shortcut.get("B"), None)
    rows = [
        ["Overall molar balance", "F = D + B", "-", "Basis for product flow split"],
        ["Light component balance", "F zF = D xD + B xB", "-", "Used to solve D and B"],
        ["Distillate flow", "D = F(zF - xB)/(xD - xB)", _fmt_value(D, "kmol/h"), "From component balance"],
        ["Bottoms flow", "B = F - D", _fmt_value(B, "kmol/h"), "Overall balance closure"],
    ]
    if None not in (F, zF, xD, xB):
        D_calc = F * (zF - xB) / max(xD - xB, 1e-12)
        B_calc = F - D_calc
        rows.extend([
            ["Substitution for D", f"{F:g}({zF:g} - {xB:g})/({xD:g} - {xB:g})", _fmt_value(D_calc, "kmol/h"), "Calculated from current inputs"],
            ["Substitution for B", f"{F:g} - {D_calc:.4g}", _fmt_value(B_calc, "kmol/h"), "Calculated from current inputs"],
        ])
    return rows


def _final_summary_rows(c):
    feed, thermo, shortcut = c["feed"], c["thermo"], c["shortcut"]
    diameter, height = c["diameter"], c["height"]
    tray, packing = c["tray_design"], c["packing_design"]
    reboiler, condenser = c["reboiler"], c["condenser"]
    mechanical, energy = c["mechanical"], c["energy"]
    mccabe, pressure_drop = c["mccabe"], c["pressure_drop"]
    return [
        ["System", f"{feed.get('light_comp', feed.get('light', '-'))} / {feed.get('heavy_comp', feed.get('heavy', '-'))}", "-", "Binary separation pair"],
        ["Column type", c["column_type"], "-", "Tray or packed design path"],
        ["Feed flow", _fmt_value(feed.get("F"), "kmol/h"), "Input", "Design basis"],
        ["Distillate / Bottoms", f"{_fmt_value(shortcut.get('D'), 'kmol/h')} / {_fmt_value(shortcut.get('B'), 'kmol/h')}", "Calculated", "Material balance"],
        ["Relative volatility", _fmt_value(thermo.get("alpha_avg")), "Thermodynamics", "Average alpha"],
        ["VLE model", thermo.get("vle_model", thermo.get("selected_model", "-")), "Thermodynamics", "Selected equilibrium model"],
        ["Minimum stages", _fmt_value(shortcut.get("N_min"), "stages"), "Fenske", "Total reflux limit"],
        ["Minimum reflux", _fmt_value(shortcut.get("R_min")), "Underwood", "Minimum reflux limit"],
        ["Actual stages", _fmt_value(shortcut.get("N_actual_int", shortcut.get("N_actual")), "stages"), "Gilliland", "Shortcut design"],
        ["McCabe stages", _fmt_value(mccabe.get("n_stages"), "stages"), "Graphical", "Stage stepping check"],
        ["Feed tray", _fmt_value(shortcut.get("NF", shortcut.get("feed_tray"))), "Kirkbride", "Tray from top"],
        ["Operating reflux", _fmt_value(shortcut.get("R", mccabe.get("R"))), "Design", "Selected R"],
        ["Tray efficiency", _fmt_value(tray.get("tray_efficiency", tray.get("E_overall"))), "Tray design", "If tray column"],
        ["Actual trays", _fmt_value(tray.get("N_actual_trays"), "trays"), "Tray design", "If tray column"],
        ["Packing type", packing.get("packing", "-"), "Packed design", "If packed column"],
        ["HETP / packed height", f"{_fmt_value(packing.get('HETP'), 'm')} / {_fmt_value(packing.get('Z_pack'), 'm')}", "Packed design", "If packed column"],
        ["Column diameter", _fmt_value(diameter.get("D_column_std_m", diameter.get("D_col")), "m"), "Hydraulics", "Standardized diameter"],
        ["Column height", _fmt_value(height.get("total_height_m", height.get("H_total")), "m"), "Layout", "Total tangent-to-tangent estimate"],
        ["Pressure drop", _fmt_value(pressure_drop.get("dP_total_mmHg", tray.get("dP_total_mmHg")), "mmHg"), "Hydraulics", "Column total pressure drop"],
        ["Reboiler duty", _fmt_value(reboiler.get("Q_reb_kW", energy.get("Q_reb_kW")), "kW"), "Utilities", "Bottom heat input"],
        ["Condenser duty", _fmt_value(condenser.get("Q_cond_kW", energy.get("Q_cond_kW")), "kW"), "Utilities", "Overhead heat removal"],
        ["Shell thickness", _fmt_value(mechanical.get("t_shell_mm"), "mm"), "ASME", "Mechanical shell design"],
        ["CAPEX", _fmt_money(energy.get("CAPEX_USD")), "Economics", "Installed cost estimate"],
        ["Annual OPEX", _fmt_money(energy.get("OPEX_USD_yr"), "USD/yr"), "Economics", "Operating cost estimate"],
        ["Design health", f"{c['health'].get('score', 0):.0f}%", "Validation", "Overall readiness score"],
    ]


def _build_professional_report_blocks(feed, thermo, col_type, shortcut, diameter, height,
                                      reboiler, condenser, mechanical, energy, health=None):
    c = _ctx(feed, thermo, col_type, shortcut, diameter, height, reboiler, condenser, mechanical, energy, health)
    s = c["settings"]
    f, t, sc = c["feed"], c["thermo"], c["shortcut"]
    mccabe, tray, packing = c["mccabe"], c["tray_design"], c["packing_design"]
    pressure_drop = c["pressure_drop"]
    h = c["health"]

    blocks = [
        {"kind": "cover"},
        {"kind": "section", "title": "1. Executive Summary"},
        {"kind": "text", "text": (
            "This engineering report summarizes the complete binary distillation column design generated "
            "by DistillAI. The report combines process basis, thermodynamic model selection, material "
            "balance, shortcut design, McCabe-Thiele verification, column hydraulics, heat duties, "
            "mechanical checks, economics, validation, and final design recommendations."
        )},
        {"kind": "table", "title": "Executive Design Snapshot", "headers": ["Item", "Value", "Basis", "Note"], "rows": [
            ["Prepared by", s["engineer_name"], "Developer", s["company_name"]],
            ["Report revision", s["revision"], "Controlled document", s["project_no"]],
            ["Column type", c["column_type"], "Selected path", "Tray or packed workflow"],
            ["Design health score", f"{h.get('score', 0):.0f}%", "Automated validation", f"{h.get('completion', 0)}/{h.get('total_required', 0)} checks complete"],
            ["Main separation", f"{f.get('light_comp', f.get('light', '-'))} / {f.get('heavy_comp', f.get('heavy', '-'))}", "Feed section", "Light/heavy key components"],
        ]},

        {"kind": "section", "title": "2. Introduction / Project Overview"},
        {"kind": "text", "text": (
            "The project is an AI-assisted binary distillation column design system. It was developed to "
            "support chemical engineering design work from initial feed specification to final column "
            "sizing and report generation. The software supports shortcut design, VLE analysis, "
            "McCabe-Thiele stage stepping, tray and packed column paths, process visualization, AI advisory, "
            "design case management, and professional PDF/DOCX report export."
        )},
        {"kind": "table", "title": "Software Capabilities", "headers": ["Capability", "Included Output", "Engineering Purpose"], "rows": [
            ["Feed and material balance", "F, D, B, compositions, recoveries", "Defines process basis"],
            ["Thermodynamic database", "VLE model, alpha, bubble/dew point", "Defines phase equilibrium"],
            ["Shortcut design", "Fenske, Underwood, Gilliland, Kirkbride", "Rapid design sizing"],
            ["McCabe-Thiele", "Operating lines and stage stepping", "Graphical verification"],
            ["Tray / packed design", "Hydraulics, flooding, height, internals", "Detailed column selection"],
            ["Utilities and economics", "Duties, steam, cooling water, CAPEX/OPEX", "Industrial feasibility"],
        ]},

        {"kind": "section", "title": "3. Design Basis and Input Parameters"},
        {"kind": "table", "title": "Feed and Product Specifications", "headers": ["Parameter", "Value", "Unit", "Source"], "rows": [
            ["Light component", f.get("light_comp", f.get("light", "-")), "-", "User input"],
            ["Heavy component", f.get("heavy_comp", f.get("heavy", "-")), "-", "User input"],
            ["Feed flow F", _fmt_value(f.get("F"), "kmol/h"), "kmol/h", "User input"],
            ["Feed composition zF", _fmt_value(f.get("z_F")), "mol fraction light", "User input"],
            ["Distillate purity xD", _fmt_value(f.get("x_D")), "mol fraction light", "User target"],
            ["Bottoms composition xB", _fmt_value(f.get("x_B")), "mol fraction light", "User target"],
            ["Feed condition q", _fmt_value(f.get("q", sc.get("q"))), "-", "Thermal condition"],
            ["Feed temperature", _fmt_value(f.get("T_feed"), "deg C"), "deg C", "User input"],
            ["Column pressure", _fmt_value(f.get("P_col_bar"), "bar"), "bar", "User input"],
            ["Column pressure", _fmt_value(f.get("P_col_mmHg", t.get("P_mmHg")), "mmHg"), "mmHg", "Converted basis"],
        ]},
        {"kind": "table", "title": "Design Assumptions", "headers": ["Assumption", "Value / Method", "Reason"], "rows": [
            ["Binary key-component separation", "Light/heavy component basis", "Matches project scope"],
            ["Equilibrium model", t.get("vle_model", "-"), "Used for VLE and stage calculation"],
            ["Shortcut method", "Fenske-Underwood-Gilliland", "Industrial preliminary design"],
            ["Feed tray estimate", "Kirkbride correlation", "Allocates rectifying/stripping stages"],
            ["Column hydraulics", "Fair method / GPDC depending on column type", "Flooding-based sizing"],
        ]},

        {"kind": "section", "title": "4. Process Calculations and Material Balance"},
        {"kind": "text", "text": "The process calculation begins from total and component balances. Product flow rates are solved from the specified feed composition and desired top/bottom purities."},
        {"kind": "table", "title": "Step-by-Step Material Balance", "headers": ["Step", "Equation / Substitution", "Result", "Comment"], "rows": _material_balance_rows(f, sc)},
        {"kind": "table", "title": "Mass Balance Summary", "headers": ["Stream", "Flow", "Light fraction", "Heavy fraction"], "rows": [
            ["Feed", _fmt_value(f.get("F"), "kmol/h"), _fmt_value(f.get("z_F")), _fmt_value(1 - _to_float(f.get("z_F"), 1), digits=4) if _to_float(f.get("z_F"), None) is not None else "-"],
            ["Distillate", _fmt_value(sc.get("D"), "kmol/h"), _fmt_value(f.get("x_D")), _fmt_value(1 - _to_float(f.get("x_D"), 1), digits=4) if _to_float(f.get("x_D"), None) is not None else "-"],
            ["Bottoms", _fmt_value(sc.get("B"), "kmol/h"), _fmt_value(f.get("x_B")), _fmt_value(1 - _to_float(f.get("x_B"), 1), digits=4) if _to_float(f.get("x_B"), None) is not None else "-"],
        ]},

        {"kind": "section", "title": "5. Thermodynamic / VLE Analysis"},
        {"kind": "table", "title": "Thermodynamic Results", "headers": ["Parameter", "Value", "Unit", "Meaning"], "rows": [
            ["Selected VLE model", t.get("vle_model", "-"), "-", "Model used for equilibrium calculations"],
            ["Advisor suggested model", t.get("suggested_vle_model", "-"), "-", "Rule-based model advisor"],
            ["Non-ideality level", t.get("nonideality_level", t.get("non_ideality_level", "-")), "-", "Physical deviation from ideal behavior"],
            ["Average relative volatility", _fmt_value(t.get("alpha_avg")), "-", "Separation difficulty indicator"],
            ["Alpha at top", _fmt_value(t.get("alpha_top")), "-", "Top section volatility"],
            ["Alpha at feed", _fmt_value(t.get("alpha_feed")), "-", "Feed section volatility"],
            ["Alpha at bottom", _fmt_value(t.get("alpha_bot")), "-", "Bottom section volatility"],
            ["Feed bubble point", _fmt_value(t.get("T_bubble_F"), "deg C"), "deg C", "Liquid begins boiling"],
            ["Feed dew point", _fmt_value(t.get("T_dew_F"), "deg C"), "deg C", "Vapor begins condensing"],
        ]},
        {"kind": "visual", "visual": "vle", "title": "VLE Equilibrium Diagram", "caption": "Generated from the selected relative-volatility/VLE basis for the binary pair."},

        {"kind": "section", "title": "6. Shortcut Distillation Design"},
        {"kind": "table", "title": "Shortcut Equations and Results", "headers": ["Method", "Engineering equation", "Result", "Purpose"], "rows": [
            ["Fenske", "Nmin = log[(xD/(1-xD))*((1-xB)/xB)] / log(alpha)", _fmt_value(sc.get("N_min"), "stages"), "Minimum stages at total reflux"],
            ["Underwood", "Solves theta, then Rmin from relative volatility split", _fmt_value(sc.get("R_min")), "Minimum reflux ratio"],
            ["Gilliland", "Relates X=(R-Rmin)/(R+1) and Y=(N-Nmin)/(N+1)", _fmt_value(sc.get("N_actual_int", sc.get("N_actual")), "stages"), "Actual theoretical stages"],
            ["Kirkbride", "Distributes stages above/below feed", _fmt_value(sc.get("NF", sc.get("feed_tray"))), "Feed stage location"],
            ["Operating reflux", "R = multiplier x Rmin", _fmt_value(sc.get("R")), "Selected operating reflux"],
        ]},

        {"kind": "section", "title": "7. McCabe-Thiele Method"},
        {"kind": "table", "title": "McCabe-Thiele Calculation Summary", "headers": ["Item", "Value", "Interpretation"], "rows": [
            ["Equilibrium equation", "y = alpha*x / [1 + (alpha - 1)*x]", "Constant relative volatility basis"],
            ["Rectifying line", "y = [R/(R+1)]x + xD/(R+1)", "Top operating section"],
            ["Feed q-line", "y = [q/(q-1)]x - zF/(q-1)", "Feed thermal condition line"],
            ["Stripping line", "Through bottoms point and feed intersection", "Bottom operating section"],
            ["Theoretical stages", _fmt_value(mccabe.get("n_stages", sc.get("N_actual_int")), "stages"), "Graphical stage count"],
            ["Rectifying / stripping stages", f"{_fmt_value(mccabe.get('n_rectifying'))} / {_fmt_value(mccabe.get('n_stripping'))}", "Stage distribution"],
            ["Feed intersection", f"({_fmt_value(mccabe.get('x_int'))}, {_fmt_value(mccabe.get('y_int'))})", "Line switching point"],
        ]},
        {"kind": "visual", "visual": "mccabe", "title": "McCabe-Thiele Stage-Stepping Diagram", "caption": "Generated from current alpha, reflux ratio, q-value, and composition targets."},

        {"kind": "section", "title": "8. Detailed Column Design Results"},
        {"kind": "table", "title": "Tray Column Results", "headers": ["Parameter", "Value", "Unit", "Purpose"], "rows": [
            ["Tray type", tray.get("tray_type", "-"), "-", "Selected tray hardware"],
            ["Tray spacing", _fmt_value(tray.get("tray_spacing_m", tray.get("tray_spacing")), "m"), "m", "Column vertical layout"],
            ["Overall tray efficiency", _fmt_value(tray.get("tray_efficiency", tray.get("E_overall"))), "-", "Converts theoretical to actual trays"],
            ["Actual trays", _fmt_value(tray.get("N_actual_trays"), "trays"), "trays", "Mechanical tray count"],
            ["Flood fraction", _fmt_value(tray.get("flood_frac", tray.get("flood_fraction"))), "-", "Hydraulic operating margin"],
            ["Hole velocity", _fmt_value(tray.get("u_hole"), "m/s"), "m/s", "Vapor through sieve holes"],
            ["Weeping velocity", _fmt_value(tray.get("u_weep"), "m/s"), "m/s", "Minimum stable vapor velocity"],
            ["Total tray pressure drop", _fmt_value(tray.get("dP_total_mmHg"), "mmHg"), "mmHg", "Hydraulic loss"],
            ["Entrainment factor", _fmt_value(tray.get("entrainment_psi")), "-", "Liquid carryover indicator"],
        ]},
        {"kind": "table", "title": "Packed Column Results", "headers": ["Parameter", "Value", "Unit", "Purpose"], "rows": [
            ["Packing type", packing.get("packing", "-"), "-", "Selected packing"],
            ["HETP", _fmt_value(packing.get("HETP"), "m"), "m", "Height equivalent to theoretical plate"],
            ["Packed height", _fmt_value(packing.get("Z_pack"), "m"), "m", "Required packing bed"],
            ["Column diameter", _fmt_value(packing.get("D_col"), "m"), "m", "Packed column hydraulic diameter"],
            ["Flood velocity", _fmt_value(packing.get("u_flood"), "m/s"), "m/s", "Flooding limit"],
            ["Operating velocity", _fmt_value(packing.get("u_op"), "m/s"), "m/s", "Selected operation"],
            ["Total pressure drop", _fmt_value(packing.get("dP_tot_Pa"), "Pa"), "Pa", "Packed bed pressure loss"],
            ["Total height", _fmt_value(packing.get("H_total"), "m"), "m", "Includes disengagement allowances"],
        ]},
        {"kind": "table", "title": "Column Diameter, Height, and Pressure Drop", "headers": ["Parameter", "Value", "Unit", "Method"], "rows": [
            ["Column diameter", _fmt_value(c["diameter"].get("D_column_std_m"), "m"), "m", "Fair/GPDC hydraulic sizing"],
            ["Net area", _fmt_value(c["diameter"].get("A_net_m2"), "m2"), "m2", "Vapor capacity area"],
            ["Operating velocity", _fmt_value(c["diameter"].get("u_op_ms", c["diameter"].get("u_op_m_s")), "m/s"), "m/s", "Selected operating point"],
            ["Flooding velocity", _fmt_value(c["diameter"].get("u_flood_ms", c["diameter"].get("u_flood_m_s")), "m/s"), "m/s", "Capacity limit"],
            ["Total height", _fmt_value(c["height"].get("total_height_m", c["height"].get("H_total")), "m"), "m", "Mechanical layout estimate"],
            ["Active height", _fmt_value(c["height"].get("active_height_m"), "m"), "m", "Mass-transfer section"],
            ["Total pressure drop", _fmt_value(pressure_drop.get("dP_total_mmHg"), "mmHg"), "mmHg", "Pressure-drop section"],
            ["Bottom pressure", _fmt_value(pressure_drop.get("P_bot_bar"), "bar"), "bar", "Top pressure plus column drop"],
        ]},

        {"kind": "section", "title": "9. Heat Exchanger and Utility Design"},
        {"kind": "table", "title": "Reboiler / Condenser / Utility Summary", "headers": ["Parameter", "Value", "Unit", "Role"], "rows": [
            ["Reboiler duty", _fmt_value(c["reboiler"].get("Q_reb_kW", c["energy"].get("Q_reb_kW")), "kW"), "kW", "Bottom vapor generation"],
            ["Reboiler area", _fmt_value(c["reboiler"].get("A_reb_m2"), "m2"), "m2", "Heat-transfer surface"],
            ["Condenser duty", _fmt_value(c["condenser"].get("Q_cond_kW", c["energy"].get("Q_cond_kW")), "kW"), "kW", "Overhead condensation"],
            ["Condenser area", _fmt_value(c["condenser"].get("A_cond_m2"), "m2"), "m2", "Heat-transfer surface"],
            ["Steam rate", _fmt_value(c["energy"].get("steam_rate_kg_h"), "kg/h"), "kg/h", "Heating utility"],
            ["Cooling water rate", _fmt_value(c["energy"].get("cw_rate_t_h"), "t/h"), "t/h", "Cooling utility"],
        ]},

        {"kind": "section", "title": "10. Mechanical Design, Internals, and Instrumentation"},
        {"kind": "table", "title": "Mechanical and Control Summary", "headers": ["Area", "Parameter", "Value", "Engineering note"], "rows": [
            ["Mechanical", "Shell thickness", _fmt_value(c["mechanical"].get("t_shell_mm"), "mm"), "ASME UG-27 pressure vessel check"],
            ["Mechanical", "Design pressure", _fmt_value(c["mechanical"].get("P_design_bar"), "bar"), "Pressure vessel basis"],
            ["Mechanical", "Material", c["mechanical"].get("material", "-"), "Selected construction material"],
            ["Internals", "Distributors", _fmt_value(c["internals"].get("n_distributors")), "Liquid distribution hardware"],
            ["Internals", "Redistributors", _fmt_value(c["internals"].get("n_redistributors")), "Packed-column liquid management"],
            ["Internals", "Mist eliminator", c["internals"].get("mist_eliminator_type", "-"), "Overhead entrainment protection"],
            ["Instrumentation", "Control loops", _fmt_value(c["instrumentation"].get("n_control_loops")), "Basic regulatory control"],
            ["Instrumentation", "SIL level", c["instrumentation"].get("SIL_level", "-"), "Safety instrumented function target"],
            ["Instrumentation", "PSV tag", c["instrumentation"].get("PSV_tag", "-"), "Pressure relief device"],
        ]},

        {"kind": "section", "title": "11. Economics and Optimization"},
        {"kind": "table", "title": "Economic Results", "headers": ["Metric", "Value", "Basis", "Interpretation"], "rows": [
            ["CAPEX", _fmt_money(c["energy"].get("CAPEX_USD")), "Installed cost", "Capital estimate"],
            ["Annual OPEX", _fmt_money(c["energy"].get("OPEX_USD_yr"), "USD/yr"), "Utility + operating cost", "Annual operating expense"],
            ["Simple payback", _fmt_value(c["energy"].get("simple_payback_yrs"), "years"), "Economic metric", "Lower is better"],
            ["NPV", _fmt_money(c["energy"].get("NPV_USD")), "Discounted cash flow", "Project value"],
            ["IRR", _fmt_value(c["energy"].get("IRR_pct"), "%"), "Discounted cash flow", "Return metric"],
        ]},

        {"kind": "section", "title": "12. Important Graphs and Visualizations"},
        {"kind": "text", "text": "The downloadable report includes generated static engineering visuals. The Streamlit app also keeps the interactive versions for live simulation, sliders, animation, and detailed graph inspection."},
        {"kind": "visual", "visual": "process", "title": "Process Flow / Column Visualization", "caption": "Column, condenser, reflux drum, reboiler, feed, distillate, bottoms, vapor and liquid movement."},
        {"kind": "table", "title": "Visualization Index", "headers": ["Visualization", "Purpose", "Location in App"], "rows": [
            ["VLE x-y diagram", "Shows equilibrium relationship and 45-degree reference", "Thermodynamics DB"],
            ["T-x-y phase diagram", "Shows bubble/dew curves and two-phase zone", "Thermodynamics DB"],
            ["McCabe-Thiele plot", "Shows operating lines, q-line, and stage stepping", "McCabe-Thiele"],
            ["Process animation", "Shows vapor rising, liquid reflux, feed, distillate and bottoms", "Visualization"],
            ["PFD / column schematic", "Shows condenser, reflux drum, reboiler and streams", "Visualization"],
            ["Economic charts", "Shows cost and utility trends", "Energy & Economics"],
        ]},

        {"kind": "section", "title": "13. Final Design Summary"},
        {"kind": "table", "title": "Master Final Output Table", "headers": ["Parameter", "Value", "Source", "Comment"], "rows": _final_summary_rows(c)},

        {"kind": "section", "title": "14. Conclusion"},
        {"kind": "text", "text": (
            "The completed design package demonstrates a full preliminary-to-detailed workflow for binary "
            "distillation column design. It combines classical chemical engineering methods with interactive "
            "visualization, AI-assisted advisory, design health checking, case saving/loading, and professional "
            "report generation. The workflow is suitable for academic design projects, early-stage industrial "
            "screening, and training users to understand how feed specifications, VLE behavior, reflux ratio, "
            "column hydraulics, utilities, and economics interact."
        )},

        {"kind": "section", "title": "15. Appendix - Validation, References, and Standards"},
        {"kind": "table", "title": "Automated Design Validation", "headers": ["Category", "Check", "Status", "Value", "Recommendation"], "rows": [
            [row.get("Category", "-"), row.get("Check", "-"), row.get("Status", "-"), row.get("Value", "-"), row.get("Recommendation", "-")]
            for row in h.get("checks", [])
        ] or [["Design", "Validation checks", "-", "-", "Run the design sections to populate validation data."]]},
        {"kind": "table", "title": "References and Industrial Standards", "headers": ["Reference", "Use in Report"], "rows": [
            ["McCabe, Smith and Harriott - Unit Operations of Chemical Engineering", "Distillation fundamentals and McCabe-Thiele method"],
            ["Seader, Henley and Roper - Separation Process Principles", "Separation design and VLE interpretation"],
            ["Coulson and Richardson - Chemical Engineering, Vol. 2", "Equipment design and process calculations"],
            ["Perry's Chemical Engineers' Handbook", "Physical properties, packing data, utility estimates"],
            ["Towler and Sinnott - Chemical Engineering Design", "Process design and economics"],
            ["ASME BPVC Section VIII Division 1", "Pressure vessel shell design"],
            ["API 520 / 521", "Pressure relief and process safety basis"],
            ["TEMA Standards", "Shell-and-tube exchanger design reference"],
        ]},

        {"kind": "section", "title": "16. About the Developer"},
        {"kind": "table", "title": "Developer Profile", "headers": ["Item", "Detail"], "rows": [
            ["Name", "Zunair Shahzad"],
            ["Program", "Chemical Engineering"],
            ["Institute", "UET Lahore - New Campus"],
            ["Focus", "AI-assisted Chemical Engineering Projects"],
            ["Project", "DistillAI - Binary Distillation Column Design System"],
            ["Email", "Eng.zunairshahzad@gmail.com"],
            ["Phone / WhatsApp", "+923074274294"],
        ]},
        {"kind": "text", "text": (
            "This project reflects the use of programming, process design calculations, visualization, and AI "
            "assistance to make chemical engineering design more interactive, transparent, and easier to verify."
        )},
    ]
    return blocks, c


def _render_report_preview(feed, thermo, col_type, shortcut, diameter, height,
                           reboiler, condenser, mechanical, energy):
    blocks, c = _build_professional_report_blocks(feed, thermo, col_type, shortcut, diameter, height,
                                                  reboiler, condenser, mechanical, energy, evaluate_design_health())
    s = c["settings"]
    st.markdown(
        f"""
        <div class="phase4-report-preview" style="padding:0;overflow:hidden;">
            <div style="background:linear-gradient(135deg,#071018,#0b3550);padding:34px 32px;border-bottom:3px solid #f8d477;">
                <div style="color:#f8d477;font-size:0.9rem;font-weight:900;letter-spacing:0.12em;text-transform:uppercase;">Professional Engineering Report Package</div>
                <h2 style="margin:8px 0 4px;color:#00d4ff;">Distillation Column Design Report</h2>
                <h3 style="margin:0;color:#eaf6ff;">{s['project_title']}</h3>
                <p style="margin:12px 0 0;color:#eaf6ff;font-weight:800;">Prepared by {s['engineer_name']} | {s['company_name']}</p>
                <p style="margin:4px 0 0;color:#93c5fd;">Report No. {s['project_no']} | Revision {s['revision']} | {s['report_date_text']}</p>
            </div>
            <div style="padding:24px 28px;">
                <h3>Final Report Structure</h3>
                <p>This preview shows the exact professional structure used in the downloadable PDF and DOCX reports.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    toc_rows = []
    for block in blocks:
        if block["kind"] == "section":
            toc_rows.append({"Section": block["title"], "Included": "Yes"})
    st.dataframe(pd.DataFrame(toc_rows), use_container_width=True, hide_index=True)
    st.markdown("### Final Output Snapshot")
    st.dataframe(pd.DataFrame(_final_summary_rows(c), columns=["Parameter", "Value", "Source", "Comment"]),
                 use_container_width=True, hide_index=True)


def _make_visual_png(kind, c):
    try:
        from PIL import Image, ImageDraw
    except Exception:
        return None

    width, height_px = 1100, 650
    img = Image.new("RGB", (width, height_px), "#071018")
    draw = ImageDraw.Draw(img)
    cyan, yellow, red, green, white, muted = "#00d4ff", "#f8d477", "#ff5b6e", "#22c55e", "#f8fbff", "#7aa2c7"
    draw.rectangle([0, 0, width - 1, height_px - 1], outline=cyan, width=4)
    title = {"vle": "VLE Equilibrium Diagram", "mccabe": "McCabe-Thiele Stage-Stepping", "process": "Distillation Process Visualization"}.get(kind, "Engineering Visualization")
    draw.text((34, 24), title, fill=yellow)

    if kind in {"vle", "mccabe"}:
        left, top, right, bottom = 90, 92, 850, 560
        draw.rectangle([left, top, right, bottom], outline="#1e6091", width=2)
        for i in range(1, 10):
            x = left + (right - left) * i / 10
            y = top + (bottom - top) * i / 10
            draw.line([x, top, x, bottom], fill="#16324a", width=1)
            draw.line([left, y, right, y], fill="#16324a", width=1)

        def sx(x): return left + max(0, min(1, x)) * (right - left)
        def sy(y): return bottom - max(0, min(1, y)) * (bottom - top)

        draw.line([sx(0), sy(0), sx(1), sy(1)], fill=muted, width=3)
        alpha = _to_float(c["thermo"].get("alpha_avg", c["shortcut"].get("alpha")), 2.5) or 2.5
        curve = []
        for i in range(101):
            x = i / 100
            y = alpha * x / max(1 + (alpha - 1) * x, 1e-9)
            curve.append((sx(x), sy(y)))
        draw.line(curve, fill=cyan, width=5)
        draw.text((left, bottom + 18), "x - liquid mole fraction light key", fill=white)
        draw.text((left - 54, top - 8), "y", fill=white)

        if kind == "mccabe":
            f = c["feed"]
            sc, mc = c["shortcut"], c["mccabe"]
            xD = _to_float(f.get("x_D"), 0.95)
            xB = _to_float(f.get("x_B"), 0.05)
            zF = _to_float(f.get("z_F"), 0.5)
            R = _to_float(mc.get("R", sc.get("R")), 1.5) or 1.5
            slope = R / (R + 1)
            intercept = xD / (R + 1)
            line = [(sx(0), sy(intercept)), (sx(1), sy(slope + intercept))]
            draw.line(line, fill=green, width=4)
            draw.line([sx(zF), sy(0), sx(zF), sy(1)], fill=red, width=3)
            steps = mc.get("stages", [])
            if isinstance(steps, list) and steps:
                pts = [(sx(xD), sy(xD))]
                for row in steps[:18]:
                    if isinstance(row, dict):
                        pts.append((sx(_to_float(row.get("x"), xB)), sy(_to_float(row.get("y"), xB))))
                if len(pts) > 1:
                    draw.line(pts, fill=yellow, width=3)
            else:
                x, y = xD, xD
                for _ in range(8):
                    x2 = max(xB, x - (xD - xB) / 8)
                    draw.line([sx(x), sy(y), sx(x2), sy(y), sx(x2), sy(max(xB, y - 0.09))], fill=yellow, width=3)
                    x, y = x2, max(xB, y - 0.09)
            draw.text((880, 122), f"Stages: {_fmt_value(mc.get('n_stages', sc.get('N_actual_int')))}", fill=yellow)
            draw.text((880, 162), f"R: {_fmt_value(R)}", fill=green)
            draw.text((880, 202), f"Feed q: {_fmt_value(f.get('q', sc.get('q')))}", fill=red)
        else:
            draw.text((880, 122), f"Model: {c['thermo'].get('vle_model', '-')}", fill=yellow)
            draw.text((880, 162), f"Alpha avg: {_fmt_value(alpha)}", fill=cyan)
            draw.text((880, 202), "45-degree line shown for reference", fill=muted)

    if kind == "process":
        draw.rounded_rectangle([455, 95, 645, 560], radius=42, outline=cyan, width=5, fill="#0d2032")
        for y in range(145, 520, 42):
            draw.line([470, y, 630, y], fill="#1e6091", width=2)
        draw.rectangle([760, 92, 980, 170], outline="#90e0ef", width=4, fill="#0d2032")
        draw.rectangle([745, 455, 980, 545], outline=red, width=4, fill="#201018")
        draw.ellipse([770, 220, 920, 330], outline=yellow, width=4, fill="#1a1420")
        draw.line([645, 130, 760, 130], fill=white, width=4)
        draw.line([645, 502, 745, 502], fill=white, width=4)
        draw.line([170, 318, 455, 318], fill=green, width=5)
        draw.line([870, 170, 870, 220], fill=yellow, width=4)
        draw.line([790, 300, 645, 155], fill=yellow, width=3)
        draw.text((488, 70), "COLUMN", fill=cyan)
        draw.text((790, 118), "CONDENSER", fill="#90e0ef")
        draw.text((788, 490), "REBOILER", fill=red)
        draw.text((790, 258), "REFLUX DRUM", fill=yellow)
        draw.text((170, 292), "FEED", fill=green)
        draw.text((900, 188), "DISTILLATE", fill=white)
        draw.text((900, 560), "BOTTOMS", fill=white)

    output = io.BytesIO()
    img.save(output, format="PNG")
    return output.getvalue()


def _visual_assets(c):
    return {kind: data for kind in ("vle", "mccabe", "process") if (data := _make_visual_png(kind, c))}


def _generate_markdown_report(feed, thermo, col_type, shortcut, diameter, height,
                              reboiler, condenser, mechanical, energy, health=None) -> str:
    blocks, c = _build_professional_report_blocks(feed, thermo, col_type, shortcut, diameter, height,
                                                  reboiler, condenser, mechanical, energy, health)
    s = c["settings"]
    lines = [
        "# DISTILLATION COLUMN DESIGN REPORT",
        "",
        f"**Project:** {s['project_title']}",
        f"**Prepared by:** {s['engineer_name']}",
        f"**Institute:** {s['company_name']}",
        f"**Report No.:** {s['project_no']} | **Revision:** {s['revision']} | **Date:** {s['report_date_text']}",
        "",
        "---",
        "",
    ]
    for block in blocks:
        kind = block["kind"]
        if kind == "cover":
            continue
        if kind == "section":
            lines.extend([f"## {block['title']}", ""])
        elif kind == "text":
            lines.extend([block["text"], ""])
        elif kind == "table":
            headers = block["headers"]
            lines.extend([f"### {block['title']}", ""])
            lines.append("| " + " | ".join(headers) + " |")
            lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
            for row in block["rows"]:
                safe = [str(cell).replace("\n", " ") for cell in row]
                lines.append("| " + " | ".join(safe) + " |")
            lines.append("")
        elif kind == "visual":
            lines.extend([f"### {block['title']}", block.get("caption", ""), ""])
    return "\n".join(lines)


def _generate_csv(feed, thermo, shortcut, diameter, height,
                  reboiler, condenser, mechanical, energy) -> str:
    blocks, _ = _build_professional_report_blocks(feed, thermo, st.session_state.get("column_type", "tray"),
                                                  shortcut, diameter, height, reboiler, condenser,
                                                  mechanical, energy, evaluate_design_health())
    rows = ["Section,Parameter,Value,Unit_or_Source,Comment"]
    current_section = "Report"
    for block in blocks:
        if block["kind"] == "section":
            current_section = block["title"].replace(",", " ")
        elif block["kind"] == "table":
            headers = block["headers"]
            for row in block["rows"]:
                cells = [str(x).replace(",", ";").replace("\n", " ") for x in row[:4]]
                while len(cells) < 4:
                    cells.append("")
                rows.append(",".join([current_section] + cells[:4]))
    return "\n".join(rows)


def _pdf_color(hex_color, stroke=False):
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16) / 255
    g = int(hex_color[2:4], 16) / 255
    b = int(hex_color[4:6], 16) / 255
    return f"{r:.3f} {g:.3f} {b:.3f} {'RG' if stroke else 'rg'}"


def _pdf_line(commands, x1, y1, x2, y2, color="#00b4d8", width=1.0):
    commands.append(_pdf_color(color, stroke=True))
    commands.append(f"{width:g} w {x1:.1f} {y1:.1f} m {x2:.1f} {y2:.1f} l S")


def _pdf_rect(commands, x, y, w, h, fill=None, stroke="#00b4d8", width=1.0):
    if fill:
        commands.append(_pdf_color(fill))
        commands.append(f"{x:.1f} {y:.1f} {w:.1f} {h:.1f} re f")
    commands.append(_pdf_color(stroke, stroke=True))
    commands.append(f"{width:g} w {x:.1f} {y:.1f} {w:.1f} {h:.1f} re S")


def _draw_pdf_visual(commands, visual, x, y_top, w, h, c):
    _pdf_rect(commands, x, y_top - h, w, h, fill="#071018", stroke="#00b4d8", width=1.3)
    px0, py0 = x + 42, y_top - h + 44
    px1, py1 = x + w - 120, y_top - 42

    if visual in {"vle", "mccabe"}:
        _pdf_rect(commands, px0, py0, px1 - px0, py1 - py0, fill="#0d1520", stroke="#1e6091", width=0.8)
        for i in range(1, 5):
            gx = px0 + (px1 - px0) * i / 5
            gy = py0 + (py1 - py0) * i / 5
            _pdf_line(commands, gx, py0, gx, py1, "#1e3a5f", 0.35)
            _pdf_line(commands, px0, gy, px1, gy, "#1e3a5f", 0.35)

        def sx(v): return px0 + max(0, min(1, v)) * (px1 - px0)
        def sy(v): return py0 + max(0, min(1, v)) * (py1 - py0)

        _pdf_line(commands, sx(0), sy(0), sx(1), sy(1), "#94a3b8", 1.2)
        alpha = _to_float(c["thermo"].get("alpha_avg", c["shortcut"].get("alpha")), 2.5) or 2.5
        points = []
        for i in range(61):
            xx = i / 60
            yy = alpha * xx / max(1 + (alpha - 1) * xx, 1e-9)
            points.append((sx(xx), sy(yy)))
        commands.append(_pdf_color("#00d4ff", stroke=True))
        commands.append("2.1 w " + " ".join(
            [f"{points[0][0]:.1f} {points[0][1]:.1f} m"] +
            [f"{a:.1f} {b:.1f} l" for a, b in points[1:]]
        ) + " S")
        if visual == "mccabe":
            f = c["feed"]
            sc, mc = c["shortcut"], c["mccabe"]
            xD = _to_float(f.get("x_D"), 0.95)
            xB = _to_float(f.get("x_B"), 0.05)
            zF = _to_float(f.get("z_F"), 0.5)
            R = _to_float(mc.get("R", sc.get("R")), 1.5) or 1.5
            slope = R / (R + 1)
            intercept = xD / (R + 1)
            _pdf_line(commands, sx(0), sy(intercept), sx(1), sy(slope + intercept), "#22c55e", 1.6)
            _pdf_line(commands, sx(zF), sy(0), sx(zF), sy(1), "#ff5b6e", 1.1)
            xcur, ycur = xD, xD
            for _ in range(8):
                xnext = max(xB, xcur - (xD - xB) / 8)
                ynext = max(xB, ycur - 0.09)
                _pdf_line(commands, sx(xcur), sy(ycur), sx(xnext), sy(ycur), "#f8d477", 1.1)
                _pdf_line(commands, sx(xnext), sy(ycur), sx(xnext), sy(ynext), "#f8d477", 1.1)
                xcur, ycur = xnext, ynext
        return

    # Process schematic
    col_x, col_y, col_w, col_h = x + 210, y_top - h + 44, 92, h - 88
    _pdf_rect(commands, col_x, col_y, col_w, col_h, fill="#0d2032", stroke="#00d4ff", width=1.6)
    for i in range(1, 8):
        yy = col_y + col_h * i / 8
        _pdf_line(commands, col_x + 8, yy, col_x + col_w - 8, yy, "#1e6091", 0.7)
    _pdf_rect(commands, x + 370, y_top - 92, 120, 42, fill="#0d2032", stroke="#90e0ef", width=1.2)
    _pdf_rect(commands, x + 366, y_top - h + 58, 126, 46, fill="#201018", stroke="#ff5b6e", width=1.2)
    _pdf_line(commands, x + 70, y_top - h / 2, col_x, y_top - h / 2, "#22c55e", 2.0)
    _pdf_line(commands, col_x + col_w, y_top - 72, x + 370, y_top - 72, "#eaf6ff", 1.4)
    _pdf_line(commands, col_x + col_w, col_y + 28, x + 366, col_y + 28, "#eaf6ff", 1.4)


def _generate_pdf_report(feed, thermo, col_type, shortcut, diameter, height,
                         reboiler, condenser, mechanical, energy, health=None) -> bytes:
    blocks, c = _build_professional_report_blocks(feed, thermo, col_type, shortcut, diameter, height,
                                                  reboiler, condenser, mechanical, energy, health)
    s = c["settings"]
    page_w, page_h = 595, 842
    margin, top, bottom = 44, 790, 46
    pages = []
    y = top

    def new_page(bg="#f8fbff"):
        nonlocal y
        commands = [_pdf_color(bg), f"0 0 {page_w} {page_h} re f"]
        pages.append(commands)
        y = top
        return commands

    def write(text, size=9, color="#111827", bold=False, x=None, leading=None, max_width=92):
        nonlocal y
        if not pages:
            new_page()
        x = margin if x is None else x
        font = "F2" if bold else "F1"
        leading = leading or (size + 4)
        wrapped = textwrap.wrap(_safe_report_text(text), width=max_width) or [""]
        for line in wrapped:
            if y < bottom + leading:
                new_page()
            pages[-1].append(_pdf_color(color))
            pages[-1].append(f"BT /{font} {size:g} Tf 1 0 0 1 {x:.1f} {y:.1f} Tm ({_pdf_escape(line)}) Tj ET")
            y -= leading

    def draw_table(title, headers, rows):
        nonlocal y
        write(title, size=10.5, color="#00a3c4", bold=True, leading=15)
        write(" | ".join(headers), size=7.6, color="#ff5b6e", bold=True, leading=11, max_width=120)
        _pdf_line(pages[-1], margin, y + 3, page_w - margin, y + 3, "#cbd5e1", 0.45)
        for idx, row in enumerate(rows):
            line = " | ".join(_safe_report_text(cell) for cell in row)
            write(line, size=7.4, color="#111827", leading=10, max_width=128)
            if idx > 0 and idx % 18 == 0:
                y -= 3
        y -= 8

    for block in blocks:
        kind = block["kind"]
        if kind == "cover":
            cmd = new_page("#071018")
            _pdf_rect(cmd, 34, 34, page_w - 68, page_h - 68, fill=None, stroke="#00d4ff", width=1.4)
            _pdf_rect(cmd, 42, page_h - 182, page_w - 84, 104, fill="#0b3550", stroke="#f8d477", width=1.2)
            y = page_h - 115
            write("DISTILLATION COLUMN DESIGN REPORT", 22, "#f8d477", True, x=66, leading=30, max_width=60)
            write(s["project_title"], 14, "#eaf6ff", True, x=66, leading=22, max_width=70)
            y = page_h - 260
            write("Prepared by", 10, "#93c5fd", True, x=66, leading=16)
            write(s["engineer_name"], 20, "#00d4ff", True, x=66, leading=26)
            write(s["company_name"], 11, "#eaf6ff", True, x=66, leading=18)
            y = page_h - 390
            cover_rows = [
                f"Report No.: {s['project_no']}",
                f"Revision: {s['revision']}",
                f"Date: {s['report_date_text']}",
                f"Column Type: {c['column_type']}",
                f"Design Health: {c['health'].get('score', 0):.0f}%",
            ]
            for row in cover_rows:
                write(row, 10.5, "#f8fbff", False, x=66, leading=18)
            write("AI-assisted Chemical Engineering Projects", 11, "#f8d477", True, x=66, leading=18)
            new_page()
        elif kind == "section":
            if y < 120:
                new_page()
            y -= 6
            _pdf_line(pages[-1], margin, y + 7, page_w - margin, y + 7, "#00b4d8", 0.8)
            write(block["title"], 13, "#0b7894", True, leading=20)
        elif kind == "text":
            write(block["text"], 8.8, "#1f2937", False, leading=12.2)
            y -= 4
        elif kind == "table":
            draw_table(block["title"], block["headers"], block["rows"])
        elif kind == "visual":
            if y < 330:
                new_page()
            write(block["title"], 10.5, "#0b7894", True, leading=14)
            top_y = y - 5
            _draw_pdf_visual(pages[-1], block["visual"], margin, top_y, page_w - 2 * margin, 240, c)
            y = top_y - 258
            write(block.get("caption", ""), 7.8, "#475569", False, leading=11)

    for i, cmd in enumerate(pages, start=1):
        _pdf_line(cmd, margin, 28, page_w - margin, 28, "#cbd5e1", 0.45)
        cmd.append(_pdf_color("#64748b"))
        footer = f"DistillAI | {s['engineer_name']} | Rev {s['revision']} | Page {i} of {len(pages)}"
        cmd.append(f"BT /F1 7.5 Tf 1 0 0 1 {margin:.1f} 17 Tm ({_pdf_escape(footer)}) Tj ET")

    objects = [None]

    def add_object(obj):
        objects.append(obj)
        return len(objects) - 1

    add_object("<< /Type /Catalog /Pages 2 0 R >>")
    add_object("")
    f1 = add_object("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    f2 = add_object("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
    page_ids = []
    for commands in pages:
        stream = "\n".join(commands).encode("latin-1", "replace")
        content_id = add_object(b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream")
        page_id = add_object(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {page_w} {page_h}] "
            f"/Resources << /Font << /F1 {f1} 0 R /F2 {f2} 0 R >> >> /Contents {content_id} 0 R >>"
        )
        page_ids.append(page_id)
    objects[2] = f"<< /Type /Pages /Kids [{' '.join(f'{pid} 0 R' for pid in page_ids)}] /Count {len(page_ids)} >>"

    pdf = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for obj_id, obj in enumerate(objects[1:], start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{obj_id} 0 obj\n".encode("ascii"))
        pdf.extend(obj if isinstance(obj, bytes) else str(obj).encode("latin-1", "replace"))
        pdf.extend(b"\nendobj\n")
    xref_start = len(pdf)
    pdf.extend(f"xref\n0 {len(objects)}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(f"trailer\n<< /Size {len(objects)} /Root 1 0 R >>\nstartxref\n{xref_start}\n%%EOF".encode("ascii"))
    return bytes(pdf)


def _docx_paragraph2(text, kind="text", align="left"):
    styles = {
        "title": (40, True, "00B4D8", 220),
        "subtitle": (26, True, "F8D477", 140),
        "section": (26, True, "0B7894", 160),
        "meta": (18, False, "64748B", 90),
        "text": (20, False, "111827", 110),
        "caption": (17, False, "64748B", 100),
    }
    size, bold, color, after = styles.get(kind, styles["text"])
    jc = f"<w:jc w:val=\"{align}\"/>" if align else ""
    border = ""
    if kind == "section":
        border = "<w:pBdr><w:bottom w:val=\"single\" w:sz=\"8\" w:space=\"5\" w:color=\"00B4D8\"/></w:pBdr>"
    return f"<w:p><w:pPr>{jc}<w:spacing w:after=\"{after}\"/>{border}</w:pPr>{_docx_run(text, size=size, bold=bold, color=color)}</w:p>"


def _docx_page_break():
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


def _docx_cell(text, shade=None, bold=False):
    shading = f'<w:shd w:fill="{shade}"/>' if shade else ""
    return (
        f"<w:tc><w:tcPr>{shading}<w:tcMar><w:top w:w=\"80\" w:type=\"dxa\"/>"
        f"<w:left w:w=\"80\" w:type=\"dxa\"/><w:bottom w:w=\"80\" w:type=\"dxa\"/>"
        f"<w:right w:w=\"80\" w:type=\"dxa\"/></w:tcMar></w:tcPr>"
        f"{_docx_paragraph2(str(text), 'text') if not bold else _docx_paragraph2(str(text), 'subtitle')}"
        f"</w:tc>"
    )


def _docx_table2(headers, rows):
    header_xml = "".join(_docx_cell(h, "0B3550", True) for h in headers)
    row_xml = [f"<w:tr>{header_xml}</w:tr>"]
    for idx, row in enumerate(rows):
        shade = "F1F5F9" if idx % 2 else "FFFFFF"
        row_xml.append("<w:tr>" + "".join(_docx_cell(cell, shade, False) for cell in row) + "</w:tr>")
    return (
        "<w:tbl><w:tblPr><w:tblW w:w=\"5000\" w:type=\"pct\"/>"
        "<w:tblBorders><w:top w:val=\"single\" w:sz=\"6\" w:color=\"94A3B8\"/>"
        "<w:left w:val=\"single\" w:sz=\"6\" w:color=\"94A3B8\"/>"
        "<w:bottom w:val=\"single\" w:sz=\"6\" w:color=\"94A3B8\"/>"
        "<w:right w:val=\"single\" w:sz=\"6\" w:color=\"94A3B8\"/>"
        "<w:insideH w:val=\"single\" w:sz=\"4\" w:color=\"CBD5E1\"/>"
        "<w:insideV w:val=\"single\" w:sz=\"4\" w:color=\"CBD5E1\"/></w:tblBorders></w:tblPr>"
        + "".join(row_xml) + "</w:tbl>"
    )


def _docx_visual_xml(rel_id, title, caption):
    cx, cy = 5486400, 3291840
    return (
        _docx_paragraph2(title, "subtitle") +
        f"""<w:p><w:pPr><w:jc w:val="center"/></w:pPr><w:r><w:drawing>
        <wp:inline distT="0" distB="0" distL="0" distR="0">
          <wp:extent cx="{cx}" cy="{cy}"/><wp:docPr id="1" name="{html.escape(title)}"/>
          <a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
            <pic:pic><pic:nvPicPr><pic:cNvPr id="0" name="{html.escape(title)}.png"/><pic:cNvPicPr/></pic:nvPicPr>
            <pic:blipFill><a:blip r:embed="{rel_id}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>
            <pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>
            </pic:pic>
          </a:graphicData></a:graphic>
        </wp:inline></w:drawing></w:r></w:p>""" +
        _docx_paragraph2(caption, "caption", "center")
    )


def _generate_docx_report(feed, thermo, col_type, shortcut, diameter, height,
                          reboiler, condenser, mechanical, energy, health=None) -> bytes:
    blocks, c = _build_professional_report_blocks(feed, thermo, col_type, shortcut, diameter, height,
                                                  reboiler, condenser, mechanical, energy, health)
    s = c["settings"]
    assets = _visual_assets(c)
    rel_lookup = {kind: f"rIdImage{i + 1}" for i, kind in enumerate(assets)}
    body = []
    for block in blocks:
        kind = block["kind"]
        if kind == "cover":
            body.extend([
                _docx_paragraph2("DISTILLATION COLUMN DESIGN REPORT", "title", "center"),
                _docx_paragraph2(s["project_title"], "subtitle", "center"),
                _docx_paragraph2(f"Prepared by {s['engineer_name']}", "subtitle", "center"),
                _docx_paragraph2(s["company_name"], "text", "center"),
                _docx_paragraph2(f"Report No. {s['project_no']} | Revision {s['revision']} | {s['report_date_text']}", "meta", "center"),
                _docx_page_break(),
            ])
        elif kind == "section":
            body.append(_docx_paragraph2(block["title"], "section"))
        elif kind == "text":
            body.append(_docx_paragraph2(block["text"], "text"))
        elif kind == "table":
            body.append(_docx_paragraph2(block["title"], "subtitle"))
            body.append(_docx_table2(block["headers"], block["rows"]))
            body.append(_docx_paragraph2("", "text"))
        elif kind == "visual":
            rel_id = rel_lookup.get(block["visual"])
            if rel_id:
                body.append(_docx_visual_xml(rel_id, block["title"], block.get("caption", "")))
            else:
                body.append(_docx_paragraph2(block["title"], "subtitle"))
                body.append(_docx_paragraph2(block.get("caption", ""), "caption"))

    document_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
            xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
            xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
            xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">
  <w:body>
    {''.join(body)}
    <w:sectPr>
      <w:pgSz w:w="11906" w:h="16838"/>
      <w:pgMar w:top="1134" w:right="900" w:bottom="900" w:left="900" w:header="708" w:footer="708" w:gutter="0"/>
    </w:sectPr>
  </w:body>
</w:document>"""
    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Default Extension="png" ContentType="image/png"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""
    package_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""
    image_rels = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">']
    for kind, rel_id in rel_lookup.items():
        image_rels.append(f'<Relationship Id="{rel_id}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/{kind}.png"/>')
    image_rels.append("</Relationships>")

    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as docx:
        docx.writestr("[Content_Types].xml", content_types)
        docx.writestr("_rels/.rels", package_rels)
        docx.writestr("word/document.xml", document_xml)
        docx.writestr("word/_rels/document.xml.rels", "".join(image_rels))
        for kind, data in assets.items():
            docx.writestr(f"word/media/{kind}.png", data)
    return output.getvalue()
