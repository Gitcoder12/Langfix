# Independent Model Audit Router — Langfix

**Revision date:** 2026-11-13

## Data integrity policy
- Never replace real or maintainer-provided data with fabricated, synthetic, generated or placeholder records.
- Inspect Git history and trace source, licence, collection date and known limitations before any data change.
- If provenance is unknown, preserve existing records and mark them unknown/unverified. Do not guess.
- Synthetic data is allowed only in clearly labelled, isolated tests/examples.
- Never invent official records, people, companies, citations, metrics, benchmark results, customers, deployments, endorsements or contributors.
- Claim tests pass only with reproducible results on the exact commit reviewed.

## README policy
Recover the last maintainer-authored README from Git history and preserve it intact. Do not replace or rewrite it. Append any AI-generated explanation only in a dated, clearly labelled secondary section at the very bottom.

## Independent reviewers
1. Data provenance and real-vs-synthetic reviewer.
2. Code, architecture and product correctness reviewer.
3. Security, privacy and dependencies reviewer.
4. Build, tests, CI and reproducibility reviewer.
5. README history, licensing, attribution and links reviewer.
6. Recruiter/researcher claims and public evidence reviewer.

## Audit workflow
1. Record repository URL, default branch, exact HEAD SHA, fork/original status and PR heads.
2. Classify work as merged, open, closed-unmerged, reverted or unverified.
3. Inventory runtime data, fixtures, generated files, APIs and provenance.
4. Compare README with its pre-AI Git-history version.
5. Run install/build/lint/test commands on the exact commit; inspect CI for false-green or suppressed failures.
6. Review security, privacy, accessibility, error handling, edge cases and performance.
7. Verify public claims and links. Company fits are hypotheses, not customer or partnership claims.
8. Publish evidence-based findings before any edits.

## Finding format
Severity (**P0/P1/P2/P3**), exact path/line, reproduction, expected vs actual, evidence and SHA, confirmed/suspected/unverifiable status, minimal fix, regression test, and data/README impact.

## Merge gate
- [ ] No fabricated data presented as real or official.
- [ ] Real/user-provided data preserved without silent substitution.
- [ ] Synthetic examples labelled and isolated.
- [ ] Original README preserved; AI notes at bottom only.
- [ ] Exact-head tests and CI verified; failures disclosed.
- [ ] No secrets, private personal data, classified or confidential information.
- [ ] Licensing and attribution preserved.
- [ ] Independent second review and maintainer approval completed.

Repository: **Langfix**. Do not infer features from name or roadmap. Do not merge, delete, force-push, overwrite datasets or modify the original README while auditing. The repository owner has final approval.
