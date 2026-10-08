---
title: Test plans and test cases
tags: test-plan, cases, matrix, given-when-then, coverage, traceability
---

## Test plans and test cases

A test plan is written **from the spec, before the code**, so it describes what the feature
must do rather than what the implementation happens to do. Writing cases afterwards
produces tests shaped like the code, which pass whatever the code does.

The plan lives in the feature spec, under `## Test plan`, between Plan and Decisions.
Straight after it, `## Library changes` records how the feature meets the project's
test-case library: the existing cases to re-run, and the ones to add, amend or retire. See
[test-library.md](test-library.md) — the spec plan is where a case is born, the library is
where it lives once the feature ships.

### The case table

```markdown
## Test plan

| ID | Case | Covers | Level | Given → When → Then | Automated |
|---|---|---|---|---|---|
| T-1 | Zone list renders from the API | AC-1 | integration | zones exist → page opens → each zone name shows | ✅ zone-list.test.tsx |
| T-2 | Empty state | AC-1 | integration | no zones → page opens → empty message, no table | ✅ zone-list.test.tsx |
| T-3 | Request fails | AC-4 | integration | API 500 → page opens → error state, retry offered | ✅ zone-list.test.tsx |
| T-4 | Only editors see Add | AC-5 | unit | viewer role → menu renders → no Add button | ✅ permissions.test.ts |
| T-5 | Drag to reorder on touch | AC-6 | manual | list of 3 → drag on a tablet → order persists | ❌ needs real pointer events |
```

IDs are stable: `T-3` still means the same case after the table is reordered, which is what
makes a failure report and a review comment mean anything.

### Deriving cases, not inventing them

Walk the spec's acceptance criteria and for each one ask:

1. **The happy path.** One case.
2. **Each boundary.** Empty, one, many, maximum, too long, zero, negative.
3. **Each failure.** Request fails, times out, returns the wrong shape, permission denied.
4. **Each state the UI can be in.** Loading, empty, error, partial, stale-while-refetching.
5. **Each actor.** Roles, permissions, tenants — anyone who sees something different.
6. **What must NOT happen.** The button that stays hidden, the request that is not sent,
   the navigation that does not occur. Negative cases catch the bugs positive ones miss.

A criterion with no case is a hole in the plan. A case covering no criterion is scope you
invented — check it with the person before it becomes a test.

### Levels

Put each case at the lowest level that can prove it: pure rules as unit tests, a feature's
flow as an integration test, and only the critical paths end to end. Say in the table when
a case cannot be automated here and why — that line is what stops it being quietly dropped.

### Traceability, both ways

- Every acceptance criterion appears in at least one case.
- Every case names the test file that implements it, once it exists.
- A case that stays manual keeps `❌` and a reason. `fe-verify` reports those as unverified
  rather than counting them as done.

### Regression cases

A bug fix earns a case that fails on the old behaviour: state the trigger exactly, because
the next person needs to know what actually broke, not the tidy summary.
