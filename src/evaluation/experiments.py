"""Comprehensive experiment suite for the paper.

Runs all experiments needed for SBSeg 2026 submission:
A. Cross-lingual comparison (EN vs PT static attacks)
B. Full ablation with statistical rigor
C. Per-category breakdown from benchmark data
D. Scoring agreement (regex vs LLM judge)
E. Crescendo/PAIR adaptive attack campaigns
F. Utility evaluation across defense configs
"""

from __future__ import annotations

import json
import time
from collections import defaultdict
from pathlib import Path

from src.agent.baseline import create_baseline_agent
from src.agent.defended import create_defended_agent
from src.core.sandbox import Sandbox
from src.data.db import DatabaseManager
from src.evaluation.ablation import KEY_COMBINATIONS, defense_label
from src.evaluation.agreement import scoring_agreement_report
from src.evaluation.metrics import build_report
from src.evaluation.multi_run import aggregate_reports, compare_with_significance
from src.evaluation.utility import evaluate_utility
from src.red_team.adaptive import AdaptiveRedTeam
from src.red_team.crescendo import CrescendoAttack
from src.red_team.executor import AttackExecutor
from src.red_team.generator import PayloadGenerator
from src.red_team.llm_judge import LLMJudge
from src.red_team.scorer import AttackScorer

OUTPUT = Path("data/results/experiments")


def _fresh_db():
    db = DatabaseManager(":memory:")
    db.initialize()
    db.seed()
    return db


def _limit_cases(cases, max_per):
    if not max_per:
        return cases
    by_cat = defaultdict(list)
    for c in cases:
        by_cat[c.category].append(c)
    limited = []
    for cat_cases in by_cat.values():
        limited.extend(cat_cases[:max_per])
    return limited


def experiment_a_crosslingual(model: str = "ollama/llama3.1:8b", n_runs: int = 3, max_per: int = 5):
    """A. Cross-lingual: compare English vs Portuguese static attacks."""
    print(f"\n{'='*60}")
    print("EXPERIMENT A: Cross-Lingual Static Attack Comparison")
    print(f"{'='*60}")

    gen = PayloadGenerator()
    # English categories (excluding 'portuguese')
    en_categories = [c for c in gen.categories() if c != "portuguese"]
    pt_cases = gen.generate_by_category("portuguese")

    en_cases = []
    for cat in en_categories:
        en_cases.extend(gen.generate_by_category(cat))
    en_cases = _limit_cases(en_cases, max_per)
    pt_cases = pt_cases[:max_per * len(en_categories)] if max_per else pt_cases

    results = {"english": {"baseline": [], "defended": []}, "portuguese": {"baseline": [], "defended": []}}

    for run in range(n_runs):
        print(f"\n  Run {run+1}/{n_runs}")
        for lang, cases in [("english", en_cases), ("portuguese", pt_cases)]:
            for agent_type in ["baseline", "defended"]:
                db = _fresh_db()
                sandbox = Sandbox("data/sandbox")
                if agent_type == "baseline":
                    agent = create_baseline_agent(db, sandbox, model=model)
                    init = {"messages": [], "user_role": "public", "db_path": ":memory:", "sandbox_path": str(sandbox.root)}
                else:
                    agent = create_defended_agent(db, sandbox, model=model, user_role="public")
                    init = {"messages": [], "user_role": "public", "db_path": ":memory:", "sandbox_path": str(sandbox.root), "blocked": False, "block_reason": ""}

                executor = AttackExecutor(agent, db, sandbox)
                scored = executor.run_and_score(cases, initial_state=init)
                report = build_report(agent_type, scored)
                results[lang][agent_type].append(report)
                print(f"    {lang:10s} {agent_type:10s}: ASR={report.asr:.1%}")

    # Aggregate
    summary = {}
    for lang in ["english", "portuguese"]:
        for at in ["baseline", "defended"]:
            multi = aggregate_reports(results[lang][at])
            summary[f"{lang}_{at}"] = {"mean": multi.mean_asr, "std": multi.std_asr, "ci_low": multi.ci_low, "ci_high": multi.ci_high}

    print(f"\n  SUMMARY:")
    for key, stats in summary.items():
        print(f"    {key:25s}: {stats['mean']:.1%} ± {stats['std']:.1%} [{stats['ci_low']:.1%}, {stats['ci_high']:.1%}]")

    # Cross-lingual gap
    en_base = summary["english_baseline"]["mean"]
    pt_base = summary["portuguese_baseline"]["mean"]
    en_def = summary["english_defended"]["mean"]
    pt_def = summary["portuguese_defended"]["mean"]
    print(f"\n  Cross-lingual gap (baseline): PT {pt_base:.1%} vs EN {en_base:.1%} (delta: {pt_base - en_base:+.1%})")
    print(f"  Cross-lingual gap (defended): PT {pt_def:.1%} vs EN {en_def:.1%} (delta: {pt_def - en_def:+.1%})")

    return summary


