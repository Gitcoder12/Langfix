"""Conservative source cleanup, validation and unified-diff generation."""
from __future__ import annotations

import ast
import difflib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from lang_registry import LANGUAGE_RULES


def _run(command: list[str], *, input_text: str | None = None, timeout: int = 10) -> subprocess.CompletedProcess:
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or timeout <= 0:
        raise ValueError("timeout must be a finite positive number")
    return subprocess.run(command, input=input_text, capture_output=True, text=True, timeout=timeout, check=False)


def _module_available(name: str) -> bool:
    try:
        __import__(name)
        return True
    except ImportError:
        return False


def validate_code(code: str, language: str, timeout: int = 10) -> dict:
    """Validate syntax only where an available validator can do so reliably."""
    if not isinstance(code, str):
        raise TypeError("code must be a string")
    if not isinstance(language, str):
        raise TypeError("language must be a string")
    language = language.lower().strip()
    if language not in LANGUAGE_RULES:
        return {"status": "unsupported", "valid": None, "message": f"Unsupported language: {language}"}
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or timeout <= 0:
        raise ValueError("timeout must be a finite positive number")

    if language == "python":
        try:
            ast.parse(code)
            return {"status": "passed", "valid": True, "message": "Python AST parsed successfully"}
        except SyntaxError as exc:
            return {"status": "failed", "valid": False, "message": f"{exc.msg} (line {exc.lineno}, column {exc.offset})"}

    if language == "json":
        try:
            json.loads(code)
            return {"status": "passed", "valid": True, "message": "Valid JSON"}
        except json.JSONDecodeError as exc:
            return {"status": "failed", "valid": False, "message": f"{exc.msg} (line {exc.lineno}, column {exc.colno})"}

    if language == "yaml":
        if not _module_available("yaml"):
            return {"status": "skipped", "valid": None, "message": "Install PyYAML for YAML syntax validation"}
        try:
            import yaml
            yaml.safe_load(code)
            return {"status": "passed", "valid": True, "message": "YAML parsed successfully"}
        except Exception as exc:
            return {"status": "failed", "valid": False, "message": str(exc)}

    validator = LANGUAGE_RULES[language]["validator"]
    if not validator:
        return {"status": "skipped", "valid": None, "message": "No safe syntax validator configured"}
    if isinstance(validator, str):
        return {"status": "skipped", "valid": None, "message": f"Validator '{validator}' is not implemented"}
    executable = validator[0]
    if not shutil.which(executable):
        return {"status": "skipped", "valid": None, "message": f"Optional validator '{executable}' is not installed"}

    with tempfile.TemporaryDirectory(prefix="langfix-") as tmp:
        source = Path(tmp) / f"input{LANGUAGE_RULES[language]['extensions'][0]}"
        source.write_text(code, encoding="utf-8")
        command = [
            part.replace("{file}", str(source)).replace("{tmp}", tmp)
            for part in validator
        ]
        if "{file}" not in " ".join(validator) and language in {
            "java", "c", "cpp", "swift", "kotlin", "javascript", "typescript",
            "go", "rust", "ruby", "php", "shell",
        }:
            command.append(str(source))
        try:
            result = _run(command, timeout=timeout)
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "valid": None, "message": f"Validator exceeded {timeout}s"}
        output = (result.stderr or result.stdout).strip()
        if result.returncode:
            return {"status": "failed", "valid": False, "message": output[:2000] or "Syntax validation failed"}
        return {"status": "passed", "valid": True, "message": output[:1000] or f"{executable} passed"}


def _safe_cleanup(code: str) -> str:
    """Remove trailing horizontal whitespace and ensure one final newline."""
    lines = [line.rstrip(" \t") for line in code.splitlines()]
    cleaned = "\n".join(lines)
    return cleaned.rstrip("\n") + "\n" if cleaned else ""


