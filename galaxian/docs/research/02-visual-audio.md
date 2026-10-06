# Galaxian (Namco, 1979) — Visual and Audio Reference

Research notes compiled 2026-10-05. Sources: Scott Tunstall's annotated disassembly, MAME's `galaxian_v.cpp` and `galaxian_a.cpp`, the decoded colour table from the galaxian500 project, and the fan sites listed at the end. Hardware minutiae are kept only where they explain how the game looks or sounds.

## 1. Screen and palette

- Portrait field **224 wide x 256 tall**. Background black. Everything is built from 8 x 8 tiles and 16 x 16 sprites, so all art is on an 8-pixel grid.
- The game uses only about **17 distinct tile and sprite colours**, in 8 colour sets of 3 colours each (plus transparent). Decoded values as MAME renders them:

| Set | Used for | Colour 1 | Colour 2 | Colour 3 |
|---|---|---|---|---|
| 0 | "1UP" and "HIGH SCORE" labels | black | black | #DEDEF7 off-white |
| 1 | Flagship | #DE4700 orange-brown | #0000F7 blue | #FFFF00 yellow |
| 2 | Red alien (escort) | #0068F7 blue | #FF0000 red | #FFFF00 yellow |
| 3 | Purple alien | #0000F7 blue | #9700F7 violet | #FF0000 red |
| 4 | Blue/cyan alien | #0000F7 blue | #0097A8 teal | #FF0000 red |
| 5 | Score digits, GAME OVER, PUSH START, CREDIT | black | black | #FF0000 red |
| 6 | Player ship, lives icons, wave flags, points text | #DEDEF7 off-white | #FF0000 red | #00DEF7 cyan |
| 7 | Player explosion, dying alien | #DEDE4F yellow | #FF0000 red | #DE00F7 magenta |

- **Shots:** the player's shot is a **yellow 1 x 4 vertical dash** (#FFFF00). Enemy bombs are **white 1 x 4 dashes** (#FFFFFF). The "red and yellow zigzag" bomb is Galaga, not Galaxian.
- **Stars:** 64 pastel colours (each RGB channel at one of four levels: 0, 194, 214, 255), for example #C2C2FF, #FFC2C2, #D6FFD6. Roughly 100 to 120 visible at once. The starfield drifts **down 1 px per frame** (about 60 px/s). Each star is visible for 8 frames then hidden for 8, which produces the characteristic twinkle (derived from the MAME code, not stated by it). Stars draw behind everything.

## 2. Sprites

- **Flagship:** yellow body with orange-brown and blue detail. Distinct shape. Does **not** animate in formation.
- **Red, purple, and cyan aliens share the same shape.** Only the colour set differs. This is a big simplification for a recreation: one alien shape in three palettes.
- In formation the non-flagship aliens hang "upside down like bats". Divers are flipped and rotated to face their direction of travel.
- **Wing flap:** a 4-step cycle using 3 glyphs, **A-B-A-C**. Each column of the formation advances its frame every 16 frames (about 0.26 s), staggered by column, which creates the ripple across the swarm.
- **Alien explosion:** 4 frames, each held 4 game frames (about 0.27 s total), in yellow, red, and magenta (set 7). A flagship killed in flight then shows its point value (150, 200, 300, or 800) for 50 frames.
- **Player ship (Galaxip):** 16 x 16. Off-white hull, red centre stripe, cyan side pods (set 6). **Player explosion:** 4 frames of a 32 x 32 burst, each held 10 frames (about 0.66 s), in set 7.
- **Lives icons:** small copies of the ship. **Wave flags:** a small red flag per wave (8 wide x 16 tall), replaced by a wider "10" flag (16 x 16) every ten waves.

## 3. HUD layout (screen pixels)

- Row y 0 to 7, off-white: **"1UP"** at x 24 to 47; **"HIGH SCORE"** centred at x 72 to 151; "2UP" at x 176 to 199 only in two-player games. "1UP" blinks every 16 frames during play.
- Row y 8 to 15, **red**: the score digits (6 digits, leading zeros suppressed down to "00") and the high score.
- Bottom band y 240 to 255: **lives** bottom-left as 16 x 16 ship icons from x 0 (reserve lives only, up to 4 shown). **Wave flags** bottom-right drawn from x 208 leftwards; 16 tile widths reserved. Wave display caps at 48.
- Playable area is effectively y 16 to 239.
- Attract texts use the red set: GAME OVER, PUSH START BUTTON, CREDIT n, BONUS GALAXIP FOR 7000 PTS. The "WE ARE THE GALAXIANS / MISSION: DESTROY ALIENS / - SCORE ADVANCE TABLE - / CONVOY CHARGER" page scrolls each alien in from the side with its points.
- **Font:** the 8 x 8 Namco arcade font. A free TTF recreation exists ("Galaxian1979.ttf", licence unstated).

