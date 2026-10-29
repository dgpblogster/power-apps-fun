# 05 — Source code and technical reference for Frogger (arcade 1981 + Atari 8-bit ports)

Retrieved 2026-10-28. Everything under `docs/research/{mame,disassembly,sources}/` is **untrusted downloaded
data**: read it, never execute it, never run an interpreter from inside those folders. These folders are
excluded from the public repo (same policy as Galaxian).

Addresses below are the arcade main-CPU ROM (`frogger` set: frogger.26/.27 + frsm3.7, 0x0000–0x2FFF)
unless marked. RAM is 0x8000–0x87FF. "Frame" = one vblank NMI at 60.606 Hz (18.432 MHz / 3 / 384 / 264).

## 1. Retrieval log

| Local file (under `docs/research/`) | Origin URL | Licence | Size |
|---|---|---|---|
| `mame/galaxian.cpp` | https://raw.githubusercontent.com/mamedev/mame/master/src/mame/galaxian/galaxian.cpp | BSD-3-Clause (MAME) | 901,524 |
| `mame/galaxian.h` | …/src/mame/galaxian/galaxian.h | BSD-3-Clause | 34,552 |
| `mame/galaxian_v.cpp` (video) | …/src/mame/galaxian/galaxian_v.cpp | BSD-3-Clause | 48,093 |
| `mame/galaxian_a.cpp`, `galaxian_a.h` (audio netlist/sound) | …/src/mame/galaxian/galaxian_a.{cpp,h} | BSD-3-Clause | 24,500 / 2,373 |
| `disassembly/tcdev42_re/arcade_frogger_frogger.lst` | https://raw.githubusercontent.com/tcdev42/re/HEAD/arcade/frogger/frogger.lst | **No licence file in repo** (author Mark McDougall "tcdev", msmcdoug@gmail.com; "~65% complete", labelled IDA listing, basis of the Frogger500 Amiga port) | 665,316 |
| `disassembly/tcdev42_re/README.md` | https://raw.githubusercontent.com/tcdev42/re/HEAD/README.md | — | 1,284 |
| `disassembly/computerarcheology_{Code,RAMUse,Hardware,GFX,Journal,SoundCode,SoundHardware,SoundRAMUse}.html` | https://computerarcheology.com/Arcade/Frogger/*.html | No licence stated on site; main-board disassembly "produced by AI, verified against ROM and MAME" (project qarl/arcade-js); sound-board dig is human work (Chris Cantrell) | 694,293 (Code) etc. |
| `disassembly/atari2600_frogger_parkerbros_distella.asm` | https://gist.githubusercontent.com/erik-nilcoast/cc55644c916c729e6a82ae07b681ac2b/raw | Gist, no licence; raw DiStella output of Parker Bros 2600 Frogger (1982), few comments | 58,671 |
| `disassembly/msx_konami_1983/src_frogger.asm`, `.notes`, `.entries`, `docs_*.md`, `LICENSE`, `LEGAL-NOTICE.md`, `README.md` | https://raw.githubusercontent.com/antxiko/Frogger-disassembly/HEAD/… | MIT (tools/comments only; game is Konami's) | 153,408 (asm), 74,588 (notes) |
| `sources/arcade-js/games_frogger_mechanisms.md`, `gameplay.md`, `DONE.md`, `ca-lines.md`, `entrypoints.json`, `machine.js`, `manifest.js`, `routines.js` | https://raw.githubusercontent.com/qarl/arcade-js/HEAD/games/frogger/… | GPL-3.0 | 126,334 (mechanisms) |
| `sources/arcade-js/games_frogger_contrib_computerarcheology_{Code,RAMUse,Hardware,README}.md` | …/games/frogger/contrib/computerarcheology/ | GPL-3.0 (Markdown source of the CA pages) | 551,342 (Code.md) |
| `sources/arcade-js/boards_frogger_{hardware.json,memory.js,video.js,io.js}` | …/boards/frogger/ | GPL-3.0 | 6,725 / 8,315 / 13,969 / 9,348 |
| `sources/arcade-js/idiomatic/*.js` (61 files, the ROM routines re-expressed as JS) | …/games/frogger/idiomatic/<name>.js | GPL-3.0 | 594 KB total |

