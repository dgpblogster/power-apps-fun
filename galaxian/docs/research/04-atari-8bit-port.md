# Galaxian — Atari 8-bit computer version (Atari, Inc., CXL4024, 1982)

Research notes compiled 2026-10-05 for recreating the Atari 400/800/XL/XE cartridge as it ran on an Atari 800XL. Primary sources inspected: the 8-page Atari manual (C014189-24 Rev. 1), box and cartridge scans, Atari's 1982 catalogue, the Atari 5200 manual, atariprotos.com, and five independent in-game captures (atarimania screenshot and YouTube frames) that were upscaled and measured.

Markers: **[UNVERIFIED]** could not be confirmed. **[INFERRED]** is a reading of screenshots. No public disassembly of this ROM exists.

## 1. Identification

| Item | Value |
|---|---|
| Title | GALAXIAN ("Trademark of Bally Midway Mfg. Co. Licensed by Namco-America, Inc.") |
| Part numbers | CXL4024 (1982, Atari, Inc.); RX8024 re-release (1986, Atari Corp., grey label) |
| Manual | C014189-24 Rev. 1, 1982, 8 pages |
| ROM | 8 KB cartridge **[UNVERIFIED by dump]** |
| Programmer | Joseph (Joe) Tung; graphics Marilyn Churchill (credited on the 5200 version, same code family) |
| Release | 1982 |
| Reception | Split. Softline 1983: "becomes tedious very quickly". Users: "one of the worst arcade conversions... erratic movement of the attacking galaxians" vs "better than the arcade... more responsive controls". |

**Box art:** black top band with "ATARI 400/800 HOME COMPUTER", "COMPUTER CARTRIDGE", "GALAXIAN" in large white serif. Painting of two winged, armoured, golden-helmeted humanoid warriors flying through a fiery orange cloudscape with lightning. Yellow starburst "Play the Arcade Game at Home!" Back: "Blast or Be Blasted!" and the text: "Relentlessly they come! The GALAXIANS: Drones, Emissaries and Hornets lead the way, and protect the Commanders who guide the attack... One or two can play GALAXIAN at 10 different skill levels including an easy version for beginners."

**Title and attract screen:** the game screen itself runs an attract demo with the full formation at the top, aliens diving, and a live HUD (level "0" in blue, score "00" in yellow, 1 red flag). Centred mid-screen: **"GALAXIAN"** in a light-blue/lavender double-width custom font. Bottom text line in grey, normal-width font: **"00 COPYRIGHT 1982 ATARI,INC."** where the leading "00" is the high-score field. Pink player ship at bottom centre. No Fuji logo graphic. When a game or life begins, **"PLAYER ONE"** (lavender, wide font) is shown centred mid-screen.

**Console keys (manual):**
- **START**: begin or restart the game at any time.
- **SELECT**: cycles difficulty. Blue numbers 0 through 9 are increasing difficulty in the standard game; blue letter **B** is a special Beginner's level. Eleven settings in total.
- **OPTION**: toggles two-player (alternating) and one-player.
- **SYSTEM RESET**: back to one player, lowest difficulty. The high score stays on screen until power off.
- **SPACE BAR**: pause and unpause.
- Pressing SELECT or OPTION during a game ends the game (the basis of the infinite-lives quirk below).

## 2. Display

**Hardware mode: [UNVERIFIED].** Measurements from captures (a colour clock is 2 hi-res pixels wide; a 4:3 frame is 160 colour clocks by about 240 scanlines):

- Background **black**.
- Alien sprite about **8 colour clocks wide by 8 scanlines tall**, 3 colours plus black. **[INFERRED]**
- Formation **column pitch about 12 colour clocks**, **row pitch about 10 scanlines**. Ten columns span about 116 to 118 clocks of the 160-wide playfield. **[INFERRED]**
- HUD line at roughly scanlines 15 to 25. Formation top row starts about scanline 28. Player ship around scanlines 205 to 220. Bottom text line about 218 to 230. **[INFERRED]**

**Colours as seen (NTSC emulator captures; hue varies by palette):**

| Object | Colours |
|---|---|
| Commanders (flagships) | yellow/gold body, red-orange lower wings, small blue/purple centre |
| Hornets (red row) | red body, green wing tips, yellow centre |
| Emissaries (purple row) | lavender/purple body, dark-blue tips, gold centre |
| Drones (blue rows) | cyan/teal body, dark blue, dark-red centre |
| Player ship | **hot pink/magenta hull with blue engine pods**, about 8 clocks wide |
| Player missile | short white vertical dash |
| Alien bombs | short white (or yellow) vertical dashes |
| Level digit | blue |
| Score | yellow |
| Ship icons | pink |
| Wave flags | red |
| Bottom text (high score, copyright) | grey/white |