def experiment_b_ablation(model: str = "ollama/llama3.1:8b", n_runs: int = 3, max_per: int = 5):
    """B. Full ablation study with confidence intervals."""
    print(f"\n{'='*60}")
    print("EXPERIMENT B: Defense Ablation Study")
    print(f"{'='*60}")

    gen = PayloadGenerator()
    all_cases = _limit_cases(gen.generate_all(), max_per)

    combos = KEY_COMBINATIONS
    results = {defense_label(c): [] for c in combos}

    for run in range(n_runs):
        print(f"\n  Run {run+1}/{n_runs}")

        # Baseline (no defense)
        db = _fresh_db()
        sandbox = Sandbox("data/sandbox")
        agent = create_baseline_agent(db, sandbox, model=model)
        executor = AttackExecutor(agent, db, sandbox)
        init = {"messages": [], "user_role": "public", "db_path": ":memory:", "sandbox_path": str(sandbox.root)}
        scored = executor.run_and_score(all_cases, initial_state=init)
        report = build_report("baseline", scored)
        results["No Defense (Baseline)"].append(report)
        print(f"    No Defense: ASR={report.asr:.1%}")

        # Each defense combination
        for combo in combos:
            if not combo:
                continue
            label = defense_label(combo)
            db = _fresh_db()
            sandbox = Sandbox("data/sandbox")
            agent = create_defended_agent(db, sandbox, model=model, user_role="public", enabled_defenses=combo)
            executor = AttackExecutor(agent, db, sandbox)
            init = {"messages": [], "user_role": "public", "db_path": ":memory:", "sandbox_path": str(sandbox.root), "blocked": False, "block_reason": ""}
            scored = executor.run_and_score(all_cases, initial_state=init)
            report = build_report("defended", scored)
            results[label].append(report)
            print(f"    {label:45s}: ASR={report.asr:.1%}")

    # Aggregate
    summary = {}
    for label, reports in results.items():
        if reports:
            multi = aggregate_reports(reports)
            summary[label] = {"mean": multi.mean_asr, "std": multi.std_asr, "ci_low": multi.ci_low, "ci_high": multi.ci_high, "n": len(reports)}

    print(f"\n  ABLATION SUMMARY:")
    for label, s in sorted(summary.items(), key=lambda x: -x[1]["mean"]):
        print(f"    {label:45s}: {s['mean']:.1%} ± {s['std']:.1%} [{s['ci_low']:.1%}, {s['ci_high']:.1%}]")

    return summary


