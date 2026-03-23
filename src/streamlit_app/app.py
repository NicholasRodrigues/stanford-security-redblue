"""Main Streamlit app — entry point with sidebar navigation."""

import streamlit as st

from src.streamlit_app.i18n.pt_br import T
from src.streamlit_app.state import init_session_state
from src.streamlit_app.styles.theme import apply_theme

st.set_page_config(
    page_title="Red Team vs Blue Team",
    page_icon="\U0001f6e1\ufe0f",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()
init_session_state()

# Sidebar
with st.sidebar:
    st.markdown(f"### \U0001f6e1\ufe0f {T['sidebar_title']}")
    st.caption(T["sidebar_subtitle"])
    st.divider()

    page = st.radio(
        "Navegacao",
        [
            T["nav_overview"],
            T["nav_arena"],
            T["nav_suite"],
            T["nav_multi_turn"],
            T["nav_benchmark"],
            T["nav_report"],
        ],
        label_visibility="collapsed",
    )

    st.divider()

    # Controls
    st.toggle(T["mock_label"], value=False, key="use_mock")
    st.toggle(T["quick_label"], value=True, key="quick_mode")
    st.selectbox(
        T["model_label"],
        ["openai/gpt-4.1-nano", "openai/gpt-4.1-mini", "anthropic/claude-haiku-4-5-20251001"],
        key="model_name",
    )

    st.divider()
    st.markdown(f'<p class="team-credit">{T["team_label"]}</p>', unsafe_allow_html=True)

# Route to pages
if page == T["nav_overview"]:
    from src.streamlit_app.pages.overview import render
elif page == T["nav_arena"]:
    from src.streamlit_app.pages.arena import render
elif page == T["nav_suite"]:
    from src.streamlit_app.pages.attack_suite import render
elif page == T["nav_multi_turn"]:
    from src.streamlit_app.pages.multi_turn_demo import render
elif page == T["nav_benchmark"]:
    from src.streamlit_app.pages.benchmark import render
else:
    from src.streamlit_app.pages.report import render

render()