**Starfield:** many single-pixel stars in blue, green/teal, orange/pink and white scattered over the whole play area, including behind the formation. Stars line up in vertical columns of one colour each, consistent with a vertically scrolling columnar starfield. Direction and speed **[UNVERIFIED]**.

**HUD layout (manual, verbatim):** "Across the top of the screen, reading from left to right: the level of difficulty (0 through 9, or B); the current player's score; the number of ships the player has left; the number of the Galaxians' attack wave (shown by small flags). At the bottom left corner of the screen is the highest final score earned since the current round of play began. In a two-player game, the current player is identified just to the right of the high score. The opponent and the opponent's score are shown to the far right."

Captures confirm: top row = blue level digit (far left), yellow score (centre-left), pink ship icons, red flags (far right, one flag per wave; 7 flags seen on wave 7). Bottom-left = high score. A bottom-right number is present even in one-player footage; its meaning is **[UNVERIFIED]**, possibly the score as of the last wave or life start.

**Fonts:** HUD digits are a custom chunky, rounded, bold double-width font. "GALAXIAN" and "PLAYER ONE" use a wide outlined custom font. Bottom text is a normal-width font resembling Atari's default character set. **[INFERRED]**

## 3. Formation (counted in 5 independent captures, consistent)

| Row (top to bottom) | Type | Count | Columns occupied (of 10) |
|---|---|---|---|
| 1 | Commanders (flagships, yellow) | **3** | **4, 6, 7** (asymmetric) |
| 2 | Hornets (red) | 6 | 3 to 8 |
| 3 | Emissaries (purple) | 8 | 2 to 9 |
| 4 | Drones (cyan) | 10 | 1 to 10 |
| 5 | Drones (cyan) | 10 | 1 to 10 |
| **Total** | | **37** | |

The arcade has 2 + 6 + 8 + 30 = 46. This port drops one Drone row and has **three** Commanders in the odd 4, 6, 7 placement, which was identical in every capture. Whether later waves change the layout: **[UNVERIFIED]**.

Movement: the formation is at different horizontal offsets in different captures, so it **moves side to side**. Whether it ever descends: **[UNVERIFIED]** (the manual never mentions it; the arcade does not). Wing-flap animation appears present and possibly unsynchronised between aliens. **[UNVERIFIED]**

## 4. Attacks (manual statements plus captures)

- "Some Galaxians come plunging down at you from the extreme right or left of their formation." Divers peel off from the **edges** of the formation.
- "If you miss them, the Galaxians fly back into formation to give you another chance." Survivors return to their slot. Whether they wrap bottom to top like the arcade or turn around on screen: **[UNVERIFIED]**.
- Convoys: "Shoot Hornets only when they're escorting a Commander, and Commanders only when they're attacking." A capture shows a Commander descending diagonally with two Hornets trailing it plus a separate Drone diving at the same time, so **at least 4 aliens in 2 groups** can be airborne together. Hard cap **[UNVERIFIED]**.
- Bombs: "Never forget the Galaxians' bombs. You can blast an attacker and still be destroyed by the charges he's already released." Bombs are short vertical dashes released in strings during the dive (a diagonal trail of 4 to 5 is visible in one capture). "In some games they fire in patterns, while in others they fire randomly" (varies with skill level).
- Mourning: "When a Commander is destroyed while attacking, the Galaxians cease firing for a few seconds."
- Safe zones: "If you need a breather while fighting off the early waves, go to the extreme right or left of the screen." Divers do not reach the screen edges in early waves.
- Beginner (B) level: "you can destroy the first 16 waves of Galaxians without their firing back at you. The only way you can lose a ship during this time is by colliding with a Galaxian."
- Reviewers describe the dive paths as "erratic", not the arcade's smooth loops.

## 5. Player

- Joystick left and right only. Red button fires. Movement speed **[UNVERIFIED]**; described as "more responsive" than the arcade.
- **One missile at a time.** "Between shots, your next missile sits on the nose of your ship. You can destroy an onrushing attacker just by touching him with it." The idle missile on the nose is a hitbox that kills divers by contact. Manual also says "Fire as often as possible."
- Lives: start with **3**. "You'll get a second ship; hit again, you'll get a third. But that's your final chance until you score 5000 points."
- Extra ship: **one bonus at 5,000 points** ("you'll earn a fourth Earthship"). Further bonuses **[UNVERIFIED, probably none]**.
- A wave-1 frame shows 3 ship icons with a ship in play, so the icons may include the current ship. **[UNVERIFIED]**
- On death: "PLAYER ONE" message is shown before the next ship.

## 6. Scoring (manual, verbatim values)