def _format_with_tool(code: str, language: str, timeout: int) -> tuple[str, str | None]:
    formatter = LANGUAGE_RULES[language].get("formatter")
    if not formatter:
        return code, "No external formatter configured"
    executable = formatter[0]
    if not shutil.which(executable):
        return code, f"Optional formatter '{executable}' is not installed"
    if executable == "black":
        command = ["black", "--quiet", "-"]
    elif executable == "prettier":
        command = ["prettier", "--parser", formatter[2]]
    else:
        return code, f"Formatter '{executable}' requires explicit file/project context; not run"
    try:
        result = _run(command, input_text=code, timeout=timeout)
    except subprocess.TimeoutExpired:
        return code, f"Formatter exceeded {timeout}s"
    if result.returncode:
        return code, (result.stderr or result.stdout).strip()[:1000] or "Formatter failed"
    return result.stdout, None


def scan_code(code: str, language: str, timeout: int = 10) -> dict:
    """Report syntax, whitespace and configured heuristic findings."""
    import re

    language = language.lower().strip()
    if language not in LANGUAGE_RULES:
        raise ValueError(f"Unsupported language: {language}")
    syntax = validate_code(code, language, timeout)
    findings = []
    for number, line in enumerate(code.splitlines(), start=1):
        if line.rstrip(" \t") != line:
            findings.append({"rule": "format.trailing-whitespace", "line": number, "severity": "warning", "message": "Trailing whitespace"})
    if code and not code.endswith("\n"):
        findings.append({"rule": "format.final-newline", "line": len(code.splitlines()), "severity": "warning", "message": "File does not end with a newline"})
    for pattern in LANGUAGE_RULES[language].get("anti_patterns", []):
        for match in re.finditer(pattern, code, re.IGNORECASE):
            line = code.count("\n", 0, match.start()) + 1
            findings.append({"rule": "heuristic.anti-pattern", "line": line, "severity": "info", "message": f"Matched configured heuristic: {pattern}"})
    if syntax["valid"] is False:
        findings.insert(0, {"rule": "syntax.invalid", "line": None, "severity": "error", "message": syntax["message"]})
    return {"language": language, "syntax": syntax, "findings": findings, "clean": not findings}


def fix_code(code: str, language: str, *, use_formatter: bool = False, timeout: int = 10) -> dict:
    """Propose a repair; unverifiable or invalid source is preserved unchanged."""
    language = language.lower().strip()
    if language not in LANGUAGE_RULES:
        raise ValueError(f"Unsupported language: {language}")
    before_validation = validate_code(code, language, timeout)
    findings_before = scan_code(code, language, timeout)["findings"]
    can_transform = before_validation["valid"] is True
    candidate = code
    formatter_note = None
    if can_transform and language not in {"shell"}:
        candidate = _safe_cleanup(code)
    if use_formatter and can_transform:
        candidate, formatter_note = _format_with_tool(candidate, language, timeout)
        if language != "shell":
            candidate = _safe_cleanup(candidate)
    after_validation = validate_code(candidate, language, timeout)
    if can_transform and after_validation["valid"] is not True:
        candidate = code
        after_validation = before_validation
        formatter_note = "Candidate rejected: validation regressed; original source preserved"
    diff = "".join(difflib.unified_diff(code.splitlines(keepends=True), candidate.splitlines(keepends=True), fromfile="original", tofile="fixed"))
    return {
        "language": language, "original": code, "fixed": candidate,
        "changed": candidate != code, "diff": diff,
        "validation_before": before_validation, "findings_before": findings_before,
        "validation_after": after_validation, "formatter_note": formatter_note,
    }


def fix_file(path: str | os.PathLike, *, use_formatter: bool = False, apply: bool = False, timeout: int = 10) -> dict:
    """Fix a source file; writing occurs only when apply=True."""
    file_path = Path(path)
    from detector import detect_language
    original = file_path.read_text(encoding="utf-8")
    detection = detect_language(original, str(file_path))
    if not detection.language:
        raise ValueError(f"Could not detect language: {detection.reason}")
    result = fix_code(original, detection.language, use_formatter=use_formatter, timeout=timeout)
    result["file"] = str(file_path)
    result["detection"] = detection.as_dict()
    if apply and result["changed"]:
        file_path.write_text(result["fixed"], encoding="utf-8")
        result["written"] = True
    else:
        result["written"] = False
    return result
