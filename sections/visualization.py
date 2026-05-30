"""sections/visualization.py - Advanced process visualization suite."""
import html
import math
import os

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from plotly.subplots import make_subplots

from calculations.distillation_calc import mccabe_thiele_stages
from sections.phase3_style import render_phase3_style


PLOT_BG = "#0d1520"
PAPER_BG = "#0a0e14"
GRID = "#1e3a5f"
TEXT = "#e2e8f0"
APP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_MEDIA_ROOT = os.path.join(APP_ROOT, "assets", "learning_media")
EXTERNAL_MEDIA_ROOT = r"D:\My_Projects\Chemical_Engineering_Projects\Distillation_pro_2\distill_data"
MEDIA_SCAN_ROOTS = [PROJECT_MEDIA_ROOT, EXTERNAL_MEDIA_ROOT]
VIDEO_EXTENSIONS = {".mp4", ".webm", ".ogg", ".mov", ".m4v"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}


def render():
    render_phase3_style()
    _render_phase4_style()

    st.markdown(
        """
        <div class="section-header">
            <h1>Process Visualization</h1>
            <p>Profiles, McCabe-Thiele, PFD, 3D tray composition, phase behavior,
            hydraulics, energy, and economics in one advanced visualization section.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    feed = st.session_state.get("feed", {})
    shortcut = st.session_state.get("shortcut", {})
    rigorous = st.session_state.get("rigorous", {})
    diameter = st.session_state.get("diameter", {})
    height = st.session_state.get("height", {})
    thermo = st.session_state.get("thermo", {})
    tray_design = st.session_state.get("tray_design", {})
    reboiler = st.session_state.get("reboiler", {})
    condenser = st.session_state.get("condenser", {})
    energy = st.session_state.get("energy", {})

    ctx = _build_context(
        feed, shortcut, rigorous, diameter, height, thermo, tray_design, reboiler, condenser, energy
    )

    st.markdown("### Visualization Command Center")
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Stages", f"{ctx['N_actual']}")
    k2.metric("Feed Tray", f"{ctx['NF']}")
    k3.metric("Reflux Ratio", f"{ctx['R']:.3f}")
    k4.metric("Column D", f"{ctx['D_col']:.2f} m")
    k5.metric("Column H", f"{ctx['H_total']:.1f} m")

    (
        tab_animation,
        tab_learning_media,
        tab_profiles,
        tab_rslider,
        tab_pfd,
        tab_3d,
        tab_phase,
        tab_flows,
        tab_energy,
        tab_hyd,
        tab_econ,
        tab_dash,
    ) = st.tabs(
        [
            "Process Animation",
            "Learning Media",
            "Profiles",
            "R Slider",
            "Complete PFD",
            "3D Tray Map",
            "T-x-y / VLE",
            "L/V Flows",
            "Energy Sankey",
            "Tray Hydraulics",
            "CAPEX/OPEX",
            "Dashboard",
        ]
    )

    with tab_animation:
        _render_process_animation(ctx)

    with tab_learning_media:
        _render_learning_media(ctx)

    with tab_profiles:
        _render_profiles(ctx)

    with tab_rslider:
        _render_reflux_slider(ctx)

    with tab_pfd:
        _render_pfd(ctx)

    with tab_3d:
        _render_3d_color_trays(ctx)

    with tab_phase:
        _render_phase_diagrams(ctx)

    with tab_flows:
        _render_flow_profiles(ctx)

    with tab_energy:
        _render_energy_sankey(ctx)

    with tab_hyd:
        _render_tray_hydraulics(ctx)

    with tab_econ:
        _render_economics(ctx)

    with tab_dash:
        _render_dashboard(ctx)


def _build_context(feed, shortcut, rigorous, diameter, height, thermo, tray_design, reboiler, condenser, energy):
    N_actual = _as_int(shortcut.get("N_actual_int", shortcut.get("N_actual", 20)), 20)
    N_actual = max(N_actual, 2)
    x_D = _clip(feed.get("x_D", 0.95), 0.001, 0.999)
    x_B = _clip(feed.get("x_B", 0.05), 0.001, 0.999)
    z_F = _clip(feed.get("z_F", 0.50), 0.001, 0.999)
    if x_B >= x_D:
        x_B, x_D = min(x_B, x_D), max(x_B, x_D)
        x_D = min(max(x_D, x_B + 0.05), 0.999)

    NF = _as_int(shortcut.get("NF", shortcut.get("feed_tray", N_actual // 2)), N_actual // 2)
    NF = int(np.clip(NF, 1, N_actual))
    F = float(feed.get("F", shortcut.get("F", 100.0)) or 100.0)
    D_flow = float(shortcut.get("D", F * (z_F - x_B) / max(x_D - x_B, 1e-6)) or F * 0.5)
    B_flow = float(shortcut.get("B", F - D_flow) or F * 0.5)
    R = float(shortcut.get("R", st.session_state.get("mccabe", {}).get("R", 2.0)) or 2.0)
    R_min = max(float(shortcut.get("R_min", max(R / 1.35, 0.35)) or 0.35), 0.05)
    q = float(shortcut.get("q", 1.0) or 1.0)
    alpha = max(float(shortcut.get("alpha", thermo.get("alpha_avg", 2.5)) or 2.5), 1.05)

    stages = np.arange(1, N_actual + 1)
    if rigorous.get("x_profiles"):
        x_prof = np.array(rigorous["x_profiles"], dtype=float)
    elif rigorous.get("x_stages"):
        x_prof = np.array(rigorous["x_stages"], dtype=float)
    else:
        x_prof = x_B + (x_D - x_B) * (1 - np.exp(-4 * stages / N_actual)) / (1 - np.exp(-4))
    x_prof = np.clip(x_prof[:N_actual], x_B, x_D)
    if len(x_prof) < N_actual:
        x_prof = np.interp(stages, np.linspace(1, N_actual, len(x_prof)), x_prof)

    stages = np.arange(1, len(x_prof) + 1)
    N_actual = len(stages)
    NF = int(np.clip(NF, 1, N_actual))

    y_prof = alpha * x_prof / (1 + (alpha - 1) * x_prof)
    if rigorous.get("y_stages"):
        y_data = np.array(rigorous["y_stages"], dtype=float)[:N_actual]
        if len(y_data) == N_actual:
            y_prof = np.clip(y_data, x_B, x_D)

    T_top = float(thermo.get("T_bubble_D", thermo.get("T_top_C", 80.0)) or 80.0)
    T_bot = float(thermo.get("T_bubble_B", thermo.get("T_bottom_C", 110.0)) or 110.0)
    if rigorous.get("T_stages"):
        T_prof = np.array(rigorous["T_stages"], dtype=float)[:N_actual]
        if len(T_prof) != N_actual:
            T_prof = np.linspace(T_top, T_bot, N_actual)
    else:
        T_prof = np.linspace(T_top, T_bot, N_actual)

    P_col = float(feed.get("P_col_bar", feed.get("P_bar", 1.013)) or 1.013)
    dP_tray_bar = float(tray_design.get("dP_tray_Pa", 500.0) or 500.0) / 100000.0
    P_prof = P_col + dP_tray_bar * (N_actual - stages)

    D_col = float(
        diameter.get("D_column_std_m", diameter.get("D_column_m", tray_design.get("D_column_m", 1.2))) or 1.2
    )
    H_total = float(height.get("total_height_m", height.get("total_with_skirt_m", 15.0)) or 15.0)
    tray_spacing = float(tray_design.get("tray_spacing_m", height.get("tray_spacing_m", 0.6)) or 0.6)
    q_reb = float(reboiler.get("Q_reb_kW", reboiler.get("Q_reboiler_kW", energy.get("Q_reb_kW", 500.0))) or 500.0)
    q_cond = float(condenser.get("Q_cond_kW", condenser.get("Q_condenser_kW", energy.get("Q_cond_kW", 450.0))) or 450.0)

    return {
        "feed": feed,
        "shortcut": shortcut,
        "thermo": thermo,
        "tray_design": tray_design,
        "reboiler": reboiler,
        "condenser": condenser,
        "energy": energy,
        "stages": stages,
        "N_actual": N_actual,
        "NF": NF,
        "x_D": x_D,
        "x_B": x_B,
        "z_F": z_F,
        "x_prof": x_prof,
        "y_prof": y_prof,
        "T_prof": T_prof,
        "P_prof": P_prof,
        "P_col": P_col,
        "D_col": D_col,
        "H_total": H_total,
        "tray_spacing": tray_spacing,
        "F": F,
        "D_flow": max(D_flow, 0.001),
        "B_flow": max(B_flow, 0.001),
        "R": max(R, 0.01),
        "R_min": R_min,
        "q": q,
        "alpha": alpha,
        "Q_reb": q_reb,
        "Q_cond": q_cond,
    }


def _render_phase4_style():
    st.markdown(
        """
        <style>
        div[data-testid="stTabs"] button p {
            color: #eaf6ff !important;
            font-weight: 900 !important;
            letter-spacing: 0;
        }
        div[data-testid="stTabs"] button[aria-selected="true"] p {
            color: #f8d477 !important;
            text-shadow: 0 0 12px rgba(248, 212, 119, 0.25);
        }
        div[data-testid="stDataFrame"] {
            border: 1px solid rgba(0, 180, 216, 0.42);
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 12px 28px rgba(0,0,0,0.18);
        }
        .phase4-status-box {
            margin: 0.35rem 0 0.85rem;
            padding: 0.85rem 1rem;
            border-radius: 8px;
            color: #eaf6ff;
            background: linear-gradient(135deg, rgba(8, 14, 24, 0.99), rgba(15, 23, 42, 0.97));
            border: 1px solid rgba(0, 180, 216, 0.42);
            border-left: 4px solid #f8d477;
            font-weight: 800;
            line-height: 1.6;
        }
        .phase4-status-box strong {
            color: #22c55e;
            font-weight: 900;
        }
        .phase4-status-box .state-running {
            color: #22c55e;
            font-weight: 900;
        }
        .phase4-status-box .state-stopped {
            color: #ff5b6e;
            font-weight: 900;
        }
        .learning-media-panel {
            background: linear-gradient(135deg, rgba(8, 14, 24, 0.99), rgba(15, 23, 42, 0.96));
            border: 1px solid rgba(0, 180, 216, 0.42);
            border-left: 4px solid #f8d477;
            border-radius: 8px;
            padding: 1rem 1.1rem;
            margin: 0.5rem 0 1rem;
            color: #eaf6ff;
            box-shadow: 0 12px 28px rgba(0,0,0,0.18), inset 0 1px 0 rgba(255,255,255,0.035);
        }
        .learning-media-panel strong {
            color: #22c55e;
            font-weight: 900;
        }
        .learning-media-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 12px;
            margin: 0.65rem 0 1rem;
        }
        .learning-media-card {
            background: linear-gradient(135deg, rgba(8, 14, 24, 0.98), rgba(17, 24, 39, 0.94));
            border: 1px solid rgba(0, 180, 216, 0.34);
            border-radius: 8px;
            padding: 0.85rem;
            color: #dbeafe;
            min-height: 96px;
            box-shadow: 0 10px 22px rgba(0,0,0,0.15);
        }
        .learning-media-card .lm-label {
            color: #ff5b6e;
            font-weight: 900;
            margin-bottom: 0.35rem;
        }
        .learning-media-card .lm-value {
            color: #00d4ff;
            font-family: 'Share Tech Mono', monospace;
            font-weight: 900;
            overflow-wrap: anywhere;
        }
        .learning-media-card .lm-note {
            color: #dbeafe;
            font-weight: 760;
            font-size: 0.85rem;
            margin-top: 0.25rem;
        }
        .learning-media-caption {
            color: #f8d477;
            font-weight: 900;
            margin: 0.3rem 0 0.55rem;
            overflow-wrap: anywhere;
        }
        .learning-media-muted {
            color: #dbeafe;
            font-weight: 760;
            line-height: 1.58;
        }
        @media (max-width: 900px) {
            .learning-media-grid {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_learning_media(ctx):
    st.markdown("### Learning Media")
    videos, images, scanned_roots = _discover_learning_media()

    st.markdown(
        f"""
        <div class="learning-media-panel">
            <strong>Media source:</strong> project assets plus your external folder.
            Detected <strong>{len(videos)}</strong> video file(s) and
            <strong>{len(images)}</strong> image file(s). Future MP4/JPG/PNG files added to the same folders
            will appear here automatically after refresh.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        _learning_media_cards(
            [
                ("Column mode", str(st.session_state.get("column_type") or "Not selected").title(), "media can support tray or packed explanation"),
                ("Stages", str(ctx["N_actual"]), "from saved design context"),
                ("Media folders", str(len(scanned_roots)), "active scan locations"),
            ]
        ),
        unsafe_allow_html=True,
    )

    if not videos and not images:
        st.info(
            "No learning media found yet. Put MP4 videos or JPG/PNG images in "
            f"`{EXTERNAL_MEDIA_ROOT}\\videos` or `{PROJECT_MEDIA_ROOT}`."
        )
        return

    video_col, image_col = st.columns([1.15, 1])
    with video_col:
        st.markdown("### Distillation Process Video")
        if videos:
            video_names = [_media_display_name(v) for v in videos]
            selected_video_name = st.selectbox(
                "Select process video",
                video_names,
                key="learning_media_video_select",
            )
            video = videos[video_names.index(selected_video_name)]
            st.markdown(_media_summary(video, "Video file"), unsafe_allow_html=True)
            st.video(video["path"])
        else:
            st.markdown(
                '<div class="learning-media-panel">No video file detected yet.</div>',
                unsafe_allow_html=True,
            )

    with image_col:
        st.markdown("### Column Structure Image")
        if images:
            image_names = [_media_display_name(i) for i in images]
            selected_image_name = st.selectbox(
                "Select column image",
                image_names,
                key="learning_media_image_select",
            )
            image = images[image_names.index(selected_image_name)]
            st.markdown(_media_summary(image, "Image file"), unsafe_allow_html=True)
            st.image(image["path"], use_container_width=True)
        else:
            st.markdown(
                '<div class="learning-media-panel">No image file detected yet.</div>',
                unsafe_allow_html=True,
            )

    if images:
        st.markdown("### Media Gallery")
        gallery_cols = st.columns(3)
        for idx, image in enumerate(images[:12]):
            with gallery_cols[idx % 3]:
                st.markdown(
                    f'<div class="learning-media-caption">{html.escape(image["name"])}</div>',
                    unsafe_allow_html=True,
                )
                st.image(image["path"], use_container_width=True)

    with st.expander("Detected media files"):
        media_rows = [
            {
                "Type": item["type"],
                "File": item["name"],
                "Size": _format_bytes(item["size"]),
                "Folder": item["folder"],
            }
            for item in videos + images
        ]
        st.dataframe(pd.DataFrame(media_rows), use_container_width=True, hide_index=True)


def _discover_learning_media():
    roots = []
    for root in MEDIA_SCAN_ROOTS:
        if os.path.isdir(root):
            roots.append(root)

    videos = []
    images = []
    seen_names = set()
    for root_index, root in enumerate(roots):
        for current, _, filenames in os.walk(root):
            for filename in filenames:
                ext = os.path.splitext(filename)[1].lower()
                if ext not in VIDEO_EXTENSIONS and ext not in IMAGE_EXTENSIONS:
                    continue
                key = filename.lower()
                if key in seen_names:
                    continue
                seen_names.add(key)
                path = os.path.join(current, filename)
                try:
                    size = os.path.getsize(path)
                except OSError:
                    size = 0
                item = {
                    "name": filename,
                    "path": path,
                    "folder": current,
                    "ext": ext,
                    "size": size,
                    "type": "Video" if ext in VIDEO_EXTENSIONS else "Image",
                    "source_priority": root_index,
                }
                if ext in VIDEO_EXTENSIONS:
                    videos.append(item)
                else:
                    images.append(item)

    videos.sort(key=lambda item: (item["source_priority"], item["ext"] != ".mp4", item["name"].lower()))
    images.sort(key=lambda item: (item["source_priority"], not _looks_like_column_image(item["name"]), item["name"].lower()))
    return videos, images, roots


def _looks_like_column_image(name):
    lowered = name.lower()
    return any(token in lowered for token in ["column", "distillation", "tower", "whatsapp image"])


def _learning_media_cards(items):
    cards = []
    for label, value, note in items:
        cards.append(
            '<div class="learning-media-card">'
            f'<div class="lm-label">{html.escape(label)}</div>'
            f'<div class="lm-value">{html.escape(value)}</div>'
            f'<div class="lm-note">{html.escape(note)}</div>'
            '</div>'
        )
    return f'<div class="learning-media-grid">{"".join(cards)}</div>'


def _media_display_name(item):
    return f'{item["name"]} ({_format_bytes(item["size"])})'


def _media_summary(item, label):
    return (
        '<div class="learning-media-panel">'
        f'<strong>{html.escape(label)}:</strong> {html.escape(item["name"])}<br>'
        f'<span class="learning-media-muted">Size: {_format_bytes(item["size"])} | '
        f'Folder: {html.escape(item["folder"])}</span>'
        '</div>'
    )


def _format_bytes(size):
    try:
        size = float(size)
    except (TypeError, ValueError):
        return "0 B"
    units = ["B", "KB", "MB", "GB"]
    index = 0
    while size >= 1024 and index < len(units) - 1:
        size /= 1024
        index += 1
    return f"{size:.1f} {units[index]}" if index else f"{int(size)} {units[index]}"


def _render_profiles(ctx):
    st.markdown("### Stage-by-Stage Process Profiles")
    stages = ctx["stages"]
    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=("Liquid/Vapor Composition", "Temperature", "Pressure", "Tray Composition Heatmap"),
        horizontal_spacing=0.08,
        vertical_spacing=0.14,
        specs=[[{}, {}], [{}, {}]],
    )
    fig.add_trace(
        go.Scatter(x=stages, y=ctx["x_prof"], name="Liquid x", mode="lines+markers", line=dict(color="#00b4d8", width=2.5)),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(x=stages, y=ctx["y_prof"], name="Vapor y", mode="lines+markers", line=dict(color="#f59e0b", width=2, dash="dash")),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(x=stages, y=ctx["T_prof"], name="Temperature", mode="lines+markers", fill="tozeroy", line=dict(color="#ef4444", width=2.5)),
        row=1,
        col=2,
    )
    fig.add_trace(
        go.Scatter(x=stages, y=ctx["P_prof"], name="Pressure", mode="lines+markers", fill="tozeroy", line=dict(color="#a855f7", width=2.5)),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Heatmap(
            z=[ctx["x_prof"]],
            x=stages,
            y=["x_light"],
            colorscale=[[0, "#1d4ed8"], [0.5, "#facc15"], [1, "#dc2626"]],
            colorbar=dict(title="x"),
            name="Composition map",
        ),
        row=2,
        col=2,
    )
    for row, col in [(1, 1), (1, 2), (2, 1), (2, 2)]:
        fig.add_vline(x=ctx["NF"], line_dash="dot", line_color="#22c55e", row=row, col=col)
    fig.update_xaxes(title_text="Stage Number (top to bottom)")
    fig.update_layout(
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font_color=TEXT,
        height=720,
        legend=dict(bgcolor=PAPER_BG),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    profile_df = pd.DataFrame(
        {
            "Stage": stages,
            "x liquid": np.round(ctx["x_prof"], 4),
            "y vapor": np.round(ctx["y_prof"], 4),
            "T [C]": np.round(ctx["T_prof"], 2),
            "P [bar]": np.round(ctx["P_prof"], 4),
        }
    )
    with st.expander("View stage-by-stage data table"):
        st.dataframe(profile_df, use_container_width=True, hide_index=True)


def _set_process_animation_running(value):
    st.session_state["process_animation_running"] = bool(value)


def _render_process_animation(ctx):
    st.markdown("### Complete Distillation Process Animation")
    col_type = st.session_state.get("column_type", "tray") or "tray"
    mode_label = "Packed Column" if col_type == "packed" else "Tray Column"
    if "process_animation_running" not in st.session_state:
        st.session_state["process_animation_running"] = True

    animation_running = bool(st.session_state.get("process_animation_running", True))
    c_start, c_stop, c_speed, c_labels = st.columns([1, 1, 2.25, 1.65])
    with c_start:
        st.button(
            "Start Animation",
            key="process_animation_start_button",
            use_container_width=True,
            disabled=animation_running,
            on_click=_set_process_animation_running,
            args=(True,),
        )
    with c_stop:
        st.button(
            "Stop Animation",
            key="process_animation_stop_button",
            use_container_width=True,
            disabled=not animation_running,
            on_click=_set_process_animation_running,
            args=(False,),
        )
    with c_speed:
        speed = st.slider(
            "Animation speed (slow to fast)",
            0.10,
            1.25,
            0.35,
            0.05,
            key="process_animation_speed",
        )
    with c_labels:
        show_values = st.toggle("Show calculation labels", value=True, key="process_animation_show_values")

    status_class = "state-running" if animation_running else "state-stopped"
    status_text = "Running" if animation_running else "Stopped"
    st.markdown(
        f"""
        <div class="phase4-status-box">
            Animation status: <span class="{status_class}">{status_text}</span>
            | Mode: <strong>{mode_label}</strong>
            | Live values are taken from the saved design calculations.
        </div>
        """,
        unsafe_allow_html=True,
    )

    tray_count = int(np.clip(ctx["N_actual"], 6, 34))
    feed_pct = 100 - ((ctx["NF"] - 1) / max(ctx["N_actual"] - 1, 1) * 100)
    reflux_flow = ctx["R"] * ctx["D_flow"]
    vapor_flow = (ctx["R"] + 1) * ctx["D_flow"]
    liquid_flow = reflux_flow + ctx["q"] * ctx["F"]
    energy_scale = np.clip((ctx["Q_reb"] + ctx["Q_cond"]) / 1200, 0.35, 1.75)
    particle_count = int(np.clip(18 + vapor_flow / max(ctx["F"], 1) * 16, 18, 56))
    comp_gradient = _css_composition_gradient(ctx["x_prof"], ctx["x_B"], ctx["x_D"])

    html = f"""
    <style>
      :root {{
        --speed: {speed:.2f};
        --feed-y: {feed_pct:.2f}%;
        --energy-scale: {energy_scale:.2f};
      }}
      .anim-wrap {{
        height: 880px;
        background:
          radial-gradient(circle at 18% 18%, rgba(0,180,216,.12), transparent 30%),
          linear-gradient(135deg, #080c12 0%, #0d1520 55%, #111827 100%);
        color: #e2e8f0;
        border: 1px solid #1e3a5f;
        border-radius: 10px;
        overflow: hidden;
        position: relative;
        font-family: Barlow, Segoe UI, sans-serif;
      }}
      .anim-wrap.paused *,
      .anim-wrap.paused *:before,
      .anim-wrap.paused *:after {{
        animation-play-state: paused !important;
      }}
      .anim-wrap.paused .particle {{
        animation: none !important;
        opacity: .92 !important;
      }}
      .anim-wrap.paused .vap {{ left: calc(38% + 92px); top: 360px; }}
      .anim-wrap.paused .liq {{ left: calc(38% + 78px); top: 270px; }}
      .anim-wrap.paused .feedp {{ left: 25%; top: calc(86px + var(--feed-y)); }}
      .anim-wrap.paused .refluxp {{ left: 61%; top: 232px; }}
      .anim-wrap.paused .distp {{ left: 83%; top: 224px; }}
      .anim-wrap.paused .bottomp {{ left: 68%; top: 662px; }}
      .anim-title {{
        position: absolute;
        left: 26px;
        top: 18px;
        z-index: 8;
      }}
      .anim-title h2 {{
        margin: 0;
        font-size: 22px;
        font-weight: 700;
        letter-spacing: 0;
        color: #f8d477;
        text-shadow: 0 0 16px rgba(248, 212, 119, .24);
      }}
      .anim-title p {{
        margin: 4px 0 0;
        color: #dbeafe;
        font-size: 13px;
        font-weight: 800;
      }}
      .metric-strip {{
        position: absolute;
        right: 22px;
        top: 18px;
        display: grid;
        grid-template-columns: repeat(4, minmax(92px, 1fr));
        gap: 8px;
        z-index: 8;
      }}
      .mini-metric {{
        background: linear-gradient(135deg, rgba(8, 13, 22, .92), rgba(15, 23, 42, .90));
        border: 1px solid rgba(0,180,216,.44);
        border-radius: 8px;
        padding: 8px 10px;
        box-shadow: 0 10px 24px rgba(0,0,0,.18);
      }}
      .mini-metric span {{
        display: block;
        color: #ff5b6e;
        font-size: 10px;
        font-weight: 900;
        text-transform: uppercase;
      }}
      .mini-metric strong {{
        display: block;
        color: #00d4ff;
        font-size: 16px;
        margin-top: 2px;
        text-shadow: 0 0 12px rgba(0,180,216,.2);
      }}
      .plant {{
        position: absolute;
        inset: 86px 28px 118px;
      }}
      .column-shell {{
        position: absolute;
        left: 38%;
        top: 54px;
        width: 190px;
        height: 560px;
        border: 3px solid #38bdf8;
        border-radius: 96px / 28px;
        background: linear-gradient(180deg, rgba(14,165,233,.12), rgba(15,23,42,.9));
        box-shadow: inset 0 0 28px rgba(56,189,248,.22), 0 0 28px rgba(14,165,233,.14);
        overflow: hidden;
      }}
      .column-shell:before,
      .column-shell:after {{
        content: "";
        position: absolute;
        left: -3px;
        width: 190px;
        height: 42px;
        border: 3px solid #38bdf8;
        border-radius: 50%;
        background: rgba(8,13,22,.92);
      }}
      .column-shell:before {{ top: -23px; }}
      .column-shell:after {{ bottom: -23px; }}
      .composition-band {{
        position: absolute;
        inset: 10px 18px;
        border-radius: 80px / 20px;
        background: {comp_gradient};
        opacity: .34;
        filter: saturate(1.25);
      }}
      .section-band {{
        position: absolute;
        left: 20px;
        right: 20px;
        border: 1px solid rgba(148,163,184,.18);
        border-radius: 72px / 18px;
        z-index: 2;
      }}
      .section-band.rectifying {{
        top: 24px;
        height: calc(var(--feed-y) - 24px);
        background: linear-gradient(180deg, rgba(34,197,94,.12), transparent);
      }}
      .section-band.stripping {{
        top: var(--feed-y);
        bottom: 24px;
        background: linear-gradient(180deg, transparent, rgba(239,68,68,.10));
      }}
      .side-rail {{
        position: absolute;
        top: 34px;
        bottom: 34px;
        width: 8px;
        border-radius: 999px;
        z-index: 5;
      }}
      .temp-rail {{ left: 8px; background: linear-gradient(180deg, #38bdf8, #f59e0b, #ef4444); }}
      .comp-rail {{ right: 8px; background: {comp_gradient}; }}
      .internals {{
        position: absolute;
        inset: 24px 20px;
        z-index: 4;
      }}
      .tray {{
        position: absolute;
        left: 0;
        width: 100%;
        height: 11px;
        border-radius: 999px;
        border-top: 2px solid rgba(186,230,253,.9);
        background: linear-gradient(180deg, rgba(125,211,252,.04), rgba(125,211,252,.20));
        box-shadow: 0 0 9px rgba(186,230,253,.55);
      }}
      .tray:before {{
        content: "";
        position: absolute;
        left: 8px;
        right: 26px;
        bottom: 0;
        height: 5px;
        border-radius: 0 0 10px 10px;
        background: linear-gradient(90deg, rgba(56,189,248,.16), rgba(125,211,252,.58), rgba(56,189,248,.16));
        animation: trayLiquid calc(3.8s / var(--speed)) ease-in-out infinite;
      }}
      .tray:after {{
        content: "";
        position: absolute;
        right: 5px;
        top: 0;
        width: 13px;
        height: 24px;
        border-right: 2px solid rgba(34,197,94,.78);
        border-bottom: 2px solid rgba(34,197,94,.78);
        border-radius: 0 0 8px 0;
      }}
      @keyframes trayLiquid {{
        50% {{ transform: translateX(5px); opacity: .76; }}
      }}
      .packed-bed {{
        position: absolute;
        inset: 36px 22px;
        border: 1px solid rgba(34,197,94,.45);
        border-radius: 64px / 18px;
        background-image:
          radial-gradient(circle, rgba(187,247,208,.75) 0 2px, transparent 3px),
          radial-gradient(circle, rgba(125,211,252,.45) 0 1.5px, transparent 2.5px);
        background-size: 22px 18px, 17px 23px;
        animation: packed calc(10s / var(--speed)) linear infinite;
        opacity: .78;
      }}
      .packing-grid {{
        position: absolute;
        left: 24px;
        right: 24px;
        height: 9px;
        border-top: 2px solid rgba(203,213,225,.62);
        border-bottom: 2px solid rgba(203,213,225,.35);
        z-index: 5;
      }}
      .packing-grid.top {{ top: 42px; }}
      .packing-grid.mid {{ top: calc(var(--feed-y) + 20px); border-color: rgba(34,197,94,.74); }}
      .packing-grid.bottom {{ bottom: 44px; }}
      @keyframes packed {{
        from {{ background-position: 0 0, 0 0; }}
        to {{ background-position: 44px 36px, -34px 46px; }}
      }}
      .feed-marker {{
        position: absolute;
        left: -18px;
        top: var(--feed-y);
        width: 226px;
        border-top: 3px solid #22c55e;
        box-shadow: 0 0 12px rgba(34,197,94,.8);
        z-index: 4;
      }}
      .feed-marker:after {{
        content: "Feed stage / zone";
        position: absolute;
        right: -116px;
        top: -10px;
        color: #22c55e;
        font-size: 11px;
        white-space: nowrap;
      }}
      .feed-spray {{
        position: absolute;
        left: 30px;
        right: 30px;
        top: calc(var(--feed-y) + 7px);
        height: 10px;
        border-top: 2px solid #22c55e;
        border-radius: 999px;
        z-index: 8;
      }}
      .feed-spray:after {{
        content: "";
        position: absolute;
        left: 4px;
        right: 4px;
        top: 3px;
        height: 6px;
        background-image: radial-gradient(circle, #86efac 0 2px, transparent 3px);
        background-size: 16px 6px;
      }}
      .tag {{
        position: absolute;
        z-index: 9;
        min-width: 38px;
        padding: 3px 6px;
        border: 1px solid #64748b;
        border-radius: 999px;
        background: rgba(3,7,18,.94);
        color: #f8fbff;
        text-align: center;
        font-size: 10px;
        font-weight: 800;
        box-shadow: 0 0 14px rgba(0,180,216,.16);
      }}
      .tag.top {{ right: 24px; top: 54px; }}
      .tag.feed {{ left: 22px; top: calc(var(--feed-y) + 17px); }}
      .tag.bottom {{ right: 24px; bottom: 54px; }}
      .equipment {{
        position: absolute;
        display: grid;
        place-items: center;
        text-align: center;
        background: rgba(8,13,22,.84);
        border: 2px solid;
        border-radius: 8px;
        color: #e2e8f0;
        font-size: 12px;
        font-weight: 700;
        z-index: 3;
        text-shadow: 0 0 12px rgba(255,255,255,.16);
      }}
      .condenser {{ left: 63%; top: 52px; width: 170px; height: 72px; border-color: #7dd3fc; color: #7dd3fc; }}
      .drum {{ left: 65%; top: 192px; width: 142px; height: 68px; border-color: #22c55e; color: #86efac; border-radius: 40px; }}
      .reboiler {{ left: 40%; top: 628px; width: 150px; height: 72px; border-color: #f59e0b; color: #fbbf24; border-radius: 50%; }}
      .condenser:after {{
        content: "";
        position: absolute;
        inset: 12px 16px;
        background:
          repeating-linear-gradient(90deg, transparent 0 10px, rgba(125,211,252,.55) 10px 12px),
          linear-gradient(180deg, transparent 46%, rgba(125,211,252,.40) 48% 52%, transparent 54%);
        opacity: .78;
      }}
      .drum:after {{
        content: "";
        position: absolute;
        left: 12px;
        right: 12px;
        bottom: 9px;
        height: 32%;
        border-radius: 0 0 25px 25px;
        background: rgba(56,189,248,.45);
      }}
      .reboiler:after {{
        content: "";
        position: absolute;
        left: 28px;
        right: 28px;
        top: 22px;
        height: 20px;
        border-top: 2px solid rgba(251,191,36,.80);
        border-bottom: 2px solid rgba(251,191,36,.45);
        border-radius: 50%;
      }}
      .control-valve {{
        position: absolute;
        z-index: 7;
        width: 24px;
        height: 18px;
        transform: rotate(45deg);
        border: 2px solid #cbd5e1;
        background: rgba(8,13,22,.88);
      }}
      .control-valve.feed {{ left: 27%; top: 393px; }}
      .control-valve.reflux {{ left: 58%; top: 286px; }}
      .control-valve.product {{ left: 85%; top: 278px; }}
      .small-pump {{
        position: absolute;
        z-index: 7;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        border: 2px solid #38bdf8;
        background: rgba(8,13,22,.88);
      }}
      .small-pump:after {{
        content: "";
        position: absolute;
        left: 8px;
        top: 7px;
        width: 0;
        height: 0;
        border-top: 7px solid transparent;
        border-bottom: 7px solid transparent;
        border-left: 11px solid #38bdf8;
      }}
      .small-pump.reflux {{ left: 62%; top: 260px; }}
      .small-pump.bottoms {{ left: 69%; top: 651px; border-color: #ef4444; }}
      .small-pump.bottoms:after {{ border-left-color: #ef4444; }}
      .heat-glow {{
        position: absolute;
        left: calc(40% + 20px);
        top: 610px;
        width: 110px;
        height: 110px;
        border-radius: 50%;
        background: rgba(249,115,22,.28);
        transform: scale(var(--energy-scale));
        filter: blur(18px);
        animation: pulse calc(1.55s / var(--speed)) ease-in-out infinite;
      }}
      .cool-glow {{
        position: absolute;
        left: calc(63% + 28px);
        top: 36px;
        width: 120px;
        height: 86px;
        border-radius: 40px;
        background: rgba(14,165,233,.22);
        filter: blur(15px);
        animation: pulse calc(1.9s / var(--speed)) ease-in-out infinite reverse;
      }}
      @keyframes pulse {{
        0%, 100% {{ opacity: .45; transform: scale(calc(var(--energy-scale) * .92)); }}
        50% {{ opacity: .92; transform: scale(calc(var(--energy-scale) * 1.08)); }}
      }}
      .pipe {{
        position: absolute;
        z-index: 1;
        overflow: visible;
      }}
      .pipe path {{
        fill: none;
        stroke-width: 7;
        stroke-linecap: round;
        stroke-linejoin: round;
        opacity: .86;
      }}
      .pipe-label {{
        position: absolute;
        z-index: 6;
        padding: 5px 7px;
        border: 1px solid rgba(0,180,216,.52);
        border-radius: 6px;
        background: rgba(3,7,18,.92);
        color: #f8fbff;
        font-size: 11px;
        font-weight: 850;
        line-height: 1.25;
        white-space: nowrap;
        box-shadow: 0 8px 18px rgba(0,0,0,.20);
      }}
      .particle {{
        position: absolute;
        width: 9px;
        height: 9px;
        border-radius: 50%;
        z-index: 5;
        box-shadow: 0 0 12px currentColor;
        opacity: 0;
      }}
      .vap {{ color: #f59e0b; background: #fbbf24; animation: vaporUp calc(2.8s / var(--speed)) linear infinite; }}
      .liq {{ color: #38bdf8; background: #7dd3fc; animation: liquidDown calc(3.2s / var(--speed)) linear infinite; }}
      .feedp {{ color: #22c55e; background: #86efac; animation: feedIn calc(2.2s / var(--speed)) linear infinite; }}
      .refluxp {{ color: #38bdf8; background: #7dd3fc; animation: refluxLoop calc(4.1s / var(--speed)) linear infinite; }}
      .distp {{ color: #22c55e; background: #86efac; animation: distillateOut calc(2.7s / var(--speed)) linear infinite; }}
      .bottomp {{ color: #ef4444; background: #fca5a5; animation: bottomsOut calc(2.9s / var(--speed)) linear infinite; }}
      @keyframes vaporUp {{
        0% {{ left: calc(38% + 92px); top: 612px; opacity: 0; }}
        12% {{ opacity: 1; }}
        88% {{ opacity: 1; }}
        100% {{ left: calc(38% + 92px); top: 74px; opacity: 0; }}
      }}
      @keyframes liquidDown {{
        0% {{ left: calc(38% + 78px); top: 80px; opacity: 0; }}
        12% {{ opacity: 1; }}
        88% {{ opacity: 1; }}
        100% {{ left: calc(38% + 78px); top: 610px; opacity: 0; }}
      }}
      @keyframes feedIn {{
        0% {{ left: 12%; top: calc(86px + var(--feed-y)); opacity: 0; }}
        20% {{ opacity: 1; }}
        100% {{ left: calc(38% - 6px); top: calc(86px + var(--feed-y)); opacity: 0; }}
      }}
      @keyframes refluxLoop {{
        0% {{ left: calc(65% + 8px); top: 232px; opacity: 0; }}
        18% {{ opacity: 1; }}
        60% {{ left: calc(38% + 178px); top: 232px; opacity: 1; }}
        100% {{ left: calc(38% + 146px); top: 102px; opacity: 0; }}
      }}
      @keyframes distillateOut {{
        0% {{ left: calc(65% + 118px); top: 224px; opacity: 0; }}
        25% {{ opacity: 1; }}
        100% {{ left: 91%; top: 224px; opacity: 0; }}
      }}
      @keyframes bottomsOut {{
        0% {{ left: calc(40% + 132px); top: 662px; opacity: 0; }}
        22% {{ opacity: 1; }}
        100% {{ left: 78%; top: 662px; opacity: 0; }}
      }}
      .legend {{
        position: absolute;
        left: 24px;
        right: 24px;
        bottom: 22px;
        display: flex;
        justify-content: center;
        gap: 14px;
        flex-wrap: wrap;
        color: #f8fbff;
        font-size: 12px;
        z-index: 12;
        padding: 12px 14px;
        border: 1px dashed rgba(248,212,119,.45);
        border-radius: 10px;
        background: rgba(3,7,18,.74);
        backdrop-filter: blur(4px);
      }}
      .legend span {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(8,13,22,.92);
        border: 1px solid rgba(0,180,216,.52);
        border-radius: 999px;
        padding: 7px 11px;
        font-weight: 900;
        box-shadow: 0 8px 18px rgba(0,0,0,.18);
      }}
      .dot {{ width: 9px; height: 9px; border-radius: 50%; display: inline-block; }}
      .phase-panel {{
        position: absolute;
        right: 24px;
        bottom: 22px;
        width: 286px;
        background: rgba(8,13,22,.80);
        border: 1px solid #1e3a5f;
        border-radius: 8px;
        padding: 12px 14px;
        z-index: 7;
      }}
      .phase-panel h3 {{
        margin: 0 0 8px;
        font-size: 14px;
        color: #f8d477;
        font-weight: 900;
      }}
      .phase-panel p {{
        margin: 5px 0;
        color: #dbeafe;
        font-size: 12px;
        line-height: 1.35;
        font-weight: 750;
      }}
      .hidden-labels .pipe-label,
      .hidden-labels .metric-strip,
      .hidden-labels .phase-panel {{
        display: none;
      }}
      @media (max-width: 900px) {{
        .anim-wrap {{ height: 930px; }}
        .metric-strip {{ left: 22px; right: 22px; top: 62px; grid-template-columns: repeat(2, 1fr); }}
        .plant {{ inset-top: 154px; transform: scale(.82); transform-origin: top left; width: 116%; }}
        .legend {{ left: 14px; right: 14px; bottom: 18px; justify-content: flex-start; }}
        .phase-panel {{ left: 20px; right: auto; width: calc(100% - 40px); bottom: 92px; }}
      }}
    </style>
    <div class="anim-wrap {'paused' if not animation_running else 'running'} {'hidden-labels' if not show_values else ''}">
      <div class="anim-title">
        <h2>{mode_label} Animated Process View</h2>
        <p>Calculation-driven animation from current saved design values</p>
      </div>
      <div class="metric-strip">
        <div class="mini-metric"><span>Feed</span><strong>{ctx['F']:.1f}</strong></div>
        <div class="mini-metric"><span>R</span><strong>{ctx['R']:.2f}</strong></div>
        <div class="mini-metric"><span>Qreb</span><strong>{ctx['Q_reb']:.0f} kW</strong></div>
        <div class="mini-metric"><span>Qcond</span><strong>{ctx['Q_cond']:.0f} kW</strong></div>
      </div>
      <div class="plant">
        <div class="cool-glow"></div>
        <div class="heat-glow"></div>
        <svg class="pipe" style="left:10%;top:90px;width:84%;height:600px" viewBox="0 0 1000 650">
          <path d="M 0 310 L 330 310" stroke="#22c55e"/>
          <path d="M 455 30 L 455 0 L 640 0 L 640 44" stroke="#fbbf24"/>
          <path d="M 740 84 L 740 164" stroke="#7dd3fc"/>
          <path d="M 716 202 L 520 202 L 520 80" stroke="#38bdf8"/>
          <path d="M 818 202 L 990 202" stroke="#22c55e"/>
          <path d="M 456 570 L 456 630 L 760 630" stroke="#ef4444"/>
          <path d="M 418 570 L 418 640" stroke="#f59e0b"/>
          <path d="M 835 18 L 990 18" stroke="#60a5fa"/>
        </svg>
        <div class="column-shell">
          <div class="composition-band"></div>
          <div class="section-band rectifying"></div>
          <div class="section-band stripping"></div>
          <div class="side-rail temp-rail"></div>
          <div class="side-rail comp-rail"></div>
          <div class="internals">
            {_tray_or_packed_markup(col_type, tray_count)}
          </div>
          <div class="feed-marker"></div>
          <div class="feed-spray"></div>
          <div class="tag top">PT<br>{ctx['P_prof'][0]:.2f}</div>
          <div class="tag feed">FT<br>{ctx['NF']}</div>
          <div class="tag bottom">TT<br>{ctx['T_prof'][-1]:.0f}C</div>
        </div>
        <div class="equipment condenser">CONDENSER<br><small>{ctx['Q_cond']:.0f} kW removed</small></div>
        <div class="equipment drum">REFLUX<br>DRUM</div>
        <div class="equipment reboiler">REBOILER<br><small>{ctx['Q_reb']:.0f} kW</small></div>
        <div class="control-valve feed"></div>
        <div class="control-valve reflux"></div>
        <div class="control-valve product"></div>
        <div class="small-pump reflux"></div>
        <div class="small-pump bottoms"></div>
        {_particles_markup(particle_count)}
        <div class="pipe-label" style="left:10%; top:305px;">Feed F={ctx['F']:.1f} kmol/h<br>zF={ctx['z_F']:.3f}</div>
        <div class="pipe-label" style="left:68%; top:226px;">Distillate D={ctx['D_flow']:.1f}<br>xD={ctx['x_D']:.3f}</div>
        <div class="pipe-label" style="left:67%; top:648px;">Bottoms B={ctx['B_flow']:.1f}<br>xB={ctx['x_B']:.3f}</div>
        <div class="pipe-label" style="left:56%; top:292px;">Reflux L={reflux_flow:.1f}<br>Vapor V={vapor_flow:.1f}</div>
        <div class="phase-panel">
          <h3>What the animation is showing</h3>
          <p><b>{mode_label}</b> auto-selected from app state.</p>
          <p>Feed enters near stage/zone <b>{ctx['NF']}</b>; vapor rises from the reboiler while liquid/reflux flows downward.</p>
          <p>Column color follows composition profile: lean bottoms blue to rich distillate red.</p>
          <p>Internal liquid estimate: <b>{liquid_flow:.1f} kmol/h</b>.</p>
        </div>
      </div>
      <div class="legend">
        <span><i class="dot" style="background:#fbbf24"></i>Vapour rising</span>
        <span><i class="dot" style="background:#7dd3fc"></i>Liquid/reflux falling</span>
        <span><i class="dot" style="background:#86efac"></i>Feed/distillate</span>
        <span><i class="dot" style="background:#fca5a5"></i>Bottoms product</span>
      </div>
    </div>
    """
    components.html(html, height=910, scrolling=False)


def _render_reflux_slider(ctx):
    st.markdown("### Interactive Reflux Ratio Slider")
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        r_low = max(0.05, ctx["R_min"] * 1.01)
        r_high = max(r_low + 0.5, ctx["R_min"] * 4.0, ctx["R"] * 2.0)
        R_live = st.slider("Reflux Ratio R", min_value=float(r_low), max_value=float(r_high), value=float(np.clip(ctx["R"], r_low, r_high)), step=0.01)
    with c2:
        alpha_live = st.slider("Relative Volatility alpha", 1.05, 8.0, float(np.clip(ctx["alpha"], 1.05, 8.0)), 0.01)
    show_numbers = c3.checkbox("Show stage numbers", value=True)

    result = _safe_mccabe(alpha_live, R_live, ctx["x_D"], ctx["x_B"], ctx["z_F"], ctx["q"])
    n_stages = result["n_stages"]
    actual_trays = int(math.ceil(n_stages / max(float(ctx["tray_design"].get("tray_efficiency", 0.70) or 0.70), 0.01)))

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Theoretical Stages", n_stages)
    m2.metric("Estimated Actual Trays", actual_trays)
    m3.metric("Rectifying", result["n_rectifying"])
    m4.metric("Stripping", result["n_stripping"])

    fig = _mccabe_figure(ctx, R_live, alpha_live, result, show_numbers=show_numbers)
    st.plotly_chart(fig, use_container_width=True)

    sweep_R = np.linspace(r_low, r_high, 35)
    sweep_N = [_safe_mccabe(alpha_live, r, ctx["x_D"], ctx["x_B"], ctx["z_F"], ctx["q"])["n_stages"] for r in sweep_R]
    fig_s = go.Figure()
    fig_s.add_trace(go.Scatter(x=sweep_R, y=sweep_N, mode="lines+markers", line=dict(color="#22c55e", width=3), name="N vs R"))
    fig_s.add_vline(x=R_live, line_dash="dot", line_color="#f59e0b", annotation_text=f"R={R_live:.2f}")
    fig_s.update_layout(
        title="Stage Count Sensitivity to Reflux Ratio",
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font_color=TEXT,
        height=340,
        xaxis=dict(title="Reflux Ratio R", gridcolor=GRID),
        yaxis=dict(title="Theoretical Stages", gridcolor=GRID),
    )
    st.plotly_chart(fig_s, use_container_width=True)


def _render_pfd(ctx):
    st.markdown("### Complete Process Flow Diagram")
    fig = go.Figure()
    H = 10
    # Equipment blocks
    _box(fig, 4.0, 1.2, 6.0, 9.0, "DISTILLATION\nCOLUMN", "#00b4d8")
    _box(fig, 7.3, 8.2, 9.6, 9.45, "CONDENSER", "#90e0ef")
    _box(fig, 7.55, 6.15, 9.35, 7.1, "REFLUX\nDRUM", "#22c55e")
    _box(fig, 4.0, -0.3, 6.0, 0.75, "REBOILER", "#f59e0b")

    # Main process lines
    _arrow(fig, 0.7, 5.0, 4.0, 5.0, "#f59e0b", f"Feed\nF={ctx['F']:.1f} kmol/h\nzF={ctx['z_F']:.3f}")
    _arrow(fig, 5.0, 9.0, 5.0, 9.8, "#22c55e", "Overhead vapor")
    _arrow(fig, 5.0, 9.8, 7.3, 8.9, "#22c55e", f"V={(ctx['R'] + 1) * ctx['D_flow']:.1f} kmol/h")
    _arrow(fig, 9.6, 8.85, 10.9, 8.85, "#00b4d8", "Cooling water")
    _arrow(fig, 8.45, 8.2, 8.45, 7.1, "#90e0ef", "Condensate")
    _arrow(fig, 9.35, 6.65, 11.2, 6.65, "#22c55e", f"Distillate\nD={ctx['D_flow']:.1f} kmol/h\nxD={ctx['x_D']:.3f}")
    _arrow(fig, 7.55, 6.55, 6.0, 6.55, "#38bdf8", f"Reflux\nL={ctx['R'] * ctx['D_flow']:.1f} kmol/h\nR={ctx['R']:.2f}")
    _arrow(fig, 5.0, 1.2, 5.0, 0.75, "#ef4444", "Bottom liquid")
    _arrow(fig, 5.0, -0.3, 5.0, 1.2, "#f59e0b", "Boilup")
    _arrow(fig, 5.0, -0.3, 6.9, -0.3, "#ef4444", f"Bottoms\nB={ctx['B_flow']:.1f} kmol/h\nxB={ctx['x_B']:.3f}")
    _arrow(fig, 3.1, 0.2, 4.0, 0.2, "#f97316", f"Steam\nQreb={ctx['Q_reb']:.0f} kW")
    _arrow(fig, 9.6, 9.35, 10.9, 9.35, "#60a5fa", f"Qcond={ctx['Q_cond']:.0f} kW")

    # Column internals
    tray_y = np.linspace(1.6, 8.6, min(ctx["N_actual"], 18))
    for y in tray_y:
        fig.add_shape(type="line", x0=4.25, x1=5.75, y0=y, y1=y, line=dict(color="#164e63", width=1))
    feed_y = 8.6 - (ctx["NF"] - 1) / max(ctx["N_actual"] - 1, 1) * 7.0
    fig.add_shape(type="line", x0=4.0, x1=6.0, y0=feed_y, y1=feed_y, line=dict(color="#22c55e", width=3))
    fig.add_annotation(x=6.08, y=feed_y, text=f"Feed tray {ctx['NF']}", showarrow=False, xanchor="left", font=dict(color="#22c55e", size=11))

    fig.update_layout(
        title="Aspen-style PFD with Stream Flow Rates",
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font_color=TEXT,
        height=720,
        xaxis=dict(range=[0, 12], visible=False),
        yaxis=dict(range=[-1.0, 10.4], visible=False, scaleanchor="x", scaleratio=0.75),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

    streams = pd.DataFrame(
        [
            ["Feed", ctx["F"], ctx["z_F"], ctx["T_prof"][ctx["NF"] - 1], ctx["P_col"]],
            ["Distillate", ctx["D_flow"], ctx["x_D"], ctx["T_prof"][0], ctx["P_prof"][0]],
            ["Bottoms", ctx["B_flow"], ctx["x_B"], ctx["T_prof"][-1], ctx["P_prof"][-1]],
            ["Reflux", ctx["R"] * ctx["D_flow"], ctx["x_D"], ctx["T_prof"][0], ctx["P_prof"][0]],
            ["Boilup", (ctx["R"] + 1) * ctx["D_flow"], ctx["y_prof"][-1], ctx["T_prof"][-1], ctx["P_prof"][-1]],
        ],
        columns=["Stream", "Flow [kmol/h]", "Light fraction", "T [C]", "P [bar]"],
    )
    st.dataframe(streams.round(3), use_container_width=True, hide_index=True)


def _render_3d_color_trays(ctx):
    st.markdown("### 3D Color-coded Tray Composition Animation")
    animate = st.checkbox("Enable tray sweep animation frames", value=True)
    fig = _3d_column_figure(ctx, animate=animate)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Tray color follows light-component liquid composition: blue = lean bottom, red = rich top.")


def _render_phase_diagrams(ctx):
    st.markdown("### T-x-y Phase Diagram and VLE Curve")
    x = np.linspace(0.001, 0.999, 300)
    y = ctx["alpha"] * x / (1 + (ctx["alpha"] - 1) * x)
    T_top = float(ctx["T_prof"][0])
    T_bot = float(ctx["T_prof"][-1])
    bubble = T_bot - (T_bot - T_top) * x
    dew = T_bot - (T_bot - T_top) * y

    fig = make_subplots(rows=1, cols=2, subplot_titles=("T-x-y Diagram", "x-y Equilibrium"))
    fig.add_trace(go.Scatter(x=x, y=bubble, name="Bubble line", line=dict(color="#f59e0b", width=3)), row=1, col=1)
    fig.add_trace(go.Scatter(x=y, y=dew, name="Dew line", line=dict(color="#00b4d8", width=3)), row=1, col=1)
    fig.add_trace(
        go.Scatter(x=[ctx["x_B"], ctx["z_F"], ctx["x_D"]], y=[T_bot, np.interp(ctx["z_F"], x, bubble), T_top], mode="markers+text", text=["xB", "zF", "xD"], marker=dict(size=11, color=["#ef4444", "#f59e0b", "#22c55e"]), name="Design points"),
        row=1,
        col=1,
    )
    fig.add_trace(go.Scatter(x=x, y=y, name="Equilibrium", line=dict(color="#22c55e", width=3)), row=1, col=2)
    fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], name="y=x", line=dict(color="#64748b", dash="dash")), row=1, col=2)
    fig.add_trace(go.Scatter(x=ctx["x_prof"], y=ctx["y_prof"], mode="markers", marker=dict(size=7, color=ctx["stages"], colorscale="Viridis", colorbar=dict(title="Stage")), name="Tray points"), row=1, col=2)
    fig.update_xaxes(title_text="Mole fraction light component", gridcolor=GRID)
    fig.update_yaxes(title_text="Temperature [C]", gridcolor=GRID, row=1, col=1)
    fig.update_yaxes(title_text="Vapor mole fraction y", gridcolor=GRID, row=1, col=2)
    fig.update_layout(paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG, font_color=TEXT, height=520, legend=dict(bgcolor=PAPER_BG))
    st.plotly_chart(fig, use_container_width=True)


def _render_flow_profiles(ctx):
    st.markdown("### Internal Liquid/Vapor Flow Profiles")
    stages = ctx["stages"]
    L_rect = ctx["R"] * ctx["D_flow"]
    V_rect = (ctx["R"] + 1) * ctx["D_flow"]
    L_strip = L_rect + ctx["q"] * ctx["F"]
    V_strip = V_rect - (1 - ctx["q"]) * ctx["F"]
    L = np.where(stages <= ctx["NF"], L_rect, L_strip)
    V = np.where(stages <= ctx["NF"], V_rect, max(V_strip, 0.001))
    lv = L / np.maximum(V, 1e-6)

    fig = make_subplots(rows=1, cols=2, subplot_titles=("Internal Flows by Stage", "L/V Ratio"))
    fig.add_trace(go.Scatter(x=stages, y=L, mode="lines+markers", name="Liquid L", line=dict(color="#00b4d8", width=3)), row=1, col=1)
    fig.add_trace(go.Scatter(x=stages, y=V, mode="lines+markers", name="Vapor V", line=dict(color="#f59e0b", width=3)), row=1, col=1)
    fig.add_trace(go.Bar(x=stages, y=lv, name="L/V", marker_color="#22c55e"), row=1, col=2)
    fig.add_vline(x=ctx["NF"], line_dash="dot", line_color="#ef4444", annotation_text="Feed", row=1, col=1)
    fig.add_vline(x=ctx["NF"], line_dash="dot", line_color="#ef4444", row=1, col=2)
    fig.update_xaxes(title_text="Stage", gridcolor=GRID)
    fig.update_yaxes(title_text="Flow [kmol/h]", gridcolor=GRID, row=1, col=1)
    fig.update_yaxes(title_text="L/V", gridcolor=GRID, row=1, col=2)
    fig.update_layout(paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG, font_color=TEXT, height=480, legend=dict(bgcolor=PAPER_BG))
    st.plotly_chart(fig, use_container_width=True)


def _render_energy_sankey(ctx):
    st.markdown("### Energy Sankey Diagram")
    heat_loss = max((ctx["Q_reb"] + ctx["Q_cond"]) * 0.04, 1.0)
    feed_preheat = min(ctx["Q_reb"], ctx["Q_cond"]) * 0.20
    fig = go.Figure(
        go.Sankey(
            arrangement="snap",
            node=dict(
                pad=18,
                thickness=18,
                line=dict(color="#1f2937", width=1),
                label=["Steam", "Reboiler", "Column", "Condenser", "Cooling Water", "Recoverable Heat", "Losses"],
                color=["#f97316", "#f59e0b", "#00b4d8", "#38bdf8", "#2563eb", "#22c55e", "#64748b"],
            ),
            link=dict(
                source=[0, 1, 2, 2, 3, 3],
                target=[1, 2, 3, 6, 4, 5],
                value=[ctx["Q_reb"], ctx["Q_reb"], ctx["Q_cond"], heat_loss, ctx["Q_cond"], feed_preheat],
                color=["rgba(249,115,22,.45)", "rgba(245,158,11,.45)", "rgba(56,189,248,.45)", "rgba(100,116,139,.35)", "rgba(37,99,235,.45)", "rgba(34,197,94,.45)"],
            ),
        )
    )
    fig.update_layout(title="Column Energy Flow [kW]", paper_bgcolor=PAPER_BG, font_color=TEXT, height=500)
    st.plotly_chart(fig, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Reboiler Duty", f"{ctx['Q_reb']:,.0f} kW")
    c2.metric("Condenser Duty", f"{ctx['Q_cond']:,.0f} kW")
    c3.metric("Heat Recovery Potential", f"{feed_preheat:,.0f} kW")


def _render_tray_hydraulics(ctx):
    st.markdown("### Tray Cross-section and Hydraulic Operating Window")
    tray = ctx["tray_design"]
    D = ctx["D_col"]
    r = D / 2
    dc_frac = float(tray.get("downcomer_area_fraction", 0.12) or 0.12)
    active_frac = max(1 - dc_frac, 0.5)
    u_op = float(tray.get("u_operating_m_s", tray.get("u_op_m_s", 1.0)) or 1.0)
    u_flood = float(tray.get("u_flood_m_s", max(u_op / 0.8, 1.2)) or max(u_op / 0.8, 1.2))
    turndown = float(tray.get("turndown", tray.get("turndown_ratio", 3.0)) or 3.0)
    dP = float(tray.get("dP_tray_Pa", 500.0) or 500.0)
    backup_pct = float(tray.get("downcomer_backup_pct", 35.0) or 35.0)
    weir_h = float(tray.get("weir_height_mm", 50.0) or 50.0)

    c1, c2 = st.columns([1, 1])
    with c1:
        fig = go.Figure()
        theta = np.linspace(0, 2 * np.pi, 200)
        fig.add_trace(go.Scatter(x=r * np.cos(theta), y=r * np.sin(theta), mode="lines", line=dict(color="#00b4d8", width=3), name="Shell"))
        chord_x = -r + 2 * r * dc_frac
        fig.add_shape(type="rect", x0=-r, x1=chord_x, y0=-r, y1=r, fillcolor="rgba(34,197,94,.20)", line=dict(color="#22c55e", width=2))
        fig.add_shape(type="rect", x0=chord_x, x1=r, y0=-r, y1=r, fillcolor="rgba(0,180,216,.12)", line=dict(color="#00b4d8", width=1))
        holes_x, holes_y = [], []
        for xx in np.linspace(chord_x + 0.12 * D, r - 0.12 * D, 9):
            for yy in np.linspace(-0.36 * D, 0.36 * D, 7):
                if xx * xx + yy * yy < (0.42 * D) ** 2:
                    holes_x.append(xx)
                    holes_y.append(yy)
        fig.add_trace(go.Scatter(x=holes_x, y=holes_y, mode="markers", marker=dict(size=5, color="#93c5fd"), name="Vapor holes"))
        fig.add_annotation(x=(chord_x - r) / 2, y=0, text="Downcomer", showarrow=False, font=dict(color="#22c55e"))
        fig.add_annotation(x=(chord_x + r) / 2, y=0.45 * D, text=f"Weir {weir_h:.0f} mm", showarrow=False, font=dict(color="#f59e0b"))
        fig.update_layout(title="Tray Cross-section", paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG, font_color=TEXT, height=430, xaxis=dict(visible=False), yaxis=dict(visible=False, scaleanchor="x"), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        load = np.linspace(0.25, 1.15, 80)
        flood_pct = load * u_op / max(u_flood, 1e-6) * 100
        weep_margin = (load - 0.35) / 0.65 * 100
        dp_curve = dP * load**2
        fig = make_subplots(rows=2, cols=1, subplot_titles=("Flooding / Weeping Window", "Pressure Drop Curve"), vertical_spacing=0.18)
        fig.add_trace(go.Scatter(x=load * 100, y=flood_pct, name="Flooding %", line=dict(color="#ef4444", width=3)), row=1, col=1)
        fig.add_trace(go.Scatter(x=load * 100, y=weep_margin, name="Weeping margin", line=dict(color="#22c55e", width=3)), row=1, col=1)
        fig.add_hrect(y0=60, y1=85, fillcolor="rgba(34,197,94,.13)", line_width=0, row=1, col=1)
        fig.add_trace(go.Scatter(x=load * 100, y=dp_curve, name="dP/tray", line=dict(color="#00b4d8", width=3)), row=2, col=1)
        fig.add_vline(x=100, line_dash="dot", line_color="#f59e0b", annotation_text="Design", row=1, col=1)
        fig.add_vline(x=100, line_dash="dot", line_color="#f59e0b", row=2, col=1)
        fig.update_xaxes(title_text="Percent of design vapor load", gridcolor=GRID)
        fig.update_yaxes(gridcolor=GRID)
        fig.update_layout(paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG, font_color=TEXT, height=430, legend=dict(bgcolor=PAPER_BG))
        st.plotly_chart(fig, use_container_width=True)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Active Area", f"{active_frac * 100:.0f}%")
    m2.metric("Flooding at Design", f"{u_op / max(u_flood, 1e-6) * 100:.0f}%")
    m3.metric("Turndown", f"{turndown:.1f}:1")
    m4.metric("DC Backup", f"{backup_pct:.0f}% spacing")


def _render_economics(ctx):
    st.markdown("### CAPEX/OPEX Visualization")
    D = ctx["D_col"]
    H = ctx["H_total"]
    shell_cost = 17640 + 79.4 * (7850 * np.pi * D * H * 0.010)
    reboiler_cost = 10000 + 500 * max(ctx["reboiler"].get("A_reb_m2", 20.0), 1.0) ** 0.85
    condenser_cost = 10000 + 500 * max(ctx["condenser"].get("A_cond_m2", 18.0), 1.0) ** 0.85
    internals_cost = shell_cost * 0.15
    instrumentation_cost = shell_cost * 0.20
    capex = {
        "Column Shell": shell_cost,
        "Reboiler": reboiler_cost,
        "Condenser": condenser_cost,
        "Internals": internals_cost,
        "Instrumentation": instrumentation_cost,
    }
    steam_cost = ctx["Q_reb"] * 3600 * 8000 / 1e9 * 15.0
    cooling_cost = ctx["Q_cond"] * 3600 * 8000 / 1e9 * 0.8
    maintenance = sum(capex.values()) * 0.03
    labor = 150000.0
    opex = {"Steam": steam_cost, "Cooling": cooling_cost, "Maintenance": maintenance, "Labor": labor}

    fig = make_subplots(rows=1, cols=2, specs=[[{"type": "domain"}, {"type": "xy"}]], subplot_titles=("CAPEX Breakdown", "Annual OPEX"))
    fig.add_trace(go.Pie(labels=list(capex.keys()), values=list(capex.values()), hole=0.45, marker_colors=["#0077b6", "#f59e0b", "#00b4d8", "#22c55e", "#a855f7"], name="CAPEX"), row=1, col=1)
    fig.add_trace(go.Bar(x=list(opex.keys()), y=list(opex.values()), marker_color=["#f97316", "#38bdf8", "#ef4444", "#22c55e"], text=[f"${v/1000:.0f}k" for v in opex.values()], textposition="outside", name="OPEX"), row=1, col=2)
    fig.update_yaxes(title_text="USD/yr", gridcolor=GRID, row=1, col=2)
    fig.update_layout(paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG, font_color=TEXT, height=470, showlegend=True, legend=dict(bgcolor=PAPER_BG))
    st.plotly_chart(fig, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Bare Equipment CAPEX", f"${sum(capex.values()):,.0f}")
    c2.metric("Annual OPEX", f"${sum(opex.values()):,.0f}/yr")
    c3.metric("Energy Share of OPEX", f"{(steam_cost + cooling_cost) / max(sum(opex.values()), 1) * 100:.1f}%")


def _render_dashboard(ctx):
    st.markdown("### Combined Engineering Dashboard")
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown("#### Key Design Parameters")
        params = {
            "Column Diameter": f"{ctx['D_col']:.2f} m",
            "Total Height": f"{ctx['H_total']:.1f} m",
            "Actual Stages": f"{ctx['N_actual']}",
            "Feed Stage": f"{ctx['NF']}",
            "Distillate xD": f"{ctx['x_D']:.3f}",
            "Feed zF": f"{ctx['z_F']:.3f}",
            "Bottoms xB": f"{ctx['x_B']:.3f}",
            "Operating P": f"{ctx['P_col']:.3f} bar",
            "Reboiler Duty": f"{ctx['Q_reb']:.0f} kW",
            "Condenser Duty": f"{ctx['Q_cond']:.0f} kW",
        }
        for key, val in params.items():
            st.metric(key, val)
    with c2:
        result = _safe_mccabe(ctx["alpha"], ctx["R"], ctx["x_D"], ctx["x_B"], ctx["z_F"], ctx["q"])
        st.plotly_chart(_mccabe_figure(ctx, ctx["R"], ctx["alpha"], result, show_numbers=False, compact=True), use_container_width=True)
        st.plotly_chart(_3d_column_figure(ctx, animate=False, compact=True), use_container_width=True)


def _mccabe_figure(ctx, R, alpha, result, show_numbers=False, compact=False):
    x = np.linspace(0, 1, 500)
    y_eq = alpha * x / (1 + (alpha - 1) * x)
    slope_rect = R / (R + 1)
    y_rect = slope_rect * x + ctx["x_D"] / (R + 1)
    x_int, y_int = result["x_int"], result["y_int"]
    if abs(x_int - ctx["x_B"]) > 1e-8:
        slope_strip = (y_int - ctx["x_B"]) / (x_int - ctx["x_B"])
    else:
        slope_strip = 1.5
    y_strip = slope_strip * x + ctx["x_B"] * (1 - slope_strip)

    stage_x = [ctx["x_D"]]
    stage_y = [ctx["x_D"]]
    stages = result["stages"]
    for i, s in enumerate(stages):
        stage_x.append(s["x"])
        stage_y.append(s["y"])
        next_y = stages[i + 1]["y"] if i + 1 < len(stages) else ctx["x_B"]
        stage_x.append(s["x"])
        stage_y.append(next_y)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y_eq, name="Equilibrium curve", line=dict(color="#00b4d8", width=3)))
    fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], name="y=x", line=dict(color="#64748b", width=1, dash="dash")))
    fig.add_trace(go.Scatter(x=x, y=np.clip(y_rect, 0, 1), name="Rectifying OL", line=dict(color="#22c55e", width=2.3)))
    fig.add_trace(go.Scatter(x=x, y=np.clip(y_strip, 0, 1), name="Stripping OL", line=dict(color="#f59e0b", width=2.3)))
    fig.add_trace(go.Scatter(x=stage_x, y=stage_y, name=f"Stages ({result['n_stages']})", line=dict(color="#ef4444", width=2), mode="lines"))
    fig.add_trace(
        go.Scatter(
            x=[ctx["x_D"], ctx["z_F"], ctx["x_B"], x_int],
            y=[ctx["x_D"], ctx["z_F"], ctx["x_B"], y_int],
            mode="markers+text",
            marker=dict(size=10, color=["#22c55e", "#c084fc", "#ef4444", "#f59e0b"]),
            text=["xD", "zF", "xB", "pinch"],
            textposition="top center",
            name="Key points",
        )
    )
    if show_numbers:
        for i, s in enumerate(stages):
            fig.add_annotation(x=s["x"], y=s["y"], text=str(i + 1), showarrow=False, font=dict(size=9, color="#fde68a"), bgcolor="rgba(0,0,0,.45)")
    fig.update_layout(
        title=f"Live McCabe-Thiele: R={R:.2f}, alpha={alpha:.2f}, N={result['n_stages']}",
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font_color=TEXT,
        height=430 if compact else 610,
        xaxis=dict(title="x liquid mole fraction", range=[0, 1], gridcolor=GRID),
        yaxis=dict(title="y vapor mole fraction", range=[0, 1], gridcolor=GRID),
        legend=dict(bgcolor=PAPER_BG),
        margin=dict(t=50, b=45, l=50, r=20),
    )
    return fig


def _3d_column_figure(ctx, animate=False, compact=False):
    D_col = ctx["D_col"]
    H_total = ctx["H_total"]
    r = D_col / 2
    theta = np.linspace(0, 2 * np.pi, 72)
    z_col = np.linspace(0, H_total, 70)
    theta_grid, z_grid = np.meshgrid(theta, z_col)
    x_surf = r * np.cos(theta_grid)
    y_surf = r * np.sin(theta_grid)

    fig = go.Figure()
    fig.add_trace(
        go.Surface(
            x=x_surf,
            y=y_surf,
            z=z_grid,
            colorscale=[[0, "#0f172a"], [0.55, "#164e63"], [1, "#0369a1"]],
            opacity=0.32,
            showscale=False,
            name="Column shell",
        )
    )
    tray_spacing = H_total / (ctx["N_actual"] + 1)
    tray_colors = _composition_colors(ctx["x_prof"], ctx["x_B"], ctx["x_D"])
    for i, color in enumerate(tray_colors, start=1):
        z_t = H_total - i * tray_spacing
        rr = r * 0.93
        x_t = rr * np.cos(theta)
        y_t = rr * np.sin(theta)
        fig.add_trace(
            go.Scatter3d(
                x=x_t,
                y=y_t,
                z=[z_t] * len(theta),
                mode="lines",
                line=dict(color=color, width=6 if i == ctx["NF"] else 4),
                hovertemplate=f"Tray {i}<br>x={ctx['x_prof'][i-1]:.3f}<extra></extra>",
                showlegend=False,
            )
        )
    feed_z = H_total - ctx["NF"] * tray_spacing
    fig.add_trace(go.Scatter3d(x=[-2 * r, -r], y=[0, 0], z=[feed_z, feed_z], mode="lines+text", text=["Feed", ""], line=dict(color="#f59e0b", width=8), textfont=dict(color="#f59e0b"), name="Feed"))
    fig.add_trace(go.Scatter3d(x=[0, 0], y=[0, 0], z=[H_total, H_total + 1], mode="lines+text", text=["", "Distillate"], line=dict(color="#22c55e", width=6), textfont=dict(color="#22c55e"), name="Distillate"))
    fig.add_trace(go.Scatter3d(x=[0, 0], y=[0, 0], z=[0, -1], mode="lines+text", text=["", "Bottoms"], line=dict(color="#ef4444", width=6), textfont=dict(color="#ef4444"), name="Bottoms"))

    if animate:
        frames = []
        for j in range(0, ctx["N_actual"], max(1, ctx["N_actual"] // 20)):
            frames.append(
                go.Frame(
                    name=str(j + 1),
                    data=[
                        go.Scatter3d(
                            x=[0],
                            y=[0],
                            z=[H_total - (j + 1) * tray_spacing],
                            mode="markers+text",
                            marker=dict(size=10, color="#fde047"),
                            text=[f"Tray {j + 1}: x={ctx['x_prof'][j]:.3f}"],
                            textfont=dict(color="#fde047"),
                            showlegend=False,
                        )
                    ],
                    traces=[len(fig.data)],
                )
            )
        fig.add_trace(go.Scatter3d(x=[0], y=[0], z=[H_total], mode="markers", marker=dict(size=1, color="#fde047"), showlegend=False))
        fig.frames = frames
        fig.update_layout(
            updatemenus=[
                {
                    "type": "buttons",
                    "buttons": [
                        {
                            "label": "Play tray sweep",
                            "method": "animate",
                            "args": [None, {"frame": {"duration": 250, "redraw": True}, "fromcurrent": True}],
                        }
                    ],
                    "x": 0.02,
                    "y": 0.02,
                }
            ]
        )

    fig.update_layout(
        title=f"3D Composition Map - blue to red trays | D={D_col:.2f} m, H={H_total:.1f} m",
        scene=dict(
            bgcolor=PLOT_BG,
            xaxis=dict(backgroundcolor=PLOT_BG, gridcolor=GRID, title="X [m]"),
            yaxis=dict(backgroundcolor=PLOT_BG, gridcolor=GRID, title="Y [m]"),
            zaxis=dict(backgroundcolor=PLOT_BG, gridcolor=GRID, title="Height [m]"),
            camera=dict(eye=dict(x=1.8, y=1.9, z=1.35)),
        ),
        paper_bgcolor=PAPER_BG,
        font_color=TEXT,
        height=420 if compact else 680,
        legend=dict(bgcolor=PAPER_BG),
        margin=dict(t=50, b=10, l=10, r=10),
    )
    return fig


def _safe_mccabe(alpha, R, x_D, x_B, z_F, q):
    try:
        return mccabe_thiele_stages(alpha, R, x_D, x_B, z_F, q)
    except Exception:
        return {
            "stages": [],
            "n_stages": 0,
            "n_rectifying": 0,
            "n_stripping": 0,
            "x_int": z_F,
            "y_int": z_F,
            "slope_rectifying": R / (R + 1),
            "slope_stripping": 1.5,
        }


def _box(fig, x0, y0, x1, y1, label, color):
    fig.add_shape(type="rect", x0=x0, x1=x1, y0=y0, y1=y1, line=dict(color=color, width=2.5), fillcolor="rgba(13,21,32,.82)")
    fig.add_annotation(x=(x0 + x1) / 2, y=(y0 + y1) / 2, text=label, showarrow=False, font=dict(color=color, size=12), align="center")


def _arrow(fig, x0, y0, x1, y1, color, label):
    fig.add_annotation(x=x1, y=y1, ax=x0, ay=y0, xref="x", yref="y", axref="x", ayref="y", text=label, showarrow=True, arrowhead=3, arrowwidth=2.5, arrowcolor=color, font=dict(color=color, size=10), bgcolor="rgba(10,14,20,.70)", bordercolor=color, borderpad=3)


def _composition_colors(values, lo, hi):
    colors = []
    for value in values:
        t = (float(value) - lo) / max(hi - lo, 1e-6)
        t = _clip(t, 0.0, 1.0)
        if t < 0.5:
            u = t / 0.5
            c0 = np.array([29, 78, 216])
            c1 = np.array([250, 204, 21])
        else:
            u = (t - 0.5) / 0.5
            c0 = np.array([250, 204, 21])
            c1 = np.array([220, 38, 38])
        rgb = (c0 + (c1 - c0) * u).astype(int)
        colors.append(f"rgb({rgb[0]},{rgb[1]},{rgb[2]})")
    return colors


def _css_composition_gradient(values, lo, hi):
    colors = _composition_colors(values, lo, hi)
    if not colors:
        return "linear-gradient(180deg, #dc2626, #1d4ed8)"
    stops = []
    for idx, color in enumerate(colors):
        pct = idx / max(len(colors) - 1, 1) * 100
        stops.append(f"{color} {pct:.1f}%")
    return "linear-gradient(180deg, " + ", ".join(stops) + ")"


def _tray_or_packed_markup(col_type, tray_count):
    if col_type == "packed":
        return (
            '<div class="packed-bed"></div>'
            '<div class="packing-grid top"></div>'
            '<div class="packing-grid mid"></div>'
            '<div class="packing-grid bottom"></div>'
        )
    trays = []
    for i in range(tray_count):
        top = 4 + i * (92 / max(tray_count - 1, 1))
        trays.append(f'<span class="tray" style="top:{top:.2f}%"></span>')
    return "\n".join(trays)


def _particles_markup(count):
    parts = []
    classes = ["vap", "liq", "feedp", "refluxp", "distp", "bottomp"]
    for i in range(count):
        cls = classes[i % len(classes)]
        delay = -1 * (i * 0.19)
        size = 6 + (i % 4)
        parts.append(f'<span class="particle {cls}" style="animation-delay:{delay:.2f}s;width:{size}px;height:{size}px"></span>')
    return "\n".join(parts)


def _clip(value, lo, hi):
    try:
        return float(np.clip(float(value), lo, hi))
    except Exception:
        return float(lo)


def _as_int(value, default):
    try:
        return int(math.ceil(float(value)))
    except Exception:
        return int(default)

