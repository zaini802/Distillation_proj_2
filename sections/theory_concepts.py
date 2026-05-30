"""sections/theory_concepts.py - Distillation theory handbook with Groq Q&A."""
import html
import os

import streamlit as st

from sections.ai_assistant import _call_groq_chat, _drop_stale_groq_install_errors
from sections.phase3_style import render_phase3_style


def render():
    render_phase3_style()
    _render_theory_style()

    st.markdown(
        """
        <div class="section-header">
            <h1>Theoretical Concepts</h1>
            <p>Core distillation theory, equations, column hardware, operating problems,
            and Groq-powered concept Q&A in one learning section.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    context = _current_design_context()
    st.markdown(_design_snapshot(context), unsafe_allow_html=True)

    tabs = st.tabs(
        [
            "Fundamentals",
            "VLE & Thermodynamics",
            "Design Methods",
            "Column Hardware",
            "Operation & Troubleshooting",
            "Ask Groq AI",
        ]
    )

    with tabs[0]:
        _render_fundamentals()

    with tabs[1]:
        _render_vle_theory()

    with tabs[2]:
        _render_design_methods()

    with tabs[3]:
        _render_column_hardware()

    with tabs[4]:
        _render_operation_troubleshooting()

    with tabs[5]:
        _render_groq_theory(context)


def _current_design_context():
    feed = st.session_state.get("feed", {})
    thermo = st.session_state.get("thermo", {})
    shortcut = st.session_state.get("shortcut", {})
    column_type = st.session_state.get("column_type", None)
    diameter = st.session_state.get("diameter", {})
    height = st.session_state.get("height", {})

    return {
        "system": f"{feed.get('light', 'Light')} / {feed.get('heavy', 'Heavy')}" if feed else "Not selected",
        "feed": feed,
        "thermo": thermo,
        "shortcut": shortcut,
        "column_type": column_type or "Not selected",
        "diameter": diameter,
        "height": height,
    }


def _design_snapshot(ctx):
    feed = ctx["feed"]
    shortcut = ctx["shortcut"]
    thermo = ctx["thermo"]
    diameter = ctx["diameter"]
    height = ctx["height"]
    metrics = [
        ("Current system", ctx["system"], "binary pair"),
        ("Column type", str(ctx["column_type"]).title(), "tray / packed"),
        ("Feed basis", _fmt(feed.get("F"), " kmol/h"), "F"),
        ("Purity targets", _purity_text(feed), "xD / xB"),
        ("Relative volatility", _fmt(shortcut.get("alpha", thermo.get("alpha_avg")), ""), "alpha"),
        ("Reflux ratio", _fmt(shortcut.get("R"), ""), "R"),
        ("Theoretical stages", _fmt(st.session_state.get("mccabe", {}).get("n_stages", shortcut.get("N_actual")), ""), "N"),
        ("Column size", _size_text(diameter, height), "D / H"),
    ]
    return _metric_grid(metrics)


def _render_fundamentals():
    st.markdown("### Distillation Fundamentals")
    st.markdown(
        _callout(
            "Main idea",
            "Distillation separates a liquid mixture because the more volatile component enters the vapour phase more easily. "
            "Repeated vapour-liquid contact inside the column enriches the top product in light component and the bottom product in heavy component.",
            "green",
        ),
        unsafe_allow_html=True,
    )

    st.markdown(
        _concept_grid(
            [
                (
                    "Volatility",
                    "A component with higher vapour pressure is more volatile and concentrates in the vapour phase.",
                ),
                (
                    "Equilibrium stage",
                    "A theoretical contact where leaving vapour and liquid are assumed to be in VLE equilibrium.",
                ),
                (
                    "Rectifying section",
                    "Column region above feed tray; vapour is enriched by contact with reflux liquid.",
                ),
                (
                    "Stripping section",
                    "Column region below feed tray; rising vapour strips light component from descending liquid.",
                ),
                (
                    "Reflux",
                    "Condensed distillate returned to the column to improve separation at the cost of energy.",
                ),
                (
                    "Reboil",
                    "Heat added at bottom to generate vapour traffic and drive separation.",
                ),
            ]
        ),
        unsafe_allow_html=True,
    )

    st.markdown("### Basic Material Balance")
    st.markdown(
        _formula_steps(
            "Binary column balance",
            [
                ("Overall balance", "F = D + B"),
                ("Light component balance", "F zF = D xD + B xB"),
                ("Distillate flow", "D = F (zF - xB) / (xD - xB)"),
                ("Bottoms flow", "B = F - D"),
            ],
            "These balances define product flow rates before tray count, diameter, heat duty, or economics are calculated.",
        ),
        unsafe_allow_html=True,
    )

    st.markdown("### Key Variables")
    st.markdown(
        _table_html(
            [
                ("F", "Feed molar flow rate", "kmol/h"),
                ("zF", "Feed mole fraction of light component", "dimensionless"),
                ("xD", "Distillate mole fraction of light component", "dimensionless"),
                ("xB", "Bottoms mole fraction of light component", "dimensionless"),
                ("alpha", "Relative volatility", "separation difficulty indicator"),
                ("R", "Reflux ratio L/D", "energy-separation tradeoff"),
                ("q", "Thermal condition of feed", "q-line slope basis"),
                ("N", "Theoretical stages", "ideal equilibrium stages"),
            ]
        ),
        unsafe_allow_html=True,
    )


def _render_vle_theory():
    st.markdown("### Vapour-Liquid Equilibrium")
    st.markdown(
        _callout(
            "Why VLE matters",
            "The VLE curve tells how much light component appears in vapour for each liquid composition. "
            "If the equilibrium curve is close to the diagonal y = x, separation is difficult and more stages or reflux are required.",
            "cyan",
        ),
        unsafe_allow_html=True,
    )

    st.markdown(
        _formula_steps(
            "Relative volatility model",
            [
                ("Relative volatility", "alpha = (y1/x1) / (y2/x2)"),
                ("Binary equilibrium", "y = alpha x / [1 + (alpha - 1)x]"),
                ("Interpretation", "alpha >> 1 means easy separation; alpha close to 1 means difficult separation."),
            ],
            "This is the common working model used in shortcut and McCabe-Thiele design when detailed activity-coefficient data are not available.",
        ),
        unsafe_allow_html=True,
    )

    st.markdown(
        _concept_grid(
            [
                ("Raoult's Law", "Best for nearly ideal, non-polar, similar-boiling systems at low pressure."),
                ("Modified Raoult's Law", "Adds activity coefficient gamma for liquid non-ideality."),
                ("Wilson Model", "Useful for miscible polar liquid systems such as alcohol-water pairs."),
                ("NRTL Model", "Strong option for highly non-ideal aqueous or partially miscible systems."),
                ("Bubble point", "Temperature where first vapour bubble forms from liquid at given pressure."),
                ("Dew point", "Temperature where first liquid drop forms from vapour at given pressure."),
            ]
        ),
        unsafe_allow_html=True,
    )

    st.markdown("### Azeotrope Concept")
    st.markdown(
        _callout(
            "Important warning",
            "At an azeotrope, vapour and liquid compositions become equal at a specific composition. "
            "Conventional distillation cannot cross that composition without pressure-swing, entrainer, extractive, or azeotropic distillation.",
            "red",
        ),
        unsafe_allow_html=True,
    )


def _render_design_methods():
    st.markdown("### Shortcut And Graphical Design")
    st.markdown(
        _concept_grid(
            [
                (
                    "Fenske equation",
                    "Gives minimum stages at total reflux. It represents the best possible separation with infinite reflux.",
                ),
                (
                    "Underwood equation",
                    "Gives minimum reflux ratio. It represents the least reflux that can theoretically make the split.",
                ),
                (
                    "Gilliland correlation",
                    "Connects actual reflux ratio to actual stage count between Fenske and Underwood limits.",
                ),
                (
                    "Kirkbride correlation",
                    "Estimates feed tray location by splitting stages above and below the feed.",
                ),
                (
                    "McCabe-Thiele method",
                    "Graphical stage stepping using equilibrium curve, operating lines, q-line, and product specifications.",
                ),
                (
                    "Rigorous simulation",
                    "Solves MESH equations: material, equilibrium, summation, and heat balance for each stage.",
                ),
            ]
        ),
        unsafe_allow_html=True,
    )

    st.markdown("### Core Equations")
    st.markdown(
        _formula_steps(
            "Shortcut design sequence",
            [
                ("Fenske", "Nmin = log[(xD/xB)((1 - xB)/(1 - xD))] / log(alpha)"),
                ("Underwood", "sum(q zi / (alpha_i - theta)) = 1"),
                ("Gilliland", "Y = (N - Nmin)/(N + 1), X = (R - Rmin)/(R + 1)"),
                ("Efficiency correction", "Nactual = Ntheoretical / tray efficiency"),
                ("Packed height", "Packed height = Ntheoretical x HETP"),
            ],
            "The app follows this logic before moving into tray/packed sizing, heat duties, hydraulics, and mechanical checks.",
        ),
        unsafe_allow_html=True,
    )

    st.markdown("### Reflux Ratio Tradeoff")
    st.markdown(
        _callout(
            "Design judgement",
            "Low reflux saves condenser/reboiler duty but needs more stages and taller column. "
            "High reflux reduces stages but increases energy, vapour traffic, diameter, condenser area, and reboiler load.",
            "gold",
        ),
        unsafe_allow_html=True,
    )


def _render_column_hardware():
    st.markdown("### Distillation Column Hardware")
    st.markdown(
        _concept_grid(
            [
                ("Column shell", "Pressure vessel containing trays or packing, designed for pressure, temperature, wind, and corrosion."),
                ("Condenser", "Removes heat from overhead vapour and creates distillate plus reflux."),
                ("Reflux drum", "Holds condensed overhead liquid and splits it between reflux and product."),
                ("Reboiler", "Adds heat at the bottom and generates rising vapour."),
                ("Tray deck", "Provides staged vapour-liquid contact through valves, sieve holes, or bubble caps."),
                ("Downcomer", "Carries liquid from one tray to the tray below while preventing vapour bypass."),
                ("Packing", "Creates large interfacial area for continuous vapour-liquid contact with lower pressure drop."),
                ("Liquid distributor", "Spreads liquid evenly over packing to avoid maldistribution."),
            ]
        ),
        unsafe_allow_html=True,
    )

    st.markdown("### Tray vs Packed Column")
    st.markdown(
        _table_html(
            [
                ("Tray column", "High liquid load, fouling tolerance, easier sampling", "Higher pressure drop; discrete stages"),
                ("Packed column", "Low pressure drop, vacuum service, corrosive service", "Needs good distributors; sensitive to maldistribution"),
                ("Sieve tray", "Simple, cheap, high capacity", "Can weep at low vapour rate"),
                ("Valve tray", "Flexible operating range", "More expensive than sieve tray"),
                ("Structured packing", "High efficiency and low pressure drop", "Costly and needs careful installation"),
                ("Random packing", "Economical and flexible", "Lower efficiency than structured packing"),
            ]
        ),
        unsafe_allow_html=True,
    )


def _render_operation_troubleshooting():
    st.markdown("### Hydraulics And Operating Problems")
    st.markdown(
        _table_html(
            [
                ("Flooding", "Vapour or liquid traffic too high; liquid backs up", "Reduce feed/reboil, increase diameter, improve internals"),
                ("Weeping", "Vapour rate too low; liquid leaks through tray holes", "Increase boil-up or use valve trays"),
                ("Entrainment", "Liquid droplets carried upward with vapour", "Reduce vapour velocity, increase tray spacing"),
                ("Foaming", "Stable foam blocks contact area", "Use antifoam, reduce contaminants, lower vapour rate"),
                ("High pressure drop", "Excess vapour load, fouling, flooding, damaged internals", "Inspect internals and reduce hydraulic load"),
                ("Poor separation", "Low reflux, wrong feed tray, poor VLE model, tray damage", "Check R, feed stage, alpha, and column hydraulics"),
                ("Packing maldistribution", "Uneven liquid flow through packed bed", "Improve distributors and redistributors"),
                ("Condenser limitation", "Not enough cooling or area", "Increase cooling duty or revise exchanger design"),
            ]
        ),
        unsafe_allow_html=True,
    )

    st.markdown("### Operator's Mental Model")
    st.markdown(
        _formula_steps(
            "What changes when controls move",
            [
                ("Increase reflux R", "Top purity usually improves, condenser/reboiler duty increases, flooding risk may rise."),
                ("Increase reboiler duty", "Vapour traffic increases, stripping improves, flooding/entrainment risk may rise."),
                ("Feed too high above optimum", "Rectifying section overloaded; bottom product may go off-spec."),
                ("Feed too low below optimum", "Stripping section overloaded; top product may go off-spec."),
                ("Pressure increase", "Relative volatility usually decreases, separation becomes harder."),
            ],
            "Industrial operation is a balance between purity, capacity, energy, pressure drop, and hydraulic stability.",
        ),
        unsafe_allow_html=True,
    )


def _render_groq_theory(context):
    _drop_stale_groq_install_errors("theory_ai_history")
    st.markdown("### Ask Groq AI About Distillation Theory")
    st.markdown(
        _callout(
            "Ask anything",
            "Use this panel for concept explanations, equations, troubleshooting, viva preparation, design reasoning, and how your current design values connect to theory.",
            "green",
        ),
        unsafe_allow_html=True,
    )

    api_key = st.session_state.get("groq_api_key", "") or os.environ.get("GROQ_API_KEY", "")
    with st.expander("Groq API Key", expanded=not bool(api_key)):
        key = st.text_input(
            "Groq API Key",
            value=st.session_state.get("groq_api_key", ""),
            type="password",
            placeholder="gsk_xxxxxxxxxxxx",
            key="theory_groq_key",
        )
        if key:
            st.session_state["groq_api_key"] = key
            api_key = key
            st.success("Groq key saved.")

    quick = [
        "Explain distillation from zero level",
        "Explain relative volatility with example",
        "Why does reflux improve separation?",
        "Difference between tray and packed columns",
        "Explain flooding, weeping, and entrainment",
        "How McCabe-Thiele stages are counted",
        "Explain Fenske Underwood Gilliland sequence",
        "Why azeotropes cannot be crossed",
    ]
    st.markdown('<div class="theory-subtitle">Quick theory questions</div>', unsafe_allow_html=True)
    cols = st.columns(4)
    for i, question in enumerate(quick):
        with cols[i % 4]:
            if st.button(question, key=f"theory_quick_{i}", use_container_width=True):
                _send_theory_question(question, context, api_key)
                st.rerun()

    st.markdown('<div class="theory-chat-wrap">', unsafe_allow_html=True)
    history = st.session_state.get("theory_ai_history", [])
    if not history:
        st.markdown(
            """
            <div class="theory-empty">
                <b>Groq theory assistant is ready.</b><br>
                Ask a distillation concept question or select a quick question above.
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        for msg in history[-10:]:
            role = "user" if msg["role"] == "user" else "assistant"
            safe = html.escape(msg["content"]).replace("\n", "<br>")
            prefix = "You" if role == "user" else "Groq AI"
            st.markdown(
                f'<div class="theory-msg theory-{role}"><span>{prefix}</span>{safe}</div>',
                unsafe_allow_html=True,
            )
    st.markdown("</div>", unsafe_allow_html=True)

    c1, c2 = st.columns([5, 1])
    with c1:
        question = st.text_area(
            "Ask any distillation theory question",
            placeholder="Example: Why does increasing column pressure reduce relative volatility?",
            key="theory_ai_input",
            height=92,
        )
    with c2:
        st.write("")
        st.write("")
        send = st.button("Ask Groq", use_container_width=True)

    if send and question.strip():
        _send_theory_question(question.strip(), context, api_key)
        st.rerun()

    if history and st.button("Clear theory chat"):
        st.session_state["theory_ai_history"] = []
        st.rerun()


def _send_theory_question(question, context, api_key):
    if "theory_ai_history" not in st.session_state:
        st.session_state["theory_ai_history"] = []

    if not api_key:
        st.warning("Enter your Groq API key in the sidebar or in this section first.")
        return

    previous_history = list(st.session_state["theory_ai_history"])
    st.session_state["theory_ai_history"].append({"role": "user", "content": question})
    with st.spinner("Groq is explaining the concept..."):
        answer = _groq_theory_answer(question, context, api_key, previous_history)
    st.session_state["theory_ai_history"].append({"role": "assistant", "content": answer})


def _groq_theory_answer(question, context, api_key, previous_history):
    feed = context.get("feed", {})
    thermo = context.get("thermo", {})
    shortcut = context.get("shortcut", {})
    diameter = context.get("diameter", {})
    height = context.get("height", {})

    system_prompt = f"""You are DistillAI Theory Tutor, an expert chemical engineering teacher.
Explain distillation theory clearly for a student-engineer and connect theory to industrial design.

Current design context:
- System: {context.get('system', 'Not selected')}
- Column type: {context.get('column_type', 'Not selected')}
- Feed: F={feed.get('F', 'N/A')} kmol/h, zF={feed.get('z_F', 'N/A')}, xD={feed.get('x_D', 'N/A')}, xB={feed.get('x_B', 'N/A')}
- Thermodynamics: alpha={thermo.get('alpha_avg', shortcut.get('alpha', 'N/A'))}
- Shortcut: R={shortcut.get('R', 'N/A')}, Rmin={shortcut.get('R_min', 'N/A')}, stages={shortcut.get('N_actual_int', shortcut.get('N_actual', 'N/A'))}
- Diameter={diameter.get('D_column_std_m', diameter.get('D_column_m', 'N/A'))} m, Height={height.get('total_height_m', 'N/A')} m

Rules:
- Keep the answer under 220 words unless the user asks for detail.
- Use simple language first, then the engineering equation/term.
- Mention industrial implication and common mistake where useful.
- Do not invent exact design data if missing.
"""

    messages = [{"role": "system", "content": system_prompt}]
    for msg in previous_history[-8:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": question})

    return _call_groq_chat(api_key, messages, temperature=0.35, max_tokens=420)


def _fmt(value, unit=""):
    if value in (None, "", "N/A"):
        return "N/A"
    try:
        number = float(value)
        if abs(number) >= 100:
            text = f"{number:.1f}"
        elif abs(number) >= 10:
            text = f"{number:.2f}"
        else:
            text = f"{number:.3f}"
        return f"{text}{unit}"
    except (TypeError, ValueError):
        return str(value)


def _purity_text(feed):
    if not feed:
        return "N/A"
    return f"{_fmt(feed.get('x_D'), '')} / {_fmt(feed.get('x_B'), '')}"


def _size_text(diameter, height):
    d = diameter.get("D_column_std_m", diameter.get("D_column_m"))
    h = height.get("total_height_m")
    if d is None and h is None:
        return "N/A"
    return f"{_fmt(d, ' m')} / {_fmt(h, ' m')}"


def _metric_grid(metrics):
    items = []
    for label, value, note in metrics:
        items.append(
            '<div class="theory-metric">'
            f'<div class="theory-metric-label">{html.escape(label)}</div>'
            f'<div class="theory-metric-value">{html.escape(str(value))}</div>'
            f'<div class="theory-metric-note">{html.escape(note)}</div>'
            '</div>'
        )
    return f'<div class="theory-metric-grid">{"".join(items)}</div>'


def _concept_grid(items):
    cards = []
    for title, body in items:
        cards.append(
            '<div class="theory-card">'
            f'<div class="theory-card-title">{html.escape(title)}</div>'
            f'<div class="theory-card-body">{html.escape(body)}</div>'
            '</div>'
        )
    return f'<div class="theory-grid">{"".join(cards)}</div>'


def _formula_steps(title, steps, result):
    rows = []
    for label, equation in steps:
        rows.append(
            '<div class="theory-formula-row">'
            f'<span class="theory-formula-label">{html.escape(label)}</span>'
            f'<span class="theory-formula-equation">{html.escape(equation)}</span>'
            '</div>'
        )
    return (
        '<div class="theory-formula-box">'
        f'<div class="theory-formula-title">{html.escape(title)}</div>'
        f'{"".join(rows)}'
        f'<div class="theory-formula-result">{html.escape(result)}</div>'
        '</div>'
    )


def _table_html(rows):
    body = []
    for c1, c2, c3 in rows:
        body.append(
            '<tr>'
            f'<td>{html.escape(c1)}</td>'
            f'<td>{html.escape(c2)}</td>'
            f'<td>{html.escape(c3)}</td>'
            '</tr>'
        )
    return (
        '<div class="theory-table-wrap">'
        '<table class="theory-table">'
        '<thead><tr><th>Concept</th><th>Meaning</th><th>Design note</th></tr></thead>'
        f'<tbody>{"".join(body)}</tbody>'
        '</table></div>'
    )


def _callout(title, body, tone):
    return (
        f'<div class="theory-callout theory-callout-{tone}">'
        f'<div class="theory-callout-title">{html.escape(title)}</div>'
        f'<div>{html.escape(body)}</div>'
        '</div>'
    )


def _render_theory_style():
    st.markdown(
        """
        <style>
        .theory-metric-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 12px;
            margin: 0 0 22px;
        }
        .theory-metric,
        .theory-card,
        .theory-formula-box,
        .theory-callout,
        .theory-table-wrap,
        .theory-chat-wrap {
            background: linear-gradient(135deg, rgba(8,14,24,.99), rgba(15,23,42,.96));
            border: 1px solid rgba(0,180,216,.38);
            border-radius: 8px;
            box-shadow: 0 12px 26px rgba(0,0,0,.16), inset 0 1px 0 rgba(255,255,255,.035);
        }
        .theory-metric {
            padding: 13px 14px;
            min-height: 108px;
            border-left: 4px solid #00b4d8;
        }
        .theory-metric-label,
        .theory-subtitle {
            color: #ff5b6e !important;
            font-weight: 900;
            letter-spacing: .2px;
            text-shadow: 0 0 10px rgba(239,68,68,.20);
        }
        .theory-metric-value {
            color: #00d4ff !important;
            font-family: 'Share Tech Mono', monospace;
            font-size: 1.22rem;
            font-weight: 900;
            margin: 7px 0 4px;
            overflow-wrap: anywhere;
        }
        .theory-metric-note {
            color: #dbeafe !important;
            font-weight: 800;
            font-size: .8rem;
        }
        .theory-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 12px;
            margin: 12px 0 20px;
        }
        .theory-card {
            padding: 16px 17px;
            border-left: 4px solid #22c55e;
            min-height: 136px;
        }
        .theory-card-title,
        .theory-formula-title,
        .theory-callout-title {
            color: #f8d477 !important;
            font-family: 'Barlow Condensed', sans-serif;
            font-size: 1.15rem;
            font-weight: 900;
            margin-bottom: 8px;
            text-shadow: 0 0 12px rgba(248,212,119,.18);
        }
        .theory-card-body,
        .theory-callout,
        .theory-formula-result {
            color: #eaf6ff !important;
            font-weight: 760;
            line-height: 1.58;
        }
        .theory-formula-box {
            padding: 15px 17px;
            border-left: 4px solid #00b4d8;
            margin: 12px 0 20px;
        }
        .theory-formula-row {
            display: grid;
            grid-template-columns: 220px 1fr;
            gap: 14px;
            padding: 8px 0;
            border-bottom: 1px dashed rgba(148,163,184,.24);
        }
        .theory-formula-label {
            color: #ff5b6e !important;
            font-weight: 900;
        }
        .theory-formula-equation {
            color: #f8fbff !important;
            font-family: 'Share Tech Mono', monospace;
            font-weight: 900;
            overflow-wrap: anywhere;
        }
        .theory-formula-result {
            color: #22c55e !important;
            margin-top: 11px;
            font-weight: 900;
        }
        .theory-callout {
            padding: 15px 17px;
            margin: 10px 0 18px;
            border-left-width: 5px;
        }
        .theory-callout-green { border-left-color: #22c55e; }
        .theory-callout-cyan { border-left-color: #00b4d8; }
        .theory-callout-red { border-left-color: #ff5b6e; }
        .theory-callout-gold { border-left-color: #f8d477; }
        .theory-table-wrap {
            overflow-x: auto;
            margin: 12px 0 20px;
            border-left: 4px solid #f8d477;
        }
        .theory-table {
            width: 100%;
            border-collapse: collapse;
            color: #f8fbff;
            font-weight: 760;
        }
        .theory-table th {
            color: #f8d477 !important;
            background: rgba(17,24,39,.92);
            text-align: left;
            padding: 12px 13px;
            font-weight: 900;
            border-bottom: 1px solid rgba(248,212,119,.28);
        }
        .theory-table td {
            padding: 11px 13px;
            border-bottom: 1px solid rgba(148,163,184,.14);
            vertical-align: top;
        }
        .theory-table td:first-child {
            color: #ff5b6e !important;
            font-weight: 900;
            white-space: nowrap;
        }
        .theory-table td:last-child {
            color: #dbeafe !important;
        }
        .theory-chat-wrap {
            padding: 14px;
            margin: 12px 0 14px;
            border-left: 4px solid #22c55e;
        }
        .theory-empty {
            text-align: center;
            color: #dbeafe;
            font-weight: 800;
            padding: 24px;
            line-height: 1.7;
        }
        .theory-empty b {
            color: #f8d477 !important;
            font-weight: 900;
        }
        .theory-msg {
            max-width: 86%;
            padding: 11px 13px;
            margin: 8px 0;
            color: #f8fbff;
            font-weight: 760;
            line-height: 1.55;
            border-radius: 8px;
        }
        .theory-msg span {
            display: block;
            color: #f8d477;
            font-weight: 900;
            margin-bottom: 5px;
        }
        .theory-user {
            margin-left: auto;
            background: linear-gradient(135deg, rgba(30,58,95,.96), rgba(8,14,24,.96));
            border: 1px solid rgba(0,180,216,.52);
        }
        .theory-assistant {
            margin-right: auto;
            background: linear-gradient(135deg, rgba(8,14,24,.98), rgba(20,83,45,.33));
            border: 1px solid rgba(34,197,94,.42);
        }
        @media (max-width: 1100px) {
            .theory-metric-grid,
            .theory-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
        }
        @media (max-width: 720px) {
            .theory-metric-grid,
            .theory-grid,
            .theory-formula-row {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
