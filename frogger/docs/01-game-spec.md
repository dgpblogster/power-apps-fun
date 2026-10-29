# Frogger for Canvas Power Apps — Game Specification

Version 1.0, 2026-10-28. **Reference version: the Parker Brothers cartridge for Atari home computers (1983,
Steve Kranish and Dawn Stockbridge, 8K ROM) as it ran on an Atari 800XL.** Target: a canvas Power App in the
**Workbench** environment (`e57d0c49-8edb-e5a5-af15-8a62479e341a`, maker marianog@maximumglobal.biz), in the
`Frogger` solution, built with Power Fx and standard controls.

See [02-platform-decision.md](02-platform-decision.md) for why canvas. Research behind every number:
[research/04-atari-8bit-port.md](research/04-atari-8bit-port.md) for the Parker Brothers version,
[research/01-gameplay-mechanics.md](research/01-gameplay-mechanics.md) and
[research/05-source-code.md](research/05-source-code.md) for the arcade mechanics and ROM tables used to fill
gaps the port's sources leave open, [research/02-visual-audio.md](research/02-visual-audio.md) for the look
and sound. Each gap-fill is marked **(arcade fill)**; a value taken from the Sierra parent code is marked
**(Sierra fill)**; a plain design choice is marked **(choice)**. The index at
[research/00-index.md](research/00-index.md) lists what is still unverified.

This is a homage. All artwork, sounds, and text will be original. The app will state that it is not affiliated
with Konami, Sega, Parker Brothers, or Atari.

---

## 1. Design goals

1. **Feel like the Parker Brothers cartridge.** Dark green border, no title screen (power on lands on the
   playfield), `SLOW`/`FAST` top-left, remaining frogs top-right, `1UP` score bottom-left, a red-brick
   "sidewalk" between road and river that changes texture every level, yellow home bank with five dark
   arches, green turtles, red-brown logs, orange bulldozers, a pink racer, an orange time band next to a red
   `TIME` label, a jingle at the start of each frog and silence (effects only) while playing, five frogs,
   one or two players alternating, speed selectable at any time.
2. **Honour the canvas constraints.** Tick-based simulation on one Timer, fixed control pools, no keyboard,
   formula-driven rendering. Where the original does something canvas cannot, this document names the
   simplification.
3. **Playable in a browser and on a tablet** with mouse or touch, in landscape. Five discrete hops are taps,
   so the no-keyboard constraint costs nothing here.
4. **Keep the formula surface small enough to debug.** The tick is a short sequence of `UpdateContext`
   steps, each reading the previous step's result once.

## 2. Playfield and coordinates

The 800XL showed a 4:3 picture. The cartridge draws a 40 by 28 character playfield (320 hi-res pixels by
224 scanlines) inside a dark green border. Logical units follow the hardware so every measured value from
the research can be used directly, the same convention as the Galaxian app.

- **Logical space:** 160 **columns** (colour clocks, X) by 240 **lines** (scanlines, Y). A column is exactly
  twice as wide as a line is tall on a 4:3 display. One character cell is 4 columns by 8 lines.
- **Scale:** named formula `nfScale` = screen pixels per line. Default **2.5**, giving a playfield of
  **800 x 600** screen pixels. A column is `2 * nfScale` = 5 screen pixels. Tablets use 2 (640 x 480).
- **Mapping:** `screenX = playfieldLeft + X * 2 * nfScale`, `screenY = playfieldTop + Y * nfScale`.
- **Bands** (from the measured cartridge capture; every band is 16 lines, one hop):

```
 Y   0-23   top HUD: SLOW/FAST at left (green), remaining frog icons at right
 Y  24-39   home bank: yellow/orange hatch, five dark arches (bays)
 Y  40-55   river 5: medium logs, move right     (alligator replaces one log from level 2)
 Y  56-71   river 4: turtle pairs, move left     (last pair dives)
 Y  72-87   river 3: long logs, move right       (snake rides one log from level 3)
 Y  88-103  river 2: short logs, move right      (lady frog sits on one log)
 Y 104-119  river 1: turtle trios, move left     (last trio dives)
 Y 120-135  sidewalk: brick or stone texture, safe; snake patrols from level 3
 Y 136-151  road 4: purple cars, move left
 Y 152-167  road 3: pink racer, move right
 Y 168-183  road 2: blue cars, move left
 Y 184-199  road 1: orange bulldozers, move right
 Y 200-215  grass and timer: TIME label (red) at left, orange time band; the frog starts here
 Y 216-239  bottom HUD: 1UP score (light blue) left, 2UP indicator centre, player-2 score right
```

