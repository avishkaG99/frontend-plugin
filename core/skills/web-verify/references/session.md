---
slug: run-session
phase: verification
lead_agent: fe-e2e
gate: none — runs between Gate A and the report
consumes:
  - target-url (phase 1, required)
  - case-list (phase 1, required)
  - storage-state (phase 1, optional — unauthenticated runs are valid)
  - mutations-allowed (phase 1, required)
produces:
  - case-result[] (id, action, expected, observed, status, attempts, duration, screenshot)
  - run-start-time, run-duration
title: Running the browser session
tags: playwright, python, headless, selectors, retries, screenshots, cleanup
---

## Running the browser session

One session per run, one script, executed once. Writing a script per case wastes a browser
launch each time and loses the shared login.

### Layout

Everything lands in a relative `_webverify/` directory next to the app — never `/tmp`,
never an absolute path:

```
_webverify/
  run.py               the generated script
  run.log              structured results, one line per case
  screenshots/         only what failures and decisive checks needed
```

Delete the directory when the report is written. It is scratch, not evidence to keep.

### The script

Write a single Python script that launches headless Chromium, loads the storage state when
one is configured, and walks the cases in order. Each case prints one structured line, so
the results survive even when a later case crashes the run:

```python
print(f"CASE|{case_id}|{status}|{attempts}|{duration_ms}|{observed}|{shot}", flush=True)
```

`flush=True` matters: a buffered line is a lost line when the process dies.

Capture for every case, passed ones included, because the report cannot be reconstructed
afterwards: the id, what the case did, what it expected, what was actually observed, the
status, how many attempts it took, the duration, and the screenshot path when there is one.

### Exploring first, once

For any case that touches a form, a dialog or a dynamic widget, run **one** exploration
script before the real one: it walks the whole path and prints an accessibility snapshot
(`page.locator("body").aria_snapshot()`) after each step. Pick every locator from those
snapshots. One replay beats a scratch script per element, and it uses the same storage
state as the run. Skip it for plain navigation and read-only checks.

### Signing in

With a scripted login (see [auth.md](auth.md)), call the profile's helper once per role at
the top of the script, before the first case, and group the cases by role so each role
signs in once. A `LoginBlocked` marks that role's cases `BLOCKED` with its message, and
the cases for other roles still run.

### Finding elements

Use the accessible name — role plus visible label — as the locator. Never a CSS path
scraped from devtools, never an nth-child chain, never a generated class name: those break
on the next styling change and produce failures that are about the test, not the product.

Before acting on an unfamiliar page, take an accessibility snapshot and pick the locator
from what is actually there. A guessed selector that misses is reported as `BLOCKED`, not
`FAILED` — the product may be fine and the test wrong, and those must not look alike.

### Waiting

Wait for the state the case is about: the element visible, the request settled, the text
present. Never a bare sleep. A fixed delay is either slower than needed or shorter than
reality, usually both on different machines.

### Large runs

A library run can hold dozens of cases. Run them in batches of about ten per script
invocation, each batch a fresh context on the same storage state, and run Python unbuffered
(`-u`) so each `CASE|` line arrives as it finishes. Keep a running tally from the lines
you have parsed; never recompute it from a half-written log. Batching limits what is lost
when one invocation dies; it does not change results.

A case missing from the log because the script exited first is `BLOCKED`, reason "script
exited before this case ran" — never silently dropped.

### Retries

Retry a failing case up to three times, with a short wait between. Take the screenshot on
the **final** attempt only. Record the attempt count: a case that passes on attempt three
is flaky and that number is the only trace of it.

A case that fails all three attempts is `FAILED`, with the observed state in one plain
sentence — "the dialog never appeared; the page still showed the zone list" — not a stack
trace.

Before reporting a `FAILED` or `BLOCKED` case, open its screenshot and confirm the failure
is real. A spinner, a half-loaded page or a toast covering the control is a timing problem:
re-run that one case in a short follow-up script before settling the status.

### Mutating cases

When the run is read-only, skip every case that creates, edits or deletes, and mark it
`SKIPPED (read-only run)`. Do not soften a mutating case into a read-only one; the case as
written is what the spec says must work.

### Browser settings

Headless Chromium, a 1280 × 1800 viewport, no full-page screenshots. With `--headed` the
person wants to watch: launch a visible window with about 250 ms slow-mo and a slightly
longer pause after each page settles, and tell them a window is about to open. Results are
the same either way.

### Waiting for a page to finish

Network quiet is not the end of loading: data often arrives just after. After each
navigation, wait for the network to settle **and** for loading skeletons
(`.animate-pulse`, `[aria-busy=true]`) to disappear, up to about 20 seconds. A page still
showing skeletons after that is reported as it is — and re-checked once, recording failed
API calls, before anyone calls it a bug.

Error detection matches error *phrases* ("something went wrong", "page not found",
"forbidden"), never bare status numbers: a "404" in a street address is not an error. Prefix every Python
call with `PYTHONUTF8=1` and open logs with `encoding="utf-8"`, so page text outside ASCII
(Norwegian strings, here) cannot crash the run.

### Secrets

The storage state file is referenced by path and never read into the script's output. Any
field that takes a password, token or key logs as `[REDACTED]`. Screenshots of a signed-in
page can carry personal data: crop or skip rather than attaching one to anything shared.

### When the app is not running

Local runs need the dev server up. Start it, wait for the port to answer, and stop it at
the end if this skill started it. If the port is already busy, use it — do not start a
second one.
