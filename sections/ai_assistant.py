"""sections/ai_assistant.py — Groq AI Engineering Assistant"""
import json
import os

import streamlit as st

from sections.phase3_style import render_phase3_style

GROQ_DEFAULT_MODEL = "llama-3.1-8b-instant"
GROQ_DEPRECATED_MODEL_REPLACEMENTS = {
    "llama3-8b-8192": GROQ_DEFAULT_MODEL,
    "llama3-70b-8192": "llama-3.3-70b-versatile",
}


def get_groq_response(user_message: str, context: dict) -> str:
    api_key = st.session_state.get("groq_api_key", "") or os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        return "⚠️ Enter your Groq API key in the sidebar to activate the AI Assistant."

    feed     = context.get("feed", {})
    shortcut = context.get("shortcut", {})
    diameter = context.get("diameter", {})
    height   = context.get("height", {})
    reboiler = context.get("reboiler", {})
    condenser= context.get("condenser", {})
    thermo   = context.get("thermo", {})
    mech     = context.get("mechanical", {})

    system_prompt = f"""You are DistillAI — an expert AI assistant for industrial distillation column design.
You help chemical engineers with distillation design, calculations, troubleshooting, and optimization.

=== CURRENT DESIGN STATE ===
System: {feed.get('light','—')} / {feed.get('heavy','—')}
Feed: F={feed.get('F','—')} kmol/h, zF={feed.get('z_F','—')}, xD={feed.get('x_D','—')}, xB={feed.get('x_B','—')}
Pressure: {feed.get('P_col_bar','—')} bar | Feed condition: {feed.get('feed_condition','—')}

Thermodynamics: α={thermo.get('alpha_avg','—')}, T_bubble_D={thermo.get('T_bubble_D','—')}°C, T_bubble_B={thermo.get('T_bubble_B','—')}°C

Shortcut Results:
  N_min={shortcut.get('N_min','—')}, R_min={shortcut.get('R_min','—')}, R={shortcut.get('R','—')} ({shortcut.get('R_mult','—')}×Rmin)
  N_actual={shortcut.get('N_actual_int','—')} stages, Feed tray={shortcut.get('NF','—')} from top

Column Sizing:
  Diameter={diameter.get('D_column_std_m','—')} m, Height={height.get('total_height_m','—')} m
  H/D={height.get('H_D_ratio','—')}, Trays={height.get('N_actual_trays','—')}

Heat Exchangers:
  Reboiler: Q={reboiler.get('Q_reboiler_kW','—')} kW, Area={reboiler.get('A_reb_m2','—')} m²
  Condenser: Q={condenser.get('Q_condenser_kW','—')} kW, Area={condenser.get('A_cond_m2','—')} m²

Mechanical: t_shell={mech.get('t_shell_mm','—')} mm, Material={mech.get('material','—')}

=== YOUR ROLE ===
- Answer industrial distillation questions concisely and technically
- Reference the current design data when relevant
- Explain equations and their industrial significance
- Give troubleshooting advice for common problems
- Suggest design optimizations
- Keep responses under 250 words unless detailed explanation is needed
- Use industrial terminology (McCabe-Thiele, Fenske, Underwood, Fair method, HETP, etc.)
- Reference Perry's, Seader-Henley, McCabe-Smith when relevant
"""

    history = st.session_state.get("ai_chat_history", [])
    messages = [{"role": "system", "content": system_prompt}]
    for m in history[-8:]:
        messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": user_message})

    return _call_groq_chat(api_key, messages, temperature=0.4, max_tokens=500)


def _call_groq_chat(api_key: str, messages: list, temperature: float, max_tokens: int) -> str:
    model = _get_groq_model()
    try:
        from groq import Groq
    except ImportError:
        return _call_groq_rest(api_key, messages, temperature, max_tokens, model)

    try:
        resp = Groq(api_key=api_key).chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content
    except Exception as e:
        # Some Windows/Python setups can make the official Groq client fail before
        # the HTTPS request is completed, commonly with a local certificate/proxy
        # file error. In that case, retry with a direct REST request.
        fallback = _call_groq_rest(api_key, messages, temperature, max_tokens, model)
        if not fallback.startswith("Groq API error:"):
            return fallback
        return _friendly_groq_error(str(e))


