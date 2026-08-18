# power-apps-fun — Claude Code working notes

Mariano Gomez Bent's monorepo of fun Power Platform side projects
(github.com/dgpblogster/power-apps-fun, account `dgpblogster`). Each top-level folder is a
self-contained project; the root README documents them and carries the clone/deploy
instructions. Built 2026-08-18 with Claude Code following Microsoft's power-platform-skills
repo guidance (github.com/microsoft/power-platform-skills).

## Projects

### parametric-motions/

Canvas app **Parametric Motions**: four parametric curves (Lissajous, Rose, Spiral,
Hypotrochoid), each on its own screen where a small circle traces the curve leaving an
SVG trail, with live parameter sliders, tracer speed, pause/restart, and a hamburger
menu for navigation. Based on Mariano's 2019 The Workbench post "PowerApps Motion
Patterns with Parametric Equations".

**Deployment facts**
- Environment: **Workbench**, id `e57d0c49-8edb-e5a5-af15-8a62479e341a`
  (https://org4b699c21.crm.dynamics.com). pac auth profile: `PckWorkbench`
  (marianog@maximumglobal.biz). `pac auth select --name PckWorkbench` before anything.
- Unmanaged solution **ParametricMotions**, publisher **Workbench** (prefix `wrk`,
  option prefix 68000; already exists in the env).
- Canvas app logical name `wrk_parametricmotions_b1e07`,
  canvasappid `056a3d7b-1553-4ba6-9397-913195b0d5ff`, display name "Parametric Motions".
- App is published; local `canvas/Src` + `canvas/base` were synced FROM the published
  version on 2026-08-18 (includes Mariano's Studio layout fixes).

**Layout**
- `canvas/Src/*.pa.yaml` — source of truth (Power Apps YAML v3 "Source Code" schema).
  `_EditorState.pa.yaml` is Studio-owned; sync it on pull, never hand-edit.
- `canvas/base/` — non-YAML msapp scaffolding (msapr-header.json + msapp/*), refreshed
  from the Studio-saved app.
- `solution/src/` — SolutionPackager format (Other/Solution.xml + CanvasApps meta.xml +
  background PNG). The `_DocumentUri.msapp` there is overwritten by each build.
- `tools/add-menu.ps1` — generates the hamburger-menu control block for a screen.
- `build.ps1` — build; `build.ps1 -Import` also imports + publishes to the environment.

**Round-trip workflow**
- Local edit: change `canvas/Src`, run `.\build.ps1 -Import`, then open the app FOR EDIT
  in Studio once (YAML-packed apps validate on first open), Save, Publish.
- Studio edit: Mariano edits in Studio and must **Publish** (Save is not enough), then
  pull with `pac canvas download --name "Parametric Motions"` +
  `pac canvas unpack --layout SourceCode`, copy `Src/*.pa.yaml` over `canvas/Src/` and
  unzip the `.msapr` over `canvas/base/`. `pac canvas download` only ever returns the
  PUBLISHED document.

## pa.yaml / pac pipeline traps (all hit and solved on 2026-08-18)

- `pac canvas pack --layout SourceCode` sources dir must contain exactly one `*.msapr`
  (zip of msapr-header.json + msapp/<non-YAML files>) plus `Src/*.pa.yaml`. pac 2.10/2.11
  has a bug: when ValidateSources wants to report an error (e.g. missing msapr) it
  crashes with System.FormatException, masking the real cause.
- Studio only accepts v3 Source Code schema: screens are `Screens:\n  <Name>:` (no
  `Control: Screen`), App.pa.yaml is `App:\n  Properties:` (no `Control: App`, no Host).
- Classic controls: `Label`, `Timer`, `Circle`, `Rectangle`, `Image` are bare names, but
  `Classic/Button`, `Classic/Slider`, `Classic/Icon` need the prefix; bare `Button`/
  `Slider` bind the modern Fluent controls and all classic properties fail with PA2108.
- Any single-line formula containing `: ` (especially `UpdateContext({x: 1})`) must be
  single-quoted at the YAML level or written as a `|-` block.
- Solution pack requires the `_BackgroundImageUri` composite file next to the msapp or
  it fails with "Missing composite reference".
- Validate YAML locally against PowerApps-Tooling `schemas/pa-yaml/v3.0/pa.schema.yaml`
  (its CodeComponent-ComponentName regex has an unbalanced paren; patch before compiling
  with ajv). `pac org fetch --xml "<fetch>..."` is the quick Dataverse query tool.

## Session-recovery state (as of 2026-08-18)

- Repo is **PRIVATE**. Make public before the blog update goes live (the post links it):
  `gh repo edit dgpblogster/power-apps-fun --visibility public --accept-visibility-change-consequences`
- Blog update to the 2019 post is STAGED in `C:\AL\Blog-Modernization` (separate
  workspace, own CLAUDE.md + hard rules; never publish, Mariano's click):
  `motion-patterns-update-2026.html` (addendum in Mariano's voice),
  `motion-patterns-preview.html` (full-post preview),
  `apply-motion-patterns-update.ps1` (PATCHes live post id 1558624108369647358; NOT run),
  `backups\motion-patterns-post-backup-20260818.json` (rollback copy).
- `C:\AL\power-apps-parametric-motions` is an empty leftover folder from the monorepo
  move (VS Code lock prevented rename); safe to delete.
- Claude memory files also live at
  `%USERPROFILE%\.claude\projects\c--AL-power-apps-fun\memory\`.

## House rules

- Publisher for solutions here is **Workbench** (`wrk`).
- Canvas Authoring MCP (coauthoring) needs a live Studio tab + interactive OAuth; in
  non-interactive sessions use the pac pipeline above instead.
- Blog anything: follow `C:\AL\Blog-Modernization\CLAUDE.md` + `voice-profile.md`
  (no em dashes, drafts only, never mention Mekorma, exact sign-off).