Row index `r` 0 to 11 from the home bank down to the start row (twelve rows): frog top edge `Y = 24 + 16 * r`.

- **Lane geometry.** Each lane's objects live on a loop of **192 + W columns** (W = object width); an object
  is drawn at screen column `X - W`, so it is fully hidden at X = 0, leaves the right edge at X = 160 + W,
  and spends 32 columns hidden before re-entering **(choice, standing in for the arcade's 256-pixel wrap on
  a 224-pixel screen)**. Objects are placed evenly: period = (192 + W) / count.
- **Object widths in columns** (from the cartridge capture, hi-res pixels halved): car 12, racer 12,
  bulldozer 12, turtle 12 per turtle (pair 24, trio 36), short log 31, medium log 39, long log 71,
  alligator 39 (replaces a medium log), frog 8, lady frog 8, fly 8, snake 16.
- **Home bays.** Five arches at 32-column pitch, centres at columns **16, 48, 80, 112, 144**, mouth 12
  columns wide. The frog (8 wide) fits with a 2-column margin each side.
- **Frog start.** Column 76 (centred, 76 to 83), row 11.

## 3. Game loop and timing model

- **One hidden Timer** `tmrGame`, `Duration 50`, `Repeat`, `AutoStart`, `AutoPause false`,
  `Start: =!ctxPaused`. `OnTimerEnd` runs one tick. The Timer is the only place that mutates game state.
- **Tick length** 50 ms (**20 ticks per second**), three 60 Hz frames per tick. All speeds are named
  formulas in columns per tick so a retune is one line and a tick change is one formula.
