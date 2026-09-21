---
name: git-flow
description: Branch, commit and pull-request conventions for this project — branch naming from a ticket key, commit messages that say why, PRs against the base branch via gh, and review follow-up. Use when asked to branch, commit, push, open or update a PR, write a commit message, or when work is finished and needs to land.
---

# Git flow

The repos, the base branch, the remote and the branch-name pattern are in the profile at
the end of this file. Read it before running anything: whether the directory you are in is
itself a git repo is a per-project fact, and getting it wrong runs your command against the
wrong tree.

## Branch names

Follow the project's pattern exactly, and **put the ticket key in the branch**: the tracker
integration resolves the ticket from the branch name, so a branch without one makes every
later step manual. When there is no ticket yet, create one or ask before branching without
a key.

## Commits

Write the subject as what the change does, in the imperative, under about 70 characters:

> `Keep the reauth loop guard active for its full window`

Then a body explaining **why**, wrapped at 72 columns, for anything not obvious from the
diff: the cause, what was ruled out, what a reader would otherwise wonder about. Mechanical
changes can skip the body.

Never do these — each one has happened in a real history and none of them helps the next
reader:

- Paste chat text, review replies or numbered answers into a commit message.
- Describe the conversation ("Thanks for the re-review. Going through the findings…").
- Write a subject that only names the files touched.

End every commit message with the attribution line the session was given, when it has one.

## What needs asking first

Committing, pushing, opening a PR, force-pushing, rebasing, resetting, and anything that
rewrites published history. The person asks; you do not offer to do it silently because the
work looks finished.

Never stage blindly. `git add -A` sweeps up stray files — read `git status` first and add
the paths that belong to the change.

## Where to look

| You need to | Read |
| --- | --- |
| Open or update a PR, handle review comments | [references/pull-requests.md](references/pull-requests.md) |
| Land spec-driven frontend work | [references/with-frontend-flow.md](references/with-frontend-flow.md) |

## The one gotcha

`cd` into the repo in the same command as the git call, or the working directory will not
be what you think. `git -C <repo> status` is safer still.

<!-- profile -->
