"""Tests for the executable messy-code demo."""
import unittest
from demo import build_cases, run_demo

class TestMessyCodeDemo(unittest.TestCase):
    def test_demo_contains_valid_and_invalid_inputs(self):
        cases = build_cases()
        self.assertGreaterEqual(len(cases), 6)
        self.assertTrue(any(case.expect_repair for case in cases))
        self.assertTrue(any(not case.expect_repair for case in cases))

    def test_demo_is_deterministic(self):
        first = [(case.name, case.source) for case in build_cases(42)]
        second = [(case.name, case.source) for case in build_cases(42)]
        self.assertEqual(first, second)

    def test_every_case_passes_and_invalid_code_is_preserved(self):
        results = run_demo(show=False)
        self.assertTrue(all(item["passed"] for item in results))
        invalid = [item for item in results if not item["expected_repair"]]
        self.assertTrue(invalid)
        self.assertTrue(all(not item["changed"] for item in invalid))
        self.assertTrue(all(item["valid_before"] is False for item in invalid))

if __name__ == "__main__":
    unittest.main()