Not found anywhere: a 6502 disassembly or source of either Atari 8-bit Frogger (Sierra/John Harris 1982,
Parker Brothers 1983) — see §8.

## 2. How to read the three arcade sources together (important caveats)

- **tcdev42 `frogger.lst`** is the trustworthy human labelling (`curr_level`, `game_timer_lsb`,
  `turtle_duo_timer`, `bonus_frog_score`, …) but only ~65% commented; data tables are mostly `byte_xxxx`.
- **arcade-js / Computer Archeology** is AI-generated and *mechanically* verified (equivalence-tested against
  MAME traces), so the **arithmetic is reliable but many names are wrong**. Confirmed mislabels, with the
  tcdev name to use instead:
  - `LIVES_COUNT` (0x83B7) is really **`curr_level`** (it never decrements on death; `update_level` 0x0A5F bumps it).
  - `awardExtraLife` (0x0A5F) is really **`update_level`** (level++ and draw a level icon, tile 0x4C).
  - `TIME_REMAINING_P1/P2` (0x83E5/6) are really **`p1/p2_num_frogs_left`** (lives); `SHARED_TIME_BYTE`
    (0x83E4) is **`starting_lives`** from DIP table 0x2E00 = `3,5,7,255`. `renderTimeBar` draws the lives column.
  - `addScoreAndAwardExtraLife` "bumps the time byte": it really **adds one frog** (`add_bonus_frog`, 0x091D).
  - `advanceScrollLaneObjects` (0x2005) is **`handle_diving_turtles`**; its "scroll objects" are the turtle rows.
  - `driveDiveAnimByLevel` (0x27EA) is the **river alligator** (tile table `alligator_codes` 0x1413), not turtles.
  - `renderFrogAnimArm0..10` are the 11 **lane layout initialisers** (jump table 0x0FBE), not frog animation.
  - `advanceAnimationFrameBuffer` (0x1802) is the **lane-speed phase stepper** (§4.3).
- Where the two disagree I say which one I used. "**(unverified)**" = my inference, not stated by either source.

## 3. Hardware, memory map, video quirks (MAME `galaxian.cpp` / `galaxian_v.cpp`)

- Board: Konami Frogger (1981), Galaxian video family; Sega/Gremlin US licence sets are the same program.
  MAME machine `frogger` → `konami_base` + `konami_sound_1x_ay8910`, address map `frogger_map`.
- Clocks: main Z80 = 18.432 MHz/6 = **3.072 MHz**; sound Z80 and the **single AY-3-8910** = 14.31818 MHz/8 =
  **1.789772 MHz**. (The "second AY" belongs to Scramble/`konami_sound_2x`; Frogger has one.) Screen:
  256×224 native, `ROT90`, **60.606 Hz**, 50,688 CPU cycles per frame.
- `frogger_map`: 0000–3FFF ROM; 8000–87FF RAM; 8800 read = watchdog kick; A800–ABFF video RAM (32×32 tiles,
  mirror 0x400); B000–B0FF object RAM (00–3F per-column scroll/colour pairs, 40–5F eight 4-byte sprites,
  60–7F bullets, unused); B808 NMI enable; B80C/B810 flip Y/X; B818/B81C coin counters; C000–FFFF two
  i8255 PPIs (decoded by A12/A13: `offset & 0x1000` → PPI1 sound latch/control, `& 0x2000` → PPI0 inputs).
  Inputs (active low): IN0 bit4 Right, bit5 Left, bit6/7 coins, bit2 service; IN1 bits0-1 lives DIP
  (00=3, 01=5, 10=7, 11=256), bit6 2P start, bit7 1P start; IN2 bit4 Up, bit6 Down, bits1-2 coinage,
  bit3 cabinet. No fire button.
- Sound CPU map: 0000–1FFF ROM, 4000–43FF RAM, 6000–6FFF filter latch; AY via port I/O (A6 data, A7 address).
  Sound command = PPI1 port A byte; a falling edge of PPI1 port B bit 3 raises the sound IRQ; bit 4 mutes.
  `frogger_sound_timer_r` = Konami timer with **bits 3 and 5 swapped** (AY port B).
