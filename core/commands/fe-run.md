---
description: Run a feature end to end — work out where it stands, do the next move, track it in the spec, and hand everything off when it is finished
argument-hint: "[ticket key, spec slug or new request] [--auto] [--status] [--no-ticket]"
---

Conduct a frontend feature. Target: $ARGUMENTS

1. Load the `frontend-flow` skill and follow `references/conductor.md`. You are the
   conductor: you delegate every move to the agent that owns it and write no product code
   yourself.
2. **Resolve the ticket, then the spec.** A ticket key or slug → find its file in the
   feature-spec folder. A new request → settle the ticket first, per the conductor
   reference "The ticket comes first": use the key given or the branch's key; otherwise
   search the tracker for a match and ask; otherwise draft a new ticket and create it only
   on a yes. `--no-ticket` is for small chores only and is recorded in the log. Then this
   is the `spec` stage. No argument → the spec with an
   unfinished Flow status block that was updated most recently; name it so the person can
   correct you.
3. **Read the state** from the spec's `## Flow status` block. If there is none, add it,
   deriving each tick from what the file already shows, and log that you did.
4. **Report where it stands** in two lines: stage, next move, anything waiting on the
   person. With `--status`, stop here.
5. **Do the next move** per the conductor reference: delegate to the owning agent with the
   spec path, the ticket key and the stage, and pass everything the agent needs in the
   prompt, since it cannot see this conversation.
6. **Record it**: update the Flow status block, make sure the agent appended to the Log,
   and correct the block if the code says otherwise.
7. **After a build step that touches a visible screen**, offer the step check from the
   conductor reference: `fe-e2e` runs that step's browser cases and reviews their
   screenshots. Ask before the browser opens; a missing dev server or session is logged as
   `BLOCKED` and the build carries on.
8. **Stop and report**: what was done, what it proved with real numbers, and the next move.
   With `--auto`, carry on to the next move instead, until one of the conductor's stop
   conditions is hit.
9. **When the plan is fully built and verified**, run the handoff: audit, the full browser
   run with screenshot review, the spec written in its final state, then the commit, PR
   and ticket drafts (comment, status move, worklog from the journal), each shown for
   approval. Finish with the summary of what shipped, what was verified, and what is still open.

Never approve on the person's behalf, never push, post, move a ticket or log time without
a yes for that specific draft, and never guess a time the journal does not record.
