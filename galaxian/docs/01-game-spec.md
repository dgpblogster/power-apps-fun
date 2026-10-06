# Galaxian for Canvas Power Apps — Game Specification

Version 1.2, 2026-10-05. **Reference version: the Atari 8-bit computer cartridge (Atari, CXL4024, 1982) as it ran on an Atari 800XL.** Target: a canvas Power App in the Workbench environment, in the `Galaxian` solution, built with Power Fx and standard controls.

See [02-platform-decision.md](02-platform-decision.md) for why canvas. Research behind every number: [research/04-atari-8bit-port.md](research/04-atari-8bit-port.md) for the Atari version, and [research/01-gameplay-mechanics.md](research/01-gameplay-mechanics.md) for the arcade mechanics used to fill gaps the Atari sources leave open. Each gap-fill is marked **(arcade fill)**.

This is a homage. All artwork, sounds, and text will be original. The app will state that it is not affiliated with Atari or Bandai Namco.

---

## 1. Design goals

1. **Feel like the 800XL version.** A 37-alien convoy with three Commanders, chunky 4:3 TV presentation, pink Earthship, blue level digit and yellow score at the top, red flags per wave, high score bottom-left, the title word centred mid-screen, "PLAYER ONE" before each life, difficulty levels 0 to 9 plus Beginner.
2. **Honour the canvas constraints.** Tick-based simulation on a Timer, fixed control pools, no keyboard, formula-driven rendering. Where the original does something canvas cannot, this document names the simplification.
3. **Playable in a browser and on a tablet** with mouse or touch, in landscape.
4. **Keep the formula surface small enough to debug.** Every per-tick computation reads a handful of global variables and writes them back once.

## 2. Playfield and coordinates

The Atari showed a 4:3 landscape picture. Logical units follow the hardware so that every measured value from the research can be used directly.

- **Logical space:** 160 **columns** (colour clocks, X) by 240 **lines** (scanlines, Y). A column is exactly twice as wide as a line is tall on a 4:3 display.
- **Scale:** named formula `nfScale` = screen pixels per line. Default **2.5**, giving a playfield of **800 x 600** screen pixels. A column is `2 * nfScale` = 5 screen pixels. Tablets use 2 (640 x 480).
- **Mapping:** `screenX = playfieldLeft + X * 2 * nfScale`, `screenY = playfieldTop + Y * nfScale`.
- **Bands:**

```
 Y   0-14   blank (TV overscan)
 Y  15-25   HUD: [level digit, blue] [score, yellow] [ship icons, pink] [flags, red]
 Y  28-78   convoy: 5 rows, 10 lines apart (row centres 32, 42, 52, 62, 72)
 Y  79-204  attack space
 Y 205-220  Earthship (8 columns wide, 8 lines tall, drawn 2x)
 Y 218-230  bottom text: high score (left), player id (centre), opponent score (right)
```

## 3. Game loop and timing model

- **One hidden Timer** `tmrGame`, `Repeat: true`, `AutoStart: true`, `AutoPause: false`. `OnTimerEnd` runs one tick. The Timer is the only place that mutates game state.
- **Tick length** `nfTickMs` default **50 ms (20 ticks per second)**, three 60 Hz frames per tick. Fallback 100 ms if a device cannot sustain it. All speeds are derived from `nfFramesPerTick` so game feel survives a tick change.
- **Speed table.** Atari speeds are unverified, so these are arcade speeds converted to the Atari grid (arcade 224 px wide maps to 160 columns, arcade 256 tall maps to 240 lines) **(arcade fill)**, rounded to whole units per tick:

| Object | Per tick (default) |
|---|---|
| Earthship | 2 columns |
| Player missile | 11 lines up |
| Convoy sweep | 1 column on 2 of every 4 ticks (about 10 columns/s) |
| Diver descent | 3 lines; 4 lines when Y > 140 |
| Alien bomb | 6 lines down, up to 2 columns sideways |
| Wing flap | every 5 ticks |
| Commander mourning | 80 ticks (4 s) |
| In-wave aggression step | 400 ticks (20 s) |
| Between waves | 85 ticks |
| Player explosion | 13 ticks |
| Score popup / Easter-egg symbol | 17 ticks |

