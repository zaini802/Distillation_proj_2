"""sections/height_packed.py — Column Height for Packed Columns (HETP method)"""
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd

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
        <h1>📏 Column Height — Packed Column</h1>
        <p>HETP method — packed bed height, redistributor spacing, sump, skirt, and total column height.</p>
    </div>
    """, unsafe_allow_html=True)

    col_type = st.session_state.get("column_type", None)
    if col_type == "tray":
        st.markdown("""
        <div class="warn-panel">
        ⚠️ <strong>Tray Column selected.</strong>
        This section uses HETP method for packed columns.
        For your tray column → use <b>📏 Column Height</b> (tray spacing method).
        <i>You can still view this section for reference or comparison.</i>
        </div>
        """, unsafe_allow_html=True)
    elif col_type == "packed":
        st.markdown("""
        <div class="success-panel">
        ✅ <strong>Packed Column selected</strong> — HETP method is correct for your design.
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

    if not shortcut:
        st.warning("⚠️ Complete Shortcut Design first.")
        return

    N_theoretical = shortcut.get("N_actual_int", 15)
    D_col         = diameter.get("D_column_std_m", 1.0)
    packing_saved = diameter.get("packing_type", "Mellapak 250Y")

    tab1, tab2 = st.tabs(["📏 Height Calculation", "🏗️ Column Sketch"])

    with tab1:
        st.markdown(f"""
        <div class="formula-box">
            <div class="formula-title">HETP Method — Packed Column Height</div>
            <b>Packed bed height</b> = N_theoretical × HETP<br>
            <b>Total column height</b> = H_packed + H_redistributors + H_top + H_sump + H_skirt<br><br>
            N_theoretical from Shortcut Design (Gilliland) = <b>{N_theoretical} stages</b>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            packing_opts = list(PACKINGS.keys())
            default_idx  = packing_opts.index(packing_saved) if packing_saved in packing_opts else 5
            packing_sel  = st.selectbox("Packing Type", packing_opts, index=default_idx)
            pk           = PACKINGS[packing_sel]
            HETP_base    = pk["HETP_base"]

            st.markdown(f"""
            <div class="result-box">
                <div class="label">Base HETP</div>
                <span class="value">{HETP_base}</span>
                <span class="unit"> m/stage</span>
            </div>""", unsafe_allow_html=True)

        with c2:
            hetp_factor = st.slider(
                "HETP correction factor",
                min_value=0.8, max_value=1.5, value=1.0, step=0.05,
                help="1.0 = nominal. Increase for high viscosity, foaming, or large diameter (>1.5m)")
            HETP = round(HETP_base * hetp_factor, 3)
            st.markdown(f"""
            <div class="result-box">
                <div class="label">Effective HETP</div>
                <span class="value">{HETP}</span>
                <span class="unit"> m/stage</span>
            </div>""", unsafe_allow_html=True)

        with c3:
            n_beds = st.selectbox(
                "Number of packing beds",
                [1, 2, 3, 4],
                index=1,
                help="Redistributors needed every 5–8 m or every 10D. Split into beds.")
            st.markdown(f"""
            <div class="result-box">
                <div class="label">Stages per bed</div>
                <span class="value">{round(N_theoretical/n_beds, 1)}</span>
                <span class="unit"> stages</span>
            </div>""", unsafe_allow_html=True)

        st.markdown("### Additional Heights")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            h_redist = st.number_input(
                "Redistributor height [m]", value=0.30,
                min_value=0.10, max_value=1.0, step=0.05,
                help="Each redistributor section ≈ 0.3–0.5 m")
        with c2:
            h_top  = st.number_input("Top disengagement [m]", value=1.5, min_value=0.3, max_value=4.0, step=0.1)
        with c3:
            h_sump = st.number_input("Bottom sump [m]",        value=2.0, min_value=0.5, max_value=5.0, step=0.1)
        with c4:
            h_skirt = st.number_input("Support skirt [m]",     value=3.0, min_value=1.0, max_value=8.0, step=0.5)

        # ── Calculations ───────────────────────────────────────
        H_packed_total  = N_theoretical * HETP
        H_per_bed       = H_packed_total / n_beds
        H_redistributors= (n_beds - 1) * h_redist   # redistributors between beds only
        H_active        = H_packed_total + H_redistributors
        H_column        = H_active + h_top + h_sump
        H_total         = H_column + h_skirt
        H_D_ratio       = round(H_column / D_col, 2) if D_col > 0 else 0

        # ── Formula box solved ─────────────────────────────────
        st.markdown(f"""
        <div class="formula-box" style="border-left:4px solid #f59e0b;">
            <div class="formula-title">✏️ Step-by-Step Height Calculation</div>
            <b>Step 1 — Packed bed height:</b><br>
            &nbsp;&nbsp; H_packed = N_theoretical × HETP = {N_theoretical} × {HETP} = <b>{H_packed_total:.2f} m</b><br><br>
            <b>Step 2 — Height per bed ({n_beds} beds):</b><br>
            &nbsp;&nbsp; H_per_bed = {H_packed_total:.2f} / {n_beds} = <b>{H_per_bed:.2f} m/bed</b><br><br>
            <b>Step 3 — Redistributors ({n_beds-1} between beds):</b><br>
            &nbsp;&nbsp; H_redist = ({n_beds}−1) × {h_redist} = <b>{H_redistributors:.2f} m</b><br><br>
            <b>Step 4 — Active section:</b><br>
            &nbsp;&nbsp; H_active = H_packed + H_redistributors = {H_packed_total:.2f} + {H_redistributors:.2f} = <b>{H_active:.2f} m</b><br><br>
            <b>Step 5 — Total column (excl. skirt):</b><br>
            &nbsp;&nbsp; H_column = H_active + H_top + H_sump = {H_active:.2f} + {h_top} + {h_sump} = <b>{H_column:.2f} m</b><br><br>
            <b>Step 6 — Total with skirt:</b><br>
            &nbsp;&nbsp; H_total = {H_column:.2f} + {h_skirt} = <b>{H_total:.2f} m</b><br><br>
            <b>H/D ratio</b> = {H_column:.2f} / {D_col} = <b>{H_D_ratio}</b>
            {"✅ Within range (5–30)" if 5 <= H_D_ratio <= 30 else "⚠️ Outside typical range 5–30"}
        </div>
        """, unsafe_allow_html=True)

        # ── Metrics ────────────────────────────────────────────
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Packed Bed Height",    f"{H_packed_total:.2f} m")
        c2.metric("Active Section",       f"{H_active:.2f} m")
        c3.metric("Total Height (col)",   f"{H_column:.2f} m")
        c4.metric("Total + Skirt",        f"{H_total:.2f} m")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("HETP Used",            f"{HETP} m/stage")
        c2.metric("Height per Bed",       f"{H_per_bed:.2f} m")
        c3.metric("H/D Ratio",            f"{H_D_ratio}")
        c4.metric("Redistributors",       f"{n_beds-1} units")

        if H_D_ratio < 5:
            st.markdown('<div class="warn-panel">⚠️ H/D < 5 — column too squat. Consider more stages or smaller diameter.</div>', unsafe_allow_html=True)
        elif H_D_ratio > 30:
            st.markdown('<div class="warn-panel">⚠️ H/D > 30 — very tall column. Check wind loading, vibration, and consider splitting.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="success-panel">✅ H/D = {H_D_ratio} within acceptable range (5–30).</div>', unsafe_allow_html=True)

        # Bed check (each bed < 8m industrial rule)
        if H_per_bed > 8:
            st.markdown(f'<div class="warn-panel">⚠️ Each bed height = {H_per_bed:.1f} m > 8 m. Add more redistributors (increase number of beds).</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="success-panel">✅ Each bed = {H_per_bed:.2f} m ≤ 8 m — redistributor spacing OK.</div>', unsafe_allow_html=True)

        # Summary table
        st.markdown("### Height Breakdown")
        sections_dict = {}
        for i in range(n_beds):
            sections_dict[f"Packed Bed {i+1}"] = round(H_per_bed, 2)
            if i < n_beds - 1:
                sections_dict[f"Redistributor {i+1}"] = h_redist
        sections_dict["Top Disengagement"] = h_top
        sections_dict["Bottom Sump"]       = h_sump
        sections_dict["Support Skirt"]     = h_skirt

        df_h = pd.DataFrame({
            "Section":      list(sections_dict.keys()),
            "Height [m]":   list(sections_dict.values()),
            "% of Total":   [round(v / H_total * 100, 1) for v in sections_dict.values()],
        })
        st.dataframe(df_h, use_container_width=True, hide_index=True)

    # ── TAB 2: Column Sketch ───────────────────────────────────
    with tab2:
        st.markdown("### 🏗️ Packed Column 2D Sketch")
        D = D_col
        fig = go.Figure()

        # Shell outline
        fig.add_shape(type="rect",
                      x0=-D/2, y0=h_skirt,
                      x1= D/2, y1=h_skirt + H_column,
                      line=dict(color="#22c55e", width=3.5),
                      fillcolor="rgba(34,197,94,0.08)")

        # Skirt
        fig.add_shape(type="rect",
                      x0=-D/4, y0=0, x1=D/4, y1=h_skirt,
                      line=dict(color="#94a3b8", width=2.5),
                      fillcolor="rgba(148,163,184,0.16)")

        # Draw each packed bed
        colors = ["rgba(0,180,216,0.15)", "rgba(34,197,94,0.12)",
                  "rgba(245,158,11,0.12)", "rgba(168,85,247,0.12)"]
        y_cursor = h_skirt + h_sump
        for i in range(n_beds):
            y0_bed = y_cursor
            y1_bed = y_cursor + H_per_bed
            fig.add_shape(type="rect",
                          x0=-D/2+0.03, y0=y0_bed, x1=D/2-0.03, y1=y1_bed,
                          line=dict(color="#00b4d8", width=2.3, dash="dot"),
                          fillcolor=colors[i % len(colors)])
            # Packing fill pattern (horizontal lines)
            for yy in np.arange(y0_bed+0.1, y1_bed, 0.2):
                fig.add_shape(type="line",
                              x0=-D/2+0.05, y0=yy, x1=D/2-0.05, y1=yy,
                              line=dict(color="#38bdf8", width=1.1, dash="dot"))
            mid_y = (y0_bed + y1_bed) / 2
            fig.add_annotation(x=D/2 + 0.15, y=mid_y,
                                text=f"Bed {i+1} ({H_per_bed:.1f}m)",
                                showarrow=True, arrowhead=2, ax=30, ay=0,
                                font=dict(color="#00b4d8", size=10))
            y_cursor = y1_bed
            # Redistributor between beds
            if i < n_beds - 1:
                fig.add_shape(type="rect",
                              x0=-D/2+0.03, y0=y_cursor,
                              x1=D/2-0.03, y1=y_cursor+h_redist,
                              line=dict(color="#f59e0b", width=2.8),
                              fillcolor="rgba(245,158,11,0.2)")
                fig.add_annotation(x=D/2+0.15, y=y_cursor+h_redist/2,
                                    text="Redistributor",
                                    showarrow=True, arrowhead=2, ax=30, ay=0,
                                    font=dict(color="#f59e0b", size=9))
                y_cursor += h_redist

        # Mist eliminator at top
        top_of_packing = h_skirt + h_sump + H_active
        fig.add_shape(type="rect",
                      x0=-D/2+0.03, y0=top_of_packing,
                      x1=D/2-0.03, y1=top_of_packing+0.2,
                      line=dict(color="#a855f7", width=3),
                      fillcolor="rgba(168,85,247,0.3)")
        fig.add_annotation(x=D/2+0.15, y=top_of_packing+0.1,
                            text="Mist eliminator",
                            showarrow=True, arrowhead=2, ax=30, ay=0,
                            font=dict(color="#a855f7", size=9))

        # Nozzle annotations
        feed_y = h_skirt + h_sump + H_active * 0.45
        top_y  = h_skirt + H_column
        bot_y  = h_skirt

        fig.add_annotation(x= D/2+0.1, y=feed_y,
                            text="← Feed", showarrow=True, arrowhead=2, ax=40, ay=0,
                            font=dict(color="#f59e0b", size=11))
        fig.add_annotation(x= D/2+0.1, y=top_y,
                            text="Distillate →", showarrow=True, arrowhead=2, ax=40, ay=0,
                            font=dict(color="#22c55e", size=11))
        fig.add_annotation(x= D/2+0.1, y=bot_y+0.3,
                            text="Bottoms →", showarrow=True, arrowhead=2, ax=40, ay=0,
                            font=dict(color="#ef4444", size=11))
        fig.add_annotation(x=0, y=top_y+0.4, text="❄ Condenser",
                            showarrow=False, font=dict(color="#00b4d8", size=11))
        fig.add_annotation(x=0, y=bot_y-0.5, text="♨ Reboiler",
                            showarrow=False, font=dict(color="#ef4444", size=11))

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0a0e14", plot_bgcolor="#111827",
            font=dict(family="Barlow", color="#e2e8f0"),
            xaxis=dict(title="Width [m]",
                       range=[-(D+0.6), D+1.8], gridcolor="#1e3a5f"),
            yaxis=dict(title="Height [m]", gridcolor="#1e3a5f"),
            height=620, margin=dict(t=30),
            title=dict(
                text=f"Packed Column — D={D} m | H={H_column:.1f} m | "
                     f"{n_beds} bed(s) | Packing: {packing_sel}",
                font=dict(color="#f8d477", size=19))
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Save ──────────────────────────────────────────────────
    st.markdown("<div class='eng-divider'></div>", unsafe_allow_html=True)
    if st.button("💾 Save Packed Height Results", type="primary"):
        st.session_state.height = {
            "column_mode":         "packed",
            "packing_type":        packing_sel,
            "HETP_m":              HETP,
            "N_theoretical":       N_theoretical,
            "H_packed_total_m":    round(H_packed_total, 3),
            "H_per_bed_m":         round(H_per_bed, 3),
            "n_beds":              n_beds,
            "H_redistributors_m":  round(H_redistributors, 3),
            "H_active_m":          round(H_active, 3),
            "active_height_m":     round(H_active, 3),
            "top_disengagement_m": h_top,
            "bottom_sump_m":       h_sump,
            "skirt_height_m":      h_skirt,
            "total_height_m":      round(H_column, 3),
            "total_with_skirt_m":  round(H_total, 3),
            "H_D_ratio":           H_D_ratio,
        }
        st.success(
            f"✅ Packed height saved: H = {H_column:.2f} m "
            f"({n_beds} bed(s) × {H_per_bed:.2f} m, HETP={HETP} m). "
            f"Proceed to ♨️ Reboiler Design."
        )
