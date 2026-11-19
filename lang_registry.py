"""Extensible language capabilities for LangFix.

Add a language by adding one entry to LANGUAGE_RULES. Commands are argument
arrays (never shell strings) and optional tools are reported as unavailable.
"""
from __future__ import annotations

LANGUAGE_RULES = {
    "python": {"extensions": [".py", ".pyw"], "comments": ["#"], "brackets": {"(": ")", "[": "]", "{": "}"}, "anti_patterns": [r"\beval\s*\(", r"\bexec\s*\("], "formatter": ["black", "--quiet", "-"], "validator": "python_ast", "tree_sitter": "python"},
    "javascript": {"extensions": [".js", ".mjs", ".cjs", ".jsx"], "comments": ["//", "/* */"], "brackets": {"(": ")", "[": "]", "{": "}"}, "anti_patterns": [r"\beval\s*\(", r"document\.write\s*\("], "formatter": ["prettier", "--parser", "babel"], "validator": ["node", "--check"], "tree_sitter": "javascript"},
    "typescript": {"extensions": [".ts", ".tsx"], "comments": ["//", "/* */"], "brackets": {"(": ")", "[": "]", "{": "}"}, "anti_patterns": [r"\bas\s+any\b"], "formatter": ["prettier", "--parser", "typescript"], "validator": ["tsc", "--noEmit", "--pretty", "false"], "tree_sitter": "typescript"},
    "java": {"extensions": [".java"], "comments": ["//", "/* */"], "brackets": {"(": ")", "[": "]", "{": "}"}, "anti_patterns": [r"Runtime\.getRuntime\(\)\.exec"], "formatter": ["google-java-format", "--replace"], "validator": ["javac"], "tree_sitter": "java"},
    "c": {"extensions": [".c", ".h"], "comments": ["//", "/* */"], "brackets": {"(": ")", "[": "]", "{": "}"}, "anti_patterns": [r"\bgets\s*\("], "formatter": ["clang-format", "-i"], "validator": ["clang", "-fsyntax-only"], "tree_sitter": "c"},
    "cpp": {"extensions": [".cc", ".cpp", ".cxx", ".hpp", ".hh", ".hxx"], "comments": ["//", "/* */"], "brackets": {"(": ")", "[": "]", "{": "}"}, "anti_patterns": [r"\bgets\s*\(", r"using\s+namespace\s+std"], "formatter": ["clang-format", "-i"], "validator": ["clang++", "-fsyntax-only"], "tree_sitter": "cpp"},
    "go": {"extensions": [".go"], "comments": ["//", "/* */"], "brackets": {"(": ")", "[": "]", "{": "}"}, "anti_patterns": [r"fmt\.Println\s*\("], "formatter": ["gofmt", "-w"], "validator": ["gofmt", "-d"], "tree_sitter": "go"},
    "rust": {"extensions": [".rs"], "comments": ["//", "/* */"], "brackets": {"(": ")", "[": "]", "{": "}"}, "anti_patterns": [r"\bunwrap\s*\("], "formatter": ["rustfmt"], "validator": ["rustfmt", "--emit", "stdout"], "tree_sitter": "rust"},
    "sql": {"extensions": [".sql"], "comments": ["--", "/* */"], "brackets": {"(": ")"} , "anti_patterns": [r"SELECT\s+\*"], "formatter": ["sqlfluff", "format", "--dialect", "ansi", "-"], "validator": None, "tree_sitter": "sql"},
    "html": {"extensions": [".html", ".htm"], "comments": ["<!-- -->"], "brackets": {}, "anti_patterns": [r" on\w+\s*="], "formatter": ["prettier", "--parser", "html"], "validator": None, "tree_sitter": "html"},
    "css": {"extensions": [".css"], "comments": ["/* */"], "brackets": {"{": "}", "(": ")"}, "anti_patterns": [r"!important"], "formatter": ["prettier", "--parser", "css"], "validator": None, "tree_sitter": "css"},
    "json": {"extensions": [".json"], "comments": [], "brackets": {"{": "}", "[": "]"}, "anti_patterns": [], "formatter": None, "validator": "json", "tree_sitter": "json"},
    "yaml": {"extensions": [".yaml", ".yml"], "comments": ["#"], "brackets": {"[": "]", "{": "}"}, "anti_patterns": [], "formatter": None, "validator": "yaml_optional", "tree_sitter": "yaml"},
    "ruby": {"extensions": [".rb"], "comments": ["#"], "brackets": {"(": ")", "[": "]", "{": "}"}, "anti_patterns": [r"\beval\s*\("], "formatter": ["rubocop", "-A"], "validator": ["ruby", "-c"], "tree_sitter": "ruby"},
    "php": {"extensions": [".php"], "comments": ["//", "#", "/* */"], "brackets": {"(": ")", "[": "]", "{": "}"}, "anti_patterns": [r"\beval\s*\("], "formatter": ["php-cs-fixer", "fix"], "validator": ["php", "-l"], "tree_sitter": "php"},
    "shell": {"extensions": [".sh", ".bash"], "comments": ["#"], "brackets": {"(": ")", "{": "}"}, "anti_patterns": [r"\beval\s+"], "formatter": ["shfmt", "-w"], "validator": ["bash", "-n"], "tree_sitter": "bash"},
    "kotlin": {"extensions": [".kt", ".kts"], "comments": ["//", "/* */"], "brackets": {"(": ")", "[": "]", "{": "}"}, "anti_patterns": [], "formatter": ["ktlint", "-F"], "validator": ["kotlinc"], "tree_sitter": "kotlin"},
    "swift": {"extensions": [".swift"], "comments": ["//", "/* */"], "brackets": {"(": ")", "[": "]", "{": "}"}, "anti_patterns": [], "formatter": ["swiftformat"], "validator": ["swiftc", "-typecheck"], "tree_sitter": "swift"},
}


def get_language(name: str) -> dict | None:
    """Return a language definition by canonical name."""
    return LANGUAGE_RULES.get(name.lower().strip())


def language_for_extension(extension: str) -> str | None:
    """Resolve a filename extension (including its leading dot)."""
    ext = extension.lower() if extension.startswith(".") else f".{extension.lower()}"
    return next((name for name, rules in LANGUAGE_RULES.items() if ext in rules["extensions"]), None)
