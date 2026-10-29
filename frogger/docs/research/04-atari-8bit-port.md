# Frogger on the Atari 8-bit computers: the two ports

Research note, 2026-10-28. For the canvas Power Apps rebuild (20 ticks/s, fixed Image pools, tap input).

There were **two** licensed Froggers for the Atari 400/800/XL/XE, plus a little-known second Sierra build:

| | A. Sierra On-Line, 1982 | B. Parker Brothers, 1983 |
|---|---|---|
| Full title on box | *The Official Frogger by Sega*, "SierraVision" label | *Frogger*, "Parker Brothers Arcade/Action Software, Cartridge for Atari Home Computers" |
| Programmer | John Harris (code, graphics, sound); music routines by a friend of his in San Diego | Steve Kranish (code), Dawn Stockbridge (graphics), working **from Harris's object code** |
| Media | Cassette (16K) and diskette (32K) | 8K ROM cartridge (16K RAM required) |
| Players | 1 | 1 or 2 alternating |
| Music during play | Yes, continuous (disk only) | No, only a jingle when a frog/level starts |

The single most important finding: **the Parker Brothers cartridge is a cut-down, re-skinned build of John Harris's
Sierra code.** Parker bought the rights from Sierra, Harris had lost the source, and Kranish disassembled the 13K
cassette image and squeezed it into 8K in six weeks, adding two-player mode and new graphics. Both games therefore
share the same lane geometry, the same scoring core and the same basic feel; they differ in HUD, colours, music,
otters and the two-player option. Measured screenshots confirm identical row boundaries (see A.1 and B.1).

Everything below is sourced; anything I could not confirm is marked **(unverified)**.

---

## A. Sierra On-Line, 1982 (John Harris)

### A.1 Screen layout

**Display mode (inferred from screenshots and Levy; no technical doc exists) (unverified):** a 40-column
character-mode playfield (the lanes are drawn with hatched log/brick textures that are clearly character cells),
with display-list interrupts recolouring each band and player/missile graphics for the frog and probably the other
multicolour movers. Levy quotes the rewrite as having "forty-four colors, the player-missile graphic routines fully
redefined, and a couple of neat tricks that managed to make the eight bits of the Atari 6502 chip emulate ten bits"
(Hackers, ch. 18). Harris's dev machine was an Atari 800 with 48K plus Axlon 128K (Halcyon Days).

**Measured layout** (Atarimania screenshot `frogger_v1.gif`, 336x240 emulator capture; x in hi-res pixels,
y in scanlines; playfield spans x 8-327 = 320 px = 40 characters; every band is a multiple of 8 scanlines):

