---
title: Running a feature end to end
tags: conductor, run, status, stages, resume, handoff, finish
---

## Running a feature end to end

`/fe:run` is the conductor. It reads where a feature stands, does the next move by handing
it to the agent that owns it, records the outcome, and says what comes next. It never
writes product code itself, and the agents never call each other: only the conductor
delegates.

The conductor runs in the main session, not as an agent, because only the main session can
delegate to agents and ask the person a question.

### The stages

| # | Stage | Owner | Done when | Stops for the person |
| --- | --- | --- | --- | :---: |
| 0 | `ticket` | conductor + tracker integration | the work has a ticket key — found, or drafted and created on a yes — or the person chose no ticket for a chore | yes, to create one |
| 1 | `spec` | `fe-spec` | spec written, every question answered, person says approved | **yes** |
| 2 | `plan` | `fe-plan` | plan table written, person says approved | **yes** |
| 3 | `test-plan` | `fe-test` | `## Test plan` table written; `## Library changes` lists the cases to re-run and the ones to add, amend or retire; automatable cases implemented if asked | — |
| 4 | `branch` | `fe-git` | a branch carrying the ticket key is checked out in the app repo | yes, to create it |
| 5 | `build` | `fe-build` + `fe-verify`, one step per move; `fe-e2e` step check on visible steps | every plan row ticked | yes, before a step check opens the browser |
| 6 | `verify` | `fe-verify` | full gates green on the whole change, Definition of Done walked | — |
| 7 | `audit` | `fe-audit` | findings reported; anything severe fixed or accepted by the person | yes, if a finding needs a decision |
| 8 | `e2e` | `fe-e2e` | the spec's not-automated cases **and** the library's impacted cases each have a status; screenshots reviewed; this final run is a **milestone**, so its report (environment block first) is committed with the library and indexed | yes, before the browser opens |
| 9 | `handoff` | `fe-test`, `fe-git`, tracker integration | library changes promoted or declined; spec written final and committed with the code; PR, ticket comment, status move and worklog drafted and approved or declined | **yes**, per draft |
| 10 | `done` | — | spec Status `Done`, nothing waiting | — |

`e2e` is skipped, with the reason recorded, only when the change has no visible UI and
no not-automated cases. A change that touches a screen always gets a browser run, even if
every case is automated, so someone looks at it. `test-plan` is never skipped: cases come
from the spec before code.

### Browser checks during build

jsdom proves behaviour, not that a screen renders right. After a build step whose files
include a visible screen, and once `fe-verify` is green, the conductor offers a **step
check**: `fe-e2e` runs only the not-automated cases for that step's acceptance criteria and
reviews their screenshots against the UI plan. The full `e2e` stage still runs at the end.

- It needs the dev server and a saved session. If either is missing, say so, log the step
  check as `BLOCKED` with the reason, and carry on — it never blocks the build.
- The browser gate still applies: ask before it opens. In `--auto`, the person can say yes
  once for all step checks of the feature; record that in the Log.
- A `FAILED` case or a serious design note goes back to `build` as a fix on the same step,
  not a new step, unless the spec was wrong.

### The Flow status block

The conductor's state lives in the spec, so the spec stays the unit of work. One block,
placed first among the sections this flow adds, above `## Plan`:

```markdown
## Flow status

| Field | Value |
|---|---|
| Ticket | AR-123 |
| Repo / branch | areasim-webapp · feat/ar-123-short-slug |
| Stage | build |
| Next | Step 3 — empty state for the zone list |
| Waiting on | — |
| Updated | 2026-10-08 |

- [x] ticket — AR-123 (existing)
- [x] spec — approved 2026-10-07
- [x] plan — approved 2026-10-07
- [x] test-plan — 14 cases, 9 automated
- [x] branch
- [ ] build — 2 of 5 steps
- [ ] verify
- [ ] audit
- [ ] e2e
- [ ] handoff
```

- **This block is state, not history.** It is the one section that is overwritten in
  place. History goes in the Log, appended, as always.
- `Waiting on` names the person and the thing ("approval of the plan", "answer to Q4",
  "browser run go-ahead") or is `—`. When it is not `—`, the next move is to ask, not act.
- `Stage` is the first unticked stage. `Next` is the concrete move inside it.
- Whoever finishes a stage updates the block — the conductor, or an agent run through its
  own command (`/fe:build`, `/fe:test`) when the spec has one. A spec without the block is
  fine; `/fe:run` adds it, deriving each tick from what the file already shows.

### Working out the next move

Read the spec, not the conversation. In order:

1. `Waiting on` is set → ask for that, and stop.
2. No ticket key, and no recorded decision to work without one → `ticket`.
3. Status is `Draft`, or a question has no answer → `spec`.
4. No plan table, or the plan is not approved → `plan`.
5. No `## Test plan` → `test-plan`.
6. No branch with the ticket key in the app repo → `branch`.
7. An unticked plan row → `build` that one row, then its step check if the row touches a
   visible screen.
8. Then `verify`, `audit`, `e2e`, `handoff`, each unless already ticked.

When the file and the code disagree — a row ticked whose code is not there, a branch named
that does not exist — the code wins. Fix the block, log the difference, and say so.

### The ticket comes first

Every artefact keys off the ticket — the spec's name and Related line, the branch, the
commits, the PR title, the tracker journal — so it is settled before the spec is written.

1. **A key was given**, or the current branch carries one → read the ticket through the
   project's tracker integration, and carry on.
