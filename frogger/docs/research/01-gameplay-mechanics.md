# Frogger (arcade, 1981) — gameplay mechanics and numbers

Research note for the canvas Power Apps rebuild. Date: 2026-10-28.
Target: Konami GX392 "Frogger" (Sega/Gremlin in North America), MAME set `frogger`.

How to read this file. Three grades of evidence are used:

- **ROM** — read directly from the annotated Z80 disassembly of the main-board ROM
  (computerarcheology.com / qarl `arcade-js`, cross-checked frame-by-frame against MAME 0.288 by its
  authors). Byte values are reliable; the *meaning* of a routine is the annotator's (partly AI-generated)
  reading and can be wrong. Where I re-derived a meaning myself it is marked **(derived)**.
- **MAME** — from the MAME `galaxian.cpp` driver source.
- **Community** — Wikipedia, arcade-history.com, StrategyWiki, Codex Gamicus, all80s, fan guides. Good
  for rules of thumb, weak on numbers.
- **(unverified)** — nothing solid found; do not build on it without measuring in MAME.

---

## 1. Hardware and playfield

| Item | Value | Grade |
|---|---|---|
| Main CPU | Z80 @ 3.072 MHz (18.432 MHz / 6) | MAME, ROM |
| Frame rate | 60.606 Hz (VSYNC = HSYNC/132/2, HSYNC = 16 kHz) | MAME |
| Native raster | 256 x 224, displayed rotated 90 deg -> **224 wide x 256 tall** (vertical monitor) | MAME, ROM |
| Tilemap | 32 x 32 cells of 8 x 8 px; a game "lane" is one tilemap column = 2 tiles (16 px) tall on screen; per-lane hardware scroll | ROM |
| Hardware sprites | 8 (frog, fly/goal popup, 3 roaming creatures, ...) | ROM |
| Playable X range | frog is "lost" when X < 8 or X >= 0xE7 (231): 224 px wide play area | ROM |
| Cell size | **16 x 16 px**; one hop = 16 px | ROM |
| Columns | 224 / 16 = 14 cells across | derived |

### Rows (13 playable rows, 16 px each; frog sprite Y as stored in RAM, top = small)

| Frog Y | Row | Contents |
|---|---|---|
| 0x20 (fully home when Y < 0x2A) | Home bank | 5 bays separated by bushes |
| 0x30 | River 5 (top) | medium logs, move right; **crocodile** here from level 2 (ROM) |
| 0x40 | River 4 | turtle pairs, move left |
| 0x50 | River 3 | long logs, move right (snake rides here, community) |
| 0x60 | River 2 | short logs, move right (lady frog here, community) |
| 0x70 | River 1 | turtle triples, move left |
| 0x80 | Median | safe; pays no hop points; snake patrols here at level 3+ (community) |
| 0x90 | Road 5 (top) | trucks, move left |
| 0xA0 | Road 4 | white racing car(s), move right |
| 0xB0 | Road 3 | purple/pink cars, move left |
| 0xC0 | Road 2 | bulldozers, move right |
| 0xD0 | Road 1 | yellow cars, move left |
| 0xE0 | Start sidewalk | frog spawns at X = 0x80 (128), Y = 0xE0 |

Row Y values, river/road split at Y = 0x80, carry band [0x30, 0x73), spawn point (128, 224) and the
"fully home" line 0x2A are ROM. Lane object names and directions: the ROM orders its 11 lane objects
as 0..10 with directions R,L,R,R,L,(spacer),L,R,L,R,L; mapping object 0 = top river row downwards
reproduces the known arcade layout exactly (median = object 5 spacer), so object order = top to bottom
**(derived)**. Arcade-history's tip page says river lanes 1/3/5 move right-to-left, which contradicts
every other source and the ROM direction table; treat it as an error.

### Home bays

Five bays, 48 px apart. The goal handler accepts the frog only if its X is inside an **8 px window**
per bay (ROM, inclusive): bay1 0x15-0x1C, bay2 0x45-0x4C, bay3 0x75-0x7C, bay4 0xA5-0xAC, bay5
0xD5-0xDC (hardware sprite X space, which is mirrored relative to tile columns, so treat these as
"centre +/- 4 px"). An X between windows (bush) with Y < 0x2A kills the frog. Y must be < 0x2A, i.e.
the hop from row 0x30 must complete. An already-filled bay: the handler simply returns no award; the
community sources agree the frog dies (Wikipedia: "jumping into a home already occupied"). So
**alignment tolerance = +/- 4 px of a 16 px cell** (ROM, derived).