- **Speed table.** Cartridge speeds are unmeasured, so these are arcade speeds converted to this grid:
  columns per tick = arcade px/frame x 3 frames x (160 / 224) **(arcade fill)**. `FAST` uses the table;
  `SLOW` multiplies by `nfSlowFactor` = 0.7 **(choice; the cartridge's ratio is unknown)**.

| Lane | Object | Arcade px/frame | Columns per tick (FAST) | Screen crossing |
|---|---|---|---|---|
| river 5 | medium logs, alligator | 0.43 | 0.92 | 8.7 s |
| river 4 | turtle pairs | 0.57 | 1.22 | 6.6 s |
| river 3 | long logs | 0.53 | 1.14 | 7.0 s |
| river 2 | short logs | 0.36 | 0.77 | 10.4 s |
| river 1 | turtle trios | 0.57 | 1.22 | 6.6 s |
| road 4 | purple cars | 0.59 | 1.26 | 6.3 s |
| road 3 | racer | 1.33 average | **2.14 for 35 ticks, then 4.29 for 35 ticks** | 2.8 s average |
| road 2 | blue cars | 0.36 | 0.77 | 10.4 s |
| road 1 | bulldozers | 0.54 | 1.16 | 6.9 s |
| sidewalk | snake | 1 px per 8 frames | 0.27 | 30 s |

The racer's two-speed pulse reproduces the arcade's speed ring, where the racing lane alternates between
1 and 2 pixels per frame on a 210-frame cycle **(arcade fill)**. Speeds do not change with level; the
arcade ROM never reads the level when it sets speeds, and difficulty comes from layout and hazards
(section 10). A named formula `nfLevelSpeedBoost` (default 0 per level) is reserved in case playtesting
wants a per-level speed-up.

- **Other timings** (ticks): hop 3; squash or drown animation 30; pause after a death before the next
  frog 20; start jingle 30 (the time band starts with the jingle, as the manual says); home-arrival pause
  20; five-homes celebration 60; `200` popup 50; fly cycle 85 shown for 37; bay alligator cycle 85
  shown from 27 to 59; turtle pair dive cycle 85; turtle trio dive cycle 43; time warning at 5 s left.

- **Tick order** inside `OnTimerEnd`, as sequential `UpdateContext` steps:
  1. `sA` scalars: tick, mode countdowns, the queued hop, timer, racer phase, dive counters, bay creature
     counter, snake position.
  2. `sL` lanes: move every active lane object one step on its loop.
  3. `sF` frog: apply the hop or carry, then resolve the frog against its row (section 7) into one event:
     none, squash, drown, edge, home, bay-death, pickup, fly.
  4. `sC` commit: score, lives, bays, level, mode, timer, player swap, high score. One `UpdateContext`
     writing every context variable.

## 4. State model

All game state is context variables on the game screen (`ctx` prefix), as in Galaxian. Named formulas
(`nf` prefix) hold constants, sprite images, and static tables.

**Scalars**
- `ctxMode`: "Attract", "Jingle", "Playing", "Dying", "Home", "LevelClear", "GameOver".
- `ctxTick`, `ctxModeTicks`, `ctxStartTime`, `ctxPaused`, `ctxFrame` (animation frame, changes every 5 ticks).
- `ctxScore`, `ctxHigh`, `ctxLives`, `ctxLevel`, `ctxBays` (5-character "1"/"0" string), `ctxFast` (boolean).
- `ctxTwoPlayer`, `ctxPlayer` (1 or 2), and the saved opposite-player state `ctxScoreP2`, `ctxLivesP2`,
  `ctxLevelP2`, `ctxBaysP2`.
- `ctxFrogX` (left edge, fractional while riding), `ctxFrogRow` (0 to 12), `ctxFrogDir` ("U","D","L","R"),
  `ctxHopTicks` (3 to 0 while a hop plays), `ctxHopQueued` (one pending direction or ""), `ctxBestRow`
  (highest row reached by this frog, for hop points), `ctxHasLady`.
- `ctxTime` (ticks left, 600 at start), `ctxRacerPhase`, `ctxDivePair`, `ctxDiveTrio`, `ctxBayTimer`,
  `ctxBayCursor` (which empty bay the fly or alligator uses), `ctxSnakeX`, `ctxSnakeDir`.
- `ctxExtraAwarded`, `ctxDeathKind` ("Squash" or "Drown").

**Table `ctxLanes`** (fixed 45 rows: 9 lanes x 5 slots): `Slot`, `Lane` (1 river 5 ... 5 river 1, 6 road 4
... 9 road 1), `Index` (1 to 5), `Active`, `X` (loop position, 0 to 191), `W`, `Kind` ("Log", "Gator",
"LogSnake", "LogLady", "Pair", "Trio", "Car", "Racer", "Car2", "Dozer"), `Dives` (true for the last
turtle group of each turtle row).

**Named-formula tables**
- `nfLaneDefs`: per lane: `Dir` (+1 right, -1 left), `Speed` (columns per tick), `W`, base `Kind`.
- `nfTiers`: per tier 0 to 4 and lane: `Count`. Tier = `Mod(ctxLevel - 1, 5)`.

**Fixed pool rule:** rows are never added or removed during play. The pool is rebuilt (all 45 rows
patched once) at level start; per tick only `X` changes, by `ForAll` + `Patch`.

## 5. Frog

- **Hop.** One tap = one hop of **one row** (16 lines) vertically or **8 columns** horizontally
  **(choice; the cartridge's horizontal hop size is unverified, 8 columns keeps every bay reachable from
  the centre start)**. The hop plays over 3 ticks with the mid-hop sprite, then the rest sprite. No
  diagonals. Hops are refused: down from row 11, left below column 4, right above column 148, sideways on
  the home row.
- **Input.** A tap during a hop queues one hop, consumed when the hop lands. A second tap during the
  same hop replaces the queued one. Taps are ignored outside "Playing" and for 10 ticks after a respawn.
- **Carry.** While the frog is on a river platform its X moves with the platform every tick, fractional.
  A hop from a platform starts from the fractional X and lands on it plus or minus 8; rows are integers.
- **Edge.** Carried to X < 0 or X > 152 (right edge past column 159): death by drowning, "drifting off
  either screen edge on a river object" per the manual.
- **Lady frog.** Landing on a short log of kind "LogLady" with the frog's centre within the lady's
  8 columns picks her up: the log reverts to "Log", `ctxHasLady` = true, and the frog sprite shows her
  on its back. Reaching home with her scores 200 extra. Losing the frog loses her; she reappears on a
  short log on the next frog.
- **Death.** `ctxMode` = "Dying" for 30 ticks with the squash sprite (road) or the drown sprite (river,
  edge, timeout), then 20 ticks of pause. If frogs remain: respawn at (76, 11) with a full time band and
  the start jingle. Otherwise, in a two-player game, hand over to the other player if they have frogs;
  else "GameOver".
- **Lives.** Start with **5** (manual). **One extra frog every five levels** (on entering levels 6, 11,
  16, ...) **(Sierra fill; the cartridge manual does not mention an extra frog)**. The top-right icons
  show frogs in reserve, max 8 drawn.

## 6. Lanes and platforms

- **Layout per level.** Counts by tier, using the cartridge level-1 capture for tier 0 and the arcade
  tier tables for the rest **(arcade fill)**:

| Lane | Tier 0 (lv 1, 6, ...) | Tier 1 (lv 2, 7, ...) | Tier 2 | Tier 3 | Tier 4 (lv 5, 10, ...) |
|---|---|---|---|---|---|
| river 5 medium logs | 3 | 3 | 2 | 2 | 1 |
| river 4 turtle pairs | 4 | 5 | 4 | 3 | 3 |
| river 3 long logs | 2 | 1 | 1 | 1 | 1 |
| river 2 short logs | 3 | 3 | 3 | 2 | 2 |
| river 1 turtle trios | 4 | 3 | 3 | 3 | 2 |
| road 4 purple cars | 4 | 4 | 5 | 4 | 5 |
| road 3 racer | 1 | 2 | 2 | 3 | 4 |
| road 2 blue cars | 4 | 4 | 4 | 4 | 5 |
| road 1 bulldozers | 4 | 4 | 4 | 4 | 4 |

  At level start slot `i` of a lane with count `n` is placed at `X = (i - 1) * (192 + W) / n`, active if `i <= n`.
  Lanes 2 and 4 (turtle rows) mark their last active group `Dives = true`.
- **Movement.** `X = Mod(X + Dir * Speed * speedMult + Loop, Loop)` per tick with `Loop = 192 + W`; drawn
  at screen column `X - W`. The racer uses the pulsed speed.
- **Turtle dives.** One group per turtle row dives, on a fixed cycle from the arcade ROM **(arcade fill)**.
  Pairs: 85-tick cycle; surfaced 0 to 26, sinking 27 to 42, deep 43 to 52, **gone 53 to 58**, deep 59 to
  68, rising 69 to 84. Trios: 43-tick cycle; sinking 0 to 7, deep 8 to 12, **gone 13 to 15**, deep 16 to
  18, rising 19 to 26, surfaced 27 to 42. A group carries the frog in every state except gone; landing
  on a gone group, or being on it when it goes, drowns the frog. The sinking and deep frames warn the
  player, as the manual promises ("you'll have to hop off before the turtle dives").
- **Alligator in the river** from level 2: the first medium log in river 5 becomes kind "Gator"
  (39 columns). The body (trailing 29 columns) carries; the **head (leading 10 columns) kills**
  **(arcade fill for the zone sizes)**. At levels 2 to 4 it is an alligator on alternate laps and a log
  otherwise; from level 5 always an alligator **(arcade fill)**.
- **Snake on a log** from level 3: the first long log in river 3 becomes "LogSnake": a snake drawn on the
  log, head toward the direction of travel. Landing on the log's snake-free part carries; the snake's
  **head (6 columns) kills**; the manual allows standing on its back.
- **Snake on the sidewalk** from level 3: one snake patrols row 6 at 0.27 columns per tick, reversing at
  the edges. Touching its head kills; its back is safe (manual). Spawn chance per sidewalk visit rises
  with level as in the arcade, `(8 * level + 128) / 256` **(arcade fill)**.
- **Lady frog**: from level 2 **(choice; cartridge first level unverified, arcade gates her at 3)**, the
  second short log in river 2 carries her, re-placed on each new frog.
- **No otters.** The cartridge dropped them.
- **Sidewalk texture** cycles by level: red brick, tan brick, grey stone, then the same with shifted
  colours (manual and Kranish: "graphics change every level").

## 7. Collision

All tests are on the frog's row only, evaluated once per tick after movement, in logical columns.
The frog's hit box is inset to columns `X + 1` to `X + 7` (6 wide) **(choice)**.

| Row kind | Test | Result |
|---|---|---|
| Road (rows 7 to 10) | any active object in the lane whose span overlaps the hit box | squash |
| River (rows 1 to 5) | frog centre `X + 4` inside a platform span: ride (X += lane step each tick); platform kind Gator and centre in the head zone: drown; LogSnake and centre in the snake head: drown; turtle group in state gone: drown; no platform under the centre: drown | ride or drown |
| Sidewalk (row 6) | snake active and hit box overlaps its head 6 columns | drown (shown as squash) |
| Home row (row 0) | centre inside a bay mouth: if bay empty and no alligator head showing, **home**; if alligator head showing or bay full, death; centre outside every mouth (bush): death | home or drown |
| Any row | `ctxTime` reaches 0 | drown ("TIME OUT" is shown on the sidewalk) |
| Any river row | X < 0 or X > 152 after carry | drown |

The racer moves at most 4.3 columns per tick against a 6-column hit box, so a plain overlap test
cannot skip it; no swept test is needed. The lady pickup and the fly are resolved in the same step.

## 8. Timer

- `ctxTime` starts at **600 ticks (30 s)** per frog (manual: "approximately 30 seconds") and counts
  down while "Playing". Refilled on every new frog and on every home arrival.
- The **time band** is a Rectangle on the grass row: `TIME` label at columns 2 to 17 in red, band from
  column 44 to 141 (97 columns) in orange, shrinking from its right end toward the label.
- **Warning:** with 100 ticks (5 s) left the band turns red and the warning sound plays (manual:
  "warning sound when a few seconds remain").
- **Expiry:** the frog dies (drown animation) and `TIME OUT` shows on the sidewalk for the death ticks.
- **Bonus:** on reaching home, `10 * Floor(ctxTime / 20)` points (10 per whole remaining second).

## 9. Scoring

| Event | Points | Source |
|---|---|---|
| Forward hop onto a row this frog has not reached before | 10 | manual |
| Frog into an empty home bay | 50 | manual |
| Time bonus | 10 per remaining second | manual |
| Bonus fly in the bay the frog enters | 200 | manual |
| Lady frog carried home | 200 | manual |
| All five bays filled | 1000 | manual |
| Extra frog | every five levels | Sierra fill |

Score shown as `1UP` followed by the number, no leading zeros, bottom-left in light blue. The cartridge
has no high-score display; the app keeps a session high score and shows it only in Attract mode
**(choice)**. Scores are not capped.

Payout order on a home arrival: fly 200 if shown in that bay, 50, time bonus, lady 200, then 1000 and
level advance if the fifth bay filled.

## 10. Levels and difficulty

- Level 1 starts with tier 0 layout, fly in bays on odd levels, no alligators, no snakes.
- **Level 2 and up:** alligator in river 5; alligator head in a random empty bay on even levels; lady frog.
- **Level 3 and up:** snake on a long log and on the sidewalk.
- Tier = `Mod(level - 1, 5)`, so the layout eases briefly every sixth level, as in the arcade.
- Speeds do not change by level (section 3). `nfLevelSpeedBoost` exists for tuning.
- **Level clear:** fifth bay filled. "LevelClear" for 60 ticks: the five home frogs show their
  celebration sprite, 1000 points, then the bays empty, level + 1, sidewalk texture advances, lanes
  rebuilt for the new tier, extra frog if level is a multiple of 5 plus 1, jingle, play.
- **Home bay creature.** `ctxBayTimer` runs an 85-tick cycle; at wrap it picks the next empty bay
  (`ctxBayCursor`). Odd levels: a fly shows in that bay for ticks 0 to 36. Even levels: an alligator
  snout appears at 0, full jaws from 27, gone at 59 **(arcade fill for the cadence)**.

## 11. Screens and game flow

One screen `scrGame` with layered groups toggled by `ctxMode`.

1. **Attract:** the playfield with lanes running and no frog, exactly the cartridge's power-on view:
   `SLOW` or `FAST` top-left, five frog icons top-right, `1UP 0` bottom-left, full time band. The app
   adds a centred `PRESS START` line on the sidewalk, the session high score, and the not-affiliated line
   under the playfield. SELECT toggles `2 UP`; OPTION toggles speed.
2. **Jingle:** 30 ticks. The frog sits at the start, the start tune plays, the time band begins to drain
   (the manual: "when the music begins, so does the time band"). Then "Playing".
3. **Playing:** full simulation. PAUSE button pauses the Timer.
4. **Dying:** 30 ticks of death sprite plus 20 ticks of pause, then Jingle, or the other player's turn, or
   GameOver.
5. **Home:** 20 ticks after a bay fills, `200` popup if earned, then Jingle for the next frog.
6. **LevelClear:** 60 ticks of celebration, then the next level's Jingle.
7. **GameOver:** `GAME OVER` on the sidewalk, final scores shown; START or the playfield tap (the manual's
   FIRE) restarts. Returns to Attract after 200 ticks.

**Two players.** SELECT in Attract toggles two-player. Players alternate on every lost frog; player 1
first; each has their own score, frogs, level, and bay state; `2UP` and the right-hand score show;
the game ends when both are out of frogs.

**Console-key equivalents:** START (begin or restart), SELECT (one or two players, Attract only), OPTION
(SLOW/FAST, any time), PAUSE, RESET (back to Attract, one player). MUTE once sound exists.

## 12. Input

Canvas apps have no keyboard events, so all input is on-screen.

- **Hop cross:** four buttons to the right of the playfield (up, left, right, down), as the skeleton
  already builds.
- **Playfield tap zones:** four transparent buttons laid out around the frog each tick: the band above
  the frog's row (full width) hops up, the band below hops down, the frog's own row left of the frog hops
  left, right of it hops right. On a tablet the player taps where they want to go.
- **Keyboard trick (later milestone):** a focused Text Input with `TriggerOutput.Keypress` reading
  W/A/S/D or I/J/K/L, reset after each key, focused after START.

## 13. Visual design

Original pixel art drawn as inline SVG named formulas in `Image` controls. Sprites are authored at the
Atari's hi-res pixel width (two art pixels per logical column, one per scanline), with a black outline and
two or three shades per object, because the first 2:1 chunky pass read as blobs in the 2026-10-28 playtest.
Positions and sizes stay on the logical column grid; only the art resolution is doubled. One frog drawing is
rotated for the four facings. Every sprite is rendered to a contact sheet and a scene mock
(`tools/` scripts, output in the session scratchpad) before it is pushed.

**Palette** (from the cartridge capture, saturated; design choices where noted):

| Element | Colour |
|---|---|
| Border and HUD background | dark green #004301 |
| Water | blue #321FFF |
| Home bank | yellow #FFC500 hatch with red #FF0000, arches black |
| Logs (level 1) | red-brown #E00800 top, #B12000 underside, light end caps |
| Turtles (level 1) | green #428300 shell, yellow #FFC500 legs; later levels grey, then orange |
| Sidewalk | red brick #660D00 on black; tan brick #C8A060; grey stone #8C8C8C |
| Road | black |
| Purple cars | #A81DE3 body, white windows |
| Racer | pink #FF60C0 with white |
| Blue cars | #5141FF body, white windows |
| Bulldozers | orange #FF8900 with grey blade |
| Grass row | dark green #004301 |
| TIME label | red #FF0000; time band orange #FF8900, red when under 5 s |
| Frog | green #40C040 body, yellow #F0E040 eyes; lady frog pink #FF80C0; dead frog yellow |
| Alligator | brown #7A4A1E with white teeth; snake yellow-tan #D8B860 |
| Fly | dark #303030 with cyan wings |
| SLOW/FAST text | green #40C040; score text light blue #80C0FF |

**Sprites** (bitmap pixels, two per column): frog rest and mid-hop 16x16, rotated for the four facings;
the lady frog drawn as a pink overlay riding on the frog; frog in bay (front view) and its celebration
frame; squash 2 frames; drown 2 frames (yellow frog with white droplets); car, blue car, racer, bulldozer
(12 x 16); turtle pair and trio with 3 paddle frames plus sinking and deep frames (24 and 36 wide);
short, medium, long log (31, 39, 71); alligator (39); long log with snake (71); short log with lady (31);
sidewalk snake 2 frames (16); fly (8); bay alligator snout and jaws (12); `200` popup; life icon (4 x 8).
The home bank and the sidewalk are one wide SVG each with a repeating pattern, swapped by level.

**Text:** `Font.'Courier New'` bold for HUD labels, letter-spaced; the cartridge's text is the stock
Atari character set, so a plain monospace reads right.

## 14. Audio

Original synthesized effects and tunes, modelled on the cartridge's behaviour (jingle at the start,
effects only during play):

