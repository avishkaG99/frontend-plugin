# Install

## 1. Write a profile

```bash
cp core/profile.template.md profiles/<name>.md
```

Fill it in: repos, stack, where code goes, standards, the exact lint / typecheck / test
commands, base branch, ticket keys, browser verification, test-case library areas, traps.
Delete any line you cannot answer — the agents treat every line as fact.

## 2. Install into the project

### From this checkout (recommended)

```bash
python3 scripts/sync.py --profile <name> --install /path/to/project
```

Writes `.claude/skills/`, `.claude/agents/`, `.claude/commands/`, `.claude/hooks/` and
`.cursor/rules/` into that project, and merges the two hooks (`SessionStart`,
`PreToolUse`) into its `.claude/settings.json` once, leaving the rest alone. Restart the
editor afterwards so everything loads. Re-run the same command after any change to
`core/`, `profiles/` or `vendor/`.

### As a Claude Code plugin

`harness/claude/` is committed and is the plugin's install source. In the target project's
`.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "areasim": { "source": { "source": "github", "repo": "<you>/frontend-plugin" } }
  },
  "enabledPlugins": { "frontend-flow@areasim": true }
}
```

Or, where `/plugin` exists:

```
/plugin marketplace add <you>/frontend-plugin
/plugin install frontend-flow@areasim
```

Installed this way, the skills, agents, commands and hooks load from the plugin — do not
also copy them into `.claude/`, or you get a second copy that drifts. The published
`harness/` is built from one profile; for several projects, publish a branch or tag per
profile, or use `sync.py --install` per project.

### Cursor

`sync.py --install` writes into `.cursor/`:

- `rules/` — one rule per skill (`frontend-flow`, `git-flow`, `web-verify`,
  `frontend-design`), each carrying its skill and every reference inline.
- `agents/` — the eight `fe-*` agents as Cursor subagents (`model: inherit`).
- `commands/` — the commands as flat files: `/fe:run` in Claude Code is `/fe-run` in
  Cursor, `/git:commit` is `/git-commit`, and so on.

Each generated agent and command opens with a short note mapping "skill" and "agent" to
the Cursor files. The two hooks (Flow status on start-up, the secrets guard) stay Claude
Code only.

## 3. Browser verification (optional)

Playwright runs from a virtual environment inside this checkout, so neither the app nor
your system Python gains a dependency:

```bash
python3 -m venv .venv
.venv/bin/pip install playwright
.venv/bin/python -m playwright install chromium
```

Then, depending on how the profile says the app signs in:

- **Scripted login** — create the accounts file and let the person fill it in:
  `~/.config/frontend-flow/<profile>/test-accounts.env`, one `<ROLE>_EMAIL` and
  `<ROLE>_PASSWORD` pair per role (`ORG_ADMIN_EMAIL`, `ORG_ADMIN_PASSWORD`, …), mode `600`.
  `.venv/bin/python scripts/login.py --edit` opens it; `--list` shows which roles are
  ready; `login.py <role> --headed` tries one sign-in.
- **Saved storage state** — `.venv/bin/python scripts/capture_auth.py <role>` opens a
  browser; sign in; the session is saved under the app's gitignored `.auth/`.

Use test accounts only, against local dev only.

## 4. Check it took

In Claude Code: `/fe:run` appears in the command list and `frontend-flow` in the skill
list. A new session prints nothing until a feature is in progress. Then:

```
/fe:run "something small"
```

It should write a spec with a `## Flow status` block, ask its questions, and stop for your
approval.
