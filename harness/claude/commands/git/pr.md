---
description: Draft a pull request against the base branch, for approval
argument-hint: "[anything reviewers should know]"
---

Prepare a pull request. Context: $ARGUMENTS

1. Load the `git-flow` skill.
2. Identify the repo and branch, and check whether it is pushed and how it differs from the
   base branch (`git log --oneline <base>..HEAD`, `git status`).
3. Check for an existing PR for this branch (`gh pr list --head <branch>`). If one exists,
   this is an update to it, not a new PR.
4. For spec-driven work, confirm the gates were run and read the feature spec for the Why
   and the check steps.
5. Delegate to the `fe-git` agent for the title and the What / Why / How to check / Notes
   body, against the base branch.
6. Show the person the title, the full body, and the exact `gh` command. Wait for approval,
   then push and create or update the PR.
