# Galaxian (Namco, 1979) — Gameplay Mechanics and Rules

Research notes compiled 2026-10-05. Primary source: Scott Tunstall's annotated Z80 disassembly of the Namco Galaxian ROM (public copies: https://seanriddle.com/galaxian.asm and https://github.com/jotd666/galaxian500). Secondary: arcade-history, shmups.wiki, Namco's galaga.com history page, Japanese and English Wikipedia, MAME source. Where this says "code", it means the disassembly.

## 0. Timing fundamentals

- Refresh rate 60.606 Hz. The player sees a **224 px wide x 256 px tall** field.
- The whole game runs on one interrupt per video frame. Every timer below is in frames (60.6 per second).
- Only aliens in flight are hardware sprites. The formation and the player ship are tile columns moved by scroll registers. This is why the formation moves in whole-pixel steps and never descends.

## 1. Player ship (Galaxip)

- **Movement:** horizontal only. 1 px per frame (about 60 px/s). Travel range 23..233, so 210 px of travel on a 224 px screen.
- **Firing:** strictly **one shot on screen**. Fire is edge-triggered (press, not hold). The shot flag clears only when the bullet hits a formation alien, hits an in-flight alien, or reaches the top. You cannot fire while a shot is in flight.
- **Shot speed:** 4 px per frame (about 242 px/s). Spawns just above the ship. A full-height miss takes about 50 frames (0.83 s). One bullet can kill two overlapping aliens.
- **Lives:** DIP-selectable. Namco set 1 / Midway set 1: 2 or 3, default 3. Lives capped at 5. The lives display has 5 cells.
- **Bonus life:** awarded **once per game**. Namco set 1 / Midway set 1 thresholds: 7000 (default), 10000, 12000, 20000. Other sets default to 4000 or none.
- **Death:** collision with an in-flight alien or an enemy bomb. Formation aliens never reach the ship. Explosion animation is 4 frames x 10 game frames. On death the in-wave aggression value drops by 1 (a small mercy). Game over at 0 lives.

## 2. Enemy formation (the "convoy")

| Row (top to bottom) | Count | Namco name | Common names and colour | Formation pts | In-flight pts |
|---|---|---|---|---|---|
| 1 | 2 (4 slots; up to 2 escaped flagships carry over) | Boss Alien | Flagship, Galboss, Commander. Yellow body with red and blue | 60 | 150 to 800 |
| 2 | 6 | Red Alien | Escorts. Red | 50 | 100 |
| 3 | 8 | Violet Alien | Purple / magenta | 40 | 80 |
| 4 to 6 | 3 x 10 = 30 | Green Alien | Called "blue" by many; the sprite is cyan / blue-green | 30 | 60 (see scoring note) |

- **Total 46 aliens per wave.**
- **Geometry:** rows 12 px apart vertically. Flagship row about 40 px from the top, bottom row about 100 px. Ship at about 220 to 230. Columns 16 px apart on a 10-column grid. Flagships occupy columns 4 and 7 of 10; spare flagship slots are 5 and 6.
- **Formation movement:** side to side only. **It never descends.** Speed 1 px every 4 frames (about 15 px/s). It reverses when the outermost *occupied* column reaches the screen edge limit. As columns are destroyed the convoy travels further each sweep.
- **Wing-flap animation:** every alien except flagships has animation frames. Each alien changes frame every **16 frames (about 0.26 s)**, phase-shifted by position, which creates the rippling flap across the swarm. Flagships do not animate in formation.
- The background drone speeds up the longer a wave lasts and thins out as the swarm shrinks.

## 3. Diving attacks

**Capacity:** at most **7 aliens in flight**: 1 flagship + 2 escorts in a convoy, plus up to 4 individual divers. The number of usable individual-diver slots is 1 to 4, scaling with difficulty.

**When a single alien launches:** a master counter ticks every 5 frames. Each tick decrements N secondary countdowns, where N grows with difficulty from 1 to 15. Any countdown reaching 0 launches one alien if a slot is free. At minimum difficulty a new diver launches about every 235 frames (3.9 s). At high difficulty launches are near-continuous. No launches during flagship "shock" (below).

**Which alien, from where:**
- Flank: if the convoy is within 28 px of its travel limit on one side, divers break from that side. Otherwise the side is random.
- From that flank, take the first occupied column. While any flagship remains in formation, only **purple or green** aliens dive singly (scan purple row, then the three green rows downward). Once no flagships remain, reds also dive singly.
- The arc direction follows the flank.

