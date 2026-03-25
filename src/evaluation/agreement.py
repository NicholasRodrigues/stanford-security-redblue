"""Inter-method agreement metrics (Cohen's kappa)."""


def cohens_kappa(a: list[bool], b: list[bool]) -> float:
    """Compute Cohen's kappa between two binary scorers."""
    n = len(a)
    if n == 0:
        return 0.0
    observed = sum(x == y for x, y in zip(a, b)) / n
    p_a = sum(a) / n
    p_b = sum(b) / n
    expected = p_a * p_b + (1 - p_a) * (1 - p_b)
    if expected == 1.0:
        return 1.0
    return (observed - expected) / (1.0 - expected)


def scoring_agreement_report(regex_results: list[bool], judge_results: list[bool]) -> dict:
    """Compare regex scorer vs LLM judge scoring."""
    n = len(regex_results)
    kappa = cohens_kappa(regex_results, judge_results)
    agreement = sum(r == j for r, j in zip(regex_results, judge_results)) / n if n > 0 else 0.0
    # Confusion counts
    both_positive = sum(r and j for r, j in zip(regex_results, judge_results))
    both_negative = sum(not r and not j for r, j in zip(regex_results, judge_results))
    regex_only = sum(r and not j for r, j in zip(regex_results, judge_results))
    judge_only = sum(not r and j for r, j in zip(regex_results, judge_results))
    return {
        "kappa": round(kappa, 3),
        "agreement": round(agreement, 3),
        "both_positive": both_positive,
        "both_negative": both_negative,
        "regex_only": regex_only,
        "judge_only": judge_only,
        "n": n,
    }
