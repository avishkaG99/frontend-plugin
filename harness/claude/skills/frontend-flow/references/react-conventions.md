---
title: Writing code that matches the codebase
tags: react, structure, hooks, data, state, i18n, conventions, reuse
---

## Writing code that matches the codebase

The project's own layout, stack and traps are in the profile at the end of SKILL.md, and
its written rules are in the standards documents that profile lists. This file is the part
that does not change between projects: how to arrive at code that looks like it belongs.

### Read before you write

Open the file you are changing **and** the closest existing example of the same kind of
thing — the sibling component, the neighbouring hook, the last service added. A codebase
usually has one way of doing each thing. Find it rather than inventing a second, and match
its naming, its file shape and its comment density.

Two similar-but-different implementations is the cost that lands on whoever comes next.

### Reuse before writing

Before adding a component, hook, service, util or type, search for one that already does
it. A near-duplicate is a defect, not a shortcut. If the existing one nearly fits, extend
it or say why it cannot be extended.

### Keep the layers honest

Most React apps here separate transport, server-state and rendering:

- **Service / transport:** one call, typed in and out, no React.
- **Query hook:** the cache key and its options — `staleTime`, `enabled`, `retry` — and any
  derived helper. Comment *why* a non-default was chosen; the default is the norm and a
  deviation is a decision.
- **Component:** renders pending, error and data. A pending query is not "no data": gating
  a redirect or a decision on an unsettled query acts on a guess during first paint.

Client state that outlives a component goes to the app's store; everything else is local
state in the component that owns it. Never mirror server data into the store.

### Strings, errors and states

Every user-visible string goes through the project's i18n layer, in **all** locale files at
once. Every new view has a loading, empty and error state that a person could live with —
not necessarily polished, but not broken. User-visible errors say what happened in plain
terms and leak nothing internal.

### Comments

Comment the *why*, especially where a line looks wrong until you know the reason: a race,
a browser quirk, an API oddity, a deliberate deviation. Do not narrate what the code
already says. Match the density of the file you are in.

### Scope

Change what the plan step says and nothing else. An unrelated improvement you noticed goes
in the spec's log as a note, not into this diff. Drive-by refactors make a review
impossible to do honestly.

### Dependencies

Don't. The stack is decided. If something genuinely needs a new package, stop and ask.
