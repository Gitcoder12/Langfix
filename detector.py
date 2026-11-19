"""Confidence-scored language detection for files and source snippets."""
from __future__ import annotations

import os
import re
from dataclasses import dataclass

from lang_registry import LANGUAGE_RULES, language_for_extension


@dataclass(frozen=True)
class Detection:
    language: str | None
    confidence: float
    reason: str

    def as_dict(self) -> dict:
        return {"language": self.language, "confidence": self.confidence, "reason": self.reason}


_SIGNATURES = {
    "python": [(r"^\s*def\s+\w+\s*\(", 3), (r"^\s*(async\s+)?import\s+\w+", 2), (r"^\s*class\s+\w+.*:", 2)],
    "javascript": [(r"\b(const|let|var)\s+\w+\s*=", 2), (r"=>", 2), (r"\bconsole\.log\s*\(", 2), (r"\brequire\s*\(", 2)],
    "typescript": [(r":\s*(string|number|boolean|unknown|any)(\[\])?\b", 3), (r"\binterface\s+\w+", 3), (r"\btype\s+\w+\s*=", 2)],
    "java": [(r"\bpublic\s+static\s+void\s+main\s*\(", 4), (r"\b(class|interface)\s+\w+", 2), (r"System\.out\.print", 3)],
    "go": [(r"^\s*package\s+\w+", 4), (r"\bfunc\s+(main|\w+)\s*\(", 3), (r"\bfmt\.Print", 2)],
    "rust": [(r"\bfn\s+main\s*\(", 4), (r"\blet\s+mut\s+", 2), (r"\bprintln!\s*\(", 3)],
    "ruby": [(r"^\s*def\s+\w+", 2), (r"\bputs\s+", 2), (r"\bend\s*$", 1)],
    "php": [(r"<\?php", 5), (r"\$[A-Za-z_]\w*\s*=", 2)],
    "sql": [(r"\b(SELECT|INSERT\s+INTO|UPDATE|CREATE\s+TABLE)\b", 3), (r"\bFROM\s+\w+", 1)],
    "html": [(r"<!doctype\s+html", 4), (r"<(html|head|body|div|section)\b", 2)],
    "css": [(r"(^|\})\s*[.#][\w-]+\s*\{", 3), (r"\b(color|margin|padding|display)\s*:", 1)],
    "json": [(r"^\s*[\[{]", 1), (r'"[^"]+"\s*:\s*', 2)],
    "yaml": [(r"^\s*[\w-]+:\s*[^:/]", 2), (r"^\s*---\s*$", 3)],
    "shell": [(r"^#!.*\b(bash|sh)\b", 5), (r"\b(echo|fi|then)\b", 1)],
    "c": [(r"#include\s*<[^>]+>", 2), (r"\bprintf\s*\(", 2)],
    "cpp": [(r"#include\s*<iostream>", 4), (r"\bstd::", 3), (r"\bcout\s*<<", 3)],
    "kotlin": [(r"\bfun\s+main\s*\(", 4), (r"\bval\s+\w+", 2)],
    "swift": [(r"\b(import\s+Foundation|let\s+\w+\s*=)", 1), (r"\bfunc\s+\w+\s*\(", 1)],
}


def detect_language(code: str, filename: str | None = None) -> Detection:
    """Detect a language. A known filename extension wins over heuristics."""
    if filename:
        language = language_for_extension(os.path.splitext(filename)[1])
        if language:
            return Detection(language, 1.0, f"file extension: {os.path.splitext(filename)[1]}")
    sample = code[:20000]
    scores = {name: sum(weight for pattern, weight in _SIGNATURES.get(name, []) if re.search(pattern, sample, re.I | re.M)) for name in LANGUAGE_RULES}
    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    if not ranked or ranked[0][1] == 0:
        return Detection(None, 0.0, "no distinctive language signature")
    best_name, best_score = ranked[0]
    second_score = ranked[1][1] if len(ranked) > 1 else 0
    if best_score < 2 or best_score == second_score:
        return Detection(None, 0.0, "ambiguous snippet; provide a filename or explicit language")
    confidence = min(0.99, 0.5 + 0.1 * best_score + 0.05 * (best_score - second_score))
    return Detection(best_name, round(confidence, 2), f"matched {best_score} weighted language signatures")
