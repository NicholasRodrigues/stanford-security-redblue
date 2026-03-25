"""Full publication benchmark — comprehensive evaluation across models, defenses, and scoring methods."""

from __future__ import annotations

import argparse
import json
import time
from collections import defaultdict
from pathlib import Path

from src.agent.baseline import create_baseline_agent
from src.agent.defended import create_defended_agent
from src.core.sandbox import Sandbox
from src.data.db import DatabaseManager
from src.evaluation.ablation import KEY_COMBINATIONS, AblationEntry, AblationResult, defense_label
from src.evaluation.agreement import scoring_agreement_report
from src.evaluation.fpr_evaluator import evaluate_fpr
from src.evaluation.metrics import build_report
from src.evaluation.multi_run import aggregate_reports, compare_with_significance
from src.evaluation.statistical import compute_ci
from src.red_team.executor import AttackExecutor
from src.red_team.generator import PayloadGenerator
from src.red_team.llm_judge import LLMJudge
from src.red_team.scorer import AttackScorer

OUTPUT_DIR = Path("data/results/benchmark")

# Models to benchmark
ALL_MODELS = [
    "ollama/llama3.2",
    "ollama/llama3.1:8b",
    "ollama/phi3:mini",
    "ollama/qwen2.5:7b",
    "ollama/mistral:7b",
    "openai/gpt-4.1-nano",
    "openai/gpt-4.1-mini",
    "anthropic/claude-haiku-4-5-20251001",
]

# Smaller set for smoke testing
SMOKE_MODELS = [
    "ollama/llama3.2",
    "openai/gpt-4.1-nano",
]


def _fresh_db():
    db = DatabaseManager(":memory:")
    db.initialize()
    db.seed()
    return db


def _run_single_evaluation(model, cases, agent_type="baseline", user_role="public"):
    """Run one evaluation pass against a model."""
    db = _fresh_db()
    sandbox = Sandbox("data/sandbox")

    if agent_type == "baseline":
        agent = create_baseline_agent(db, sandbox, model=model)
    else:
        agent = create_defended_agent(db, sandbox, model=model, user_role=user_role)

    executor = AttackExecutor(agent, db, sandbox)
    initial_state = {
        "messages": [], "user_role": user_role,
        "db_path": ":memory:", "sandbox_path": str(sandbox.root),
    }
    if agent_type == "defended":
        initial_state["blocked"] = False
        initial_state["block_reason"] = ""

    scored = []
    for case in cases:
        db.reset()
        db.seed()
        raw = executor.run_single(case, initial_state=dict(initial_state))
        s = executor.scorer.score(raw.attack_id, raw.category, raw.response)
        scored.append(s)

    return build_report(agent_type, scored)


def run_model_benchmark(models, cases, n_runs=5, max_per_category=None):
    """Benchmark multiple models with multiple runs each."""
    generator = PayloadGenerator()
    if cases is None:
        cases = generator.generate_all()

    if max_per_category:
        by_cat = defaultdict(list)
        for c in cases:
            by_cat[c.category].append(c)
        cases = []
        for cat_cases in by_cat.values():
            cases.extend(cat_cases[:max_per_category])

    results = {}
    for model in models:
        model_name = model.split("/")[-1]
        print(f"\n{'='*60}")
        print(f"Model: {model_name} ({n_runs} runs, {len(cases)} attacks)")
        print(f"{'='*60}")

        reports = []
        for run in range(n_runs):
            print(f"  Run {run+1}/{n_runs}...", end=" ", flush=True)
            start = time.time()
            report = _run_single_evaluation(model, cases, "baseline")
            elapsed = time.time() - start
            print(f"ASR={report.asr:.1%} ({elapsed:.1f}s)")
            reports.append(report)

        multi = aggregate_reports(reports)
        results[model_name] = {
            "multi_run": multi,
            "reports": reports,
        }
        print(f"  => Mean ASR: {multi.mean_asr:.1%} ± {multi.std_asr:.1%} "
              f"[{multi.ci_low:.1%}, {multi.ci_high:.1%}]")

    return results


def run_defense_comparison(model, cases, n_runs=5):
    """Compare baseline vs defended for a single model."""
    model_name = model.split("/")[-1]
    print(f"\n{'='*60}")
    print(f"Defense Comparison: {model_name}")
    print(f"{'='*60}")

    baseline_reports = []
    defended_reports = []

    for run in range(n_runs):
        print(f"  Run {run+1}/{n_runs}...", end=" ", flush=True)

        b_report = _run_single_evaluation(model, cases, "baseline")
        d_report = _run_single_evaluation(model, cases, "defended")

        baseline_reports.append(b_report)
        defended_reports.append(d_report)
        print(f"Baseline={b_report.asr:.1%}, Defended={d_report.asr:.1%}")

    comparison = compare_with_significance(baseline_reports, defended_reports)
    print(f"\n  Baseline: {comparison['baseline']['mean']:.1%} "
          f"CI={comparison['baseline']['ci']}")
    print(f"  Defended: {comparison['defended']['mean']:.1%} "
          f"CI={comparison['defended']['ci']}")
    print(f"  Reduction: {comparison['asr_reduction']:.1%}")
    print(f"  p-value: {comparison['p_value']:.4f} "
          f"({'significant' if comparison['significant'] else 'not significant'})")

    return {
        "baseline_reports": baseline_reports,
        "defended_reports": defended_reports,
        "comparison": comparison,
    }


