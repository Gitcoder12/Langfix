# Langfix — Feature Upgrade Plan

## Objective

A command-line code quality assistant that scans several programming languages, reports issues and can call formatters to fix files.

## P0 — trustworthy fixes

- [ ] Remove or implement the documented dashboard and ensure every README command exists.
- [ ] Use safe subprocess argument lists with shell disabled; check exit code and report formatter failures accurately.

## P1 — robust analysis

- [ ] Add mocked subprocess tests for success, non-zero exit, missing executable and timeout.
- [ ] Improve language detection, parse errors and report schema with clear unsupported-language behavior.

## P2 — integrations and scale

- [ ] Benchmark large repositories and incremental-cache correctness.
- [ ] Add SARIF output and CI integration after output schema stabilises.

## Contributor work packages

1. Safe subprocess execution and failure tests.
2. Language/file discovery and parser error handling.
3. Incremental cache correctness tests.
4. Machine-readable reports and CI integration.

## Definition of done

- [ ] Formatter commands are invoked safely and return accurate status.
- [ ] Non-zero exit, timeout and missing binary are handled.
- [ ] README commands point to committed files.
- [ ] Tests prove files are changed only when a formatter reports success.
