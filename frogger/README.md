# Frogger — Power Apps canvas app

A playable homage to Frogger built **directly as a canvas Power App**: Power Fx, one Timer, and standard
controls. No code components, no Code Apps. The reference version is the **Parker Brothers cartridge for Atari
home computers (1983) as it ran on an Atari 800XL**: dark green border, five river lanes and four road lanes, a
brick sidewalk that changes texture every level, SLOW/FAST top-left, 1UP score bottom-left, an orange time band,
a jingle at the start of each frog and effects only while playing.

Not affiliated with Konami, Sega, Parker Brothers, or Atari. All art, sound, and text are original.

Deployed to the **Workbench** environment (`e57d0c49-8edb-e5a5-af15-8a62479e341a`) inside the unmanaged
solution **Frogger** (publisher **Workbench**, prefix `wrk`). App ID `80f9c4ce-e9a8-4dd1-a8d2-a9bb969fc958`.

Play: https://apps.powerapps.com/play/e/e57d0c49-8edb-e5a5-af15-8a62479e341a/a/80f9c4ce-e9a8-4dd1-a8d2-a9bb969fc958

## What's in the game

| Area | Behaviour |
|---|---|
| Lanes | Nine lanes (five river, four road) on a per-lane loop. Layouts come from five tiers that cycle every five levels, taken from the arcade ROM tables. Speeds are arcade speeds scaled to the Atari grid; the racer pulses between two speeds like the arcade's speed ring. |
| Frog | One tap, one hop: a row vertically or 8 columns sideways, 3-tick animation, one queued hop. Rides logs and turtles with fractional carry; dies on the road, in the water, off the screen edge, on the bush, in a full bay, or when the time band empties. |
| Hazards | The last turtle group in each row dives on the arcade cycle. River alligator from level 2 (ride the body, not the head). Snakes on the first long log and on the sidewalk from level 3. Lady frog on the first short log from level 2, worth 200 at home. Bay fly on odd levels (200), bay alligator on even levels (deadly). |
| Timer | 30 seconds per frog, red with a warning tick in the last five, `TIME OUT` on expiry, 10 points per remaining second on arrival. |
| Scoring | 10 per new forward row, 50 per home, 1000 for all five, 200 fly, 200 lady. Five frogs, an extra frog every five levels. |
| Players | One or two players alternating on every lost frog (SELECT), each with their own score, frogs, level, and bays. |
| Console keys | START, SELECT, OPTION (SLOW/FAST at any time), PAUSE, RESET, MUTE, KEYS (shows a text box that reads W A S D or I J K L on desktop), LEVEL+ (debug: skips to the next level). |
| Sound | Eleven original chiptune clips synthesized by `tools/sounds.py` and embedded as WAV data URIs: start jingle, hop, squash, drown, warning, home, bonus, fanfare, pickup, extra frog, game over. |
| HUD | SLOW/FAST and reserve frogs on the top row; 1UP, turn indicator, 2UP across the bottom; session high score in Attract. A level and ticks-per-second readout sits under the playfield. |

Not yet built: Dataverse high-score table (see [docs/01-game-spec.md](docs/01-game-spec.md) section 19).

## How it runs inside canvas constraints

- **One Timer is the game loop.** `tmrGame` (`Duration 50`, `Repeat`, `AutoStart`) runs `OnTimerEnd` as one
  tick written as four sequential `UpdateContext` steps: scalars, frog, outcomes, commit. Nothing else mutates
  game state. A "tps" readout under the playfield shows the measured tick rate.
- **No tables in the tick.** Each lane's objects are evenly spaced on a loop, so the whole lane is one scalar
  offset; object `i` sits at `Mod((i - 1) * Loop / N + Off, Loop)`. Collision against the frog is a `Mod` on the
  lane period. A first version with a 45-row pool updated by `ForAll` + `Patch` ran at 0.2 ticks per second.
- **Logical coordinates.** 160 columns x 240 lines, like the Atari's colour clocks and scanlines. Named formulas
  `nfScale`, `nfCol`, `nfLine`, `nfLeft`, `nfTop` map them to screen pixels (800 x 600 playfield on a 1366 x 768 app).
- **Sprites are SVG named formulas** generated from bitmaps in `tools/sprites.py`, drawn at hi-res pixel width
  with a black outline, composed by rotation, mirroring, and overlay. The playfield background is one SVG.
- **Sound is data URIs.** `tools/sounds.py` synthesizes 8 kHz WAV clips; each has an `Audio` control whose
  `Start` is held true by a tick counter (a one-tick pulse pauses the clip before it loads).
- **Input is taps.** Four transparent tap zones around the frog, a hop cross beside the playfield, console-key
  buttons, and an optional focused text box for desktop keys.

## Layout

```
canvas/Src/        Generated .pa.yaml (App, Screen1, _EditorState). Build output; do not hand-edit.
canvas/base/       The non-YAML half of the app (unzipped .msapr) exported from the environment.
canvas/media/      The synthesized WAV clips as files (for reference or hosted fallback).
solution/src/      Unpacked Frogger solution (CanvasApps, Other).
tools/             gen_app.py (generator), game_logic.py (Power Fx), sprites.py, sounds.py,
                   mcp-canvas.js (stdio client for the Canvas Authoring MCP server), calls/*.json.
docs/              01-game-spec.md, 02-platform-decision.md, research/ (five research notes and an index).
build.ps1          Generate, pack the msapp and solution zip, optionally push, import, or publish.
```

## Build and deploy

1. `python tools/gen_app.py` regenerates `canvas/Src` from the generator.
2. `.\build.ps1` also packs `dist/Frogger.msapp` and `dist/Frogger_unmanaged.zip` from `canvas/base` and
   `solution/src`. `-Import` imports the zip into the pac-selected environment.
3. `-Push` compiles the YAML into a live Studio coauthoring session (app open in Studio, coauthoring on). The
   compile call runs twice because the authoring service appends newly created controls on top of the z-order
   and only reorders to file order on a second apply.
4. `-Publish` publishes the last saved version through the Power Apps API (Azure CLI logged into the tenant).

Requirements: pac CLI 2.12+, Python 3 (with Pillow only for the optional sprite contact sheet), Node 20+ and the
.NET 10 SDK for `-Push`, Azure CLI for `-Publish`.

## Research

`docs/research/00-index.md` summarises five research notes: arcade mechanics and ROM tables, arcade visuals
and audio, history and rights, the two Atari 8-bit ports side by side, and a source-code catalogue. Raw
third-party sources (MAME driver, disassemblies, open-source clones) stay local and are not published.