**Flagship convoys:** timed separately on a 1-second tick. Interval is about 6 to 9 s early, shorter with difficulty, and **2 s** once no green or purple aliens remain. On launch the flagship takes **up to 2 red escorts from the three red positions directly beneath it** (below-left, below, below-right). Escorts copy the flagship's path so they fly in tight formation. A flagship whose underlying reds are dead dives alone. If no flagship is found on the chosen flank, a single red is sent instead.

**Flight path stages:**
1. Leaves formation: tile removed, sprite created at the slot position, attack sound starts.
2. **90-degree arc** up and toward the flank side.
3. Picks a lateral target: the player's horizontal position relative to the alien at that instant, **clamped to 48..112 px**. A pivot value plus an oscillating delta produces the characteristic **S-curve / zig-zag** descent.
4. Descends at **1 px per frame**, dropping bombs when allowed, facing the player.
5. Within about 72 px of the ship's plane it speeds up to **1.5 px per frame**.
6. At the bottom, divers **do not die. They wrap to the top.** Then:
   - Normal case: returns to its own formation slot from the top, flips when within 25 px, and becomes a formation tile again.
   - If 3 or fewer aliens remain in the swarm, **or** only reds and flagships remain: the alien re-enters at a random position, charges at full speed without shooting, performs a **loop-the-loop** at the vertical centre if there is room, then resumes shooting. These aliens never return to the swarm until they or the player die.
   - Off the side of the screen is treated like reaching the bottom.
7. Flagship at the bottom: **with an escort it returns to the top and keeps fighting; with no escort it flees the level** and is counted as a survivor (max 2). Survivors re-enter the two spare top-row slots next wave, so **up to 4 flagships** can start a wave.

**Enemy speed:** descent is a fixed 1 px per frame (1.5 near the bottom). The wave-to-wave ramp is in **frequency and count** of attackers, not raw speed.

**Flagship kill "shock":** shooting a flagship *in flight* starts a **240-frame (about 4 s)** period during which no alien leaves the swarm and in-flight aliens stop firing. Killing a flagship in formation gives no shock.

## 4. Enemy bombs

- About **7 enemy shots visible at once** maximum (hardware). Published claims of "2 or 3" are unverified.
- Only in-flight aliens fire. The formation never fires.
- Vertical speed **2 px per frame** (about 121 px/s). Horizontal drift up to about 1 px per frame, **aimed toward the player's position at the moment of firing, with random spread**. Straight flight after launch, no homing. Removed at the bottom or off the side.
- Firing opportunities: a diver tries to fire at fixed vertical checkpoints 25 px apart during its descent. The number of checkpoints starts at **2** and rises by 1 for each emptied pair of rows from the bottom (max 5). **The fewer aliens in the swarm, the more bombs each diver drops.** No firing during shock, the from-the-top continuation run, or the full-speed charge.

## 5. Scoring

| Target | In formation ("CONVOY") | In flight ("CHARGER") |
|---|---|---|
| Green/blue alien | 30 | 60 |
| Purple alien | 40 | 80 |
| Red alien | 50 | 100 |
| Flagship alone | 60 | 150 |
| Flagship with 1 escort | n/a | 200 |
| Flagship with 2 escorts, at least one escort alive | n/a | 300 |
| Flagship with 2 escorts, **both escorts killed first** | n/a | **800** |

- Discrepancy: the ROM score table as transcribed would pay **70** for a diving green alien, while the attract-mode table and every published source say 60. Unresolved. Use 60 (the published value).
- The flagship's point value is shown at the kill location for 50 frames (about 0.8 s).
- Score is 6 digits, max **999,990**, then rolls over.
- No bonus for clearing a wave. No points for escaped flagships.
- Default high score appears to start at 0. No name entry.

## 6. Wave progression and difficulty

Two values drive difficulty:
- **Base difficulty:** +1 at each wave clear, **capped at 7** (maxes from wave 8 on).
- **In-wave aggression:** +1 every **1200 frames (about 20 s)** in the current wave, capped at 7. Reset to 0 at wave start. -1 on each player death. Frozen during flagship shock.

Their sum drives: simultaneous individual divers (1 to 4), how many launch countdowns run in parallel (1 to 15), and convoy interval (about 9 s down to 6 s, minus carried-over flagships; 2 s in the end phase). Bomb frequency scales with rows cleared, not wave.

