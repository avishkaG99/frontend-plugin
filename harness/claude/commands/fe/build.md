---
description: Implement the next step of an approved plan, run the gates, update the spec
argument-hint: "[step number or spec slug]"
---

Build the next step of an approved plan. Target: $ARGUMENTS

1. Load the `frontend-flow` skill.
2. Resolve the spec and its plan. Take the lowest-numbered unticked step, or the step the
   person named. If the plan is not approved, stop and say so.
3. Delegate to the `fe-build` agent for that one step, with its tests.
4. Delegate to the `fe-verify` agent: lint, typecheck, the full test suite, Definition of
   Done, then tick the plan row and append to the spec's log.
5. Report with real numbers what passed, what was fixed, what is pre-existing, and what
   could not be verified here.
6. Name the next step and stop. Do not roll on to it, and do not commit unless asked.
