# Platform Decision: Canvas Power App vs. Power Apps Code App

Decided 2026-10-05. Environment: **Workbench** (marianog@maximumglobal.biz).

## Decision

**Build Galaxian as a canvas Power App, directly in Power Apps Studio, using Power Fx and standard controls.**

The user's stated goal is to recreate the game *within* the constraints of canvas apps. The constraints are the point of the project, not an obstacle to route around. Code Apps and PCF code components are documented below only so the trade-off is on record.

## Comparison

| Concern | Canvas Power App | Power Apps Code App |
|---|---|---|
| Language | Power Fx, declarative formulas | TypeScript/JavaScript, React or Vue, Vite |
| Authoring | Power Apps Studio (plus the canvas-apps plugin writing `.pa.yaml` through a coauthoring session) | VS Code, `pa app init / run / push` |
| Game loop | Timer control, `Duration` in ms, `Repeat`, `OnTimerEnd`. Practical floor is roughly 50 to 100 ms per tick (community experience, not documented) | `requestAnimationFrame` at 60 Hz |
| Input | Buttons, touch, pointer position on controls. **No keyboard key events** in canvas apps | Full DOM keyboard, pointer, gamepad events |
| Rendering | Image, Rectangle, Label controls with X/Y bound to variables; galleries over collections | HTML canvas or DOM, pixel-exact sprites |
| Sound | Audio control per effect, `Start` toggled by formula, `Loop` for background hum. Media limit 64 MB per file, 200 MB per app | Web Audio API, synthesize the original tones in code |
| Persistence (high score) | `SaveData`/`LoadData` on mobile player, or a Dataverse table | Dataverse via connector, or browser storage |
| End-user licensing | Standard license is enough when no premium connectors are used | Premium license, pay-as-you-go, or App Pass required for every player |
| Platform maturity | GA, very stable | Newer feature; not supported in Power Apps for Windows; no Git integration yet |
| Faithfulness ceiling | Approximation: coarse tick rate, simplified dive curves, limited simultaneous moving objects | Arcade-faithful is achievable |
| Fun factor for this project | High. "Can it be done?" is the question | Low. It is an ordinary web game that happens to be hosted in Power Platform |

## What the canvas choice means for the design

These constraints shape every section of the game spec.

1. **Tick-based simulation.** One hidden Timer with `Repeat: true` and `AutoStart: true` drives the game. Each `OnTimerEnd` is one tick. Target 10 to 20 ticks per second. All speeds are expressed in pixels per tick, not per frame. Movement will look stepped rather than smooth, which is accepted.
2. **Formation as a fixed grid of controls, not a gallery.** Patching a collection that feeds a gallery can force the gallery to reload all items, which is too slow for a per-tick update. The 46-enemy formation will instead be a fixed set of Image controls whose `Visible`, `X`, `Y`, and `Image` properties are formulas over a small number of global variables (formation offset, animation frame, alive flags). Only the few *diving* enemies and bullets are tracked as individual records.
3. **Few moving objects.** Original Galaxian has at most a handful of divers and three enemy bombs at once, plus one player shot. That cap is a gift: a fixed pool of 3 diver slots, 3 bomb slots, and 1 player shot is enough and keeps per-tick work bounded.
4. **Input via on-screen controls.** Left and right regions of the screen (or two buttons) move the Galaxip; a fire button or a tap on the playfield fires. A Slider control is an alternative for analog-like horizontal movement. Keyboard play is not available in canvas apps and is out of scope.
5. **Collision by arithmetic.** Rectangle overlap tests in Power Fx on each tick, limited to the active pool entries, keep the formula count small.
6. **Alive state as a bitmask or text string.** 46 enemies can be stored in one text string of 46 characters ("1"/"0") or in a small collection with 46 rows that is only patched on a kill, never per tick. Per-tick formulas read it; they do not write it.
7. **Sound as toggled Audio controls.** Each sound effect is an Audio control whose `Start` property follows a boolean variable that the game sets true and immediately false. The background hum is a looping Audio control whose playback rate cannot be changed, so the original "speeds up as enemies die" effect is approximated by swapping between two or three pre-rendered loops.
8. **Original assets only.** Sprites, sounds, and the wordmark will be original homage artwork, not ROM rips. The app will state it is not affiliated with Bandai Namco.
9. **High score persistence.** First version keeps the high score in a variable for the session. A Dataverse table in Workbench can be added later without changing the game loop.

