---
name: frontend-flow
description: Spec-driven feature work in a React app — write or update a feature spec, plan it, implement it one step at a time, verify it against the project's quality gates, and track it to handoff. Use when starting, resuming or finishing frontend work, planning it, writing a frontend spec, implementing a planned step, or running the app's typecheck/lint/test gates.
---

# Frontend flow

Spec-driven delivery for the React app described in the profile below. Eight agents share
this skill: `fe-spec` writes the spec, `fe-plan` plans from it, `fe-test` derives the test
cases, `fe-build` implements one step at a time, `fe-verify` runs the gates and records the
outcome, `fe-audit` reviews security and performance, and `fe-e2e` checks it in a real
browser. `fe-git` lands it.

`/fe:run` conducts them: it reads where a feature stands from the spec's Flow status
block, hands the next move to the agent that owns it, records the outcome, and drafts the
commit, PR and ticket update once the work is finished. Use it to start, resume or finish a
feature; the single-stage commands still work on their own.

## The one rule that makes this work

> The spec file is the unit of work, not the conversation.

Every feature has one file in the project's feature-spec folder. The request, the plan, the
decisions and the log all live there. A new session picks up the file and knows where
things stand. If it is not in the file, it did not happen.

## Standards live in the project, not here

This skill is *method*. The written rules of the codebase — folder layout, component
shape, state, styling, i18n, accessibility, security, Definition of Done — live in the
project's own standards documents, listed in the profile. Read the one that governs what
you are touching. Never restate its rules from memory, and never copy them into a feature
spec: a second copy drifts.

When the project has no written standard for something, the nearest existing code is the
standard. Read its neighbours before writing.

## Where to look

| You need to | Read |
| --- | --- |
| Write or update a feature spec | [references/spec-workflow.md](references/spec-workflow.md) |
| Turn an approved spec into a plan | [references/planning.md](references/planning.md) |
| Write code that matches this codebase | [references/react-conventions.md](references/react-conventions.md) |
| Plan, build and review a screen in the app's design system | [references/ui-design.md](references/ui-design.md) |
| Derive test cases from the spec | [references/test-plan.md](references/test-plan.md) |
| Keep, select and grow the regression library | [references/test-library.md](references/test-library.md) |
| Write tests that pass for the right reason | [references/testing.md](references/testing.md) |
| Check a change for security holes | [references/security.md](references/security.md) |
| Check what a change costs to load and run | [references/performance.md](references/performance.md) |
| Run the gates, decide if it is done | [references/quality-gates.md](references/quality-gates.md) |
| Run a feature end to end, track it, hand it off | [references/conductor.md](references/conductor.md) |

## Verifying in a real browser

jsdom cannot click, navigate or paint, so every case the test plan marks as not automated
is unverified until someone looks. The `web-verify` skill and the `fe-e2e` agent run those
cases against a running app and write the results back into the spec. Load it when a change
needs checking beyond the unit and integration suites.

## Landing the work

Branching, commits and PRs belong to the `git-flow` skill — load it when the work is ready
to land. Branch **before** the first build step, named from the ticket, and commit the
feature spec together with the code it describes.

## Gates

Two stops, and the person decides at each:

1. After the spec — do not plan until it is approved.
2. After the plan — do not write code until it is approved.

The test plan is written from the approved spec, **before** the code: cases derived from
the implementation describe what it does, not what it should do.

Implementation runs without stopping per file, but `fe-build` does one plan step per turn,
so a wrong direction costs one step rather than a feature.

## What never happens without asking

- Committing, pushing, opening a PR.
- Installing a dependency. The stack is already decided; a new package is the person's
  decision, not a convenience.
- Touching a repo this flow does not own (see the profile).
- Rewriting an approved spec section. Append to its log instead.
- Deleting, skipping or loosening a test to make a gate pass.

<!-- profile -->
