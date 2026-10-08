# Project profile — areaSim

## Repos

| Repo | Holds |
| --- | --- |
| `areasim-webapp` | the React app — this flow's scope |
| `areasim-backend` | .NET API — out of scope, name it as a dependency |

The project root is **not** a git repo. Every git command runs inside one of the two, or
uses `git -C <repo>`.

## The app

| Thing | This project |
| --- | --- |
| Build / dev | Vite (`@vitejs/plugin-react`) |
| Router | TanStack Router, file routes, generated `routeTree.gen.ts` |
| Server state | TanStack Query |
| Client state | Redux Toolkit (`src/store`) |
| HTTP | one Axios instance, `src/lib/api/http-client.ts` |
| Styling | Tailwind + shadcn/ui (`src/components/ui`) |
| i18n | react-i18next via `useAppI18n()`, `src/locales/{en-US,nb-NO}.json` |
| Tests | Vitest + Testing Library, jsdom, setup in `src/test/setup.ts` |

## Where code goes

```
src/routes/            TanStack file routes; `-` prefixed files are NOT routes
  _authenticated/      guarded area (-authenticated-before-load.ts, -authenticated-route.tsx)
src/features/<area>/   the feature's own components/, hooks/, lib/, schema/
src/components/        shared: ui/, layout/, dropdowns/, loaders/
src/hooks/api/         one file per API area, exporting TanStack Query hooks
src/lib/api/services/  Axios calls; hooks wrap these, components never call them directly
src/lib/               auth, router, i18n, config, utils — no feature imports
src/types/             shared API and domain types
src/locales/           en-US.json, nb-NO.json — always updated together
```

Data flows component → query hook → service → `httpClient`. `httpClient` already handles
auth headers, the tenant header, 401 recovery and the network error page: never add a
second Axios instance or re-implement any of that.

A file used by one feature lives in that feature. It moves to `src/components/` or
`src/lib/` when a second feature needs it, not in anticipation.

## Standards

All under `areasim-webapp/React-Specs/`:

- Index, including the fixed stack decisions: `React-Specs/SPEC-LIST.md`
- Definition of Done: `React-Specs/quality-ops/definition-of-done-spec.md`
- Testing strategy: `React-Specs/quality-ops/testing-strategy-spec.md`
- PR checklist: `React-Specs/quality-ops/pr-review-checklist-spec.md`
- Architecture: `React-Specs/architecture/` · Data: `React-Specs/data/` ·
  UI and UX: `React-Specs/ui-ux/` · Security: `React-Specs/quality-ops/security-spec.md`
  and `React-Specs/ImplementationSpec.md`

Design system — what every screen is built from (read before any UI step):

- `React-Specs/ui-ux/design-system.md` — primitives, patterns, page recipes, do/don't
- `React-Specs/ui-ux/styling-spec.md` §2.1 — the palette and its usage rules
- `src/styles/globals.css` — tokens and shell classes (`.page-container`,
  `.surface-card`, `.admin-table-panel`), the source of truth
- `/design-system` in the running app — the living catalog, to compare a screenshot
  against
- Loading, empty and error states: `React-Specs/ui-ux/error-handling-user-feedback-spec.md`

The cream page background, teal primary and white rounded cards are the brand. Never
"fix" them toward a more distinctive look in feature work.

Feature specs live in: `areasim-webapp/React-Specs/features/`
Template: `React-Specs/feature-spec-template.md`

## Commands

Run from `areasim-webapp/`:

```bash
npm run lint
npm run typecheck          # tsc -b AND tsconfig.test.json — test-only type errors surface
npx vitest run src/lib/auth  # one area, while iterating
npm run test               # whole suite, ~4 minutes, 750+ files
```

## Git

| Thing | This project |
| --- | --- |
| Base branch | `develop` (not `main`) |
| Remote | `AreaSim-AS/areasim-webapp`, `AreaSim-AS/areasim-backend` |
| Branch names | `feat/ar-720-utilization-dashboard-charts`, `fix/ar-724-project-module-fixes` |
| Ticket keys | `AR-` — the key belongs **in the branch name**, the jira flow reads it from there |

## Browser verification