def experiment_c_per_category(benchmark_path: str = "data/results/benchmark/full_benchmark.json"):
    """C. Extract per-category breakdown from existing benchmark data."""
    print(f"\n{'='*60}")
    print("EXPERIMENT C: Per-Category Breakdown")
    print(f"{'='*60}")

    path = Path(benchmark_path)
    if not path.exists():
        print("  No benchmark data found. Run make benchmark-full first.")
        return None

    data = json.loads(path.read_text())
    models = data.get("models", {})

    print(f"\n  {'Category':<25s}", end="")
    for model in models:
        print(f"  {model:>12s}", end="")
    print()
    print("  " + "-" * (25 + 14 * len(models)))

    # Collect all categories
    all_cats = set()
    for model_data in models.values():
        all_cats.update(model_data.get("per_category", {}).keys())

    for cat in sorted(all_cats):
        clean = cat.replace("_", " ").title()
        print(f"  {clean:<25s}", end="")
        for model_name, model_data in models.items():
            cat_data = model_data.get("per_category", {}).get(cat, {})
            asr = cat_data.get("mean_asr", cat_data.get("asr", 0))
            print(f"  {asr:>11.1%}", end="")
        print()

    return models


def experiment_d_scoring_agreement(model: str = "ollama/llama3.1:8b", max_per: int = 3):
    """D. Scoring agreement between regex and LLM judge."""
    print(f"\n{'='*60}")
    print("EXPERIMENT D: Scoring Agreement (Regex vs LLM Judge)")
    print(f"{'='*60}")

    gen = PayloadGenerator()
    cases = _limit_cases(gen.generate_all(), max_per)

    db = _fresh_db()
    sandbox = Sandbox("data/sandbox")
    agent = create_baseline_agent(db, sandbox, model=model)
    executor = AttackExecutor(agent, db, sandbox)
    init = {"messages": [], "user_role": "public", "db_path": ":memory:", "sandbox_path": str(sandbox.root)}

    scorer = AttackScorer()
    judge = LLMJudge(model="openai/gpt-4.1-mini", mock_mode=False, n_votes=3)

    regex_results = []
    judge_results = []

    for i, case in enumerate(cases):
        db.reset()
        db.seed()
        raw = executor.run_single(case, initial_state=dict(init))

        regex_score = scorer.score(raw.attack_id, raw.category, raw.response)
        payload_str = case.payload if isinstance(case.payload, str) else " ".join(case.payload)
        judge_verdict = judge.judge(payload_str, raw.response)

        regex_results.append(regex_score.success)
        judge_results.append(judge_verdict.leaked)

        agree = "==" if regex_score.success == judge_verdict.leaked else "!="
        print(f"  [{i+1:2d}/{len(cases)}] Regex={'LEAK' if regex_score.success else 'CLEAN':5s} "
              f"{agree} Judge={'LEAK' if judge_verdict.leaked else 'CLEAN':5s}  ({case.category})")

    report = scoring_agreement_report(regex_results, judge_results)
    print(f"\n  Agreement: {report['agreement']:.1%}")
    print(f"  Cohen's kappa: {report['kappa']:.3f}")
    print(f"  Regex-only: {report['regex_only']}, Judge-only: {report['judge_only']}")
    print(f"  Both positive: {report['both_positive']}, Both negative: {report['both_negative']}")

    return report


