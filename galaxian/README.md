# Galaxian Arcade — Power Apps canvas app

A playable homage to Galaxian built **directly as a canvas Power App**: Power Fx, one Timer, and standard
controls. No code components, no Code Apps. The reference version is the **Atari 8-bit cartridge (1982) as it
ran on an Atari 800XL**: a 37-alien convoy with three Commanders, a pink Earthship, blue level digit and yellow
score across the top, red flags per wave, difficulty levels 0 to 9 plus Beginner.

Not affiliated with Atari or Bandai Namco. All art, sound, and text are original.

Deployed to the **Workbench** environment (`e57d0c49-8edb-e5a5-af15-8a62479e341a`) inside the unmanaged
solution **Galaxian** (publisher **Workbench**, prefix `wrk`). App ID `d54c1069-9192-4e86-a6ec-db2d5f66ff2c`.

Play: https://apps.powerapps.com/play/e/e57d0c49-8edb-e5a5-af15-8a62479e341a/a/d54c1069-9192-4e86-a6ec-db2d5f66ff2c

## What's in the game

| Area | Behaviour |
|---|---|
| Convoy | 37 aliens in 5 rows (3 Commanders at columns 4, 6, 7; 6 Hornets; 8 Emissaries; 2 x 10 Drones). Sweeps side to side, never descends, limits widen as edge columns empty. Two-frame wing flap, unsynchronised. |
| Earthship | Slider-controlled, 6 columns per tick toward the slider. One missile at a time; the idle missile sits on the nose and kills divers by contact. |
| Divers | Peel off from the convoy's edges, quarter-circle arc, sine S-curve toward the player with random amplitude and jitter, wrap from bottom to top and return to their own slot. In waves 1 and 2 they never reach the screen edges (the manual's safe zones). |
| Commanders | Dive with up to two Hornets taken from directly beneath them, trailing diagonally. Escort scoring: 150 alone, 200 with one, 300 with two, **800** if both Hornets die first. Killing a Commander in flight silences the enemy for 4 s ("mourning"). |
| Bombs | Only divers fire, at fixed descent checkpoints, aimed at the player with spread. Count rises as rows empty and with level. Beginner level has no bombs for 16 waves. |
| Scoring | 30/40/50/60 in formation, 60/80/100/150+ in flight. Bonus ship once at 5,000. Score caps at 999,990. |
| Waves | Clear the convoy, 4 s pause, rebuild. Base difficulty +1 per wave (cap 7), in-wave aggression +1 every 20 s (cap 7, -1 on death). End phase (3 or fewer aliens, or no Drones/Emissaries): divers never return. |
| Console keys | START, SELECT (level 0-9, B), OPTION (reserved for two-player), PAUSE, RESET as on-screen buttons. |
| HUD | Level digit (blue), score (yellow), reserve ships (pink), wave flags (red) top row; high score bottom-left; "GALAXIAN" title in Attract, "PLAYER ONE" before each life, "GAME OVER". |

Not yet built (see [docs/01-game-spec.md](docs/01-game-spec.md) section 19): wave-10 surprise symbols,
flags past 16, attract-mode demo divers, two-player alternating mode, sound, Dataverse high-score table.

## How it runs inside canvas constraints

- **One Timer is the game loop.** `tmrGame` (`Duration 50`, `Repeat`, `AutoStart`) runs `OnTimerEnd` as a
  single tick: one long `With(...)` chain that reads the previous state and ends in one `UpdateContext`.
  Nothing else mutates game state. A small "tps" readout under the playfield shows the measured tick rate.
- **Logical coordinates.** 160 columns x 240 lines, like the Atari's colour clocks and scanlines. Named formulas
  `nfScale`, `nfColW`, `nfLeft`, `nfTop` map them to screen pixels (800 x 600 playfield on a 1366 x 768 app).
- **The convoy is a 37-character text.** `ctxAlive` holds "1"/"0" per slot. Each of the 37 alien `Image`
  controls reads its own character; the missile-vs-formation test is arithmetic on the missile position, not
  a scan of controls. Occupied-column bounds are recomputed only when the string changes.
- **Divers and bombs are fixed pools** (7 + 7) held in context-variable tables and updated with `ForAll`, so
  no collection is patched per tick and no gallery re-renders.
