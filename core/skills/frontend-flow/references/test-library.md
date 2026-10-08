---
title: The test-case library
tags: test-library, regression, use-cases, test-cases, coverage, impacted, suite
---

## The test-case library

A feature spec's `## Test plan` proves one change. The library is what stays behind: every
use case and test case the app must keep passing, grouped by area, so any of them can be
run again against the current code. Its location, its area files and which code each area
owns are in the profile.

The spec plan is where cases are born. The library is where they live once the feature
ships. A case is never maintained in two places: once promoted, the spec's row points at
the library ID.

### One file per area

Each area file has two sections, in this order.

```markdown
# Surveys — use cases and test cases

## Use cases

### UC-SUR-02 — Compare Before and After results
- **Actor:** org-admin
- **Goal:** see how scores changed between the two survey phases
- **Preconditions:** a project with a closed Before survey
- **Main flow:** 1. Open the project's Surveys tab. 2. Choose "Before vs After".
  3. Read the change per category.
- **Alternatives:** After not started → hint with the expected date. Before missing →
  the comparison option is hidden.
- **Spec:** features/projects/survey-before-after-comparison-feature.md (AR-760)

## Test cases

| ID | UC | Title | Type | Role | Steps | Expected | Automated | Status | Added in |
|---|---|---|---|---|---|---|---|---|---|
| TC-SUR-004 | UC-SUR-02 | After missing shows a hint | Negative | org-admin | 1. Open a project with only a Before survey<br>2. Choose "Before vs After" | A hint names when the After survey closes; no chart renders | browser | Active | AR-760 |
| TC-SUR-005 | UC-SUR-02 | Category deltas render | Happy | org-admin | 1. Open a project with both phases closed<br>2. Choose "Before vs After" | Each category shows Before, After and the change | `survey-comparison.test.tsx` | Active | AR-760 |
```

- **IDs** are `UC-<AREA>-NN` and `TC-<AREA>-NNN`, using the area prefixes from the profile.
  They are permanent: never renumbered, never reused, even after a case is retired.
- **Type**: `Smoke` (a page opens and shows its main content, for a role), `Happy`,
  `Negative`, `Edge`, `Permission`, `Regression` (a bug's trigger).
- **Role**: one of the profile's browser roles, or `any`.
- **Steps**: one action per step, `<br>` between them so the table stays one row per case.
  Concrete: the page, the control's visible label, the data it needs.
- **Expected**: what a person can observe. "Works" is not an expected result.
- **Automated**: the test file in backticks, or `browser` for a Playwright case, or
  `manual` with the reason in a note under the table. The test itself carries the case ID
  at the start of its name — `it('TC-SUR-005 renders a change per category', …)` — so
  `vitest run <file> -t TC-SUR-005` runs exactly that case, and the library check can see
  the link.
- **Status**: `Active` runs. `Draft` is proposed and awaiting approval, and never runs.
  `Retired` stays in the table with the ticket that retired it, and never runs.
- **Added in**: the ticket key, or the spec slug when there is none.

No results in the area files. A run's outcome goes to a run report, so those files only
change when what the app must do changes. **Milestone** runs — everything, a whole area, or
a feature's final browser run before its PR — are committed beside the library, with an
index, so anyone can see what was last checked and against which environment. Every other
run stays local. Where both live is in the profile.

### The library script

When the profile names a library script, use it rather than reading the tables by eye:
`check` validates the library (unique permanent IDs, columns, statuses, roles, use cases,
test files that exist and mention their ID), `select` lists the `Active` cases for a scope,
and `impacted` maps the branch's changes to areas through the ownership file and lists
their cases. Its output is what the person sees, so a selection is never a judgement call.

Run `check` after every edit to the library; a library that fails it is not committed.

### Choosing what to run

| Scope | Selects | Typical use |
| --- | --- | --- |
| `--all` | every `Active` case in every area | before a release, after a dependency bump |
| `--area <area>` | every `Active` case in one area file | after a change across an area |
| `TC-SUR-004` (one or more) | those cases | re-running a failure, checking a fix |
| `UC-SUR-02` | every `Active` case under that use case | checking one user journey |
| `--type Smoke` | every `Active` case of one type, across areas | the quick check before a PR or release |
| `--impacted` | `Active` cases in the areas owning the changed files (the diff against the base branch, mapped through the profile), plus any case whose steps name a changed route | the default before handing a change off |
| a spec slug | the spec's own `## Test plan` cases | the feature under construction |

`Automated` cases run through the project's test command, scoped to their files; `browser`
cases run through `web-verify`; `manual` cases are listed as not run, with their reason.
The report says which ran how. Never subset silently: if a selection is cut short, say what
was not run.

### Finding what a change needs: coverage

Run on every feature at the `test-plan` stage, and again before handoff, because the
answer changes as the code does. A green run says nothing about whether the new behaviour
is covered; those are separate questions.

1. **List the user-facing surface the change touches** — from the spec's acceptance
   criteria and, once code exists, the changed files: a new route is a new page, a new
   feature folder a new screen, a changed component an existing behaviour. Ignore files
   that cannot change what a user sees: docs, config, tests, types-only changes.
2. **Search the area's library** for each surface by use case, title and steps.
3. **Sort each surface into exactly one bucket:**
   - **Covered, unchanged** → name the existing case IDs. They go into the re-run list.
   - **Covered, behaviour changes** → propose an **amendment** to that ID, never a
     duplicate row.
   - **Uncovered** → propose new cases, continuing the area's ID sequence, under an
     existing use case or a new one.
   - **Obsolete** → the change removes the behaviour: propose retiring the ID.
4. **Write the result into the spec** under `## Library changes`: the re-run list, then the
   proposed rows with every column filled and `Status: Draft`. Base proposals on the spec
   and the code; when a browser run confirms them, say so.

Propose a case only when the change adds or changes user-facing behaviour that no `Active`
case covers. No proposals for refactors with no behaviour change, for internal code with
no visible surface, or for behaviour an existing case already covers — name that case
instead. A new form deserves both a valid-input and a rejected-input case.

### Promoting cases at handoff

Nothing reaches the library unapproved, and declining costs nothing:

1. At handoff, show the person the `## Library changes` section: rows to add, amend and
   retire.
2. **On a yes**, write them into the area file with `Status: Active` (or `Retired`), and
   replace each promoted spec row's ID with a pointer: `T-4 → TC-SUR-004`.
   Rename each automated test so its name starts with the new ID, then run the library
   check. A failing check is fixed before the commit, not after.
3. **On a no**, leave the rows as `Draft` in the spec and log the decision. A later run
   never blocks or nags because a proposal is outstanding.

The library change is part of the feature's commit, next to the spec and the code.

### Backfilling an area

When an area has no cases yet and is worth covering, derive `Draft` rows from its existing
feature specs' acceptance criteria and test plans, and present them for approval in one
batch. Never mark backfilled rows `Active` without the person's review: a case written from
an old spec may describe behaviour the app no longer has.