Local only. There is no PR-driven or CI browser suite, and no Playwright in
`areasim-webapp/package.json` — runs use Python `playwright` as a harness beside the app,
so the repo gains no dependency.

| Thing | This project |
| --- | --- |
| Dev server | `npm run dev` in `areasim-webapp/`, `http://localhost:3000` |
| API it talks to | `http://localhost:8080/api/v1` — the backend must be running too |
| Sign-in | Microsoft Entra. Scripted login is not viable; save a storage state once and reuse it |
| Storage state | `areasim-webapp/.auth/<role>.json` — gitignored, never printed, never committed |
| Roles worth keeping | `super-admin` (admin portal), `tenant-admin` (normal org user), `external-architect` (invited, external grants) |
| Mutations | allowed against local dev only. Never against the Azure Static Web App or a real tenant |

Which account signs in for each role is chosen at capture time and deliberately not written
down here — this plugin may be published, and a test account in a public repo is an
invitation. The role name is the contract; the session file behind it is local.

Capture or refresh a session — the person signs in, the agent never sees a credential:

```bash
python3 frontend-plugin/scripts/capture_auth.py tenant-admin
python3 frontend-plugin/scripts/capture_auth.py --list     # what exists, and how old
```

It installs Chromium on first use and adds `.auth/` to `areasim-webapp/.gitignore`.

The Playwright runtime lives in `frontend-plugin/.venv` (gitignored), so the app's
`package.json` and your system Python both stay untouched. Scripts run as
`frontend-plugin/.venv/bin/python`, never a bare `python3` and never `npx playwright`.

## Test-case library

Use cases and regression test cases, one Markdown file per area, in
`areasim-webapp/React-Specs/test-cases/` (format and rules: its `README.md`). Committed
with the code; results are not.

| Area file | Prefix | Owns (for `--impacted`) |
| --- | --- | --- |
| `projects.md` | `PRJ` | `src/features/projects/` except `project-surveys/`, `src/routes/_authenticated/{project,projects,utilization-canvas}/` |
| `surveys.md` | `SUR` | `src/features/projects/project-surveys/`, `src/features/{public-survey,organization-survey-templates}/`, `src/routes/_authenticated/surveys/`, `src/routes/survey.$token.tsx` |
| `subscription.md` | `SUB` | `src/features/{subscription,pricing}/`, `src/routes/_authenticated/subscription/` |
| `onboarding.md` | `ONB` | `src/features/{onboarding,welcome}/`, `src/routes/_authenticated/{onboarding,welcome,create-organization}/` |
| `organization.md` | `ORG` | `src/features/{organization-structure,organizations,organization-switcher}/`, `src/routes/_authenticated/organization/` |
| `super-admin.md` | `ADM` | `src/features/admin/`, `src/routes/_authenticated/admin/` |
| `platform.md` | `PLT` | `src/features/{auth,authorization,dashboard,errors}/`, `src/routes/{(auth),(public)}/`, `src/components/layout/`, `src/lib/{auth,api}/` |

A change under `src/components/`, `src/hooks/` or `src/lib/` outside those paths is shared:
`--impacted` takes the areas whose code imports the changed file, and says so.

Run reports (library runs only): `docs/test-runs/` in the workspace root — local, not in
any repo.

## Traps

- **No `:` in an i18n key.** i18next reads it as a namespace separator, so the string
  silently renders wrong. Put the colon in the value instead.
- **Konva / canvas does not mount under jsdom.** Test the logic beside it
  (`canvas-pointer.ts`, hooks, geometry), never the canvas component.
- **`npm run typecheck`, not `tsc -b`.** Only the script covers `tsconfig.test.json`, so
  `tsc -b` alone misses type errors in tests.
- **Radix needs the pointer-capture and `scrollIntoView` stubs** already in
  `src/test/setup.ts`. That is why a Select or Dialog opens under jsdom at all.
- **Never hand-edit `routeTree.gen.ts`.** Add the route file, then `npm run router:generate`
  (which `typecheck` and `build` already run).
- **No `use client`.** ESLint rejects it: this is a Vite SPA with no RSC boundary.
- **A module with top-level state** (locks, single-flight promises, caches) needs
  `vi.resetModules()` and a per-test re-import, or one test decides the next one's result.
