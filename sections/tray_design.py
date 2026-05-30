"""sections/tray_design.py — Complete Tray Column Hydraulic Design"""
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd


def render():
    st.markdown("""
    <div class="section-header">
        <h1>▦ Tray Column Design</h1>
        <p>Tray type selection, hydraulic design, O'Connell efficiency, downcomer backup,
           entrainment, weeping, turndown — complete sieve/valve/bubble-cap design.</p>
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
    .formula-box {
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
    .formula-box strong {
        color: #22c55e !important;
        font-weight: 900 !important;
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
    .success-panel strong,
    .info-panel strong,
    .warn-panel strong {
        color: #f8d477 !important;
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
    .tray-check-row {
        background: linear-gradient(135deg, rgba(8, 14, 24, 0.99), rgba(15, 23, 42, 0.97));
        border-radius: 8px;
        padding: 0.8rem 1rem;
        margin: 0.45rem 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 1rem;
        border: 1px solid rgba(0, 180, 216, 0.28);
        box-shadow: 0 8px 20px rgba(0,0,0,0.14);
    }
    .tray-check-label {
        color: #f8fbff !important;
        font-weight: 900;
    }
    .tray-check-value {
        font-family: 'Share Tech Mono', monospace;
        font-weight: 900;
        text-align: right;
        overflow-wrap: anywhere;
    }
    .tray-calc-separator {
        border-top: 1px dashed rgba(248, 212, 119, 0.48);
        margin: 0.85rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

    col_type = st.session_state.get("column_type", None)
    if col_type == "packed":
        st.markdown("""
        <div class="warn-panel">
        ⚠️ <b>Packed Column selected.</b> Tray hydraulics apply to tray columns only.
        Go to <b>◎ Packing Design</b> for your column.
        <i>This section is still viewable for reference/comparison.</i>
        </div>
        """, unsafe_allow_html=True)
    elif col_type == "tray":
        st.markdown("""
        <div class="success-panel">
        ✅ <b>Tray Column selected</b> — all calculations below apply to your design.
        </div>
        """, unsafe_allow_html=True)

    feed     = st.session_state.get("feed", {})
    shortcut = st.session_state.get("shortcut", {})
    diameter = st.session_state.get("diameter", {})

    if not feed or not shortcut:
        st.warning("⚠️ Complete Feed Specifications and Shortcut Design first.")
        return

    R        = shortcut.get("R", 2.0)
    D_mol    = shortcut.get("D", feed.get("F", 100) * 0.5)
    N_theor  = shortcut.get("N_actual_int", 15)
    alpha    = shortcut.get("alpha", 2.5)
    P_mmHg   = feed.get("P_col_mmHg", 760.0)
    V_mol    = (R + 1) * D_mol   # kmol/h
    rho_L    = diameter.get("rho_L", feed.get("rho_L_distillate", feed.get("rho_L_feed", 850.0)))
    rho_V    = diameter.get("rho_V", 3.0)
    D_col    = diameter.get("D_column_std_m", 1.2)
    MW_avg   = diameter.get("MW_avg", feed.get("distillate_props", {}).get("MW", 80.0))

    tab1, tab2, tab3, tab4 = st.tabs([
        "🔧 Tray Type & Geometry",
        "📐 Hydraulic Calculations",
        "📊 Performance Curves",
        "📋 Summary & Checks"
    ])

    # ═══════════════════════════════════════════════════
    # TAB 1 — Tray Type & Geometry
    # ═══════════════════════════════════════════════════
    with tab1:
        st.markdown("### Tray Type Selection")
        tray_type = st.selectbox("Tray Type", [
            "Sieve Tray", "Valve Tray", "Bubble Cap Tray"
        ])

        st.markdown("""
        <div class="formula-box">
        <div class="formula-title">Tray Type Comparison</div>
        <b>Sieve:</b> Simple punched holes — lowest cost, good efficiency, moderate turndown (2:1)<br>
        <b>Valve:</b> Floating valves — better turndown (4:1), self-regulating, most common industrially<br>
        <b>Bubble Cap:</b> Highest turndown (∞), handles low liquid flow, highest cost/pressure drop
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            tray_spacing = st.number_input("Tray Spacing [m]",
                value=0.60, min_value=0.15, max_value=1.2, step=0.05)
            weir_h_mm = st.number_input("Weir Height [mm]",
                value=50.0, min_value=10.0, max_value=150.0, step=5.0)
            weir_len_frac = st.number_input("Weir Length / D_col",
                value=0.73, min_value=0.60, max_value=0.85, step=0.01,
                help="Typically 0.73 × D_col for segmental downcomer")
        with c2:
            dc_frac = st.number_input("Downcomer Area Fraction",
                value=0.12, min_value=0.05, max_value=0.25, step=0.01,
                help="A_dc / A_total — typically 10–15%")
            if tray_type == "Sieve Tray":
                hole_dia_mm = st.number_input("Hole Diameter [mm]",
                    value=5.0, min_value=2.0, max_value=25.0, step=0.5)
                hole_pitch_frac = st.number_input("Hole Area / Active Area",
                    value=0.10, min_value=0.05, max_value=0.20, step=0.005)
            elif tray_type == "Valve Tray":
                hole_dia_mm = 39.0  # standard valve opening ~39mm
                hole_pitch_frac = 0.14
                st.info("Valve trays: standard 39mm valve, ~14% open area used")
            else:
                hole_dia_mm = 38.0  # bubble cap riser
                hole_pitch_frac = 0.08
                st.info("Bubble caps: 38mm riser diameter, ~8% open area used")
        with c3:
            mu_L = st.number_input("Liquid Viscosity μ_L [mPa·s]",
                value=float(feed.get("mu_L_distillate", feed.get("mu_L_feed", 0.5))),
                min_value=0.05, max_value=100.0, step=0.05,
                help="Used in O'Connell efficiency correlation")
            flood_frac = st.slider("Design Flooding Fraction f",
                0.60, 0.85, 0.80, 0.01,
                help="u_op = f × u_flood. Typical: 75–82%")
            tray_thick_mm = st.number_input("Tray Thickness [mm]",
                value=2.0, min_value=1.0, max_value=5.0, step=0.5)

        # Geometry calculations
        A_total  = np.pi * D_col**2 / 4
        A_dc     = dc_frac * A_total
        A_net    = A_total - A_dc
        A_active = A_total - 2 * A_dc
        A_holes  = hole_pitch_frac * A_active
        weir_len = weir_len_frac * D_col
        n_holes  = int(A_holes / (np.pi * (hole_dia_mm/1000)**2 / 4))

        st.markdown(f"""
        <div class="formula-box" style="border-left:4px solid #22c55e;">
        <div class="formula-title">Tray Geometry Calculation</div>
        <b>1. Column cross-sectional area:</b>
        A<sub>total</sub> = πD²/4 = π({D_col:.2f})²/4 = <b>{A_total:.4f} m²</b><br>
        <div class="tray-calc-separator"></div>
        <b>2. Downcomer and net area:</b>
        A<sub>dc</sub> = {dc_frac:.2f} × {A_total:.4f} = <b>{A_dc:.4f} m²</b><br>
        A<sub>net</sub> = A<sub>total</sub> − A<sub>dc</sub> = {A_total:.4f} − {A_dc:.4f} = <b>{A_net:.4f} m²</b><br>
        <div class="tray-calc-separator"></div>
        <b>3. Active bubbling area:</b>
        A<sub>active</sub> = A<sub>total</sub> − 2A<sub>dc</sub> = {A_total:.4f} − 2({A_dc:.4f}) = <b>{A_active:.4f} m²</b><br>
        A<sub>holes</sub> = open area × A<sub>active</sub> = {hole_pitch_frac:.3f} × {A_active:.4f} = <b>{A_holes:.5f} m²</b><br>
        <div class="tray-calc-separator"></div>
        <b>4. Weir and hole count:</b>
        l<sub>w</sub> = {weir_len_frac:.2f} × D = <b>{weir_len:.3f} m</b><br>
        N<sub>holes</sub> = A<sub>holes</sub> / (πd<sub>h</sub>²/4)
        = {A_holes:.5f} / [π({hole_dia_mm/1000:.4f})²/4] = <b>{n_holes:,}</b>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### Geometric Results")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("A_total",  f"{A_total:.4f} m²")
        c2.metric("A_net",    f"{A_net:.4f} m²")
        c3.metric("A_active", f"{A_active:.4f} m²")
        c4.metric("A_holes",  f"{A_holes:.5f} m²")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("A_downcomer", f"{A_dc:.4f} m²")
        c2.metric("Weir length", f"{weir_len:.3f} m")
        c3.metric("No. of holes", f"{n_holes:,}")
        c4.metric("Hole dia",     f"{hole_dia_mm} mm")

    # ═══════════════════════════════════════════════════
    # TAB 2 — Hydraulic Calculations
    # ═══════════════════════════════════════════════════
    with tab2:

        # Vapour volumetric flow
        V_m3_s = (V_mol * MW_avg / 1000) / (rho_V * 3600)

        # ── Flooding velocity (Souders-Brown / Fair) ──────────
        CSB_base = 0.04 + 0.015 * np.log10(max(tray_spacing / 0.6, 0.01))
        u_flood  = CSB_base * np.sqrt((rho_L - rho_V) / rho_V)
        u_op     = flood_frac * u_flood
        u_hole   = V_m3_s / A_holes

        # ── O'Connell Tray Efficiency ─────────────────────────
        st.markdown("""
        <div class="formula-box">
        <div class="formula-title">O'Connell Correlation — Overall Tray Efficiency</div>
        E_o = 51 − 32.5 × log(α × μ_L) &nbsp;&nbsp; [%]<br>
        α = relative volatility, μ_L = liquid viscosity [mPa·s]<br>
        Valid range: 0.1 ≤ α·μ_L ≤ 10 &nbsp;|&nbsp; Typical E_o = 60–80% for hydrocarbon systems
        </div>
        """, unsafe_allow_html=True)

        alpha_mu = alpha * mu_L
        E_o_raw  = 51 - 32.5 * np.log10(max(alpha_mu, 0.01))
        E_o      = max(0.20, min(0.95, E_o_raw / 100))
        N_actual_trays = int(np.ceil(N_theor / E_o))

        st.markdown(f"""
        <div class="formula-box" style="border-left:4px solid #22c55e;">
        <div class="formula-title">✏️ O'Connell Calculation</div>
        α × μ_L = {alpha:.4f} × {mu_L} = <b>{alpha_mu:.4f}</b><br>
        E_o = 51 − 32.5 × log({alpha_mu:.4f}) = 51 − 32.5 × ({np.log10(max(alpha_mu,0.01)):.4f})<br>
        E_o = 51 − {32.5 * np.log10(max(alpha_mu,0.01)):.2f} = <b>{E_o_raw:.2f}% → {E_o*100:.1f}%</b><br>
        N_actual_trays = N_theoretical / E_o = {N_theor} / {E_o:.4f} = <b>{N_actual_trays} trays</b>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("α × μ_L",        f"{alpha_mu:.4f}")
        c2.metric("E_o (O'Connell)", f"{E_o*100:.1f}%")
        c3.metric("N_theoretical",   f"{N_theor}")
        c4.metric("N_actual trays",  f"{N_actual_trays}")

        st.markdown("<div class='eng-divider'></div>", unsafe_allow_html=True)

        # ── Dry tray pressure drop ─────────────────────────────
        st.markdown("""
        <div class="formula-box">
        <div class="formula-title">Dry Tray Pressure Drop (Francis Weir + Orifice Equation)</div>
        h_dry = C_dry × (u_h)² × ρᵥ / ρ_L &nbsp;&nbsp; [mm liquid]<br>
        C_dry = 0.60 (sieve), 0.50 (valve), 0.45 (bubble cap)<br>
        h_weir = h_w + 750 × (Q_L / l_w)^(2/3) &nbsp;&nbsp; Francis weir formula<br>
        h_dc = h_weir + h_dry + h_da &nbsp;&nbsp; (downcomer backup)<br>
        ΔP_tray = (h_dry + h_weir) × ρ_L × g / 1000 &nbsp;&nbsp; [Pa]
        </div>
        """, unsafe_allow_html=True)

        C_dry_map = {"Sieve Tray": 0.60, "Valve Tray": 0.50, "Bubble Cap Tray": 0.45}
        C_dry = C_dry_map[tray_type]

        # Liquid flow (approx from internal reflux)
        L_mol   = R * D_mol          # kmol/h liquid in rectifying
        L_m3_s  = (L_mol * MW_avg / 1000) / (rho_L * 3600)
        Q_L     = L_m3_s

        h_dry   = C_dry * u_hole**2 * rho_V / rho_L   # mm liquid
        h_weir  = weir_h_mm + 750 * (Q_L / max(weir_len, 0.01))**(2/3)
        # Downcomer apron head loss — Perry's 14-31
        # h_da = 165.2 * (Q_L / A_da)^2  [mm liquid]
        # A_da = apron clearance area ≈ 60% of downcomer area (conservative)
        A_da    = 0.60 * A_dc
        h_da    = 165.2 * (Q_L / max(A_da, 1e-6)) ** 2  # mm liquid
        h_dc_backup = h_weir + h_dry + h_da   # total downcomer backup mm

        dP_tray = (h_dry + h_weir) * rho_L * 9.81 / 1000   # Pa

        st.markdown(f"""
        <div class="formula-box" style="border-left:4px solid #00b4d8;">
        <div class="formula-title">✏️ Hydraulic Calculation</div>
        u_hole = V_vol / A_holes = {V_m3_s:.5f} / {A_holes:.5f} = <b>{u_hole:.3f} m/s</b><br>
        h_dry = {C_dry} × {u_hole:.3f}² × {rho_V:.3f} / {rho_L} = <b>{h_dry:.2f} mm liq</b><br>
        Q_L = {Q_L*3600:.4f} m³/h, weir_len = {weir_len:.3f} m<br>
        h_weir = {weir_h_mm} + 750 × ({Q_L:.5f}/{weir_len:.3f})^(2/3) = <b>{h_weir:.2f} mm liq</b><br>
        Downcomer backup h_dc = {h_dry:.2f} + {h_weir:.2f} + {h_da:.2f} = <b>{h_dc_backup:.2f} mm liq</b><br>
        ΔP_tray = ({h_dry:.2f} + {h_weir:.2f}) × {rho_L} × 9.81 / 1000 = <b>{dP_tray:.1f} Pa</b>
        </div>
        """, unsafe_allow_html=True)

        # ── Entrainment ───────────────────────────────────────
        st.markdown("""
        <div class="formula-box">
        <div class="formula-title">Entrainment — Fair Correlation</div>
        ψ = e / (L + e) &nbsp;&nbsp; fractional entrainment<br>
        FLV = (L/V) × √(ρᵥ/ρ_L) &nbsp;&nbsp; flow parameter<br>
        ψ = 10^[a + b × log(FLV)] &nbsp;&nbsp; from Fair's chart
        </div>
        """, unsafe_allow_html=True)

        FLV = (L_mol / V_mol) * np.sqrt(rho_V / rho_L)
        # Fair entrainment approximation
        psi_raw = 10 ** (-1.463 * FLV**0.842)
        psi = min(psi_raw, 0.5)   # cap at 50%
        e_frac = psi * L_mol / max(1 - psi, 0.01)

        # ── Weeping check ─────────────────────────────────────
        st.markdown("""
        <div class="formula-box">
        <div class="formula-title">Weeping Check — Minimum Hole Velocity</div>
        u_weep = √[(h_weir × ρ_L × g) / (0.7 × ρᵥ)] &nbsp;&nbsp; [m/s]<br>
        Condition: u_hole > u_weep to prevent weeping
        </div>
        """, unsafe_allow_html=True)

        u_weep = np.sqrt((h_weir/1000 * rho_L * 9.81) / (0.7 * rho_V))

        # ── Turndown ratio ────────────────────────────────────
        st.markdown("""
        <div class="formula-box">
        <div class="formula-title">Turndown Ratio</div>
        Turndown = u_op / u_weep &nbsp;&nbsp; (how far below design flow tray still operates)<br>
        Sieve: ~2:1 | Valve: ~4:1 | Bubble cap: theoretically unlimited
        </div>
        """, unsafe_allow_html=True)

        turndown = u_hole / max(u_weep, 0.01)
        turndown_min = {"Sieve Tray": 2.0, "Valve Tray": 4.0, "Bubble Cap Tray": 6.0}
        td_ok = turndown >= turndown_min[tray_type]

        st.markdown(f"""
        <div class="formula-box" style="border-left:4px solid #f59e0b;">
        <div class="formula-title">Operating Window Calculation</div>
        <b>1. Entrainment flow parameter:</b>
        FLV = (L/V) × √(ρ<sub>V</sub>/ρ<sub>L</sub>)
        = ({L_mol:.2f}/{V_mol:.2f}) × √({rho_V:.3f}/{rho_L:.1f})
        = <b>{FLV:.4f}</b><br>
        <div class="tray-calc-separator"></div>
        <b>2. Entrainment fraction:</b>
        ψ = 10<sup>[-1.463 × FLV<sup>0.842</sup>]</sup>
        = <b>{psi*100:.2f}%</b> liquid entrainment<br>
        <div class="tray-calc-separator"></div>
        <b>3. Weeping velocity:</b>
        u<sub>weep</sub> = √[(h<sub>weir</sub> × ρ<sub>L</sub> × g)/(0.7 × ρ<sub>V</sub>)]
        = √[({h_weir/1000:.4f} × {rho_L:.1f} × 9.81)/(0.7 × {rho_V:.3f})]
        = <b>{u_weep:.3f} m/s</b><br>
        <div class="tray-calc-separator"></div>
        <b>4. Turndown ratio:</b>
        Turndown = u<sub>hole</sub>/u<sub>weep</sub>
        = {u_hole:.3f}/{u_weep:.3f}
        = <b>{turndown:.2f}:1</b> &nbsp; (minimum for {tray_type}: {turndown_min[tray_type]:.0f}:1)
        </div>
        """, unsafe_allow_html=True)

        # ── Results metrics ───────────────────────────────────
        st.markdown("### Hydraulic Results")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("u_hole",       f"{u_hole:.3f} m/s")
        c2.metric("u_flood",      f"{u_flood:.3f} m/s")
        c3.metric("u_op",         f"{u_op:.3f} m/s")
        c4.metric("Flood %",      f"{flood_frac*100:.0f}%")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("h_dry",        f"{h_dry:.2f} mm liq")
        c2.metric("h_weir",       f"{h_weir:.2f} mm liq")
        c3.metric("DC backup",    f"{h_dc_backup:.2f} mm liq")
        c4.metric("ΔP / tray",    f"{dP_tray:.1f} Pa")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("FLV",          f"{FLV:.4f}")
        c2.metric("Entrainment ψ",f"{psi*100:.2f}%")
        c3.metric("u_weep",       f"{u_weep:.3f} m/s")
        c4.metric("Turndown",     f"{turndown:.2f}:1")

        # ── Design Checks ─────────────────────────────────────
        st.markdown("### ✅ Design Checks")
        max_dc = 0.5 * tray_spacing * 1000   # 50% of tray spacing in mm
        checks_list = [
            ("Flooding fraction",        flood_frac,          0.60, 0.82,     "Should be 60–82%",            True),
            ("Downcomer backup / spacing",h_dc_backup/1000/tray_spacing, 0.0, 0.50,"< 50% of tray spacing",  True),
            ("Weeping (u_hole > u_weep)", u_hole,              u_weep, 999,    f"u_hole {u_hole:.2f} > u_weep {u_weep:.2f} m/s", u_hole > u_weep),
            ("Entrainment ψ",             psi,                 0.0, 0.10,     "< 10% recommended",           True),
            ("Turndown ratio",            turndown,            turndown_min[tray_type], 99, f"Min {turndown_min[tray_type]:.0f}:1 for {tray_type}", True),
            ("ΔP per tray",               dP_tray,             0.0, 1200,     "< 1200 Pa recommended",       True),
            ("Weir height / spacing",     weir_h_mm/1000/tray_spacing, 0.05, 0.20, "5–20% of tray spacing",  True),
        ]

        for label, val, lo, hi, note, use_range in checks_list:
            if use_range:
                ok = lo <= val <= hi
            else:
                ok = val  # boolean
            color = "#22c55e" if ok else "#f59e0b"
            icon  = "✅" if ok else "⚠️"
            st.markdown(f"""
            <div class="tray-check-row" style="border-color:{color}88;">
              <span class="tray-check-label">{icon} {label}</span>
              <span class="tray-check-value" style="color:{color};">{val:.3f} — {note}</span>
            </div>""", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════
    # TAB 3 — Performance Curves
    # ═══════════════════════════════════════════════════
    with tab3:
        st.markdown("### 📊 Tray Performance Envelope")

        # Flooding curve vs throughput
        load_range = np.linspace(0.3, 1.2, 80)
        u_hole_range = u_hole * load_range
        h_dry_range  = C_dry * u_hole_range**2 * rho_V / rho_L
        dP_range     = (h_dry_range + h_weir) * rho_L * 9.81 / 1000

        fig = go.Figure()

        # ΔP vs load
        fig.add_trace(go.Scatter(
            x=load_range * 100, y=dP_range, mode="lines",
            name="ΔP/tray [Pa]", line=dict(color="#00b4d8", width=3.2)))

        # Weep limit
        fig.add_hline(y=h_weir * rho_L * 9.81 / 1000,
                       line_dash="dot", line_color="#ef4444", line_width=3,
                       annotation_text="Weep limit", annotation_font_color="#ef4444")

        # Design point
        fig.add_vline(x=100, line_dash="dot", line_color="#f59e0b", line_width=3,
                       annotation_text="Design (100%)", annotation_font_color="#f59e0b")

        # Flood limit
        fig.add_vline(x=flood_frac * 100, line_dash="dash", line_color="#a855f7", line_width=3,
                       annotation_text=f"Flood ({flood_frac*100:.0f}%)",
                       annotation_font_color="#a855f7")

        fig.update_layout(
            template="plotly_dark", paper_bgcolor="#0a0e14", plot_bgcolor="#111827",
            font=dict(family="Barlow", color="#e2e8f0"),
            xaxis=dict(title="Vapour Load [% of design]", gridcolor="#1e3a5f"),
            yaxis=dict(title="ΔP per tray [Pa]", gridcolor="#1e3a5f"),
            height=360, margin=dict(t=20))
        st.plotly_chart(fig, use_container_width=True)

        # E_o sensitivity vs α·μ_L
        st.markdown("### O'Connell Efficiency — Sensitivity")
        am_range = np.logspace(-1, 1, 100)
        eo_range = np.clip(51 - 32.5 * np.log10(am_range), 20, 95)

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=am_range, y=eo_range, mode="lines",
            line=dict(color="#22c55e", width=3.2), name="E_o"))
        fig2.add_vline(x=alpha_mu, line_dash="dot", line_color="#f59e0b", line_width=3,
                        annotation_text=f"Your system: α·μ={alpha_mu:.3f}, E_o={E_o*100:.1f}%",
                        annotation_font_color="#f59e0b")
        fig2.update_layout(
            template="plotly_dark", paper_bgcolor="#0a0e14", plot_bgcolor="#111827",
            font=dict(family="Barlow", color="#e2e8f0"),
            xaxis=dict(title="α × μ_L", gridcolor="#1e3a5f", type="log"),
            yaxis=dict(title="Overall Tray Efficiency E_o [%]", gridcolor="#1e3a5f"),
            height=320, margin=dict(t=20))
        st.plotly_chart(fig2, use_container_width=True)

    # ═══════════════════════════════════════════════════
    # TAB 4 — Summary & Checks
    # ═══════════════════════════════════════════════════
    with tab4:
        dP_total     = N_actual_trays * dP_tray
        dP_total_mmHg = dP_total / 133.322
        col_h = N_actual_trays * tray_spacing + 1.5 + 2.0  # active + top + sump

        st.markdown("### 📋 Complete Tray Design Summary")
        summary = {
            "Tray type":                    tray_type,
            "N_theoretical (Gilliland)":    f"{N_theor}",
            "O'Connell E_o":                f"{E_o*100:.1f}% (α·μ_L = {alpha_mu:.3f})",
            "N_actual trays":               f"{N_actual_trays}",
            "Tray spacing":                 f"{tray_spacing} m",
            "Active column height":         f"{N_actual_trays * tray_spacing:.2f} m",
            "Weir height":                  f"{weir_h_mm} mm",
            "Hole diameter":                f"{hole_dia_mm} mm",
            "A_total / A_active / A_dc":    f"{A_total:.3f} / {A_active:.3f} / {A_dc:.3f} m²",
            "Number of holes":              f"{n_holes:,}",
            "u_hole":                       f"{u_hole:.3f} m/s",
            "u_flood / u_op":               f"{u_flood:.3f} / {u_op:.3f} m/s",
            "Flooding fraction":            f"{flood_frac*100:.0f}%",
            "h_dry":                        f"{h_dry:.2f} mm liq",
            "h_weir (Francis)":             f"{h_weir:.2f} mm liq",
            "Downcomer backup":             f"{h_dc_backup:.2f} mm liq ({h_dc_backup/1000/tray_spacing*100:.1f}% of spacing)",
            "ΔP per tray":                  f"{dP_tray:.1f} Pa",
            "ΔP total column":              f"{dP_total:.0f} Pa ({dP_total_mmHg:.1f} mmHg)",
            "FLV (flow parameter)":         f"{FLV:.4f}",
            "Entrainment ψ":                f"{psi*100:.2f}%",
            "u_weep":                       f"{u_weep:.3f} m/s",
            "Turndown ratio":               f"{turndown:.2f}:1 (min {turndown_min[tray_type]:.0f}:1)",
            "Weeping check":                f"{'✅ OK' if u_hole > u_weep else '⚠️ RISK'}",
        }
        df = pd.DataFrame({
            "Parameter": list(summary.keys()),
            "Value":     list(summary.values())
        })
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.markdown(f"""
        <div class="success-panel">
        ✅ <b>Tray Design Complete:</b>
        {tray_type} | N_theoretical = {N_theor} |
        E_o = {E_o*100:.1f}% (O'Connell) |
        N_actual = <b>{N_actual_trays} trays</b> |
        ΔP_total = {dP_total_mmHg:.1f} mmHg
        </div>
        """, unsafe_allow_html=True)

    # ── Save ──────────────────────────────────────────────────────────
    st.markdown("<div class='eng-divider'></div>", unsafe_allow_html=True)
    if st.button("💾 Save Tray Design", type="primary"):
        st.session_state["tray_design"] = {
            "tray_type":          tray_type,
            "tray_spacing":       tray_spacing,
            "tray_spacing_m":     tray_spacing,
            "weir_height_mm":     weir_h_mm,
            "hole_dia_mm":        hole_dia_mm,
            "flood_frac":         flood_frac,
            "E_o":                round(E_o, 4),
            "E_overall":          round(E_o, 4),
            "tray_efficiency":    round(E_o, 4),
            "N_theoretical":      N_theor,
            "N_actual_trays":     N_actual_trays,
            "alpha_mu":           round(alpha_mu, 4),
            "u_hole":             round(u_hole, 4),
            "u_flood":            round(u_flood, 4),
            "u_op":               round(u_op, 4),
            "u_weep":             round(u_weep, 4),
            "h_dry_mm":           round(h_dry, 3),
            "h_weir_mm":          round(h_weir, 3),
            "h_dc_backup_mm":     round(h_dc_backup, 3),
            "dP_tray_Pa":         round(dP_tray, 2),
            "dP_total_Pa":        round(N_actual_trays * dP_tray, 1),
            "dP_total_mmHg":      round(N_actual_trays * dP_tray / 133.322, 2),
            "FLV":                round(FLV, 5),
            "entrainment_psi":    round(psi, 5),
            "turndown_ratio":     round(turndown, 2),
            "weeping_ok":         bool(u_hole > u_weep),
            "A_active":           round(A_active, 4),
            "A_dc":               round(A_dc, 4),
            "n_holes":            n_holes,
            "D_col":              D_col,
        }
        st.success(
            f"✅ Tray design saved! "
            f"E_o = {E_o*100:.1f}%, N_actual = {N_actual_trays} trays, "
            f"ΔP = {N_actual_trays * dP_tray / 133.322:.1f} mmHg. "
            f"Proceed to 📐 Column Diameter → 📏 Column Height."
        )