---

## 2. Frog

| Item | Value | Grade |
|---|---|---|
| Hop length | 16 px (one cell) | ROM |
| Hop animation | reload counter = 9; frog moves 2 px/frame while counter > 0 after decrement -> 8 moving frames (16 px) + 1 landing frame. ~0.15 s per hop | ROM |
| Input model | one press = one hop. While a hop is in flight the same direction only continues it; after landing an "arrival latch" blocks re-trigger until the stick is released (latch cleared when the direction is not pressed). No auto-repeat while held | ROM |
| Diagonal | no (4-way stick; UP is ignored while a LEFT/RIGHT hop is in flight) | ROM, MAME |
| Hop refused | DOWN at Y >= 0xF0; RIGHT at X >= 0xE0 or Y < 0x30; LEFT at X < 0x20 or Y < 0x30 (no sideways hops on the home row) | ROM |
| Input lock after respawn / after home | 0x10 (16) frames input lock; 0x20 (32) frames "gated countdown" after a home arrival | ROM |
| Carry on platforms | each frame the lane mover adds the object's pixel step to the frog X when the frog's row matches the object's row and it is riding (band [0x30,0x73)); a hop that is mid-flight still gets carried when its row low-nibble is < 3 or >= 0xC | ROM |
| Death by edge | carried to X < 8 or X >= 231 -> lost | ROM |
| Death animation | 16 frames per phase; squash = 6 phases (96 fr, ~1.6 s), drown = 5 phases (80 fr, ~1.3 s); then a 0xD8 = 216 frame (~3.6 s) sound pause before the next frog | ROM |
| Respawn | frog reset to (128, 224), timer bar refilled, high-water row mark reset | ROM |
| Known quirk | "the player can hang off the left side of a turtle, but attempting the same on the right side results in death" | community (arcade-history) |

Collision model (ROM, derived from `resolveFrogMoveAgainstLanes`):

- The lane test runs only when the frog is mostly inside a row (low nibble of Y+15 >= 5); mid-hop
  between rows nothing is tested.
- Road band (Y >= 0x80): the lane's object list is scanned against the frog's X band; any object in
  band -> HOLD (death). Clear lane -> safe.
- River band (Y < 0x80): object in band -> frog rides it (delegates to the carry); **clear lane ->
  drown**. The X band width used is not stated by the annotator **(unverified; measure in MAME)**.
- Crocodile (top row): tested with the frog centre (X+8): inside [crocX-32, crocX-8) = back, rides;
  [crocX-8, crocX+8] = head, dies.
- Roaming creature (snake/otter): same row and object X within [frogX, frogX+16) -> death.

---

## 3. Timer

| Item | Value | Grade |
|---|---|---|
| Timer length | **60 units x 32 frames = 1920 frames = 31.7 s** at 60.606 Hz. Seed word 0x3C20 ("sixty steps of thirty-two frames each"), display byte starts at BCD 60 | ROM |
| Bar | 15 tiles, each drained in 4 quarter-steps (tiles 0x10/0x0F/0x0E/0x0D) -> 60 visible steps | ROM |
| Low-time warning | tone when 10 units remain (~5.3 s) | ROM |
| Reset | re-seeded on every new frog and after every home arrival | ROM |
| Expiry | bar drained -> "TIME" strip drawn, HOLD flag set -> frog dies (community: "running out of time" costs a life) | ROM + community |
| Time bonus | remaining units are paid as BCD units of 10 points = **10 points per unused unit (~0.53 s)**. Matches Wikipedia "10 points per unused 1/2 second" | ROM |
| Per-level change | the seed 0x3C20 is a constant in the one-shot field init; no level dependence found. Claims that "60 seconds at level 1" (arcade-history) or "time gets shorter on later rounds" (ZX81 review) are not supported for the arcade | ROM / (unverified) |

So the user's "30-unit time bar, 60 seconds at level 1" is wrong on both counts for the arcade: it is
~32 s, shown as 60 half-second units on a 15-tile bar.

---

## 4. Scoring

Scores are stored as BCD value/10 (ROM), so all awards are multiples of 10.

