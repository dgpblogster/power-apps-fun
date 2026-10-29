# Frogger (arcade, Konami 1981 / Sega-Gremlin NA) — visual and audio presentation

Date: 2026-10-28. Purpose: describe the arcade original precisely enough to design ORIGINAL homage art and
sound for a canvas Power App. Nothing here is a licence to copy the tile ROM; the pixel-level descriptions are
for drawing lookalikes. Items marked **(unverified)** could not be confirmed against a primary source.

Primary sources: MAME `galaxian.cpp` / `galaxian_v.cpp` / `galaxian.h` (hardware, timing, palette maths),
Computer Archeology's Frogger disassembly (main board `Code`, `RAMUse`, `GFX`, sound board `SoundCode`,
`SoundHardware`), and a pixel analysis of the native 224x256 MAME screenshot on Wikipedia
(`Frogger_game_arcade.png`, colours sampled per scanline and per object). Secondary: Wikipedia, arcade-museum,
classicgaming.cc, classicarcadegaming.com forum (version differences), tenshi-a blog and arcade-museum forum
(music identification), search snippets of TCRF (page itself is bot-walled) and StrategyWiki (bot-walled).

## 1. Hardware and screen

| Item | Value | Source |
|---|---|---|
| Board | Konami "Galaxian-family" video hardware, Frogger-specific memory map (schematics known) | MAME |
| Main CPU | Z80 at 18.432 MHz / 6 = 3.072 MHz | MAME `galaxian_base` |
| Sound CPU | Z80 at 14.318181 MHz / 8 = 1.78977 MHz | MAME `konami_sound_1x_ay8910` |
| Sound chip | ONE AY-3-8910A at 1.78977 MHz (3 square-wave voices + 1 noise generator shared), through a switched-capacitor low-pass network; mono, one speaker | MAME, Computer Archeology SoundHardware |
| Raster | 384 x 264 total, 256 x 224 visible (H x V) in hardware; cabinet monitor rotated 90 degrees (`ROT90`) so the player sees **224 wide x 256 tall** | MAME `galaxian.h`: HBSTART 256, VBEND 16, VBSTART 240 |
| Refresh | 6.144 MHz pixel clock / (384 x 264) = **60.606 Hz** | MAME |
| Tiles | 8x8, 2 bits per pixel (3 colours + transparent per tile), tile map 32 columns x 32 rows (in rotated terms: 28 visible columns of the 32-row direction... see layout) | MAME `galaxian_charlayout`, CA GFX |
| Sprites | 16x16, 2 bpp, **8 hardware sprites** (4 bytes each: pos, code/flip, colour, pos), sprite code N = tiles 4N..4N+3 | CA Hardware, MAME `galaxian_spritelayout` |
| Scrolling | Per-column scroll register for each of the 32 tile columns (0xB000..0xB03F): every road/river lane is a 2-column tile strip scrolled by hardware. Vehicles, logs and turtles are **tiles**, not sprites | CA Hardware ("The river and road lanes scroll this way") |
| Colour PROM | 32 x 8 bits (`pr-91.6l`): 8 palettes x 4 entries, bits RRRGGGBB; colour 0 = transparent | MAME ROM list, `galaxian_palette` |
| Background | Hard-wired: dark blue `rgb(0,0,0x47)` on the top half (scanlines 0..127 as seen by the player), black below. "according to schematics it is at 128+8; but it has been verified different on real machine" | MAME `frogger_draw_background` |
| Lives DIP | 3 / 5 / 7 frogs; coinage DIP; upright/cocktail (screen flip) | MAME input ports |

Palette maths (MAME): R and G from 3 bits through 1000/470/220 ohm resistors, B from 2 bits through 470/220
ohm. MAME scales the whole palette to a maximum of 224 (headroom for Galaxian stars), so a "full" channel
reads 0xE0 in screenshots; multiply by 255/224 for a saturated version. Full 32-entry PROM values were not
published in text form **(unverified)**; the per-object colours below are measured from the MAME frame.

### Measured colour set (MAME frame, hex RGB; "x255/224" = saturated equivalent)