- Decryption/"bit-swap" notes (`decode_frogger_sound/gfx`): first 0x800 of the sound ROM and the **second
  gfx ROM (0x800–0xFFF) have data lines D0 and D1 swapped**. Video: in object RAM the scroll byte and sprite
  byte 0 have their **top and bottom nibbles swapped "entering the adder"** (`m_frogger_adjust`); colour bits
  are permuted `((c>>1)&3)|((c<<2)&4)` for tiles and sprites (`frogger_extend_*_info`).
- Background: `frogger_draw_background` = `background_draw_colorsplit(..., rgb(0,0,0x47), 128, 128)` — the
  river half is dark blue, the road half black, split at pixel 128 (schematics say 136; verified on hardware).
- Hardware sprites: 8 × 16×16, line buffer renders only the first 7½ per scanline; 16 px hard-clipped at the
  top; sprite X carries a +1 offset versus the tilemap. Per-column tilemap scroll (32 columns) is what
  moves the lanes: each lane is two tile columns (16 px on the rotated screen).

## 4. Extracted game constants (arcade)

### 4.1 Coordinates and rows
- Lanes run along the native vertical axis: a 256-px cycle (8-bit wrap), **224 px visible**. Object X values
  live in 0..255 and wrap. Frog vertical position (`FROG_Y` 0x8047, tcdev "frog X" = sprite byte 3): start
  row **0xE0**; each hop is **16 px**; rows: road 0xD0,0xC0,0xB0,0xA0,0x90 (lanes 10→6), median **0x80**,
  river 0x70,0x60,0x50,0x40,0x30 (lanes 4→0), home row when `FROG_Y < 0x2A` (bays at 0x18 .. .).
- Frog horizontal (`FROG_X` 0x8044): hop guards — no right hop at X ≥ 0xE0, no left hop at X < 0x20; while
  riding, X < 0x08 or ≥ 0xE7 = carried off-screen → dead. Home bays sit at X = **0x18, 0x48, 0x78, 0xA8,
  0xD8** (48 px apart).
- Frog hop (`animateFrogHop`, ROM 0x1C0D area): counter reload **9**, **2 px per frame**, 8 stepping frames =
  16 px; one hop per press (arrival latch, re-armed when the stick is released); scan order DOWN, UP, RIGHT,
  LEFT, one direction serviced per frame; hop sound command 0x04. Input is locked for **0x20 = 32 frames**
  after a respawn (`GATED_COUNTDOWN` 0x826A/0x826C).

### 4.2 Lane table (per-level layout, ROM 0x2260 → five 33-byte blocks at 0x226A/0x228B/0x22AC/0x22CD/0x22EE)
Selected by `(level−1) mod 5` (index 0x8293/0x8294, wraps 5→0 in `advanceBoardForeground` 0x05D3); copied to
RAM 0x8270 at every board/life start (`update_game_data_for_frogs_home` 0x223D). Each lane is a triple
**(gap, width, count)**: byte0/32 = gap in 8-px tiles (VRAM column stride), byte1 = object width in tiles,
byte2 = number of objects. Objects are laid out at period (gap+width) tiles starting at X=0, all inside the
256-px cycle. Direction and the turtle/log/vehicle identity come from the per-lane handler table 0x14C7.
(Decode of byte0 as gap: from the layout loop 0x0FD4–0x1047 and the dive-address arithmetic 0x2104–0x211C.)

