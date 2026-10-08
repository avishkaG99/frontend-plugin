---
title: Landing frontend work
tags: frontend-flow, spec, gates, tracker, worklog, handoff
---

## Landing frontend work

How `git-flow` meets the `frontend-flow` skill. Load both when the work is a spec-driven
feature.

### Order

1. **Branch before the first build step**, named from the ticket. `/fe:build` writes code
   but never branches, so a missing branch means work lands on whatever was checked out.
2. **Build and verify** through `/fe:build`. Gates green before any commit.
3. **Commit the spec with the code.** The feature spec is part of the change — it is what
   the next person reads. Committing it separately, or later, defeats it.
4. **PR against the base branch**, body per [pull-requests.md](pull-requests.md). The
   spec's Decisions section is usually the "Why", and its log is the "How to check".
5. **Ticket**, if the person asks: the tracker integration drafts the worklog and comment.
   Nothing is written to the tracker without approval.

### One commit per plan step, or one per feature?

Per step, when the steps are genuinely separate changes — each reviewable and green on its
own. Per feature when they only make sense together. Ask if unsure, and never squash
someone else's history to make it tidy.

### What the commit message says

The spec's Decisions section, in prose. If a step exists only because of a constraint the
spec records — a browser behaviour, an API quirk — that constraint is the body of the
commit message.

### Before opening the PR

- The project's lint, typecheck and test gates pass, with the numbers in the PR body.
- Walk the project's PR checklist, where it has one.
- The spec's status is `Done`, or the PR says which steps remain and why it is open early.