| Event | Points | Grade |
|---|---|---|
| Forward hop onto a new furthest row (rows 0xD0..0x30; the median 0x80 pays nothing) | 10 | ROM, community |
| Max from hops per frog | 10 scored rows x 10 = 100 ("max 100 per home") | derived + arcade-history |
| Frog home | 50 | ROM (0x05), community |
| Fly eaten (frog enters the bay while the fly is shown there) | 200 | ROM (0x20), community |
| Lady frog escorted home | 200 | community (arcade-history, Wikipedia, StrategyWiki) |
| Time bonus | 10 x remaining units | ROM, community |
| All five frogs home | 1000 | ROM (0x0100), community |
| Extra frog | **once per game at 20,000** (ROM constant 0x2000, award latch per player). No DIP for it | ROM; Wikipedia agrees; all80s "10K and 20K" is wrong |
| Score rollover | 99,990 max display; higher scores keep the last five digits | community (Wikipedia) |

Order of payout on a home arrival (ROM): fly bonus (if any) -> flat 50 -> time bonus strip -> 1000 if
it was the fifth bay -> board advance.

---

## 5. Lanes: per-level layout tables

### 5a. Layout tiers (ROM data, $2260 pointer table -> five 33-byte blocks)

The ROM holds five "lane parameter" blocks selected by a **difficulty tier 0..4**; the tier is
`(level - 1) mod 5` (incremented on every board clear, "wrapping to 0 at 5"). This is the mechanism
behind Wikipedia's "after five levels, the difficulty briefly eases". Each block is 11 triples, one
per lane object, in object order 0..10 (top river row -> bottom road row, object 5 = median spacer).

Triple meaning (ROM annotation: "column stride / rows per column / columns to stamp"; derived to
screen terms): **byte0 / 0x20 x 8 = gap between objects in px, byte1 x 8 = object length in px, byte2 =
number of objects** in the lane's 256 px wrap loop. The derived reading fits level 1 perfectly
(long logs: 2 x (96 + 32) = 256; turtle triples: 4 x (48 + 16) = 256) but tier 1's turtle triples
3 x (48 + 48) = 288 overflow the loop, so either the loop is longer than 256 px or the last gap is
clipped **(unverified)**. Raw bytes are given so you can re-derive.

Tier 0 (levels 1, 6, 11, ...):

| Obj | Lane | Dir | Raw | Gap px | Length px | Count |
|---|---|---|---|---|---|---|
| 0 | River 5 medium logs | R | 60 08 03 | 24 | 64 (4 cells) | 3 |
| 1 | River 4 turtle pairs | L | 60 04 04 | 24 | 32 (2 turtles) | 4 |
| 2 | River 3 long logs | R | 80 0C 02 | 32 | 96 (6 cells) | 2 |
| 3 | River 2 short logs | R | 80 06 03 | 32 | 48 (3 cells) | 3 |
| 4 | River 1 turtle triples | L | 40 06 04 | 16 | 48 (3 turtles) | 4 |
| 5 | Median (spacer) | - | 80 02 04 | - | - | - |
| 6 | Road 5 trucks | L | E0 04 02 | 56 | 32 (2 cells) | 2 |
| 7 | Road 4 racing car | R | 60 02 01 | 24 | 16 | **1** |
| 8 | Road 3 purple cars | L | C0 02 03 | 48 | 16 | 3 |
| 9 | Road 2 bulldozers | R | C0 02 03 | 48 | 16 | 3 |
| 10 | Road 1 yellow cars | L | E0 02 03 | 56 | 16 | 3 |

Tiers 1-4 (same columns; only gap/count change, lengths are identical in all tiers):

