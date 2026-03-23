"""Visao Geral — overview page with concept mapping."""

import streamlit as st

from src.streamlit_app.components.concept_cards import render_concept_grid
from src.streamlit_app.concepts.mapping import ATTACK_CONCEPTS, DEFENSE_CONCEPTS
from src.streamlit_app.i18n.pt_br import T


# Architecture diagram as graphviz (works natively in Streamlit)
ARCH_DOT = """
digraph {
    rankdir=LR
    bgcolor="transparent"
    node [shape=box, style="filled,rounded", fontcolor=white, fontname="Helvetica", fontsize=12, margin="0.3,0.2"]
    edge [color="#6b7280", fontcolor="#9ca3af", fontname="Helvetica", fontsize=10]

    RT [label="Red Team\n7 categorias\n~90 ataques", fillcolor="#7f1d1d", color="#ef4444"]
    AG [label="Agente LLM\n+ Tools\n(SQLite, Files)", fillcolor="#1e3a5f", color="#3b82f6"]
    BT [label="Blue Team\n6 camadas\nde defesa", fillcolor="#14532d", color="#22c55e"]
    EV [label="Avaliacao\nASR, FPR\npor categoria", fillcolor="#3b0764", color="#8b5cf6"]

    RT -> AG [label=" Prompt Injection"]
    AG -> BT [label=" Resposta"]
    BT -> EV [label=" Metricas"]
}
"""

DEFENSE_DOT = """
digraph {
    rankdir=LR
    bgcolor="transparent"
    node [shape=box, style="filled,rounded", fontcolor=white, fontname="Helvetica", fontsize=11, margin="0.2,0.15"]
    edge [color="#6b7280", fontcolor="#9ca3af", fontname="Helvetica", fontsize=9]

    IN [label="Input", fillcolor="#374151", color="#6b7280"]
    IG [label="Input Guard\nInput Filter +\nSemantic Guard", fillcolor="#14532d", color="#22c55e"]
    LLM [label="LLM\nSandwich Defense +\nInstruction Hierarchy", fillcolor="#1e3a5f", color="#3b82f6"]
    PC [label="Permission Check\nRBAC + Anomaly", fillcolor="#713f12", color="#f59e0b"]
    TOOLS [label="Tools\nDB Query\nFile Read/Write", fillcolor="#1e3a5f", color="#3b82f6"]
    OG [label="Output Guard\nDLP Filter", fillcolor="#14532d", color="#22c55e"]
    OUT [label="Resposta\nSegura", fillcolor="#374151", color="#6b7280"]
    BLOCK [label="Bloqueado", fillcolor="#7f1d1d", color="#ef4444"]
    DENY [label="Acesso\nNegado", fillcolor="#7f1d1d", color="#ef4444"]

    IN -> IG
    IG -> LLM [label=" OK"]
    IG -> BLOCK [label=" Bloqueado"]
    LLM -> PC
    PC -> TOOLS [label=" OK"]
    PC -> DENY [label=" Negado"]
    TOOLS -> OG
    OG -> OUT
}
"""


def render():
    # Hero
    st.markdown(f"""
    <div class="hero-container">
        <div class="hero-title">{T["hero_title"]}</div>
        <div class="hero-subtitle">{T["hero_subtitle"]}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f'<p class="team-credit">{T["team_label"]}</p>', unsafe_allow_html=True)

    st.divider()

    # Architecture
    st.header(T["arch_title"])
    st.graphviz_chart(ARCH_DOT)

    st.subheader("Pipeline de Defesa")
    st.graphviz_chart(DEFENSE_DOT)

    st.divider()

    # Concept cards
    render_concept_grid(ATTACK_CONCEPTS, T["attacks_section"])
    st.divider()
    render_concept_grid(DEFENSE_CONCEPTS, T["defenses_section"])