## Build notes from the first build (2026-10-05)

What actually worked, in order:

1. **Seeding the app record.** Workbench had no canvas app to start from and pac cannot create one. A blank
   msapp from Microsoft's PowerApps-Language-Tooling test assets was unpacked with `pac canvas unpack`, given a
   title screen, repacked, and imported inside the Galaxian solution (`CanvasApps/*.meta.xml`, a
   `_BackgroundImageUri` PNG, a type-300 RootComponent, and a `<CanvasApps />` element in Customizations.xml,
   all of which the packager requires). Studio opened it and validated the YAML.
2. **Driving the Canvas Authoring MCP server directly.** The canvas-apps plugin's tools did not load mid-session,
   so a 60-line Node stdio client (`tools/mcp-canvas.js`) speaks JSON-RPC to
   `dnx Microsoft.PowerApps.CanvasAuthoring.McpServer`. `connect` needs the app open in Studio with coauthoring
   on. `compile_canvas` validates and applies the YAML to the live session in one call. `sync_canvas`,
   `describe_control`, `get_appchecker_errors`, and `get_accessibility_errors` complete the loop.
3. **Save and publish.** The hand-packed seed could be edited live but Studio could neither save nor publish
   it. **File > Save as** produced a Studio-native copy, Galaxian Arcade, which saves normally. Publishing works
   from Studio or through `POST https://api.powerapps.com/providers/Microsoft.PowerApps/apps/{appId}/publish?api-version=2017-05-01`
   with a `service.powerapps.com` token from Azure CLI. The copy was added to the solution with
   `pac solution add-solution-component --componentType 300` once Dataverse had synced the new app record,
   and the seed was deleted.
4. **Generator over hand-written YAML.** 125 controls, 37 of them near-identical aliens, plus a tick formula
   of about 300 lines: `tools/gen_app.py` and `tools/game_logic.py` are the source of truth and the YAML is
   build output.

## Build toolchain

- Power Platform CLI (`pac`) 2.12.2, auth profile **PckWorkbench**, environment **Workbench**.
- Microsoft `power-platform-skills` marketplace installed in Claude Code. The **canvas-apps** plugin writes `.pa.yaml` files through the Canvas Authoring MCP server attached to a Studio coauthoring session. Requires the .NET 10 SDK (installed, 10.0.401).
- Workflow: create a blank canvas app in Studio in the Workbench environment, enable **Settings > Updates > Coauthoring**, keep the tab open, run the `configure-canvas-mcp` skill with the Studio URL, then build screens with the `canvas-app` skill.
- Local repo: `C:\AL\Galaxian` holds the spec, research, and the synced `.pa.yaml` workspace.

## Sources

- Timer control: https://learn.microsoft.com/power-apps/maker/canvas-apps/controls/control-timer
- Audio and Video controls: https://learn.microsoft.com/power-apps/maker/canvas-apps/controls/control-audio-video
- Gallery best practices (patching reloads items): https://learn.microsoft.com/power-apps/maker/canvas-apps/gallery-best-practice
- Collections and ForAll optimization: https://learn.microsoft.com/power-apps/guidance/coding-guidelines/code-optimization
- Code apps overview, prerequisites, licensing, limitations: https://learn.microsoft.com/power-apps/developer/code-apps/overview
- Code apps npm quickstart: https://learn.microsoft.com/power-apps/developer/code-apps/how-to/npm-quickstart
- Media size limits: https://learn.microsoft.com/power-apps/maker/canvas-apps/power-apps-studio
- Canvas-apps plugin: https://github.com/microsoft/power-platform-skills/tree/main/plugins/canvas-apps
