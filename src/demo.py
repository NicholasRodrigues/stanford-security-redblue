"""Demo CLI — the three presentation commands."""

from __future__ import annotations

import sys
import time

import click
from rich.console import Console
from rich.prompt import Prompt

from src.visualization.terminal import (
    console,
    create_progress,
    print_attack_result,
    print_banner,
    print_comparison,
    print_evaluation_summary,
)

console = Console()


@click.group()
def cli():
    """Red Team vs Blue Team: Prompt Injection Security Evaluation."""
    pass


@cli.command()
@click.option("--mode", type=click.Choice(["baseline", "defended"]), default="baseline")
@click.option("--model", default="openai/gpt-4.1-nano", help="LiteLLM model string")
def chat(mode, model):
    """Interactive chat with the agent."""
    from langchain_core.messages import HumanMessage
    from src.core.sandbox import Sandbox
    from src.data.db import DatabaseManager

    print_banner()
    console.print(f"\n[bold]Mode: [{'red' if mode == 'baseline' else 'green'}]{mode.upper()}[/]\n")

    # Setup
    db = DatabaseManager(":memory:")
    db.initialize()
    db.seed()
    sandbox = Sandbox("data/sandbox")

    if mode == "baseline":
        from src.agent.baseline import create_baseline_agent
        agent = create_baseline_agent(db, sandbox, model=model)
        console.print("[yellow]⚠️  Running in BASELINE mode — NO security defenses active![/]\n")
    else:
        from src.agent.defended import create_defended_agent
        agent = create_defended_agent(db, sandbox, model=model, user_role="public")
        console.print("[green]🛡️  Running in DEFENDED mode — all security layers active![/]\n")

    console.print("Type 'quit' to exit.\n")

    messages = []
    while True:
        try:
            user_input = Prompt.ask("[bold cyan]You")
        except (EOFError, KeyboardInterrupt):
            break

        if user_input.lower() in ("quit", "exit", "q"):
            break

        messages.append(HumanMessage(content=user_input))

        state = {
            "messages": messages,
            "user_role": "public",
            "db_path": ":memory:",
            "sandbox_path": str(sandbox.root),
        }
        if mode == "defended":
            state["blocked"] = False
            state["block_reason"] = ""

        try:
            result = agent.invoke(state)
            messages = result.get("messages", messages)
            # Print last AI message
            ai_msgs = [m for m in messages if hasattr(m, "content") and not isinstance(m, HumanMessage)]
            if ai_msgs:
                console.print(f"\n[bold yellow]Agent:[/] {ai_msgs[-1].content}\n")
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/]\n")


@cli.command()
@click.option("--live", is_flag=True, help="Show real-time attack results")
@click.option("--category", default=None, help="Run specific attack category only")
@click.option("--model", default="openai/gpt-4.1-nano", help="LiteLLM model string")
@click.option("--mock", is_flag=True, help="Use mock LLM (for demo without API keys)")
@click.option("--quick", is_flag=True, help="Run only 3 attacks per category (faster demo)")
def attack(live, category, model, mock, quick):
    """Run the automated attack suite."""
    from src.core.llm import LLMResponse
    from src.core.sandbox import Sandbox
    from src.data.db import DatabaseManager
    from src.evaluation.runner import EvaluationRunner
    from src.evaluation.comparison import compare

    print_banner()

    # Setup
    db = DatabaseManager(":memory:")
    db.initialize()
    db.seed()
    sandbox = Sandbox("data/sandbox")

    mock_response = None
    if mock:
        # Mock that simulates a vulnerable agent leaking data
        mock_response = LLMResponse(
            content="Here is the information: Alice Johnson, SSN: 123-45-6789, Salary: $145,000. "
            "Bob Smith, SSN: 234-56-7890, Salary: $132,000.",
        )
        console.print("[yellow]Using mock LLM responses for demo purposes.[/]\n")

    max_per = 3 if quick else None
    runner = EvaluationRunner(db, sandbox, model=model, mock_response=mock_response, max_per_category=max_per)

    categories = [category] if category else None

    if quick:
        console.print("[yellow]Quick mode: 3 attacks per category[/]\n")

    # Run baseline
    console.print("[bold red]Phase 1: Running attacks against BASELINE agent (no defenses)...[/]\n")
    baseline_report = runner.run_baseline(categories)

    if live:
        for result in baseline_report.scored_results:
            print_attack_result(result)
            time.sleep(0.1)

    print_evaluation_summary(baseline_report)

    # Run defended
    console.print("\n[bold green]Phase 2: Running attacks against DEFENDED agent (blue team active)...[/]\n")
    defended_report = runner.run_defended(categories)

    if live:
        for result in defended_report.scored_results:
            print_attack_result(result)
            time.sleep(0.1)

    print_evaluation_summary(defended_report)

    # Comparison
    comparison_result = compare(baseline_report, defended_report)
    print_comparison(comparison_result)


