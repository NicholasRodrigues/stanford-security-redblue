"""Dark cybersecurity theme for the Streamlit app."""

import streamlit as st

COLORS = {
    "bg_dark": "#0a0a1a",
    "bg_card": "#111827",
    "bg_card_hover": "#1a2332",
    "red": "#ef4444",
    "red_dim": "#7f1d1d",
    "green": "#22c55e",
    "green_dim": "#14532d",
    "accent": "#e94560",
    "blue": "#3b82f6",
    "text": "#e0e0e0",
    "text_dim": "#9ca3af",
    "border": "#1f2937",
}


def apply_theme():
    """Inject custom CSS for the cybersecurity dark theme."""
    st.markdown("""
    <style>
    /* Concept cards */
    .concept-card {
        background: linear-gradient(135deg, #111827 0%, #1a2332 100%);
        border: 1px solid #1f2937;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        margin-bottom: 0.8rem;
    }
    .concept-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(233, 69, 96, 0.15);
        border-color: #e94560;
    }
    .card-icon { font-size: 2rem; margin-bottom: 0.3rem; }
    .card-title { font-size: 1rem; font-weight: 700; color: #e0e0e0; margin: 0.3rem 0; }
    .card-analogy { color: #e94560; font-weight: 600; font-size: 0.8rem; }

    /* Verdict badges */
    .verdict-leaked {
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: white;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 1.1rem;
        display: inline-block;
        animation: pulse-red 1.5s infinite;
    }
    .verdict-blocked {
        background: linear-gradient(135deg, #22c55e, #16a34a);
        color: white;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 1.1rem;
        display: inline-block;
    }
    @keyframes pulse-red {
        0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }
        100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
    }

    /* Phase stepper */
    .phase-step {
        padding: 0.8rem 1rem;
        border-left: 3px solid #1f2937;
        margin-bottom: 0.5rem;
        border-radius: 0 8px 8px 0;
    }
    .phase-active {
        border-left-color: #e94560;
        background: rgba(233, 69, 96, 0.1);
    }
    .phase-done {
        border-left-color: #22c55e;
        background: rgba(34, 197, 94, 0.05);
    }
    .phase-pending {
        opacity: 0.5;
    }

    /* Hero section */
    .hero-container {
        text-align: center;
        padding: 2rem 0;
    }
    .hero-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #ef4444, #e94560, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .hero-subtitle {
        font-size: 1.1rem;
        color: #9ca3af;
        max-width: 600px;
        margin: 0 auto;
    }

    /* Evidence pills */
    .evidence-pill {
        display: inline-block;
        background: #1f2937;
        color: #ef4444;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        margin: 2px;
        border: 1px solid #374151;
    }

    /* KPI metrics override */
    [data-testid="stMetric"] {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 12px;
        padding: 1rem;
    }

    /* Team credit */
    .team-credit {
        text-align: center;
        color: #6b7280;
        font-size: 0.75rem;
        padding: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)
