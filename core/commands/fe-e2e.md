---
description: Verify the change in a real browser — run the spec's browser cases, report per case
argument-hint: "[spec slug] [--url <url>] [--bug <what to re-check>]"
---

Verify in a real browser. Target: $ARGUMENTS

1. Load the `web-verify` skill.
2. Resolve the spec and the cases its test plan marks as not automated, plus any the person
   named. With `--bug`, the run re-checks that behaviour instead and ends with a decisive
   check.
3. Resolve the URL — the `--url` argument, then the environment in the profile, then the
   local dev server — and decide whether this run may mutate data. Stop if no URL resolves.
4. Show the URL, the role, the read-only decision and the case list. Wait for approval
   before opening a browser.
5. Delegate to the `fe-e2e` agent for the Playwright session.
6. Report per case with statuses that mean what they say, append the results to the spec's
   log, and name any failure with its screenshot. Change nothing in the product.
