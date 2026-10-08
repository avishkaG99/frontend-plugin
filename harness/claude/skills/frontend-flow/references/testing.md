---
title: Tests that pass for the right reason
tags: tests, mocks, levels, behaviour, jsdom, coverage
---

## Tests that pass for the right reason

Which runner, which environment and which traps apply are in the profile. What to test at
which level is the project's testing-strategy document. This file is the craft.

The nearest existing test to your change is the best template — copy its shape.

### Test behaviour, not wiring

Assert what a user or a caller would notice: what renders, what request goes out, what the
function returns, what happens on failure. A test that asserts an internal function was
called with particular arguments breaks on every refactor and proves nothing.

Name the test as the behaviour, not the mechanism:
`'redirects to sign-in instead of logging out on 401'`, not `'handles 401'`.

### The test must be able to fail

A new test that passes with the change reverted is noise. Check it: revert mentally, or
actually, and ask what would break. This is the single most common defect in generated
tests.

### Mocking

- Mock at the **module boundary** you own, not deep inside a library.
- Reset mocks between tests. A leaked mock makes a later test pass for the wrong reason.
- Mock config and environment rather than depending on real local files.
- A module with top-level state — locks, single-flight promises, caches — needs a fresh
  import per test, or one test decides the next one's result.
- Prefer a real collaborator over a mock when it is cheap and deterministic. Every mock is
  an assumption about how the real thing behaves.

### Async and time

Wait for the settled result rather than sleeping a fixed number of milliseconds. Assert on
the outcome, not an intermediate render — unless the intermediate state *is* the behaviour,
like a loading gate. Restore faked timers in the same test that fakes them.

### Levels

Push each test as low as it will go and still prove the thing: pure logic as a unit test,
a feature's flow as an integration test, and only the critical paths end to end. A test at
too high a level is slow and flaky; one at too low a level proves the wrong thing.

Some things cannot run in a headless DOM at all — canvas, real navigation, layout
measurement, network. The profile lists the project's cases. Test the logic beside them and
say plainly in the spec what is only checkable by hand.

### When you cannot test it

Write that in the spec's log, with the reason. That is honest and useful. A test written to
raise the count, which would pass either way, is worse than no test.
