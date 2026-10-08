---
title: Pull requests
tags: pr, gh, review, base-branch, body, follow-up
---

## Pull requests

PRs target the project's base branch — check the profile, it is not always `main`. Use the
`gh` CLI when it is installed and authenticated.

```bash
git -C <repo> push -u origin <branch>
gh pr create --repo <org>/<repo> --base <base> --head <branch> \
  --title "<subject>" --body-file <file>
```

Write the body to a file rather than passing a long `--body` string: quoting eats newlines
and backticks.

### Title

The same rule as a commit subject: what the change does, imperative, readable on its own.
GitHub truncates long titles in lists, so keep it under about 70 characters.

### Body

Four short sections, written for a reviewer who does not know the ticket:

```markdown
## What
One or two sentences on the change.

## Why
The cause, or the decision behind it. Link the ticket.

## How to check
The steps a reviewer follows, or the gates that were run, with their results.

## Notes
Anything deliberately left out, follow-ups, or a config change needed outside the code.
```

A bullet list of everything touched is not a PR body — that is the diff. What a reviewer
cannot get from the diff is *why*, and what to look at first.

End the body with the PR attribution line the session was given, when it has one.

### Review follow-up

- Address findings in new commits on the same branch. Do not force-push over a review in
  progress; the reviewer loses their place.
- Reply to a finding you are **not** acting on, with the reason. Silence reads as agreement.
- A finding that is wrong gets a short, factual answer — not a change made to satisfy it. A
  test deleted to quiet a review is a defect.
- When the branch has drifted from the base, merge the base in rather than rebasing a
  pushed branch, unless the person asks for a rebase.

### Before asking for review

Gates pass locally, the branch carries the ticket key, the PR targets the base branch, and
the body says why. For spec-driven frontend work, see
[with-frontend-flow.md](with-frontend-flow.md).