| Role | Measured | Saturated | Notes |
|---|---|---|---|
| Top-half background (river/home/HUD) | `#000047` | `#000051` | hard-wired, not PROM |
| Bottom-half background (road, sidewalk gaps, time row) | `#000000` | | |
| Bright green (frog, home bank, time bar, turtle legs) | `#1DC300` | `#21DE00` | |
| Red (scores, turtle shells, car wheels, truck cab) | `#E00000` | `#FF0000` | |
| Yellow (lane-1 car body, lives icons, TIME label) | `#E0E000` | `#FFFF00` | |
| White-grey (HUD labels, trucks, dozer, race car body, log ends) | `#C3C3D9` | `#DEDEF7` | slightly lavender white |
| Purple (median, sidewalk, lane-1 car windows) | `#8500D9` | `#9700F7` | |
| Blue dots in median/sidewalk | `#0400D9` | `#0500F7` | |
| Magenta-pink (lane-3 car body, level icon, lady frog) | `#E03ED9` / `#DF00D8` | `#FF47F7` / `#FE00F6` | |
| Cyan (lane-3 car windows, frog-at-home belly, fly wings) | `#00C3D9` | `#00DEF7` | |
| Log top (brown-orange) | `#C35B45` | `#DE684F` | |
| Log underside (dark brown) | `#855B45` | `#97684F` | |
| Orange-red (bank speckles, fly body, frog-at-home mouth) | `#D54500` / `#E03E00` | `#F24F00` / `#FF4700` | |
| Yellow-green (lane-3 car wheels, snake) | `#82DC00` | `#94FA00` | |

## 2. Screen layout (player view, 224 wide x 256 tall, y down)

Every lane is 16 px (2 tile rows). Measured from the frame; x positions are pixels from the left.

| y range | Band | Content and colours |
|---|---|---|
| 0-7 | HUD row 1 | `1-UP` at x 34-63 (tiles 4-7), `HI-SCORE` at x 81-143 (tiles 10-17); white-grey text on dark blue. `2-UP` on the right when 2 players **(position unverified)** |
| 8-15 | HUD row 2 | scores in red: P1 `03040` at x 25-63 (5 digits, tiles 3-7), hi-score `04630` at x 89-127 (tiles 11-15). Scores are 5 digits, leading zeros shown |
| 16-23 | blank | dark blue |
| 24-47 | home bank | bright green bank 24 px tall, speckled with orange-red and dark-blue pixels (texture, "Base at top" tiles 0x40-0x47). Five bays cut into it from y 31 to 47 (16 px tall): openings about 16-18 px wide centred at x ~36, ~84, ~132, ~180 (and one at the right edge; bays are 48 px apart = 6 tiles). Bay walls have a 1-px orange-red outline. Frog-X capture bands in the code: 0x15-0x1C, 0x45-0x4C, 0x75-0x7C, 0xA5-0xAC, 0xD5-0xDC (8-px windows, 48 px apart); home row frog Y = 0x2A |
| 48-63 | river lane 5 (top) | medium logs, ~58 px long, moving **right** |
| 64-79 | river lane 4 | turtle pairs (2 x 15 px, 1-px gap), moving **left** |
| 80-95 | river lane 3 | long logs, ~90 px, moving **right** |
| 96-111 | river lane 2 | short logs, ~42 px, moving **right** |
| 112-127 | river lane 1 | turtle triples (3 x 15 px), moving **left**; some groups dive |
| 128-143 | median | purple with a repeating 16-px pattern of blue 2x2 dots and red/blue dashes (grass tiles 0x48-0x4B). `TIME nn` time-bonus text appears here in red after a frog gets home (measured: `TIME 60` at x ~88-143) |
| 144-159 | road lane 5 (top) | trucks (2 sprites-worth, ~27 px drawn, 32 px nominal), moving **left** |
| 160-175 | road lane 4 | race cars (white, 16 px), moving **right**; fastest lane |
| 176-191 | road lane 3 | pink cars (15 px), moving **left** |
| 192-207 | road lane 2 | bulldozers (14 px), moving **right** |
| 208-223 | road lane 1 (bottom) | yellow cars (16 px), moving **left** |
| 224-239 | sidewalk / start | same purple pattern as the median. Frog spawns here, centred (x ~104) |
| 240-247 | status row | lives: green/yellow 8x8 frog icons at x 1,9,17,... (8-px pitch, up to 15 drawn) bottom-left; level: small magenta/green icon(s) at bottom-right (measured x 210-214) |
| 248-255 | time row | green time bar, full length 118-120 px ending at x 191, with yellow `TIME` at x 194-223 (tiles 24-27). The bar depletes from its left end toward the label (bar stays attached to `TIME`) |

