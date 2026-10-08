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
- **A milestone run** — `--all`, a whole `--area`, or a feature's final browser run before
  its PR — gets a report **committed** in the library's runs folder (path in the profile),
  one file per **day and scope**, named `<date>-<scope>.md`, and a row in that folder's
  index, newest first. Another run of the same scope on the same day is **added to that
  file** as a new `## Run N — HH:MM` section with its own environment block — earlier runs
  are never edited — and the file's `Latest:` line and its index row are updated to the
  newest result and the run count. The format is the index's own template.
- **Any other library run** (IDs, `--type`, `--impacted`, re-runs): the same report at the
  local path the profile gives. Step checks write only to the spec's log.
- When the run happened inside a feature's flow, the spec's log gets one line linking to
  the report.
- **Never into the area files.** Their rows describe what must work, not what last
  happened.

### The environment block

Every run report opens with the environment, filled from facts, not from memory, so a
result always says what it was a result *of*:

- **Environment name** — `local`, or the named environment from the profile.
- **App** — URL, repo, branch, commit (`git rev-parse --short HEAD`), and whether the
  working tree had uncommitted changes.
- **API** — URL and, when the backend is a repo here, its branch and commit.
- **Identity** — which sign-in provider and tenant, never an account.
- **Browser** — engine and version, headless or not, viewport.
- **Roles** used, **data** (which test organisation, whether mutations were allowed),
  start time and duration.

In a committed report, list only failed, blocked, skipped and flaky cases; count the
passes. Never a screenshot, an email address, a password or a token — describe what was
seen. A pass against `local` says nothing about any other environment, and the report
must not imply it does.

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
