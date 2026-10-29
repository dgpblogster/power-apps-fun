# Frogger research index

Research completed 2026-10-28 by five parallel tracks. Read this file first; it says what each document
holds, which cross-document disagreements were resolved and how, and what remains open before the game
spec (`docs/01-game-spec.md`) can be written.

## Documents

| File | Covers | Strongest content |
|---|---|---|
| [01-gameplay-mechanics.md](01-gameplay-mechanics.md) | Arcade rules and numbers | 13-row grid, hop timing, input latch, five lane-layout tiers from ROM, scoring, hazards by level, DIPs, open questions |
| [02-visual-audio.md](02-visual-audio.md) | Arcade look and sound | Band-by-band pixel measurements of the 224x256 frame, palette, every sprite described for an original redraw, sound command table, music identification and rights notes |
| [03-history-legacy.md](03-history-legacy.md) | Origin, intent, hardware, commerce, rights | Konami staff, Sega/Gremlin licence story, the Parker Brothers vs Sierra split, the John Harris story, records, trademark status, homage rules |
| [04-atari-8bit-port.md](04-atari-8bit-port.md) | Both Atari 8-bit versions side by side | Shared 40x28 character picture, scanline bands, colours, manuals transcribed, "tell them apart in 10 seconds", gaps to fill from the arcade |
| [05-source-code.md](05-source-code.md) | Catalogue of disassemblies, MAME driver, clones | ROM lane tables for all five tiers, lane speed ring with raw bytes, turtle dive cycles, timer, scoring gates, RNG, bay positions, naming caveats |

Raw third-party files (MAME driver, the tcdev and Computer Archeology listings, the MSX disassembly, the
2600 DiStella dump, the arcade-js translation) live in `mame/`, `disassembly/`, and `sources/`. Those three
folders are listed in `.gitignore` and never go to the public repo, the same rule Galaxian used.

## Headline facts the spec will build on

- **Grid.** 224 wide by 256 tall logical pixels, 16 px rows, 13 rows: home bank, 5 river lanes, median,
  5 road lanes, start row. Frog hop = 16 px in 9 frames (2 px per frame for 8 frames plus a landing frame).
  One press, one hop, with an arrival latch; no diagonals.
- **Lanes.** Five layout tiers in ROM, selected by (level - 1) mod 5. Level 1 from the top: medium logs,
  turtle pairs, long logs, short logs, turtle triples, median, trucks, racing car, purple cars,
  bulldozers, yellow cars. Directions top-down R L R R L, then L R L R L. Objects live on a 256 px wrap.
- **Speeds.** A ring of nine 11-byte tables re-copied every 21 frames. Weighted averages in px per frame:
  medium logs 0.43, turtle pairs 0.57, long logs 0.53, short logs 0.36, turtle triples 0.57, trucks 0.52,
  racing car 1.33 (pulsing 1 to 2), purple cars 0.59, bulldozers 0.54, yellow cars 0.36. Speed does not
  depend on level in the ROM; difficulty comes from sparser platforms, denser traffic, and creature spawn rate.
- **Turtle dives.** Last group in each turtle row dives. Pairs: 256-frame cycle, submerged frames 160 to 176.
  Triples: 128-frame cycle, submerged frames 40 to 48.
- **Timer.** 60 units of 32 frames, 31.7 s per frog. Warning at 10 units. Bonus 10 points per remaining unit.
- **Scoring.** 10 per new forward row (median pays 0), 50 per home, 200 fly or lady frog, 1000 for all five,
  one extra life at 20,000. Score display wraps at 99,990.
- **Hazards.** River crocodile from level 2, roaming snake or otter from level 3, a second roamer from level 6.
  Home bay: fly on odd levels, crocodile on even levels. Bay window 8 px at 48 px pitch.
- **Determinism.** Traffic, logs, and dives are deterministic; only creature spawns use the RNG. Patterns work.
- **Hardware.** Konami Galaxian-family Z80 board, one AY-3-8910 plus a sound Z80, 60.606 Hz.
- **Atari 8-bit.** Parker Brothers 1983 is Steve Kranish's 8K rebuild of John Harris's Sierra 1982 code.
  Both share a 40x28 character picture, 16-scanline lanes, 5 river lanes, 4 road lanes (one fewer than the
  arcade). They differ in border colour, HUD placement, median style, turtle colour, music, and player count.

## Disagreements between documents, and how they were settled

| Topic | Said | Resolution |
|---|---|---|
| Lane speed averages | 01 originally had purple cars at 1.16 px/f, faster than the racing car at 0.97; 05 had racing car 1.43 and purple 0.54 | Recomputed from the raw bytes in 05 section 4.3 with table 8 weighted twice. Racing car 1.33, purple 0.59. The table in 01 was replaced on 2026-10-28; 05 differs by rounding only |
| Timer warning point | 01 and 02 say 10 units; 05 says 16 units | The counter is BCD, so the compare value 0x10 is 10 units. Use 10 |
| Log lengths | 01 and 05 give tile widths 48, 64, 96 px; 02 measured about 42, 58, 90 px on screen | Both right: the tile strip is 6, 8, 12 tiles, and the rounded end tiles leave transparent pixels. Use tile widths for collision, measured widths for art |
| Trucks are slow | Community says trucks are slow; ROM says 0.52 px/f, mid pack | ROM wins; trucks feel slow because they are 32 px long |
| Per-level speed-up | Community says vehicles get faster each round; ROM ring never reads the tier | Treated as unverified in 01. The spec will take the ROM reading and leave a named-formula multiplier so a per-level speed-up can be added if playtesting wants it |
| Sound chips | Brief said two AY-3-8910; 02, 03, 05 all found one | One AY plus a sound Z80. Two is the Scramble sibling board |

## Open items (version decided; the rest are tracked in the spec's gap-fill table)

1. **Which version.** Decided 2026-10-28: **Parker Brothers 1983** (the user confirmed via the music
   tell). Four road lanes, five river lanes. The spec is `docs/01-game-spec.md`.
2. **Port timings.** No disassembly of either Atari 8-bit build exists. Lane speeds, dive cycles, and spawn
   rules for the port must be measured in Altirra or taken from the arcade tables and labelled as arcade fills.
3. **Collision band width** for cars and logs (centre point versus overlap threshold). The home window and
   crocodile zones are known; the lane bands are not.
4. **Roaming creature identities** (which ROM variant is snake, otter, lady frog) and the lady frog's rule.
5. **Occupied bay kills** is community-reported only.
6. **Tick mapping.** At 20 ticks per second a hop is 3 ticks, a timer unit is about 10.6 ticks, and the
   racing car moves up to 6 px per tick, under the 16 px frog, so a swept test is a precaution not a necessity.

## Suggested next steps

1. Done: version chosen, `docs/01-game-spec.md` and `docs/02-platform-decision.md` written 2026-10-28.
2. (Superseded) Write `docs/01-game-spec.md` from these documents in the Galaxian spec's shape (design goals, playfield
   and coordinates, tick model, speed table, tick order, rules, HUD, sprites, sound, states), marking every
   arcade fill. Write `docs/02-platform-decision.md` by adapting the Galaxian one.
3. Only then start the build: Studio app, generator, first compile with the tps label on screen.
