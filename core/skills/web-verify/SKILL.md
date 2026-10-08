---
name: web-verify
description: Runs browser test cases against a running local app with Python Playwright — a feature spec's cases, or any slice of the project's test-case library (all, one area, one use case, named cases, or those impacted by the current change) — with storage-state auth, screenshots and a per-case report. Use to verify a change in a real browser, run regression cases, run the manual cases from a test plan, or re-check a reported bug.
---

# Web verify

Browser verification for work that `frontend-flow` has already specified. jsdom cannot
click, navigate, or paint; this closes that gap for the cases the test plan marks as not
automatable.

Shaped after the `web-app-tester` plugin, with one deliberate difference: that plugin is
**PR-driven** and generates a plan from the pull request. This one is **spec-driven and local** —
the cases already exist, in the feature spec or in the project's test-case library, so they
are read from there, and the results go back into the spec or a local run report.

## Three phases

Each phase states what it consumes and what it produces, in the AI-DLC stage style, so a
phase cannot start on inputs nobody produced and nothing it produces goes unrecorded.

| # | Phase | Consumes | Produces | Gate | Reference |
| --- | --- | --- | --- | --- | --- |
| 1 | Resolve | spec, arguments, profile | target-url, case-list, mutations-allowed, storage-state | **Gate A** — approval before a browser opens | this file |
| 2 | Run | phase 1's outputs | case-result[], run timings | — | [session.md](references/session.md) |
| 3 | Report | case-result[], spec path | spec-log-entry, verdict, test-plan updates | **Gate B** — approval before anything is posted outside the spec | [report.md](references/report.md) |

Signing in runs inside phase 1: [auth.md](references/auth.md).

A phase that cannot produce its outputs stops the run and says which input was missing. It
does not carry on with a guess — that is how a run ends up reporting failures that are
really a missing URL or an expired session.

## Phase 1 — resolve the run

1. **The cases.** From one of two sources, keeping their IDs: `T-5` or `TC-SUR-004` in
   the report means the same row in the file.
   - **A feature spec**: its `## Test plan` cases marked not automated, plus any the person
     names. A **step check** — run by the conductor right after a build step — takes only
     the cases covering that step's acceptance criteria; the full run at the end takes them
     all, plus the spec's re-run list from `## Library changes`.
   - **The library**: the scope the person gave — `--all`, `--area`, case or use-case IDs,
     or `--impacted` — selected per the frontend-flow skill's `references/test-library.md`.
     `Active` rows only. Rows whose `Automated` names a test file go to the project's test
     command, not the browser; say so in the report.
   - **A bug re-check** (`--bug`): see [bug-recheck.md](references/bug-recheck.md). It
     builds its own one-case plan with a decisive check.
2. **The URL.** In order: an argument the person gave, then the environment named in the
   profile, then the local dev server. Never guess a hostname. If nothing resolves, say so
   and stop — do not test a URL you invented.
3. **Mutations.** Decide before opening a browser whether this run may change data. Against
   anything shared — staging, production, a real tenant — the answer is no, and cases that
   create, edit or delete are skipped and reported as skipped, not failed. Local dev
   against a disposable database may mutate.
4. **Auth.** Resolve the storage state per [auth.md](references/auth.md). A run that cannot
   authenticate stops here rather than reporting every case as failed.

**Gate A.** Show the person the URL, the case list, which cases mutate data, and the
account being used. Wait for a yes before opening a browser. Skip this gate only when the
person has asked for an unattended run.

## Looking at the screenshots

A case that passes can still look wrong. For every case on a visible screen, take a
screenshot of the state the case ends in, open it, and review it against the spec's UI
plan and the project's design system, following the frontend-flow skill's
`references/ui-design.md` §5–§6: alignment with neighbouring screens, one clear primary
action, tokens rather than one-off colours, real empty/error states, copy that says what
happens, nothing clipped or overflowing at the narrowest supported width.

Report what you see as **design notes**, separate from the case statuses: a case's status
says whether the behaviour happened; a design note says how it looks. A note never turns a
`PASSED` into a `FAILED` unless the case's own *then* is about the visual.

Describe only screenshots you actually opened. If the run could not capture one, say so.

## Python Playwright, not the repo's toolchain

Browser automation runs through **Python `playwright`**, driven by a script this skill
writes. Never `npx playwright`, never a Node runner, never a new dependency in the app's
`package.json`. The app under test stays untouched: this is a harness, not a feature of the
product.

Chromium is installed once and cached — check the cache before installing, because the
first run costs a minute and later runs cost nothing.

Where the interpreter lives is a per-project fact: see the profile. Use that one, not a
bare `python3`, or the import will fail on a machine whose system Python has no playwright.

## Rules that hold for every run

- **Never print a storage state, cookie, token or password.** Paths are fine, contents are
  not, in logs, in scripts, in the spec, and in anything posted anywhere.
- **Never invent a result.** A case that did not run is `BLOCKED`, not `PASSED`. A
  screenshot you did not take is not described.
- **Never change the app to make a case pass.** This skill reads the product; fixing is
  `fe-build`'s job, after the person decides.
- **Clean up.** The run directory goes when the run ends, screenshots kept only as long as
  the report needs them.
- **One case, one behaviour.** A case that needs three assertions to describe it is really
  three cases: fix the spec.

<!-- profile -->
