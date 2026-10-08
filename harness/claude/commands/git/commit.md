---
description: Draft a commit for the current change — staging plan and message — for approval
argument-hint: "[what the change is, if the diff alone is unclear]"
---

Prepare a commit. Context: $ARGUMENTS

1. Load the `git-flow` skill.
2. Work out which repo holds the change, per the skill's profile, and whether the
   directory you are in is itself a git repo.
3. Delegate to the `fe-git` agent to check the branch (pattern, same ticket as the work,
   not the base branch), read the diff, and draft the staging plan and message. A branch
   mismatch is fixed first, with the person's yes.
4. Show the person: branch, files to stage, files deliberately left out, and the exact
   commit message.
5. Wait for approval. On a yes, stage those paths and commit. Do not push unless they ask.
6. If the branch has no ticket key and the work has a ticket, say so and offer to rename it
   before the first push.