Lane direction evidence: the disassembly's lane mover labels objects 0/2/3/7/9 "rightward" and 1/4/6/8/10
"leftward" with object 5 a "spacer" (the median). Read top-down (object 0 = top river lane) this gives the
directions above; they also match every published description. Object order orientation **(unverified)**.

Lane group widths used by the collision code (px): river 60, 31, 92, 44, 47 (lanes 5..1 = medium log, turtle
pair, long log, short log, turtle triple) and road 34 (truck) and 18 (cars) — a good source for hit boxes.

## 3. Sprite and tile catalogue

All objects are drawn from 8x8 tiles; a "16x16 sprite" is four tiles. Tile codes come from the Computer
Archeology GFX page (its colour swatches are PROM-derived and agree with the frame measurements). Shapes are
described from the upscaled frame plus the tile groups. Draw 16x16 originals that read the same at a glance.

### Player frog and its states

| Name | Size | Tiles / sprite | Colours | Description |
|---|---|---|---|---|
| Frog, rest (up) | 16x16 (drawn ~12x10) | tiles 0x78-0x7B, sprite 0x1E | green body, yellow belly/eyes, magenta mouth (palette green/magenta/yellow) | Top-down frog: round green body, two big round eyes at the top with yellow highlights, four bent legs splayed out at 45 degrees (two "elbows" up, two "knees" down), yellow belly patch |
| Frog, mid-hop (up) | 16x16 | tiles 0x70-0x73, sprite 0x1C | same | Body stretched: front legs reaching forward, rear legs fully extended behind, narrower silhouette |
| Frog left rest / left hop | 16x16 | sprites 0x21 / 0x1F | same | Side-facing versions of the two frames. Right = hardware flip of left; down = double flip of up. So the ROM stores only 2 frames x 2 orientations (+2 spare frog blocks, 0x74 and 0x80: likely frog-with-lady frames **(unverified)**) |
| Frog at home | 16x16 | tiles 0x6C-0x6F (sprite 0x1B); second version 0xFC-0xFF | green body, cyan belly, orange mouth, dark blue eyes | Front-facing frog sitting in the bay, arms up on the bay walls, cyan chest. Second block = celebration version: "the noses of all the frogs ... turn into hearts and their eyes will light up" when the level is cleared (arcade-museum) |
| Road death (squash) | 16x16 x 3 frames | tiles 0xE4-0xEF (sprites 0x39, 0x3A, 0x3B) | yellow, red, purple | Frog flattened progressively: frame 1 wide splat with legs out, frame 2 flatter with red smear, frame 3 a thin yellow/red streak |
| Water death (drown) | 16x16 x 3 frames | tiles 0x88-0x93 (sprites 0x22, 0x23, 0x24) | white, dark, green | Shared with the turtle sinking frames: frog sinks into concentric white ripple rings, then only ripples remain |
| Skull | 16x16 | tiles 0xF0-0xF3 (sprite 0x3C) | yellow skull, red/purple | Skull and crossbones shown at the death spot as the final phase of both deaths and of time-out. Rounded skull with two dark eye sockets, crossed bones below |
| Lives icon | 8x8 | tiles 0x4C/0x4D | green, yellow, magenta | Tiny front-facing frog, 7 px wide: green outline, yellow face/belly; drawn at the bottom-left at 8-px pitch |
| Level icon | 8x8 | tiles 0x4C/0x4D (other palette) | magenta, green | Same tiny frog in magenta/green at the bottom-right, one per level **(count/placement beyond level 1 unverified)** |

### Road vehicles (tiles in scrolled lane strips)