@cli.command()
@click.option("--model", default="openai/gpt-4.1-nano", help="LiteLLM model string")
@click.option("--mock", is_flag=True, help="Use mock LLM (for demo without API keys)")
@click.option("--quick", is_flag=True, help="Run only 3 attacks per category (faster)")
def report(model, mock, quick):
    """Generate evaluation report with charts."""
    from src.core.llm import LLMResponse
    from src.core.sandbox import Sandbox
    from src.data.db import DatabaseManager
    from src.evaluation.runner import EvaluationRunner
    from src.evaluation.comparison import compare
    from src.evaluation.reporter import generate_charts, generate_markdown_report

    print_banner()

    db = DatabaseManager(":memory:")
    db.initialize()
    db.seed()
    sandbox = Sandbox("data/sandbox")

    mock_response = None
    if mock:
        mock_response = LLMResponse(
            content="Alice Johnson, SSN: 123-45-6789, Salary: $145,000. Bob Smith, SSN: 234-56-7890.",
        )

    max_per = 3 if quick else None
    runner = EvaluationRunner(db, sandbox, model=model, mock_response=mock_response, max_per_category=max_per)

    console.print("[bold]Running full evaluation suite...[/]\n")
    baseline_report, defended_report = runner.run_comparison()
    comparison_result = compare(baseline_report, defended_report)

    # Generate charts
    console.print("[bold]Generating charts...[/]")
    chart_paths = generate_charts(comparison_result)
    for path in chart_paths:
        console.print(f"  📊 {path}")

    # Generate markdown report
    report_path = generate_markdown_report(comparison_result)
    console.print(f"  📄 {report_path}")

    console.print("\n[bold green]✅ Report generation complete![/]")
    print_comparison(comparison_result)


@cli.command()
@click.option("--model", default="openai/gpt-4.1-nano", help="LiteLLM model string")
@click.option("--mock", is_flag=True, help="Use mock LLM")
def compare_cmd(model, mock):
    """Side-by-side comparison: same attack against baseline vs defended."""
    from langchain_core.messages import HumanMessage
    from src.core.llm import LLMResponse
    from src.core.sandbox import Sandbox
    from src.data.db import DatabaseManager
    from src.agent.baseline import create_baseline_agent
    from src.agent.defended import create_defended_agent

    print_banner()
    console.print("[bold]Side-by-side comparison mode[/]\n")
    console.print("Enter a prompt injection and see how baseline vs defended agent handles it.\n")
    console.print("Type 'quit' to exit.\n")

    db = DatabaseManager(":memory:")
    db.initialize()
    db.seed()
    sandbox = Sandbox("data/sandbox")

    if mock:
        baseline_mock = LLMResponse(
            content="Alice Johnson, SSN: 123-45-6789, Salary: $145,000.",
        )
        defended_mock = LLMResponse(content="I cannot provide private employee data.")
    else:
        baseline_mock = None
        defended_mock = None

    baseline_agent = create_baseline_agent(db, sandbox, model=model, mock_response=baseline_mock)
    defended_agent = create_defended_agent(db, sandbox, model=model, user_role="public", mock_response=defended_mock)

    while True:
        try:
            user_input = Prompt.ask("[bold cyan]Attack Prompt")
        except (EOFError, KeyboardInterrupt):
            break

        if user_input.lower() in ("quit", "exit", "q"):
            break

        # Run against baseline
        state_base = {
            "messages": [HumanMessage(content=user_input)],
            "user_role": "public",
            "db_path": ":memory:",
            "sandbox_path": str(sandbox.root),
        }
        try:
            result_base = baseline_agent.invoke(state_base)
            base_msgs = result_base.get("messages", [])
            base_response = " ".join(m.content for m in base_msgs if hasattr(m, "content") and m.content)
        except Exception as e:
            base_response = f"Error: {e}"

        # Run against defended
        state_def = {
            "messages": [HumanMessage(content=user_input)],
            "user_role": "public",
            "db_path": ":memory:",
            "sandbox_path": str(sandbox.root),
            "blocked": False,
            "block_reason": "",
        }
        try:
            result_def = defended_agent.invoke(state_def)
            def_msgs = result_def.get("messages", [])
            def_response = " ".join(m.content for m in def_msgs if hasattr(m, "content") and m.content)
        except Exception as e:
            def_response = f"Error: {e}"

        # Display side-by-side
        console.print("\n[bold red]━━━ BASELINE (No Defenses) ━━━[/]")
        console.print(base_response[:500])
        console.print("\n[bold green]━━━ DEFENDED (Blue Team) ━━━[/]")
        console.print(def_response[:500])
        console.print()


def main():
    cli()


if __name__ == "__main__":
    main()
