# LangFix

**A multithreaded static analysis engine for polyglot software environments.**

LangFix analyzes codebases across 10 programming languages to identify syntax errors, security vulnerabilities, excessive complexity, documentation gaps, and formatting issues.

## Features

- **Multithreaded Analysis** — Analyzes files concurrently using `ThreadPoolExecutor`.
- **Incremental Caching** — Uses MD5 hashes to skip unchanged files.
- **Automated Formatting** — Supports Black, Prettier, and Gofmt.
- **Security Scanning** — Detects potential credential leaks, dangerous execution sinks, and command injection risks.
- **Complexity Analysis** — Measures cyclomatic complexity using Radon.
- **Multiple Output Formats** — Supports terminal reports and JSON output.
- **Streamlit Dashboard** — Provides an interactive interface for exploring analysis results.

## Installation

```
git clone https://github.com/Gitcoder12/Langfix.git
cd Langfix

pip install -r requirements.txt
```

## Usage

### Analyze a project

```
python langfix.py ./src
```

### Analyze and automatically fix formatting

```
python langfix.py ./src --fix
```

### Export results as JSON

```
python langfix.py ./src --json
```

### Configure the number of worker threads

```
python langfix.py ./src --workers 8
```

## Streamlit Dashboard

Launch the interactive dashboard:

```
streamlit run dashboard.py
```

Open the local URL displayed in your terminal, typically:

```
http://localhost:8501
```

The dashboard can provide an interactive view of:

- Overall project quality score
- Syntax and security findings
- Complexity and documentation metrics
- File-level analysis results
- Formatting issues and suggested fixes

*The dashboard requires a `dashboard.py` implementation.*

## Example Output

The following is illustrative output showing how LangFix reports findings across different repositories.

```
Running: python langfix.py ./github-clones --workers 8

Scanning ./github-clones (Threads: 8)...

--- Repository: django/django (Python) ---
File: django/core/management/base.py
Score: 55/100 (POOR)
Issues: BaseCommand too complex (14)
        3/12 missing docstrings

--- Repository: nodejs/node (JavaScript) ---
File: lib/child_process.js
Score: 10/100 (FAIL)
Security Risk: Potential command execution vulnerability

--- Repository: apache/logging-log4j2 (Java) ---
File: JndiLookup.java
Score: 10/100 (FAIL)
Security Risk: Potential dangerous JNDI lookup

--- Repository: php/php-src (PHP) ---
File: Zend/zend_ast.c
Score: 0/100 (FAIL)
Syntax Error: Compiler check failed

Project Average: 40/100 (POOR)
```

## Scoring System

LangFix assigns each analyzed file a score between 0 and 100.

### Critical findings

| Finding                         | Score |
| ------------------------------- | ----- |
| Syntax error                    | 0     |
| Critical security vulnerability | 10    |
| Complexity risk                 | 30    |

### Standard scoring

When no critical issue is found:

- Formatting score: 100 if clean, 50 if formatting is required.
- Documentation score: Percentage of documented functions.
- Final score: Average of formatting and documentation scores.

### Grade Definitions

| Score | Grade   |
| ----- | ------- |
| 100   | AWESOME |
| 70–99 | GOOD    |
| 40–69 | POOR    |
| 0–39  | FAIL    |

## Evaluation Pillars

1. **Syntax** — Checks whether code parses successfully using language-appropriate tools.
2. **Security** — Identifies potential hardcoded secrets, injection vulnerabilities, and unsafe execution patterns.
3. **Complexity** — Flags excessive cyclomatic complexity.
4. **Documentation** — Evaluates docstring and comment coverage.
5. **Formatting** — Checks code style and formatting consistency.

## Roadmap

### v2.0

- **SARIF Integration** — Export findings for GitHub Security integration.
- **Deep AST Parsing** — Replace regex-based JavaScript and TypeScript scanning with Tree-sitter.
- **Plugin Architecture** — Support custom organization-specific analysis rules.
- **Taint Analysis** — Track untrusted input through data flows to potentially dangerous execution sinks.

## License

Distributed under the [MIT License](https://opensource.org/license/mit).

---

## Project handbook

- [Activity log](ACTIVITY_LOG.md) · [Feature upgrade plan](FEATURE_UPGRADE_PLAN.md)
- [Company and team fit](COMPANY_FIT.md) · [README explanation draft](README_ADDENDUM_DRAFT.md)
- [README quality checklist](README_QUALITY_CHECKLIST.md)
- [Contributing](CONTRIBUTING.md) · [Agent instructions](AGENTS.md) · [Agent skills](SKILLS.md)

## Understanding the project

### In plain language

A command-line code quality assistant that scans several programming languages, reports issues and can call formatters to fix files.

### Technical and research view

The user points LangFix at a codebase. It scans supported files, identifies configured issues and may invoke installed formatters. Every attempted fix should say whether the formatter actually succeeded.

For future work, see [FEATURE_UPGRADE_PLAN.md](FEATURE_UPGRADE_PLAN.md), [ACTIVITY_LOG.md](ACTIVITY_LOG.md), [COMPANY_FIT.md](COMPANY_FIT.md) and [CONTRIBUTING.md](CONTRIBUTING.md).