- **Sprites are inline SVG data URIs** generated from 8 x 8 bitmaps in `tools/sprites.py`, drawn 2:1 to mimic
  the Atari's wide pixels, and stored as named formulas so they are built once.
- **Input is on-screen only.** Canvas apps have no keyboard events: a Classic Slider moves the ship, FIRE (or a
  tap on the playfield) launches the missile in the press itself, and the console keys are buttons.

## Project layout

```
canvas/Src/*.pa.yaml      Generated app source (Power Apps YAML v3) — regenerate, do not hand-edit
canvas/base/              Non-YAML msapp scaffolding (Header, Properties, References, themes)
tools/game_logic.py       The Power Fx: OnVisible, START, and the tick formula
tools/sprites.py          8x8 pixel-art bitmaps -> SVG data-URI named formulas
tools/gen_app.py          Emits the YAML: 37 aliens, 32 stars, HUD, pools, controls, timer
tools/mcp-canvas.js       Stdio client for the Canvas Authoring MCP server (connect, compile, sync, checkers)
tools/calls/*.json        Call sequences for mcp-canvas.js
solution/src/             SolutionPackager-format solution (Other/*.xml + CanvasApps metadata)
docs/01-game-spec.md      Game specification (v1.1, Atari 800XL target) and build plan
docs/02-platform-decision.md   Why canvas rather than Code Apps; constraint-to-design mapping; build notes
docs/research/            Atari port, arcade mechanics, visuals/audio, history
build.ps1                 Generate, pack, push, import, publish — see below
dist/                     Build output (msapp + solution zip)
```

## Build, push, deploy

Requires Power Platform CLI (pac) 2.12+, Python 3, Node 20+, the .NET 10 SDK (provides `dnx` for the MCP
server), and a pac auth profile for the target environment (`PckWorkbench` was used).

```powershell
.\build.ps1              # regenerate canvas\Src, build dist\GalaxianArcade.msapp + dist\Galaxian_unmanaged.zip
.\build.ps1 -Push        # ... and compile the YAML into the live Studio coauthoring session
.\build.ps1 -Import      # ... and import the solution zip into the selected environment
.\build.ps1 -Publish     # publish the last saved app version via the Power Apps API (az login to the tenant first)
```

Two ways to get changes into the app:

1. **Live push (used during development).** Open Galaxian Arcade in Power Apps Studio in edit mode with
   **Settings > Updates > Coauthoring** on and keep the tab open. `.\build.ps1 -Push` connects the Canvas
   Authoring MCP server to that session and runs `compile_canvas`, which validates the YAML **and applies it**
   to the live document. Save in Studio to persist, then publish (Studio or `-Publish`).
2. **Solution import.** `.\build.ps1 -Import` packs the YAML into an msapp and the solution zip and imports it.
   An app packed from YAML should then be opened once in Studio to validate, then saved and published.

`tools/calls/check.json` runs the app checker and accessibility checker and syncs the server's normalized
YAML into `scratch/synced` for inspection.

## Editing notes that bite

- Every property value is a Power Fx formula starting with `=`, including `App.Properties.Formulas`.
- Multi-line formulas and anything containing `: ` or `{record: literals}` go in a `|-` block scalar.
- Control properties sit two levels under the control name (`Properties:` at indent 10, values at 12).
- `Label@2.5.1` and `Classic/Button@2.2.0` reject `AccessibleLabel`; `Image@2.2.3` and `Classic/Slider@2.1.0`
  accept it. Sprites carry `TabIndex: -1` on purpose, which the accessibility checker still flags.
- Timers only run in Preview inside Studio.
- The Canvas Authoring MCP server refuses to connect until coauthoring is enabled on the app, and a blank app
  seeded from a hand-packed msapp could be edited but not saved or published; **File > Save as** in Studio
  produced a Studio-native copy that works. That copy is this app.

## Research

The design draws on the Atari manual and captures ([docs/research/04-atari-8bit-port.md](docs/research/04-atari-8bit-port.md)),
and on the arcade's annotated ROM disassembly and MAME source for the mechanics the Atari sources leave open
([docs/research/01-gameplay-mechanics.md](docs/research/01-gameplay-mechanics.md), linked rather than copied here).