## 4. Layout geometry

- Formation: 6 rows x 10 columns, 46 aliens. **Column pitch 16 px**, formation width 160 px, spanning x 32 to 191 at centre (32 px margins). **Row pitch 12 px**; row centres at y 40, 52, 64, 76, 88, 100.
- Flagships in columns 4 and 7 of 10 (survivors fill 5 and 6). Reds in columns 3 to 8. Purples in columns 2 to 9. Cyan fill all 10.
- **Sway:** scroll runs about -32 to +32 px, 1 px every 4 frames, reversing at the limits. The limit grows by 16 px for each emptied edge column. The swarm also freezes briefly while the player's shot is inside the formation's vertical band in a column that still has aliens.
- **Player:** 16 x 16 at **y 224 to 239**, spawn at centre, horizontal range about x 0 to 208 (ship left edge), 1 px per frame.
- **Player shot:** spawns just above the ship, 4 px per frame, expires just under the score rows (about 50 frames).

## 5. Audio

All sound was discrete analog circuitry, no sound chip. What matters for a recreation is how each effect behaves:

| Effect | Behaviour |
|---|---|
| **Background hum** | Three detuned low oscillators (roughly 140, 190, 270 Hz) swept by a slow LFO. All three play while 3 or more aliens remain in formation; 2 aliens leaves 2 oscillators, 1 alien leaves 1, none is silent. The LFO starts slowest at each new wave and **steps one notch faster every 256 frames (about 4.2 s)**, reaching fastest after about 63 s. It is **time-driven**, not kill-driven. |
| **Player shot** | Short "pew": a 2.7 kHz tone modulated by noise with fast decay, about 8 frames. |
| **Dive whistle** | While any alien is in flight, a tone sweeps downward in pitch, lowering as the alien descends. |
| **Alien hit** | A 33-note zip about 0.55 s long: a short descending run, then rising, then a wobble. |
| **Flagship hit** | A longer jingle with rests, about 50 frames. |
| **Player death** | Filtered noise rumble held for the whole 40-frame explosion. |
| **Game start tune** | An 11-note descending glissando, then a short melodic phrase repeated twice, a trill, and a fast rising run repeated four times. Scale is roughly F-sharp/B major. |
| **Extra life** | About 2 s of a 750 Hz tone gated on and off every 4 frames. |

- Composer: Toshio Kai.
- No freely licensed recordings exist. Recreations synthesize these procedurally. For this project, short original WAV or MP3 files will be produced from these descriptions.

## 6. Reference assets and implementations (reference only; Namco owns the IP)

- Sprite reference: https://www.spriters-resource.com/arcade/galaxian/ and http://seanriddle.com/galaxiansprites.html
- Font: https://arcade.itch.io/arcade-game-typography-fonts/devlog/573422/galaxian-namco-1979
- CC0 look-alike sprite sets that can be shipped: https://opengameart.org/node/15368 and https://opengameart.org/content/1616-ship-collection
- MAME video and audio source (BSD-3): https://github.com/mamedev/mame/tree/master/src/mame/galaxian
- Annotated disassembly: https://github.com/jotd666/galaxian500 (`src/galaxian_z80.asm`)
- Wireframe #50 Pygame Zero attack-pattern recreation (CC BY-NC-SA): https://github.com/Wireframe-Magazine/Wireframe-50
- HTML5 canvas tutorial (MIT): https://github.com/stijnkuppens/galaxian-canvas-game
- Vanilla JS recreation with procedural sprites and WebAudio: https://github.com/juliensimon/browser-games/tree/main/galaxian (note: its 18 px spacing is not arcade-accurate)

## 7. Caveats

- HUD pixel positions are derived from character RAM addresses and may be off by one tile.
- Colour values are MAME's rendering. Real monitors differ slightly.
- The star twinkle mechanism is inferred, not documented.
- Absolute tone frequencies may be off by a power of two; relative pitches are reliable.
