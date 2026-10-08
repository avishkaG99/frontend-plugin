# Project profile — <project name>

Fill this in once per project and keep it short. `scripts/sync.py` injects it into both
skills, so everything here is what the agents treat as fact about *this* codebase.

Anything you cannot answer yet: delete the line rather than guessing. A wrong fact here is
worse than a missing one, because the agents will not question it.

---

## Repos

| Repo | Holds |
| --- | --- |
| `<web-repo>` | the React app |

Is the directory you open the editor in itself a git repo? `<yes / no — commands must cd>`

## The app

| Thing | This project |
| --- | --- |
| Build / dev | `<vite / next / cra>` |
| Router | `<tanstack-router / react-router / file routes>` |
| Server state | `<tanstack-query / rtk-query / swr>` |
| Client state | `<redux-toolkit / zustand / context>` |
| HTTP | `<axios instance path / fetch wrapper>` |
| Styling | `<tailwind + shadcn/ui / css modules / mui>` |
| i18n | `<react-i18next + locale files, or none>` |
| Tests | `<vitest + testing-library / jest>` |

## Where code goes

```
<paste the src/ layout, one line per directory, with what belongs in each>
```

## Standards

Where the written rules live, and the two or three a change is most often checked against:

- Index: `<path to the spec index, e.g. React-Specs/SPEC-LIST.md>`
- Definition of Done: `<path>`
- Testing strategy: `<path>`
- PR checklist: `<path>`

Feature specs live in: `<path, e.g. React-Specs/features/>`

## Commands

Run from `<the app directory>`:

```bash
<lint command>
<typecheck command>        # note any trap: does it cover test files too?
<single-area test command>
<full test command>        # roughly how long?
```

## Git

| Thing | This project |
| --- | --- |
| Base branch | `<develop / main>` |
| Remote | `<org/repo>` |
| Branch names | `<pattern, e.g. feat/ar-123-slug>` |
| Ticket keys | `<prefix, e.g. AR- ; or none>` |

## Browser verification

| Thing | This project |
| --- | --- |
| Dev server | `<command>`, `<url>` |
| Depends on | `<a backend that must also run, or none>` |
| Sign-in | `<provider, and whether a scripted login is viable>` |
| Storage state | `<gitignored path, e.g. .auth/<role>.json>` |
| Roles worth keeping | `<the roles whose views actually differ>` |
| Mutations | `<where data may be changed, and where it may never be>` |

Delete this section when browser verification is not set up — the agents will then say a
case cannot be checked rather than inventing a URL.

## Test-case library

<!-- Where the regression library lives, one file per area. Delete this section if the
project has none. -->

| Area file | Prefix |
| --- | --- |
| `<area>.md` | `<ABC>` |

Ownership map for `--impacted`: `<library>/areas.json` (see `scripts/test_library.py`).
Library script: `python3 frontend-plugin/scripts/test_library.py --app <app> --library <library> check|select|impacted`

Run reports (library runs only): `<local folder, outside the repo>`

## Traps

The things a competent newcomer gets wrong here. Two or three lines each, with the reason.

- `<e.g. i18n keys must not contain ':' — i18next reads it as a namespace separator and the
  string silently renders wrong>`
- `<e.g. canvas/WebGL components cannot mount under jsdom — test the logic beside them>`
- `<e.g. the typecheck script covers test files; tsc -b alone does not>`
