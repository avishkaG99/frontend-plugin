---
description: Write or update a frontend feature spec, then stop for approval
argument-hint: "<what you want built, or a ticket key>"
---

Start spec-driven frontend work. Request: $ARGUMENTS

1. Load the `frontend-flow` skill.
2. Look in the project's feature-spec folder (named in the skill's profile) for an existing
   spec covering this. If one exists, update it rather than starting a second file.
3. Delegate to the `fe-spec` agent with the request, the existing spec path if there is
   one, and the ticket key if the request or the branch carries one.
4. Show the person the spec path, its open questions and anything in the code that
   contradicts the request.
5. Stop. Do not plan or implement. Tell them to answer the questions in the file (or
   here), then run `/fe:plan` once the spec is approved.
