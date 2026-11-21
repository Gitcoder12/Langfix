"""Extensible language capabilities for LangFix.

A registry entry advertises file recognition and conservative tooling only.
A language is not syntax-validated unless its validator is explicitly supported.
"""
from __future__ import annotations

LANGUAGE_RULES = {
    "python": {"extensions": [".py", ".pyw"], "comments": ["#"], "brackets": {"(": ")", "[": "]", "{": "}"}, "anti_patterns": [r"\beval\s*\(", r"\bexec\s*("], "formatter": ["black", "--quiet", "-"], "validator": "python_ast", "tree_sitter": "python"},
    "javascript": {"extensions": [".js", ".mjs", ".cjs", ".jsx"], "comments": ["//", "/* */"], "brackets": {"(": ")", "[": "]", "{": "}"}, "anti_patterns": [r"\beval\s*\(", r"document\.write\s*\("], "formatter": ["prettier", "--parser", "babel"], "validator": ["node", "--check"], "tree_sitter": "javascript"},
    "typescript": {"extensions": [".ts", ".tsx"], "comments": ["//", "/* */"], "brackets": {"(": ")", "[": "]", "{": "}"}, "anti_patterns": [r"\bas\s+any\b"], "formatter": ["prettier", "--parser", "typescript"], "validator": ["tsc", "--noEmit", "--pretty", "false"], "tree_sitter": "typescript"},
    "java": {"extensions": [".java"], "comments": ["//", "/* */"], "brackets": {"(": ")", "[": "]", "{": "}"}, "anti_patterns": [r"Runtime\.getRuntime\(\)\.exec"], "formatter": ["google-java-format", "--replace"], "validator": ["javac"], "tree_sitter": "java"},
    "c": {"extensions": [".c", ".h"], "comments": ["//", "/* */"], "brackets": {"(": ")", "[": "]", "{": "}"}, "anti_patterns": [r"\bgets\s*\("], "formatter": ["clang-format", "-i"], "validator": ["clang", "-fsyntax-only"], "tree_sitter": "c"},
    "cpp": {"extensions": [".cc", ".cpp", ".cxx", ".hpp", ".hh", ".hxx"], "comments": ["//", "/* */"], "brackets": {"(": ")", "[": "]", "{": "}"}, "anti_patterns": [r"\bgets\s*\(", r"using\s+namespace\s+std"], "formatter": ["clang-format", "-i"], "validator": ["clang++", "-fsyntax-only"], "tree_sitter": "cpp"},
    "go": {"extensions": [".go"], "comments": ["//", "/* */"], "brackets": {"(": ")", "[": "]", "{": "}"}, "anti_patterns": [r"fmt\.Println\s*\("], "formatter": ["gofmt", "-w"], "validator": ["gofmt", "-d"], "tree_sitter": "go"},
    "rust": {"extensions": [".rs"], "comments": ["//", "/* */"], "brackets": {"(": ")", "[": "]", "{": "}"}, "anti_patterns": [r"\bunwrap\s*\("], "formatter": ["rustfmt"], "validator": ["rustfmt", "--emit", "stdout"], "tree_sitter": "rust"},
    "sql": {"extensions": [".sql"], "comments": ["--", "/* */"], "brackets": {"(": ")"}, "anti_patterns": [r"SELECT\s+\*"], "formatter": ["sqlfluff", "format", "--dialect", "ansi", "-"], "validator": None, "tree_sitter": "sql"},
    "html": {"extensions": [".html", ".htm"], "comments": ["<!-- -->"], "brackets": {}, "anti_patterns": [r" on\w+\s*="], "formatter": ["prettier", "--parser", "html"], "validator": None, "tree_sitter": "html"},
    "css": {"extensions": [".css"], "comments": ["/* */"], "brackets": {"{": "}", "(": ")"}, "anti_patterns": [r"!important"], "formatter": ["prettier", "--parser", "css"], "validator": None, "tree_sitter": "css"},
    "json": {"extensions": [".json"], "comments": [], "brackets": {"{": "}", "[": "]"}, "anti_patterns": [], "formatter": None, "validator": "json", "tree_sitter": "json"},
    "yaml": {"extensions": [".yaml", ".yml"], "comments": ["#"], "brackets": {"[": "]", "{": "}"}, "anti_patterns": [], "formatter": None, "validator": "yaml_optional", "tree_sitter": "yaml"},
    "ruby": {"extensions": [".rb"], "comments": ["#"], "brackets": {"(": ")", "[": "]", "{": "}"}, "anti_patterns": [r"\beval\s*\("], "formatter": ["rubocop", "-A"], "validator": ["ruby", "-c"], "tree_sitter": "ruby"},
    "php": {"extensions": [".php"], "comments": ["//", "#", "/* */"], "brackets": {"(": ")", "[": "]", "{": "}"}, "anti_patterns": [r"\beval\s*\("], "formatter": ["php-cs-fixer", "fix"], "validator": ["php", "-l"], "tree_sitter": "php"},
    "shell": {"extensions": [".sh", ".bash"], "comments": ["#"], "brackets": {"(": ")", "{": "}"} , "anti_patterns": [r"\beval\s+"], "formatter": ["shfmt", "-w"], "validator": ["bash", "-n"], "tree_sitter": "bash"},
    "kotlin": {"extensions": [".kt", ".kts"], "comments": ["//", "/* */"], "brackets": {"(": ")", "[": "]", "{": "}"}, "anti_patterns": [], "formatter": ["ktlint", "-F"], "validator": ["kotlinc"], "tree_sitter": "kotlin"},
    "swift": {"extensions": [".swift"], "comments": ["//", "/* */"], "brackets": {"(": ")", "[": "]", "{": "}"}, "anti_patterns": [], "formatter": ["swiftformat"], "validator": ["swiftc", "-typecheck"], "tree_sitter": "swift"},
    # Systems, functional, symbolic and scientific languages. Validators below
    # are syntax/compile checks only; no target program is executed.
    "haskell": {"extensions": [".hs", ".lhs"], "comments": ["--", "{- -}"], "brackets": {"(": ")", "[": "]", "{": "}"}, "anti_patterns": [], "formatter": None, "validator": ["ghc", "-fno-code", "{file}"], "tree_sitter": "haskell"},
    "ocaml": {"extensions": [".ml", ".mli"], "comments": ["(* *)"], "brackets": {"(": ")", "[": "]", "{": "}"}, "anti_patterns": [], "formatter": None, "validator": ["ocamlc", "-stop-after", "parsing", "{file}"], "tree_sitter": "ocaml"},
    "scala": {"extensions": [".scala", ".sc"], "comments": ["//", "/* */"], "brackets": {"(": ")", "[": "]", "{": "}"}, "anti_patterns": [], "formatter": None, "validator": ["scalac", "-Ystop-after:parser", "{file}"], "tree_sitter": "scala"},
    "elixir": {"extensions": [".ex", ".exs"], "comments": ["#"], "brackets": {"(": ")", "[": "]", "{": "}"}, "anti_patterns": [], "formatter": None, "validator": None, "tree_sitter": "elixir"},
    "erlang": {"extensions": [".erl", ".hrl"], "comments": ["%"], "brackets": {"(": ")", "[": "]", "{": "}"}, "anti_patterns": [], "formatter": None, "validator": None, "tree_sitter": "erlang"},
    "clojure": {"extensions": [".clj", ".cljs", ".cljc", ".edn"], "comments": [";"], "brackets": {"(": ")", "[": "]", "{": "}"}, "anti_patterns": [], "formatter": None, "validator": None, "tree_sitter": "clojure"},
    "julia": {"extensions": [".jl"], "comments": ["#"], "brackets": {"(": ")", "[": "]", "{": "}"}, "anti_patterns": [], "formatter": None, "validator": ["julia", "--startup-file=no", "-e", "Meta.parseall(read(ARGS[1], String))", "{file}"], "tree_sitter": "julia"},
    "lua": {"extensions": [".lua"], "comments": ["--", "--[[ ]]"], "brackets": {"(": ")", "[": "]", "{": "}"}, "anti_patterns": [], "formatter": None, "validator": ["luac", "-p", "{file}"], "tree_sitter": "lua"},
    "perl": {"extensions": [".pl", ".pm"], "comments": ["#"], "brackets": {"(": ")", "[": "]", "{": "}"}, "anti_patterns": [], "formatter": None, "validator": None, "tree_sitter": "perl"},
    "r": {"extensions": [".r", ".R"], "comments": ["#"], "brackets": {"(": ")", "[": "]", "{": "}"}, "anti_patterns": [], "formatter": None, "validator": ["Rscript", "-e", "parse(file=commandArgs(TRUE)[1])", "{file}"], "tree_sitter": "r"},
    "dart": {"extensions": [".dart"], "comments": ["//", "/* */"], "brackets": {"(": ")", "[": "]", "{": "}"}, "anti_patterns": [], "formatter": None, "validator": ["dart", "analyze", "{file}"], "tree_sitter": "dart"},
    "solidity": {"extensions": [".sol"], "comments": ["//", "/* */"], "brackets": {"(": ")", "[": "]", "{": "}"}, "anti_patterns": [], "formatter": None, "validator": ["solc", "--stop-after", "parsing", "{file}"], "tree_sitter": "solidity"},
    "zig": {"extensions": [".zig"], "comments": ["//"], "brackets": {"(": ")", "[": "]", "{": "}"}, "anti_patterns": [], "formatter": None, "validator": ["zig", "ast-check", "{file}"], "tree_sitter": "zig"},
    "prolog": {"extensions": [".pl", ".pro"], "comments": ["%"], "brackets": {"(": ")", "[": "]", "{": "}"}, "anti_patterns": [], "formatter": None, "validator": None, "tree_sitter": "prolog"},
    "fsharp": {"extensions": [".fs", ".fsi", ".fsx"], "comments": ["//", "(* *)"], "brackets": {"(": ")", "[": "]", "{": "}"}, "anti_patterns": [], "formatter": None, "validator": None, "tree_sitter": "fsharp"},
}


def get_language(name: str) -> dict | None:
    """Return a language definition by canonical name."""
    return LANGUAGE_RULES.get(name.lower().strip())


def language_for_extension(extension: str) -> str | None:
    """Resolve a filename extension (including its leading dot)."""
    ext = extension.lower() if extension.startswith(".") else f".{extension.lower()}"
    matches = [name for name, rules in LANGUAGE_RULES.items() if ext in rules["extensions"]]
    if len(matches) > 1:
        # .pl is shared by Perl and Prolog; avoid an arbitrary language guess.
        return None
    return matches[0] if matches else None
