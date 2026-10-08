---
slug: bug-recheck
phase: verification
lead_agent: fe-e2e
gate: Gate A — the plan, the decisive check and the mutating steps, before a browser opens
consumes:
  - bug description, repro steps, expected and actual result (ticket or the person, required)
  - target-url, storage-state, mutations-allowed (phase 1, required)
produces:
  - a one-case plan ending in a decisive check
  - verdict — STILL REPRODUCIBLE, NOT REPRODUCIBLE, or INCONCLUSIVE
  - a regression case proposal for the library, when the bug is real
title: Re-checking a reported bug
tags: bug, verify, repro, decisive-check, verdict, regression
---

## Re-checking a reported bug

A bug re-check answers one question — is it still there? — and the answer has to be
trustworthy in both directions.

### 1. Can a browser see it at all?

Before anything opens, decide whether the failure is visible in the UI. A backend-only
crash, a wrong API body with no screen, a build failure: none of these can be verified
here. Say so, with the reason, and stop. No browser, no verdict.

### 2. Build the plan

From the ticket (through the project's tracker integration) or from the person:

- **Steps**: the repro steps, one action each, with the real page and control labels.
- **Decisive check**, two signals:
  - **Bug signal** — what the reporter saw: the actual result.
  - **Fixed signal** — the expected result. It must be **positively observed** to call the
    bug fixed. The bug signal being absent is never enough.
- **Preconditions**: the data, role and flags the path needs, each marked `exists`,
  `must-create` or `unknown`.
- **Mutating steps**, flagged, so a read-only run skips them visibly.

If the expected result is not stated anywhere, ask for it in one question. Without it there
is no decisive check, and the honest verdict is `INCONCLUSIVE`.

Show the plan, the decisive check, the preconditions and the mutating steps at Gate A.

### 3. Run it

The decisive check is the script's last step. It asserts the fixed signal; when that fails
it looks for the bug signal; and it **always** takes a screenshot, whichever way it goes.

### 4. The verdict

| Verdict | When |
| --- | --- |
| **STILL REPRODUCIBLE** | the decisive check saw the bug signal |
| **NOT REPRODUCIBLE — appears fixed** | every step ran and the fixed signal was positively observed |
| **INCONCLUSIVE** | anything else: a blocked step, an expired session, a missing precondition, neither signal seen |

A blocked run is never reported as fixed. "Appears fixed" is the strongest wording: one
clean run on one build with one account is evidence, not proof.

### 5. After the verdict

- Still reproducible: the evidence goes to the person. Changing ticket state, or posting to
  the ticket, needs their yes for that specific draft.
- Real bug, either verdict: propose a `Regression` case for the library with the trigger
  exactly as found, so it can never come back unnoticed.
