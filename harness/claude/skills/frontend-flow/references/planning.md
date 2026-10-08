---
title: Planning a feature
tags: plan, steps, slice, questions, ambiguity, traceability, gate
---

## Planning a feature

Adapted from AI-DLC's inception stages (`units-generation`, `delivery-planning`), cut down
to what a single frontend app needs. Four ideas are worth keeping; the ceremony around
them is not.

### 1. Resolve ambiguity in writing, before planning

A plan built on a guess fails at review, after the code exists. So the spec carries a
questions block, and the person answers in the file:

```markdown
## Questions

1. Does the picker stay open after a selection? [Answer]:
2. Empty state: hide the section or show a placeholder row? [Answer]:
```

Scan the request for vague words ("handle", "support", "properly"), contradictions, and
missing states — loading, empty, error, permission-denied. Ask about those before
planning, not during implementation. Unanswered questions block the plan; the person can
waive one explicitly and that waiver goes in Decisions.

### 2. The first step is a thin slice that runs

AI-DLC calls this skeleton-on: the first unit is the smallest working integrated path, not
a layer. Here that means step 1 reaches the screen — route renders, hook calls a service,
something visible, even hardcoded. Not "add the types", not "write the service layer".

A layer-first plan hides integration problems until the end, which is exactly when they
cost most.

### 3. Steps are ordered by dependency, and each one is reviewable

| Rule | Why |
| --- | --- |
| One coherent change per step | A person can review it in one sitting |
| At most ~3 files | Bigger steps hide mistakes |
| Name the files up front | Forces you to look before you plan |
| A step ends green | Typecheck, lint and tests pass before the next starts |
| Tests belong to the step | Not a "write tests" step at the end |

Where two steps are genuinely independent, say so — the person may reorder them.

### 4. Traceability: requirement → step → test

Every acceptance criterion in the spec maps to at least one plan step, and every step that
changes behaviour names the test that proves it. A criterion with no step is a gap in the
plan; a step with no criterion is scope you invented, and it needs the person's word
before it goes in.

State the mapping in the plan table:

```markdown
| # | Step | Covers | Files | Test | Done |
|---|---|---|---|---|---|
| 1 | Render the zone list from the API | AC-1, AC-2 | features/…/zone-list.tsx | zone-list.test.tsx | ☐ |
```

### The gate

The plan is written to the spec file and then stops. Nothing is implemented until the
person approves it. If the plan changes after approval — a step splits, a file turns out
to be the wrong one — that is a new draft: say what changed and get a yes for it, rather
than quietly following the new version.

### What AI-DLC does that we deliberately skip

| Theirs | Why not here |
| --- | --- |
| 33 stages across 5 phases | One app, one person; ideation and operations live elsewhere |
| Separate dependency DAG and economic sequencing stages | A frontend feature's order is nearly always dependency order |
| Reviewer agent with iteration caps per artifact | the harness's own review command covers this |
| Per-stage record directories | One spec file per feature is easier to find and to keep current |