def _call_groq_rest(api_key: str, messages: list, temperature: float, max_tokens: int, model: str) -> str:
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "DistillAI/1.0 (Streamlit; Windows)",
    }

    try:
        import requests

        session = requests.Session()
        session.trust_env = False
        response = session.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=45,
        )
        if response.status_code >= 400:
            return _friendly_groq_error(f"{response.status_code} {response.reason}. {response.text[:500]}")
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except ImportError:
        pass
    except Exception as e:
        return _friendly_groq_error(str(e))

    try:
        import urllib.error
        import urllib.request

        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=45) as response:
            data = json.loads(response.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="ignore")
        return _friendly_groq_error(f"{e.code} {e.reason}. {detail[:400]}")
    except urllib.error.URLError as e:
        return _friendly_groq_error(f"Network error: {e.reason}")
    except Exception as e:
        return _friendly_groq_error(str(e))


def _friendly_groq_error(error_text: str) -> str:
    lowered = error_text.lower()
    if "model_decommissioned" in lowered or "decommissioned" in lowered:
        return (
            f"Groq model was decommissioned. The app has been updated to use "
            f"`{GROQ_DEFAULT_MODEL}`. Please refresh the page and send the question again."
        )
    if "403" in lowered and "1010" in lowered:
        return (
            "Groq access is being blocked with 403 / code 1010. This is usually a network, firewall, "
            "VPN, or API access restriction issue, not a calculation problem. Try a fresh Groq API key, "
            "turn off VPN/proxy, or use another network. The app code now uses the official client when "
            "installed and a requests-based fallback when it is not."
        )
    if "401" in lowered or "invalid api key" in lowered or "unauthorized" in lowered:
        return "Groq API key is invalid or expired. Please paste a fresh key from console.groq.com in the sidebar."
    if "errno 2" in lowered or "no such file or directory" in lowered:
        return (
            "Groq request could not start because Python found a missing local network/certificate file. "
            "The app now retries through a direct REST fallback. Refresh the page and send the question again. "
            "If it still appears, restart the Streamlit app once."
        )
    return f"Groq API error: {error_text}"


def _get_groq_model() -> str:
    configured = os.environ.get("GROQ_MODEL", GROQ_DEFAULT_MODEL).strip()
    return GROQ_DEPRECATED_MODEL_REPLACEMENTS.get(configured, configured or GROQ_DEFAULT_MODEL)