- **Tick order** inside `OnTimerEnd`:
  1. Read input flags set by the on-screen controls.
  2. Move Earthship; spawn missile if requested and none is live.
  3. Move missile; remove above Y 26.
  4. Advance convoy offset; reverse at limits.
  5. Advance launch countdowns; launch a diver or a convoy if due and a slot is free.
  6. Move each active diver through its path stage.
  7. Move each active bomb; remove off-screen bombs.
  8. Collisions: missile vs formation, missile vs divers, nose-missile vs divers, bombs vs ship, divers vs ship.
  9. Apply kills: alive string, score, popups, mourning timer, escort tracking.
  10. Check wave clear, extra ship, game over. Advance timers.
  11. Write all state back, one `Set` per variable.

## 4. State model

**Scalars**
- `gblMode`: "Attract", "Ready", "Playing", "Dying", "WaveClear", "GameOver".
- `gblTick`, `gblScore`, `gblHighScore`, `gblLives`, `gblWave`, `gblBonusAwarded`.
- `gblLevel`: 0 to 9, or 10 meaning **B** (Beginner). Set with the SELECT control before a game.
- `gblTwoPlayer` (boolean), `gblCurrentPlayer` (1 or 2), `gblScoreP2`, `gblLivesP2`, `gblWaveP2`, `gblAliveP2` (saved state for the alternating second player).
- `gblShipX` (centre, 6 to 154), `gblTargetX`, `gblFireRequested`.
- `gblMissileActive`, `gblMissileX`, `gblMissileY`.
- `gblConvoyX` (-16 to +16 columns from centre), `gblConvoyDir`.
- `gblAlive`: a **37-character text**, "1" or "0" per slot, ordered: 1 to 3 Commanders (columns 4, 6, 7), 4 to 9 Hornets (columns 3 to 8), 10 to 17 Emissaries (columns 2 to 9), 18 to 27 Drones row A (columns 1 to 10), 28 to 37 Drones row B (columns 1 to 10). Read per tick with `Mid`, written only on a kill or a return.
- `gblMinCol`, `gblMaxCol`: outermost occupied columns, recomputed on each kill.
- `gblDiffBase` (0 to 7), `gblDiffExtra` (0 to 7), `gblMourningTicks`, `gblWaveTicks`.
- `gblLaunchTimer`, `gblConvoyTimer`.

**Collection `colDivers`** (fixed 7 rows): `Slot` 1 to 7 (1 Commander, 2 and 3 Hornet escorts, 4 to 7 singles), `Active`, `Kind`, `HomeIndex`, `X`, `Y`, `Stage`, `StageTick`, `Dir`, `Pivot`, `Phase`, `Amplitude`, `EscortOf`, `EscortsLaunched`, `EscortsKilled`.

**Collection `colBombs`** (fixed 7 rows): `Slot`, `Active`, `X`, `Y`, `DX`.

**Fixed pool rule:** rows are never added or removed during play. `Active: false` means free.

## 5. Earthship (player)

- Horizontal only. Moves 2 columns per tick toward `gblTargetX`, clamped to 6..154 (ship is 8 columns wide).
- **One missile at a time.** The manual: "Between shots, your next missile sits on the nose of your ship." While `!gblMissileActive`, a **nose missile** is drawn at (`gblShipX`, 203) and acts as a hitbox: a diver that touches it dies and scores its in-flight value. This is a distinctive Atari feature and is kept.
- On `gblFireRequested` and `!gblMissileActive`, the nose missile launches: `gblMissileY = 203`, travels 11 lines per tick, deactivates above Y 26. Fire is edge-triggered.
- **Death:** overlap with an active bomb (unless Beginner shield applies) or an active diver. `gblMode` = "Dying" for 13 ticks with the explosion sprite, divers and bombs cleared, `gblDiffExtra` decremented by 1 (min 0) **(arcade fill)**. Then if lives remain: "Ready" with "PLAYER ONE" (or "PLAYER TWO") centred for 40 ticks, ship respawns at X 80. Otherwise "GameOver".
- **Lives:** start with **3**. **One bonus ship at 5,000 points**, once per game. The HUD shows ship icons for ships in reserve (the manual says "the number of ships the player has left"); the build shows reserve ships, max 4.