| Obj | Tier 1 (lv 2,7..) | Tier 2 (lv 3,8..) | Tier 3 (lv 4,9..) | Tier 4 (lv 5,10..) |
|---|---|---|---|---|
| 0 medium logs | 60 08 03 -> gap 24, x3 | 60 08 02 -> gap 24, x2 | 60 08 02 -> x2 | 60 08 01 -> **x1** |
| 1 turtle pairs | 40 04 05 -> gap 16, x5 | 80 04 04 -> gap 32, x4 | A0 04 03 -> gap 40, x3 | E0 04 03 -> gap 56, x3 |
| 2 long logs | 80 0C 01 -> **x1** | 80 0C 01 -> x1 | 80 0C 01 -> x1 | 80 0C 01 -> x1 |
| 3 short logs | 60 06 03 -> gap 24, x3 | C0 06 03 -> gap 48, x3 | E0 06 02 -> gap 56, x2 | A0 06 02 -> gap 40, x2 |
| 4 turtle triples | C0 06 03 -> gap 48, x3 | 60 06 03 -> gap 24, x3 | 80 06 03 -> gap 32, x3 | E0 06 02 -> gap 56, x2 |
| 6 trucks | E0 04 03 -> gap 56, x3 | A0 04 03 -> gap 40, x3 | 80 04 04 -> gap 32, x4 | 60 04 03 -> gap 24, x3 |
| 7 racing cars | 60 02 02 -> x2 | E0 02 02 -> gap 56, x2 | C0 02 03 -> gap 48, x3 | A0 02 04 -> gap 40, x4 |
| 8 purple cars | E0 02 04 -> gap 56, x4 | A0 02 05 -> gap 40, x5 | E0 02 04 -> x4 | 80 02 05 -> gap 32, x5 |
| 9 bulldozers | C0 02 04 -> gap 48, x4 | E0 02 04 -> gap 56, x4 | A0 02 04 -> gap 40, x4 | C0 02 04 -> gap 48, x4 |
| 10 yellow cars | E0 02 04 -> gap 56, x4 | C0 02 04 -> gap 48, x4 | E0 02 04 -> x4 | A0 02 05 -> gap 40, x5 |

Pattern: higher tiers have **fewer and sparser river platforms, more road vehicles**. Arcade-history's
"fewer platforms are available to land on in later levels" matches.

### 5b. Lane speeds

This is the weakest part of the record. What the ROM shows (ROM, interpretation derived):

- Each lane object has a **control byte**: low nibble `c` = speed; bit 4 clear -> `c` px/frame;
  bit 4 set -> 1 px every `c` frames (a per-lane countdown implements the fractional rate).
- The 11 control bytes are **not** in the tier tables. They are copied from a ring of 11-byte
  "frames" at ROM $186B: a 21-frame timer steps a 10-slot index (frames 0..8 are loaded; the wrap
  slot loads nothing, so frame 8 stays for 42 frames). The ring is reset once per game and never
  depends on the tier. 21 frames exist in ROM but only the first 10 slots are reachable.
- Averaging the ring over its 210-frame cycle gives (px/frame -> px/s at 60.606 Hz):

| Obj | Lane | Avg px/frame | px/s | Min..max px/frame | Screen crossing (224 px) |
|---|---|---|---|---|---|
| 0 | medium logs | 0.43 | 26 | 0.33..0.50 | 8.5 s |
| 1 | turtle pairs | 0.57 | 34 | 0.33..1.00 | 6.5 s |
| 2 | long logs | 0.53 | 32 | 0.33..1.00 | 7.0 s |
| 3 | short logs | 0.36 | 22 | 0.17..0.50 | 10.2 s |
| 4 | turtle triples | 0.57 | 34 | 0.33..1.00 | 6.5 s |
| 6 | trucks | 0.52 | 31 | 0.33..1.00 | 7.2 s |
| 7 | racing car | 1.33 | 81 | 0.33..2.00 | 2.8 s |
| 8 | purple cars | 0.59 | 36 | 0.25..1.00 | 6.2 s |
| 9 | bulldozers | 0.54 | 33 | 0.20..1.00 | 6.9 s |
| 10 | yellow cars | 0.36 | 22 | 0.17..0.50 | 10.3 s |

(Recomputed 2026-10-28 from the nine reachable tables listed in [05-source-code.md](05-source-code.md)
section 4.3, table 8 weighted twice because it holds for 42 frames. An earlier draft of this table
mis-decoded the bytes and made the purple cars faster than the racing car; that is not what the ROM says.)

**Reading:** the racing car is the fastest lane and pulses between 1 and 2 px/frame on alternate
tables, which is the "white cars speed up" players report. Trucks are not slow in the ROM (0.52 px/f),
they only feel slow because they are long. The river platforms all sit at 0.36 to 0.57 px/f; the short
logs are the slow platform. **What the ring does not contain is any per-level speed-up**: the control
bytes never depend on the tier. Difficulty comes from the tier layouts (fewer and shorter platforms,
denser traffic) and the creature spawn rate, not from speed. Community sources that say "faster each
round" may be describing the sparser layouts; confirm by frame-stepping levels 1 and 6 in MAME
**(unverified)**.

Speed-up with time: arcade-history and Codex Gamicus both say the lane-4 racing cars accelerate when
the player takes too long to fill the bays; not located in the ROM **(unverified)**.

