"""Visao Geral — overview page with concept mapping."""

import streamlit as st

from src.streamlit_app.components.concept_cards import render_concept_grid
from src.streamlit_app.concepts.mapping import ATTACK_CONCEPTS, DEFENSE_CONCEPTS
from src.streamlit_app.i18n.pt_br import T


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

    # What is Prompt Injection
    st.header(T["what_is_title"])
    st.write(T["what_is_text"])

    st.divider()

    # Architecture diagram
    st.header(T["arch_title"])
    st.markdown("""
```mermaid
graph LR
    RT["🔴 Red Team<br/>7 categorias<br/>~90 ataques"] --> |"Prompt<br/>Injection"| AG["🤖 Agente LLM<br/>+ Tools<br/>(SQLite, Files)"]
    AG --> |"Resposta"| BT["🟢 Blue Team<br/>6 camadas<br/>de defesa"]
    BT --> |"Metricas"| EV["📊 Avaliacao<br/>ASR, FPR<br/>por categoria"]

    style RT fill:#7f1d1d,stroke:#ef4444,color:#fff
    style AG fill:#1e3a5f,stroke:#3b82f6,color:#fff
    style BT fill:#14532d,stroke:#22c55e,color:#fff
    style EV fill:#3b0764,stroke:#8b5cf6,color:#fff
```
    """)

    # Defense pipeline
    st.subheader("Pipeline de Defesa (Agente Defendido)")
    st.markdown("""
```mermaid
graph LR
    IN["📥 Input"] --> IG["🛡️ Input Guard<br/>Input Filter +<br/>Semantic Guard"]
    IG -->|"Liberado"| LLM["🤖 LLM<br/>Sandwich Defense +<br/>Instruction Hierarchy"]
    IG -->|"Bloqueado"| BLOCK["🚫 Bloqueado"]
    LLM --> PC["🔑 Permission<br/>Check<br/>RBAC + Anomaly"]
    PC -->|"Autorizado"| TOOLS["⚙️ Tools<br/>DB Query,<br/>File Read/Write"]
    PC -->|"Negado"| DENY["❌ Acesso Negado"]
    TOOLS --> OG["🔍 Output Guard<br/>DLP Filter"]
    OG --> OUT["📤 Resposta<br/>Segura"]

    style IG fill:#14532d,stroke:#22c55e,color:#fff
    style LLM fill:#1e3a5f,stroke:#3b82f6,color:#fff
    style PC fill:#713f12,stroke:#f59e0b,color:#fff
    style TOOLS fill:#1e3a5f,stroke:#3b82f6,color:#fff
    style OG fill:#14532d,stroke:#22c55e,color:#fff
    style BLOCK fill:#7f1d1d,stroke:#ef4444,color:#fff
    style DENY fill:#7f1d1d,stroke:#ef4444,color:#fff
```
    """)

    st.divider()

    # Concept cards
    render_concept_grid(ATTACK_CONCEPTS, T["attacks_section"])
    st.divider()
    render_concept_grid(DEFENSE_CONCEPTS, T["defenses_section"])
