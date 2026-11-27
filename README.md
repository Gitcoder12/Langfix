# LangFix

LangFix is an early-stage, multi-language source inspection CLI with conservative repair proposals. It combines extension/signature-based language detection, available syntax validators, heuristic findings, Python complexity/documentation checks, and terminal/JSON/SARIF reports.

> **Scope:** LangFix is not a compiler, complete SAST platform, or security audit. Heuristic checks can produce false positives and miss real issues. Review findings and proposed diffs before acting.

## Quick demo

Run the deterministic messy-code demo. It generates valid-but-messy Python/JSON samples and invalid Python/JSON samples, then prints validation results and unified diffs. It is preview-only and never writes source files.

~~~bash
python demo.py
~~~

Run the demo tests:

~~~bash
python -m unittest -v test_langfix.py test_demo.py
~~~

## Current capabilities

| Area | Current behavior |
|---|---|
| Language registry | 18 registered languages; capability varies by language |
| Detection | Filename extensions first, then confidence-scored source signatures |
| Built-in validation | Python AST, JSON parser, optional PyYAML parser |
| External validation | Optional local tools for JavaScript, TypeScript, Java, C/C++, Go, Rust, Ruby, PHP, Bash, Kotlin, and Swift |
| Findings | Trailing whitespace, final newline, and configured heuristic patterns |
| Python analysis | Radon complexity and function/class docstring checks |
| Formatting | Black and Prettier when installed and source validation passes |
| Reports | Terminal, JSON, and SARIF |

A registered language is not a promise of a built-in parser. External validation is reported as skipped when its tool is unavailable. HTML, CSS, and SQL currently have no syntax validator configured. Tree-sitter metadata is not an implemented parser integration.

## Requirements

- Python 3.11+
- Install dependencies from requirements.txt
- Optional language toolchains and formatters for the languages you want validated or formatted

## Install

~~~bash
git clone https://github.com/Gitcoder12/Langfix.git
cd Langfix
python -m pip install -r requirements.txt
~~~

## Usage

Scan a project:

~~~bash
python langfix.py ./src
~~~

Apply supported repairs before analysis (the --fix flag explicitly opts into writes):

~~~bash
python langfix.py ./src --fix
~~~

JSON output:

~~~bash
python langfix.py ./src --json
~~~

Generate a SARIF report:

~~~bash
python langfix.py ./src --sarif
~~~

## Library API

The library defaults to preview-only behavior:

~~~python
from fixer import fix_file

preview = fix_file("example.py")
print(preview["diff"])

# Apply only after reviewing the proposal:
applied = fix_file("example.py", apply=True)
~~~

## Safety model

- A source file is transformed only when an available syntax validator explicitly passes.
- Invalid or unverifiable source is preserved unchanged.
- Shell source is excluded from whitespace cleanup because trailing spaces after a backslash can affect line continuation.
- External processes use argument arrays, never a shell, and have a timeout.
- Library file writes require apply=True; the CLI --fix flag explicitly opts into applying changes.
- Formatter support is limited to known stdin/stdout integrations; tools requiring guessed file/project arguments are not invoked.

## Scoring and limitations

Per-file scores are heuristic prioritization signals, not calibrated measurements of code quality or security. Security checks use regex patterns rather than taint analysis. Complexity and docstring analysis currently apply only to Python. Syntax validation and formatter support differ by language and installed tools.

The scanner caches file hashes in .langfix_cache.json. Use a fresh scan when validating scanner changes. It excludes .git, venv, __pycache__, node_modules, and .github.

## Development

~~~bash
python -m compileall -q .
~~~

## License

MIT — see LICENSE.

---

## Comparison with Existing Open-Source Projects

LangFix is documented as a multi-language source-inspection CLI with conservative repair proposals, available syntax validators, heuristic findings and terminal/JSON/SARIF reports. These projects provide adjacent linting, static-analysis and formatting capabilities.

| Project | Established focus | Relationship to LangFix |
|---|---|---|
| [Semgrep](https://github.com/semgrep/semgrep) | Static analysis with configurable rules across many languages | A much deeper rule-based code-analysis engine; LangFix currently uses a smaller set of heuristic checks and optional external validators, not Semgrep-equivalent semantic analysis. |
| [Ruff](https://github.com/astral-sh/ruff) | Fast Python linter and formatter | A focused, mature Python tool with extensive rule coverage; LangFix aims for a cross-language single entry point, but its Python analysis is narrower. |
| [Prettier](https://github.com/prettier/prettier) | Opinionated formatter for many languages and file types | A dedicated formatting engine; LangFix invokes supported formatters conservatively after validation rather than replacing their formatting logic. |

### Where LangFix is different
- **Cross-language entry point:** one CLI can detect files and report which validators are available across a range of languages.
- **Conservative repair workflow:** fixes are preview-only by default and require explicit opt-in to write changes.
- **Multiple report formats:** terminal output, JSON and SARIF support different developer and CI workflows.

### Where established projects are stronger
Semgrep has substantially deeper static-analysis capabilities; Ruff has much broader Python rule coverage; Prettier is a mature formatter. LangFix should not claim to be a full SAST platform, compiler or replacement for language-specific toolchains. Its advantage is a unified, cautious orchestration layer.

### Evidence and limitations
Make validator availability explicit per language, retain exact tool versions and exit codes, and test both safe and invalid source samples. Heuristic scores are prioritization signals, not calibrated code-quality or security measurements. Preserve the default preview-only behavior and never apply a repair when validation is unavailable or fails. This is a scope comparison, not a defect-detection benchmark.

---

## Repository navigation

[Alphabetical file index](FILE_INDEX.md)
