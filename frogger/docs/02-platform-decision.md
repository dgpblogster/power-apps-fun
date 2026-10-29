# Platform Decision: Canvas Power App for Frogger

Decided 2026-10-28. Environment: **Workbench** (`e57d0c49-8edb-e5a5-af15-8a62479e341a`), maker
**marianog@maximumglobal.biz**, pac auth profile **PckWorkbench**, publisher Workbench (prefix `wrk`),
solution **Frogger**.

## Decision

**Build Frogger as a canvas Power App, directly in Power Apps Studio, using Power Fx and standard
controls**, the same platform and pipeline as Galaxian Arcade. The constraints are the point of the series.
Code Apps and PCF code components remain documented in the Galaxian decision
([reference/galaxian-platform-decision.md](reference/galaxian-platform-decision.md)) and are not
repeated here; nothing about Frogger changes that comparison.

## Why Frogger is a better fit for canvas than Galaxian was

| Concern | Galaxian | Frogger |
|---|---|---|
| Input | Continuous ship movement and a fire button; canvas has no hold or keyboard events, so a Slider stood in for the joystick | **Five discrete hops.** One tap is one hop. Buttons and tap zones are the natural control, not a compromise |
| Moving objects | 37 aliens sweeping, up to 7 divers and 7 bombs on free paths | At most 45 lane objects moving on fixed loops in straight lines, plus one frog and one snake. Positions are one addition per object per tick |
| Collision | Missile versus 37 slots and divers, bombs versus ship, swept tests | One row at a time: the frog is only ever on one lane, so at most 5 objects are tested per tick |
| Timing precision | Fast missiles needed a swept test at 20 ticks per second | The fastest object (racer, 4.3 columns per tick) is smaller than the frog's hit box; plain overlap works |
| Rendering | 37 flapping alien images re-evaluated per tick | Lane images only change X; sprite frames change every 5 ticks |

The one new cost is **fractional positions**: platforms carry the frog at fractions of a column, so
`ctxFrogX` and lane `X` are decimals, rounded only at render time.

## What the canvas choice means for the design

1. **Tick-based simulation.** One hidden Timer at 50 ms. Speeds in columns per tick as named formulas.
   Movement is stepped; accepted.
2. **Fixed pools, not galleries.** `ctxLanes` is a 45-row table (9 lanes x 5 slots) rebuilt at level
   start and updated per tick with `ForAll` + `Patch` into a context variable. Each slot has its own
   `Image` control whose X, `Visible`, and `Image` are formulas over the row. No gallery.
3. **Sequential tick.** The tick is four `UpdateContext` steps (`sA` scalars, `sL` lanes, `sF` frog, `sC`
   commit). No step references a computed table twice; that rule took Galaxian from 0.5 to 20 ticks per
   second and is non-negotiable.
4. **Bit-strings for small sets.** Home bays are a 5-character "1"/"0" string read with `Mid`.
5. **Input via on-screen controls.** A hop cross beside the playfield, four transparent tap zones placed
   around the frog by formula, and later a focused Text Input for desktop keys. One queued hop so a fast
   tap during a hop is not lost.
6. **Collision by arithmetic** on the frog's row only.
7. **Sound as toggled Audio controls**, added late because media cannot be pushed through YAML.
8. **Original assets only.** Sprites are SVG data-URI named formulas generated from 8-bit bitmaps by
   `tools/sprites.py`, drawn 2:1 for the Atari look. No ROM art, no original tunes.
9. **High score persistence** in a session variable first, a Dataverse table in the Frogger solution later.
10. **Diagnostics from the first build:** the tps label stays on screen until release.

## Control budget

| Group | Controls |
|---|---|
| Playfield bands, bank, sidewalk, grass, time band, border | about 12 Rectangles and Images |
| Lane objects | 45 Images |
| Frog, lady on frog, death sprite, popup, sidewalk snake | 5 Images |
| Bays: five frog-home stamps, five fly or alligator stamps | 10 Images |
| HUD labels: speed, score, 2UP, player-2 score, messages, tps | about 8 Labels |
| Frog icons top-right | 8 Images |
| Input: hop cross 4, tap zones 4, console keys 5, mute | 14 Buttons |
| Timer | 1 |
| Audio (later) | about 11 |

About 120 controls, the same order as Galaxian's 125, which ran at 20 ticks per second once the tick
was sequential.

## Build pipeline

Unchanged from Galaxian and recorded in `CLAUDE.md`:

1. The user creates a blank **Tablet** canvas app in Studio in Workbench, saves it, enables
   **Settings > Updates > Coauthoring**, keeps the tab open in edit mode, and shares the app id.
2. `python tools/gen_app.py` writes `canvas/Src/*.pa.yaml` from `tools/game_logic.py` and
   `tools/sprites.py`.
3. `node tools/mcp-canvas.js tools/calls/compile.json` validates and applies the YAML to the live session
   (`connect` with env `e57d0c49-8edb-e5a5-af15-8a62479e341a`, login hint marianog@maximumglobal.biz).
4. Save in Studio; publish from Studio or the Power Apps API; export and unpack for the repo.
5. Solution: `pac solution init --publisher-name Workbench --publisher-prefix wrk` named Frogger, import,
   then `pac solution add-solution-component --componentType 300` for the app.

## Toolchain

- Power Platform CLI `pac`, profile **PckWorkbench** (verified 2026-10-28: connected to Workbench as
  marianog@maximumglobal.biz, environment id e57d0c49-8edb-e5a5-af15-8a62479e341a).
- Canvas Authoring MCP server via `dnx Microsoft.PowerApps.CanvasAuthoring.McpServer` (.NET 10 SDK),
  driven by `tools/mcp-canvas.js` or the canvas-apps plugin's tools.
- Azure CLI logged into tenant `de15742f-63f5-46b8-a255-8ff07a8577fd` for the publish API.
- GitHub `dgpblogster/power-apps-fun`, folder `frogger/`, PR-only `main`.

## Sources

- Galaxian platform decision and build notes: [reference/galaxian-platform-decision.md](reference/galaxian-platform-decision.md)
- Timer control: https://learn.microsoft.com/power-apps/maker/canvas-apps/controls/control-timer
- Audio and Video controls: https://learn.microsoft.com/power-apps/maker/canvas-apps/controls/control-audio-video
- Gallery best practices: https://learn.microsoft.com/power-apps/maker/canvas-apps/gallery-best-practice
- Canvas-apps plugin: https://github.com/microsoft/power-platform-skills/tree/main/plugins/canvas-apps
