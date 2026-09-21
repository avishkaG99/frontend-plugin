---
description: Derive a numbered test plan from an approved spec, then optionally implement the cases
argument-hint: "[spec slug] [--implement]"
---

Build the test plan for a frontend spec. Target: $ARGUMENTS

1. Load the `frontend-flow` skill.
2. Resolve the spec in the project's feature-spec folder. With no argument, use the most
   recently modified one and name it so the person can correct you.
3. Delegate to the `fe-test` agent to derive cases from the acceptance criteria — happy
   path, boundaries, failures, UI states, actors, and what must not happen — and write the
   table into the spec under `## Test plan`.
4. Show the case count by level, any criterion too vague to test, and every case that
   cannot be automated here, with its reason.
5. Stop, unless `--implement` was passed. Then have `fe-test` write the automatable cases
   and report which ones now exist.
