"""Regression tests for polyglot detection, validation and conservative repair."""
import tempfile
import unittest
from pathlib import Path

from detector import detect_language
from fixer import fix_code, fix_file, scan_code, validate_code
from lang_registry import LANGUAGE_RULES, language_for_extension


class TestLangfixPolyglot(unittest.TestCase):
    def test_registry_has_advanced_language_coverage(self):
        self.assertGreaterEqual(len(LANGUAGE_RULES), 30)
        self.assertEqual(language_for_extension(".rs"), "rust")
        self.assertEqual(language_for_extension("tsx"), "typescript")
        self.assertEqual(language_for_extension(".hs"), "haskell")
        self.assertEqual(language_for_extension(".zig"), "zig")
        self.assertEqual(language_for_extension(".jl"), "julia")
        self.assertEqual(language_for_extension(".sol"), "solidity")

    def test_ambiguous_perl_prolog_extension_is_not_guessed(self):
        self.assertIsNone(language_for_extension(".pl"))

    def test_detects_language_from_extension_and_snippet(self):
        self.assertEqual(detect_language("not really code", "app.py").language, "python")
        self.assertEqual(detect_language("package main\nfunc main() {}").language, "go")
        self.assertEqual(detect_language("interface User { name: string }").language, "typescript")

    def test_ambiguous_snippet_is_not_guessed(self):
        result = detect_language("hello world")
        self.assertIsNone(result.language)
        self.assertEqual(result.confidence, 0.0)

    def test_broken_python_and_json_are_preserved(self):
        broken = "def add(a, b)\n    return a + b"
        self.assertFalse(validate_code(broken, "python")["valid"])
        self.assertFalse(validate_code('{"key": }', "json")["valid"])
        self.assertFalse(scan_code(broken, "python")["clean"])
        result = fix_code(broken, "python")
        self.assertEqual(result["fixed"], broken)
        self.assertFalse(result["validation_after"]["valid"])

    def test_safe_cleanup_and_unified_diff_for_valid_python(self):
        messy = "def add(a, b):  \n    return a + b   "
        result = fix_code(messy, "python")
        self.assertTrue(result["changed"])
        self.assertTrue(result["validation_after"]["valid"])
        self.assertIn("--- original", result["diff"])
        self.assertIn("+++ fixed", result["diff"])
        self.assertTrue(result["fixed"].endswith("\n"))

    def test_shell_backslash_whitespace_is_never_rewritten(self):
        source = "printf '%s' foo\\ \nbar"
        result = fix_code(source, "shell")
        self.assertEqual(result["fixed"], source)
        self.assertFalse(result["changed"])

    def test_unvalidated_language_is_preserved(self):
        source = "<div>hello</div>   "
        result = fix_code(source, "html")
        self.assertIsNone(result["validation_before"]["valid"])
        self.assertEqual(result["fixed"], source)
        self.assertFalse(result["changed"])

    def test_fix_file_is_preview_only_unless_apply_is_true(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.py"
            original = "value = 1   "
            path.write_text(original, encoding="utf-8")
            preview = fix_file(path)
            self.assertTrue(preview["changed"])
            self.assertFalse(preview["written"])
            self.assertEqual(path.read_text(encoding="utf-8"), original)
            applied = fix_file(path, apply=True)
            self.assertTrue(applied["written"])
            self.assertEqual(path.read_text(encoding="utf-8"), "value = 1\n")

    def test_unavailable_advanced_validator_is_reported_as_skipped(self):
        result = validate_code("module Example where\nmain = pure ()", "haskell")
        if result["status"] == "skipped":
            self.assertIsNone(result["valid"])
            self.assertIn("not installed", result["message"])

    def test_registry_only_does_not_claim_unsupported_validator(self):
        for language in ("elixir", "erlang", "clojure", "perl", "prolog", "fsharp"):
            self.assertIsNone(LANGUAGE_RULES[language]["validator"])
            self.assertIsNone(validate_code("source", language)["valid"])


    def test_validator_rejects_non_finite_timeouts(self):
        import math
        for timeout in (math.nan, math.inf, -math.inf):
            with self.assertRaises(ValueError):
                validate_code("value = 1", "python", timeout=timeout)


if __name__ == "__main__":
    unittest.main()