| Band | Scanlines | Height | Colour (as captured) | Contents |
|---|---|---|---|---|
| Border | all | | grey #a2a2a2 | background/overscan colour is grey in this version |
| Top HUD | 16-23 | 8 | purple #6c1fed band, light-purple text | `SCORE: 000000` left, frog-life icons centre, `FAST`/`SLOW` right |
| Home bank | 24-39 | 16 | green hatch #00ab04 on black | five black arches (home bays), bay pitch 64 px, bay mouth ~24 px |
| River lane 5 (top) | 40-55 | 16 | water #2010da | medium logs, ~78 px, olive hatch #204b00/#bf9e11, moving right |
| River lane 4 | 56-71 | 16 | water | turtles (red #78037a shells, green legs), 24 px pitch, groups of 2 and 3, moving left; diving turtles drawn as a white dotted outline |
| River lane 3 | 72-87 | 16 | water | long logs ~142 px, brown #451200, moving right |
| River lane 2 | 88-103 | 16 | water | short logs ~62 px, brown, moving right |
| River lane 1 | 104-119 | 16 | water | turtles (dark-blue/green), 20-22 px, groups of 3, moving left |
| Median | 120-135 | 16 | green hatch #00dc04 on black | safe strip; snakes crawl here on round 3+ |
| Road lane 4 (top) | 136-151 | 16 | black | purple cars #8812bb, 24 px wide, 96 px pitch (4 per lane) |
| Road lane 3 | 152-167 | 16 | black | one pink/orange racer, 24 px, fast |
| Road lane 2 | 168-183 | 16 | black | purple/blue cars, 24 px, 96 px pitch |
| Road lane 1 | 184-199 | 16 | black | bulldozers/trucks, 24 px, multicolour (blue, green, orange) |
| Start row + timer | 200-215 | 16 | grey | `TIME` in red at left, orange/red time bar from x 88 to ~261; the frog starts on this row |
| Bottom HUD | 216-239 | 24 | grey | `HIGH: 000000` in light blue, centred |

So the whole picture is 28 character rows (224 scanlines) tall, taller than the standard 24-row display. Each lane is
exactly two character rows (16 scanlines); a forward hop is 16 scanlines. Cars are 3 characters (24 px) wide; short,
medium and long logs are roughly 8, 10 and 18 characters; a turtle occupies one 3-character slot. Lane directions
match the arcade (COMPUTE!: "turtles in lanes 1 and 4 swim left; logs in lanes 2, 3 and 5 float right"; road lanes
alternate). Horizontal hop distance and whether the frog is grid-snapped horizontally: **(unverified)**.

### A.2 Gameplay vs. the arcade

Sources: the SierraVision manual (3-page folded sheet, scanned on Atarimania) and the COMPUTE! review (March 1983,
Larry Isaacs). The manual verbatim:

- "Move frog vertically or horizontally using joystick. Object is to safely maneuver frog to its home within allotted
  time (120 beats of the timer). Cross highway without getting run over and cross river without falling in. Avoid
  traffic, deadly snakes, otters, crocodiles, and the treacherous diving turtles."
- Scoring: forward jump 10; safely arriving home 50; beating the timer 5 pts per beat saved. Bonus: escorting home a
  lady frog 200; gobbling an insect 200; getting all five frogs home 1000.
- Special features: "Toggle music (not sound) - select key. Replay game - start key. Fast/Slow - option key. An extra
  frog every five levels. Sound control is through the monitor. Music and otters not available on cassette version."

COMPUTE! adds:

- **Lives:** five frogs; game over when all five are lost. Losing a frog: hit by a vehicle, falling in the river,
  carried under by a diving turtle, hitting the wall beside a home bay, or time out. "A skull and crossbones marks the
  spot briefly." (Screenshots show a yellow splayed frog with white droplets for a water death.)
- **Timer:** 120 counts, about 32 seconds, shown as an orange bar that shrinks. "Twice as many time counts as the
  arcade but only 5 points per count" (arcade: 30 s, 10 pts per half-second).
- **Road:** four lanes, alternating directions, each at a different speed.
- **River:** five lanes; rest on the riverbank (median) first. Some turtles submerge. The frog must hop from the last
  log lane straight into an arch; hitting the bank beside it kills the frog.
- **Levels:** each round harder. Traffic increases and gets trickier; lane 3 has fewer logs; some lane-5 logs are
  replaced by alligators (ride the back; too close to the mouth and you are eaten); alligators sometimes sit in empty
  homes. **Round 3 and beyond:** snakes on lane-3 logs and on the riverbank; they do not chase you but kill on contact;
  you can hop away from a snake but not over it. **Otters** (disk only) swim among logs and turtles and eat the frog.
- **Insect (fly)** appears in an empty home for 200. **Lady frog** rides a log; carry her home for 200.
- **Players:** one only (COMPUTE!). Atarimania lists "1, 2 (alt.)" for this entry; COMPUTE! is the primary source,
  so treat two-player as **not present** in the Harris build.
- **Joystick:** forward/back/left/right, no diagonals; "each hop requires returning the stick to neutral before pushing
  again" (no auto-repeat while held). Response "very quick and quite sensitive".
- **Speed:** OPTION toggles FAST/SLOW; FAST is the default; can be changed mid-game. Shown top-right.
- **High score:** kept on screen (`HIGH:`), and the disk version can save it (Atari Compendium).
- **Game over:** a `GAME OVER` sign floats across the river on a log (screenshot; same gag as Sierra's C64 version).

Extra life: every five levels (manual), not the arcade's 20,000 points.

### A.3 Sprites

From the screenshots: the frog is green with yellow highlights, about 16x16 (two character rows tall). Cars are 24 px
wide, two-tone (purple body, blue/orange wheels and lights); the racer is pink/orange; bulldozers are multicolour with a
blade. Logs are olive or brown with a hatched wood texture and lighter rounded ends (white/yellow oval end-grain).
Turtles are red-shelled with green flippers; a submerged turtle is drawn as a white dotted ring. Alligator: dark green,
long, with an open jaw at the head end. Snake: light blue on logs, green on the median. Lady frog: pink. Dead frog:
yellow. Life icons: small frog glyphs in the top band. Creative Computing's review of the C64 sibling praises "the
turning bulldozer treads, the three-dimensional logs" and a frog "more realistic than the arcade"; the Atari original
is the same design (Harris's shapes were the template for the C64 port) **(the C64 parallel is unverified)**.

### A.4 Sound and music

Levy: "A friend of John's in San Diego had written some routines to generate continuous music, using the three-voice
sound synthesizer chip in the Atari to mingle the strains of the original Frogger theme with Camptown Races, all with
the gay contrapuntal upbeat of a calliope." (POKEY has four voices; Levy says three.) After the rewrite the friend
"made some improvement on the three-voice concurrent sound track". COMPUTE!: "the music is among the best I've
heard on any game"; effects: a bleep per hop, distinct sounds for each way of losing a frog. SELECT toggles music;
**cassette version has no music at all**. This continuous calliope-style soundtrack is the signature of the Harris
version; the retro365 article calls it "joyful and looping".

### A.5 Title screen and attract mode

There is no separate title picture: after loading you land directly on the playfield with `SCORE: 000000`, the five
frog icons, `FAST` top-right, `TIME` bar full and `HIGH: 000000`; pixelatedarcade labels this "Starting screen" and
you press START to play. Whether the field animates as an attract demo while waiting: **(unverified)**. The disk
boots to the game; the cassette loads with START held at power-on, one beep, RETURN. Packaging: blue box, red
"The Official FROGGER by Sega" logo, cartoon frog in a red scarf leaping in front of a red truck, "SierraVision" at
the bottom, a round sticker "ATARI VERSION / JOHN HARRIS / 16K CASSETTE / 400/800 / SRL 403" (or the disk
equivalent). The manual sheet reads "THE OFFICIAL FROGGER by SEGA - ATARI VERSION BY JOHN HARRIS - THE GAME".

### A.6 Bugs, quirks, reception

- COMPUTE! (March 1983): "among the best games available for the Atari"; difficulty curve praised; joystick "touchy at
  first". Price $34.95.
- Levy: first month's royalty cheque $36,000; "number one on Softsel Distributors' new Hot List ... staying there for
  months"; Ken Williams was quoted claiming Harris earned $300,000 a year (a four-month royalty cheque was $160,000).
- Atarimania user rating 7.5/10 (327 votes). Atari Compendium: tape lacks music, otters and high-score save.
- Antic, ANALOG, Electronic Games and Softline reviews: **not located** in the online archives searched (Antic June
  1983 full text has no Frogger review; ANALOG and Electronic Games scans not indexed). Softline's Dec 1982 issue
  reviewed the *Apple* version savagely ("as much soul as month-old lettuce in the Sahara") while praising the Atari
  one (Levy ch. 19).
- The otters and the "GAME OVER on a log" are the two details people remember.

### A.7 Technical, load, copy protection

- RAM image: "13K" (Kranish); cassette needs 16K, disk 32K. Code was developed in small blocks scattered through
  memory with "debris" between them (Kranish), which is why the cart conversion needed a full disassembly.
- Copy protection: Levy mentions a "logjam in packaging, marketing and copy protection" that delayed release two
  months after Harris delivered; no technical details of the disk scheme were found **(unverified)**. Atarimania has a
  dumped copy, so it was cracked.
- The theft: at Software Expo, a muscular-dystrophy charity show in San Diego, about two months into the project,
  Harris's whole disk box (the only Frogger copies plus all his tools) was stolen while he was talking to an admirer.
  He wrote almost nothing for two months, worked as an arcade cashier, then rewrote the game from scratch with
  embellishments. A Synapse programmer later lifted a sound routine from the stolen disk's object code.
- Aftermath: Parker Brothers offered Sierra about $200,000 for the code; Ken Williams offered Harris 20% of it;
  Harris refused, they fell out ("Get out of my office, John Harris"), and Harris left for Synapse (25% royalty).

### A.8 Disassembly or source

None public. Harris lost his only source copy; Sierra never had it. Kranish's 1983 commented disassembly (printed,
"two inches thick") was Parker Brothers property and has not surfaced. Nothing on AtariAge or GitHub for the 8-bit
build (only a 2600 DiStella listing exists). Timing and lane tables must therefore be measured from emulation.

### A.9 The second Sierra build: Chuck Benton (c. 1983-84)

Sierra also sold an "ATARI VERSION BY CHUCK BENTON" on cassette and disk (box stickers "FOR 1 OR 2 PLAYERS";
cassette packages included a "Mr. Cool demonstration" insert; a 1984 Sierra-branded Commodore 64 / Atari flip disk
carried a Benton manual for each side). Atarimania (entry 12181) lists it as 1 / 2 alternating / 2 simultaneous
players; Atari Compendium says head-to-head two-player; an Atarimania commenter says the code "appeared to be done
by someone that knew the 6502 but not the Atari that well" with "sound and music nearly identical" to Harris's.
Kranish says Benton's 19K version existed but was unfinished when Parker came asking (AtariAge thread 109915, via
search snippet) **(unverified)**. Atarimania rating 7.8/10 (29 votes); no screenshot or dump archived there. If the user
remembers a two-player Sierra Frogger on tape or disk, it was this one.

---

## B. Parker Brothers, 1983 (Steve Kranish / Dawn Stockbridge)

### B.1 Screen layout

Same engine, so the same 40x28 character picture and 16-scanline lanes. Measured from Atarimania's
`frogger_parker_bros.gif` and the pixelatedarcade set:

| Band | Scanlines | Colour (as captured) | Contents |
|---|---|---|---|
| Border | | dark green #004301 | the whole background is dark green, not grey |
| Top HUD | 0-23 | green text on dark green | `SLOW`/`FAST` upper-left (manual: "the speed is indicated in the upper left-hand corner"); remaining-frog icons upper-right (manual: "the remaining frogs are shown on the upper right-hand corner"). **No score at the top.** |
| Home bank | 24-39 | yellow/orange hatch #ffc500/#ff0000 | five dark arches ("home bays"), bushes between them are fatal ("if your frog hits the sides of the bay, you'll lose him") |
| River lanes 5..1 | 40-119 | water #321fff | same five lanes, same object sizes (78 / 22 / 142 / 62 / 20-22 px); logs red-brown #e00800/#b12000 on level 1, turtles green #428300 with yellow #ffc500 |
| "Sidewalk" (median) | 120-135 | red brick #660d00 on black on level 1 | **changes graphic every level**: red brick, tan brick, grey stone seen |
| Road lanes 4..1 | 136-199 | black | purple cars #a81de3, pink racer, blue cars #5141ff, orange bulldozers #ff8900 |
| Grass + timer | 200-215 | dark green | `TIME` red at left, orange time band x 88-~283 |
| Bottom HUD | 216-239 | dark green | `1UP` + score bottom-left (light blue), `2UP` indicator bottom-centre in a 2-player game, right player's score bottom-right |

The manual's own diagram (page 3) labels: Remaining Frogs, Home Bays, Speed of Game, Sidewalk, 1-player Score,
2-player Score, Time Band, Grass, 2-player Game Indicator.

### B.2 Gameplay vs. the arcade (and vs. Sierra)

Parker Brothers 8-page manual (scanned on Atarimania, Rules (c) 1982, 1983 Parker Brothers, Beverly MA):

- **Setup:** SELECT chooses 1- or 2-player ("You'll see '2 UP' on the bottom center of the screen"); OPTION "now or
  at any time during a game" chooses slow or fast; START or FIRE begins; FIRE restarts after game over.
- **Joystick:** "Use the Joystick to jump your frogs forward, backward, and to the left and right." Whether the stick
  must return to centre between hops is not stated; since the code is Harris's, assume the same neutral-then-push
  behaviour **(unverified)**. The 5200 build differs: stick aims, fire button hops (Kranish: the non-centring 5200
  stick forced this, "the cartridge got the version everyone disliked the least").
- **Lives:** "Start the game with 5 frogs."
- **Timer:** "approximately 30 seconds to get a frog home"; warning sound when a few seconds remain; time out loses
  the frog. (The 5200 manual adds that the band changes colour near the end.) Bonus: **10 points per remaining second**
  (vs. Sierra's 5 per beat of 120).
- **Scoring:** forward hop 10; into a home bay 50; five frogs home 1000; rescuing the pink lady frog 200; eating a
  bonus fly 200; time bonus 10/second.
- **Hazards:** vehicles ("you'll lose your frog if it touches any part of a vehicle"); falling off the end of a log or
  turtle row sideways; drifting off either screen edge on a river object; diving turtles ("it's okay to jump onto the
  back of a partially submerged turtle, but you'll have to hop off before the turtle dives"); alligators in the river
  ("okay to jump on the back of an alligator or snake, but not on their heads"); alligator head showing in a home bay
  makes it unsafe; occupied bays cannot be entered.
- **Lady frog:** "hop your frog exactly onto the pink lady frog and take her home".
- **Difficulty:** "After you bring 5 frogs home, the game will continue at a more difficult level with your remaining
  frogs. The speed and density of the traffic and floating objects will vary, and snakes will appear on the sidewalk
  and logs." Plus (Kranish) the sidewalk and other graphics change each level "because we could".
- **Otters:** not mentioned anywhere in the manual or box; given the 13K-to-8K cut, assume removed **(unverified)**.
- **Extra life:** not mentioned in the manual; unknown whether Sierra's every-five-levels frog survived **(unverified)**.
- **Two players:** alternate turns; left player first; turn ends when a frog is lost; either player may change speed
  at the start of a turn (5200 manual); game ends when both are out of frogs.
- **Dying:** a yellow flattened-frog sprite is drawn on the spot (screenshot); the river death shows the same yellow
  frog with white droplets.

### B.3 Sprites

Same shapes as Harris's for the frog, cars, racer, bulldozers, logs, turtles, alligator, snake, lady frog and fly, but
re-coloured by Dawn Stockbridge and re-themed per level: level 1 has red-brown logs, green turtles with yellow legs,
red brick sidewalk, orange bulldozers; later levels seen with grey turtles and tan brick, and red/orange turtles with
grey stone. The alligator is brown with a white-toothed jaw; the snake is yellow-tan; the lady frog pink; the home-bay
alligator shows as a snout in the arch. The frog is green with yellow eyes, same 16x16 footprint.

### B.4 Sound and music

Box copy: "fast-paced action, arcade-like graphics, and even the familiar Frogger theme song". Manual: "When the music
begins, so does the time band - so start hopping!" Atari Compendium: "no music during gameplay, only at the beginning of
a level." So: a Frogger-theme jingle at the start, silence (effects only) while playing. Kranish: "I don't remember much
about the music." Whether the jingle plays per frog or per level: **(unverified)**; the manual wording suggests per frog.
Contemporary AtariAge posters remember the missing in-game music as the main disappointment of this version.

### B.5 Title screen and attract mode

No title picture: cartridge power-on shows the playfield with `SLOW` top-left (default appears to be SLOW in all
captures, the opposite of Sierra's FAST default **(unverified)**), frog icons top-right, `1UP 0` and a full orange
time band; pixelatedarcade: "Starting screen; you can select game options here." Attract animation: **(unverified)**.
Packaging: beige/gold box, "PARKER BROTHERS ARCADE/ACTION SOFTWARE", green FROGGER logo in a yellow diamond, a
frog recoiling from a white alligator, "CARTRIDGE FOR ATARI HOME COMPUTERS - Under License from Sega Enterprises
Inc." Product no. 73000-01110 (serial 1110); European Parker Brothers International serial 942001 with a 14-page
multilingual manual.

### B.6 Bugs, quirks, reception

- **Easter egg, removed:** on level 6 or 7 landing on the lady frog turned the frog into Kranish's initials "BK". A
  tester found it while he was away; management had it removed and withheld his completion bonus. The hidden credit
  string `@1983 PARKERBROS B KRANISH` at the end of the ROM survived (Atari Compendium / Scott Stilphen; TCRF puts it
  at 0x1FE0 in the 8-bit ROM, 0x1FDD in the 5200 ROM, per search snippet).
- Personal Computer Games #7 (UK, 1984): "a superb cartridge version of Frogger for the Atari"; praised the fast/slow
  option "that some Frogger imitators omit" and the manual's colour screenshots; no tips for novices.
- Atarimania 8.2/10 (223 votes), the highest of the three Atari 8-bit entries. AtariAge opinion is split: some call it
  the better port ("improved graphics, 2-player"), others "the Parker Brothers port is poor on every system".
- Kranish's cartridge-shell story: test shells fit the 800 but not the 400's slot; reporting it nearly got him fired.
- Antic / ANALOG / Electronic Games reviews: **not located**.

### B.7 Technical

- 8K ROM (Kranish: "fit it into 8K"; the 13K cassette image was the input). 16K RAM, joystick required. Atari
  400/800/1200XL. The 5200 cartridge is "the same code and graphics, modified for the 5200 memory map and
  controllers" (Kranish on Atarimania).
- Developer attribution conflict: Atarimania credits Roklan Corp. as developer; Kranish describes himself as a Parker
  Brothers employee who did the work in-house and wrote Parker's 5200 porting manual. Treat "Roklan" as
  **(unverified)**.
- Method (Atari Compendium interview): three-path 6502 disassembler (1-, 2- and 3-byte instruction passes plus a
  bitmap dump of candidate graphics), remove the "debris", comment every line, reorganise top-down with graphics at high
  addresses; six weeks, before fiscal year end.

### B.8 Disassembly or source

Kranish's commented listing is not public; he no longer has source for his Risk prototype either. No community
disassembly of the 8-bit cartridge was found. An 8K ROM with a known credit string at 0x1FE0 is a small, clean target
for da65 if a separate agent wants lane tables; look for the per-lane speed/direction table near the display-list and
DLI code.

---

## How to tell them apart in 10 seconds

1. **Background colour.** Sierra/Harris: grey border all round. Parker: dark green.
2. **Where the score is.** Harris: purple band at the top reading `SCORE: 000000`, with the frog-life icons in the
   middle and `FAST`/`SLOW` at the right, and `HIGH:` at the bottom. Parker: nothing but `SLOW` top-left and frog
   icons top-right; the score is `1UP nnnn` at the bottom-left, with a `2UP` indicator in two-player games.
3. **The strip between road and river.** Harris: green hatched grass (with a green snake on it later). Parker: a red
   brick "sidewalk" that turns tan brick, then grey stone, on later levels.
4. **Music.** Harris (disk): a continuous calliope medley of the Frogger theme and Camptown Races the whole game.
   Parker: a short theme jingle, then only hop bleeps.
5. **Turtles and bank.** Harris: red turtles, green home bank. Parker: green turtles, yellow/orange home bank.
6. **Two players?** Only Parker (and the rare Benton Sierra build).
7. **How it started.** Parker: cartridge, instant. Harris: cassette (hold START, beep, RETURN) or disk boot.

The user played an 800XL. Both run on it; the cartridge is far more likely to have been bought in 1983-85 (rarity 3
vs 5-7 on Atarimania, and it was the one in toy shops), but the Sierra disk was the famous one.

## Gaps the arcade research must fill

Neither port is documented at the level a tick-by-tick rebuild needs. Use arcade values, labelled, for:

- Per-lane speeds (pixels per frame) for road and river lanes, and how they scale by level; both manuals only say
  "speed and density vary". FAST/SLOW ratio is unknown **(unverified)**; measure in emulation.
- Vehicle counts and spacing per lane (screenshots show 4 cars at 96 px pitch in lanes 2 and 4, 1 racer in lane 3,
  4 bulldozers in lane 1 on level 1; later levels unknown).
- Log lengths and gaps per lane (measured: ~62 / 142 / 78 px on lanes 2, 3, 5; turtle groups of 3 and 2) and the
  reduced-log pattern of lane 3 on round 2+.
- Diving-turtle cycle (how long up, warning, how long down).
- Alligator share of lane-5 logs on round 2+; alligator-in-home and fly-in-home timing and duration.
- Lady-frog spawn rule and which lane; snake speed on logs vs median; otter speed and spawn (Sierra disk only).
- Timer: Sierra 120 beats ≈ 32 s (5 pts/beat); Parker ≈ 30 s (10 pts/s). Arcade is 30 s; choose per version.
- Extra life: Sierra every five levels; Parker unknown; arcade 20,000 points.
- Horizontal hop size and whether the frog is grid-snapped or carried fractionally on logs (sprites suggest 8 px
  character-cell hops; carry is fractional) **(unverified)**.
- Difficulty easing after five levels (arcade) - unknown in both ports.
- Attract/demo mode and any title screen text - none observed; confirm with a longplay.

## Sources

Primary documents (read in full for this note)
- Sierra manual scan: https://www.atarimania.com/8bit/files/Sierravision_Frogger_manual.pdf
- Parker Brothers manual scan (8 pages): https://www.atarimania.com/8bit/files/Frogger_Parker_Brothers.pdf
- Atarimania, Sierra/Harris entry (screenshot `frogger_v1.gif`, box scans, manual): https://www.atarimania.com/game-atari-400-800-xl-xe-frogger_6780.html
- Atarimania, Sierra/Benton entry: https://www.atarimania.com/game-atari-400-800-xl-xe-frogger_12181.html
- Atarimania, Parker Brothers USA entry (screenshot `frogger_parker_bros.gif`, manual, ads): https://www.atarimania.com/game-atari-400-800-xl-xe-frogger_5990.html
- Atarimania, Parker Brothers International (Europe) entry: https://www.atarimania.com/game-atari-400-800-xl-xe-frogger_6767.html
- COMPUTE! issue 34, March 1983, "Frogger for Atari" (Larry Isaacs): https://www.atarimagazines.com/compute/issue34/041_1_FROGGER_FOR_ATARI.php
- Steven Levy, *Hackers* (1984/2010), ch. 18 "Frogger", ch. 19 "Applefest", ch. 20 "Wizard vs. Wizards" (PDF mirror read via pdftotext): https://gateway.pinata.cloud/ipfs/QmXhRHDn7DtsrAiesjmun3JyrEinkrt8dSyJp9kds5yhxb/Hackers.pdf
- Steve Kranish interview (Atari Compendium, 2007): https://www.ataricompendium.com/archives/interviews/steve_kranish/interview_steve_kranish.html
- Atari Compendium easter eggs / version notes for A48 Frogger: https://www.ataricompendium.com/game_library/easter_eggs/a48/a48frogger.html
- pixelatedarcade Atari 8-bit screenshot sets (838 = Parker, 839 = Sierra): https://pixelatedarcade.com/games/frogger/screenshots
- retro365, "Frogger, finally an officially licensed game" (packaging photos incl. Benton version): https://retro365.blog/2023/02/01/bits-from-my-personal-collection-frogger-finally-an-officially-licensed-game/

Secondary
- ANTIC Interview 454, Steve Kranish (episode notes): https://ataripodcast.libsyn.com/antic-interview-454-steve-kranish-parker-brothers-frogger
- ANTIC Interview 200, John Harris (episode notes; audio at https://archive.org/details/JohnHarrisJawbreaker): https://ataripodcast.libsyn.com/antic-interview-200-john-harris-jawbreaker-frogger-mouskattack
- Halcyon Days, John Harris interview: https://dadgum.com/halcyon/BOOK/HARRIS.HTM
- Wikipedia, John Harris: https://en.wikipedia.org/wiki/John_Harris_(software_developer)
- Wikipedia, Frogger (arcade rules, licensing): https://en.wikipedia.org/wiki/Frogger
- Parker Brothers 5200 manual text (same code, different controls): https://discmaster.textfiles.com/view/1886/1000gamemanuals.iso/Atari%205200/Frogger.TXT
- Eli's Software Encyclopedia, Parker cartridge (part no., requirements, box copy): https://elisoftware.org/wiki/Frogger_(Atari_8-Bit,_Cartridge)_Parker_Brothers_-_1983_USA,_Canada_Release
- Personal Computer Games #7 review (snippets only; page would not load): https://everygamegoing.com/larticle/Frogger-000/31037
- Creative Computing Nov 1983, Sierra C64 Frogger review (sibling port): https://www.atarimagazines.com/creative/v9n11/134_Arcade_action_for_the_Com.php
- C64-wiki, Sierra Frogger (sibling port feature list): https://www.c64-wiki.com/wiki/Frogger_(Sierra_Online,_Inc.)
- AtariAge threads (blocked by Cloudflare for fetch; quoted via search snippets only): https://forums.atariage.com/topic/8173-sc-frogger-vs-atari-8bit-frogger/ , https://forums.atariage.com/topic/82200-why-starpath-frogger/page/2/ , https://forums.atariage.com/topic/109915-retro-gamer-magazine-cant-help-with-frogger , https://forums.atariage.com/topic/372056-rare-version-of-frogger-sierra-on-line-flip-diskette
- Antic June 1983 full text (checked, no Frogger review): https://archive.org/stream/1983-06-anticmagazine/Antic_Vol_2-03_1983-06_Data_Base_Survey_djvu.txt