| Name | Size | Tiles | Colours | Description |
|---|---|---|---|---|
| Car 1 (lane 1, bottom) | 16x16 (drawn ~16x14) | 0x50-0x53 | yellow body, red wheels, purple windows | Top-down sedan: yellow rounded body, four red wheels sticking out at the corners (2 px past the body), purple windscreen/rear-window bars, red detail at the front; moves left |
| Dozer (lane 2) | 16x16 (drawn ~14x14) | 0xA4-0xA7 | white-grey, red, green | Bulldozer seen from above: white-grey tracked body with a green cab block, red-striped blade on the leading (right) side drawn as a vertical comb of red/white stripes; moves right |
| Car 2 (lane 3) | 16x16 (drawn ~15x12) | 0x30-0x33 | magenta-pink body, cyan windows, yellow-green wheels | Small pink car with cyan window strip and light-green wheels; moves left |
| Car 3, race car (lane 4) | 16x16 (drawn ~16x12) | 0xA0-0xA3 | white-grey body, red wheels/nose, green stripe | Formula-style racer: pointed white body with red wheels spaced front/rear and a green stripe or driver; fastest lane; moves right |
| Truck (lane 5) | 32x16 (drawn ~27x12) | 0xA8-0xAF (two 16x16 blocks) | white-grey trailer, red cab, green corner lights | Long box trailer in white-grey with a short red cab at the leading (left) end and small green marker pixels at the corners; moves left |

### River objects

| Name | Size | Tiles | Colours | Description |
|---|---|---|---|---|
| Log, 3 pieces | 16x16 each: left cap, middle, right cap | 0x54-0x5F | brown-orange top, dark-brown underside, white-grey highlights | Horizontal cylinder: rounded ends drawn as white-grey arcs, light brown top two-thirds flecked with short white dashes (bark), dark brown bottom third. Assembled into three lengths: short ~42 px, medium ~58 px, long ~90 px (measured) |
| Turtle (3 paddle frames) | 16x16 (drawn 15x12) | 0x34-0x3F (sprites 0x0D, 0x0E, 0x0F) | red shell, green head/legs, white highlights | Top-down turtle: red oval shell with white rim highlights, green head poking out one end, four green flippers that alternate position across the 3 frames (paddle animation). Groups of 2 (lane 4) or 3 (lane 1) with 1-px gaps |
| Turtle sinking | 16x16 x up to 5 | 0x88-0x9B (sprites 0x22-0x26) | white, dark, green | Shell lowers under the surface: green-only silhouette, then a white ripple ring, then smaller ripples, then nothing (same frames as the frog drowning) |
| Alligator / crocodile (river) | 32x16, two poses | 0x68-0x6B (sprite 0x1A) + 0xC8-0xD3 (sprites 0x32-0x34) | brown-orange like the logs (CA palette), with white teeth **(colours of jaws unverified)** | Log-coloured body with a head at the leading end that alternates between closed and open jaws (pose A at animation phase 64, pose B at phase 112). Landing on the body carries the frog; landing in the open jaws kills. Appears from level 2 |
| Crocodile head in bay | 16x16 as tiles stamped in the bay | 0xD0-0xD3 (emerging uses blank tile 0x10 over 0xD0/0xD1) | same | Snout rises out of a bay: first only the lower half, then the full open-jawed head; jumping in while it shows kills |
| Snake | 16x16 x 6 blocks (3 slither frames x 2 halves, 32 px long) | 0xB0-0xC7 (sprites 0x2C-0x31) | yellow-green body, teal, magenta (CA palette: `#97FF00`, `#28E6B3`, `#F346F0`) | Long thin S-curved serpent with a wedge head and forked magenta tongue; slithers along the median (from level 3) and later on logs. Deadly on contact |
| Otter | 16x16 x 2 frames | 0x9C-0x9F, 0xE0-0xE3 (sprites 0x27, 0x38) | log palette (brown, dark brown, white-grey) | Brown swimming mammal with a white face/belly, two frames (swimming); surfaces beside a log and knocks the frog off (appears on later levels, "second drifting creature appears at level 6" per the dispatcher comment) |
| Lady frog | 16x16 | frog tiles with a different palette | magenta/pink body ("normally purple", arcade-museum) | Same silhouette as the player frog in pink/purple; sits on a log; when carried she rides on the frog's back (bug: can be invisible until touched, then "white with red legs") |
| Fly (bonus insect) | 16x16 (drawn ~10x10) | 0x2C-0x2F (sprite 0x0B) | orange-red body, cyan wings, green | Small bug seen from above: orange body, two cyan wing blobs either side, green legs; appears inside an empty bay and blinks out |
| Bonus score popup | 8x8 digits, drawn as a 16x16 sprite (code 0x19, palette 3) | 0x60-0x67 | green/magenta/yellow palette | `200` shown in the bay for 160 frames after a fly catch or lady-frog delivery; an unused `100` graphic exists (TCRF via search snippet) |
| Frog in bay (goal stamp) | 16x16 | see Frog at home | | |

