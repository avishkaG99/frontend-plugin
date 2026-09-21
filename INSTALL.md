# Install

## Claude Code, from this checkout

```bash
python3 scripts/sync.py --profile areasim --install /path/to/project
```

Writes `.claude/skills/`, `.claude/agents/`, `.claude/commands/` and `.cursor/rules/` into
that project. Restart the editor afterwards so they load.

## Claude Code, as a plugin

Push this repo to GitHub, then in the target project's `.claude/settings.json`:

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

Installed this way, Claude Code loads the skills, agents and commands straight from the
plugin — do not also copy them into `.claude/`, or you get a second copy that drifts.

**Profiles and the plugin route.** The published `harness/claude/` is built from one
profile. For several projects, either publish a branch or tag per profile, or install with
`sync.py --install` per project.

## Cursor

`sync.py --install` writes `.cursor/rules/frontend-flow.mdc` and `git-flow.mdc`. Cursor has
no subagents, so each rule carries the skill and all of its references inline.

## Check it took

Claude Code: `/fe:spec` should appear in the command list, and `frontend-flow` in the skill
list. Then run `/fe:spec something small` — it should write a spec file and stop.
