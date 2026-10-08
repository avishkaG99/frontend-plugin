---
description: Derive a numbered test plan from an approved spec, check it against the test-case library, then optionally implement, promote or backfill cases
argument-hint: "[spec slug] [--implement] [--promote] [--backfill <area>]"
---

Build the test plan for a frontend spec. Target: $ARGUMENTS

1. Load the `frontend-flow` skill.
2. Resolve the spec in the project's feature-spec folder. With no argument, use the most
   recently modified one and name it so the person can correct you.
3. Delegate to the `fe-test` agent to derive cases from the acceptance criteria — happy
   path, boundaries, failures, UI states, actors, and what must not happen — write the
   table into the spec under `## Test plan`, and check the feature against the test-case
   library.
4. Show the case count by level, any criterion too vague to test, and every case that
   cannot be automated here, with its reason.
5. Show the `## Library changes` result: existing cases to re-run, and the cases proposed
   to add, amend or retire.
6. Stop, unless a flag was passed:
   - `--implement` → `fe-test` writes the automatable cases and reports which now exist.
   - `--promote` → show the proposed library rows; on a yes, `fe-test` writes them into the
     library and points the spec rows at their IDs.
   - `--backfill <area>` → `fe-test` drafts cases for an area from its existing specs, for
     review. Nothing becomes `Active` without approval.
