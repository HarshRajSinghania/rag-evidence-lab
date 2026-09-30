import unittest
from rag_evidence_lab.core import inspect, validate


def fixture(answer, text="Refunds are available within 30 days of purchase."):
    return {"cases": [{"id": "case", "answer": answer, "sources": [{"id": "p", "text": text}]}]}


class EvidenceTests(unittest.TestCase):
    def test_grounded(self):
        self.assertEqual(inspect(fixture("Refunds are available within 30 days of purchase [p]."))["summary"]["flagged_claims"], 0)

    def test_number_drift_even_with_high_overlap(self):
        claim = inspect(fixture("Refunds are available within 90 days of purchase [p]."))["cases"][0]["claims"][0]
        self.assertIn("unmatched_number", claim["flags"])
        self.assertGreater(claim["lexical_overlap"], .45)

    def test_unknown_citation(self):
        self.assertIn("unknown_citation", inspect(fixture("Refunds [wrong]."))["cases"][0]["claims"][0]["flags"])

    def test_missing_citation(self):
        self.assertIn("missing_citation", inspect(fixture("Refunds within 30 days."))["cases"][0]["claims"][0]["flags"])

    def test_does_not_use_uncited_source_for_numbers(self):
        data = fixture("Refunds within 90 days [p].")
        data["cases"][0]["sources"].append({"id": "other", "text": "90 days"})
        self.assertIn("unmatched_number", inspect(data)["cases"][0]["claims"][0]["flags"])

    def test_decimal_not_split(self):
        self.assertEqual(inspect(fixture("Rate is 3.5 percent [p].", "Rate is 3.5 percent."))["summary"]["claims"], 1)

    def test_duplicate_ids_rejected(self):
        data = fixture("Test")
        data["cases"].append(data["cases"][0])
        with self.assertRaises(ValueError):
            validate(data)

    def test_negation_is_not_understood(self):
        # This intentionally documents the false negative: overlap cannot establish entailment.
        self.assertEqual(inspect(fixture("Refunds are not available within 30 days of purchase [p]."))["summary"]["flagged_claims"], 0)


if __name__ == "__main__":
    unittest.main()