def render():
    render_phase3_style()
    _render_ai_visibility_style()
    _drop_stale_groq_install_errors("ai_chat_history")

    st.markdown("""
    <div class="section-header">
        <h1>🤖 AI Engineering Assistant</h1>
        <p>Groq-powered distillation expert — design validation, troubleshooting, optimization, and industrial Q&A.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── API Key ──────────────────────────────────────────────
    with st.expander("🔑 Groq API Key", expanded=not st.session_state.get("groq_api_key")):
        key_inp = st.text_input("Groq API Key", value=st.session_state.get("groq_api_key",""),
                                 type="password", placeholder="gsk_xxxxxxxxxxxx")
        if key_inp:
            st.session_state["groq_api_key"] = key_inp
            st.success("✅ Key saved")
        st.markdown("[🔗 Get free key at console.groq.com](https://console.groq.com)")

    # ── Quick Questions ───────────────────────────────────────
    st.markdown("**⚡ Quick Questions:**")
    quick = [
        "Explain Fenske equation",
        "Why is R/Rmin = 1.2–1.5 typical?",
        "Validate my current design",
        "How to reduce reboiler duty?",
        "Explain McCabe-Thiele method",
        "What causes flooding?",
        "How to improve tray efficiency?",
        "Explain HETP for packed columns",
        "What is optimal reflux ratio?",
        "Troubleshoot high rejection rate",
    ]
    cols = st.columns(5)
    for i, q in enumerate(quick):
        with cols[i % 5]:
            if st.button(q, key=f"quick_{i}", use_container_width=True):
                _send_message(q)

    st.markdown("<div class='eng-divider'></div>", unsafe_allow_html=True)

    # ── Chat History ─────────────────────────────────────────
    history = st.session_state.get("ai_chat_history", [])
    if not history:
        st.markdown("""
        <div class="phase4-ai-empty">
            <div style="font-size:2.5rem;margin-bottom:10px">🤖</div>
            <b>DistillAI is ready.</b><br>
            Ask me about your distillation design — calculations, troubleshooting, optimization, or theory.
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in history:
            if msg["role"] == "user":
                st.markdown(f"""
                <div style="display:flex;justify-content:flex-end;margin:8px 0">
                  <div class="phase4-ai-user">
                    {msg['content']}
                  </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="display:flex;justify-content:flex-start;margin:8px 0">
                  <div class="phase4-ai-assistant">
                    🤖 {msg['content']}
                  </div>
                </div>
                """, unsafe_allow_html=True)

    # ── Input ────────────────────────────────────────────────
    c1, c2 = st.columns([5, 1])
    with c1:
        user_in = st.text_input("Ask DistillAI...", key="ai_input",
                                 placeholder="e.g. Why is my column diameter too large?",
                                 label_visibility="collapsed")
    with c2:
        send = st.button("Send ➤", use_container_width=True)

    if send and user_in:
        _send_message(user_in)
        st.rerun()

    if history:
        if st.button("🗑️ Clear Chat"):
            st.session_state["ai_chat_history"] = []
            st.rerun()


def _send_message(msg: str):
    if "ai_chat_history" not in st.session_state:
        st.session_state["ai_chat_history"] = []
    st.session_state["ai_chat_history"].append({"role": "user", "content": msg})
    context = {k: st.session_state.get(k, {}) for k in
               ["feed","thermo","shortcut","diameter","height","reboiler","condenser","mechanical"]}
    with st.spinner("DistillAI thinking..."):
        reply = get_groq_response(msg, context)
    st.session_state["ai_chat_history"].append({"role": "assistant", "content": reply})


def _drop_stale_groq_install_errors(history_key: str):
    history = st.session_state.get(history_key, [])
    cleaned = [
        msg for msg in history
        if not _is_stale_groq_error(str(msg.get("content", "")))
    ]
    if len(cleaned) != len(history):
        st.session_state[history_key] = cleaned


def _is_stale_groq_error(content: str) -> bool:
    lowered = content.lower()
    return (
        "groq library not installed" in lowered
        or ("groq api error" in lowered and "403" in lowered and "1010" in lowered)
        or ("groq api error" in lowered and "errno 2" in lowered)
        or ("groq api error" in lowered and "no such file or directory" in lowered)
        or "model_decommissioned" in lowered
        or "model was decommissioned" in lowered
        or "has been decommissioned" in lowered
    )


def _render_ai_visibility_style():
    st.markdown(
        """
        <style>
        .phase4-ai-empty {
            text-align: center;
            padding: 32px;
            color: #eaf6ff;
            background: linear-gradient(135deg, rgba(8, 14, 24, 0.99), rgba(15, 23, 42, 0.96));
            border: 1px dashed rgba(248, 212, 119, 0.44);
            border-radius: 8px;
            line-height: 1.7;
            font-weight: 800;
            box-shadow: 0 10px 24px rgba(0,0,0,0.16);
        }
        .phase4-ai-empty b {
            color: #f8d477;
            font-weight: 900;
        }
        .phase4-ai-user,
        .phase4-ai-assistant {
            padding: 12px 15px;
            max-width: 84%;
            font-size: 0.94rem;
            line-height: 1.65;
            color: #f8fbff;
            font-weight: 750;
            box-shadow: 0 10px 24px rgba(0,0,0,0.16);
        }
        .phase4-ai-user {
            background: linear-gradient(135deg, rgba(30, 58, 95, 0.96), rgba(8, 14, 24, 0.96));
            border: 1px solid rgba(0, 180, 216, 0.58);
            border-radius: 12px 2px 12px 12px;
        }
        .phase4-ai-assistant {
            background: linear-gradient(135deg, rgba(8, 14, 24, 0.98), rgba(15, 23, 42, 0.96));
            border: 1px solid rgba(248, 212, 119, 0.38);
            border-radius: 2px 12px 12px 12px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
