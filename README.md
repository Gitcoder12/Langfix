# LangFix

**A conservative, multi-language source inspection and repair toolkit.**

LangFix detects source languages, checks syntax where a validator is available, reports lightweight code-quality and heuristic findings, and proposes narrowly scoped cleanup. Its defining rule is simple: **when it cannot establish that a transformation is safe, it leaves the source alone.**

> **Project stage:** early-stage CLI and Python library. LangFix is not a compiler, complete SAST platform, or security audit. Detection and heuristic findings can be wrong or incomplete. Review reports and diffs before relying on them.

## Why LangFix is designed this way

The features are deliberate engineering choices, not a checklist of impressive-sounding capabilities.

| Feature | Why we chose it | Trade-off / boundary |
|---|---|---|
| Extensible language registry | Keeps extensions, validators, formatters and language-specific rules in one place. Adding a language should not require rewriting the core pipeline. | A registry entry means the language is recognised; it does **not** mean every analysis or repair capability is implemented for it. |
| Extension-first, signature-assisted detection | File extensions are usually the strongest low-cost signal. Signatures help with snippets and extensionless input. | Ambiguous snippets are left undetected instead of forcing a potentially wrong language guess. |
| Real syntax validators where available | A parser/compiler check is a stronger safety gate than trying to infer correctness from regular expressions. | Several validators are optional external tools. Missing tools produce a skipped/unverified result, not a pass. |
| Conservative cleanup | Trailing-space removal and a final newline are small, reviewable changes that solve common formatting noise. | Cleanup runs only after validation passes. It is intentionally not a general-purpose code-repair engine. |
| Opt-in formatter integration | Black and Prettier can provide consistent formatting without LangFix implementing language formatters itself. | External formatting is opt-in and limited to supported stdin/stdout integrations. Other configured tools are not blindly invoked. |
| Unified diffs and preview-first library API | Developers need to understand exactly what will change before a tool edits source files. | fix_file() does not write unless apply=True. The CLI --fix flag explicitly writes supported changes in place. |
| Heuristic findings | Lightweight patterns can surface suspicious constructs without requiring a heavyweight analysis platform. | Regex rules are hints only: they can miss context, produce false positives, and do not perform taint or data-flow analysis. |
| JSON and SARIF reports | Machine-readable output makes it easier to connect scans to scripts and code-review workflows. | Report formats do not make the underlying heuristic analysis more accurate. |
| Deterministic messy-code demo | A runnable example makes the actual repair boundary visible: valid messy code is cleaned; invalid or unverifiable code is preserved. | The demo is a small regression fixture, not a representative benchmark of real-world repositories. |

## What currently works

| Area | Implemented behavior |
|---|---|
| Language registry | 18 registered languages |
| Detection | Filename extension and confidence-scored source signatures |
| Built-in syntax validation | Python AST and JSON parser |
| Optional syntax validation | YAML through PyYAML; external validators for JavaScript, TypeScript, Java, C/C++, Go, Rust, Ruby, PHP, shell, Kotlin and Swift |
| Source findings | Trailing whitespace, missing final newline and configured language heuristics |
| Python analysis | Radon cyclomatic-complexity checks and function/class docstring checks |
| Safe cleanup | Trailing horizontal whitespace removal and final newline, only when syntax validation passes |
| Formatting | Black and Prettier when installed and explicitly enabled |
| Output | Terminal, JSON and SARIF |
| Repair review | Before/after validation status and unified diff |

A language being registered is not a promise of full support. HTML, CSS and SQL currently have no syntax validator configured. Tree-sitter language metadata is present, but a Tree-sitter parser integration is **not** implemented.

## Quick demo

The demo builds deterministic messy examples, shuffles them with a fixed seed, and runs the real repair function. It includes valid Python and JSON with whitespace noise plus invalid Python and JSON.

~~~bash
python demo.py
~~~

Expected behavior:

- Valid, validator-backed examples: safe whitespace cleanup and a diff.
- Invalid examples: no rewrite; original source remains unchanged.
- The demo exits with an error if any expectation fails.

Run the regression suite:

~~~bash
python -m unittest -v test_langfix.py test_demo.py
~~~

## Installation

Requirements: Python 3.11+.

~~~bash
git clone https://github.com/Gitcoder12/Langfix.git
cd Langfix
python -m pip install -r requirements.txt
~~~

Optional language validators and formatters must be installed separately if you want those integrations. YAML validation requires PyYAML.

## Usage

Scan a directory:

~~~bash
python langfix.py ./src
~~~

Apply supported repairs in place:

~~~bash
python langfix.py ./src --fix
~~~

**Caution:** --fix is a write operation. Run it on a clean working tree or a disposable copy first. The CLI currently has no separate dry-run flag; use the library preview API below when you want to inspect a proposed diff without writing.

JSON report:

~~~bash
python langfix.py ./src --json
~~~

SARIF report:

~~~bash
python langfix.py ./src --sarif
~~~

## Python library API

The library defaults to preview-only behavior:

~~~python
from fixer import fix_file

# Preview: source file is not modified.
proposal = fix_file("example.py")
print(proposal["validation_before"])
print(proposal["validation_after"])
print(proposal["diff"])
assert proposal["written"] is False

# Apply only after reviewing the proposal.
applied = fix_file("example.py", apply=True)
~~~

For in-memory source:

~~~python
from fixer import fix_code, scan_code, validate_code

validation = validate_code("value = 1\\n", "python")
findings = scan_code("value = 1   ", "python")
proposal = fix_code("value = 1   ", "python")

print(validation)
print(findings)
print(proposal["diff"])
~~~

## Safety model

1. **Validate first.** A transformation is considered only when an available syntax validator explicitly returns valid=True.
2. **Preserve uncertainty.** Invalid, unsupported or unverified source is not rewritten by the conservative cleanup path.
3. **Protect language semantics.** Shell cleanup is disabled because trailing whitespace after a backslash can change line-continuation behavior.
4. **Reject regressions.** If a formatted candidate fails validation, LangFix restores the original source.
5. **Keep external execution bounded.** Validators and supported formatters are invoked with argument arrays rather than shell command strings and use timeouts.
6. **Require explicit writes.** The library writes only with apply=True; CLI --fix is an explicit in-place write request.

These safeguards reduce avoidable damage; they do not prove that a program behaves correctly.

## Scoring and interpretation

The existing CLI score is a heuristic prioritisation signal, not a calibrated measure of correctness, maintainability, performance or security. Security patterns are regular expressions rather than taint analysis. Complexity and docstring checks currently apply only to Python. Validator availability and depth vary by language.

Treat a finding as a prompt for review—not a verdict.

## Known limitations

- No Tree-sitter parser integration yet.
- No LLM-based repair layer.
- No semantic or behavior-preserving proof for proposed changes.
- No complete security analysis, taint tracking or control/data-flow engine.
- HTML, CSS and SQL have no syntax validator configured.
- External tool availability determines how much validation is possible.
- The demo covers a deliberately small set of deterministic examples; broader language fixtures and real-repository benchmarks are still needed.
- The CLI cache/report behavior needs further hardening before cached scans should be treated as complete audit reports.

## Development

Run tests and compile the Python modules:

~~~bash
python -m unittest -v test_langfix.py test_demo.py
python -m compileall -q .
python demo.py
~~~

## License

MIT — see [LICENSE](LICENSE).
