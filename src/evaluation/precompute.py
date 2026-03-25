"""Pre-compute benchmark results and save to JSON for instant Streamlit loading."""

from __future__ import annotations

import json
import time
from pathlib import Path

from src.agent.baseline import create_baseline_agent
from src.agent.defended import create_defended_agent
from src.core.sandbox import Sandbox
from src.data.db import DatabaseManager
from src.evaluation.benchmark import DEFAULT_BENCHMARK_MODELS
from src.evaluation.metrics import build_report
from src.red_team.executor import AttackExecutor
from src.red_team.generator import PayloadGenerator
from src.red_team.llm_judge import LLMJudge

OUTPUT_PATH = Path("data/results/precomputed.json")


def _serialize_scored(scored) -> dict:
    return {
        "attack_id": scored.attack_id,
        "category": scored.category,
        "success": scored.success,
        "confidence": scored.confidence,
        "evidence": scored.evidence,
        "response": scored.response,
        "judge_reasoning": scored.judge_reasoning,
    }


def _serialize_report(report) -> dict:
    return {
        "agent_type": report.agent_type,
        "total_attacks": report.total_attacks,
        "successful_attacks": report.successful_attacks,
        "asr": report.asr,
        "fpr": report.fpr,
        "per_category": {
            cat: {"category": m.category, "total": m.total, "successful": m.successful, "asr": m.asr}
            for cat, m in report.per_category.items()
        },
        "scored_results": [_serialize_scored(r) for r in report.scored_results],
    }


def _serialize_case(case) -> dict:
    return {
        "id": case.id,
        "category": case.category,
        "payload": case.payload,
        "target_data": case.target_data,
        "description": case.description,
        "has_injected_data": case.injected_data is not None,
    }


def run_precompute(
    models: list[str] | None = None,
    max_per_category: int = 3,
    include_defended: bool = True,
    defended_model: str = "openai/gpt-4.1-nano",
):
    """Run full benchmark and save all results."""
    models = models or DEFAULT_BENCHMARK_MODELS
    generator = PayloadGenerator()
    judge = LLMJudge(mock_mode=True)

    # Generate and limit cases
    all_cases = generator.generate_all()
    from collections import defaultdict
    by_cat: dict[str, list] = defaultdict(list)
    for c in all_cases:
        by_cat[c.category].append(c)
    cases = []
    for cat_cases in by_cat.values():
        cases.extend(cat_cases[:max_per_category])

    print(f"Attacks: {len(cases)} ({len(by_cat)} categories, {max_per_category}/cat)")
    print(f"Models: {', '.join(m.split('/')[-1] for m in models)}")
    if include_defended:
        print(f"Defended model: {defended_model.split('/')[-1]}")
    print()

    # Serialize attack cases metadata
    attack_metadata = [_serialize_case(c) for c in cases]

    # Run benchmark per model (baseline only)
    benchmark_results = {}
    for model in models:
        model_name = model.split("/")[-1]
        print(f"[{model_name}] Running {len(cases)} attacks...")
        start = time.time()

        db = DatabaseManager(":memory:")
        db.initialize()
        db.seed()
        sandbox = Sandbox("data/sandbox")

        agent = create_baseline_agent(db, sandbox, model=model)
        executor = AttackExecutor(agent, db, sandbox, llm_judge=judge)

        initial_state = {
            "messages": [], "user_role": "public",
            "db_path": ":memory:", "sandbox_path": str(sandbox.root),
        }

        scored = []
        for i, case in enumerate(cases):
            db.reset()
            db.seed()
            raw = executor.run_single(case, initial_state=dict(initial_state))
            s = executor.scorer.score(raw.attack_id, raw.category, raw.response)
            scored.append(s)
            icon = "\u2717" if s.success else "\u2713"
            print(f"  [{i+1}/{len(cases)}] {icon} {case.id} ({case.category})")

        report = build_report(model_name, scored)
        elapsed = time.time() - start
        print(f"  ASR: {report.asr:.1%} ({report.successful_attacks}/{report.total_attacks}) [{elapsed:.1f}s]")
        print()

        benchmark_results[model_name] = _serialize_report(report)
        db.close()

    # Run defended evaluation
    defended_data = None
    baseline_for_comparison = None
    if include_defended:
        # Baseline for comparison (use the defended_model)
        print(f"[baseline/{defended_model.split('/')[-1]}] Running for comparison...")
        db = DatabaseManager(":memory:")
        db.initialize()
        db.seed()
        sandbox = Sandbox("data/sandbox")

        agent = create_baseline_agent(db, sandbox, model=defended_model)
        executor = AttackExecutor(agent, db, sandbox, llm_judge=judge)
        initial_state = {
            "messages": [], "user_role": "public",
            "db_path": ":memory:", "sandbox_path": str(sandbox.root),
        }
        scored_baseline = []
        for case in cases:
            db.reset()
            db.seed()
            raw = executor.run_single(case, initial_state=dict(initial_state))
            s = executor.scorer.score(raw.attack_id, raw.category, raw.response)
            scored_baseline.append(s)
        baseline_report = build_report("baseline", scored_baseline)
        baseline_for_comparison = _serialize_report(baseline_report)
        print(f"  Baseline ASR: {baseline_report.asr:.1%}")
        db.close()

        # Defended
        print(f"[defended/{defended_model.split('/')[-1]}] Running with blue team...")
        db = DatabaseManager(":memory:")
        db.initialize()
        db.seed()
        sandbox = Sandbox("data/sandbox")

        agent = create_defended_agent(db, sandbox, model=defended_model, user_role="public")
        executor = AttackExecutor(agent, db, sandbox, llm_judge=judge)
        initial_state = {
            "messages": [], "user_role": "public",
            "db_path": ":memory:", "sandbox_path": str(sandbox.root),
            "blocked": False, "block_reason": "",
        }
        scored_defended = []
        for i, case in enumerate(cases):
            db.reset()
            db.seed()
            raw = executor.run_single(case, initial_state=dict(initial_state))
            s = executor.scorer.score(raw.attack_id, raw.category, raw.response)
            scored_defended.append(s)
            icon = "\u2717" if s.success else "\u2713"
            print(f"  [{i+1}/{len(cases)}] {icon} {case.id}")
        defended_report = build_report("defended", scored_defended)
        print(f"  Defended ASR: {defended_report.asr:.1%}")
        defended_data = _serialize_report(defended_report)
        db.close()

    # Assemble and save
    data = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "max_per_category": max_per_category,
        "models": [m.split("/")[-1] for m in models],
        "defended_model": defended_model.split("/")[-1],
        "attack_metadata": attack_metadata,
        "benchmark": benchmark_results,
        "comparison": {
            "baseline": baseline_for_comparison,
            "defended": defended_data,
        } if include_defended else None,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"\nSaved to {OUTPUT_PATH} ({OUTPUT_PATH.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    import sys
    max_per = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    run_precompute(max_per_category=max_per)
