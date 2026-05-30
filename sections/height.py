"""sections/height.py — Column Height Design"""
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd
from calculations.distillation_calc import column_height_tray


def render():
    st.markdown("""
    <div class="section-header">
        <h1>📏 Column Height Design</h1>
        <p>Total column height from tray spacing, tray efficiency, top disengagement, sump height, and skirt.</p>
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
    </style>
    """, unsafe_allow_html=True)

    shortcut = st.session_state.get("shortcut", {})
    diameter = st.session_state.get("diameter", {})

    col_type = st.session_state.get("column_type", None)
    if col_type == "packed":
        st.markdown("""
        <div class="warn-panel">
        ⚠️ <strong>Packed Column selected.</strong>
        This section uses <b>tray spacing method</b> for tray columns.
        For your packed column → use <b>📏 Column Height (Packed)</b> (HETP method).
        <i>You can still view this section for reference or comparison.</i>
        </div>
        """, unsafe_allow_html=True)
    elif col_type == "tray":
        st.markdown("""
        <div class="success-panel">
        ✅ <strong>Tray Column selected</strong> — tray spacing method is correct for your design.
        </div>
        """, unsafe_allow_html=True)

    if not shortcut:
        st.warning("⚠️ Complete **Shortcut Design** first.")
        return

    N_theoretical = int(shortcut.get("N_actual_int", 20))
    NF            = int(shortcut.get("NF", N_theoretical // 2))
    D_col         = diameter.get("D_column_std_m", 1.2)

    tab1, tab2 = st.tabs(["📏 Height Calculation", "🏗️ Column Sketch"])

    with tab1:
        st.markdown("""
        <div class="formula-box">
          <div class="formula-title">Column Height</div>
          N<sub>actual trays</sub> = N<sub>theoretical</sub> / E<sub>o</sub><br>
          H<sub>active</sub> = N<sub>actual</sub> × h<sub>tray spacing</sub><br>
          H<sub>total</sub> = H<sub>active</sub> + H<sub>top</sub> + H<sub>sump</sub>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"**Theoretical stages from Shortcut/McCabe-Thiele: N = {N_theoretical}**")

        c1, c2, c3 = st.columns(3)
        with c1:
            tray_spacing = st.number_input("Tray Spacing [m]",
                value=float(diameter.get("tray_spacing", 0.60)),
                min_value=0.15, max_value=1.20, step=0.05, format="%.2f")
            tray_eff = st.slider("Overall Tray Efficiency E_o", 0.40, 0.90, 0.70, 0.01,
                                  help="O'Connell correlation: typically 0.6–0.75 for sieve trays")
        with c2:
            top_dis = st.number_input("Top Disengagement Height [m]", value=1.5, min_value=0.5, max_value=4.0, step=0.1)
            sump_h  = st.number_input("Bottom Sump Height [m]",       value=2.0, min_value=0.5, max_value=5.0, step=0.1)
        with c3:
            skirt_h = st.number_input("Skirt Height [m]",             value=3.0, min_value=1.0, max_value=8.0, step=0.5)
            st.markdown(f"""
            <div class="result-box">
                <div class="label">N actual trays</div>
                <span class="value">{int(np.ceil(N_theoretical/tray_eff))}</span>
                <span class="unit"> trays</span>
            </div>
            """, unsafe_allow_html=True)

        result = column_height_tray(N_theoretical, tray_spacing, tray_eff, top_dis, sump_h, skirt_h)

        # H/D ratio
        H_D = round(result["total_height_m"] / D_col, 2) if D_col > 0 else 0

        st.markdown(f"""
        <div class="formula-box" style="border-left-color:#22c55e !important;">
          <div class="formula-title">Step-by-step height calculation</div>
          <b>1. Actual trays:</b>
          N<sub>actual</sub> = N<sub>theoretical</sub> / E<sub>o</sub>
          = {N_theoretical} / {tray_eff:.4f}
          = <b>{result['N_actual_trays']} trays</b><br>
          <b>2. Active tray section:</b>
          H<sub>active</sub> = N<sub>actual</sub> Ã— tray spacing
          = {result['N_actual_trays']} Ã— {tray_spacing:.2f}
          = <b>{result['active_section_m']:.2f} m</b><br>
          <b>3. Column shell height:</b>
          H<sub>shell</sub> = H<sub>active</sub> + H<sub>top</sub> + H<sub>sump</sub>
          = {result['active_section_m']:.2f} + {top_dis:.2f} + {sump_h:.2f}
          = <b>{result['total_height_m']:.2f} m</b><br>
          <b>4. Installed height:</b>
          H<sub>installed</sub> = H<sub>shell</sub> + skirt
          = {result['total_height_m']:.2f} + {skirt_h:.2f}
          = <b>{result['total_with_skirt_m']:.2f} m</b><br>
          <b>5. Slenderness:</b>
          H/D = {result['total_height_m']:.2f} / {D_col:.2f} = <b>{H_D:.2f}</b>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### Height Results")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("N theoretical", N_theoretical)
        c2.metric("N actual trays", result["N_actual_trays"])
        c3.metric("Active Section Height", f"{result['active_section_m']:.2f} m")
        c4.metric("Total Height (excl. skirt)", f"{result['total_height_m']:.2f} m")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Height (incl. skirt)", f"{result['total_with_skirt_m']:.2f} m")
        c2.metric("H/D Ratio", f"{H_D:.2f}", help="Should be 5–30 for typical columns")
        c3.metric("Tray Efficiency E_o", f"{tray_eff*100:.0f}%")
        c4.metric("Tray Spacing", f"{tray_spacing} m")

        if H_D < 5:
            st.markdown('<div class="warn-panel">⚠️ H/D ratio < 5 — column may be too squat. Consider increasing stages or reducing diameter.</div>', unsafe_allow_html=True)
        elif H_D > 30:
            st.markdown('<div class="warn-panel">⚠️ H/D ratio > 30 — column is very tall relative to diameter. Check for wind loading and vibration.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="success-panel">✅ H/D = {H_D:.2f} is within acceptable industrial range (5–30).</div>', unsafe_allow_html=True)

        # Height breakdown
        st.markdown("### Height Breakdown")
        sections = {
            "Top Disengagement": top_dis,
            "Active Tray Section": result["active_section_m"],
            "Bottom Sump": sump_h,
            "Skirt": skirt_h,
        }
        df_h = pd.DataFrame({
            "Section": list(sections.keys()),
            "Height [m]": list(sections.values()),
            "% of Total": [round(v / result["total_with_skirt_m"] * 100, 1) for v in sections.values()]
        })
        st.dataframe(df_h, use_container_width=True, hide_index=True)

    with tab2:
        st.markdown("### 🏗️ 2D Column Sketch")
        H_total = result["total_with_skirt_m"]
        D = D_col

        fig = go.Figure()
        # Shell
        fig.add_shape(type="rect", x0=-D/2, y0=skirt_h, x1=D/2, y1=skirt_h + result["total_height_m"],
                       line=dict(color="#00b4d8", width=3.5), fillcolor="rgba(0,180,216,0.08)")
        # Skirt
        fig.add_shape(type="rect", x0=-D/4, y0=0, x1=D/4, y1=skirt_h,
                       line=dict(color="#94a3b8", width=2.5), fillcolor="rgba(148,163,184,0.16)")

        # Trays
        N_trays = result["N_actual_trays"]
        active_start = skirt_h + sump_h
        for i in range(N_trays):
            y_tray = active_start + i * tray_spacing
            color = "#f59e0b" if (i + 1) == NF else "#38bdf8"
            width = 3 if (i + 1) == NF else 1.4
            fig.add_shape(type="line", x0=-D/2 + 0.02, y0=y_tray, x1=D/2 - 0.02, y1=y_tray,
                           line=dict(color=color, width=width))

        # Feed, distillate, bottoms annotations
        feed_y   = active_start + (NF - 1) * tray_spacing
        top_y    = skirt_h + result["total_height_m"]
        bot_y    = skirt_h

        fig.add_annotation(x=D/2 + 0.1, y=feed_y, text="← Feed (zF)", showarrow=True,
                            arrowhead=2, ax=40, ay=0, font=dict(color="#f59e0b", size=11))
        fig.add_annotation(x=D/2 + 0.1, y=top_y, text="Distillate →", showarrow=True,
                            arrowhead=2, ax=40, ay=0, font=dict(color="#22c55e", size=11))
        fig.add_annotation(x=D/2 + 0.1, y=bot_y + 0.2, text="Bottoms →", showarrow=True,
                            arrowhead=2, ax=40, ay=0, font=dict(color="#ef4444", size=11))
        # Condenser at top
        fig.add_annotation(x=0, y=top_y + 0.3, text="❄ Condenser", showarrow=False,
                            font=dict(color="#00b4d8", size=11))
        # Reboiler at bottom
        fig.add_annotation(x=0, y=bot_y - 0.4, text="♨ Reboiler", showarrow=False,
                            font=dict(color="#ef4444", size=11))

        fig.update_layout(
            template="plotly_dark", paper_bgcolor="#0a0e14", plot_bgcolor="#111827",
            font=dict(family="Barlow", color="#e2e8f0"),
            xaxis=dict(title="Width [m]", range=[-(D + 0.5), D + 1.5], gridcolor="#1e3a5f"),
            yaxis=dict(title="Height [m]", gridcolor="#1e3a5f"),
            height=600, margin=dict(t=30),
            title=dict(text=f"Distillation Column — D={D} m | H={result['total_height_m']:.1f} m | {N_trays} trays",
                        font=dict(color="#f8d477", size=20))
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Save ──────────────────────────────────────────────────
    st.markdown("<div class='eng-divider'></div>", unsafe_allow_html=True)
    if st.button("💾 Save Height Results", type="primary"):
        st.session_state.height = {
            "N_theoretical": N_theoretical,
            "N_actual_trays": result["N_actual_trays"],
            "tray_efficiency": tray_eff,
            "tray_spacing_m": tray_spacing,
            "active_section_m": result["active_section_m"],
            "active_height_m": result["active_section_m"],
            "top_disengagement_m": top_dis,
            "bottom_sump_m": sump_h,
            "skirt_height_m": skirt_h,
            "total_height_m": result["total_height_m"],
            "total_with_skirt_m": result["total_with_skirt_m"],
            "H_D_ratio": H_D,
        }
        st.success(f"✅ Height saved: H = {result['total_height_m']:.2f} m (+ {skirt_h} m skirt). Proceed to **Reboiler Design**.")