| Effect | Behaviour | Trigger |
|---|---|---|
| Start jingle | 1.5 s two-voice bouncy phrase, original melody | Jingle mode |
| Hop | 60 ms pitch slide up | each hop |
| Squash | low buzz 0.4 s | road death |
| Drown | three falling tones 0.8 s | river death, edge, timeout |
| Time warning | repeating two-pitch tick | last 5 s |
| Home | bright chime | bay filled |
| Five homes | 2 s fanfare | level clear |
| Lady pickup | low boop | pickup |
| Bonus | short rising arpeggio | fly or lady 200 |
| Extra frog | rising beeps | every five levels |
| Game over | 4-bar sad phrase | game over |

Each is an `Audio` control with `Start` bound to a one-tick boolean flag from the commit step, gated by a
MUTE toggle. Media files cannot be pushed through YAML (Galaxian finding), so the clips are synthesized by
`tools/sounds.py` and embedded as WAV data URIs in named formulas, the same technique as the sprites. The
original's Japanese children's songs and anime themes are not reproduced; every melody is original.

## 15. Persistence

- Version 1: session high score in `ctxHigh`.
- Version 2: Dataverse table `wrk_froggerscore` in the `Frogger` solution (Score, Player, Level, Date),
  written at game over when the score beats the stored best, read at app start.

