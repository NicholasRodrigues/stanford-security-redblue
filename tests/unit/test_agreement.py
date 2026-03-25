from src.evaluation.agreement import cohens_kappa, scoring_agreement_report


class TestCohensKappa:
    def test_perfect_agreement(self):
        a = [True, False, True, False]
        b = [True, False, True, False]
        assert cohens_kappa(a, b) == 1.0

    def test_no_agreement(self):
        a = [True, True, False, False]
        b = [False, False, True, True]
        k = cohens_kappa(a, b)
        assert k < 0  # worse than chance

    def test_partial_agreement(self):
        a = [True, True, False, False]
        b = [True, False, False, True]
        k = cohens_kappa(a, b)
        assert -1.0 <= k <= 1.0

    def test_empty_lists(self):
        assert cohens_kappa([], []) == 0.0


class TestAgreementReport:
    def test_report_keys(self):
        r = scoring_agreement_report([True, False], [True, False])
        assert "kappa" in r
        assert "agreement" in r
        assert "both_positive" in r
        assert "both_negative" in r
        assert "n" in r

    def test_perfect_agreement_report(self):
        r = scoring_agreement_report([True, False, True], [True, False, True])
        assert r["agreement"] == 1.0
        assert r["kappa"] == 1.0
        assert r["regex_only"] == 0
        assert r["judge_only"] == 0
