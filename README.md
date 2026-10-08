# frontend-flow

Spec-driven React delivery for Claude Code and Cursor: write the spec, plan it, derive the
test cases, build one step at a time, run the gates, audit it, land it.

One project-neutral core, one small profile per project. Point it at a second React
codebase by writing a new profile — the method does not change.

## How it works

```
core/                      project-neutral method (the part you reuse)
  skills/frontend-flow/    spec workflow, planning, conventions, test plan,
                           testing, security, performance, gates, conductor,
                           ui-design, test-library
  skills/git-flow/         branches, commits, PRs, review follow-up
  skills/web-verify/       real-browser runs: Python Playwright, storage-state auth,
                           per-case results back into the spec
  agents/                  fe-spec fe-plan fe-test fe-build fe-verify fe-audit
                           fe-e2e fe-git
  commands/                /fe:run /fe:spec /fe:plan /fe:test /fe:build /fe:audit
                           /fe:e2e /git:commit /git:pr
  hooks/                   fe-flow-status.py — SessionStart: which features are mid-flight
  profile.template.md      copy this to start a new project

vendor/<skill>/            third-party skills, pinned to a commit and reviewed;
                           SOURCE.md says where from and what was changed
                           (frontend-design, from anthropics/skills)

profiles/<name>.md         one project's facts: repos, stack, paths, commands,
                           base branch, ticket keys, traps

harness/claude/            generated — .claude/ layout (skills, agents, commands)
harness/cursor/            generated — one .mdc rule per skill

scripts/sync.py            core + profile -> harness, and installs into a project
```

`sync.py` splices the profile into each skill where it says `<!-- profile -->`. Everything
under `harness/` is generated: edit `core/` or `profiles/`, never the output.

## The flow

`/fe:run <TICKET-1 or slug>` conducts the whole thing: it reads the spec's
`## Flow status` block, does the next move through the agent that owns it, updates the
block, and stops. Run it again for the next move, or pass `--auto` to keep going until it
needs you. When the plan is built and verified it runs the audit and browser checks, then
drafts the commit, the PR and the ticket update for approval. `--status` just reports.

Visible work is looked at, not just tested. The spec carries a UI plan built from the
project's design system, each screen state gets a browser case, and after a build step that
touches a screen `/fe:run` offers a step check: `fe-e2e` runs that step's cases and reviews
the screenshots against the UI plan. The full browser run still happens at the end.

A new Claude Code session starts with a line per feature still in progress, from the
SessionStart hook, so nothing depends on remembering where you were.

The steps it runs are also commands of their own:

| Step | Command | What it does | Stops for you |
| --- | --- | --- | :---: |
| 1 | `/fe:spec <idea or TICKET-1>` | Writes the feature spec, asks its open questions in the file | yes |
| 2 | `/fe:plan` | Ordered, file-level plan; step 1 is a thin slice that runs | yes |
| 3 | `/fe:test` | Test cases derived from the acceptance criteria, before the code, plus what the test-case library needs: re-run, add, amend, retire | yes |
| 4 | `/fe:build` | One plan step with its tests, then the full gates, then updates the spec | per step |
| 5 | `/fe:audit` | Security and performance findings on the diff | — |
| 6 | `/fe:e2e` | Runs the plan's browser cases, or any slice of the library (`--all`, `--area`, IDs, `--impacted`), against your local app | before the browser opens |
| 7 | `/git:commit`, `/git:pr` | Drafts the message and the PR body for approval | yes |

The spec file is the unit of work, not the conversation. It carries the request, the flow
status, the plan, the test cases, the decisions and the log, so a new session picks it up
and knows where things stand.

## Install

Into a project's `.claude/` (and `.cursor/`):

```bash
python3 scripts/sync.py --profile areasim --install /path/to/project
```

Restart the editor so the skills, agents and commands load. `--install` also merges the
SessionStart hook into the project's `.claude/settings.json`, once, leaving the rest of
the file alone.

## Add a project

1. `cp core/profile.template.md profiles/<name>.md` and fill it in. Delete lines you
   cannot answer rather than guessing — the agents treat every line as fact.
2. `python3 scripts/sync.py --profile <name> --install /path/to/that/project`

What belongs in a profile: the repos, the stack, where code goes, where the standards live,
the exact lint/typecheck/test commands, the base branch and ticket-key pattern, and the
traps — the things a competent newcomer gets wrong here.