## 16. Deliberate deviations and gap-fills

| Original (Parker Brothers cartridge) | This app | Reason |
|---|---|---|
| 60 frames per second | 20 ticks per second | Timer control floor |
| Joystick, return to centre between hops | Tap buttons and tap zones, one queued hop | No keyboard or hold events |
| Console keys START, SELECT, OPTION | On-screen buttons | No keyboard events |
| Lane speeds, counts after level 1, dive cycles, alligator and snake zones, bay creature cadence | Arcade ROM values scaled to the Atari grid | Cartridge timings unmeasured |
| SLOW/FAST ratio | 0.7 | Unknown |
| Horizontal hop size | 8 columns | Unverified |
| Extra frog | every five levels | Sierra parent code; cartridge silent |
| Lady frog first level | 2 | Unverified |
| No high score display | Session high score in Attract only | Convenience |
| No attract text | `PRESS START` and not-affiliated line | Needed in a browser |
| Start jingle melody, all effects | Original compositions | Rights |

## 17. Acceptance criteria

1. The playfield shows the thirteen bands at the measured positions with the cartridge's colours, the
   dark green border, `SLOW`/`FAST` top-left, frog icons top-right, `1UP` score bottom-left, the red
   `TIME` label and orange band on the grass row.
2. Nine lanes run with the tier-0 counts and directions; objects wrap seamlessly on the 192-column loop.
3. The frog hops one row or 8 columns per tap, with a 3-tick animation, one queued hop, no diagonals,
   and refuses hops off the field or sideways on the home row.