### Scenery tiles

| Name | Tiles | Colours | Description |
|---|---|---|---|
| Home bank | 0x40-0x47 (5x3 tile motif) | green, orange-red, dark | Solid green bank speckled with 1-px orange-red and dark-blue dots; bay openings have an orange-red 1-px rim and a short "shoulder" at the top corners |
| Median / sidewalk | 0x48-0x4B | purple, blue, red | Purple field with a 16-px repeating motif: a 2x2 blue dot, a 2x2 red dot, 1-px blue dashes — reads as gravel/grass |
| Time bar | 0x0C-0x0F (partial bar tiles) + 0x4D + cap 0x10 | green | Solid green bar 8 px tall; the four `Time` tiles give sub-tile (2-px) granularity **(2 px/unit inferred from 118 px at 60 units)** |
| Text font | 0x00-0x2B, 0x4E, 0x4F (44 glyphs) | per palette: white-grey labels, red scores, yellow TIME, blue credit line | Bold 8x8 arcade font with 7-px-wide glyphs and 1-px gap: digits 0-9, A-Z, `-`, `.`, `©`, and a few symbols. Strokes 2 px thick, square corners, `0` with no slash |
| Title letters | 0xD4-0xDF, 0xF4-0xFB (5 x 16x16 blocks) | green, magenta, yellow | Big chunky "FROGGER" letters built 16x16 **(unverified whether all 7 letters are from these 5 blocks plus repeats)** |

## 4. Animation and timing (frames at 60.606 Hz)

| Thing | Value | Source |
|---|---|---|
| Hop | 9-frame hop animation, 2 px per frame step; one hop = 16 px (one lane) in about 0.15 s; the mid-hop frame shows for the moving frames, the rest frame at the end. Input ignored while a hop plays | CA Code (0x8254/0x8255 step, "nine-frame hop-animation length") |
| Lane/turtle animation clock | `ANIM_FRAME_TIMER` reloads to 21 frames; frame index wraps at 10. Turtle paddle frames therefore change every ~0.35 s (3-frame cycle) | CA RAMUse |
| Turtle dive | `copyDiveAnimFrame` steps 8 frames (index +2 to 0x10); diving groups cycle submerged -> up on their own timer. Dive cadence per level **(unverified)** | CA Code |
| Gator jaw cycle | pose A at phase 64, pose B at phase 112, cycle restarts (so ~1.9 s per open/close cycle if the phase ticks per frame **(unverified)**) | CA Code |
| Death | 16 frames per phase. Road: squash 1, squash 1 (held), squash 2, squash 3, skull -> ~96 frames (1.6 s). Water: drown 1, 2, 3, skull -> ~80 frames (1.3 s). Then a 216-frame (3.6 s) pause with the next-life jingle before respawn | CA Code `driveFrogDeathAnimation` |
| Time | starts at 60 units (BCD 0x60); one unit = 32 frames (0x3C20 seed = 60 steps x 0x20) -> **31.7 s** per frog. Low-time warning sound (cmd 5) when 10 units remain; bar turns red at the same point **(colour change unverified)**. Time-out kills the frog with the skull; no separate text in the ROM comment list ("TIME OUT" is a home-port string) **(unverified)** | CA Code `initDisplayFieldOnce` |
| Time bonus display | `TIME nn` in red in the median after a frog gets home; worth 10 pts per remaining unit (listed as "10 per unused half-second") | frame measurement; classicgaming.cc |
| Bay fly / croc | bay counter: fly stamped at wrap-to-0, erased at 0x70; croc emerging at 0, fully surfaced at 0x50, erased at 0xB0; which of the two is chosen by lives-count bit 0. Fly on-screen patrol: 60 frames with a flip at 30 | CA Code |
| Home arrival | bonus sprite shown 160 frames; 16-frame input lock; frog-home jingle index cycles through 20 entries | CA Code |
| Attract demo | each title "cell" dwells 32 frames, title animation 8 ticks per frame over 4 frames, demo scroll 4 px/step, 48 frames between scripted hops | CA Code |
| Game start | start jingle sequence 416 frames (~6.9 s) before play; board reveal sweeps in with a 64-frame lead-in | CA Code |
| Extra life | one per player per game at 20,000 (DIP: 10,000 or 20,000) | CA Code, Wikipedia |
| Difficulty | lane parameter block (33 bytes = 11 objects x speed/spacing/phase triple) selected by a 0..4 tier that wraps after 5 boards ("after five levels, the game gets briefly easier") | CA Code, classicgaming.cc |

