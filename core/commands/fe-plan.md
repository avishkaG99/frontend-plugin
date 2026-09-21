---
description: Turn an approved frontend spec into an ordered, file-level plan, then stop for approval
argument-hint: "[spec slug or feature name]"
---

Plan an approved frontend spec. Target: $ARGUMENTS

1. Load the `frontend-flow` skill.
2. Resolve the spec in the project's feature-spec folder. With no argument, use the most
   recently modified one, and name it so the person can correct you.
3. If questions in the spec are unanswered, or its status is not `Approved`, stop and say
   which. Do not plan around a gap.
4. Delegate to the `fe-plan` agent.
5. Show the plan table, what step 1 proves end to end, the reuse it found, and any risk
   needing a decision.
6. Stop. No code until the person approves the plan. Then `/fe:build`.