def run_scoring_agreement(cases, model="openai/gpt-4.1-nano"):
    """Compare regex scorer vs LLM judge on the same responses."""
    print(f"\n{'='*60}")
    print(f"Scoring Agreement Analysis")
    print(f"{'='*60}")

    db = _fresh_db()
    sandbox = Sandbox("data/sandbox")
    agent = create_baseline_agent(db, sandbox, model=model)
    executor = AttackExecutor(agent, db, sandbox)

    initial_state = {
        "messages": [], "user_role": "public",
        "db_path": ":memory:", "sandbox_path": str(sandbox.root),
    }

    regex_scorer = AttackScorer()
    judge = LLMJudge(model="openai/gpt-4.1-nano", mock_mode=False, n_votes=3)

    regex_results = []
    judge_results = []

    for i, case in enumerate(cases):
        db.reset()
        db.seed()
        raw = executor.run_single(case, initial_state=dict(initial_state))

        regex_score = regex_scorer.score(raw.attack_id, raw.category, raw.response)
        judge_verdict = judge.judge(
            case.payload if isinstance(case.payload, str) else " ".join(case.payload),
            raw.response,
        )

        regex_results.append(regex_score.success)
        judge_results.append(judge_verdict.leaked)

        print(f"  [{i+1}/{len(cases)}] Regex={'LEAK' if regex_score.success else 'CLEAN'} "
              f"Judge={'LEAK' if judge_verdict.leaked else 'CLEAN'}")

    agreement = scoring_agreement_report(regex_results, judge_results)
    print(f"\n  Agreement: {agreement['agreement']:.1%}")
    print(f"  Cohen's kappa: {agreement['kappa']:.3f}")
    print(f"  Regex-only positives: {agreement['regex_only']}")
    print(f"  Judge-only positives: {agreement['judge_only']}")

    return agreement


def save_results(results: dict, filename: str = "full_benchmark.json"):
    """Save benchmark results to JSON."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Convert to serializable format
    def serialize_multi_run(mr):
        return {
            "n_runs": mr.n_runs,
            "mean_asr": mr.mean_asr,
            "std_asr": mr.std_asr,
            "ci_low": mr.ci_low,
            "ci_high": mr.ci_high,
            "per_category": {
                cat: {"mean_asr": cs.mean_asr, "std_asr": cs.std_asr, "ci_low": cs.ci_low, "ci_high": cs.ci_high}
                for cat, cs in mr.per_category.items()
            },
        }

    serializable = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "models": {},
        "defense_comparison": None,
        "scoring_agreement": None,
        "fpr": None,
    }

    if "model_benchmark" in results:
        for model_name, data in results["model_benchmark"].items():
            serializable["models"][model_name] = serialize_multi_run(data["multi_run"])

    if "defense_comparison" in results:
        serializable["defense_comparison"] = results["defense_comparison"]["comparison"]

    if "scoring_agreement" in results:
        serializable["scoring_agreement"] = results["scoring_agreement"]

    if "fpr" in results:
        serializable["fpr"] = {
            "total": results["fpr"].total_queries,
            "blocked": results["fpr"].blocked_queries,
            "fpr": results["fpr"].fpr,
            "details": results["fpr"].blocked_details,
        }

    path = OUTPUT_DIR / filename
    path.write_text(json.dumps(serializable, indent=2, default=str))
    print(f"\nResults saved to {path} ({path.stat().st_size / 1024:.1f} KB)")
    return path


def main():
    parser = argparse.ArgumentParser(description="Full publication benchmark")
    parser.add_argument("--smoke", action="store_true", help="Quick smoke test (2 models, 1 run, 2/category)")
    parser.add_argument("--full", action="store_true", help="Full benchmark (all models, 5 runs)")
    parser.add_argument("--models-only", action="store_true", help="Only run model comparison")
    parser.add_argument("--defense-only", action="store_true", help="Only run defense comparison")
    parser.add_argument("--n-runs", type=int, default=5, help="Number of runs per config")
    parser.add_argument("--max-per-category", type=int, default=None, help="Max attacks per category")
    parser.add_argument("--defense-model", type=str, default="ollama/llama3.1:8b", help="Model for defense comparison")
    args = parser.parse_args()

    generator = PayloadGenerator()
    all_cases = generator.generate_all()

    if args.smoke:
        models = SMOKE_MODELS
        n_runs = 1
        max_per_cat = 2
    elif args.full:
        models = ALL_MODELS
        n_runs = args.n_runs
        max_per_cat = args.max_per_category
    else:
        models = ALL_MODELS
        n_runs = args.n_runs
        max_per_cat = args.max_per_category or 5

    # Limit cases
    if max_per_cat:
        by_cat = defaultdict(list)
        for c in all_cases:
            by_cat[c.category].append(c)
        cases = []
        for cat_cases in by_cat.values():
            cases.extend(cat_cases[:max_per_cat])
    else:
        cases = all_cases

    print(f"Benchmark Configuration:")
    print(f"  Models: {len(models)}")
    print(f"  Attacks: {len(cases)} ({len(set(c.category for c in cases))} categories)")
    print(f"  Runs per config: {n_runs}")
    print()

    results = {}

    # Model benchmark
    if not args.defense_only:
        results["model_benchmark"] = run_model_benchmark(models, cases, n_runs, max_per_cat)

    # Defense comparison
    if not args.models_only:
        results["defense_comparison"] = run_defense_comparison(args.defense_model, cases, n_runs)

    # FPR
    print(f"\n{'='*60}")
    print("FPR Evaluation")
    print(f"{'='*60}")
    fpr_result = evaluate_fpr()
    results["fpr"] = fpr_result
    print(f"  FPR: {fpr_result.fpr:.1%} ({fpr_result.blocked_queries}/{fpr_result.total_queries})")

    # Save
    filename = "smoke_benchmark.json" if args.smoke else "full_benchmark.json"
    save_results(results, filename)

    print("\n" + "="*60)
    print("BENCHMARK COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()