4. Road contact squashes; river without a platform drowns; platforms carry with fractional X; the screen
   edge kills; the last turtle group of each row dives on its cycle and drowns a rider while gone.
5. Home bays accept a centred frog, kill on the bush, on a full bay, and on a shown alligator head;
   the fly pays 200; the fifth bay pays 1000 and advances the level.
6. The time band drains over 30 s, turns red at 5 s with the warning, kills at 0 with `TIME OUT`, and
   pays 10 per remaining second on arrival.
7. Level 2 brings the river alligator and the bay alligator on even levels; level 3 brings the snakes;
   the sidewalk texture changes each level; tiers repeat every five levels.
8. The lady frog can be picked up, rides on the frog, and pays 200 at home.
9. Five frogs, an extra frog every five levels, two-player alternating with separate state, OPTION
   changes speed mid-game, RESET returns to one player.
10. Attract shows the running playfield and `PRESS START`; game over shows `GAME OVER` and restarts on
    START.
11. The tps readout stays near 20 for a full level on a mid-range laptop browser.

## 18. Build plan

| Milestone | Scope |
|---|---|
| M1 Skeleton | Studio app in Workbench, coauthoring on, `scrGame`, `tmrGame`, scale formulas, bands and HUD, mode machine, console keys, tps readout |
| M2 Lanes | `ctxLanes` pool, `nfLaneDefs`, `nfTiers`, movement and wrap, sprites for logs, turtles, vehicles, racer pulse |
| M3 Frog | hop cross and tap zones, hop animation, queue, carry, road and river collision, deaths, respawn, lives |
| M4 Home and timer | bays, bush and full-bay deaths, time band, warning, timeout, scoring, level clear and tiers |
| M5 Hazards | turtle dives, river alligator, bay fly and alligator, snakes, lady frog, extra frog, sidewalk textures |
| M6 Flow and polish | attract, jingle phase, two players, OPTION speed, game over, keyboard trick, sounds |
| M7 Persistence | Dataverse high score table in the Frogger solution |

