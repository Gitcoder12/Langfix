"""Regression tests for detection, validation and conservative repair."""
import tempfile
import shutil
import unittest
from unittest.mock import patch
from pathlib import Path

from detector import detect_language
from fixer import fix_code, fix_file, scan_code, validate_code
from lang_registry import LANGUAGE_RULES, language_for_extension


class TestLangfixPolyglot(unittest.TestCase):
    def test_registry_has_extensible_coverage(self):
        self.assertGreaterEqual(len(LANGUAGE_RULES), 15)
        self.assertEqual(language_for_extension(".rs"), "rust")
        self.assertEqual(language_for_extension("tsx"), "typescript")

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


    def test_rust_is_detected_by_extension_and_signature(self):
        self.assertEqual(detect_language("fn main() { println!(\"hello\"); }", "main.rs").language, "rust")
        self.assertEqual(detect_language("fn main() { println!(\"hello\"); }").language, "rust")

    def test_rust_validator_fails_closed_when_rustfmt_is_missing(self):
        with patch("fixer.shutil.which", return_value=None):
            result = validate_code("fn main() {}", "rust")
        self.assertEqual(result["status"], "skipped")
        self.assertIsNone(result["valid"])
        self.assertIn("not installed", result["message"])

    @unittest.skipUnless(shutil.which("rustfmt"), "rustfmt is installed in the Rust-enabled CI job")
    def test_rustfmt_validates_syntax_and_rejects_invalid_rust(self):
        valid = validate_code('fn main() { println!("hello"); }', "rust")
        invalid = validate_code("fn main( {", "rust")
        self.assertEqual(valid["status"], "passed")
        self.assertTrue(valid["valid"])
        self.assertEqual(invalid["status"], "failed")
        self.assertFalse(invalid["valid"])

    @unittest.skipUnless(shutil.which("rustfmt"), "rustfmt is installed in the Rust-enabled CI job")
    def test_rustfmt_formats_valid_rust_without_typechecking_claims(self):
        messy = 'fn main(){println!("hello");}'
        result = fix_code(messy, "rust", use_formatter=True)
        self.assertTrue(result["validation_before"]["valid"])
        self.assertTrue(result["validation_after"]["valid"])
        self.assertTrue(result["changed"])
        self.assertIn('    println!("hello");', result["fixed"])
        self.assertIsNone(result["formatter_note"])

    @unittest.skipUnless(shutil.which("rustfmt"), "rustfmt is installed in the Rust-enabled CI job")
    def test_rust_file_repair_requires_explicit_apply(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "main.rs"
            original = 'fn main(){println!("hello");}   '
            path.write_text(original, encoding="utf-8")
            preview = fix_file(path, use_formatter=True)
            self.assertTrue(preview["changed"])
            self.assertFalse(preview["written"])
            self.assertEqual(path.read_text(encoding="utf-8"), original)
            applied = fix_file(path, use_formatter=True, apply=True)
            self.assertTrue(applied["written"])
            self.assertTrue(applied["validation_after"]["valid"])
            self.assertNotEqual(path.read_text(encoding="utf-8"), original)


if __name__ == "__main__":
    unittest.main()
