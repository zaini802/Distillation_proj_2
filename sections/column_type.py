"""sections/column_type.py - Column Type Selection"""
import streamlit as st


def _reason_html(reasons, fallback):
    if not reasons:
        return f'<p class="column-reason muted">{fallback}</p>'
    return "".join(f'<p class="column-reason">{reason}</p>' for reason in reasons)


def render():
    st.markdown("""
    <div class="section-header">
        <h1>🏗️ Column Type Selection</h1>
        <p>AI-assisted decision system for tray column vs packed column selection based on process conditions.</p>
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
    .column-tab-heading {
        color: #f8d477 !important;
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 2.05rem !important;
        font-weight: 900 !important;
        letter-spacing: 0;
        line-height: 1.12;
        margin: 0.45rem 0 1rem 0;
        text-shadow: 0 0 14px rgba(248, 212, 119, 0.24);
    }
    .column-input-label {
        color: #ff5b6e !important;
        font-weight: 900 !important;
        letter-spacing: 0.2px;
        margin: 0 0 0.42rem 0.05rem;
        text-shadow: 0 0 10px rgba(239, 68, 68, 0.22);
    }
    .column-helper-box,
    .column-final-box,
    .column-saved-box {
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
    .column-helper-title,
    .column-final-title,
    .column-saved-title {
        color: #f8d477;
        font-weight: 900;
        margin-bottom: 0.35rem;
    }
    .column-card {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.98), rgba(8, 14, 24, 0.98));
        border: 1px solid rgba(0, 180, 216, 0.42);
        border-left: 4px solid var(--column-accent);
        border-radius: 8px;
        padding: 1.05rem 1.1rem;
        min-height: 345px;
        color: #f8fbff;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.04), 0 10px 24px rgba(0,0,0,0.16);
    }
    .column-card.is-muted {
        border-color: rgba(148, 163, 184, 0.28);
        border-left-color: #64748b;
    }
    .column-card-title {
        color: var(--column-accent);
        font-size: 1.45rem;
        font-weight: 900;
        letter-spacing: 0;
        margin-bottom: 0.3rem;
    }
    .column-card.is-muted .column-card-title {
        color: #cbd5e1;
    }
    .column-score {
        color: var(--column-accent);
        font-family: 'Share Tech Mono', monospace;
        font-size: 2.65rem;
        font-weight: 900;
        line-height: 1;
        margin-bottom: 0.8rem;
        text-shadow: 0 0 14px rgba(0,180,216,0.18);
    }
    .column-card.is-muted .column-score {
        color: #94a3b8;
    }
    .column-card-rule {
        border: 0;
        border-top: 2px dotted rgba(248, 212, 119, 0.45);
        margin: 0.85rem 0;
    }
    .column-reason {
        color: #e7f0ff !important;
        font-size: 0.96rem;
        font-weight: 700;
        line-height: 1.45;
        margin: 0.38rem 0;
    }
    .column-reason.muted {
        color: #cbd5e1 !important;
    }
    .column-card-foot {
        color: #dbeafe;
        font-size: 0.9rem;
        font-weight: 700;
        line-height: 1.45;
        margin: 0.35rem 0;
    }
    .column-card-foot strong {
        color: #ffffff;
    }
    .column-final-box {
        border-color: rgba(34, 197, 94, 0.45);
        border-left-color: #22c55e;
        font-size: 1.02rem;
    }
    .column-final-title {
        color: #22c55e;
    }
    .column-saved-box {
        border-left-color: #f8d477;
    }
    div[role="radiogroup"] label p {
        color: #f8fbff !important;
        font-weight: 900 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    feed = st.session_state.get("feed", {})

    # Decision Criteria Panel
    st.markdown('<h3 class="column-tab-heading">&#9881;&#65039; Selection Criteria</h3>', unsafe_allow_html=True)
    st.markdown("""
    <div class="column-helper-box">
        <div class="column-helper-title">Decision inputs</div>
        Column type is selected from pressure, flow rate, fouling, corrosion, vacuum duty,
        and service behaviour. Tray and packed options are scored separately so the
        recommendation is easy to understand.
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="column-input-label">Feed Flow Rate F [kmol/h]</div>', unsafe_allow_html=True)
        F = st.number_input(
            "Feed Flow Rate F [kmol/h]",
            value=float(feed.get("F", 100.0)),
            min_value=1.0,
            step=1.0,
            label_visibility="collapsed",
        )
        st.markdown('<div class="column-input-label">Column Pressure [bar]</div>', unsafe_allow_html=True)
        P_col = st.number_input(
            "Column Pressure [bar]",
            value=float(feed.get("P_col_bar", 1.013)),
            min_value=0.01,
            step=0.01,
            format="%.4f",
            label_visibility="collapsed",
        )
        st.markdown('<div class="column-input-label">Fouling Tendency</div>', unsafe_allow_html=True)
        fouling = st.selectbox("Fouling Tendency", ["Low", "Medium", "High"], label_visibility="collapsed")

    with c2:
        st.markdown('<div class="column-input-label">Corrosive Service</div>', unsafe_allow_html=True)
        corrosive = st.selectbox("Corrosive Service", ["No", "Yes"], label_visibility="collapsed")
        st.markdown('<div class="column-input-label">Vacuum Service (&lt;0.1 bar)?</div>', unsafe_allow_html=True)
        vacuum_svc = st.selectbox("Vacuum Service (<0.1 bar)?", ["No", "Yes"], label_visibility="collapsed")
        st.markdown('<div class="column-input-label">System Type</div>', unsafe_allow_html=True)
        system_type = st.selectbox(
            "System Type",
            ["Clean", "Foaming", "Viscous", "Solid-containing"],
            label_visibility="collapsed",
        )

    st.markdown("<div class='eng-divider'></div>", unsafe_allow_html=True)

    # AI Logic Decision Engine
    st.markdown('<h3 class="column-tab-heading">&#129302; Engineering Decision Analysis</h3>', unsafe_allow_html=True)

    score_tray = 0
    score_packed = 0
    reasons_tray = []
    reasons_packed = []

    # Pressure
    if P_col < 0.1:
        score_packed += 3
        reasons_packed.append("✅ Low pressure drop required — packed column preferred for vacuum service")
    elif P_col > 5.0:
        score_tray += 2
        reasons_tray.append("✅ High pressure service — trays are more mechanically robust")
    else:
        reasons_tray.append("🔵 Atmospheric/moderate pressure — both types are suitable")

    # Flow rate
    if F > 500:
        score_tray += 3
        reasons_tray.append(f"✅ High throughput F = {F} kmol/h — tray column preferred for large diameter")
    elif F < 50:
        score_packed += 2
        reasons_packed.append(f"✅ Low flow rate F = {F} kmol/h — packed column is more cost-effective")

    # Fouling
    if fouling == "High":
        score_tray += 3
        reasons_tray.append("✅ High fouling tendency — trays are easier to inspect, clean, and maintain")
    elif fouling == "Low":
        score_packed += 2
        reasons_packed.append("✅ Low fouling — structured packing can achieve higher efficiency")

    # Corrosion
    if corrosive == "Yes":
        score_packed += 2
        reasons_packed.append("✅ Corrosive service — ceramic/plastic packing avoids metal degradation")

    # Vacuum
    if vacuum_svc == "Yes":
        score_packed += 3
        reasons_packed.append("✅ Vacuum service — packed column gives much lower pressure drop per stage")

    # Foaming / solids
    if system_type == "Foaming":
        score_tray += 2
        reasons_tray.append("✅ Foaming system — tray columns are easier to control with weir adjustments")
    elif system_type == "Solid-containing":
        score_tray += 3
        reasons_tray.append("✅ Solid-containing system — packed beds may plug; trays with large openings preferred")

    # Recommendation cards
    col1, col2 = st.columns(2)
    with col1:
        tray_color = "#22c55e" if score_tray >= score_packed else "#64748b"
        tray_card_class = "" if score_tray >= score_packed else "is-muted"
        st.markdown(f"""
        <div class="column-card {tray_card_class}" style="--column-accent:{tray_color};">
            <div class="column-card-title">▦ Tray Column</div>
            <div class="column-score">{score_tray} pts</div>
            <hr class="column-card-rule">
            {_reason_html(reasons_tray, "No strong tray-column advantage identified")}
            <hr class="column-card-rule">
            <p class="column-card-foot"><strong>Types:</strong> Sieve, valve, bubble-cap</p>
            <p class="column-card-foot"><strong>Best for:</strong> Large diameter, high liquid flow, fouling service, easy maintenance</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        pack_color = "#22c55e" if score_packed > score_tray else "#64748b"
        pack_card_class = "" if score_packed > score_tray else "is-muted"
        st.markdown(f"""
        <div class="column-card {pack_card_class}" style="--column-accent:{pack_color};">
            <div class="column-card-title">◎ Packed Column</div>
            <div class="column-score">{score_packed} pts</div>
            <hr class="column-card-rule">
            {_reason_html(reasons_packed, "No strong packed-column advantage identified")}
            <hr class="column-card-rule">
            <p class="column-card-foot"><strong>Types:</strong> Random packing, structured packing</p>
            <p class="column-card-foot"><strong>Best for:</strong> Vacuum, low ΔP, corrosive duty, small diameter, high efficiency</p>
        </div>
        """, unsafe_allow_html=True)

    # Final recommendation
    st.markdown("<div class='eng-divider'></div>", unsafe_allow_html=True)
    if score_tray >= score_packed:
        recommendation = "tray"
        rec_text = f"Tray Column recommended (Score: {score_tray} vs {score_packed})"
    else:
        recommendation = "packed"
        rec_text = f"Packed Column recommended (Score: {score_packed} vs {score_tray})"

    st.markdown(f"""
    <div class="column-final-box">
        <div class="column-final-title">Final recommendation</div>
        ✅ <strong>{rec_text}</strong>
    </div>
    """, unsafe_allow_html=True)

    # Manual override
    st.markdown('<div class="column-input-label">Final Column Type Selection (override if needed)</div>', unsafe_allow_html=True)
    col_type_manual = st.radio(
        "Final Column Type Selection (override if needed):",
        ["tray", "packed"],
        index=0 if recommendation == "tray" else 1,
        horizontal=True,
        label_visibility="collapsed",
    )

    if st.button("💾 Save Column Type Selection", type="primary"):
        st.session_state.column_type = col_type_manual
        st.success(
            f"✅ Column type saved: **{col_type_manual.upper()} COLUMN**. "
            f"Proceed to **{'Tray Design' if col_type_manual == 'tray' else 'Packing Design'}**."
        )

    if st.session_state.get("column_type"):
        st.markdown(f"""
        <div class="column-saved-box">
            <div class="column-saved-title">Currently saved</div>
            📌 <strong>{st.session_state.column_type.upper()} COLUMN</strong>
        </div>
        """, unsafe_allow_html=True)