| idx | lane (top→bottom), handler | dir | FROG_Y | L1 g/w/n | L2 | L3 | L4 | L5 |
|---|---|---|---|---|---|---|---|---|
| 0 | medium logs (`update_top_logs_scroll`) | → | 0x30 | 3/8/3 | 3/8/3 | 3/8/2 | 3/8/2 | 3/8/**1** |
| 1 | turtle duos (`update_top_turtles_scroll`) | ← | 0x40 | 3/4/4 | 2/4/5 | 4/4/4 | 5/4/3 | 7/4/3 |
| 2 | long logs (`update_middle_logs_scroll`) | → | 0x50 | 4/12/2 | 4/12/**1** | 4/12/1 | 4/12/1 | 4/12/1 |
| 3 | short logs (`update_bottom_logs_scroll`) | → | 0x60 | 4/6/3 | 3/6/3 | 6/6/3 | 7/6/2 | 5/6/2 |
| 4 | turtle trios (`update_bottom_turtles_scroll`) | ← | 0x70 | 2/6/4 | 6/6/3 | 3/6/3 | 4/6/3 | 7/6/2 |
| 5 | median (spacer, no mover) | – | 0x80 | 4/2/4 | 4/2/4 | 4/2/4 | 4/2/4 | 4/2/4 |
| 6 | trucks (`update_top_cars_scroll`) | ← | 0x90 | 7/4/2 | 7/4/3 | 5/4/3 | 4/4/4 | 3/4/3 |
| 7 | race car (`update_2nd_cars_scroll`) | → | 0xA0 | 3/2/1 | 3/2/2 | 7/2/2 | 6/2/3 | 5/2/4 |
| 8 | purple cars (`update_3rd_cars_scroll`) | ← | 0xB0 | 6/2/3 | 7/2/4 | 5/2/5 | 7/2/4 | 4/2/5 |
| 9 | bulldozers (`update_4th_cars_scroll`) | → | 0xC0 | 6/2/3 | 6/2/4 | 7/2/4 | 5/2/4 | 6/2/4 |
| 10 | yellow cars (`update_bottom_cars_scroll`) | ← | 0xD0 | 7/2/3 | 7/2/4 | 6/2/4 | 7/2/4 | 5/2/5 |

Widths: car 16 px, truck 32, turtle duo 32, turtle trio 48, short log 48, medium log 64, long log 96 — all
drawn as tile runs two tiles tall. Vehicle colour/type names for lanes 6–10 are the usual arcade identities
**(unverified against tile codes; tcdev only labels them top/2nd/3rd/4th/bottom cars)**.

### 4.3 Lane speeds (ROM 0x1841 pointer table → 11-byte blocks at 0x186B…; stepper `sub_1802`)
Each lane has a control byte in RAM 0x819B+i: **low nibble c; bit 4 clear → c px/frame; bit 4 set → 1 px
every c frames** (per-lane countdown in 0x81A6+i, `handle_scroll_right/left_row` 0x1598/0x163E). The 11-byte
block is **re-copied every 21 frames** from a cycle of ten ROM tables (index 0x81B3 0..9, hold timer 0x81B4 =
0x15; the index-9 step resets to 0 *without copying*, so table 8 stays 42 frames; stepping is suspended
while a river-alligator dive is busy, 0x814F/0x815B ≠ 0). The pointer table has 21 entries but only 0..8 are
ever copied by this routine **(tables 9–20 unused as far as I can see — unverified)**. So lane speed
"pulses" on a 210-frame cycle; this is the arcade's way of getting fractional speeds and the visible
race-car speed-ups.

| tbl | bytes for lanes 0..10 (hex) |
|---|---|
| 0 (0x186B) | 13 12 11 16 12 00 12 13 14 15 16 |
| 1 (0x1876) | 12 13 12 15 01 00 13 02 12 13 12 |
| 2 (0x1881) | 12 12 13 14 12 00 12 01 13 12 13 |
| 3 (0x188C) | 12 01 12 13 13 00 12 02 12 01 14 |
| 4 (0x1897) | 13 12 01 12 12 00 12 01 01 12 13 |
| 5 (0x18A2) | 13 01 12 13 13 00 01 02 12 13 12 |
| 6 (0x18AD) | 12 12 13 12 12 00 12 01 13 12 13 |
| 7 (0x18B8) | 13 13 12 13 01 00 13 02 12 01 12 |
| 8 (0x18C3) | 12 12 13 12 12 00 12 01 01 12 13 |
| 9 (0x18CE, never copied) | 13 01 12 01 13 00 01 02 12 13 13 |

Decoded: 0x11 = 1 px/f, 0x12 = ½, 0x13 = ⅓, 0x14 = ¼, 0x15 = ⅕, 0x16 = ⅙, 0x01 = 1, 0x02 = 2 px/f.
Mean over the ten tables (≈ at 60.6 f/s): lane0 medium logs **0.42 px/f (25 px/s)**; lane1 duos 0.62 (37);
lane2 long logs 0.55 (33); lane3 short logs 0.41 (25); lane4 trios 0.55 (33); lane6 trucks 0.57 (34);
lane7 race car **1.43 (87), peaks at 2 px/f** on tables 1/3/5/7/9; lane8 purple 0.54 (33); lane9 dozers
0.52 (32); lane10 yellow 0.36 (22). Speeds do **not** depend on level (only layout, creatures and counts do).
For a Power Fx port: use the mean speeds, or the 9-table cycle if you want the pulsing.

### 4.4 Riding and carry (`moveLaneObjectsAndCarryFrog` / `handle_scroll_*_row`)
Objects are processed 0..10 each frame (`row_to_scroll` 0x80FF). After shifting a lane's tile run and its
lead sprite, the mover drags the frog if `FROG_Y` is in the river band **0x30 ≤ Y < 0x73** (left movers omit
the 0x30 floor — real ROM asymmetry) and the frog's cell matches this lane: low nibble of Y < 3 → "low edge"
carry with off-screen test; ≥ 0xC → carry into the next row with no edge test; mid-hop (3..B) → no carry.
Being carried to X < 8 or X ≥ 0xE7 sets `HOLD_FLAG` 0x8004 = dead. Collision/drown is decided separately
(`dispatchFrogMoveAgainstLanes` 0x11BF) by scanning the lane's object list (count byte + object X list,
band widths 92/44/47/34/31/18 for the river lanes) against the frog.
Known ROM bug (arcade-museum thread, §7): object right edges are stored 2 px (turtles) / 4 px (logs) short,
and the frog is tested by its right edge — "edge riding" works.

### 4.5 Turtle rows: paddle animation and dive cycles (`handle_diving_turtles` 0x2005)
- Paddle animation: counter 0x826E +1/frame; at 0x10, 0x20, 0x30 the duo and trio rows are re-stamped with
  frame A/B/C (tiles 0x1423/0x142B/0x1433 duos, 0x145F/0x1473/0x1487 trios), counter resets at 0x30 →
  **3-frame cycle, 16 frames per frame, 48-frame period**.
- Only **one group per turtle row dives**: the group index in 0x811A (duos) / 0x8119 (trios), seeded to
  count−1 (the last group) at level start (0x17F2/0x17F5).
- Duo dive (lane 1): `turtle_duo_timer` 0x8110 **+1/frame, free-running 0..255 = 256-frame cycle (4.2 s)**.
  Handler runs while timer ≥ 0x50 and swaps tiles at exact values: 0x50 (80) half-down (tiles 94–97),
  0x80 (128) deep (98–9B), **0xA0 (160) submerged (blank 0x10)**, 0xB0 (176) deep, 0xD0 (208) half-down,
  wrap → normal turtles restored by the next paddle re-stamp (≤16 f). So: up ≈80–96 f, sinking 48 f,
  deep 32 f, gone 16 f, deep 32 f, rising 48 f.
- Trio dive (lane 4): `turtle_trio_timer` 0x8111 **+2/frame = 128-frame cycle (2.1 s)**; handler runs while
  timer < 0xA0: 0x00 half-down, 0x30 deep, **0x50 submerged**, 0x60 deep, 0x70 half-down, ≥0xA0 normal.
  In frames: half 0–24, deep 24–40, gone 40–48, deep 48–56, half 56–80, up 80–128.
- Whether the "deep" frame already kills is in the collision scan, not here **(unverified; the MAME test
  would be: stand on a diver and note the frame it dies)**.

### 4.6 Timer and time bonus (`init_time_bar` 0x0ABA, `time_tick_and_update_time_bar` 0x0887)
- Start: `game_timer_lsb` = **32**, `game_timer_msb` = **60**, BCD display 0x60. Every frame lsb−−; at 0 it
  reloads 32 and msb−− / BCD−−. **TIME OVER when msb reaches 0 → 60 units × 32 frames = 1920 frames ≈
  31.7 s.** The time bar is 15 tiles (VRAM 0xA8DF, 0x20 stride) × 4 steps each = 60 units, partial tile =
  0x10 − (msb & 3). Warning sound #5 and a colour change at BCD 0x10 (**16 units ≈ 8.4 s left**).
- Reaching home cashes the remaining units via the fall-through at 0x08E0: **10 points per remaining
  unit** ("10 PTS X REMAINING SECOND", 0x0C51). Lives DIP: 3/5/7 (Twin Galaxies uses 5).

### 4.7 Scoring (all deltas are packed BCD in tens, through 0x08E0)
| event | delta | pts | where |
|---|---|---|---|
| forward hop onto a row not yet reached this life | 0x0001 | 10 | `scoreFrogRowProgress` 0x1FD6 (band 0x30..0xD0; **row 0x80 (median) pays nothing** — code says so, unverified by play) |
| frog in home | 0x0005 | 50 | `stampHomeGoalAndResetFrog` |
| fly in that bay / lady frog escorted | 0x0020 | 200 | `awardBonusPoints` 0x2673, `display_200_for_lady_frog` 0x27CB |
| time left | 0x00tt | 10 × units | 0x08E0 fall-through |
| all five homes | 0x0100 | 1000 | 0x0623 / `advanceBoardForeground`, then level++ |
| extra frog | once, at `bonus_frog_score` 0x2E08 = **20,000** (flag 0x83E7/8) | | `add_bonus_frog` 0x091D |
Score is 4 BCD digits ×10 → wraps at 99,990 (Twin Galaxies rollover). High score 0x83EF never reset.
Popup "200" sprite (code 0x19) stays **0xA0 = 160 frames**. Home-bay fill animation on board complete sweeps
a countdown 255→16 stamping bays at 192/144/112/80/48.

### 4.8 Home bays, fly and alligator (0x1A74 area)
- Cursor 0x8123 steps 1..5 (mod 6), skipping filled bays (occupancy 0x825E–0x8262 P1 / 0x8263–0x8267 P2).
- **Odd levels: fly**; **even levels: alligator** (`bit 0, curr_level`). `creature_home_timer` 0x8122 +1/frame:
  fly appears when it wraps to 0 (every **256 frames**) and is cleared at **0x70 (112 frames shown)**;
  alligator snout at 0, full jaws at **0x50 (80 f)**, cleared at **0xB0 (176 f)**. Landing in an occupied bay or
  the jaws kills; landing between bays kills (`holdFrogMissedHomeBay`).

### 4.9 Level progression (every `curr_level` 0x83B7 compare in the ROM)
- Level starts at 1; `update_level` 0x0A5F increments after 5 homes, displays up to 15 icons (tile 0x4C).
- Layout cycles the five tables of §4.2 by `(level−1) mod 5` forever.
- **Level ≥ 2: river alligator** (0x27EA; tiles `alligator_codes` 0x1413 replace a log run — rides lane 0/top
  logs **(inferred)**; pacing seed = (lane-0 speed nibble) × 8 frames; different arm at level ≥ 5). Jaw
  collision 0x28BB only when level ≥ 2 and `f_alligator` bit 0.
- **Level ≥ 3: snakes** (0x2970 `add_snake` on the median; sprite-object engine 0x2A6A/0x2C13 also gated at
  ≥3) and the otter/second sprite object; a **second dispatcher-A object from level ≥ 6**. tcdev flags a
  ROM bug at 0x2993: the level ≥ 6 branch jumps into the middle of an instruction.
- Spawn density: a random byte must be ≤ `(8·level + 128) & 0xFF`; variant = `roll & 7`, only 0..4 spawn.
- Alligators in homes only on even levels (tcdev "fun fact"); fly on odd.

### 4.10 Random numbers (`sub_AEE` 0x0AEE)
32-byte ring at 0x8400 seeded from ROM 0x2EB1. Cell 0 is a cursor: cursor−− (wrap 0→31); partner =
cursor+13, minus 31 if ≥ 32; `ring[partner] ^= ring[cursor]`; return it. Used only for creature spawns —
**traffic, logs, turtles and dives are fully deterministic from level start**, which is why patterns work.

### 4.11 Death and respawn
Death animation advances a phase every **16 frames** (0x8247), 3 tile phases (0x22, 0x23, 0x3C at 0x17D3–
0x17E6) then the life restart; the frog object is reset and input locked 32 frames (§4.1). A "RESPAWN"
jingle, "GAME OVER" line and high-score entry follow (Computer Archeology sound index: Insert Coin, Die in
Water, Die in Road, Free Frog, Snake on Ground, Race Car, Pick up Friend, Landing Safe, Running Out of Time,
Hopping, plus Main/Game Over/Level Complete/Respawn songs and 20 "frog home" songs).

## 5. Konami MSX Frogger (1983, RC-704) — same designer lineage, useful cross-check
From `disassembly/msx_konami_1983/docs_FINDINGS.md` and `THE-GAME.md` (100 % traced, reassembles byte-exact):
4 layouts over a 5-slot cycle (`(stage−1) mod 5`, slots 2 and 3 identical); difficulty stops rising at stage
11; stage counter wraps 100→1; timer starts 0x96 (96 units, −1 every 20 frames ≈ 32 s); 10 pts/jump, time
cashed at 10/unit; extra life at 10,000 then every 50,000; up/down hop 16 px, left/right 8 px; two
hand-picked diving turtle groups (third from stage 6); landing in a filled home kills. Good evidence that
"one diving group per row, deterministic traffic" is the family design.

## 6. Atari 2600 Parker Brothers (1982) — raw DiStella
`disassembly/atari2600_frogger_parkerbros_distella.asm` is an uncommented DiStella dump (assembles with dasm).
Useful only for tables if someone wants to compare the PB console port's lane counts; no analysis exists.

## 7. Community, pattern and bug analysis
- **arcade-museum "Frogger – bugs, descriptions and fixes" (philmurr, Dec 2020)**:
  https://forums.arcade-museum.com/threads/frogger-bugs-descriptions-and-fixes.482765/ — six ROM bugs with
  fixes as a MAME cheat file (https://gist.github.com/fedekrum/a7790d422cca3050f8d6bd3c5b9dfe15): short
  object right-edges (2 px turtles / 4 px logs) + frog tested by right edge; a wrong-row collision routine
  during vertical jumps (dying on a valid top-turtle→log jump); frog controllable in attract; off-screen
  jump from X=0xDE (positions 0x10..0xE0, water landings move 2 px at a time); stuttered movement under an
  occupied home; invisible lady frog (colour 0).
- **"Any game play strategies?"** https://forums.arcade-museum.com/threads/frogger-any-game-play-strategies-high-scores.357404/
  — players confirm each board is a fixed pattern ("logs timed so the next group enters as one leaves",
  "left ends of logs more forgiving" = the right-edge bug above).
- **StrategyWiki** https://strategywiki.org/wiki/Frogger/Gameplay — "white cars in the fourth lane speed up"
  = the 2 px/f entries in speed tables 1/3/5/7 for lane 7.
- **Twin Galaxies / records**: 5-lives DIP; score wraps at 99,990; Michael Smith 1,356,520 (2022), Pat Laffaye
  1,029,990 (2017, unsubmitted). No published frame-level "golden path" analysis found; the determinism in
  §4.10 means one can be derived from the tables here.
- **Frogger500 (tcdev, 2025)** https://retroports.blogspot.com/2025/07 — Z80→68000 transcode of this ROM,
  39 % done in July 2025; confirms "5 layouts" and the 11-entry scrolling-object jump table.
- Konami arcade test ROM source: https://www.arcade-cabinets.com/rom_hacks/frogger-testrom.asm (diagnostics
  only, not downloaded).

## 8. Could not find
- Any 6502 disassembly, source listing, or technical write-up of the **Atari 8-bit** Frogger (Sierra/John
  Harris 1982 disk, Chuck Benton 2-player disk, Parker Brothers 1983 cart). Only interviews
  (ANTIC podcast 454 Steve Kranish; Harris in "Hackers"/MobyGames). The 8-bit lane tables must come from
  playing the ROM in Altirra or from the arcade tables above.
- A fully licensed, human-commented arcade disassembly (tcdev's has no licence file; CA/arcade-js is AI
  work under GPL-3). Treat both as reference only; do not copy code.
- The exact lethality boundary of the turtle "deep" frame and of the alligator jaws (§4.5, §4.9).
- The lane the river alligator and the lady frog ride on, and the lady-frog spawn timer.
