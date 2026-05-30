"""sections/home.py — Advanced Home Dashboard (pump-project level redesign)"""
import streamlit as st


def render():
    s         = st.session_state
    feed      = s.get("feed", {})
    thermo    = s.get("thermo", {})
    col_type  = s.get("column_type", None)
    shortcut  = s.get("shortcut", {})
    diameter  = s.get("diameter", {})
    height    = s.get("height", {})
    reboiler  = s.get("reboiler", {})
    condenser = s.get("condenser", {})
    mech      = s.get("mechanical", {})
    td        = s.get("tray_design", {})
    mc        = s.get("mccabe", {})
    pd_       = s.get("packing_design", {})
    pdrop     = s.get("pressure_drop", {})
    energy    = s.get("energy", {})

    checks    = [feed, thermo, col_type, shortcut, diameter, height, reboiler, condenser]
    done_count = sum(1 for c in checks if c)
    pct       = int(done_count / len(checks) * 100)
    bar_w     = pct
    bar_color = "#22c55e" if pct >= 75 else ("#f59e0b" if pct >= 40 else "#ef4444")
    col_label = col_type.upper() if col_type else "NOT SELECTED"

    # ── DEVELOPER CARD + MAIN TITLE ───────────────────────────────────
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Rajdhani:wght@500;600;700&family=Share+Tech+Mono&display=swap');

    .dev-card {
        background: linear-gradient(135deg, #0d1224 0%, #0a1628 50%, #0d2137 100%);
        border: 1px solid #1a4a7a;
        border-radius: 16px;
        padding: 28px 36px 22px 36px;
        margin-bottom: 0px;
        position: relative;
        overflow: hidden;
        text-align: center;
    }
    .dev-card::before {
        content: '';
        position: absolute; top: 0; left: 0; right: 0; bottom: 0;
        background: repeating-linear-gradient(
            90deg, transparent, transparent 80px,
            rgba(0,180,216,0.025) 80px, rgba(0,180,216,0.025) 81px
        );
    }
    .dev-card::after {
        content: '';
        position: absolute; top: -40%; right: -8%;
        width: 350px; height: 350px;
        background: radial-gradient(circle, rgba(0,180,216,0.07) 0%, transparent 70%);
        border-radius: 50%;
    }
    .dev-label {
        font-family: 'Share Tech Mono', monospace;
        font-size: 11px; letter-spacing: 4px;
        color: #00b4d8; opacity: 0.8; margin-bottom: 8px;
        position: relative; z-index: 2;
    }
    .dev-name {
        font-family: 'Orbitron', sans-serif;
        font-size: 2.4em; font-weight: 900;
        color: #fff;
        text-shadow: 0 0 30px rgba(0,180,216,0.45);
        letter-spacing: 2px; margin-bottom: 6px;
        position: relative; z-index: 2;
    }
    .dev-field {
        font-family: 'Rajdhani', sans-serif;
        font-size: 1.1em; font-weight: 600;
        color: #ffa500; letter-spacing: 1px;
        margin-bottom: 3px; position: relative; z-index: 2;
    }
    .dev-uni {
        font-size: 0.95em; color: #8ab4d4;
        margin-bottom: 3px; position: relative; z-index: 2;
    }
    .dev-year {
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.85em; color: #4ade80;
        letter-spacing: 3px; position: relative; z-index: 2;
    }

    .main-title-wrap {
        background: linear-gradient(135deg, #070b12 0%, #0a0e18 100%);
        border: 1px solid #1a3a5f;
        border-top: none;
        border-radius: 0 0 16px 16px;
        padding: 22px 36px 20px 36px;
        text-align: center;
        margin-bottom: 20px;
    }
    .main-icon { font-size: 2em; margin-bottom: 6px; }
    .main-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.65em; font-weight: 700;
        background: linear-gradient(90deg, #00b4d8, #4ade80, #ffa500, #f472b6);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        letter-spacing: 3px; margin-bottom: 8px;
    }
    .main-subtitle {
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.78em; color: #8ecdf6; letter-spacing: 0.8px; line-height: 1.8;
        font-weight: 600;
        text-shadow: 0 0 12px rgba(0,180,216,0.16);
    }
    .rainbow-bar {
        height: 3px;
        background: linear-gradient(90deg, #00b4d8, #4ade80, #ffa500, #f472b6, #a855f7, #00b4d8);
        border-radius: 2px; margin: 16px 0 0 0;
    }

    /* NAV PILLS */
    .nav-pills-wrap {
        display: flex; flex-wrap: wrap; gap: 8px;
        justify-content: center; margin-bottom: 22px;
    }
    .nav-pill {
        font-family: 'Rajdhani', sans-serif;
        font-size: 0.82em; font-weight: 700;
        padding: 6px 16px; border-radius: 20px;
        letter-spacing: 0.5px; border: 1px solid;
    }
    .np-cyan  { color:#00b4d8; border-color:rgba(0,180,216,0.4); background:rgba(0,180,216,0.08); }
    .np-green { color:#4ade80; border-color:rgba(74,222,128,0.4); background:rgba(74,222,128,0.08); }
    .np-orange{ color:#ffa500; border-color:rgba(255,165,0,0.4);  background:rgba(255,165,0,0.08); }
    .np-purple{ color:#a855f7; border-color:rgba(168,85,247,0.4); background:rgba(168,85,247,0.08); }

    /* KPI ROW */
    .kpi-row {
        display: grid; grid-template-columns: repeat(5, 1fr);
        gap: 10px; margin-bottom: 22px;
    }
    .kpi-card {
        background: linear-gradient(135deg, #0d1828, #0a1422);
        border-radius: 12px; padding: 14px 12px;
        border: 1px solid rgba(0,180,216,0.15);
        text-align: center; position: relative; overflow: hidden;
    }
    .kpi-card::before {
        content:''; position:absolute; top:0; left:0; right:0; height:2px;
        background: linear-gradient(90deg, #00b4d8, transparent);
    }
    .kpi-val {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.5em; font-weight: 700;
        color: #00b4d8; line-height: 1; margin-bottom: 4px;
        overflow-wrap: anywhere;
    }
    .kpi-lbl {
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.68em; color: #9cc7e6;
        letter-spacing: 1px; text-transform: uppercase;
        font-weight: 700;
    }
    .kpi-sub { font-size: 0.78em; color: #78a9cc; margin-top: 4px; font-weight: 500; }

    /* PROGRESS BAR */
    .prog-wrap {
        background: #0d1828; border-radius: 12px;
        padding: 14px 20px; margin-bottom: 22px;
        border: 1px solid rgba(0,180,216,0.1);
        display: flex; align-items: center; gap: 16px;
    }
    .prog-label {
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.76em; color: #9cc7e6;
        letter-spacing: 1px; white-space: nowrap;
        font-weight: 700;
    }
    .prog-bar-bg {
        flex: 1; height: 8px; background: #1a2a3a;
        border-radius: 4px; overflow: hidden;
    }
    .prog-bar-fill { height: 100%; border-radius: 4px; transition: width 0.5s; }
    .prog-pct {
        font-family: 'Orbitron', sans-serif;
        font-size: 1em; font-weight: 700; white-space: nowrap;
    }

    /* PHASE SECTIONS */
    .phase-wrap {
        background: linear-gradient(135deg, #0a0f1a, #0d1422);
        border: 1px solid #1a3a5f; border-radius: 14px;
        padding: 18px 20px; margin-bottom: 16px;
    }
    .phase-head {
        display: flex; align-items: center; gap: 10px;
        margin-bottom: 14px; padding-bottom: 10px;
        border-bottom: 1px solid #1a3a5f;
    }
    .phase-dot {
        width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0;
        background: #fbbf24 !important;
        box-shadow: 0 0 12px rgba(251,191,36,0.45);
    }
    .phase-title {
        font-family: 'Rajdhani', sans-serif;
        font-size: 0.98em; font-weight: 700;
        color: #f8d477; letter-spacing: 1px; text-transform: uppercase;
        text-shadow: 0 0 10px rgba(251,191,36,0.18);
    }
    .steps-grid   { display: grid; grid-template-columns: repeat(4,1fr); gap: 10px; }
    .steps-grid-3 { display: grid; grid-template-columns: repeat(3,1fr); gap: 10px; }
    .steps-grid-5 { display: grid; grid-template-columns: repeat(5,1fr); gap: 10px; }

    /* STEP CARD */
    .step-card {
        background: #0d1828; border-radius: 10px;
        padding: 12px 14px; border: 1px solid #1e3a5f;
        position: relative; overflow: hidden;
        transition: border-color 0.2s;
    }
    .step-card.done  { border-color: rgba(74,222,128,0.35); }
    .step-card.pend  { border-color: rgba(0,180,216,0.12); }
    .step-card.opt   { border-color: rgba(168,85,247,0.25); }
    .step-card::before {
        content:''; position:absolute; top:0; left:0; right:0; height:2px;
    }
    .step-card.done::before  { background: linear-gradient(90deg, #4ade80, transparent); }
    .step-card.pend::before  { background: linear-gradient(90deg, #00b4d8, transparent); }
    .step-card.opt::before   { background: linear-gradient(90deg, #a855f7, transparent); }

    .step-num {
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.70em; color: #f8d477 !important;
        letter-spacing: 2px; margin-bottom: 4px;
        font-weight: 700;
        text-shadow: 0 0 10px rgba(251,191,36,0.18);
    }
    .step-icon-row { display: flex; align-items: center; gap: 6px; margin-bottom: 4px; }
    .step-title {
        font-family: 'Rajdhani', sans-serif;
        font-size: 0.98em; font-weight: 700; color: #f1f7ff;
    }
    .step-title.done { color: #4ade80; }
    .step-what { font-size: 0.82em; color: #89b6d8; line-height: 1.55; margin-bottom: 8px; font-weight: 500; }
    .step-badge {
        display: inline-block; font-family: 'Share Tech Mono', monospace;
        font-size: 0.65em; padding: 2px 8px; border-radius: 10px;
    }
    .badge-done { background: rgba(74,222,128,0.12); color: #4ade80; border: 1px solid rgba(74,222,128,0.3); }
    .badge-pend { background: rgba(0,180,216,0.12); color: #77d9ff; border: 1px solid rgba(0,180,216,0.32); }
    .badge-opt  { background: rgba(168,85,247,0.1);  color: #a855f7; border: 1px solid rgba(168,85,247,0.3); }

    /* INFO GRID */
    .info-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 12px; margin: 20px 0 16px; }
    .info-card {
        background: #0d1828; border: 1px solid #1e3a5f; border-radius: 12px; padding: 16px 18px;
    }
    .info-card h4 {
        font-family: 'Rajdhani', sans-serif; font-weight: 700;
        color: #f8fafc; font-size: 1.02em; margin-bottom: 12px;
        letter-spacing: 0.5px;
        text-shadow: 0 0 10px rgba(148,163,184,0.18);
    }
    .info-card ul { padding-left: 14px; margin: 0; }
    .info-card li {
        font-size: 0.86em;
        color: #a8d0f0;
        margin-bottom: 7px;
        line-height: 1.5;
        font-weight: 500;
    }

    /* START BANNER */
    .start-banner {
        background: linear-gradient(135deg, #0a1a2a, #0d1f35);
        border: 1px solid rgba(0,180,216,0.25);
        border-radius: 12px; padding: 14px 20px;
        font-size: 0.88em; color: #5a8aaa; text-align: center;
        margin-top: 8px;
    }
    .start-banner strong { color: #00b4d8; }
    </style>
    """, unsafe_allow_html=True)

    # ── DEVELOPER CARD ────────────────────────────────────────────────
    st.markdown("""
    <div class="dev-card">
        <div class="dev-label">✦ DEVELOPED BY ✦</div>
        <div class="dev-name">ZUNAIR SHAHZAD</div>
        <div class="dev-field">Chemical Engineering</div>
        <div class="dev-uni">University of Engineering &amp; Technology (UET), Lahore — New Campus</div>
        <div class="dev-year">2022 – 2026</div>
    </div>
    <div class="main-title-wrap">
        <div class="main-icon">⚗️</div>
        <div class="main-title">AI-ASSISTED DISTILLATION DESIGN PLATFORM</div>
        <div class="main-subtitle">
            Binary Separation System &nbsp;|&nbsp; Fenske · Underwood · Gilliland · Kirkbride Shortcut
            &nbsp;|&nbsp; McCabe-Thiele Graphical &nbsp;|&nbsp; Tray &amp; Packed Column Design
            &nbsp;|&nbsp; ASME Mechanical &nbsp;|&nbsp; Groq AI Advisory
        </div>
        <div class="rainbow-bar"></div>
    </div>
    """, unsafe_allow_html=True)

    # ── NAV PILLS ─────────────────────────────────────────────────────
    st.markdown("""
    <div class="nav-pills-wrap">
        <span class="nav-pill np-cyan">📥 Feed Specs</span>
        <span class="nav-pill np-cyan">🧪 Thermodynamics</span>
        <span class="nav-pill np-cyan">⚡ Shortcut Design</span>
        <span class="nav-pill np-cyan">📈 McCabe-Thiele</span>
        <span class="nav-pill np-green">▦ Tray Design</span>
        <span class="nav-pill np-green">◎ Packing Design</span>
        <span class="nav-pill np-orange">♨️ Reboiler</span>
        <span class="nav-pill np-orange">❄️ Condenser</span>
        <span class="nav-pill np-orange">⚙️ Mechanical</span>
        <span class="nav-pill np-purple">🤖 AI Assistant</span>
        <span class="nav-pill np-purple">📋 Report</span>
    </div>
    """, unsafe_allow_html=True)

    # ── PROGRESS BAR ──────────────────────────────────────────────────
    st.markdown(f"""
    <div class="prog-wrap">
        <span class="prog-label">DESIGN PROGRESS</span>
        <div class="prog-bar-bg">
            <div class="prog-bar-fill" style="width:{bar_w}%; background:{bar_color};"></div>
        </div>
        <span class="prog-pct" style="color:{bar_color}">{pct}%</span>
        <span class="prog-label">{done_count}/{len(checks)} SECTIONS</span>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI STRIP ─────────────────────────────────────────────────────
    kpi_feed   = f"{feed.get('F','—')} kmol/h" if feed else "—"
    kpi_comp   = f"{feed.get('light','?')}/{feed.get('heavy','?')}" if feed else "—/—"
    kpi_stages = str(shortcut.get('N_actual_int','—')) if shortcut else "—"
    kpi_r      = f"{shortcut.get('R',0):.3f}" if shortcut and shortcut.get('R') else "—"
    kpi_diam   = f"{diameter.get('D_column_std_m','—')} m" if diameter else "—"
    kpi_ht     = f"{height.get('total_height_m','—')} m" if height else "—"

    col_icon   = "▦" if col_type=="tray" else ("◎" if col_type=="packed" else "⚙️")
    col_color  = "#00b4d8" if col_type=="tray" else ("#22c55e" if col_type=="packed" else "#a9bed8")

    st.markdown(f"""
    <div class="kpi-row">
        <div class="kpi-card">
            <div class="kpi-val">{kpi_feed}</div>
            <div class="kpi-lbl">Feed Flow</div>
            <div class="kpi-sub">{kpi_comp}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-val">{kpi_stages}</div>
            <div class="kpi-lbl">Theoretical Stages</div>
            <div class="kpi-sub">Gilliland N_theoretical</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-val">{kpi_r}</div>
            <div class="kpi-lbl">Reflux Ratio R</div>
            <div class="kpi-sub">Operating reflux</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-val">{kpi_diam}</div>
            <div class="kpi-lbl">Column Diameter</div>
            <div class="kpi-sub">Fair / GPDC method</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-val" style="color:{col_color}">{col_icon} {col_label}</div>
            <div class="kpi-lbl">Column Type</div>
            <div class="kpi-sub">H = {kpi_ht}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── helper ────────────────────────────────────────────────────────
    def step(num, icon, title, what, done, val="", optional=False):
        cls   = "done" if done else ("opt" if optional else "pend")
        tcls  = "done" if done else ""
        badge = f'<span class="step-badge badge-done">✓ {val}</span>' if done and val else \
                (f'<span class="step-badge badge-done">✓ done</span>' if done else
                 (f'<span class="step-badge badge-opt">optional</span>' if optional else
                  f'<span class="step-badge badge-pend">pending</span>'))
        return f"""
        <div class="step-card {cls}">
          <div class="step-num">STEP {num}</div>
          <div class="step-icon-row">
            <span style="font-size:13px">{icon}</span>
            <span class="step-title {tcls}">{title}</span>
          </div>
          <div class="step-what">{what}</div>
          {badge}
        </div>"""

    # ── PHASE 1 — COMMON ──────────────────────────────────────────────
    p1 = (step("01","📥","Feed Specifications",
               "Feed flow, binary components, purity targets (xD, xB), q-value, operating pressure",
               bool(feed), f"F={feed.get('F','?')} | {feed.get('light','?')}/{feed.get('heavy','?')}" if feed else "") +
          step("02","🧪","Thermodynamics DB",
               "VLE model, α calculation, bubble/dew points, Antoine equation, x-y equilibrium curve",
               bool(thermo), f"α={thermo.get('alpha_avg','?')}" if thermo else "") +
          step("03","🏗️","Column Type Selection",
               "Choose Tray (sieve/valve/bubble-cap) or Packed (random/structured) — unlocks correct design path",
               col_type is not None, f"Type: {col_label}" if col_type else "") +
          step("04","⚡","Shortcut Design",
               "Fenske (N_min) → Underwood (R_min) → Gilliland (N_actual) → Kirkbride (feed tray)",
               bool(shortcut),
               f"N={shortcut.get('N_actual_int','?')} R={shortcut.get('R',0):.2f}" if shortcut and shortcut.get('R') else "") +
          step("05","📈","McCabe-Thiele",
               "Graphical x-y stage stepping — common to both column types. N_theoretical → trays (tray) or HETP×N (packed)",
               bool(mc), f"N_graphical={mc.get('n_stages','?')}" if mc else ""))

    st.markdown(f"""
    <div class="phase-wrap">
      <div class="phase-head">
        <div class="phase-dot" style="background:#00b4d8"></div>
        <span class="phase-title">⬡ Phase 1 — Process Basis &amp; Shortcut Design &nbsp;(Common to Both Column Types)</span>
      </div>
      <div class="steps-grid">{p1}</div>
    </div>""", unsafe_allow_html=True)

    # ── PHASE 2a — TRAY ──────────────────────────────────────────────
    if col_type == "tray" or col_type is None:
        tray_val = f"{td.get('tray_type','?')} | E={td.get('E_o',0)*100:.0f}% | {td.get('N_actual_trays','?')} trays" if td else ""
        p2a = (step("06a","▦","Tray Design",
                    "O'Connell efficiency, sieve/valve/bubble-cap hydraulics, weeping, flooding, entrainment, downcomer backup",
                    bool(td), tray_val) +
               step("07a","📐","Column Diameter",
                    "Fair flooding correlation — operating velocity 80% flood, column cross-section area, standardise diameter",
                    bool(diameter) and col_type=="tray",
                    f"D={diameter.get('D_column_std_m','?')} m" if (diameter and col_type=='tray') else "") +
               step("08a","📏","Column Height",
                    "N_actual_trays × tray_spacing + top disengagement + feed nozzle + sump = total column height",
                    bool(height) and col_type=="tray",
                    f"H={height.get('total_height_m','?')} m" if (height and col_type=='tray') else ""))
        lbl = "⬡ Phase 2a — Tray Column Design"
        if col_type is None:
            lbl += " &nbsp;(select Tray in Column Type to activate)"
        st.markdown(f"""
        <div class="phase-wrap">
          <div class="phase-head">
            <div class="phase-dot" style="background:#00b4d8"></div>
            <span class="phase-title">{lbl}</span>
          </div>
          <div class="steps-grid-3">{p2a}</div>
        </div>""", unsafe_allow_html=True)

    # ── PHASE 2b — PACKED ─────────────────────────────────────────────
    if col_type == "packed" or col_type is None:
        pack_val = f"{pd_.get('packing','?')} HETP={pd_.get('HETP','?')} m" if pd_ else ""
        p2b = (step("05b","◎","Packing Design",
                    "Random (Pall Rings/Raschig/IMTP) or Structured (Mellapak/Flexipac). HETP selection, Z = N × HETP",
                    bool(pd_), pack_val) +
               step("06b","📐","Diameter (Packed)",
                    "GPDC Eckert flooding correlation — 70-80% flood operating velocity, column diameter from area",
                    bool(diameter) and col_type=="packed",
                    f"D={diameter.get('D_column_std_m','?')} m" if (diameter and col_type=='packed') else "") +
               step("07b","📏","Height (Packed)",
                    "Packed bed + redistributors every 3-5m + top disengagement + sump = total column height",
                    bool(height) and col_type=="packed",
                    f"H={height.get('total_height_m','?')} m" if (height and col_type=='packed') else ""))
        lbl = "⬡ Phase 2b — Packed Column Design"
        if col_type is None:
            lbl += " &nbsp;(select Packed in Column Type to activate)"
        st.markdown(f"""
        <div class="phase-wrap">
          <div class="phase-head">
            <div class="phase-dot" style="background:#22c55e"></div>
            <span class="phase-title">{lbl}</span>
          </div>
          <div class="steps-grid-3">{p2b}</div>
        </div>""", unsafe_allow_html=True)

    # ── PHASE 3 — DETAILED ────────────────────────────────────────────
    p3 = (step("09","♨️","Reboiler Design",
               "Kettle/thermosyphon — duty Q_R, LMTD, heat transfer area, steam consumption, shell-and-tube sizing",
               bool(reboiler), f"Q={reboiler.get('Q_reb_kW','?')} kW" if reboiler else "") +
          step("10","❄️","Condenser Design",
               "Total/partial condenser — Q_C, cooling water rate, area, LMTD correction, tube/shell design",
               bool(condenser), f"Q={condenser.get('Q_cond_kW','?')} kW" if condenser else "") +
          step("11","📉","Pressure Drop",
               "Full column ΔP — per-tray or per-metre, total pressure profile, vacuum/atmospheric feasibility",
               bool(pdrop), f"ΔP={pdrop.get('dP_total_mmHg','?')} mmHg" if pdrop else "") +
          step("12","⚙️","Mechanical Design",
               "ASME UG-27 shell thickness, material selection (CS/SS/alloy), nozzle sizing, skirt support loads",
               bool(mech), f"t={mech.get('t_calculated_mm','?')} mm" if mech else "") +
          step("13","🔧","Column Internals",
               "Liquid distributors, redistributors, tray support rings, weir types, downcomer seals, manways",
               bool(s.get("internals",{})), "done" if s.get("internals") else "") +
          step("14","🎛️","Instrumentation",
               "P&ID control loops — temperature, pressure, flow, level, safety instrumented functions (SIF)",
               bool(s.get("instrumentation",{})), "done" if s.get("instrumentation") else "") +
          step("15","💰","Energy & Economics",
               "Steam/CW consumption, CAPEX (AACE Class 4), annual OPEX, payback period, NPV & IRR analysis",
               bool(energy), "done" if energy else "") +
          step("16","🔬","Rigorous Design",
               "Stage-by-stage Murphree efficiency, Kremser method, composition profiles — optional verification",
               bool(s.get("rigorous",{})), "optional", optional=True))

    st.markdown(f"""
    <div class="phase-wrap">
      <div class="phase-head">
        <div class="phase-dot" style="background:#f59e0b"></div>
        <span class="phase-title">⬡ Phase 3 — Detailed Design &nbsp;(Common to Both Column Types)</span>
      </div>
      <div class="steps-grid">{p3}</div>
    </div>""", unsafe_allow_html=True)

    # ── PHASE 4 — OUTPUT ──────────────────────────────────────────────
    ai_ok = bool(s.get("groq_api_key",""))
    p4 = (step("17","🖼️","3D Visualization",
               "Interactive column schematic, temperature/composition profiles along height, tray or packing diagrams",
               True, "always available") +
          step("18","🤖","AI Assistant",
               "Groq Llama-3 powered advisor — design review, optimization suggestions, troubleshooting, what-if analysis",
               ai_ok, "API active ✓" if ai_ok else "needs Groq key") +
          step("19","📋","Report Generator",
               "Full engineering design report — all sections compiled, Markdown preview, CSV export, printable summary",
               True, "always available"))

    st.markdown(f"""
    <div class="phase-wrap">
      <div class="phase-head">
        <div class="phase-dot" style="background:#a855f7"></div>
        <span class="phase-title">⬡ Phase 4 — Output, AI &amp; Reports</span>
      </div>
      <div class="steps-grid-3">{p4}</div>
    </div>""", unsafe_allow_html=True)

    # ── REFERENCES + EQUATIONS ────────────────────────────────────────
    st.markdown("""
    <div class="info-grid">
        <div class="info-card">
            <h4>📖 Key References</h4>
            <ul>
                <li>McCabe, Smith &amp; Harriott — Unit Operations of Chemical Engineering</li>
                <li>Seader, Henley &amp; Roper — Separation Process Principles</li>
                <li>Coulson &amp; Richardson — Chemical Engineering Vol. 2</li>
                <li>Perry's Chemical Engineers' Handbook (9th Ed.)</li>
                <li>Towler &amp; Sinnott — Chemical Engineering Design</li>
                <li>Strigle — Packed Tower Design &amp; Applications</li>
                <li>Kern — Process Heat Transfer</li>
            </ul>
        </div>
        <div class="info-card">
            <h4>🏭 Industrial Standards</h4>
            <ul>
                <li>ASME BPVC Section VIII Div. 1 — Pressure Vessels</li>
                <li>TEMA Standards — Shell &amp; Tube Heat Exchangers</li>
                <li>API 520 / 521 — PSV Sizing &amp; Selection</li>
                <li>IEC 61511 — Safety Instrumented Systems</li>
                <li>ISA-5.1 — P&amp;ID Symbols &amp; Identification</li>
                <li>GPDC / Eckert Chart — Packed Column Flooding</li>
                <li>Fair Method — Tray Column Diameter</li>
            </ul>
        </div>
        <div class="info-card">
            <h4>⚗️ Core Equations</h4>
            <ul>
                <li>Antoine: log₁₀(P*) = A − B/(C+T)</li>
                <li>Fenske: N_min = log[xD/xB·(1-xB)/(1-xD)] / log(α)</li>
                <li>Underwood: α·zF/(α−θ) = 1−q → R_min</li>
                <li>Gilliland: Molokanov (1972) Y = f(X)</li>
                <li>Kirkbride: log(Nr/Ns) = 0.206·log[…]</li>
                <li>Fair: u_flood = C_SB·√(ρL−ρV)/ρV</li>
                <li>ASME UG-27: t = P·R/(S·E − 0.6P) + CA</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── START BANNER ──────────────────────────────────────────────────
    st.markdown("""
    <div class="start-banner">
        🚀 <strong>Start here:</strong> Go to <strong>📥 Feed Specifications</strong> in the sidebar.
        Follow the phase sequence step by step for a complete column design.
        &nbsp;|&nbsp; Get a free <strong>Groq API key</strong> at <strong>console.groq.com</strong>
        to activate AI optimization advisor.
    </div>
    """, unsafe_allow_html=True)
