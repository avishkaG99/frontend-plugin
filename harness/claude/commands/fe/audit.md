---
description: Review the current frontend change for security and performance findings
argument-hint: "[paths, or a branch to diff against the base]"
---

Audit a frontend change. Scope: $ARGUMENTS

1. Load the `frontend-flow` skill.
2. Work out the scope: the named paths, or the working-tree diff, or the branch against the
   project's base branch. State what you are reviewing before you start.
3. Delegate to the `fe-audit` agent for the security pass and the performance pass.
4. Report findings ranked by consequence, each with file, line, what actually goes wrong,
   and the fix. Then say what was examined and what could not be checked from the client
   side.
5. Change nothing. Ask before fixing anything the audit found.
