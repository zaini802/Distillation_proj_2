"""Shared visual polish for detailed-design sections."""
import streamlit as st


def render_phase3_style():
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
    .phase3-calc-separator {
        border-top: 1px dashed rgba(248, 212, 119, 0.48);
        margin: 0.85rem 0;
    }
    .phase3-check-row {
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
    .phase3-check-label {
        color: #f8fbff !important;
        font-weight: 900;
    }
    .phase3-check-value {
        font-family: 'Share Tech Mono', monospace;
        font-weight: 900;
        text-align: right;
        overflow-wrap: anywhere;
    }
    </style>
    """, unsafe_allow_html=True)
