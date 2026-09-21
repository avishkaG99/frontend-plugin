---
title: Frontend security review
tags: security, xss, tokens, auth, secrets, csp, dependencies, privacy
---

## Frontend security review

What a browser app can get wrong, in the order it usually gets it wrong. The project's own
security standard wins where it says something different; this is the checklist for a
change, not a policy.

### The rule behind all of it

**The client enforces nothing.** Hidden buttons, disabled inputs, client-side guards and
filtered lists are user experience, not access control — anyone can call the API directly.
Every check in the UI must have a matching one on the server. When you cannot find the
server-side check, say so; that is a finding, not an assumption.

### Injection

- `dangerouslySetInnerHTML` (or the framework's equivalent) needs a reason and sanitised
  input. Untrusted HTML rendered this way is XSS, full stop.
- Never build a URL, a redirect target or a `href` from user input without validating it
  against an allow-list. `javascript:` URLs execute; open redirects hand off sessions.
- Anything reaching `eval`, `new Function`, `setTimeout(string)` or a template compiler is
  a finding.
- Rendering Markdown or SVG from users means sanitising it.

### Tokens and session

- Where does the token live, and why? Storage that survives a tab is readable by any script
  that gets injected; storage scoped to the tab limits the blast radius. Either way, never
  put a token in a URL, a log line, or an analytics payload.
- Logout clears every local trace — caches, stores, in-memory user state — not just the
  token.
- Session-expiry handling should recover or re-authenticate, not strand the user or loop.
- Never log or display a token, an id token's claims, a password, or an API key.

### Secrets and the bundle

Everything shipped to the browser is public. Config that the build inlines — anything with
a public prefix — is readable by any visitor. A secret in there is a leaked secret, and
rotating it is the only fix. Check that new config is genuinely public.

### Data exposure

- Errors shown to users say what happened, never the stack, the query, the internal id or
  the upstream body.
- Logs and telemetry must not carry personal data, tokens or full request bodies.
- Do not fetch more than the view needs. A list endpoint returning whole user records
  leaks through the network tab even when the UI renders two fields.

### Cross-origin and framing

Requests go to the project's own API origin; a new third-party origin is a decision, not a
detail. Check CORS assumptions, and keep whatever framing protection the app already sets —
removing it enables clickjacking.

### Dependencies

A new package is new code with your privileges. Do not add one to save a few lines. When
one is genuinely needed, say who maintains it, how widely it is used, and what it pulls in.

### Files and uploads

Validate type and size before upload, and never trust a filename: it can contain a path.
Render user-supplied files in a way that cannot execute — no inline SVG from an upload.

### Reporting a finding

Say what an attacker does, in one concrete sentence, then the fix. "Untrusted HTML rendered
at `comment-body.tsx:41`: a comment containing `<img onerror=…>` runs script for every
reader" beats "possible XSS risk".
