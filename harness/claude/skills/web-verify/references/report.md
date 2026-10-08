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

### Where it goes

- **A feature run** (spec cases, step checks): into the spec's log, as below.
- **A library run** (`--all`, `--area`, IDs, `--impacted`): a run report at the local path
  the profile gives, named `<date>-<scope>.md` (`2026-10-08-area-surveys.md`), with the
  same table plus the URL, role, read-only decision, git branch and commit. When the run
  happened inside a feature's flow, the spec's log gets one line linking to it.
- **Never into the library.** Its rows describe what must work, not what last happened.

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

After the table, the design notes from the screenshot review, each tied to a case and a
screenshot, or `Design notes: none` when there were none:

```markdown
Design notes:
- T-2 (`T-2.png`): empty state uses a custom grey card instead of the design system's
  empty-state recipe; copy says "Nothing here" with no action.
```

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

### Gaps seen during the run

A run that passes still answers a second question: did it walk past behaviour no case
covers? While running, note any screen, control or state the cases reached but did not
check. After the table, list them as proposed cases, per the frontend-flow skill's
`references/test-library.md` coverage rules — every column filled, `Status: Draft`, the
next unused ID. For a feature run they go into the spec's `## Library changes`; for a
library run, into the run report. Propose only what you actually observed; never write to
the library from here.

### Bug re-checks

The verdict and its rules are in [bug-recheck.md](bug-recheck.md). Lead with the verdict,
name the decisive step and its screenshot, and say what was tried, on what build, with what
account, so the next person can repeat it.
