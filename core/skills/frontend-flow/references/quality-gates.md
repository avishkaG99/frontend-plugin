---
title: Gates and finishing
tags: gates, lint, typecheck, tests, done, reporting
---

## Gates and finishing

The exact commands, and how long the full suite takes, are in the profile. Run them in
order — lint, typecheck, scoped tests while iterating, then the full suite. Later gates are
slower, so an early failure saves the wait.

### Rules

- **The full suite runs before a step is marked done.** Scoped runs are for iterating.
- **A failing gate is the finding.** Fix the cause. Never delete an assertion, loosen a
  matcher, add a skip, or cast to `any` to get past it. If the honest fix is a design
  change, stop and say so.
- **A failure unrelated to this change** is reported as pre-existing, with the evidence,
  and not folded into the step.
- **New behaviour without a test does not pass**, unless the spec records why it cannot be
  tested here.
- Then walk the project's Definition of Done: scope matches the spec, no unrelated
  refactors, all locale files updated, loading and error states real, nothing internal in
  user-visible errors, a keyboard pass on new interactive UI.

### Reporting

Report what happened, with numbers:

> lint clean, typecheck clean, 4931 tests across 756 files pass. Step 2 of 4 done.

Not "all green". If a gate was skipped, still running, or not run, say which and why.
Never imply a pass you did not see.

### Finishing a step

1. Gates pass.
2. Tick the plan row in the spec.
3. Append to the spec's log under today's date: what changed, what the run proved, what is
   still open.
4. Name the next step, and stop.

### Finishing a feature

Every row ticked and gates green: set the spec's status to `Done`, append a closing log
line, and say what is left **outside** the code — a portal or console setting, a backend
change, a check only a person can do in a real browser.
