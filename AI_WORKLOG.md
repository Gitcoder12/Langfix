# AI Worklog

## Assessment
- Date: 2026-11-15
- Branch: `docs/portfolio-operating-kit-2026-11-13`
- Recommendation: Improve
- Maturity: Small Python CLI prototype for heuristic code scanning and formatting.

## Purpose and implemented scope
Langfix scans selected source-file extensions, runs limited syntax checks, applies heuristic security and complexity checks, computes a score, and optionally invokes formatters.

Verified implementation:
- `langfix.py` provides file traversal, caching, analysis, SARIF output, and CLI options.
- `pyproject.toml` declares a Python package and console entry point.
- `requirements.txt` and one unittest module are present.
- `.github/workflows/ci.yml` installs Python dependencies, runs two unit tests, and scans the repository.

## Findings
### P1 — Unsupported compiler paths can be reported as syntax-valid
The extension allow-list includes `.rs`, `.c`, `.cpp`, and `.java`, but `check_syntax` only invokes parsers/compilers for Python, JavaScript/TypeScript, PHP, Ruby, and Go. For the other accepted extensions it falls through to `"OK"`. These files can therefore receive a high score without syntax validation. Return an explicit NOT CHECKED state or implement real compiler integrations.

### P1 — Auto-fix success is reported without checking formatter exit status
The Black, Prettier, and gofmt subprocess calls do not inspect their return codes. The Prettier call uses `shell=True` with an argument list, which is not the intended portable invocation on POSIX. A failed formatter can still be reported as fixed. Use argument lists with `shell=False`, capture and validate exit status, and report the actual outcome.

### P1 — Security analysis is regex-based and can create false confidence
The current secret, SQL, eval/exec, and child-process checks are regular expressions. They are useful heuristics but are not comprehensive static analysis, data-flow analysis, or taint analysis. Do not label a file "secure" or "perfect" based on absence of regex matches.

### P2 — TypeScript syntax checking depends on Node behaviour
The code routes `.ts` through `node --check`; this is not equivalent to a TypeScript compiler/type check. Use `tsc --noEmit` or a parser appropriate to the project and report missing toolchains as NOT CHECKED.

### P2 — Regression coverage is too small
The inspected test module has two tests. Add tests for each supported extension, compiler unavailable states, cache invalidation, formatter failures, SARIF schema, path handling, and security heuristic false positives/negatives.

## Checks and evidence
- Inspected README, root tree, `langfix.py`, `test_langfix.py`, `pyproject.toml`, `requirements.txt`, and CI workflow.
- CI workflow runs `python -m unittest test_langfix.py` and `python langfix.py .` on Python 3.10.
- Local tests and self-scan: NOT RUN.
- Default-branch combined status query returned no status entries; no CI pass/fail claim is made.
- Independent model review: NOT PERFORMED.

## Next actions
1. Separate CHECKED, NOT CHECKED, SKIPPED, and FAILED states in scoring.
2. Fix formatter invocation and verify return codes.
3. Replace broad "perfect" claims with explicit heuristic coverage.
4. Add compiler-backed checks for every advertised language or narrow the supported list.
5. Expand tests and run CI across supported Python versions.

## PR head verification
- PR #3 head CI: LangFix CI failed in the unit-test step. Both existing tests raise ValueError because test_langfix.py unpacks analyze_file(...) into three values while the implementation returns a dictionary. The self-scan step was skipped after the failure. This is a verified P1 test/API-contract mismatch.

## Follow-up remediation evidence
- A separate draft PR [#4](https://github.com/Gitcoder12/Langfix/pull/4) updates the two tests to match the dictionary result contract returned by `analyze_file`.
- PR #4 head CI run 43734138407 completed successfully: dependency installation, unit tests, and the repository self-scan all passed.
- This fixes the verified test/API-contract mismatch only. The unsupported-compiler scoring and formatter-result issues listed above remain open.
