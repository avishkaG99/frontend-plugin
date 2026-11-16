# AreaSim web tester — setup for a new teammate (frontend only)

This gets you from nothing to running AreaSim's browser test cases on your own machine.
You run only the React app locally; it talks to a shared backend.

You do **not** need the .NET backend, a database or Docker.

Plan for about 30 minutes, most of it waiting for installs.

---

## Before you start: get these from Avishka

| You need | Why |
|---|---|
| Access to the GitHub repo `avishkaG99/frontend-plugin` (private) | It holds the test tooling and the agents |
| Access to `AreaSim-AS/areasim-webapp` | The app itself |
| The shared backend URL — `VITE_API_BASE_URL` | The app has no data without it |
| A copy of a working `.env.local` (no secrets in it, only client IDs and URLs) | Entra sign-in settings for the dev tenant |
| Your own test accounts in the Entra dev tenant, one per role you will test | Sign-in for the tester. Never share accounts — a wrong password can lock them for everyone |
| Whether test runs may **change data** on the shared backend | Decides which cases you are allowed to run (see step 6) |

You also need: Git, Node.js (the version in `areasim-webapp/.nvmrc`), Python 3.10 or newer, and Claude Code (or Cursor).

---

## 1. Lay out the workspace

The tooling expects both repos side by side in one folder:

```bash
mkdir areaSim && cd areaSim
git clone https://github.com/AreaSim-AS/areasim-webapp.git
git clone https://github.com/avishkaG99/frontend-plugin.git
```

```
areaSim/
├── areasim-webapp/     the React app
└── frontend-plugin/    the test tooling and agents
```

All later commands run from `areaSim/` unless a step says otherwise.

## 2. Run the app

```bash
cd areasim-webapp
npm install
cp .env.example .env.local
```

Edit `.env.local` with the values you got from Avishka. The one that matters most:

```
VITE_API_BASE_URL=<shared backend URL>/api/v1
```

Then start it:

```bash
npm run dev
```

Open http://localhost:3000 and sign in by hand once with one of your test accounts. If you
see your dashboard with data, the app and the backend are talking. If every request fails,
the backend may not allow `http://localhost:3000` (CORS) — tell Avishka.

Leave `npm run dev` running and open a new terminal in `areaSim/`.

## 3. Install the tooling into the workspace

```bash
python3 frontend-plugin/scripts/sync.py --profile areasim --install .
```

This writes the agents, commands and skills into `areaSim/.claude/` (and `.cursor/`).
Restart Claude Code or Cursor afterwards.

## 4. Install Playwright (once)

Playwright lives in a private Python environment inside `frontend-plugin/`. Nothing is
added to the app or to your system Python.

```bash
cd frontend-plugin
python3 -m venv .venv
.venv/bin/pip install playwright
.venv/bin/python -m playwright install chromium
cd ..
```

## 5. Add your test accounts

```bash
frontend-plugin/.venv/bin/python frontend-plugin/scripts/login.py --edit
```

This opens `~/.config/frontend-flow/areasim/test-accounts.env` (outside every repo). Fill
in one pair per role you have an account for:

```
ORG_ADMIN_EMAIL=...
ORG_ADMIN_PASSWORD=...
ORG_MEMBER_EMAIL=...
ORG_MEMBER_PASSWORD=...
```

Role names: `SUPER_ADMIN`, `ORG_ADMIN`, `ORG_MANAGER`, `ORG_MEMBER`, `ARCHITECT`,
`LANDLORD`, `ORG2_ADMIN`, `ORG2_MANAGER`. You only need the roles you will test.

Check and try one:

```bash
frontend-plugin/.venv/bin/python frontend-plugin/scripts/login.py --list
frontend-plugin/.venv/bin/python frontend-plugin/scripts/login.py org-admin --headed
```

`--list` shows only role names and `ready` / `missing password` — never an email or password. The
second command opens a browser, signs in and reports where it landed.

The script stops instead of retrying on a wrong password (so the account does not lock),
stops at any one-time-code or MFA prompt (use accounts without MFA), and refuses to run
against anything but `localhost`.

## 6. Run test cases

From `areaSim/`, in Claude Code:

| You want | Type |
|---|---|
| One or more cases | `/fe:e2e TC-PRJ-106` |
| One area | `/fe:e2e --area projects` |
| What your branch touches | `/fe:e2e --impacted` |
| Something specific | "check the utilization heat map in the browser as org-admin" |

A Chromium window opens so you can watch. Ask for headless if you want it in the
background.

The cases live in `areasim-webapp/React-Specs/test-cases/` (`projects.md`, `surveys.md`,
`subscription.md`, …). Each names its role and the data it expects (for example the
project `Test 1` with finished counting).

**On a shared backend, everyone sees what you change.** Unless Avishka has said that data
changes are fine on it, run only cases that look and do not touch: viewing pages, charts,
reports, and permission checks. Skip cases that create, edit, delete, invite, count or
pay.

## 7. Where results go

- Everyday runs: `areaSim/docs/test-runs/` — local, not in any repo.
- A feature's final run before its PR, or a full area: the run report in
  `areasim-webapp/React-Specs/test-cases/runs/<ticket>.md`, committed with the work.

---

## When something goes wrong

| Symptom | Likely cause |
|---|---|
| `login.py --list` shows `missing password` | That role's pair is not in the accounts file, or the key is misspelt |
| Sign-in stops with "blocked" | Wrong password, or the account asks for a code. Fix it by hand in a normal browser first |
| App loads but every list is empty or errors | `VITE_API_BASE_URL` wrong, backend down, or CORS. Check the browser's Network tab |
| A case fails on "Test 1 not found" | The shared backend does not have that data. Tell Avishka rather than creating it |
| `/fe:e2e` is not in Claude Code | Step 3 not run from `areaSim/`, or Claude Code not restarted |
| `ModuleNotFoundError: playwright` | Running a bare `python3` instead of `frontend-plugin/.venv/bin/python` |

Never paste a password into Claude Code or a chat. The tooling never needs it; only
`login.py` reads the accounts file.
