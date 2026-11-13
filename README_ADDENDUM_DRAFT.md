# Langfix — README Explanation Draft

## In plain language

A command-line code quality assistant that scans several programming languages, reports issues and can call formatters to fix files.

## What it does

The user points LangFix at a codebase. It scans supported files, identifies configured issues and may invoke installed formatters. Every attempted fix should say whether the formatter actually succeeded.

## Technical explanation

Python tool using ThreadPoolExecutor, incremental file caching, formatters including Black/Prettier/gofmt, security-pattern checks and complexity analysis. The audit found that README promises a dashboard file not in the tree and formatter execution uses questionable shell/argument handling without reliably checking exit codes. Do not claim a file was fixed unless the formatter actually succeeded.

Document file discovery, concurrency, cache key, supported languages, formatter invocation, exit-code handling, report formats and safety boundaries.

## Limits

Static rules can produce false positives and false negatives. Formatter success does not prove code correctness. List supported languages and tools exactly as tested.

## Contributing

See FEATURE_UPGRADE_PLAN.md and CONTRIBUTING.md.