Each milestone ends with a playable build pushed through `compile_canvas`, saved in Studio, and checked
against the acceptance criteria it covers.

---

## 19. Implementation status (2026-10-28)

| Milestone | Status | Notes |
|---|---|---|
| M1 Skeleton | Done | App `80f9c4ce-e9a8-4dd1-a8d2-a9bb969fc958` in the Frogger solution; bands, HUD, mode machine, console keys, tps label |
| M2 Lanes | Done | 45-slot pool, tier counts, per-lane loop of 192 + W, racer two-speed pulse, log/turtle/vehicle sprites |
| M3 Frog | Done | Hop cross and tap zones, 3-tick hop, one queued hop, carry, road/river/edge collisions, deaths, respawn, lives |
| M4 Home and timer | Done | Bays with bush and full-bay deaths, time band, 5 s warning, TIME OUT, scoring, level clear, tiers, sidewalk textures |
| M5 Hazards | Done | Turtle dives on the arcade cycles, river alligator (lap parity at levels 2 to 4, always from 5), snake on the first long log and on the sidewalk from level 3, lady frog on the first short log from level 2, bay fly on odd and bay alligator on even levels, extra frog every five levels. Compiled 2026-10-28 |
| M6 Flow and polish | Done | Sound (eleven synthesized clips as WAV data URIs, Audio controls with tick-counter Start, MUTE/UNMUTE), two-player alternating with SELECT and 1UP/2UP HUD, keyboard text box behind a KEYS toggle, debug LEVEL+ key kept at the user's request. Compiled and saved 2026-10-28 |
| M7 Persistence | Not started | |

First build validated by `compile_canvas` and applied to the live Studio session on 2026-10-28; app checker
clean; accessibility checker reports only decorative-image tab stops and transparent tap-zone focus borders,
as in Galaxian. Playtested by the user 2026-10-28: tick rate, hops, speeds, hazards, and sound confirmed. Exported as solution `Frogger` (app schema name `wrk_frogger_103d1`) and published to the repo.
