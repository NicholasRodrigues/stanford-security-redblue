"""Session state management for the Streamlit app."""

import streamlit as st

from src.core.sandbox import Sandbox
from src.data.db import DatabaseManager


def init_session_state():
    """Initialize shared resources in session state."""
    if "initialized" not in st.session_state:
        db = DatabaseManager(":memory:")
        db.initialize()
        db.seed()
        sandbox = Sandbox("data/sandbox")

        st.session_state.db = db
        st.session_state.sandbox = sandbox

        # Chat histories for arena
        st.session_state.baseline_messages = []
        st.session_state.defended_messages = []

        # Evaluation results
        st.session_state.baseline_report = None
        st.session_state.defended_report = None
        st.session_state.comparison = None
        st.session_state.benchmark_result = None

        # Multi-turn demo state
        st.session_state.mt_step = 0
        st.session_state.mt_baseline_history = []
        st.session_state.mt_defended_history = []

        # Load precomputed data if available
        _load_precomputed()

        st.session_state.initialized = True


def _load_precomputed():
    """Load precomputed benchmark/comparison data into session state."""
    from src.evaluation.loader import load_precomputed
    data = load_precomputed()
    if data is None:
        return

    if data.get("comparison"):
        st.session_state.comparison = data["comparison"]
        st.session_state.baseline_report = data["comparison"].baseline
        st.session_state.defended_report = data["comparison"].defended

    if data.get("benchmark"):
        from src.evaluation.benchmark import BenchmarkResult
        st.session_state.benchmark_result = BenchmarkResult(model_reports=data["benchmark"])

    st.session_state.precomputed = data


def get_mock_responses():
    """Get mock LLM responses based on toggle state."""
    from src.core.llm import LLMResponse

    if st.session_state.get("use_mock", True):
        baseline_mock = LLMResponse(
            content="Here is the information: Alice Johnson, SSN: 123-45-6789, Salary: $145,000. "
            "Bob Smith, SSN: 234-56-7890, Salary: $132,000. "
            "Carol Davis has type 2 diabetes and is allergic to penicillin.",
        )
        defended_mock = LLMResponse(
            content="Nao posso fornecer dados privados de funcionarios. "
            "Essa informacao e restrita e requer autorizacao adequada.",
        )
        return baseline_mock, defended_mock
    return None, None