## 6. Convoy (formation)

- **Layout:** 37 aliens, 5 rows, 10 columns, exactly as the Atari captures show. Column c (1 to 10) has logical X `= 22 + (c - 1) * 12 + gblConvoyX` (alien left edge; aliens are 8 columns wide, so the convoy spans 116 columns centred in 160). Row r (1 to 5) has Y `= 28 + (r - 1) * 10`.
- Row 1: Commanders at columns **4, 6, 7**. Row 2: Hornets at 3 to 8. Row 3: Emissaries at 2 to 9. Rows 4 and 5: Drones at 1 to 10.
- **Movement:** `gblConvoyX` changes by `gblConvoyDir` on 2 of every 4 ticks. Reverses when the leftmost or rightmost occupied column would pass the limits (X 4 or X 148). Limits widen as edge columns empty, so a thinned convoy travels further.
- **Never descends.** Unverified for the Atari version; the manual never mentions it and the arcade does not **(arcade fill)**.
- **Rendering:** 37 fixed `Image` controls, `Visible: = Mid(gblAlive, n, 1) = "1"`, X and Y from the formulas above, image chosen by kind and by `Mod(Int(gblTick / 5) + n, 2)` for a two-frame flap, phase-shifted by slot so the flap is unsynchronised as in the captures. Commanders also flap (observed in a capture).

## 7. Diving attacks

### 7.1 Launch timing (arcade fill, scaled by Atari level)
- `nfDiff` = `gblDiffBase + gblDiffExtra + gblLevelBoost`, where `gblLevelBoost` = `gblLevel` for levels 0 to 9 (so level 9 starts near maximum aggression, matching "level 9 is incredibly difficult") and 0 for Beginner.
- `gblLaunchTimer` counts down each tick. At 0, if a single-diver slot is free (`nfMaxSingles` = `Min(Floor(nfDiff / 2), 3) + 1` slots), launch one alien. Reset to `Max(12, RoundDown(78 / (1 + nfDiff / 2), 0))` ticks.
- `gblConvoyTimer` interval `= (9 - Min(3, Floor(nfDiff / 4))) * 20` ticks (6 to 9 s). 40 ticks once no Drones or Emissaries remain.
- No launches while `gblMourningTicks > 0` or `gblMode <> "Playing"`.

### 7.2 Choosing the alien
- **Flank:** the manual says divers come "from the extreme right or left of their formation". If `gblConvoyX` is within 10 columns of a travel limit, use that side; otherwise random **(arcade fill for the tie-break)**.
- **Single diver:** first occupied column from the flank. While any Commander is alive, pick from the Emissary row then the two Drone rows downward. Once no Commander remains, Hornets dive singly too **(arcade fill)**.
- **Convoy:** first alive Commander from the flank. Take up to 2 alive Hornets from the three Hornet positions beneath it (below-left, below, below-right; Hornet columns 3 to 8 sit under Commander columns 4, 6, 7 so each Commander has 3 candidates) **(arcade fill)**. Escorts trail the Commander in a diagonal line, as the Atari capture shows: offsets (-6, +10) and (+6, +10) in (columns, lines).
- On launch set the slot's `gblAlive` character to "0" and activate the diver row at the alien's formation position.

### 7.3 Path stages
Reviewers call the Atari dives "erratic" rather than smooth loops. The model below is a sine S-curve with a random per-dive amplitude and a jitter term to reproduce that feel.

1. **Arc** (8 ticks): quarter-circle of radius 10 columns up and toward the flank, from a static 8-entry table `colArc`.
2. **Aim:** `TargetDX` = ship X minus diver X, clamped to magnitude 30..80 columns toward the ship. `Pivot` = diver X + `TargetDX` / 2. `Amplitude` = `Abs(TargetDX) / 2 * (0.6 + Rand() * 0.8)`.
3. **Descend:** Y += 3 (4 when Y > 140). X = `Pivot + Sin(Phase) * Amplitude + jitter`, `Phase += 0.35`, `jitter` = `(Rand() - 0.5) * 2` columns. Divers in early waves (`gblWave <= 2`) are clamped to X 14..146 so the screen edges are safe, matching the manual's "go to the extreme right or left" tip.
4. **Bombing** during Descend at Y checkpoints 130, 155, 180 (first `nfBombChecks` of them).
5. **Bottom** (Y > 240):
   - **Normal:** the manual says missed Galaxians "fly back into formation". Stage "Return": reappear at Y -10 above the home column and descend at 3 lines per tick to the home Y, then set the `gblAlive` character back to "1" and deactivate.
   - **End phase** (3 or fewer aliens alive in formation, or no Drones and no Emissaries alive) **(arcade fill)**: stage "Charge": re-enter at a random X at Y -10, descend with the S-curve at 4 lines per tick, no bombs for the first 40 lines, never return.
   - **Commander:** with at least one escort launched, behaves as above. Launched alone, it flees and is removed, not counted for wave clear **(arcade fill)**.
