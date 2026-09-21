---
slug: report-run
phase: verification
lead_agent: fe-e2e
gate: Gate B — nothing is posted outside the spec without approval
consumes:
  - case-result[] (phase 2, required)
  - run-start-time, run-duration (phase 2, required)
  - spec-path (phase 1, required)
produces:
  - spec-log-entry (appended, never rewritten)
  - verdict (to the person)
  - test-plan updates (Automated column)
title: Reporting the run
tags: report, verdict, spec-log, evidence, flaky, bug
---

## Reporting the run

The run is only worth as much as what it writes down. Two audiences: the person reading
the answer now, and whoever opens the spec in three months.

### Into the spec

Append one block to the feature spec's log, under today's date. Update the test plan's
`Automated` column for any case that now runs here.

```markdown
### 2026-09-21 — browser run
Against http://localhost:3000 as `editor`, read-only. 5 cases: 4 passed, 1 failed.

| ID | Status | Attempts | Observed |
|---|---|---|---|
| T-2 | PASSED | 1 | empty message shown, no table rendered |
| T-5 | FAILED | 3 | dragged row snapped back; order unchanged after reload |
| T-6 | SKIPPED | — | mutating case, read-only run |
| T-7 | BLOCKED | — | session expired, landed on the sign-in page |
```

Statuses mean exactly one thing each, and they must not blur:

| Status | Meaning |
| --- | --- |
| `PASSED` | The expected outcome was observed. |
| `FAILED` | It ran, and the product did the wrong thing. This is a bug. |
| `BLOCKED` | It could not run — expired session, missing data, a locator that no longer exists. Says nothing about the product. |
| `SKIPPED` | Deliberately not run, with the reason: read-only run, needs a device, out of scope. |

A `BLOCKED` reported as `FAILED` sends someone hunting a bug that does not exist. A
`FAILED` softened to `BLOCKED` hides a real one.

### To the person

Lead with the verdict, then the exception:

> 5 browser cases against localhost as `editor`: 4 passed, **T-5 failed** — dragging a row
> reorders it visually, but the order is gone after a reload. Screenshot:
> `_webverify/screenshots/T-5.png`. T-6 skipped, read-only run.

Say which URL, which role, and whether mutations were allowed. A pass against the wrong
environment is not a pass.

### Flakiness

A case that needed two or three attempts is flaky and is reported as such even though it
passed. Flakiness is a finding about the product or the case, not a detail to swallow:
either the UI has a race, or the case waits for the wrong thing.

### A failure is not a fix

Report it, attach the evidence, and stop. Changing the product to make a case pass is
`fe-build`'s job after the person has decided what the right behaviour is. A case that
fails because the **spec** is wrong gets the spec corrected — say so rather than quietly
rewriting the case to match what the app happens to do.

### Bug re-checks

When the run exists to re-check a reported bug, decide one thing and say it plainly:

- **Still reproducible** — the trigger and what was observed, with a screenshot.
- **Not reproducible** — what was tried, on what build, with what account.
- **Inconclusive** — what stopped a decisive answer. This is an honest answer; a guessed
  verdict is not.

Name the exact step that decided it, so the next person can repeat it.