- **End phase:** attackers never return to the swarm once 3 or fewer aliens remain in formation, or once all green and purple are gone.
- **Wave clear:** when the grid is empty and no in-flight or dying aliens remain (fled flagships count as gone). About **256 frames (4.2 s)** of pause, then the same 46-alien formation (plus up to 2 survivor flagships) is rebuilt, scroll reset, drone tempo reset, aggression reset, base +1, flags redrawn.
- **Wave indicator:** red flags bottom right. One small flag per wave, a wider "10" flag per ten waves. Display capped at 48.
- **No kill screen.** The game loops indefinitely with difficulty plateaued.

## 7. Game flow and attract mode

Attract sequence: "GAME OVER" + "CREDIT n" with starfield, then **"WE ARE THE GALAXIANS" / "MISSION: DESTROY ALIENS"**, then **"- SCORE ADVANCE TABLE -"** with headings **"CONVOY CHARGER"** and each alien row scrolled in from the side (flagship "60 ... 150", with the charger value cycling 150, 200, 300, 800 and blinking; red "50 100 PTS"; purple "40 80 PTS"; green "30 60 PTS"), then the NAMCO logo, then a demo game until the demo ship dies, then loop. With credit inserted: "PUSH START BUTTON" and **"BONUS GALAXIP FOR 7000 PTS"**.

ROM strings: GAME OVER, PUSH START BUTTON, PLAYER ONE, PLAYER TWO, HIGH SCORE, CREDIT, BONUS GALAXIP FOR 000 PTS, CONVOY CHARGER, - SCORE ADVANCE TABLE -, MISSION: DESTROY ALIENS, WE ARE THE GALAXIANS, FREE PLAY.

Game: swarm appears, "PLAYER ONE" shown then cleared, ship spawns, start tune, 1UP blinks. On the last life lost, "GAME OVER". HUD layout: 1UP score left, 2UP right, HIGH SCORE centre, flags bottom right, ships remaining bottom left.

## 8. Timing cheat-sheet (60.6 fps)

| Thing | Value |
|---|---|
| Player ship | 1 px/frame |
| Player shot | 4 px/frame, about 50 frames to top, 1 on screen |
| Convoy sweep | 1 px every 4 frames (about 15 px/s), horizontal only |
| Alien flap frame change | every 16 frames per alien |
| Diver descent | 1 px/frame; 1.5 px/frame near the bottom |
| Enemy bomb | 2 px/frame down, up to about 1 px/frame sideways |
| Flagship shock | 240 frames |
| Aggression step | every 1200 frames in-wave |
| Single-diver base interval | about 235 frames at minimum difficulty |
| Convoy interval | 6 to 9 s, 2 s in end phase |
| Between waves | 256 frames |
| Player explosion | 4 x 10 frames |
| Flagship score popup | 50 frames |

## Open questions and disagreements

1. Diving green alien: 60 (published) vs 70 (ROM table transcription).
2. Bottom-row colour name: "blue" vs "green". The sprite is cyan.
3. Max simultaneous attackers: arcade-history says 10 to 15; code caps at 7.
4. Enemy shots on screen: 2 or 3 (shmups.wiki) vs 7 hardware sprites.
5. "Enemies get faster per wave": common claim; code shows frequency scaling, not speed.
6. Bonus-life defaults differ by ROM set.
7. Default high score presumed 0.

## Sources

- Scott Tunstall annotated disassembly: https://seanriddle.com/galaxian.asm and https://archive.org/details/galaxianasm_201904
- MAME driver: https://github.com/mamedev/mame/blob/master/src/mame/galaxian/galaxian.cpp
- arcade-history: https://www.arcade-history.com/?n=galaxian&page=detail&id=901
- Namco official: https://galaga.com/en/history/galaxian.php
- shmups.wiki: https://shmups.wiki/library/Galaxian
- Japanese Wikipedia: https://ja.wikipedia.org/wiki/ギャラクシアン
- English Wikipedia: https://en.wikipedia.org/wiki/Galaxian
- Pixelated Arcade: https://pixelatedarcade.com/games/galaxian
- Galaxian DX author notes: https://arlagames.itch.io/galaxian-dx-c64
- Wireframe recreation article: https://www.raspberrypi.com/news/recreate-galaxians-iconic-attack-patterns-wireframe-50/