## 5. Text screens and attract loop

- **Power-on "rug" test**: the whole screen fills with one repeated character; Konami original and Sega set 1
  show a white `0`, Sega set 2 an `X`, set 3 an `I`, Moon Cresta hardware a `K` (classicarcadegaming forum).
- **Title**: frogs hop in and spell `FROGGER` in big 16x16 letters (bootlegs spell `FROG`); frogs also appear
  along the bottom. Copyright line at the bottom: `KONAMI © 1981` (Konami) or `SEGA © 1981` (Sega sets).
  Labels white, scores red, `CREDIT nn` blue (forum table: "Label White, Score Red, Credit Blue").
- **`-POINT TABLE-`** screen: 10 PTS per step forward, 50 PTS per frog home, 200 PTS fly or lady frog, 1000 PTS
  five homes, 10 PTS per remaining time unit (exact on-screen wording **(unverified)**; the Konami ROM has the
  typo `FIYE HOMES`, fixed to `FIVE HOMES` in Sega set 1 per TCRF search snippets).
- **`SCORE RANKING`** screen: high-score table (mode 3 in the code).
- Sega set 2 (and Moon Cresta / Turtles hardware sets) replace the point table with a **game instructions
  and scoring page** (two screens of text).
- After a credit: `ONE PLAYER ONLY` / `ONE OR TWO PLAYERS` prompt (strings referenced by the code). A literal
  `PUSH START` string was not found **(unverified)**.
- In play: `1-UP`, `2-UP`, `HI-SCORE`, `TIME`, `TIME nn` bonus, `GAME OVER` banner (blitted from ROM 0x2F0E).
- Attract trick: the demo frog can be taken over by the player when it reaches the top log (arcade-museum).

## 6. Audio

Hardware: one AY-3-8910 (3 tone voices + noise), driven by the sound Z80 through a 700 Hz tick scheduler.
"Frogger is mostly two-voice music with a third voice for sound effects"; voices are allocated dynamically
per request, with a priority table (nothing preempts the hop chirp). Each voice can switch 0.047 uF and/or
0.220 uF capacitors into its output (4 filter states) for a softer timbre. Note table: 5-bit note numbers,
frequency = 1,789,750 / (16 x period), range G#1 (51.9 Hz) to G6 (1575 Hz). Known bugs: a pitch off-by-one
("notes land on white keys" if fixed), a missing eighth note, and a garbage note that stops voice B so "part
of the background music will cut out from time to time".

### Sound command table (main board -> sound board, 0x00-0x18)

| Cmd | Name (disassembly label) | Trigger | Character |
|---|---|---|---|
| 01 | Coin inserted | credit | short rising two-note "ding" (the Sugababes-sampled coin tone); ~0.3 s |
| 02 | Die in water | drown | descending gurgle: tone steps 0x70 -> 0x3C -> 0xFC with filter, ~1 s |
| 03 | Die in road | squash | low buzzy "splat": tone 0x100 with a decaying counter, ~0.5 s |
| 04 | Frog hopping | each hop | highest priority; a quick pitch sweep (direction set by a bit, sweep amount from the low nibble, length a power-of-two frame count): a short "boing/chirp" per hop |
| 05 | Time running out | 10 units left | repeating fast two-pitch tick/alarm until home or death |
| 06 | Next life begins | respawn | short jingle (song 3 "Respawn") |
| 07 | Extra frog | 20,000 pts | ascending arpeggio fanfare, tone 0x50 base |
| 08 | Music interlude after frog home | frog home | one of 20 short tunes (songs 5-24), chosen in sequence |
| 09 / 0A / 0B | Main song intro, voices A/B/C | game start | the opening tune (see below), 3 voices |
| 0C / 0D | Game over song | game over | 2-voice sad ending |
| 0E | Music voice B | | companion voice for 08 |
| 0F / 16 | Main song after intro (+ voice B) | after intro | the looping gameplay theme |
| 10 | Frog landing safe | frog enters bay | bright chime, tone 0x50, long delay counter |
| 11 / 12 / 13 | Level complete (3 voices) | five homes | triumphant jingle |
| 14 | Reset program | boot | none |
| 15 | Snake on the ground | snake appears | sliding four-step tone 0x100 -> 0x60 -> 0x30 -> 0x20 (a "hiss/slither" glide) |
| 17 | Race car | race car passes | **noise** channel, period 18, pulsing amplitude: engine whoosh |
| 18 | Pick up mate | lady frog boarded | tone 0x300 with a 16-count: a low "boop" |

