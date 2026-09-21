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
  agents/                  fe-spec fe-plan fe-test fe-build fe-verify fe-audit fe-git
  commands/                /fe:spec /fe:plan /fe:test /fe:build /fe:audit
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
| 6 | `/git:commit`, `/git:pr` | Drafts the message and the PR body for approval | yes |

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

## What it borrows from AI-DLC

[awslabs/aidlc-workflows](https://github.com/awslabs/aidlc-workflows) is the "one core,
many harnesses" template. Four of its ideas are here, cut down for a single app:
ambiguity resolved in writing before planning, a first step that runs end to end
(skeleton-on), traceability from criterion to step to test, and a hard gate between plan
and code. Its 33 stages, phase graph and reviewer agents are not.
