# frontend-flow

Spec-driven React delivery for Claude Code and Cursor: write the spec, plan it, derive the
test cases, build one step at a time, run the gates, audit it, land it.

One project-neutral core, one small profile per project. Point it at a second React
codebase by writing a new profile — the method does not change.

## How it works

```
core/                      project-neutral method (the part you reuse)
  skills/frontend-flow/    spec workflow, planning, conventions, test plan,
                           testing, security, performance, gates
  skills/git-flow/         branches, commits, PRs, review follow-up
  skills/web-verify/       real-browser runs: Python Playwright, storage-state auth,
                           per-case results back into the spec
  agents/                  fe-spec fe-plan fe-test fe-build fe-verify fe-audit
                           fe-e2e fe-git
  commands/                /fe:spec /fe:plan /fe:test /fe:build /fe:audit /fe:e2e
                           /git:commit /git:pr
  profile.template.md      copy this to start a new project

profiles/<name>.md         one project's facts: repos, stack, paths, commands,
                           base branch, ticket keys, traps

harness/claude/            generated — .claude/ layout (skills, agents, commands)
harness/cursor/            generated — one .mdc rule per skill

scripts/sync.py            core + profile -> harness, and installs into a project
```

`sync.py` splices the profile into each skill where it says `<!-- profile -->`. Everything
under `harness/` is generated: edit `core/` or `profiles/`, never the output.

## The flow

| Step | Command | What it does | Stops for you |
| --- | --- | --- | :---: |
| 1 | `/fe:spec <idea or TICKET-1>` | Writes the feature spec, asks its open questions in the file | yes |
| 2 | `/fe:plan` | Ordered, file-level plan; step 1 is a thin slice that runs | yes |
| 3 | `/fe:test` | Test cases derived from the acceptance criteria, before the code | yes |
| 4 | `/fe:build` | One plan step with its tests, then the full gates, then updates the spec | per step |
| 5 | `/fe:audit` | Security and performance findings on the diff | — |
| 6 | `/fe:e2e` | Runs the plan's browser cases against your local app, per-case results | before the browser opens |
| 7 | `/git:commit`, `/git:pr` | Drafts the message and the PR body for approval | yes |

The spec file is the unit of work, not the conversation. It carries the request, the plan,
the test cases, the decisions and the log, so a new session picks it up and knows where
things stand.

## Install

Into a project's `.claude/` (and `.cursor/`):

```bash
python3 scripts/sync.py --profile areasim --install /path/to/project
```

Restart the editor so the skills, agents and commands load.

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
`web-verify`. Its 33 stages, phase graph and reviewer agents are not here.

### From web-app-tester

[avishkaG99/plugins-official](https://github.com/avishkaG99/plugins-official/tree/main/plugins/web-app-tester)
is the browser-testing pattern: a phased orchestrator, Python Playwright in a scratch run
directory, structured per-case log lines, storage-state auth, retries with a screenshot on
the last attempt, a mutations guard, and approval gates before the browser and before
anything is posted.

It is PR-driven and generates a plan from the pull request. `web-verify` is **local and
spec-driven**: the cases come from the feature spec's test plan and the results go back to
the same file, so nothing depends on a PR, a deployment URL or a comment thread.