| Alien | In formation | In flight |
|---|---|---|
| Drones (cyan) | 30 | 60 |
| Emissaries (purple) | 40 | 80 |
| Hornets (red) | 50 | 100 |
| Commanders (yellow) | 60 | 150 (no escorts), 200 (one escort), 300 (two escorts), **800** ("Blast both Escorts, then the Commander") |

This matches the arcade exactly.

## 7. Waves, levels, Easter eggs

- Each cleared wave adds one red flag at top right (7 flags observed on wave 7). Whether flags consolidate at 10 or cap: **[UNVERIFIED]**.
- Progression: "each faster and more powerful than the last". At levels 0 to 9 "they fire more and more missiles, faster and faster, as the level of difficulty increases."
- **Easter eggs** (atariprotos, confirmed for 8-bit and 5200): "After wave 10, every now and then you'll see a small symbol when you destroy a Galaxian. On wave 10 the symbol is a Pac-Man, on wave 12 the symbol is the Atari logo, and on wave 14 the symbol is the initials JT (for programmer Joe Tung)." The 8-bit manual only hints: "Get past the tenth wave and you've more than earned your wings. You may also see a few surprises." Exact appearance and behaviour beyond wave 14: **[UNVERIFIED]**.

## 8. Sound (descriptions only, no recordings analysed)

- Background: "a constant low pitched rumble which sounds like interference". The arcade's pulsing drone is absent.
- Dive: pitch rapidly changes as the Galaxians descend. Described as irritating.
- "Stationary aliens produce long high pitched tones."
- Consensus: the sounds were cut down to fit the 8 KB cartridge and "don't really fit the game".
- Shot, explosion, and start jingle details: **[UNVERIFIED]**. The arcade's start tune is reportedly not reproduced.

## 9. Known quirks

- **SELECT infinite-lives trick:** start a game, press SELECT. GAME OVER appears but you can keep playing with infinite lives. "You can also use the GAME OVER text as a makeshift shield... After a few waves of this your ship will turn invisible and the Galaxians will start appearing randomly."
- Two-player: alternating turns via OPTION, joystick jacks 1 and 2; opponent's score bottom right.
- Pause: SPACE BAR (manual warns about screen burn after 15 minutes).
- Level 9 reported "incredibly difficult". B level has no enemy fire for 16 waves.
- 5200 differences: analogue stick with two speeds, optional Trak-Ball, PAUSE button, occasional slowdown, minor collision issues.

## 10. Links

**Scans and databases**
- atarimania 8-bit page (manual, scans, screenshot): https://www.atarimania.com/game-atari-400-800-xl-xe-galaxian_2141.html
- Screenshot: https://www.atarimania.com/8bit/screens/Galaxian.gif
- Manual pages: https://www.atarimania.com/8bit/boxes/hi_res/Galaxian_i.jpg through Galaxian_i_8.jpg
- Box front and back: https://www.atarimania.com/8bit/boxes/hi_res/Galaxian_cart_2.jpg and Galaxian_cart_6.jpg
- atarimania 5200 page: https://www.atarimania.com/game-atari-5200-galaxian_13599.html
- atariprotos 5200 page (Easter eggs, SELECT trick, sound): https://www.atariprotos.com/5200/software/galaxian/galaxian.htm
- 5200 manual OCR: https://archive.org/stream/Atari5200Manuals_201812/Galaxian%20%28USA%29_djvu.txt

**Video**
- Longplay (Atari 8-bit), RetroGamingLoft: https://www.youtube.com/watch?v=RtMOiaovAWg
- Atari 800XL flashback, Screen Shooters: https://www.youtube.com/watch?v=4Uc37tILu-w
- Highretrogamelord: https://www.youtube.com/watch?v=C9u2_Kl58DI
- Long play, ATARI 8 BITS FOR EVER: https://www.youtube.com/watch?v=Otsq6xzC6fI
- Robert's Retro-Gaming: https://www.youtube.com/watch?v=7BqoVypgdV8

**Forum threads (blocked by captcha during research; worth reading manually)**
- https://forums.atariage.com/topic/313907-ataris-galaxian/
- https://forums.atariage.com/topic/243376-atari-8-bit-to-5200-which-port-is-better/

**Disassemblies and recreations:** none found for this port. For ground truth, load the ROM in the Altirra emulator and inspect the display list and player/missile registers.

## Biggest open questions

1. Rendering mode and exact pixel sizes.
2. Dive path shapes, return behaviour (wrap vs. turn), max simultaneous attackers, bomb timing per skill level.
3. Whether the formation ever descends; wing-flap timing.
4. Easter-egg graphics and behaviour beyond wave 14; flag display past 10 waves; maximum level.
5. Meaning of the bottom-right number in one-player games; whether ship icons include the active ship.
6. Sound synthesis details for the rumble, dive sweep, shot, and explosion.
