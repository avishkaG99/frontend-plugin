---
title: Frontend performance
tags: performance, bundle, rendering, queries, lists, images, profiling
---

## Frontend performance

Two questions answer most of it: **how much arrives before the page is usable**, and **how
much work happens on every interaction**. Everything below serves one of those.

### Measure before you optimise

A memo added on suspicion costs readability and buys nothing. Profile first — the
framework's profiler for re-renders, the network panel for payloads, the build's bundle
output for size. State the number you saw before and after, or it is not an optimisation,
it is a guess.

### What arrives

- **Route-level code splitting** is the highest-value change in most apps: a screen nobody
  opens should not be in the first download.
- A heavy library pulled in for one helper (dates, charts, lodash, icon sets) is the most
  common bundle regression. Import the function, not the package, or write the helper.
- Images: right dimensions, modern format, lazy below the fold. An oversized hero image
  routinely outweighs all the JavaScript.
- Fonts: subset, preload the one that matters, and never let text stay invisible while a
  font loads.

### What re-renders

- A component re-renders when its state, its context, or its props change. Most "slow UI"
  is one of: a new object or arrow function created inline as a prop, context holding a
  value that changes on every render, or state that lives too high in the tree.
- Move state **down** to the component that owns it before reaching for memoisation.
- `memo`, `useMemo` and `useCallback` are for measured hot paths and referentially stable
  props. Used everywhere, they add allocation and noise and hide the real cause.
- Keys on lists must be stable identities, never the array index, or the framework rebuilds
  rows on every change.

### Lists and tables

Hundreds of rows in the DOM is the common wall. In order of preference: render fewer rows
(paginate, filter server-side), then virtualise, then optimise the row component. Sorting
and filtering large arrays belongs in a memo keyed on the inputs, not in the render body.

### Data fetching

- A stale-time of zero makes every mount refetch. Pick it from how often the data actually
  changes, and say why in a comment.
- Waterfalls are the silent cost: a request that waits for another that waits for a third.
  Fire independent requests together.
- Cancel what the user navigated away from, and do not refetch a list after every mutation
  when the response already carries the new row.
- Do not over-fetch: ask the API for the fields the view renders.

### Interaction

Debounce searches and resize handlers. Keep work out of scroll and pointer handlers. Show
the optimistic or pending state immediately — perceived speed is what people report, and a
spinner that appears in 50 ms beats a frozen button that resolves in 300 ms.

### What to write down

Put the measurement in the spec's log: what was slow, what you changed, what the number is
now. Without the before and after, the next person cannot tell whether to keep it.
