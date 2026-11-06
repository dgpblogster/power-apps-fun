# Deep Station for Canvas Power Apps — Game Specification

Version 0.1 (draft), 2026-11-06. **Genre reference: the early-1990s first-person shooter, the style set by
Doom (id Software, 1993).** Target: a canvas Power App in the **Workbench** environment
(`e57d0c49-8edb-e5a5-af15-8a62479e341a`), in a new `DeepStation` solution, built as **Option C**: game logic,
HUD, menus, and flow in Power Fx; one PCF code component that only draws the 3D view, plays sound, and
captures input.

See [02-platform-decision.md](02-platform-decision.md) for why Option C. Values marked **(choice)** are
design decisions; values marked **(spike)** are placeholders that milestone M0 must measure and confirm.

This is an original game in the genre, not a recreation. It uses no id Software code, levels, art, sounds,
names, or characters. All maps, textures, sprites, sounds, and text are made for this project. The app will
state that it is not affiliated with id Software, ZeniMax, Bethesda, or Microsoft's games business.

---

## 1. Design goals

1. **Feel like a 1993-era shooter.** Fast movement with no jumping, mouse or keyboard turning, a weapon at the
   bottom of the view, a status bar, keycard doors, secrets, enemies that wake when they see you, hitscan and
   projectile weapons, and short levels that end at an exit switch.
2. **Keep Power Fx the game.** Every rule, every number, every state change lives in Power Fx on one Timer, as
   in Galaxian and Frogger. The code component is a display and an input device. It holds no game state that
   Power Fx does not send it, so the game can be read, tuned, and debugged in Studio.
3. **Use code only where canvas cannot do the job.** Canvas can't draw about 64,000 pixels 30+ times a second,
   can't read held keys, and can't lock the mouse. The PCF control does exactly those three things, plus
   sound because it has to be timed to the picture.
4. **Playable in a desktop browser with keyboard and mouse;** touch on a tablet is a later milestone.
5. **Keep the tick small enough to hit 20 per second.** Scalars, not tables, in the tick (the Frogger rule).

## 2. Architecture

```
 ┌────────────────────────── Canvas app (Power Fx) ───────────────────────────┐
 │                                                                            │
 │  tmrGame (50 ms) ──► OnTimerEnd: one tick, sequential UpdateContext steps  │
 │       │                 reads  pcfView.Keys / .Yaw / .UseSeq / .WeaponReq   │
 │       │                 writes ctx* game state                              │
 │       ▼                                                                    │
 │  nfFrame (named formula) = packed text of everything the view must show    │
 │       │                                                                    │
 │       ▼                                                                    │
 │  ┌──────────────── pcfView (RaycastView code component) ────────────────┐  │
 │  │ inputs : MapData, LightData, Frame, Paused, ShowTouch, TickMs        │  │
 │  │ renders: requestAnimationFrame, 320x200 offscreen canvas, scaled     │  │
 │  │ outputs: Keys, Yaw, UseSeq, WeaponReq, MenuSeq, Fps, Ready           │  │
 │  └──────────────────────────────────────────────────────────────────────┘  │
 │                                                                            │
 │  Status bar, messages, menus, automap, high scores: standard controls      │
 └────────────────────────────────────────────────────────────────────────────┘
```

| Concern | Owner | Why |
|---|---|---|
| Player position, health, armor, ammo, weapons, keys | Power Fx | Game state |
| Enemies, projectiles, pickups, doors, switches, secrets | Power Fx | Game state |
| Collision, hitscan, line of sight, damage, AI | Power Fx | Game rules |
| Level flow, difficulty, scoring, menus, automap | Power Fx | Game flow and standard controls |
| Status bar and messages | Power Fx | Standard controls, same as the other projects |
| View yaw (turning) | **PCF, reported to Power Fx** | Mouse turning at 20 Hz feels broken; see 4.3 |
| 3D view, sprites, weapon overlay, damage flash | PCF | Pixels |
| Sound effects | PCF | Web Audio, timed to the frame; triggered by Power Fx events |
| Keyboard, mouse, touch input | PCF | Canvas has no held-key or pointer-delta events |

**The rule:** the PCF control may *predict* (interpolate positions, turn the camera) but never *decide*.
If Power Fx and the view disagree, Power Fx wins on the next tick.

## 3. Contract between Power Fx and the code component

Code component properties can't be removed after import (only added, and only as optional), so the contract
is frozen at the end of M0. Every property after M0 is optional.

