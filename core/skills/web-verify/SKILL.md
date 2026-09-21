---
name: web-verify
description: Runs a feature spec's browser cases against a running app with Python Playwright — headless Chromium, storage-state auth, one case at a time with screenshots — and writes the results back into the spec. Use to verify a change in a real browser, to run the manual cases from a test plan, or to re-check a reported bug.
---

# Web verify

Browser verification for work that `frontend-flow` has already specified. jsdom cannot
click, navigate, or paint; this closes that gap for the cases the test plan marks as not
automatable.

Shaped after the `web-app-tester` plugin, with one deliberate difference: that plugin is
**PR-driven** and generates a plan from the pull request. This one is **spec-driven** — the
plan already exists in the feature spec, so the cases are read from there and the results
go back to the same file.

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

1. **The spec.** Read its `## Test plan`. The cases to run are the ones marked not
   automated, plus any the person names. Keep their IDs: `T-5` in the report means `T-5`
   in the spec.
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
