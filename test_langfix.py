import os
import unittest

from langfix import analyze_file


class TestLangFix(unittest.TestCase):
    def setUp(self):
        with open("test_good.py", "w", encoding="utf-8") as handle:
            handle.write(
                'def add(a, b):\n'
                '    """Adds two numbers."""\n'
                '    return a + b\n'
            )

        with open("test_bad.py", "w", encoding="utf-8") as handle:
            handle.write('password = "secret123"\n')

    def tearDown(self):
        for path in ("test_good.py", "test_bad.py"):
            if os.path.exists(path):
                os.remove(path)

    def test_good_code_returns_expected_analysis_mapping(self):
        result = analyze_file("test_good.py")
        self.assertEqual(result["vibe"], "AWESOME")
        self.assertEqual(result["score"], 100)

    def test_security_flaw_returns_failure_mapping(self):
        result = analyze_file("test_bad.py")
        self.assertEqual(result["vibe"], "FAIL")
        self.assertEqual(result["score"], 10)
        self.assertIn("Hardcoded secret/password", result["note"])


if __name__ == "__main__":
    unittest.main()
