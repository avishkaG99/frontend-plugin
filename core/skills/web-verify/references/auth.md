---
slug: resolve-auth
phase: verification
lead_agent: fe-e2e
gate: stops the run when no usable session resolves
consumes:
  - role (from the case, or the person)
  - storage-state-path (profile)
produces:
  - storage-state (a path, never its contents)
  - role-used (named in every report)
title: Signing in
tags: auth, storage-state, sso, roles, secrets
---

## Signing in

Most screens worth verifying sit behind a login, so authentication is the part that decides
whether browser verification is usable at all.

Two ways, and the profile says which one this project uses:

- **Scripted login through a helper the profile names** — when the app keeps its tokens
  where a saved browser state cannot reach them (`sessionStorage`), or when sessions
  expire too fast to keep. See "Scripted login" below.
- **A saved storage state** — everywhere else. See the next section.

### Scripted login

The profile's login helper signs the run's page in once, at the start, as the role the
cases need; every case then runs in that same page. Credentials live in a local file
outside every repo, filled in by the person, and only the helper reads it.

- **Never open, print, search, copy or edit the credentials file**, and never ask for a
  password in chat. A hook blocks the ordinary ways of reading it; the rule holds anyway.
  To see which roles are ready, use the helper's list command.
- **One sign-in per run, one attempt.** A rejected password, a one-time-code prompt or a
  federated account stops the run with `BLOCKED` and the helper's reason. Never retry a
  rejected password: test accounts lock.
- **Never screenshot the sign-in pages.** Screenshots start after the helper returns.
- **Local only.** The helper refuses any URL that is not the local dev server.
- A role whose password is missing is `BLOCKED — <role> not set up`, and the person fills
  it in. Cases for other roles still run.

### Storage state, not a scripted login

Log in **once**, by hand, and save the resulting browser state (cookies plus local storage)
to a file. Every later run loads that file and starts already signed in.

```bash
# once, and again whenever it expires
python3 -m playwright open --save-storage=.auth/<role>.json <app-url>
```

Scripting a login through an identity provider on every run is the classic mistake: the
provider changes its markup, adds a consent screen, asks for a second factor, or rate-limits
you, and every case fails for a reason that has nothing to do with the change under test.

### Where the file lives

Outside the repo, or in a path the repo ignores. **Never commit it** — it is a live
session. Treat it exactly like a password: never printed, never pasted into a report,
never attached to a ticket. The profile records the path; the content stays on the machine.

### When it expires

A run that lands on the sign-in page has an expired state. Report that plainly as
`BLOCKED — session expired`, and ask the person to refresh it. Do not attempt to log in
with credentials found anywhere, and do not ask the person for a password: they refresh the
file themselves with the command above.

### Roles

A case that says "a viewer cannot see the Add button" needs a viewer's session, so keep one
storage state per role that matters and name it after the role. A run states which role it
used; a role mismatch invalidates every permission case in it.

### Single sign-on and tenants

With SSO, the saved state usually covers the identity provider too, which is why it keeps
working. Where the app scopes data by tenant or organisation, the state also carries that
choice — so a case about a different tenant needs its own file, not a switcher click at
the start of every run.

### Never run destructive cases with a real person's account

If the only available session belongs to a real user, the run is read-only. A test that
deletes something is only acceptable against a disposable account and a disposable
environment.
