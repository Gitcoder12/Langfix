# Contributing to Langfix

1. Read README.md and FEATURE_UPGRADE_PLAN.md.
2. Select one bounded analyzer, formatter or report task.
3. Work on a feature branch.
4. Add tests for success, failure, missing tool, timeout and invalid input.
5. Use subprocess APIs safely; do not hide non-zero exit codes.
6. Verify changed files and include exact command output in PRs.
7. Update ACTIVITY_LOG.md with real results.

Do not execute untrusted project scripts or format files outside the selected repository scope. Human maintainers approve merges/releases.