6. Off the side (X < -8 or X > 168) is treated like Bottom.

### 7.4 Mourning
The manual: "When a Commander is destroyed while attacking, the Galaxians cease firing for a few seconds." Killing a Commander in flight sets `gblMourningTicks` = 80. While positive: no launches, no bombs, aggression timer frozen. Killing a Commander in formation has no effect.

## 8. Alien bombs

- Only divers fire. The formation never fires.
- **Beginner level (B):** no bombs at all for the first 16 waves. Collisions still kill.
- Pool of 7. A diver fires when its Y crosses a checkpoint and a slot is free and `gblMourningTicks = 0`.
- `nfBombChecks` starts at `1 + Floor(gblLevel / 4)` (so 1 at levels 0 to 3, 2 at 4 to 7, 3 at 8 to 9) and adds 1 for each emptied row from the bottom, max 3. Bombs are released in a string, which produces the diagonal trail of dashes seen in captures.
- Spawn at the diver's position. `DX` = `(gblShipX - X) / 40 + (Rand() - 0.5) * 0.8`, clamped to -2..2 columns per tick. Y += 6 per tick. Straight flight. Removed when Y > 240 or X off screen. At levels 0 to 4 bombs are aimed ("fire in patterns"); at 5 to 9 the random term doubles ("fire randomly").

## 9. Collision

Axis-aligned rectangle overlaps in logical units, evaluated per tick only for active objects.

| Pair | Box A | Box B |
|---|---|---|
| Missile vs formation alien | missile 1 x 4 | alien 8 x 8 at slot |
| Missile vs diver | missile 1 x 4 | diver 8 x 8 |
| Nose missile vs diver | nose 1 x 4 at (gblShipX, 203) | diver 8 x 8 |
| Bomb vs ship | bomb 1 x 4 | ship 8 x 8 at (gblShipX, 205) |
| Diver vs ship | diver 8 x 8 | ship 8 x 8 |

Missile vs formation is arithmetic: column = `(gblMissileX - 22 - gblConvoyX) / 12`, row = `(gblMissileY - 28) / 10`; if both are within tolerance of an integer and the slot exists, read that one character of `gblAlive`.

## 10. Scoring

Identical to the arcade, confirmed by the Atari manual.

| Target | In formation | In flight |
|---|---|---|
| Drone (cyan) | 30 | 60 |
| Emissary (purple) | 40 | 80 |
| Hornet (red) | 50 | 100 |
| Commander alone | 60 | 150 |
| Commander that launched with 1 escort | n/a | 200 |
| Commander with 2 escorts, at least one alive | n/a | 300 |
| Commander with 2 escorts, **both escorts killed first** | n/a | **800** |

