---
title: The feature spec
tags: spec, plan, log, status, template, update
---

## The feature spec

One file per feature, in the project's feature-spec folder (see the profile), built from
the project's spec template. The slug is kebab-case and carries the ticket key when there
is one: `ar-730-reauth-on-401-spec.md`.

Create it on first contact with the work, not at the end.

### Sections

The project's template supplies the top: purpose, owner, status, related links, problem
statement, goals and non-goals, users and context. Keep whatever it defines. This flow adds
its sections at the bottom, in this order: Flow status, Plan, Test plan (see
[test-plan.md](test-plan.md)), Library changes (see [test-library.md](test-library.md)),
Decisions, Log.

```markdown
## Flow status

| Field | Value |
|---|---|
| Ticket | AR-730 |
| Repo / branch | areasim-webapp · fix/ar-730-reauth-on-401 |
| Stage | build |
| Next | Step 2 — call it from the 401 handler |
| Waiting on | — |
| Updated | 2026-09-21 |

- [x] ticket — AR-730 (existing)
- [x] spec — approved 2026-09-20
- [x] plan — approved 2026-09-20
- [x] test-plan — 6 cases, 5 automated
- [x] branch
- [ ] build — 1 of 3 steps
- [ ] verify
- [ ] audit
- [ ] e2e
- [ ] handoff

## Plan

| # | Step | Files | Done |
|---|---|---|---|
| 1 | Add the reauth helper | src/lib/auth/msal.ts | ☐ |
| 2 | Call it from the 401 handler | src/lib/api/http-client.ts | ☐ |
| 3 | Tests for the loop guard | src/lib/auth/msal.test.ts | ☐ |

## Decisions

- Re-sign-in instead of logout on an unrecoverable 401, so Entra never shows its
  sign-out account picker.

## Log
### 2026-09-21
- Step 1 implemented. typecheck, lint, 393 tests pass.
- Open: the Entra `login_hint` claim is a portal change, not code.
```

### Flow status

The conductor's state: which stage the feature is in, the next concrete move, and what is
waiting on the person. It is the one section overwritten in place rather than appended to,
and the format and stage list are in [conductor.md](conductor.md). Any agent that finishes
a stage updates it when the spec has one; `/fe:run` adds it to a spec that does not.

### Status line

`Draft` → `Approved` → `In progress` → `Done`. `fe-spec` sets Draft, the person approves,
`fe-build` moves it to In progress on the first step, `fe-verify` sets Done when every
plan row is ticked and the gates pass.

### Rules

- **Append to the log, never rewrite it.** A wrong turn that was corrected is worth more
  to the next reader than a tidy file. Flow status is the one exception: it is state, not
  history.
- **Absolute dates.** "Yesterday" is useless in six weeks.
- **A decision needs its reason.** The reason is the part that survives; the decision
  alone reads as arbitrary a month later.
- **One file per feature, edited.** Coming back to a feature means updating this file, not
  starting a second one. When scope genuinely splits, write the new file and link both.
- **Plan rows are small.** A row is one coherent change a person can review: a helper and
  its caller, or a component and its test. If a row touches more than about three files,
  split it.
- **No standards in here.** Link to the project's standards document instead. Restating a
  rule creates a second copy that drifts.
- **Record what the tests proved**, not that tests were run. "393 pass" is a fact;
  "tests green" is a claim.

### Reading a ticket

Every spec starts from a ticket, settled before the spec is written (see
[conductor.md](conductor.md), "The ticket comes first"). Read it first — description,
acceptance criteria, comments — through the project's tracker integration (the `jira`
skill, where it exists). Put the key in the spec's file name and Related line. A chore
worked without a ticket says so in the Related line (`no ticket — chore: <reason>`).

Nothing is written to the tracker without the person seeing the draft and saying yes —
that includes creating the ticket.

### When the spec and the code disagree

The code wins, and the spec is wrong until someone fixes it. Say so plainly, append the
difference to the log, and ask whether the spec should change or the code should.
