"""DistillAI — Industrial Distillation Column Design System"""
import streamlit as st
import importlib, sys, os
import base64

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

st.set_page_config(
    page_title="DistillAI – Industrial Design System",
    page_icon="⚗️", layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────
def load_css():
    p = os.path.join(ROOT, "assets", "styles.css")
    if os.path.exists(p):
        with open(p, encoding="utf-8", errors="ignore") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    st.markdown("""
    <style>
    section[data-testid="stSidebar"] {
        background:
          linear-gradient(180deg, #05080f 0%, #071421 48%, #05080f 100%) !important;
        border-right:1px solid rgba(0,180,216,.36)!important;
    }
    section[data-testid="stSidebar"] > div {
        padding-top:0.55rem;
    }
    .sidebar-profile-wrap {
        display:flex;
        justify-content:center;
        align-items:center;
        padding:12px 0 12px;
        margin:0 0 2px;
    }
    .sidebar-profile-frame {
        width:138px;
        height:138px;
        border-radius:50%;
        padding:4px;
        box-sizing:border-box;
        overflow:hidden;
        background:
          linear-gradient(#071018, #071018) padding-box,
          linear-gradient(135deg, #22c55e, #00d4ff 48%, #f8d477) border-box;
        border:3px solid transparent;
        box-shadow:
          0 0 0 1px rgba(255,255,255,.05),
          0 0 22px rgba(0, 180, 216, .24),
          0 0 18px rgba(34, 197, 94, .18);
    }
    .sidebar-profile-photo {
        width:100%;
        height:100%;
        border-radius:50%;
        background-repeat:no-repeat;
        background-size:145% auto;
        background-position:center top;
    }
    .sidebar-logo {
        display:grid!important;
        grid-template-columns:38px 1fr 38px;
        align-items:center!important;
        gap:9px!important;
        padding:12px 10px 13px!important;
        margin:2px 0 13px!important;
        border-top:2px solid #22c55e!important;
        border-bottom:2px solid #22c55e!important;
        border-left:3px solid #f8d477!important;
        border-right:3px solid #f8d477!important;
        border-radius:10px!important;
        background:
          linear-gradient(90deg, rgba(34,197,94,.11), transparent 18%, transparent 82%, rgba(0,212,255,.11)),
          linear-gradient(135deg, rgba(8,14,24,.98), rgba(12,38,52,.93))!important;
        box-shadow:0 14px 30px rgba(0,0,0,.24), 0 0 24px rgba(0,180,216,.11), inset 0 1px 0 rgba(255,255,255,.06);
    }
    .sidebar-brand-center {
        text-align:center;
        min-width:0;
    }
    .logo-title {
        font-family:'Barlow Condensed', sans-serif!important;
        font-size:1.52rem!important;
        font-weight:900!important;
        line-height:.96!important;
        letter-spacing:.4px!important;
        color:#f8d477!important;
        text-shadow:0 0 14px rgba(248,212,119,.24), 0 0 18px rgba(0,180,216,.16);
    }
    .logo-title .logo-ai {
        color:#00d4ff!important;
    }
    .logo-sub {
        color:#dbeafe!important;
        font-size:.72rem!important;
        line-height:1.25!important;
        font-weight:850!important;
        letter-spacing:.65px!important;
        text-transform:uppercase!important;
        margin-top:5px!important;
        opacity:.95;
    }
    .brand-column-symbol,
    .brand-ai-symbol {
        position:relative;
        display:block;
        width:36px;
        height:36px;
        border-radius:10px;
        background:linear-gradient(135deg, rgba(5,12,20,.98), rgba(13,37,52,.92));
        border:1px solid rgba(0,212,255,.55);
        box-shadow:0 0 16px rgba(0,180,216,.18), inset 0 1px 0 rgba(255,255,255,.08);
    }
    .brand-column-symbol:before {
        content:"";
        position:absolute;
        left:12px;
        top:5px;
        width:12px;
        height:25px;
        border:2px solid #00d4ff;
        border-radius:9px / 4px;
        background:linear-gradient(180deg, rgba(0,180,216,.18), rgba(34,197,94,.10));
    }
    .brand-column-symbol:after {
        content:"";
        position:absolute;
        left:14px;
        top:11px;
        width:8px;
        height:1px;
        background:#f8d477;
        box-shadow:0 6px 0 #f8d477, 0 12px 0 #f8d477;
    }
    .brand-ai-symbol:before {
        content:"AI";
        position:absolute;
        inset:0;
        display:grid;
        place-items:center;
        color:#22c55e;
        font-family:'Share Tech Mono', monospace;
        font-weight:900;
        font-size:13px;
    }
    .brand-ai-symbol:after {
        content:"";
        position:absolute;
        inset:5px;
        border:1px solid rgba(248,212,119,.50);
        border-radius:7px;
        box-shadow:
          -8px 5px 0 -6px #00d4ff,
          8px 5px 0 -6px #00d4ff,
          5px -8px 0 -6px #22c55e,
          5px 8px 0 -6px #22c55e;
    }
    .sidebar-progress-card {
        padding:9px 10px 10px;
        margin:0 0 10px;
        border:1px solid rgba(0,180,216,.30);
        border-radius:8px;
        background:linear-gradient(135deg, rgba(8,14,24,.94), rgba(14,32,46,.86));
        box-shadow:0 9px 20px rgba(0,0,0,.18);
    }
    .sidebar-progress-top {
        display:flex;
        justify-content:space-between;
        align-items:center;
        font-size:10.8px;
        color:#dbeafe;
        margin-bottom:6px;
        font-weight:850;
    }
    .sidebar-progress-top .progress-value {
        font-family:'Share Tech Mono', monospace;
        font-weight:900;
    }
    .column-status-card {
        border-radius:8px;
        padding:7px 9px;
        font-size:11px;
        font-weight:900;
        margin:6px 0 10px;
        border:1px solid;
        box-shadow:0 8px 18px rgba(0,0,0,.16);
    }
    .status-tray {
        background:rgba(0,180,216,.13);
        border-color:rgba(0,180,216,.55);
        color:#7dd3fc!important;
    }
    .status-packed {
        background:rgba(34,197,94,.12);
        border-color:rgba(34,197,94,.55);
        color:#86efac!important;
    }
    .status-pending {
        background:rgba(248,212,119,.10);
        border-color:rgba(248,212,119,.38);
        color:#f8d477!important;
    }
    .sidebar-dev-card {
        margin:16px 0 0;
        padding:13px 12px 12px;
        border-radius:7px;
        background:linear-gradient(135deg, rgba(8, 51, 68, .96), rgba(12, 74, 110, .78));
        border:1px solid rgba(0,180,216,.45);
        box-shadow:0 10px 22px rgba(0,0,0,.18), inset 0 1px 0 rgba(255,255,255,.06);
        color:#dbeafe!important;
        font-size:11.2px;
        line-height:1.68;
        letter-spacing:0!important;
        word-spacing:0!important;
        text-align:center;
        font-weight:700;
    }
    .sidebar-dev-card * {
        letter-spacing:0!important;
        word-spacing:0!important;
        text-transform:none!important;
    }
    .sidebar-dev-card b {
        color:#f8fbff!important;
        font-weight:900!important;
        letter-spacing:.2px;
    }
    .sidebar-dev-card .dev-accent {
        color:#f8d477!important;
        font-weight:900!important;
    }
    .sidebar-dev-card .dev-line {
        display:block;
        white-space:nowrap;
    }
    .sidebar-dev-card .dev-campus {
        color:#dbeafe!important;
        font-weight:800!important;
        white-space:nowrap;
    }
    .sidebar-dev-card .dev-label {
        color:#22c55e!important;
        font-weight:900!important;
        letter-spacing:0!important;
    }
    .sidebar-dev-card .dev-icon {
        color:#22c55e!important;
        margin-right:3px;
    }
    .sidebar-dev-card .dev-contact {
        display:grid;
        grid-template-columns:22px minmax(0, 1fr);
        align-items:center;
        justify-content:initial;
        gap:7px;
        margin-top:6px;
        padding-top:6px;
        border-top:1px dashed rgba(248,212,119,.32);
        color:#dbeafe!important;
        font-size:9.9px;
        line-height:1.25;
        text-align:left;
    }
    .sidebar-dev-card .dev-contact + .dev-contact {
        margin-top:2px;
        padding-top:0;
        border-top:0;
    }
    .sidebar-dev-card .contact-icon {
        width:20px;
        height:20px;
        min-width:20px;
        display:inline-grid;
        place-items:center;
        border-radius:50%;
        background:rgba(34,197,94,.14);
        border:1px solid rgba(34,197,94,.45);
        color:#22c55e!important;
    }
    .sidebar-dev-card .contact-icon svg {
        width:12px;
        height:12px;
        stroke:currentColor;
        fill:none;
        stroke-width:2.2;
        stroke-linecap:round;
        stroke-linejoin:round;
    }
    .sidebar-dev-card .whatsapp-icon {
        background:rgba(34,197,94,.20);
        border-color:rgba(34,197,94,.62);
    }
    .sidebar-dev-card .contact-value {
        color:#f8fbff!important;
        font-weight:850!important;
        white-space:nowrap;
        overflow:hidden;
        text-overflow:ellipsis;
    }
    /* Nav buttons */
    section[data-testid="stSidebar"] button[kind="secondary"] {
        width:100%!important; text-align:left!important;
        background:linear-gradient(90deg, rgba(13,25,36,.96), rgba(8,15,23,.94))!important;
        border:1px solid rgba(30,58,95,.50)!important;
        border-left:3px solid rgba(0,180,216,.30)!important;
        border-radius:9px!important;
        padding:8px 10px!important;
        font-size:12.8px!important;
        color:#dbeafe!important;
        transition:all .15s ease!important;
        margin-bottom:5px!important;
        font-weight:780!important;
        box-shadow:0 7px 16px rgba(0,0,0,.13);
    }
    section[data-testid="stSidebar"] button[kind="secondary"]:hover {
        background:rgba(0,180,216,.16)!important;
        border-color:rgba(0,180,216,.52)!important;
        color:#f8fbff!important;
        transform:translateX(2px);
        border-left-color:#22c55e!important;
    }
    section[data-testid="stSidebar"] button[kind="primary"] {
        width:100%!important; text-align:left!important;
        background:linear-gradient(90deg, #15803d, #22c55e)!important;
        border:1px solid rgba(248,212,119,.55)!important;
        border-left:4px solid #f8d477!important;
        border-radius:9px!important;
        padding:8px 10px!important;
        font-size:12.9px!important;
        color:#f8fbff!important;
        font-weight:900!important;
        margin-bottom:5px!important;
        box-shadow:0 10px 22px rgba(34,197,94,.22);
    }
    section[data-testid="stSidebar"] button p {
        font-weight:inherit!important;
        letter-spacing:0!important;
    }
    section[data-testid="stSidebar"] button[kind="primary"] p {
        color:#f8fbff!important;
    }
    .nav-group-label {
        font-size:13.2px!important;
        color:#f8d477!important;
        letter-spacing:.55px!important;
        text-transform:uppercase;
        padding:9px 10px!important;
        margin:13px 0 7px!important;
        font-weight:950!important;
        border-left:3px solid #00d4ff;
        border-right:1px solid rgba(248,212,119,.30);
        border-top:1px solid rgba(34,197,94,.34);
        border-bottom:1px solid rgba(0,180,216,.24);
        border-radius:7px;
        background:linear-gradient(90deg, rgba(0,180,216,.20), rgba(248,212,119,.10), rgba(34,197,94,.06));
        text-shadow:0 0 12px rgba(248,212,119,.16);
        box-shadow:0 8px 18px rgba(0,0,0,.14), inset 0 1px 0 rgba(255,255,255,.035);
    }
    .nav-group-label:after {
        content:"";
        display:block;
        height:2px;
        margin-top:5px;
        border-radius:999px;
        background:linear-gradient(90deg, #22c55e, #00d4ff, transparent);
    }
    .nav-warn { font-size:11px; color:#f59e0b;
        padding:3px 4px 6px; line-height:1.4; }
    .progress-bar-bg {
        background:#111827;
        border:1px solid rgba(30,58,95,.70);
        border-radius:999px;
        height:9px;
        overflow:hidden;
    }
    .progress-bar-fill {
        background:linear-gradient(90deg, #00b4d8, #22c55e);
        border-radius:999px;
        height:100%;
        box-shadow:0 0 12px rgba(0,180,216,.24);
    }
    section[data-testid="stSidebar"] details {
        border:1px solid rgba(30,58,95,.70);
        border-radius:8px;
        background:rgba(8,14,24,.52);
        margin-bottom:8px;
    }
    </style>
    """, unsafe_allow_html=True)

load_css()


def _asset_data_uri(filename):
    path = os.path.join(ROOT, "assets", filename)
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


# ── Session defaults ───────────────────────────────────────────────────
DEFAULTS = {
    "feed":{}, "thermo":{}, "column_type":None,
    "shortcut":{}, "mccabe":{}, "rigorous":{},
    "diameter":{}, "height":{}, "reboiler":{},
    "condenser":{}, "mechanical":{}, "internals":{},
    "tray_design":{}, "packing_design":{},
    "instrumentation":{}, "energy":{},
    "ai_chat_history":[], "groq_api_key":"",
    "active_section":"🏠 Home Dashboard",
}
for k,v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

col_type = st.session_state.get("column_type", None)
active   = st.session_state.get("active_section", "🏠 Home Dashboard")

# ── Section → module ───────────────────────────────────────────────────
SECTION_MAP = {
    "🏠 Home Dashboard":           "sections.home",
    "📥 Feed Specifications":      "sections.feed",
    "🧪 Thermodynamics DB":        "sections.thermodynamics",
    "🏗️ Column Type":              "sections.column_type",
    "⚡ Shortcut Design":          "sections.shortcut",
    "📈 McCabe-Thiele":            "sections.mccabe_thiele",
    # tray
    "▦ Tray Design":               "sections.tray_design",
    "📐 Column Diameter":          "sections.diameter",
    "📏 Column Height":            "sections.height",
    # packed
    "◎ Packing Design":            "sections.packing_design",
    "📐 Column Diameter (Packed)": "sections.diameter_packed",
    "📏 Column Height (Packed)":   "sections.height_packed",
    # common bottom
    "♨️ Reboiler Design":          "sections.reboiler",
    "❄️ Condenser Design":         "sections.condenser",
    "📉 Pressure Drop":            "sections.pressure_drop",
    "⚙️ Mechanical Design":        "sections.mechanical",
    "🔧 Column Internals":         "sections.internals",
    "🎛️ Instrumentation":          "sections.instrumentation",
    "💰 Energy & Economics":       "sections.energy_economics",
    "🔬 Rigorous Design":          "sections.rigorous",
    "🖼️ Visualization":            "sections.visualization",
    "📚 Theoretical Concepts":      "sections.theory_concepts",
    "🧭 Design Manager":            "sections.design_manager",
    "🤖 AI Assistant":             "sections.ai_assistant",
    "📋 Report Generator":         "sections.report",
}

# ── Nav helper ─────────────────────────────────────────────────────────
def nav_btn(label, done=False):
    is_active = (active == label)
    kind = "primary" if is_active else "secondary"
    prefix = "✅ " if (done and not is_active) else ""
    if st.sidebar.button(f"{prefix}{label}", key=f"nb_{label}",
                         type=kind, use_container_width=True):
        st.session_state.active_section = label
        st.rerun()

def nav_label(text):
    st.sidebar.markdown(f'<p class="nav-group-label">{text}</p>',
                        unsafe_allow_html=True)

# ── Completion flags ───────────────────────────────────────────────────
s = st.session_state
done = {
    "feed":     bool(s.feed),
    "thermo":   bool(s.thermo),
    "coltype":  s.column_type is not None,
    "shortcut": bool(s.shortcut),
    "tray":     bool(s.tray_design),
    "mccabe":   bool(s.mccabe),
    "diam":     bool(s.diameter),
    "height":   bool(s.height),
    "packing":  bool(s.packing_design),
    "reboiler": bool(s.reboiler),
    "condenser":bool(s.condenser),
    "mech":     bool(s.mechanical),
    "pressure": bool(s.get("pressure_drop", {})),
}

# ── Sidebar ────────────────────────────────────────────────────────────
with st.sidebar:
    profile_uri = _asset_data_uri("sidebar_profile.jpg")
    if profile_uri:
        st.markdown(f"""
        <div class="sidebar-profile-wrap">
          <div class="sidebar-profile-frame">
            <div class="sidebar-profile-photo" style="background-image:url('{profile_uri}')" aria-label="Zunair Shahzad profile"></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class='sidebar-logo'>
      <span class='brand-column-symbol' aria-hidden='true'></span>
      <div class='sidebar-brand-center'>
        <div class='logo-title'>Distill<span class='logo-ai'>AI</span></div>
        <div class='logo-sub'>Industrial Design System</div>
      </div>
      <span class='brand-ai-symbol' aria-hidden='true'></span>
    </div>""", unsafe_allow_html=True)

    # Overall progress bar
    total_steps = 9
    completed = sum([done["feed"], done["thermo"], done["coltype"],
                     done["shortcut"], done["diam"], done["height"],
                     done["reboiler"], done["condenser"], done["pressure"]])
    pct = int(completed / total_steps * 100)
    bar_color = "#22c55e" if pct==100 else "#00b4d8"
    st.markdown(f"""
    <div class="sidebar-progress-card">
      <div class="sidebar-progress-top">
        <span>Design Progress</span>
        <span class="progress-value" style="color:{bar_color}">{completed}/{total_steps} · {pct}%</span>
      </div>
      <div class="progress-bar-bg">
        <div class="progress-bar-fill"
             style="width:{pct}%;background:{bar_color}"></div>
      </div>
    </div>""", unsafe_allow_html=True)

    # Groq key
    with st.expander("🔑 Groq API Key", expanded=False):
        ki = st.text_input("Key", value=s.groq_api_key, type="password",
                           placeholder="gsk_...", key="gk",
                           label_visibility="collapsed")
        if ki:
            st.session_state.groq_api_key = ki
            st.success("✅ Saved")

    # Column type badge
    if col_type == "tray":
        st.markdown('<div class="column-status-card status-tray">▦ TRAY COLUMN active</div>', unsafe_allow_html=True)
    elif col_type == "packed":
        st.markdown('<div class="column-status-card status-packed">◎ PACKED COLUMN active</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="column-status-card status-pending">⚙️ Column type not selected</div>', unsafe_allow_html=True)

    # ── PHASE 1: Process basis (common) ───────────────────────────────
    nav_label("📋 Phase 1 — Process Basis (Common)")
    nav_btn("🏠 Home Dashboard")
    nav_btn("📥 Feed Specifications",  done["feed"])
    nav_btn("🧪 Thermodynamics DB",    done["thermo"])
    nav_btn("🏗️ Column Type",          done["coltype"])
    nav_btn("⚡ Shortcut Design",      done["shortcut"])
    nav_btn("📈 McCabe-Thiele",        done["mccabe"])

    # ── PHASE 2: Tray column ───────────────────────────────────────────
    nav_label("▦ Phase 2a — Tray Column Design")
    if col_type == "packed":
        st.sidebar.markdown('<p class="nav-warn">⚠️ Packed selected — reference only</p>',
                            unsafe_allow_html=True)
    nav_btn("▦ Tray Design",      done["tray"])
    nav_btn("📐 Column Diameter", done["diam"] and col_type=="tray")
    nav_btn("📏 Column Height",   done["height"] and col_type=="tray")

    # ── PHASE 2: Packed column ─────────────────────────────────────────
    nav_label("◎ Phase 2b — Packed Column Design")
    if col_type == "tray":
        st.sidebar.markdown('<p class="nav-warn">⚠️ Tray selected — reference only</p>',
                            unsafe_allow_html=True)
    nav_btn("◎ Packing Design",            done["packing"])
    nav_btn("📐 Column Diameter (Packed)", done["diam"] and col_type=="packed")
    nav_btn("📏 Column Height (Packed)",   done["height"] and col_type=="packed")

    # ── PHASE 3: Common detailed design ───────────────────────────────
    nav_label("🔩 Phase 3 — Detailed Design")
    nav_btn("♨️ Reboiler Design",   done["reboiler"])
    nav_btn("❄️ Condenser Design",  done["condenser"])
    nav_btn("📉 Pressure Drop",     bool(s.get("pressure_drop",{})))
    nav_btn("⚙️ Mechanical Design", done["mech"])
    nav_btn("🔧 Column Internals")
    nav_btn("🎛️ Instrumentation")
    nav_btn("💰 Energy & Economics")
    nav_btn("🔬 Rigorous Design")

    # ── PHASE 4: Output ────────────────────────────────────────────────
    nav_label("📤 Phase 4 — Output")
    nav_btn("🖼️ Visualization")
    nav_btn("📚 Theoretical Concepts")
    nav_btn("🧭 Design Manager")
    nav_btn("🤖 AI Assistant")
    nav_btn("📋 Report Generator")

# ── Router ─────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="sidebar-dev-card">
      <span class="dev-line"><span class="dev-icon">🔬</span><span class="dev-label">Developed by</span> <b>ZUNAIR SHAHZAD</b></span>
      <span class="dev-line dev-accent">Chemical Engineering</span>
      <span class="dev-line dev-campus">UET Lahore (New Campus)</span>
      <span class="dev-contact">
        <span class="contact-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24"><path d="M4 6h16v12H4z"></path><path d="m4 7 8 6 8-6"></path></svg>
        </span>
        <span class="contact-value">Eng.zunairshahzad@gmail.com</span>
      </span>
      <span class="dev-contact">
        <span class="contact-icon whatsapp-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24"><path d="M20.5 11.8a8.3 8.3 0 0 1-11.9 7.5L4 20.5l1.2-4.4a8.3 8.3 0 1 1 15.3-4.3Z"></path><path d="M9.1 8.8c.2-.5.4-.5.7-.5h.5c.2 0 .4 0 .5.4l.7 1.6c.1.2.1.4 0 .6l-.4.5c-.1.2-.2.3 0 .6.4.8 1.1 1.5 2 2 .3.1.4.1.6-.1l.6-.7c.2-.2.4-.2.6-.1l1.6.8c.3.1.4.3.3.6-.1.6-.7 1.4-1.5 1.5-1.4.2-4.4-1.1-5.9-3.7-1.1-1.8-1-2.9-.8-3.5Z"></path></svg>
        </span>
        <span class="contact-value">+923074274294</span>
      </span>
    </div>
    """, unsafe_allow_html=True)

module_path = SECTION_MAP.get(active, "sections.home")
try:
    if module_path in sys.modules:
        mod = importlib.reload(sys.modules[module_path])
    else:
        mod = importlib.import_module(module_path)
    mod.render()
except ModuleNotFoundError as e:
    st.error(f"❌ Module not found: `{module_path}`\n\n`{e}`")
    st.info("Run: `pip install -r requirements.txt`")
except Exception as e:
    st.exception(e)