---

## 6. Hazards and bonuses by level

Level counter is 1-based (ROM 0x83B7 starts at 1, +1 per board clear).

| Hazard | First level | Behaviour | Grade |
|---|---|---|---|
| Diving turtles | level 1 | some turtle groups submerge periodically; a frog on a fully submerged group drowns. Fan guides: ~3 s up / ~2 s down; a remake uses 4 s / 1.5 s. Dive cycle fixed per group, group dives together | community only; not located in the ROM **(unverified)** |
| Fly in a home bay | level 1 (odd levels only per ROM: level bit 0 set -> fly path) | shows in an empty bay for 112 of a 256-frame cycle (~1.85 s of 4.2 s); bay chosen by a 6-phase cursor (5 bays + rest); entering that bay = 200 | ROM |
| Crocodile head in a home bay | level 2 (even levels per ROM: level bit 0 clear -> gator path) | emerging stamp at cycle frame 0, full gator at 80, erased at 176 of 256 (~2.9 s shown, ~1.3 s clear); entering while shown = death. Quirk: if it vanishes between take-off and landing the frog dies *and* the bay counts (community) | ROM + community |
| Crocodile in the river (top row) | level 2 | tile-animated creature in river row 5; at levels 2-4 it alternates with a log every cycle, from level 5 it is always the croc. Emerges over 8 tile-pair steps, one step every `(c x 8)` frames where `c` = row-5 speed nibble (typically 16-24 fr -> 2-3 s to surface). Ride the body, die on the head | ROM (derived); fandom wiki agrees "from the second level, farthest river lane" |
| Snake, otter (roaming hardware-sprite creatures) | level 3; second roamer from level 6 | spawn when idle, after a cooldown, if PRNG roll <= 8 x level + 128 (so more frequent per level, saturating ~level 16); 5 kinds (variants 0-4; which is snake/otter/lady frog/... **unverified**); step 1 px every 8 frames (7.6 px/s) between band edges, despawn on arrival; touching one on the same row = death | ROM; community: snake on the median at level 3 or riding the long log (arcade-history), "snakes and otters from the third round" (fandom) |
| Lady frog | community: appears on a river-2 short log; hop on her, carry her home = 200 | the ROM has an always-running "rideable object" slot (mount test +20 px ahead/4 px behind, within 16 px) gated at level >= 3; first level is **(unverified)** | community + ROM |
| Otter | community: swims in the river and eats a frog on a log/turtle (ColecoVision manual); Atari Starpath port: from level 3 in the centre row, fast, right to left | arcade specifics **(unverified)** |

Level cycle: layout tier repeats every 5 levels; creature density and count keep growing; no end.

---

## 7. Lives, DIP switches, settings

MAME `frogger` input ports (MAME):

| Switch | Options | Default |
|---|---|---|
| Lives | 3 / 5 / 7 / 256 (cheat) | 3 |
| Coinage | A 1/1 B 1/1 C 1/1; A 2/1 B 2/1 C 2/1; A 2/1 B 1/3 C 2/1; A 1/1 B 1/6 C 1/1 | 1/1 |
| Cabinet | Upright / Cocktail | Upright |

There is **no difficulty switch and no bonus-life switch**; the extra life is fixed at 20,000, once.
Lives DIP table in ROM: 03 05 07 FF. Lives row on screen caps at 15 markers.
Twin Galaxies / tournament setting is reported as **5 lives** (RetroAchievements forum, CAG contest
pages; the CAG page itself could not be fetched) **(unverified)**. Record holders: Pat Laffaye
1,029,990 (2017) after trading the record with Donald Hayes; the game's display rolls at 100,000.

---

## 8. Attract mode and demo (brief)

ROM: boot enters mode 3 "SCORE RANKING" (5 high-score entries with " PTS"), then a point-table screen
(10 PTS / 50 PTS / 1000 PTS), then mode 0 attract-demo: the board is built and a scripted frog
auto-hops from a hop script at $2E68 (hop codes for L/R/U/D, 48-frame dwell between scripted hops,
32-frame dwell between demo cells) with input, collisions and the timer frozen. Credits present ->
"PUSH START" idle. Two-player games alternate per frog with separate bay/lane state.

---

## 9. Open questions for the Power Apps build

