import json
import unittest
from servicebench.evaluate import evaluate, grade, load_cases, oracle_answer, public_case


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.cases = load_cases()
        self.case = self.cases[0]

    def test_thirty_unique_cases_have_two_real_sources(self):
        self.assertEqual(len(self.cases), 30)
        self.assertEqual(len({c["id"] for c in self.cases}), 30)
        self.assertEqual(len({c["expected"]["diagnosis"] for c in self.cases}), 30)
        for case in self.cases:
            self.assertTrue(grade(case, oracle_answer(case))["pass"])
            self.assertNotIn("expected", public_case(case))

    def test_missing_cases_cannot_improve_denominator(self):
        report = evaluate(self.cases, [{"case_id": self.case["id"], "answer": oracle_answer(self.case)}])
        self.assertEqual(report["missing"], 29)
        self.assertAlmostEqual(report["pass_rate"], 1 / 30)

    def test_forged_and_blank_evidence_fail(self):
        for evidence in ([{"source_id": "invented", "quote": "A made up quotation"}],
                         [{"source_id": "log", "quote": ""}], None, [42]):
            answer = oracle_answer(self.case)
            answer["evidence"] = evidence
            self.assertFalse(grade(self.case, answer)["pass"])

    def test_wrong_part_and_unsafe_action_fail(self):
        case = next(c for c in self.cases if c["expected"]["action"] == "escalate")
        answer = oracle_answer(case)
        answer["action"] = "fix_on_site"
        answer["parts"] = ["UNAPPROVED-PART"]
        result = grade(case, answer)
        self.assertFalse(result["pass"])
        self.assertFalse(result["checks"]["action"])
        self.assertFalse(result["checks"]["compatible_parts"])

    def test_invalid_outputs_are_failures_not_excluded(self):
        for output in (None, "not JSON", [], "null", 7):
            self.assertEqual(grade(self.case, output)["score"], 0)

    def test_duplicate_and_unknown_ids_rejected(self):
        p = {"case_id": self.case["id"], "answer": {}}
        for predictions in ([p, p], [{"case_id": "unknown", "answer": {}}]):
            with self.assertRaises(ValueError):
                evaluate(self.cases, predictions)

    def test_promptfoo_adapter_uses_same_grader(self):
        from examples.assertion import get_assert
        from examples.reference_provider import call_api
        context = {"vars": {"case_id": self.case["id"]}}
        response = call_api("unused", {}, context)
        self.assertTrue(get_assert(response["output"], context)["pass"])

    def test_promptfoo_export_does_not_forward_grading_labels(self):
        import subprocess
        import sys
        result = subprocess.run([sys.executable, "-m", "servicebench", "export-promptfoo"],
                                capture_output=True, text=True, check=True)
        config = json.loads(result.stdout)
        self.assertEqual(len(config["tests"]), 30)
        for test in config["tests"]:
            self.assertEqual(set(test["vars"]), {"case_id", "task"})
            self.assertNotIn("expected", json.loads(test["vars"]["task"]))


if __name__ == "__main__":
    unittest.main()
