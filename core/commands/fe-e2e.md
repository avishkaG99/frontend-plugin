---
description: Verify the change in a real browser — run the spec's browser cases, report per case
argument-hint: "[spec slug | TC-/UC- IDs | --all | --area <area> | --impacted] [--url <url>] [--bug <what to re-check>]"
---

Verify in a real browser. Target: $ARGUMENTS

1. Load the `web-verify` skill.
2. Resolve the cases:
   - a spec slug → the cases its test plan marks as not automated, plus its re-run list;
   - `TC-…` / `UC-…` IDs, `--area`, `--all` or `--impacted` → that slice of the test-case
     library (path in the profile), `Active` rows only, selected per the frontend-flow
     skill's `references/test-library.md`;
   - `--bug` → a re-check of that behaviour, ending in a decisive check
     (`references/bug-recheck.md`).
   With no argument, use the spec with the most recent unfinished Flow status block, and
   name it.
   Rows whose `Automated` column names a test file run through the project's test command,
   scoped to those files; only the rest open a browser.
3. Resolve the URL — the `--url` argument, then the environment in the profile, then the
   local dev server — and decide whether this run may mutate data. Stop if no URL resolves.
4. Show the URL, the role, the read-only decision and the case list. Wait for approval
   before opening a browser.
5. Delegate to the `fe-e2e` agent for the Playwright session.
6. Report per case with statuses that mean what they say, and name any failure with its
   screenshot. A feature run appends to the spec's log; a library run writes a local run
   report (path in the profile). List any uncovered behaviour seen as proposed `Draft`
   cases. Change nothing in the product, and never write to the library from a run.