Not in the table: no separate all-home bonus sound (cmd 11 covers it) and no dedicated time-out sound (the
drown/squash jingle plays with the skull **(unverified which)**).

### Music: what the tunes are

| Slot (sound ROM song #) | Identified as | Status |
|---|---|---|
| 0 Main song intro / game start | first verse of **"Inu no Omawarisan"** (The Dog Policeman), Japanese children's song, music Yoshimi Sato 1960 | Wikipedia; arcade-museum forum |
| 25 Main song (gameplay loop) | opening theme **"Rock River e"** of the anime *Araiguma Rascal* (1977) — "later used as the main gameplay theme" | Wikipedia (Rascal article via forum), tenshi-a blog; TCRF: the last 8 s of the loop never play because the timer (31.7 s) always runs out first |
| 5-24 Frog-home interludes (20 tunes, played in rotation) | a medley: *Hana no Ko Lunlun* OP, *Alps no Shoujo Heidi* OP "Oshiete", *Mahou Shoujo Lalabel* OP "Hello Lalabel", *Moero Arthur* OP snippet, **"Yankee Doodle"**, **"Camptown Races"**, plus unidentified ones | tenshi-a blog (fan identification), Wikipedia; which slot is which **(unverified)** |
| 1 Game over, 2 Level complete, 3 Respawn | original Konami jingles | CA SoundCode |

Wikipedia states "The American release has the same opening song plus 'Yankee Doodle'"; the Sega sets share the
Konami sound ROMs in MAME, so the difference is most likely which interlude the player hears, not different
ROMs **(unverified)**.

### Rights note (what NOT to reuse)

- "Inu no Omawarisan" (1960, Sato/Sato) and the anime openings ("Rock River e" 1977, "Hana no Ko Lunlun"
  1979, "Oshiete" 1974, "Hello Lalabel" 1980, "Moero Arthur" 1979) are **copyrighted works**; Konami's use
  appears unlicensed ("seems unlikely that Konami did this with permission"). Do not transcribe them.
- "Yankee Doodle" and "Camptown Races" (Foster, 1850) are public-domain melodies and could be used, but a
  recognisable arrangement would still read as "the Frogger sound"; an original tune is safer and more fun.
- The sound effects themselves are not musical works, but recreate them from the descriptions above, not
  from recordings.

## 7. Konami vs Sega/Gremlin differences

- Code: Sega set 1 is the Konami ROM with the copyright string changed to `SEGA © 1981` and the `FIYE HOMES`
  typo fixed. Sega set 2 (rug `X`) replaces the point table with instruction/scoring screens and is reported
  as the hardest difficulty; set 3 (rug `I`) medium; Moon Cresta-hardware conversion (rug `K`) also has the
  instruction screens. Set 4 runs on Konami M-1300 boards.
- Graphics ROMs (`frogger.606/.607`) and colour PROM (`pr-91.6l`) are identical across Konami and all Sega sets
  in MAME: **no in-game art differences**. Bootlegs differ (white frog legs on "Frog"/"Quaak", blue titles).
- Cabinet: Sega/Gremlin shipped wood-grain "convert-a-cabinets" and cocktail tables with a side-art frog
  carrying a suitcase; Konami's Japanese cabinets differ (not relevant to the screen).
- Controls: 4-way stick, no buttons, mono speaker.

## 8. Sources

- MAME source: https://raw.githubusercontent.com/mamedev/mame/master/src/mame/galaxian/galaxian.cpp ,
  .../galaxian_v.cpp , .../galaxian.h
- Computer Archeology, Frogger: https://computerarcheology.com/Arcade/Frogger/ (Hardware.html, Code.html,
  RAMUse.html, GFX.html, SoundCode.html, SoundHardware.html; GFX source
  https://raw.githubusercontent.com/topherCantrell/computerarcheology/master/content/Arcade/Frogger/GFX.md)
- Native screenshot analysed: https://en.wikipedia.org/wiki/File:Frogger_game_arcade.png (224x256)
- Wikipedia, Frogger: https://en.wikipedia.org/wiki/Frogger
- Arcade-museum (KLOV) Frogger: https://www.arcade-museum.com/Videogame/frogger
- Arcade-museum forum, "Origin of Frogger's opening song": https://forums.arcade-museum.com/threads/origin-of-froggers-opening-song.536878/
- tenshi-a blog, "The Music of Frogger": http://tenshi-a.blogspot.com/2009/11/music-of-frogger.html
- classicarcadegaming.com, "Different versions of Frogger": https://www.classicarcadegaming.com/forums/index.php/topic,7022.0.html
- classicgaming.cc Frogger: https://www.classicgaming.cc/classics/frogger/about
- PixelatedArcade Frogger: https://pixelatedarcade.com/games/frogger
- all80s.co.uk Frogger: https://www.all80s.co.uk/frogger
- TCRF Frogger (Arcade) (bot-walled; cited via search snippets only): https://tcrf.net/Frogger_(Arcade)
- StrategyWiki Frogger/Gameplay (bot-walled; cited via search snippets only): https://strategywiki.org/wiki/Frogger/Gameplay
- Frogger fandom wiki (paywalled fetch; music list via search snippet): https://frogger.fandom.com/wiki/Frogger_(video_game)
- Arcade History GX392 entry (hardware clocks via search snippet): https://www.arcade-history.com/game/879/frogger-model-gx392

## Notes for original asset design

- Keep the geometry, change the drawing: 16-px lanes, 13 hops bottom-to-top, five 16-px bays 48 px apart,
  8x8 HUD glyphs. The feel comes from the grid, not from the exact pixels. Draw our own frog (e.g. different
  eye placement, a belly stripe) and our own vehicles (a van, a taxi, a pickup) in the same lane colour
  scheme: yellow / white-green / pink-cyan / white-red / white-red-cab so each lane still reads instantly.
- Use the measured palette family (saturated values) rather than Konami's PROM order: dark navy top half,
  black bottom half, one green, one red, one yellow, lavender-white, purple, pink, cyan, two browns. Twelve
  colours total is enough and keeps the SVG named formulas tiny.
- Logs: brown cylinders with a darker lower third and light end caps, three lengths (~3, ~4, ~6 tiles).
  Turtles: red shells with green limbs is the arcade identity; shift to orange shells or a different limb
  animation to stay original while keeping the "red on blue" readability.
- Draw logical pixels 2:1 wide only if we go for the Atari-8-bit look; the arcade is square-pixel 224x256.
  Decide once (see the platform notes) and keep every sprite on the same pixel aspect.
- Deaths: a 3-frame squash (widen, flatten, streak) and a 3-frame ripple sink, both ending on a skull, at
  ~16 frames (about 0.27 s) per phase; copy the timing, not the frames.
- Time bar: 120 px green strip at the bottom right next to a yellow `TIME`, draining toward the label in 2-px
  steps, red for the last ~10 units with an alarm tick; ~32 s per frog.
- Sound: one square-wave "voice" for effects and two for music is the texture. Hop = 60-ms pitch slide up;
  squash = low buzz; drown = three falling tones with a muffled low-pass; home = bright chime; race car =
  filtered noise burst; coin = two rising dings. Write an original 2-voice tune in a bouncy major-key
  children's-song style (6/8 or straight 4/4, ~120-140 bpm, lots of repeated I-IV-V phrases), an 8-bar
  home-jingle set (several short variants in rotation like the arcade's 20), and a 4-bar game-over phrase.
  Never transcribe the Japanese songs or the anime themes.
- Attract: big blocky title letters that frogs hop into place, a point table, a ranking screen, copyright
  line stating non-affiliation; the "rug" power-on pattern is a nice optional nod.
