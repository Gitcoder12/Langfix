# LangFix

A lightweight, multi-language source-code inspection CLI. LangFix scans a project for selected syntax problems, heuristic security patterns, Python complexity/documentation issues, and formatting opportunities. It can emit JSON or SARIF reports and optionally run supported formatters.

> **Scope:** LangFix is an early-stage static-analysis utility, not a compiler, SAST platform, or complete security audit. Its pattern-based checks can produce false positives and miss real issues. Review every finding before acting on it.

## What it checks

| Area | Current behavior |
|---|---|
| File coverage | Discovers Python, JavaScript, TypeScript, PHP, Ruby, Go, Rust, C, C++, and Java files |
| Syntax | Python AST parsing; external checks for JavaScript/TypeScript (Node), PHP, Ruby, and Go when their tools are installed |
| Security signals | Regex checks for selected hardcoded-secret, SQL-like, dynamic-execution, Node child-process, and PHP shell-execution patterns |
| Complexity | Radon cyclomatic-complexity checks for Python |
| Documentation | Python function/class docstring coverage |
| Formatting | Black check for Python |
| Auto-fix | Black for Python, Prettier for JavaScript/TypeScript, and gofmt for Go |
| Reports | Terminal, JSON, and SARIF |

Language support is not uniform: discovering a file extension does not mean LangFix performs a language-native parse or full semantic analysis for that language. Missing external tools may cause checks to be skipped.

## Requirements

- Python 3.10+
- Install the Python dependencies from `requirements.txt`
- Optional tools, depending on the files you scan: Node.js, PHP, Ruby, and Go toolchains; Prettier for JS/TS formatting

## Install

```bash
git clone https://github.com/Gitcoder12/Langfix.git
cd Langfix
python -m pip install -r requirements.txt
```

## Usage

Run a scan:

```bash
python langfix.py ./src
```

Apply supported formatting fixes before analysis:

```bash
python langfix.py ./src --fix
```

Write machine-readable JSON to stdout:

```bash
python langfix.py ./src --json
```

Generate a SARIF report at `langfix.sarif`:

```bash
python langfix.py ./src --sarif
```

Choose the worker count:

```bash
python langfix.py ./src --workers 8
```

Combine flags where appropriate, for example:

```bash
python langfix.py ./src --json --workers 8
```

## Scoring

Each analyzed file receives a heuristic score from 0 to 100:

| Condition | Score |
|---|---:|
| Syntax check reports an error | 0 |
| A configured security pattern matches | 10 |
| Python complexity exceeds the configured threshold | 30 |
| Otherwise | Average of formatting and documentation scores |

Grades are `AWESOME` (100), `GOOD` (70–99), `POOR` (40–69), and `FAIL` (0–39).

These scores are prioritization signals from the current implementation—not a calibrated measure of overall code quality or security. In particular, checks and scoring differ by language.

## Cache and exclusions

LangFix stores file hashes in `.langfix_cache.json` to skip unchanged files on later runs. The scanner currently excludes `.git`, `venv`, `__pycache__`, `node_modules`, and `.github`, along with its own main and test files.

## Development

Install dependencies, then run the current test module with:

```bash
python -m unittest test_langfix.py
```

The test module and analyzer interface are currently out of sync; treat the test result as a known maintenance issue until that is corrected. Do not interpret the presence of CI configuration as proof that the suite passes.

## Current limitations

- Security checks are regex heuristics; they do not perform taint analysis or prove exploitability.
- JavaScript/TypeScript checking uses `node --check`; it is not a TypeScript type-check or project build.
- Several recognized extensions do not yet have a language-native syntax checker.
- Complexity and docstring analysis currently apply to Python only.
- Formatter availability and behavior depend on tools installed in the environment.
- Cached files are skipped, so use a fresh scan when validating changes to scanner behavior.

## Roadmap

- Language-native parsing and clearer per-language capability reporting
- More precise findings with rule identifiers and source locations
- Adversarial fixtures and false-positive/false-negative evaluation
- Cache integrity handling and broader automated tests
- Deeper data-flow and taint analysis

## License

MIT — see [LICENSE](LICENSE).
