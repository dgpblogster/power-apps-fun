# Frogger: history, design intent, and legacy

Research note for the canvas Power Apps homage. Date: 2026-10-28.
Scope: the purpose and story of the game, not its mechanics (see the gameplay and platform notes).
Claims that rest on a single fan source or that the sources contradict are marked **(unverified)**.

## 1. Origin (Konami, 1981)

- Frogger was developed by Konami in Japan and released in arcades in August 1981 (Japan), September 1981
  (North America, via Sega/Gremlin) and October 1981 (Europe, via Sega) [W1].
- **Japanese title.** フロッガー (*Furoggā*), simply the katakana rendering of "Frogger"; it carries no other
  meaning [W1][KLOV]. Konami's working title was reportedly "Highway Crossing Frog"; Sega wanted something
  unique and renamed it Frogger [W1][FW]. The literal working title is the best clue to the concept: a frog,
  a highway, a crossing.
- **Who designed it.** Konami, like most arcade companies of the period, did not credit staff (it "claimed sole
  responsibility for all its games" to stop head-hunting) [TE]. The widely repeated story that a Konami employee
  named **Akira Hashimoto** got the idea watching a frog try to cross a road at a traffic light is **(unverified)**
  and probably apocryphal: former Konami programmer Masahiro Inoue, who did a sound effect for Frogger, "didn't
  know anyone by that name" [TE]. Inoue credits **Takahide Harima** (播真隆秀, also romanised Hoso) and one or two
  other programmers. A staff list shared in December 2025 by former Konami sound designer Yuji Takenouchi gives:
  leader/director **Takeshi Hara**; programmers Hara, Harima/Hoso and **Keiichi Miyoshi** (part-time); graphics
  unknown; sound Harima/Hoso, Hirokazu Fujinaka, Shigeru Fukutake and Masahiro Inoue [TE]. Wikipedia's infobox
  (director Hara, designer Harima, programmers Miyoshi, Harima, Hara) agrees with that list [W1]. So the honest
  answer is: designer Takahide Harima, director Takeshi Hara, with the "Hashimoto at the traffic light" anecdote
  unsupported.
- **Earlier games it drew on.** Frogger is a pure "avoidance" game in the lineage of Konami's own scrolling and
  maze games on the same board family (Scramble, Amidar), and the idea of a frog crossing traffic had a direct
  precedent at Gremlin: *Frogs* (1978), a Gremlin arcade game about a frog catching insects, had flopped, which is
  exactly why Gremlin management hesitated [W1][R365]. No source names a specific game as the design model
  **(unverified)**.
- **Why Sega/Gremlin got the North American rights.** On 22 July 1981 Sega obtained exclusive worldwide
  manufacturing rights [W1]. Gremlin (Sega's San Diego subsidiary) was sceptical: nobody else had licensed the
  game, *Frogs* had failed, and the company expected *Eliminator* to be its next hit. Executives called it a
  "women and kids game". A Gremlin forecast analyst, **Elizabeth Falconer**, found the game in the company's
  library, argued from Pac-Man's success that a non-violent game could be a hit, and got a playtest: Sega/Gremlin
  paid Konami $3,500 per day for a 60-day licensing window, put a prototype in Spanky's Saloon in San Diego, and
  the earnings were strong enough that distributors agreed to carry it on that test alone [W1][R365]. One
  popular account that Gremlin first rejected it as "too cute for boys" is a single-source version of the same
  story **(unverified)** [Med].

## 2. Design intent: what the game was trying to do

- **A non-violent avoidance game.** The player never shoots; every hazard is something to avoid or ride. Gremlin's
  own executives framed it as a "women and kids game", and Falconer's pitch was that this was an asset, not a
  flaw, after Pac-Man [W1]. The 1982 Softline review summarised the result from the other side: "the arcade game
  with the most ways to die" [W1].
- **Two opposite hazard rules in one screen.** The road kills on contact (anything that touches you is lethal,
  the ground is safe); the river kills on absence (the water is lethal, you survive only while standing on
  something, and that something moves you). The player must flip mental models at the median. This is the core
  of why Frogger stays interesting with only four inputs: the same hop means "dodge" below the median and
  "board" above it.
- **Layered timing.** Twelve lanes (five traffic, a median, five river lanes, plus the bank and the homes in most
  counts) each scroll at their own speed and direction [C83]; turtles dive, logs are different lengths,
  crocodiles have a lethal head, otters and snakes patrol the river, and the home bays can hold a fly (bonus) or
  a crocodile (death) [W1]. Difficulty comes from pattern reading, not reflexes alone.
- **The timer and the five homes.** Each frog has a countdown (30 seconds on the arcade, shown as a shrinking bar;
  the original counter is 60 ticks of half a second) and the round ends only when all five homes are filled
  [W1]. The timer forces commitment; the five homes make the last frog the hardest because the remaining bay is
  usually on the wrong side of the river traffic. Unused time pays 10 points per half-second, which makes speed
  a scoring choice, not just a survival one [W1].
- **Bonuses that tempt detours.** Escorting the lady frog (200) and eating a fly in a bay (200) both reward
  leaving the safe line [W1]. Finishing a round is worth 1,000; a bonus frog comes at 20,000 [W1].
- **Difficulty curve.** Each new round is faster and busier; Wikipedia records that difficulty "briefly eases
  after level five, then rises again" [W1]. Computer Archeology's disassembly notes there are 26 song fragments
  and hearing them all requires beating the first five levels and dying, which suggests the designers thought in
  five-level cycles [CA]. The score counter has only five digits and rolls over at 99,990, so the designers never
  expected marathon play [W1][Kot].
- **Music as part of the design.** The arcade opens with the first verse of the Japanese children's song "Inu no
  Omawarisan" (The Dog Policeman); the main in-game tune is the theme from the anime *Araiguma Rascal*, and other
  fragments are reported to be from *Hana no Ko Lunlun* and *Heidi* [W1][CA][TVT]. The US ROM also plays
  "Yankee Doodle" [A80]. The Japanese songs were used without clearance, which is the usual explanation for why
  most home ports replaced the music **(unverified)** [AA2][TVT].

## 3. Hardware

- **Board.** Konami's Scramble-family Z80 hardware ("Konami Z80 based" at PixelatedArcade). Main CPU Zilog Z80
  at 3.072 MHz; sound CPU Z80 at 1.78975 MHz driving **one** General Instrument AY-3-8910A at 1.789772 MHz,
  mono output [PA][KLOV]. (Scramble itself has two AY-3-8910As; the brief's "2x AY-3-8910" applies to that
  sibling board, not Frogger [FPGA].) The FPGA Arcade notes list two 8255 PPIs on the Scramble/Frogger design
  and document the Frogger-specific address-pin and input-bit swaps [FPGA]. The sound ROM corrects a hardware
  mistake where data lines D0 and D1 are swapped on the sound chip; the sound code ticks at 700 Hz with one
  thread per voice and 24 sound effects; the main board signals the sound board through port A of the AY [CA].
- **Display.** Standard-resolution colour raster, vertical (portrait) orientation, 60.6 Hz [PA][KLOV].
- **Cabinets.** KLOV lists upright, cocktail, and a Sega "Slimline" table/island; Froggers are "typically only
  found in the Sega/Gremlin laminated wood-grain convert-a-cabinets" [KLOV]. A cabaret (mini) cabinet is often
  mentioned but KLOV does not list one **(unverified)**.
- **Controls.** A single ambidextrous panel with one 4-way joystick and **no buttons**; one- and two-player start
  buttons, alternating play [KLOV][PA].
- **DIP options.** Starting frogs 3, 5, 7 or 256; coinage; upright/cocktail [KLOV]. The 256-frog setting is
  the operator's "free play for testing" mode.
- **Score display.** Five digits; wraps at 99,990 [W1].

## 4. Commercial impact

- **Arcade.** About $135 million in US cabinet sales (roughly $478 million in 2025 dollars), Sega/Gremlin's most
  successful release, one of North America's top-grossing arcade games of 1981 and the 12th highest-grossing in
  Japan that year [W1]. It stayed a top earner into 1982; the home-port wave made 1982 the "Frogger year" even
  though the arcade peak was 1981.
- **The licensing split.** Sega's licence let it sub-license home rights. **Parker Brothers** bought the ROM
  cartridge rights and backed them with a $10 million advertising budget shared with its Star Wars titles, larger
  than a typical film's marketing budget at the time [W1][A80]. Its 1982 Atari 2600 Frogger took $40 million in
  orders at launch and sold about 4 million cartridges by year end (about $80 million wholesale); one source says
  3 million [W1][A80]. **Sierra On-Line** (then On-Line Systems) noticed that Parker's deal covered only
  cartridges, and Ken Williams bought the floppy and cassette ("magnetic media") rights from Sega for a reported
  10 percent royalty [R365]. Sierra sold them under the SierraVision label as *The Official Frogger* and
  sub-licensed systems it did not cover (Cornsoft for TRS-80, Dragon 32 and Timex Sinclair) [W1][SR].
- **The most-ported game of its era.** Parker Brothers cartridges: Atari 2600, Intellivision, Atari 5200,
  ColecoVision, Odyssey², Atari 8-bit, TI-99/4A, VIC-20, Commodore 64 (1982-1983) [W1]. Sierra magnetic media:
  Atari 8-bit, Apple II, IBM PC, Commodore 64, Macintosh, TRS-80 and Color Computer, plus an Atari 2600
  Supercharger cassette through Starpath [W1][R365]. Later: Gakken TV Boy (Japan 1983 launch title), Coleco
  tabletop Mini-Arcade (about 3 million units across four titles), Game Boy and Game Boy Color (1998), Genesis
  and SNES (1998, Majesco; the Genesis one was the last licensed Genesis game in North America), Game.com (1999)
  [W1][W2]. By 2005 some 20 million home copies had sold worldwide, 5 million in the US [W1]. Vectrex is often
  listed among the ports but no official Vectrex Frogger shipped **(unverified)**.
- **Awards.** The 1983 Arcade Awards (Electronic Games) gave Frogger "Best Arcade-to-Home Computer Game
  Translation" for an Atari 8-bit version; the listing does not say whether it was Sierra's or Parker's
  **(unverified which)** [EG].
- **"Frogger: Official" versions.** The "Official" branding is Sierra's (*The Official Frogger*, SierraVision,
  "under license from Sega"), used to distinguish licensed disks from the clone wave (Ribbit, Hopper, Preppie!,
  Pacific Coast Highway, Frostbite) [W1][C83][AM1].

## 5. The Atari 8-bit situation: Sierra (1982) versus Parker Brothers (1983)

Three licensed Frogger builds exist for the Atari 400/800/XL/XE, and they share one ancestor.

### 5.1 Sierra On-Line / SierraVision, John Harris, 1982 (disk and cassette)

- Written in 6502 assembly by John Harris on an Atari 800 (48K plus an Axlon 128K board, a fast floppy interface
  and an 80-column board) [HD]. Credited for programming, graphics and sound; Levy says a friend of Harris wrote
  the POKEY music [AM1][AM2]. Released 1982; Compute! reviewed it in March 1983 at $34.95, disk (32K) or cassette
  [C83]. Atarimania rarity: disk 7, tape 5 [AM1].
- **The Hackers story.** Steven Levy's *Hackers* (1984) devotes chapter 18, "Frogger", to it. Harris, Sierra's
  star Atari programmer (Jawbreaker, Mouskattack), earning six figures in royalties at 24, took Frogger as his
  next project. At a software trade show in 1982 where he was presenting, the disks holding his whole development
  environment, tools, libraries and the Frogger work in progress were stolen; Wikipedia says "a game developer
  conference", retro365 says "a San Diego software expo" **(city unverified)** [WJH][R365]. He was unable to
  program for about two months, Ken Williams lost patience, and Harris finally rewrote the game from scratch,
  a second time, and it became a big success for On-Line [WJH][Levy-S]. Reported first-month royalties were about
  $40,000, and a forum poster citing Levy puts his total at around $300,000 **(unverified)** [R365][AM1]. A
  dispute over a two-player version and withheld royalties followed, and Harris left for Synapse [R365][WJH].
  Harris's own verdict on the book: "most of the material relating to programming is actually fairly close",
  with "some mild inaccuracies and exaggerations" [HD].
- **What it looks and sounds like.** One player only (Compute!: "The Atari version allows only one player").
  Timer is an **orange bar** at the bottom with 120 counts, about 32 seconds, twice the arcade allowance, paying
  5 points per remaining count. OPTION toggles FAST/SLOW, SELECT toggles music, START starts. **Music plays
  throughout the game** on the disk version (Compute!: "some of the best I've heard on any game so far"); the
  cassette version has **no music, no otters and no high-score saving** [C83][AC]. Starts with five frogs
  [AA2]. Four traffic lanes, a rest bank, five river lanes, five arched homes in a wall at the top [C83].

### 5.2 Sierra On-Line, Chuck Benton, 1983 (disk and cassette)

- A second Sierra build by Chuck Benton (who also did Sierra's C64 Frogger) adding a **two-player simultaneous
  head-to-head** mode and other upgrades, apparently Sierra's answer to the two-player question in the Harris
  royalty dispute [R365][AM2]. Very rare (rarity 8), the "almost lost release" that researcher FastRobPlus
  documented decades later; Atarimania could not establish whether it shipped before, with or after Harris's
  [AM2]. Sound and music are "nearly identical" to Harris's [AM2]. An 800XL owner is unlikely to have met it.

### 5.3 Parker Brothers, 1983 (8K cartridge)

- After the 2600 cartridge's success Parker wanted Frogger on every cartridge platform fast. It licensed Sierra's
  Atari code (retro365 reports $200,000) but Sierra had no source: Harris had kept a single copy and lost it
  [SK][R365]. Steve Kranish at Parker was handed the **cassette image** (a 13K RAM dump of code, graphics and
  "debris"), disassembled it with a three-path 6502 disassembler into a two-inch listing, commented and
  reorganised it, and in about six weeks produced an 8K cartridge [SK]. Atarimania credits Roklan as developer
  with Kranish and Dawn Stockbridge; Kranish describes doing the work at Parker, so the Roklan credit is
  **(unverified)** [AM3][SK].
- Parker's requirements: fit in 8K, ship in six weeks, **add a two-player (alternating) mode, and change the
  graphics**. Dawn Stockbridge redrew the graphics; the **median/sidewalk pattern changes every level** because
  there was room for it [SK]. Because of the 8K limit, **music plays only at the start of a level, not during
  play** [AC][AA2]. Starts with four frogs [AA2]. The Atari 5200 cartridge is the same code and graphics [AM3].
  A removed easter egg turned the frog into Kranish's initials on jumping the lady frog on level 6 or 7; the
  shipped ROM still carries the string "@1983 PARKERBROS B KRANISH" [SK][AC]. The cartridge shell fits an 800 but
  not a 400 [SK].

### 5.4 Telling them apart (questions to ask the user)

| Tell | Sierra / John Harris (1982) | Parker Brothers (1983) |
|---|---|---|
| Media | Floppy disk or cassette, loaded from DOS/boot | Cartridge in the slot, instant start |
| Music | Continuous tune during play (disk); none at all on tape | Short jingle at the start of each level, then silence |
| Players | One player only | Two-player alternating option |
| Starting frogs | Five | Four |
| Median strip | Same every level | Pattern changes each level |
| Otters | Yes on disk, absent on tape | Present (shared code) **(unverified)** |
| Timer | Orange bar, long (about 32 s, "twice the arcade") | Shorter **(unverified)** |
| Speed option | OPTION toggles FAST/SLOW | FAST/SLOW also present [AA1] |
| Branding | SierraVision / "The Official Frogger", under licence from Sega | Parker Brothers, 1983 copyright |

The one-question version: **"Did music play the whole time you were hopping, or only a little jingle at the start
of each level?"** Whole time means Sierra disk; jingle only means Parker Brothers cartridge; no music means the
Sierra cassette. Follow-up: "Was it a cartridge or did you load it from disk?"

- **Which one an 800XL owner most likely played.** The 800XL shipped in 1983, the same year as the Parker
  cartridge, which was pushed through toy and department stores on Parker's advertising budget and needs no disk
  drive, so a child with an 800XL and a joystick most plausibly played **Parker Brothers**. The Sierra disk was a
  computer-store product from the year before, but it was also the one that circulated on copied disks in user
  groups, so a user who had a 1050 drive and a pirate library would remember **Sierra's music** **(unverified)**.
  Ask; do not assume.

## 6. Legacy

- **Seinfeld, "The Frogger"** (season 9, episode 18, 1998): George finds his 1980s high score of 860,630 still on
  the machine at Mario's Pizza and tries to wheel the cabinet across a street without unplugging it. The cabinet
  on screen has custom side art, not the real Frogger art [W3][KLOV].
- **World records.** Twin Galaxies offered $1,000 in 2005 to the first player to beat George's fictional score;
  nobody did by the deadline. A rivalry between **Donald Hayes** and **Pat Laffaye** ran from 2005 (Hayes held the
  record in 2008). Laffaye scored 896,980 on 22 December 2009, announced at midnight on New Year's, the first to
  pass Costanza. **Michael Smith** scored 970,440 on 15 July 2012. Laffaye reportedly passed one million
  (1,029,990) in 2017 (sources give 15 August or 21 September) but never submitted it to Twin Galaxies. Smith
  scored 1,356,520 on 27 February 2022 (accepted 1 March) on one credit over seven hours, the first verified
  million-plus; Wikipedia lists a further Smith record of 1,404,570 on 21 September 2024 **(single weak source)**
  [W3][W1][NBC][Kot][GZ].
- **Rule disputes.** Because the display rolls over at 99,990, records depend on video adjudication of how many
  times the counter wrapped (Smith's 2022 run wrapped 12 times) and on submission to Twin Galaxies' adjudication
  process, which is why Laffaye's 2017 score is "reported" rather than recognised [Kot]. Record play also depends
  on the operator lives setting (3/5/7), which the DIP table makes explicit [KLOV].
- **Sequels and remakes.** Frogger II: ThreeeDeep! (Parker Brothers, 1984); Frogger (Hasbro Interactive, 1997,
  PlayStation/Windows); Frogger 2: Swampy's Revenge (2000); The Great Quest (2001); Frogger Beyond (2002);
  Frogger's Adventures: The Rescue (2003); Ancient Shadow (2005); Frogger 2 (Xbox 360, 2008); Frogger Returns
  (2009); Frogger 3D (3DS, 2011); Frogger in Toy Town (2019) and Frogger and the Rumbling Ruins (2022) on Apple
  Arcade by Q-Games; a Peacock game show (September 2021) [W2]. Sega's own 1991 arcade *Ribbit* was blocked by
  Konami's lawsuit; one board survives [W2].
- **Crossy Road lineage.** Crossy Road (Hipster Whale, 2014) turned Frogger's fixed screen into an endless,
  randomly generated road-and-river with one life, and was openly pitched as "endless Frogger" [W1].
- **Other references.** CBS cartoon *Saturday Supercade* (1983); Bad Religion's 1985 song "Frogger"; cameos in
  Wreck-It Ralph, Pixels and Ralph Breaks the Internet; a *Drosophila* transposon named Frogger; Melbourne's 2008
  "Grogger" anti-drink-walking campaign; finalist for the World Video Game Hall of Fame in 2025 [W1].

## 7. Rights today

- Konami created the game and owns the franchise. Sega's 1981 licence covered manufacturing and the 1982-1984
  home sub-licences; Konami took the name back in the West in the mid-1990s and licensed it to Hasbro Interactive
  (1997 Frogger), which sub-licensed console ports to Majesco [W2][SR-T]. Konami has published the series itself
  since 2001 [W2].
- **Trademark.** FROGGER, US Reg. No. 6,870,309 (Serial 97022040), filed 10 September 2021, registered
  11 October 2022, standard character mark in classes 9 (software), 28 (toys) and 41 (entertainment), owner
  Konami; listed as live by aggregators (not checked on TSDR directly). Older US registrations (2002, 2015)
  lapsed. A 2024 Australian registration is also Konami's [TM].
- The legal status of the 1980s Parker and Sierra ports "today is unknown" [SR]. The ROMs are not abandonware in
  any legal sense.
- **What a homage must avoid.** The word FROGGER as a title or in marketing; the Frogger logo and its lettering;
  the arcade or home sprites and screen layout copied pixel for pixel; the arcade music (which is itself
  unlicensed Japanese children's and anime songs, so doubly off-limits); cabinet art; the Konami and Sega marks;
  character names from the sequels. Game mechanics (hop, lanes, logs, timer, homes) are not protected.
- This project uses original art, sound and text, a different title, and states on screen that it is not
  affiliated with or endorsed by Konami.

## 8. What this means for our homage

- Keep the two-rule structure sacred: contact kills on the road, absence kills on the river. Everything else is
  tuning.
- Keep five homes and a visible, shrinking time bar; the last home is the designed climax of every round.
- Put the lady frog and the fly in from the first playable build; they are what make the safe line tempting to
  leave.
- Plan difficulty in five-round cycles with a breather after round five, matching the original curve.
- Write original music (and sound) that cycles through a few short fragments; do not quote the arcade tunes or
  Yankee Doodle arrangements from the ROM.
- Decide Sierra-vs-Parker with the user using the music question above before fixing the look: continuous music,
  five frogs and an orange time bar say Sierra; level-start jingle, four frogs and a per-level median pattern say
  Parker.
- Four-way input with no fire button maps cleanly to four tap zones; the arcade panel had nothing else.
- Keep the five-digit score display as a period touch but store the real score so it does not wrap.
- Use a title that is not FROGGER, no frog-logo lettering, and the "not affiliated with Konami" line in the app.
- Credit the real people in the README: Takahide Harima, Takeshi Hara, Keiichi Miyoshi (Konami), Elizabeth
  Falconer (Gremlin), John Harris and Chuck Benton (Sierra), Steve Kranish and Dawn Stockbridge (Parker).

## Sources

- [W1] Wikipedia, "Frogger": https://en.wikipedia.org/wiki/Frogger
- [W2] Wikipedia, "Frogger (series)": https://en.wikipedia.org/wiki/Frogger_(series)
- [W3] Wikipedia, "The Frogger" (Seinfeld): https://en.wikipedia.org/wiki/The_Frogger
- [WJH] Wikipedia, "John Harris (software developer)": https://en.wikipedia.org/wiki/John_Harris_(software_developer)
- [TE] Time Extension, "Who created the arcade classic Frogger?" (2023, updated Dec 2025):
  https://timeextension.com/features/flashback-who-created-the-arcade-classic-frogger
- [KLOV] Museum of the Game / KLOV, Frogger: https://arcade-museum.com/Videogame/frogger
- [PA] PixelatedArcade, Frogger tech specs: https://pixelatedarcade.com/games/frogger/techspecs
- [FPGA] FPGA Arcade, Scramble/Frogger notes: https://www.fpgaarcade.com/?p=65320 and https://fpgaarcade.com/?p=1104
- [CA] Computer Archeology, Frogger arcade disassembly: https://www.computerarcheology.com/Arcade/Frogger/
- [SR] Sega Retro, Frogger: https://segaretro.org/Frogger (fetch blocked; cited via search excerpts)
- [SR-T] Sega Retro talk page: https://segaretro.org/Talk:Frogger
- [R365] retro365, "Frogger, finally an officially licensed game" (2023):
  https://retro365.blog/2023/02/01/bits-from-my-personal-collection-frogger-finally-an-officially-licensed-game/
- [C83] Larry Isaacs, "Frogger for Atari", COMPUTE! issue 34, March 1983:
  https://atarimagazines.com/compute/issue34/041_1_FROGGER_FOR_ATARI.php
- [HD] James Hague, Halcyon Days: John Harris interview (1997): https://dadgum.com/halcyon/BOOK/HARRIS.HTM
- [Levy-S] Steven Levy, Hackers (1984), ch. 18 "Frogger", via O'Reilly chapter page and ANTIC 1985 excerpt:
  https://www.oreilly.com/library/view/hackers/9781449390259/ch18.html and https://atarimagazines.com/v4n5/hackers.php
- [SK] Atari Compendium, Steve Kranish interview:
  https://ataricompendium.com/archives/interviews/steve_kranish/interview_steve_kranish.html
- [AC] Atari Compendium, Atari 8-bit Frogger easter eggs and version notes:
  https://www.ataricompendium.com/game_library/easter_eggs/a48/a48frogger.html
- [AM1] Atarimania, Frogger (Sierra, John Harris): https://www.atarimania.com/game-atari-400-800-xl-xe-frogger_6780.html
- [AM2] Atarimania, Frogger (Sierra, Chuck Benton): https://www.atarimania.com/game-atari-400-800-xl-xe-frogger_12181.html
- [AM3] Atarimania, Frogger (Parker Brothers): https://www.atarimania.com/game-atari-400-800-xl-xe-frogger_6767.html
- [AA1] AtariAge, 8-bit High Score Club round on Frogger: https://atariage.com/forums/topic/317760-hsc18-round-4-frogger
- [AA2] AtariAge, "Frogger (Parker Bros. vs. On-Line Systems) analysis?":
  https://forums.atariage.com/topic/379048-frogger-parker-bros-vs-on-line-systems-analysis/ (direct fetch blocked; cited via search excerpts)
- [ANTIC] ANTIC podcast interviews: John Harris (no. 200, 2016)
  https://ataripodcast.libsyn.com/antic-interview-200-john-harris-jawbreaker-frogger-mouskattack and Steve Kranish (no. 454, 2025)
  https://ataripodcast.libsyn.com/antic-interview-454-steve-kranish-parker-brothers-frogger
- [EG] 1983 Arcade Awards list (Electronic Games): https://en.wikipedia.org/wiki/1983_in_video_games
- [NBC] NBC Connecticut, "Man shatters Costanza Frogger record" (2010):
  https://www.nbcconnecticut.com/local/poor-george-man-shatters-costanza-frogger-record/2058540
- [Kot] Kotaku, Frogger world record 1,356,520 (8 March 2022):
  https://kotaku.com/frogger-arcade-world-record-beat-million-points-twin-ga-1848622422
- [GZ] The Gazette on the Hayes/Laffaye rivalry: https://www.thegazette.com/?p=239985
- [TM] TrademarkElite / Markinton, FROGGER Serial 97022040:
  https://www.trademarkelite.com/trademark/trademark-detail/97022040/FROGGER
- [A80] all80s.co.uk, Frogger: https://www.all80s.co.uk/frogger
- [TVT] TV Tropes, Frogger: https://www.tvtropes.org/pmwiki/pmwiki.php/VideoGame/Frogger
- [FW] Frogger fan wiki, "Arcade Classics Frogger": https://frogger.fandom.com/wiki/Arcade_Classics_Frogger
- [Med] Medium, "Great Games: Frogger": https://medium.com/portraits-in-pixel/great-games-frogger-b97b15bef2c