2. **No key** → search the tracker for open tickets that look like the request, and ask
   "is it one of these?" Show at most five, with key, summary and status.
3. **None fits** → draft a new ticket and show it: summary, a description written from the
   request (problem, outcome, acceptance criteria as known), type, parent, assignee. On a
   yes, the tracker integration creates it and starts its journal. On a no, ask what to
   change. Never create a ticket unseen.
4. **No ticket on purpose** — only for a small chore (a typo, a dependency bump, a config
   tweak): the person says so, the branch is `chore/<slug>` without a key, and the spec's
   log records why. Anything with user-visible behaviour gets a ticket.

Record the outcome in Flow status: `Ticket` holds the key or `none — chore`, and the
`ticket` line is ticked with how it was resolved (existing, created, none).

### The branch check

Before the first `build` move and before any commit, `fe-git` checks the app repo's
current branch against the profile's pattern:

- it matches the pattern (type prefix, ticket key, slug);
- its key is **this** spec's key — not another ticket's branch left checked out;
- it is not the base branch.

Any mismatch stops the move with a proposal — the branch to create, or the rename — and
waits. The conductor never switches, renames or creates a branch without a yes: it would
move the person's uncommitted work out from under them.

### Pace

One move per `/fe:run`, then report and stop. The person decides when the next one runs.

`/fe:run --auto` keeps going without stopping between moves, but still stops at:

- the ticket draft, either approval gate, and every draft in `handoff`;
- any gate that fails and is not obviously this change's fault;
- any question the agent cannot answer from the spec or the code;
- any finding from `audit` rated high or above;
- the browser gate before `e2e`.

A wrong direction found in `--auto` costs one move, because each `build` move is still one
plan row with its own gate run.

### Cost

Long sessions and agent runs dominate the bill, not single searches. The `token-efficiency`
skill has the general habits; the flow applies them like this:

- **One ticket per session.** After a handoff, or about every three build moves, the
  conductor suggests `/compact` (same ticket) or a new chat (next ticket). Flow status
  makes resuming free, so nothing is lost.
- **Brief agents narrowly.** Tell an agent which sections to read: Flow status, its plan
  row, the acceptance criteria and test cases that row covers, `## Decisions`, and the
  latest Log entry. Never "read the whole spec and every Log entry" once a spec is long.
  Point at paths and line ranges instead of pasting content into the prompt.
- **Small rows may share a move.** Two adjacent plan rows that touch the same files and
  together stay within about three files go to one `fe-build` run. Each row is still
  ticked on its own.
- **Gates where they are cheapest.** Between steps, `fe-build`'s own lint, typecheck and
  scoped tests are enough; the full `fe-verify` run happens once, at `verify`, and again
  only after fixes that touch shared code.
- **Reports, not dumps.** Agents report changed files, test numbers and open points; the
  conductor relays that, not the agent's full output.

These never weaken a gate: both approval stops, the full gate run before the browser, and
the browser run itself still happen.

### Handoff: what "finished" produces

When every plan row is ticked and `verify` is green, the conductor finishes the work in
this order and shows each draft before anything leaves the machine:

1. **Library**: `fe-test` re-runs the coverage check against the final code, then the
   conductor shows the `## Library changes` rows. On a yes they are written into the
   library as `Active` (or `Retired`) and the spec rows point at their new IDs; on a no
   they stay `Draft` in the spec. See `references/test-library.md`.
2. **Spec, in its final state, before the commit**: Status `Done`, every Flow status box
   ticked including `handoff`, Stage `done`, Next `— (PR review)`, and a closing Log entry
   that says what the change does and what the final gate run proved, with numbers. The
   commit carries the finished spec, so nothing is left to write into the repo afterwards.
   Facts that only exist after the push (PR number, comment and worklog ids) never go in
   the spec; they go in the tracker journal, which lives outside the app repo.
3. **Commit draft** via `fe-git`: staging plan path by path, the spec and any library
   files included with the code, message from the Decisions section. Commits on a yes; never pushes unprompted.
4. **PR draft** via `fe-git` against the base branch: What / Why / How to check / Notes,
   gate numbers, e2e table, open items. Pushes and opens it on a yes.
5. **Ticket drafts**, when the profile names a tracker integration and the work has a key.
   Shown together, each approved or declined on its own:
   - a progress comment summarising what shipped and the PR link;
   - a status move: fetch the ticket's transitions and propose the one the profile names
     for finished work, by id, never by a guessed name;
   - a worklog: the ticket's unlogged journal rows for this work, with their recorded
     times, totalled. Never guess, round or stretch a time; a row with no recorded time is
     shown as untimed and the person gives the figure or leaves it out. Declining, or
     "log it later", is a valid answer and leaves the rows ⏳.
   Every write that is sent lands in the integration's local journal in the same turn.
6. **A summary to the person**: what shipped, what was verified and how, what was not
   verified and why, what is still open, and the links.

If a draft is declined after the commit, the spec stays as committed and the decline is
recorded in the tracker journal ("PR not opened: waiting on backend AR-731"), not as a new
uncommitted edit. A draft declined before the commit is noted in the spec's closing Log
entry and Next instead.

### What the conductor never does

- Approve on the person's behalf, or read silence as approval.
- Skip `test-plan`, or reorder `build` ahead of an approved plan.
- Write product code itself. If no agent fits the move, stop and say so.
- Push, open a PR, post to the tracker or log time without a yes for that specific draft.