## Editing

```bash
# change method  -> core/
# change a fact  -> profiles/<name>.md
python3 scripts/sync.py --profile <name>            # regenerate harness/
python3 scripts/sync.py --check                     # CI: fails if harness is stale
```

## The test-case library

A spec's test plan proves one change; the library keeps what must go on working. It lives
in the app repo (path in the profile), one Markdown file per area, with use cases
(`UC-SUR-02`) and test cases (`TC-SUR-004`) whose IDs never change.

- `/fe:test` checks each feature against its area and writes `## Library changes` into the
  spec: the existing cases to re-run, and new, amended or retired cases as `Draft`.
- At handoff `/fe:run` shows those rows; approved ones go into the library as `Active`, in
  the feature's commit. Declining costs nothing.
- `/fe:e2e` runs any slice: everything, an area, a use case, named cases, or the cases
  impacted by the current branch. Automated rows go through the test command; `browser`
  rows through Playwright. Results go to a local run report, never into the library.
- Every run also lists behaviour it walked past that no case covers, as proposals.

## Browser verification

Lint, typecheck and the unit suite never open a browser, so every case the test plan marks
as not automated stays unverified. `/fe:e2e` closes that: it reads those cases from the
spec, runs them against your **local** dev server with Python `playwright` (no dependency
added to the app), signs in from a saved storage state rather than scripting an identity
provider, retries a failing case three times with a screenshot on the last, and writes a
per-case table back into the spec.

Sessions are captured by you, not by an agent:

```bash
python3 scripts/capture_auth.py <role>     # a browser opens; you sign in; the file is saved
python3 scripts/capture_auth.py --list     # what exists, and how stale it is
```

No agent ever needs a password, and the saved file is gitignored, never printed and never
pasted into a report.

Statuses mean one thing each: `PASSED`, `FAILED` (the product misbehaved), `BLOCKED` (the
case could not run — says nothing about the product), `SKIPPED` (with a reason). A case that
only passed on attempt three is reported as flaky.

## What it borrows

### From AI-DLC

[awslabs/aidlc-workflows](https://github.com/awslabs/aidlc-workflows) is the "one core,
many harnesses" template. Four of its ideas are here, cut down for a single app:
ambiguity resolved in writing before planning, a first step that runs end to end
(skeleton-on), traceability from criterion to step to test, and a hard gate between plan
and code. Its stage format — each phase declaring what it consumes and produces — shapes
`web-verify`. Its conductor shapes `/fe:run`: one main-session conductor that only
delegates, state kept in a file rather than the conversation, and a session-start hook
that surfaces it. Its Stop-hook loop that refuses to end a turn is deliberately not here:
the person sets the pace. Its 33 stages, phase graph and reviewer agents are not here.

### From Anthropic's frontend-design skill

[anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/frontend-design)
supplies the method in `references/ui-design.md` — plan the UI before code, review the plan,
critique from screenshots, the quality floor, and its rules for interface copy — pointed
at matching an existing design system rather than inventing one. The skill itself is in
`vendor/`, scoped to greenfield design work, so it never restyles the product.

### From web-app-tester

[avishkaG99/plugins-official](https://github.com/avishkaG99/plugins-official/tree/main/plugins/web-app-tester)
is the browser-testing pattern: a phased orchestrator, Python Playwright in a scratch run
directory, structured per-case log lines, storage-state auth, retries with a screenshot on
the last attempt, a mutations guard, and approval gates before the browser and before
anything is posted.

Its skills are folded in here rather than installed beside it, adapted to run locally:
the committed test-case sheet became the test-case library; its coverage analysis
(proposing rows for uncovered behaviour, amendments instead of duplicates) became
`/fe:test`'s Library changes and the gaps section of every run report; its propose →
approve → apply flow became promotion at handoff; `/verify-bug`'s decisive check and three
verdicts became `references/bug-recheck.md`; and its session rules (one exploration pass,
batches of ten, unbuffered streaming, screenshot self-check) are in `session.md`.

What did not come across is everything PR-shaped: no PR or work-item comments, no labels
or checkbox approvals, no preview-URL scraping, no CI runner. Cases come from the spec or
the library, results stay on this machine, and every run is against the local app.
