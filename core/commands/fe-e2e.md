---
description: Run browser and regression cases locally — a spec's cases, or any slice of the test-case library (all, area, use case, IDs, impacted) — and report per case
argument-hint: "[spec slug | TC-/UC- IDs | --all | --area <area> | --type <type> | --impacted] [--headed] [--url <url>] [--bug <what to re-check>]"
---

Verify in a real browser. Target: $ARGUMENTS

1. Load the `web-verify` skill.
2. Resolve the cases:
   - a spec slug → the cases its test plan marks as not automated, plus its re-run list;
   - `TC-…` / `UC-…` IDs, `--area`, `--all` or `--impacted` → that slice of the test-case
     library, `Active` rows only, selected by the profile's library script (`select` or
     `impacted`) — show its output as the case list;
   - `--bug` → a re-check of that behaviour, ending in a decisive check
     (`references/bug-recheck.md`).
   With no argument, use the spec with the most recent unfinished Flow status block, and
   name it.
   Rows whose `Automated` column names a test file run through the project's test command,
   scoped to those files; only the rest open a browser.
3. Resolve the URL — the `--url` argument, then the environment in the profile, then the
   local dev server — and decide whether this run may mutate data. Stop if no URL resolves.
4. Show the URL, the role, the read-only decision and the case list. Wait for approval
   before opening a browser. With `--headed`, the browser opens visibly and slowed down so
   the person can watch; say so before it opens.
5. Delegate to the `fe-e2e` agent for the Playwright session.
6. Report per case with statuses that mean what they say, and name any failure with its
   screenshot. Every report opens with the environment block. A milestone run (`--all`, a
   whole `--area`, or a feature's final run before its PR) is committed in the library's
   runs folder with a row in its index; other library runs write a local report; step
   checks write only to the spec's log. Paths are in the profile. List any uncovered behaviour seen as proposed `Draft`
   cases. Change nothing in the product, and never write to the library from a run.
