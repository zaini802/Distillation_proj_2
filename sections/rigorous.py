"""pages/rigorous.py — Rigorous Column Design (Stage-by-Stage)"""
import streamlit as st
import numpy as np
import plotly.graph_objects as go
from thermodynamics.thermo_engine import y_from_x, x_from_y, antoine_pvap, COMPONENT_DB
from sections.phase3_style import render_phase3_style

def render():
    st.markdown("""
    <div class="section-header">
        <h1>🔬 Rigorous Column Design</h1>
        <p>Stage-by-stage mass & energy balance. Temperature, composition, and flow profiles.</p>
    </div>
    """, unsafe_allow_html=True)

    render_phase3_style()

    feed     = st.session_state.get("feed", {})
    shortcut = st.session_state.get("shortcut", {})
    mccabe   = st.session_state.get("mccabe", {})

    if not feed or not shortcut:
        st.warning("⚠️ Complete **Feed Specifications** and **Shortcut Design** first.")
        return

    x_D    = feed["x_D"];  x_B = feed["x_B"];  z_F = feed["z_F"]
    F      = feed["F"];    light = feed["light"]; heavy = feed["heavy"]
    P_mmHg = feed["P_col_mmHg"]
    alpha  = shortcut.get("alpha", 2.5)
    R      = shortcut.get("R", 2.0)
    N      = shortcut.get("N_actual_int", 15)
    N_feed = shortcut.get("feed_tray", int(N * 0.4))
    D_flow = shortcut.get("D", F * 0.5)
    B_flow = shortcut.get("B", F * 0.5)

    tab1, tab2, tab3 = st.tabs(["📊 Stage Profiles", "⚖️ Mass & Energy Balance", "🌡️ Temperature Profile"])

    # ── Stage-by-stage calculation ────────────────────────────
    V = (R + 1) * D_flow   # vapour flow [kmol/h] rectifying
    L = R * D_flow          # liquid flow [kmol/h] rectifying
    q = shortcut.get("q", 1.0)
    V_prime = V - (1 - q) * F
    L_prime = L + q * F

    # Stage compositions
    x_stages = np.zeros(N + 1)
    y_stages = np.zeros(N + 1)
    x_stages[0] = x_D
    y_stages[0] = x_D

    for i in range(1, N + 1):
        # Equilibrium
        x_stages[i] = x_from_y(y_stages[i-1], alpha)
        # Operating line (switch at feed)
        if i <= N_feed:
            y_stages[i] = (L / V) * x_stages[i] + x_D / (R + 1)
        else:
            y_stages[i] = (L_prime / V_prime) * x_stages[i] - (B_flow / V_prime) * x_B
        y_stages[i] = max(x_B, min(x_D, y_stages[i]))
        if x_stages[i] <= x_B:
            break

    # Temperature profile (interpolate between boiling points)
    Tb_light = COMPONENT_DB.get(light, {}).get("Tb", 80)
    Tb_heavy = COMPONENT_DB.get(heavy, {}).get("Tb", 110)
    T_stages = []
    for i in range(N + 1):
        x  = max(0.0, min(1.0, x_stages[i]))
        Tb = x * Tb_light + (1 - x) * Tb_heavy
        T_stages.append(round(Tb, 2))

    # Flow profiles
    V_profile = [V if i <= N_feed else V_prime for i in range(N+1)]
    L_profile = [L if i <= N_feed else L_prime for i in range(N+1)]

    with tab1:
        st.markdown("### Composition Profile — Stage by Stage")
        stage_nos = list(range(N + 1))
        final_stage_x = x_stages[min(N, len(x_stages) - 1)]
        separation_margin = final_stage_x - x_B

        st.markdown(f"""
        <div class="formula-box" style="border-left:4px solid #00b4d8;">
          <div class="formula-title">Stage-by-stage calculation basis</div>
          <b>Equilibrium relation:</b> y = αx/[1+(α−1)x], using α = <b>{alpha:.4f}</b><br>
          <b>Rectifying line:</b> y = (L/V)x + x<sub>D</sub>/(R+1), with L = {L:.2f}, V = {V:.2f} kmol/h<br>
          <b>Stripping line:</b> y = (L'/V')x − (B/V')x<sub>B</sub>, with L' = {L_prime:.2f}, V' = {V_prime:.2f} kmol/h<br>
          <div class="phase3-calc-separator"></div>
          <b>Target check:</b> final liquid x = {final_stage_x:.5f}, target x<sub>B</sub> = {x_B:.5f},
          margin = <b>{separation_margin:.5f}</b>
        </div>
        """, unsafe_allow_html=True)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=stage_nos, y=list(x_stages[:N+1]),
                                  mode="lines+markers", name="x (liquid)",
                                  line=dict(color="#00b4d8", width=3.2),
                                  marker=dict(size=7, color="#00d4ff", line=dict(color="#f8fbff", width=1))))
        fig.add_trace(go.Scatter(x=stage_nos, y=list(y_stages[:N+1]),
                                  mode="lines+markers", name="y (vapour)",
                                  line=dict(color="#22c55e", width=3.2),
                                  marker=dict(size=7, color="#22c55e", line=dict(color="#f8fbff", width=1))))
        fig.add_vline(x=N_feed, line_dash="dash", line_color="#f59e0b", line_width=3,
                      annotation_text=f"Feed Stage {N_feed}")
        fig.add_hline(y=z_F, line_dash="dot", line_color="#c084fc", line_width=3,
                      annotation_text=f"zF={z_F}")
        fig.update_layout(
            template="plotly_dark", paper_bgcolor="#0a0e14", plot_bgcolor="#111827",
            font=dict(color="#e2e8f0"), height=430,
            title=dict(text="Liquid/Vapour Composition Profiles",
                       font=dict(color="#f8d477", size=19)),
            xaxis=dict(title="Stage Number (from top)", gridcolor="#1e3a5f"),
            yaxis=dict(title="Mole Fraction (light component)", gridcolor="#1e3a5f"),
            legend=dict(bgcolor="#111827"), margin=dict(t=20)
        )
        st.plotly_chart(fig, use_container_width=True)

        # Stage table
        with st.expander("📋 Stage-by-Stage Data Table"):
            import pandas as pd
            df_stages = pd.DataFrame({
                "Stage": stage_nos,
                "x (liquid)": [round(x, 5) for x in x_stages[:N+1]],
                "y (vapour)": [round(y, 5) for y in y_stages[:N+1]],
                "T [°C]":     T_stages[:N+1],
                "V [kmol/h]": [round(v, 2) for v in V_profile],
                "L [kmol/h]": [round(l, 2) for l in L_profile],
                "Section":    ["Rectifying" if i <= N_feed else "Stripping" for i in stage_nos]
            })
            st.dataframe(df_stages, use_container_width=True, hide_index=True)

    with tab2:
        st.markdown("### ⚖️ Overall Mass & Energy Balance")

        # Material balance
        D_check = F * (z_F - x_B) / (x_D - x_B)
        B_check = F - D_check

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            <div class="formula-box">
              <div class="formula-title">Overall Balance</div>
              F = D + B<br>
              F·z_F = D·x_D + B·x_B
            </div>""", unsafe_allow_html=True)
            m1,m2,m3 = st.columns(3)
            m1.metric("Feed F", f"{F:.2f} kmol/h")
            m2.metric("Distillate D", f"{D_check:.3f} kmol/h")
            m3.metric("Bottoms B", f"{B_check:.3f} kmol/h")

        with c2:
            st.markdown("""
            <div class="formula-box">
              <div class="formula-title">Internal Flows</div>
              L = R·D  (rectifying)<br>
              V = (R+1)·D<br>
              L' = L + q·F  (stripping)<br>
              V' = V - (1-q)·F
            </div>""", unsafe_allow_html=True)
            m1,m2,m3,m4 = st.columns(4)
            m1.metric("V (rect.)", f"{V:.2f}")
            m2.metric("L (rect.)", f"{L:.2f}")
            m3.metric("V' (strip.)", f"{V_prime:.2f}")
            m4.metric("L' (strip.)", f"{L_prime:.2f}")

        # Flow profile chart
        st.markdown("### Internal Flow Profiles")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=stage_nos, y=V_profile, mode="lines",
                                   name="Vapour V [kmol/h]",
                                   line=dict(color="#00b4d8", width=3.2)))
        fig2.add_trace(go.Scatter(x=stage_nos, y=L_profile, mode="lines",
                                   name="Liquid L [kmol/h]",
                                   line=dict(color="#f59e0b", width=3.2)))
        fig2.add_vline(x=N_feed, line_dash="dash", line_color="#ef4444", line_width=3,
                       annotation_text="Feed Stage")
        fig2.update_layout(
            template="plotly_dark", paper_bgcolor="#0a0e14", plot_bgcolor="#111827",
            font=dict(color="#e2e8f0"), height=370,
            title=dict(text="Internal Flow Profiles", font=dict(color="#f8d477", size=19)),
            xaxis=dict(title="Stage Number", gridcolor="#1e3a5f"),
            yaxis=dict(title="Flow Rate [kmol/h]", gridcolor="#1e3a5f"),
            margin=dict(t=20)
        )
        st.plotly_chart(fig2, use_container_width=True)

        # Energy balance (quick estimate)
        lambda_vap = st.number_input("Latent Heat λ [J/mol]", 20000.0, 50000.0, 32000.0, 1000.0)
        Q_reb  = V_prime * 1000 * lambda_vap / 3600 / 1000  # kW
        Q_cond = V       * 1000 * lambda_vap / 3600 / 1000  # kW

        st.markdown(f"""
        <div class="success-panel">
        ⚡ <strong>Energy Balance Summary:</strong><br>
        Reboiler Duty Q_reb ≈ <strong>{Q_reb:.1f} kW</strong>
        &nbsp;&nbsp;|&nbsp;&nbsp;
        Condenser Duty Q_cond ≈ <strong>{Q_cond:.1f} kW</strong>
        </div>""", unsafe_allow_html=True)

    with tab3:
        st.markdown("### 🌡️ Temperature Profile")
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=stage_nos, y=T_stages[:N+1],
                                   mode="lines+markers", name="Stage Temperature",
                                   line=dict(color="#ef4444", width=3.2),
                                   marker=dict(size=7, color="#f59e0b", line=dict(color="#f8fbff", width=1))))
        fig3.add_vline(x=N_feed, line_dash="dash", line_color="#00b4d8", line_width=3,
                       annotation_text=f"Feed Stage {N_feed}")
        fig3.update_layout(
            template="plotly_dark", paper_bgcolor="#0a0e14", plot_bgcolor="#111827",
            font=dict(color="#e2e8f0"), height=410,
            title=dict(text="Temperature Profile", font=dict(color="#f8d477", size=19)),
            xaxis=dict(title="Stage Number (Top → Bottom)", gridcolor="#1e3a5f"),
            yaxis=dict(title="Temperature [°C]", gridcolor="#1e3a5f"),
            margin=dict(t=20)
        )
        st.plotly_chart(fig3, use_container_width=True)

        st.markdown(f"""
        <div class="info-panel">
        📌 <strong>Temperature Range:</strong>
        Top = <strong>{T_stages[0]:.1f} °C</strong> (distillate) →
        Bottom = <strong>{T_stages[min(N, len(T_stages)-1)]:.1f} °C</strong> (bottoms)
        </div>""", unsafe_allow_html=True)

    if st.button("💾 Save Rigorous Results", type="primary"):
        st.session_state["rigorous"] = {
            "x_stages": list(x_stages[:N+1]),
            "y_stages": list(y_stages[:N+1]),
            "T_stages": T_stages[:N+1],
            "V_rect": V, "L_rect": L,
            "V_strip": V_prime, "L_strip": L_prime,
            "Q_reb_kW": round(Q_reb, 2),
            "Q_cond_kW": round(Q_cond, 2),
        }
        st.success("✅ Rigorous design results saved!")