- Kill popups: the point value is shown at the kill position for 17 ticks for Commander kills.
- **Surprises** (the manual: "Get past the tenth wave... You may also see a few surprises"): from wave 10 on, every fourth kill shows a small symbol at the kill position instead of a point value. Wave 10 to 11: a yellow chomping disc (homage to the original's Pac-Man symbol). Wave 12 to 13: the app's own logo mark. Wave 14 and up: the player's initials, taken from the signed-in user's display name via `User().FullName`. The original showed Pac-Man, the Atari logo, and "JT"; those are trademarks and are replaced with original equivalents.
- Score capped at 999,990. No wave-clear bonus. No points for fled Commanders.
- High score updates at game over, matching the manual's "highest final score".

## 11. Waves and difficulty

- `gblDiffBase` += 1 per wave clear, cap 7. `gblDiffExtra` += 1 every 400 ticks in a wave, cap 7, reset at wave start, -1 on death, frozen during mourning **(arcade fill)**. `gblLevel` adds a constant boost (section 7.1).
- **End phase** as in 7.3 **(arcade fill)**.
- **Wave clear:** no "1" in `gblAlive` and no active diver. "WaveClear" for 85 ticks, then rebuild the 37-alien pattern, reset convoy offset and aggression, base +1, wave +1, add a flag.
- **Wave flags:** one red flag per wave at the top right, as observed. 16 flag slots are reserved; beyond 16 the flags are replaced by a wide "10" marker per ten waves plus small flags for the remainder **(arcade fill, since the Atari behaviour past wave 10 is unverified)**.
- No kill screen. Difficulty plateaus.

## 12. Screens and game flow

One screen `scrGame` with layered groups toggled by `gblMode`.

1. **Attract:** the live game screen runs a demo (convoy sweeping, occasional AI diver, no player). Centred mid-screen (Y 125): **"GALAXIAN"** in a wide lavender font. Bottom text line in grey: the high score at left followed by the app's own copyright or "not affiliated" line. Pink Earthship at bottom centre. On-screen **START**, **SELECT**, **OPTION** buttons stand in for the console keys.
2. **Ready:** "PLAYER ONE" or "PLAYER TWO" in wide lavender text centred for 40 ticks, then "Playing".
3. **Playing:** full simulation. SPACE-bar pause becomes an on-screen **PAUSE** button.
4. **Dying:** explosion 13 ticks, then Ready or GameOver (or hand over to the other player in a two-player game).
5. **WaveClear:** 85-tick pause.
6. **GameOver:** "GAME OVER" centred, final score, high score updated, START restarts. Returns to Attract after 200 ticks.

**HUD (top row, Y 15 to 25, left to right):** level digit or "B" in **blue**; score in **yellow** (leading zeros suppressed to "00"); reserve ship icons in **pink**; red **flags** at the far right.
**Bottom row (Y 218 to 230):** high score in grey at left; in two-player games the current player id centre and the opponent's score at right.

**Console-key equivalents:**
- **START:** begin or restart at any time.
- **SELECT:** cycles level 0, 1, ... 9, B. Shown in the HUD level slot. Available only in Attract and GameOver (pressing it mid-game in the original ended the game; the app simply disables it mid-game and does not reproduce the infinite-lives bug).
- **OPTION:** toggles two-player alternating mode.
- **RESET:** back to one player, level 0. High score is kept for the session.

## 13. Input

Canvas apps have no keyboard events, so all input is on-screen.

- **Movement:** a horizontal **Slider** `sldMove` below the playfield, `Min 6`, `Max 154`, bound to `gblTargetX`. The ship moves 2 columns per tick toward the slider value, keeping a speed limit like the joystick. Alternative: two transparent tap regions (left half, right half of the lower playfield) that set `gblTargetX` to the tap column. Both ship; a settings toggle picks one.
- **Fire:** a large FIRE button at bottom right and a tap anywhere on the upper two thirds of the playfield both set `gblFireRequested = true`.
- **START, SELECT, OPTION, PAUSE, RESET, MUTE:** buttons in a strip under the playfield, styled as the 800XL's console keys.

## 14. Visual design

Original pixel art on an 8 x 8 logical grid (8 columns by 8 lines), drawn as inline SVG in `Image` controls so each sprite scales with `nfScale` and shows the wide-pixel Atari look (each logical column is drawn 2:1).

**Palette** (NTSC Atari look; values are design choices informed by the captures):

| Element | Colours |
|---|---|
| Background | black #000000 |
| Commander | gold #E8C840 body, red-orange #E05A20 lower wings, blue-violet #6060D0 centre |
| Hornet | red #E03030 body, green #40B040 wing tips, yellow #F0E040 centre |
| Emissary | lavender #B080E0 body, dark blue #3040A0 tips, gold #E8C840 centre |
| Drone | teal #40C0C0 body, dark blue #2040A0, dark red #A02020 centre |
| Earthship | hot pink #F050A0 hull, blue #4060E0 engine pods |
| Player missile and nose missile | white #F0F0F0 1 x 4 dash |
| Alien bombs | white #F0F0F0 (yellow #F0E040 at levels 5 to 9) 1 x 4 dash |
| Level digit | blue #5080F0 |
| Score | yellow #F0E040 |
| Ship icons | pink #F050A0 |
| Flags | red #E03030 |
| Bottom text | grey #B0B0B0 |
| Title and PLAYER ONE | lavender #B0A0F0 |
| Explosion | yellow, orange, white |
| Stars | blue #6080F0, teal #40C0A0, orange-pink #F09060, white #E0E0E0 |

- **Sprites:** one 8 x 8 alien shape in three palettes for Hornet, Emissary, Drone; a distinct Commander shape; a two-frame flap for all four. Earthship 8 x 8 in two colours. Explosion 3 frames.
- **Starfield:** 32 single-pixel stars in vertical columns, one colour per column, scrolling down 1 line per tick, wrapping at 240. Toggle `Visible` on `Mod(gblTick + n, 9) = 0` for a sparse twinkle.
- **Fonts:** HUD digits in a chunky rounded bold double-width style; the title and "PLAYER ONE" in a wide outlined style; bottom text in a plain monospace. Implemented with `Font.'Courier New'` bold and letter-spaced labels, or custom SVG glyphs for the title word.
- **Attract title:** the word "GALAXIAN" only, mid-screen, in the lavender wide font, exactly where the original places it. No logo graphic.

## 15. Audio

Original synthesized effects, modelled on the descriptions of the Atari sound (not the arcade):

| Effect | Behaviour | Trigger |
|---|---|---|
| Background rumble | constant low-pitched noisy drone, looped | Playing mode |
| Formation tone | long high-pitched tone from stationary aliens, soft, looped | Playing mode while aliens remain |
| Dive sweep | pitch changes rapidly and falls as the alien descends | diver launch (loops while any diver is active) |
| Shot | short click-blip | missile launch |
| Alien hit | short noise burst | any kill |
| Commander hit | slightly longer two-tone | Commander killed in flight |
| Ship explosion | low noise burst | player death |
| Extra ship | brief rising beeps | bonus at 5,000 |

Each is an `Audio` control with `Start` bound to a boolean set true by the tick and false the next tick, or `Loop: true` for the rumble, formation tone, and dive sweep. A MUTE toggle is provided.

## 16. Persistence

- Version 1: high score in `gblHighScore` for the session, as the original kept it until power off.
- Version 2: Dataverse table `wrk_galaxianscore` in the `Galaxian` solution (Score, Player, Wave, Level, Date), written at game over when the score beats the stored best, read at app start.

## 17. Deliberate deviations and gap-fills

| Original (Atari 8-bit) | This app | Reason |
|---|---|---|
| 60 frames per second | 20 ticks per second | Timer control floor |
| Joystick hold | Slider or tap-to-target | No press-and-hold events |
| Console keys START, SELECT, OPTION, SPACE | On-screen buttons | No keyboard events |
| Pac-Man, Atari logo, "JT" symbols | Original symbols and the player's initials | Trademarks |
| SELECT-during-game ends the game and enables infinite lives | SELECT disabled mid-game | Bug, not a feature |
| Dive paths (unverified shape) | Sine S-curve with random amplitude and jitter | Reproduces the "erratic" feel |
| Return behaviour, end phase, mourning length, launch cadence, Commander flee rule | Arcade mechanics | Atari behaviour unverified |
| Flags past wave 10 | "10" marker plus small flags | Unverified |
| Sound | Synthesized approximations | No recordings analysed |

## 18. Acceptance criteria

1. The 37-alien convoy renders with Commanders at columns 4, 6, 7, Hornets at 3 to 8, Emissaries at 2 to 9, Drones across 1 to 10 in two rows, and sweeps side to side without descending.
2. The HUD shows level digit (blue), score (yellow), reserve ships (pink), flags (red) across the top, and the high score bottom-left in grey.
3. The Earthship moves within 6..154 and has exactly one missile; the idle missile sits on the nose and kills a diver by contact.
4. Formation and in-flight kills score per the table. The 800 combo works.
5. Divers launch from the convoy's edges, return to their own slots, and in waves 1 to 2 never reach the screen edges.
6. A Commander launches with up to two Hornets trailing diagonally.
7. Killing a Commander in flight stops launches and bombs for 4 seconds.
8. Beginner level: no bombs for 16 waves. Levels 0 to 9 raise launch frequency and bomb count.
9. Death shows the explosion, then "PLAYER ONE", costs a life. Bonus ship once at 5,000.
10. Wave clear adds a flag and rebuilds the convoy.
11. From wave 10, surprise symbols appear on some kills.
12. START, SELECT, OPTION, PAUSE, RESET work as specified; two-player alternating mode swaps scores and convoy state.
13. Attract shows "GALAXIAN" mid-screen with a demo convoy. Game over shows "GAME OVER" and allows restart.
14. Runs at the default tick without visible stalls for a full wave on a mid-range laptop browser.

## 19. Build plan

| Milestone | Scope |
|---|---|
| M1 Skeleton | Canvas app in the Galaxian solution, coauthoring on, `scrGame`, `tmrGame`, scale formulas, starfield, HUD labels, mode variable, console-key buttons |
| M2 Convoy | `gblAlive`, 37 alien images, sweep and reverse, flap |
| M3 Earthship | Slider and tap movement, nose missile, one-shot rule, missile vs formation, scoring, high score |
| M4 Divers | `colDivers` pool, launch timers, flank selection, arc, S-curve, return, early-wave edge safety |
| M5 Convoys and bombs | Commander plus Hornets, escort scoring, mourning, `colBombs`, Beginner shield, death, lives, bonus ship |
| M6 Waves and levels | Wave clear, flags, difficulty by level, end phase, surprise symbols |
| M7 Attract and polish | Attract demo, title text, PLAYER ONE, sounds, pause, mute, two-player alternating |
| M8 Persistence | Dataverse high score table in the Galaxian solution |

Each milestone ends with a playable build and the acceptance criteria it covers checked in the browser.

---

## 20. Implementation status (2026-10-05)

| Milestone | Status | Notes |
|---|---|---|
| M1 Skeleton | Done | Timer at 50 ms, logical coordinate formulas, 32-star field, HUD, mode machine, console keys |
| M2 Convoy | Done | 37 Image controls over `ctxAlive`, sweep with widening limits, unsynchronised flap |
| M3 Earthship | Done | Slider movement, nose missile, instant fire on press, formation collision, scoring, bonus ship, high score |
| M4 Divers | Done | 7-slot pool as a context table, flank selection, arc, sine S-curve with jitter, return, early-wave edge safety |
| M5 Convoys and bombs | Done | Commander plus up to two Hornets, escort scoring, mourning, 7-slot bomb pool, Beginner shield, death, lives |
| M6 Waves and levels | Partial | Wave clear, difficulty by level and time, end phase done. Surprise symbols and flags past 16 pending |
| M7 Attract and polish | Partial | Attract title and HUD done. Demo divers, two-player, sound, mute pending |
| M8 Persistence | Not started | Session high score only |

Tuning changes made after playtesting, superseding earlier sections:

| Spec value | Shipped value | Why |
|---|---|---|
| Earthship 2 columns per tick (section 3) | **6 columns per tick** (`nfShipSpeed`) | The slider is position-based; at 2 the ship lagged the handle by seconds |
| Missile 11 lines per tick, launched on the next tick (sections 3, 5) | **16 lines per tick**, launched **in the button press** | Fire felt slow: tick latency plus a 0.75 s flight before the next shot |
| No diagnostics | "tps" readout under the playfield | Shows whether the browser sustains 20 ticks per second |
| Point-sample collision at the missile tip (section 9) | **Swept test** over the segment the missile covered this tick, lowest intersecting alive row wins | At 16 lines per tick the missile skipped 8-line-tall aliens, worst on the top row |

Deviations discovered in the build: the accessibility checker flags every sprite Image for a tab stop (they
carry `TabIndex -1` as decorative); `Label@2.5.1` has no `AccessibleLabel`, so HUD text relies on its visible
content. Sound (section 15) is not implemented because media files cannot be added through YAML; it needs a
Studio media upload or externally hosted HTTPS clips.