### 3.1 Inputs (Power Fx → PCF)

| Property | Type | Set when | Content |
|---|---|---|---|
| `MapData` | Text | Level load | `W,H;` then W×H cell characters, row by row (section 6.1) |
| `LightData` | Text | Level load | W×H digits `0`–`9`, light level per cell |
| `Frame` | Text | Every tick | Packed frame record (3.3) |
| `Paused` | Boolean | Menu, automap | Stops rendering and releases pointer lock |
| `ShowTouch` | Boolean | Settings | Draws the on-screen stick and buttons |
| `TickMs` | Whole number | Constant 50 | Interpolation window |

### 3.2 Outputs (PCF → Power Fx)

| Property | Type | Meaning |
|---|---|---|
| `Keys` | Whole number | Bitmask of held controls: 1 forward, 2 back, 4 strafe left, 8 strafe right, 16 run, 32 fire, 64 turn left, 128 turn right |
| `Yaw` | Decimal | Current view angle in degrees, 0–360, owned by the view (4.3) |
| `UseSeq` | Whole number | Increments on each Use press (edge, never lost between ticks) |
| `WeaponReq` | Whole number | Last weapon slot pressed, 1–5, 0 if none since the last `Frame.ack` |
| `MenuSeq` | Whole number | Increments on Esc (pause) and Tab (automap) presses; low bit tells which |
| `Fps` | Whole number | Rendered frames per second, for the diagnostics readout |
| `Ready` | Boolean | Assets decoded and first frame drawn |

Power Fx reads these as `pcfView.Keys` and so on **inside the tick**. `OnChange` is left empty. Microsoft's
guidance warns that calling `notifyOutputChanged` on every keypress or mouse move floods the host with events,
so the control calls it at most **30 times per second**, and only when an output changed. Edge inputs (Use,
weapon, menu) are counters, not flags, so a press that falls between two ticks is never lost: the tick compares
`pcfView.UseSeq` with `ctxUseSeqSeen`.

### 3.3 Frame record

One text value, rebuilt every tick by the named formula `nfFrame`, fields separated by `|`:

```
tick|px|py|weapon|wframe|flash|doors|sprites|events|ack
 41 |12.40|7.85|2|1|0|0000900000000000|1,4,10.5,6.5,2;3,7,15.0,9.2,0;9,1,11.0,7.0,0|6:41;11:41|7
```

| Field | Meaning |
|---|---|
| `tick` | `ctxTick`; the view uses it to order frames and drop stale ones |
| `px`, `py` | Player position in cells, two decimals |
| `weapon`, `wframe` | Weapon slot and animation frame (0 idle, 1–3 firing) |
| `flash` | Screen tint for this tick: 0 none, 1 damage red, 2 pickup gold, 3 radiation green |
| `doors` | One digit per door id 0–15: `0` closed … `9` fully open |
| `sprites` | `;`-separated `kind,frame,x,y,state` for every visible thing: enemies, projectiles, pickups, decorations, corpses |
| `events` | `;`-separated `soundId:tick` pairs raised this tick; the view plays each pair once |
| `ack` | Echo of the last `WeaponReq`/`UseSeq` handled, so the view can clear its edge outputs |

The record is text on purpose: one input property, one `updateView` per tick, and the whole visible world is
readable in a Studio label while debugging. Expected size: under 1 KB.

## 4. Game loop and timing

### 4.1 Tick
- **One hidden Timer** `tmrGame`, `Duration 50`, `Repeat`, `AutoStart`, `Start: =!ctxPaused`. `OnTimerEnd`
  runs one tick and is the only place that mutates game state.