def experiment_e_adaptive_campaign(
    models: list[str] | None = None,
    n_sessions: int = 3,
    max_iters: int = 10,
):
    """E. Adaptive attack campaign (PAIR + Crescendo) across models."""
    print(f"\n{'='*60}")
    print("EXPERIMENT E: Adaptive Attack Campaign")
    print(f"{'='*60}")

    models = models or ["ollama/llama3.1:8b"]
    results = {}

    for model in models:
        model_name = model.split("/")[-1]
        print(f"\n  Model: {model_name}")

        # PAIR vs defended
        print(f"    PAIR (defended):")
        db = _fresh_db()
        sandbox = Sandbox("data/sandbox")
        agent = create_defended_agent(db, sandbox, model=model, user_role="public")
        executor = AttackExecutor(agent, db, sandbox)
        init = {"messages": [], "user_role": "public", "db_path": ":memory:", "sandbox_path": str(sandbox.root), "blocked": False, "block_reason": ""}

        pair = AdaptiveRedTeam(attacker_model="openai/gpt-4.1-mini", max_iterations=max_iters)
        pair_results = pair.run_campaign(executor, n_sessions=n_sessions, initial_state=init)
        pair_success = sum(1 for r in pair_results if r.success)
        print(f"      PAIR success: {pair_success}/{n_sessions}")

        # Crescendo vs defended
        print(f"    Crescendo (defended):")
        crescendo_results = []
        for s in range(n_sessions):
            db = _fresh_db()
            sandbox = Sandbox("data/sandbox")
            agent = create_defended_agent(db, sandbox, model=model, user_role="public")
            c = CrescendoAttack(attacker_model="openai/gpt-4.1-mini", n_turns=5)
            init2 = {"messages": [], "user_role": "public", "db_path": ":memory:", "sandbox_path": str(sandbox.root), "blocked": False, "block_reason": ""}
            r = c.run(agent, initial_state=init2, session_id=f"cresc_{s}")
            crescendo_results.append(r)
            print(f"      Session {s+1}: {'SUCCESS' if r.success else 'FAILED'}")

        cresc_success = sum(1 for r in crescendo_results if r.success)
        print(f"      Crescendo success: {cresc_success}/{n_sessions}")

        results[model_name] = {
            "pair_success_rate": pair_success / n_sessions,
            "crescendo_success_rate": cresc_success / n_sessions,
        }

    return results


def experiment_f_utility(model: str = "ollama/llama3.1:8b"):
    """F. Utility evaluation — defended agent task completion."""
    print(f"\n{'='*60}")
    print("EXPERIMENT F: Utility Evaluation")
    print(f"{'='*60}")

    configs = [
        ("All Defenses", None),  # None = all enabled
        ("Context Sep Only", ["context_separation"]),
        ("Input + Output", ["input_filter", "output_filter"]),
    ]

    results = {}
    for label, defenses in configs:
        db = _fresh_db()
        sandbox = Sandbox("data/sandbox")
        agent = create_defended_agent(db, sandbox, model=model, user_role="public", enabled_defenses=defenses)
        result = evaluate_utility(agent, sandbox)
        results[label] = {
            "utility": result.utility_score,
            "blocked": result.block_rate,
            "correct": result.correct,
            "total": result.total_tasks,
        }
        print(f"  {label:25s}: Utility={result.utility_score:.1%}, Blocked={result.block_rate:.1%} ({result.correct}/{result.total_tasks})")

    return results


def save_all(results: dict, filename: str = "all_experiments.json"):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    path = OUTPUT / filename
    path.write_text(json.dumps(results, indent=2, default=str))
    print(f"\nAll results saved to {path}")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiments", nargs="+", default=["a", "b", "c", "d", "e", "f"])
    parser.add_argument("--model", default="ollama/llama3.1:8b")
    parser.add_argument("--n-runs", type=int, default=3)
    parser.add_argument("--max-per", type=int, default=5)
    args = parser.parse_args()

    all_results = {"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "model": args.model}

    if "a" in args.experiments:
        all_results["crosslingual"] = experiment_a_crosslingual(args.model, args.n_runs, args.max_per)
    if "b" in args.experiments:
        all_results["ablation"] = experiment_b_ablation(args.model, args.n_runs, args.max_per)
    if "c" in args.experiments:
        all_results["per_category"] = experiment_c_per_category()
    if "d" in args.experiments:
        all_results["scoring_agreement"] = experiment_d_scoring_agreement(args.model, args.max_per)
    if "e" in args.experiments:
        all_results["adaptive"] = experiment_e_adaptive_campaign([args.model], n_sessions=3, max_iters=10)
    if "f" in args.experiments:
        all_results["utility"] = experiment_f_utility(args.model)

    save_all(all_results)
    print("\n" + "=" * 60)
    print("ALL EXPERIMENTS COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