1. **Lane speeds per level.** Measure in MAME (frame-step, read object X) for levels 1-6: px/frame per
   lane and whether lane 4 speeds up with elapsed time. Until then use the ordering in 5b and tune by
   feel. The 20 tps tick means fractional px/tick anyway; store speeds as named formulas.
2. **Turtle dive schedule.** Which groups dive (per tier), surface/submerge durations, whether the
   cycle changes per level. Nothing in the extracted ROM covers it; measure in MAME.
3. **Lane loop length / initial phase.** Confirm whether the lane wrap loop is 256 px with the "gap"
   reading above (tier 1 turtle triples overflow) and where objects start at board load.
4. **Collision band width** for road/river tests (how many px of overlap kill or carry). The 8 px home
   window and the croc 32/16 px zones are known; the car/log bands are not. Decide: centre-point test
   vs overlap threshold, and swept test for the racing car at 20 tps.
5. **Roaming creature identities** (which of the 5 variants is snake / otter / lady frog), their rows,
   and the lady frog's first level and 200-point rule. Also whether the lady frog rides a log (moves
   with it) in the arcade.
6. **Home-bay creature cadence**: when the 6-phase bay cursor advances (per frame vs per cycle) and
   whether odd/even-level fly/gator alternation is real; verify in MAME on levels 1-3.
7. **Death on an occupied bay** is community-only (ROM path just "returns"); confirm, plus the
   "croc vanishes mid-hop" edge case.
8. **Timer at 20 tps**: 60 units x 32 frames = 1.6 tps-ticks... use 60 units x ~10.6 ticks (0.528 s)
   and keep the 15-tile bar with quarter fills, or simplify to 60 ticks of 0.5 s. Decide the time-over
   death delay.
9. **Hop at 20 tps**: 9 frames = 0.15 s -> ~3 ticks; decide 2 or 3 ticks per hop and whether carry
   applies mid-hop.
10. **Version choice**: the Atari 8-bit port (Parker Brothers 1983 / Sierra 1982) differs in lane
    count/speeds/hazards; this file covers the arcade only.

---

## Sources

- computerarcheology.com, Frogger: main page, Hardware, RAM use, annotated code —
  https://computerarcheology.com/Arcade/Frogger/ , .../Hardware.html , .../RAMUse.html , .../Code.html
- qarl/arcade-js (frame-checked JS translation of the ROM; notes `mechanisms.md`, `gameplay.md`,
  `ca-lines.md`, `DONE.md`) — https://github.com/qarl/arcade-js/tree/main/games/frogger
- MAME source, `src/mame/galaxian/galaxian.cpp` and `galaxian.h` (Frogger input ports, screen timing) —
  https://github.com/mamedev/mame/blob/master/src/mame/galaxian/galaxian.cpp
- Wikipedia, "Frogger" — https://en.wikipedia.org/wiki/Frogger
- arcade-history.com, Frogger [Model GX392] — https://www.arcade-history.com/game/879/frogger-model-gx392
- StrategyWiki, Frogger/Gameplay (via search snippets; page blocks fetch) — https://strategywiki.org/wiki/Frogger/Gameplay
- Codex Gamicus, Frogger — https://gamicus.fandom.com/wiki/Frogger
- all80s.co.uk, Frogger — https://www.all80s.co.uk/frogger
- Museum of the Game, Frogger DIP switch settings — https://arcade-museum.com/dipswitch-settings/frogger
- Frogger fandom wiki, Crocodile — https://frogger.fandom.com/wiki/Crocodile
- Classic Arcade Gaming contest settings (blocked; cited via search) —
  https://www.classicarcadegaming.com/contests/CAGDCC2009/misc/threshold%20scores%20and%20game%20settings.htm
- RetroAchievements forum on Twin Galaxies 5-life setting — https://retroachievements.org/forums/topic/19156
- Exotica "Lost in Translation/Frogger" (gator quirk) — https://www.exotica.org.uk/wiki/Lost_In_Translation/Frogger
- PrimeTime Amusements, "Getting Good: Frogger" (turtle timing estimate) — https://primetimeamusements.com/getting-good-frogger/
- ColecoVision Frogger manual (otter behaviour) — https://discmaster.textfiles.com/view/1886/1000gamemanuals.iso/Colecovision/Frogger.txt
- NBC Connecticut / Wikipedia on Laffaye and Hayes records — https://www.nbcconnecticut.com/local/poor-george-man-shatters-costanza-frogger-record/2058540