- **20 ticks per second** (choice, from the Galaxian and Frogger measurements; spike confirms with this
  game's tick size). All speeds and timers are named formulas in cells per tick or ticks.
- A `tps` and `fps` readout sits in the status bar's corner, as in the other projects.

### 4.2 Tick order (sequential `UpdateContext` steps)
1. `sIn` input: read `Keys`, `Yaw`, edge counters; decide intended move vector, fire, use, weapon switch.
2. `sPl` player: move with wall and door collision (6.3), pick up items, apply hazard floor damage.
3. `sWp` weapon: cooldown, ammo, hitscan or projectile spawn, melee (section 8).
4. `sEn` enemies: for each pool slot, AI state step, movement, attack, line-of-sight check on its stagger slot
   (section 9).
5. `sPr` projectiles: move, hit walls, hit player or enemy, splash damage.
6. `sWo` world: doors, switches, secret walls, hazard timers, wave triggers, exit.
7. `sC` commit: one `UpdateContext` that writes every changed context variable, the event list, and mode
   transitions.

No step references a computed table twice. No collection is patched in the tick.

### 4.3 Who owns turning
Turning at 20 Hz with 50–100 ms of round-trip lag makes mouse look feel broken. So the view owns yaw. It turns
the camera every animation frame from mouse movement (pointer lock) or the turn keys (180°/s, 270°/s running),
and reports `Yaw`. Power Fx uses the reported yaw for movement direction and aiming. Yaw is pure input with no
collision, so nothing can disagree about it.

### 4.4 Interpolation
The view keeps the last two `Frame` records and their arrival times and draws positions interpolated between
them, one tick behind real time. That turns 20 Hz state into smooth 60 Hz motion at a constant 50 ms delay.
If a frame is late, the view holds the last position (no extrapolation in v1).

## 5. State model

Context variables on `scrGame` (`ctx` prefix); named formulas (`nf` prefix) for constants and level data.

**Player:** `ctxPX`, `ctxPY`, `ctxYaw`, `ctxHealth` (0–200), `ctxArmor` (0–200), `ctxArmorClass` (1 or 2),
`ctxWeapon`, `ctxWeaponsOwned` (5-char bit string), `ctxAmmoRivet`, `ctxAmmoShell`, `ctxAmmoCell`,
`ctxAmmoCharge`, `ctxKeys` (3-char bit string: amber, cyan, violet), `ctxCooldown`, `ctxWFrame`,
`ctxFlash`, `ctxHurtTicks`.

**Enemy pool:** 12 slots per level (choice; spike may lower to 8). Each slot `n` is six scalars generated by
the Python tool: `ctxE{n}K` kind, `ctxE{n}X`, `ctxE{n}Y`, `ctxE{n}S` state, `ctxE{n}H` health,
`ctxE{n}T` state timer. Slots are filled at level load and never added during play. A level with more than
12 enemies in total uses **waves**: slots whose enemy has died and fully decayed may refill from the level's
reserve list when the player enters a trigger cell (section 6.2).

**Projectile pool:** 6 slots (`ctxP{n}K`, `X`, `Y`, `DX`, `DY`, `Owner`).

**Pickups:** a level has at most 40, stored as a 40-character taken/not-taken string `ctxTaken`; positions and
kinds are named-formula level data, so the tick only flips characters.

**World:** `ctxDoors` (16 digits, openness), `ctxDoorT` (16 two-digit timers as a 32-char string),
`ctxSwitches`, `ctxSecretsFound`, `ctxKills`, `ctxItems`, `ctxLevelTicks`.

**Flow:** `ctxMode` (`Title`, `Briefing`, `Playing`, `Dead`, `Intermission`, `Victory`), `ctxLevel`,
`ctxSkill` (1–3), `ctxTick`, `ctxPaused`, `ctxUseSeqSeen`, `ctxMenuSeqSeen`, `ctxEvents`.

## 6. World and levels

### 6.1 Grid and cell codes
Levels are grids up to **48 × 48** cells (choice). One cell is 1.0 unit; walls are 1.0 high; floor and
ceiling are flat (no stairs, lifts, or height changes in v1: that is the price of the raycaster).

| Char | Cell |
|---|---|
| `.` | Floor |
| `1`–`9` | Wall, texture 1–9 |
| `D` | Door (index assigned in reading order, 0–15) |
| `a` `c` `v` | Door that needs the amber, cyan, or violet chip |
| `S` | Secret wall: slides back one cell when used, counts as a secret |
| `X` | Exit switch wall |
| `~` | Hazard floor (coolant): 5 damage every 20 ticks without the suit |
| `T` | Trigger floor: releases the next enemy wave |

Things (player start, enemies, pickups, decorations) are not in the grid. They are a list per level:
`kind x y angle skillmask`, `skillmask` bit 1 easy, 2 normal, 4 hard.

### 6.2 Source format
Each level is a text file in `deep-station/levels/` that `tools/levels.py` turns into named formulas:

```
name: Intake
music: none
light-default: 6
---grid---
11111111111111
1....1.......1
1.P..D...~~..1
1....1.......1
111a111111X111
---things---
player  2.5 2.5  90 7
drone   8.5 1.5 180 7
crawler 11.5 3.5 270 6
rivets  3.5 1.5   0 7
---lights---
(optional W×H digits; default fills the grid)
```

The `P` marker in the grid is a convenience the tool removes and turns into the player thing.

### 6.3 Collision
The player is a circle of radius 0.25. Movement is applied on X then on Y separately; each axis is rejected if
the target point plus radius lands in a solid cell (wall, closed door, door less than 7/9 open, secret wall not
yet moved). This is four `Mid(nfMap, …)` lookups per axis, cheap enough for every tick. Enemies use the same
test with radius 0.3.

### 6.4 Doors, switches, secrets
- **Doors** open when the player presses Use within 1.2 cells while facing them (±45°), over 9 ticks, stay open
  60 ticks, and close over 9 ticks unless something stands in the doorway. Locked doors need the chip and show
  "You need the amber chip" otherwise.
- **Exit switch:** Use on an `X` wall ends the level.
- **Secrets:** Use on an `S` wall slides it one cell back over 20 ticks and counts a secret.

### 6.5 Campaign (v1)
Four levels, one episode, about 5–8 minutes each (choice):

| # | Name | Introduces |
|---|---|---|
| 1 | Intake | Movement, doors, drones, crawlers, rivet pistol, scatter cannon |
| 2 | Coolant Loop | Amber and cyan chips, hazard floor and suit, welders |
| 3 | Ore Processing | Violet chip, brutes, arc repeater, secret walls |
| 4 | The Shaft | Charge launcher, the Warden boss, end screen |

Setting (original): a deep-crust mining station whose maintenance machines have gone hostile after the drill
broke into something below. The player is the station's last safety officer.

## 7. Player

| Value | Number |
|---|---|
| Walk speed | 0.15 cells/tick (3 cells/s) |
| Run speed | 0.25 cells/tick (5 cells/s) |
| Strafe | Same as walk/run |
| Start health / armor | 100 / 0 |
| Max health / armor | 200 / 200 |
| Armor absorption | Class 1: 1/3 of damage; class 2: 1/2 |
| Death | `Dead` mode, view drops to the floor, Use or click restarts the level with start-of-level inventory |

No lives and no score total; the intermission shows kills %, items %, secrets %, and time, like the genre.

## 8. Weapons

Original weapons. Damage is per hit; hitscan uses the aim ray (8.1).

| Slot | Weapon | Ammo (per shot) | Cooldown | Damage | Notes |
|---|---|---|---|---|---|
| 1 | Pipe wrench | none | 10 ticks | 10–30 | Melee, range 1.0 |
| 2 | Rivet pistol | rivet (1) | 8 | 5–15 | Hitscan, start weapon, 50 rivets |
| 3 | Scatter cannon | shell (1) | 18 | 7 pellets × 5–15 | Hitscan, pellets spread ±6° |
| 4 | Arc repeater | cell (1) | 3 | 5–20 | Fast hitscan |
| 5 | Charge launcher | charge (1) | 16 | 80 direct + 0–100 splash (radius 2.5) | Projectile, hurts the player too |

### 8.1 Hitscan in Power Fx
For each live enemy slot (at most 12), compute the angle from the player to the enemy and its angular
half-width `atan(0.3 / distance)`. Candidates are slots whose angle difference to the aim yaw (plus pellet
offset) is inside the half-width. The nearest candidate is hit if its distance is shorter than the wall
distance along the aim ray. The wall distance is a grid DDA (digital differential analyser) of at most 32
steps, done once per shot with `Sequence(32)` and `Mid` on the map, and only on ticks when a shot is fired.

## 9. Enemies

Original machines and one creature. Speeds in cells per tick.

| Kind | Health | Speed | Attack | Notes |
|---|---|---|---|---|
| Drone | 20 | 0.08 | Hitscan 3–15, every 30 ticks | Common, floats |
| Crawler | 40 | 0.16 | Melee 4–20 | Fast, low |
| Welder | 60 | 0.07 | Plasma bolt projectile, 5–25 | Keeps distance 4–6 cells |
| Brute | 150 | 0.10 | Melee 20–40, charge | Pain chance low |
| Warden (boss) | 1000 | 0.06 | Three-bolt volley | Level 4 only |

### 9.1 AI states
`Idle` → `Alert` (saw or heard the player) → `Chase` ⇄ `Attack` → `Pain` (chance per kind) → `Dead`
(corpse sprite stays). Enemies that are hit by another enemy's projectile turn on it for 100 ticks (the
genre's infighting, cheap to do: change the target slot).

### 9.2 Line of sight with a budget
Every enemy needs line of sight to decide to attack. A DDA per enemy per tick is too much, so line of sight is
**staggered**: on each tick only slots `n` where `Mod(ctxTick, 4) = Mod(n, 4)` get a 16-step check (3 checks per
tick for 12 slots), and the result is held for 4 ticks. Hearing: a player shot wakes every idle enemy within
10 cells, no line-of-sight needed.

### 9.3 Movement
Chase moves straight toward the player; if the next cell is blocked, the enemy tries the two 90° turns in a
fixed order, then waits. No pathfinding in v1 (choice; the genre's monsters are famously simple).

## 10. Pickups

Health vial +10 (to 200), medkit +25 (to 100), armor vest (100, class 1), heavy armor (200, class 2), rivets,
shells, cells, charges, the three access chips, the coolant suit (60 s hazard immunity), and a backpack that
doubles ammo caps. Each pickup is a sprite, a message, a sound event, and a gold flash.

## 11. Rendering (PCF)

- **Resolution:** an internal 320 × 200 canvas, scaled to the control size with `image-rendering: pixelated`.
  The control is 960 × 600 on desktop by default.
- **Walls:** classic grid raycasting with DDA, one ray per column (320 rays), field of view 66° (choice),
  fish-eye correction by perpendicular distance. 64 × 64 textures, side-dependent shading.
- **Doors:** a door is a thin wall in the middle of its cell, shifted sideways by its openness digit.
- **Floor and ceiling:** flat colors with a distance gradient in v1; textured floor casting is a backlog item.
- **Light:** each column's brightness = cell light level × distance falloff, through a 16-step shade table.
- **Sprites:** billboards sorted far-to-near, clipped against a per-column depth buffer. One facing in v1
  (8-angle rotations are backlog). Frames: walk ×2, attack, pain, death ×3.
- **Overlays:** weapon sprite with bob, crosshair, damage or pickup tint from `flash`, a "paused" dim.
- **Assets:** textures and sprites are original pixel art generated by `tools/textures.py` and
  `tools/sprites.py` into PNG atlases, embedded in the bundle as base64 so the control makes no network calls.
- **Budget:** at least 50 fps at 320 × 200 on a mid-range laptop (spike).

## 12. Screens and HUD (Power Fx)

- `scrTitle`: title art, New Game, skill (Easy / Normal / Hard), Controls, High scores.
- `scrGame`: `pcfView` at the top; under it a status bar of standard controls: ammo, health, armor, owned
  weapons 1–5, chips, and an original **vital-signs trace** (a heartbeat line whose speed and color follow
  health) in place of a face. A message line above the bar for pickups and locked doors.
- **Automap:** Tab pauses and shows an SVG drawn by `Concat` over the map string, with seen cells only
  (`ctxSeen` bit string updated on the line-of-sight stagger). Built only when opened, never per tick.
- `scrIntermission`: kills, items, secrets, time, par.
- `scrVictory`: end text after level 4.

## 13. Input

| Action | Keyboard / mouse | Touch (M5) |
|---|---|---|
| Move | W/S or ↑/↓ | Left stick |
| Strafe | A/D | Left stick |
| Turn | Mouse (pointer lock) or ←/→ | Drag on the right half |
| Run | Shift (hold) or Caps toggle | Always on |
| Fire | Left click or Ctrl | Fire button |
| Use | E or Space | Use button |
| Weapon | 1–5, mouse wheel | Weapon button cycles |
| Pause / automap | Esc / Tab | Buttons in the status bar |

The control is focusable (`tabindex=0`) and takes focus on click. If pointer lock is refused by the host frame
(see risks), turning falls back to dragging inside the view and to the arrow keys.

## 14. Audio

The PCF control synthesizes original sound effects with Web Audio at load time (pistol, scatter, arc, charge,
explosion, door, switch, pickup, item, pain, death, enemy wake and attack per kind). Power Fx raises sound
events by id in the `events` field; the view plays each `id:tick` pair once. A mute toggle in the status bar
sets a `Muted` flag carried in `Frame` (an added optional field after M0). No music in v1.

## 15. Persistence

v1 keeps the best time per level and skill for the session. A Dataverse table for best times in the solution is
milestone M6, as in Frogger's M7.

## 16. Risks and the M0 spike

| # | Risk | What M0 measures | Go / no-go |
|---|---|---|---|
| R1 | Tick rate with a bigger tick (12 enemy slots, collision, staggered LOS) | `tps` readout over 60 s | ≥ 15 tps, else 8 slots, then 10 Hz tick with longer interpolation |
| R2 | How fast `Frame` changes reach `updateView` in the player and in Studio preview | Arrival-time jitter logged in the control | Median ≤ 60 ms, p95 ≤ 120 ms |
| R3 | How fast outputs reach the tick | Key-down to `ctxPX` change, via a timestamp echo | ≤ 150 ms end-to-end |
| R4 | Render speed | `Fps` output | ≥ 50 fps desktop, ≥ 30 fps tablet |
| R5 | Pointer lock and keyboard focus inside the Power Apps player frame | Manual test in `apps.powerapps.com` and Teams | Works, or the drag fallback is good enough |
| R6 | `requestAnimationFrame` and listeners in a code component (the FAQ says the Window object isn't supported) | Run in player, Studio, and mobile | Works in player; document anything else |
| R7 | Environment setting: **Power Apps component framework for canvas apps** must be on in Workbench | Admin center check | On |
| R8 | Frozen contract: properties can't be removed after import | Review at end of M0 | Contract signed off; later fields optional |

## 17. Acceptance criteria (v1)

1. Title, skill choice, four levels, intermission after each, victory screen.
2. The view renders at ≥ 50 fps with textured walls, doors, light levels, sprites clipped by walls, the weapon
   overlay, and tints; `tps` stays ≥ 15 for a full level on a mid-range laptop.
3. WASD + mouse play with pointer lock; arrow keys and drag fallback work when pointer lock is not available.
4. All five weapons and five enemy kinds behave as in sections 8 and 9, including splash self-damage and
   infighting.
5. Doors, locked doors, chips, secrets, hazard floor and suit, exit switch work as in section 6.
6. The status bar and message line are standard controls and match `ctx` state on every tick.
7. The automap shows explored cells and the player arrow.
8. All content is original; the app shows the non-affiliation notice on the title screen.
9. Removing the code component from the screen leaves an app that still loads and shows the status bar (the
   game can't be played, but nothing errors), proving the view holds no game state.

## 18. Build plan

| Milestone | Scope |
|---|---|
| M0 Spike | PCF skeleton with the frozen contract, flat-shaded raycast of a test map, Power Fx tick moving the player from `Keys`/`Yaw`, a 12-slot enemy stub; measure R1–R6; sign off the contract |
| M1 Walkable | Level loader (`tools/levels.py`), textures, collision, doors, light, interpolation, status bar, level 1 grid |
| M2 Combat | Weapons, hitscan, projectiles, enemy AI and stagger LOS, sprites, damage, death and restart |
| M3 Content | Levels 2–4, chips, secrets, hazard, pickups, Warden, intermission and victory |
| M4 Sound and polish | Web Audio effects, weapon bob, automap, title and skill screens, diagnostics |
| M5 Touch | On-screen stick and buttons, tablet layout |
| M6 Persistence | Dataverse best times |

### 18.1 Repository layout
```
deep-station/
  README.md
  build.ps1                 builds the PCF, generates YAML, packs msapp and solution
  canvas/                   generated *.pa.yaml (do not hand-edit)
  pcf/RaycastView/          ControlManifest.Input.xml, index.ts, render/, input/, audio/
  levels/                   one text file per level (6.2)
  tools/gen_app.py          emits the YAML: screens, status bar, timer, pcfView binding
  tools/game_logic.py       the Power Fx tick, nfFrame, constants
  tools/levels.py           level text -> named formulas (map, lights, things)
  tools/textures.py         original 64x64 textures -> PNG atlas -> base64 module
  tools/sprites.py          original sprites -> PNG atlas -> base64 module
  solution/                 DeepStation solution, including the code component
  docs/01-game-spec.md      this document
  docs/02-platform-decision.md
```

## 19. Open questions

1. Keep the working title "Deep Station", or pick another?
2. 12 enemy slots plus waves, or accept 8 and design smaller fights?
3. Is the Workbench DLP policy and admin setting for code components in canvas apps something we can turn on,
   or does this need a separate environment?
4. Touch in v1 or later (currently M5)?
