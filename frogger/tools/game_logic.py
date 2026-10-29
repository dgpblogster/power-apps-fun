"""Power Fx game logic for Frogger (sequential-step tick, see CLAUDE.md and docs/01-game-spec.md).

Lanes are NOT a table. Each lane's objects are evenly spaced on a loop of (192 + W) columns, so the whole
lane state is one scalar offset per lane (ctxOff1..ctxOff9) plus the object count per lane for the current
tier (ctxN1..ctxN9). Object i of lane L sits at X = Mod((i - 1) * Loop / N + Off, Loop) and is drawn at screen
column X - W. Collision against the frog is arithmetic on the lane's period, no table scans. This replaced a
45-row ForAll/Patch pool that ran at 0.2 ticks per second (2026-10-28).

Exports:
  LANES        - per-lane constants shared with gen_app.py
  APP_FORMULAS - named formulas (speeds as nfSpd1..9 so a retune is one line)
  ON_VISIBLE, START_GAME, TICK
"""

# lane, row, dir, speed (columns per tick at FAST), width, kind
LANES = [
    (1, 1, 1, 0.92, 39, "Log"),
    (2, 2, -1, 1.22, 24, "Pair"),
    (3, 3, 1, 1.14, 71, "LogL"),
    (4, 4, 1, 0.77, 31, "LogS"),
    (5, 5, -1, 1.22, 36, "Trio"),
    (6, 7, -1, 1.26, 12, "Car"),
    (7, 8, 1, 2.14, 12, "Racer"),
    (8, 9, -1, 0.77, 12, "Car2"),
    (9, 10, 1, 1.16, 12, "Dozer"),
]
LOOP_PAD = 192

def loop_of(w):
    return LOOP_PAD + w

# tier counts: 5 tiers x 9 lanes (river 5, river 4, river 3, river 2, river 1, road 4, road 3, road 2, road 1)
TIERS = "342344144" "351334244" "241335244" "231234344" "131225454"

APP_FORMULAS = f"""
nfSlowFactor = 0.7;
nfFrogStartX = 76;
nfStartRow = 11;
nfTimeTicks = 600;
nfTiers = "{TIERS}";
""" + "".join(f"nfSpd{L} = {spd};\n" for L, _, _, spd, _, _ in LANES)


def _switch(expr_fn):
    """Switch(ln, 1, v1, 2, v2, ..., 0) over the nine lanes."""
    return "Switch(ln, " + ", ".join(f"{L}, {expr_fn(L, row, d, w, kind)}" for L, row, d, _, w, kind in LANES) + ", 0)"


def counts(level_expr):
    return ", ".join(f"ctxN{L}: Value(Mid(nfTiers, Mod(({level_expr}) - 1, 5) * 9 + {L}, 1))" for L, *_ in LANES)


_OFF_INIT = ", ".join(f"ctxOff{L}: 0" for L, *_ in LANES)

_FROG_RESET = """
  ctxFrogX: nfFrogStartX, ctxFrogRow: nfStartRow, ctxFrogDir: "U", ctxHopTicks: 0, ctxHopQueued: "",
  ctxLockTicks: 10, ctxBestRow: nfStartRow, ctxTime: nfTimeTicks, ctxDeathKind: "", ctxHasLady: false,
  ctxDivePair: 0, ctxDiveTrio: 0, ctxBayTimer: 0, ctxBayCursor: 1, ctxSnakeX: 72, ctxSnakeDir: 1, ctxGatorOn: false,
  ctxSndJingle: 0, ctxSndHop: 0, ctxSndSquash: 0, ctxSndDrown: 0, ctxSndWarn: 0, ctxSndHome: 0,
  ctxSndBonus: 0, ctxSndFanfare: 0, ctxSndPickup: 0, ctxSndExtra: 0, ctxSndOver: 0
"""

ON_VISIBLE = """
UpdateContext({
  ctxMode: "Attract", ctxTick: 0, ctxModeTicks: 0, ctxStartTime: Now(), ctxPaused: false, ctxFrame: 0, ctxMuted: false, ctxKeys: false,
  ctxScore: 0, ctxHigh: 0, ctxLives: 5, ctxLevel: 1, ctxBays: "00000", ctxFast: false, ctxRacerPhase: 0, ctxLadyOn: false,
  ctxTwoPlayer: false, ctxPlayer: 1, ctxScoreP2: 0, ctxLivesP2: 0, ctxLevelP2: 1, ctxBaysP2: "00000",
""" + _FROG_RESET + ",\n  " + _OFF_INIT + ",\n  " + counts("1") + "\n})\n"

START_GAME = """
UpdateContext({
  ctxMode: "Jingle", ctxModeTicks: 30, ctxStartTime: Now(), ctxTick: 0, ctxPaused: false,
  ctxScore: 0, ctxLives: 5, ctxLevel: 1, ctxBays: "00000", ctxRacerPhase: 0, ctxLadyOn: false,
  ctxPlayer: 1, ctxScoreP2: 0, ctxLivesP2: If(ctxTwoPlayer, 5, 0), ctxLevelP2: 1, ctxBaysP2: "00000",
""" + _FROG_RESET + ",\n  " + _OFF_INIT + ",\n  " + counts("1") + "\n})\n"
START_GAME = START_GAME.replace("ctxSndJingle: 0", "ctxSndJingle: 34")

# per-lane offset advance inside sA (racer doubles while racerFast)
_OFF_STEP = ",\n        ".join(
    f"off{L}: Mod(ctxOff{L} + If(moving, {d} * nfSpd{L} * mult" + (" * If(racerFast, 2, 1)" if kind == "Racer" else "") +
    f", 0) + {loop_of(w)}, {loop_of(w)})"
    for L, _, d, _, w, kind in LANES)

_LANE_W = _switch(lambda L, row, d, w, kind: str(w))
_LANE_LOOP = _switch(lambda L, row, d, w, kind: str(loop_of(w)))
_LANE_OFF = _switch(lambda L, row, d, w, kind: f"sA.off{L}")
_LANE_STEP = _switch(lambda L, row, d, w, kind: f"{d} * nfSpd{L}")
_LANE_N = _switch(lambda L, row, d, w, kind: f"ctxN{L}")

TICK = r"""
// ---- Step A: scalars (tick, hop, timer, racer phase, lane offsets) ----
UpdateContext({sA:
  With(
    {
      tick: ctxTick + 1,
      playing: ctxMode = "Playing",
      ticking: ctxMode = "Playing" || ctxMode = "Jingle",
      moving: ctxMode <> "Dying",
      modeTicks0: Max(0, ctxModeTicks - 1),
      mult: If(ctxFast, 1, nfSlowFactor),
      racerPhase: Mod(ctxRacerPhase + 1, 70),
      racerFast: ctxRacerPhase + 1 >= 35,
      canHop: ctxMode = "Playing" && ctxHopTicks = 0 && ctxLockTicks = 0 && ctxHopQueued <> ""
    },
    With(
      {
        dir: If(canHop, ctxHopQueued, ""),
        hop: canHop && Switch(ctxHopQueued,
          "U", ctxFrogRow > 0,
          "D", ctxFrogRow < nfStartRow,
          "L", ctxFrogRow > 0 && ctxFrogX >= 4,
          "R", ctxFrogRow > 0 && ctxFrogX <= 148,
          false)
      },
      {
        tick: tick, playing: playing, moving: moving, modeTicks0: modeTicks0, mult: mult,
        racerPhase: racerPhase,
        snakeX: If(moving && ctxLevel >= 3, Min(144, Max(0, ctxSnakeX + ctxSnakeDir * 0.27 * mult)), ctxSnakeX),
        gatorOn: If(ctxLevel >= 5, true, If(ctxLevel >= 2, If(moving && Mod(ctxOff1 + nfSpd1 * mult, 231) < ctxOff1, !ctxGatorOn, ctxGatorOn), false)),
        hopped: hop,
        hopTicks: If(hop, 3, Max(0, ctxHopTicks - 1)),
        lockTicks: Max(0, ctxLockTicks - 1),
        frogDir: If(hop, dir, ctxFrogDir),
        frogRow: ctxFrogRow + If(hop, Switch(dir, "U", -1, "D", 1, 0), 0),
        frogX: ctxFrogX + If(hop, Switch(dir, "L", -8, "R", 8, 0), 0),
        hopQueued: If(canHop, "", ctxHopQueued),
        time: If(ticking, Max(0, ctxTime - 1), ctxTime),
        timeOut: playing && ctxTime <= 1,
        divePair: Mod(ctxDivePair + If(moving, 1, 0), 85),
        diveTrio: Mod(ctxDiveTrio + If(moving, 1, 0), 43),
        bayTimer: If(ticking, Mod(ctxBayTimer + 1, 85), ctxBayTimer),
        snakeDir: If(ctxSnakeX <= 0 && ctxSnakeDir < 0 || ctxSnakeX >= 144 && ctxSnakeDir > 0, -ctxSnakeDir, ctxSnakeDir),
        """ + _OFF_STEP + r"""
      }
    )
  )
});
// ---- Step B: frog against its row (arithmetic on the lane period) ----
UpdateContext({sF:
  With(
    {
      ln: If(sA.frogRow >= 1 && sA.frogRow <= 5, sA.frogRow, If(sA.frogRow >= 7 && sA.frogRow <= 10, sA.frogRow - 1, 0)),
      fx0: sA.frogX,
      landed: sA.hopTicks = 0,
      c0: sA.frogX + 4
    },
    With(
      {
        lw: """ + _LANE_W + r""",
        loop: """ + _LANE_LOOP + r""",
        off: """ + _LANE_OFF + r""",
        step: """ + _LANE_STEP + r""",
        n: Max(1, """ + _LANE_N + r"""),
        bay: RoundDown(c0 / 32, 0) + 1
      },
      With(
        {
          period: loop / n
        },
        With(
          {
            u: If(ln >= 1, Mod(c0 + lw - off + loop, period), -1),
            v: If(ln >= 6, Mod(fx0 + 7 + lw - off + loop, period), -1)
          },
          With(
            {
              onPlat: ln >= 1 && ln <= 5 && u > 0 && u <= lw,
              pi: Mod(Round((c0 + lw - u - off) / period, 0) + 2 * n, n) + 1,
              pairGone: sA.divePair >= 53 && sA.divePair <= 58,
              trioGone: sA.diveTrio >= 13 && sA.diveTrio <= 15,
              roadHit: sA.playing && landed && ln >= 6 && v > 0 && v < lw + 6,
              sxHead: If(ctxSnakeDir > 0, sA.snakeX + 10, sA.snakeX),
              bayCreature: sA.bayTimer <= If(Mod(ctxLevel, 2) = 1, 36, 58)
            },
            With(
              {
                diveGone: onPlat && ((ln = 2 && pi = n && pairGone) || (ln = 5 && pi = n && trioGone)),
                gatorHead: onPlat && ln = 1 && pi = 1 && sA.gatorOn && u > lw - 10,
                logSnakeHead: onPlat && ln = 3 && pi = 1 && ctxLevel >= 3 && u > lw - 6,
                walkSnake: sA.playing && landed && sA.frogRow = 6 && ctxLevel >= 3 && fx0 + 1 < sxHead + 6 && fx0 + 7 > sxHead,
                ladyHere: onPlat && ln = 4 && pi = 1 && ctxLadyOn && Abs(u - lw / 2) < 5
              },
            With(
              {
                riding: sA.playing && onPlat && !diveGone,
                fx: If(sA.playing && onPlat && !diveGone && sA.moving, fx0 + step * sA.mult, fx0),
                bayOk: bay >= 1 && bay <= 5 && Abs(c0 - (16 + (bay - 1) * 32)) <= 3 && Mid(ctxBays, bay, 1) = "0",
                bayGator: Mod(ctxLevel, 2) = 0 && bay = ctxBayCursor && bayCreature,
                bayFly: Mod(ctxLevel, 2) = 1 && bay = ctxBayCursor && bayCreature
              },
              {
                fx: fx,
                row: sA.frogRow,
                bay: bay,
                pickLady: sA.playing && landed && ladyHere && !ctxHasLady,
                flyHit: bayFly,
                event:
                  If(!sA.playing, "",
                  If(sA.timeOut, "TimeOut",
                  If(roadHit || walkSnake, "Squash",
                  If(ln >= 1 && ln <= 5 && landed && !riding, "Drown",
                  If(ln >= 1 && ln <= 5 && (fx < 0 || fx > 152), "Drown",
                  If(ln >= 1 && ln <= 5 && landed && (gatorHead || logSnakeHead), "Drown",
                  If(sA.frogRow = 0 && landed, If(bayOk && !bayGator, "Home", "Drown"),
                  "")))))))
              }
            )
          )
          )
        )
      )
    )
  )
});
// ---- Step C: outcomes (score, lives, bays, mode) ----
UpdateContext({sC:
  With(
    {
      dying: sF.event = "Squash" || sF.event = "Drown" || sF.event = "TimeOut",
      home: sF.event = "Home",
      ended: sA.modeTicks0 = 0 && ctxMode <> "Playing" && ctxMode <> "Attract"
    },
    With(
      {
        bays1: If(home, Left(ctxBays, sF.bay - 1) & "1" & Mid(ctxBays, sF.bay + 1), ctxBays),
        hopPts: If(sA.hopped && sA.frogDir = "U" && sA.frogRow < ctxBestRow, 10, 0),
        lives1: If(dying, ctxLives - 1, ctxLives)
      },
      With(
        {
          fifth: home && !("0" in bays1)
        },
        With(
          {
            otherAlive: ctxTwoPlayer && ctxLivesP2 > 0,
            nextMode:
              If(dying, "Dying",
              If(fifth, "LevelClear",
              If(home, "Home",
              If(ctxMode = "Jingle" && ended, "Playing",
              If(ctxMode = "Dying" && ended, If(lives1 <= 0 && !(ctxTwoPlayer && ctxLivesP2 > 0), "GameOver", "Jingle"),
              If(ctxMode = "Home" && ended, "Jingle",
              If(ctxMode = "LevelClear" && ended, "Jingle",
              If(ctxMode = "GameOver" && ended, "Attract",
              ctxMode))))))))
          },
          With(
            {
              newLevel: ctxMode = "LevelClear" && nextMode = "Jingle",
              swap: ctxMode = "Dying" && nextMode = "Jingle" && otherAlive,
              score1: ctxScore + hopPts + If(home, 50 + 10 * RoundDown(sA.time / 20, 0) + If(sF.flyHit, 200, 0) + If(ctxHasLady, 200, 0), 0) + If(fifth, 1000, 0)
            },
            With(
              {
                lives2: lives1 + If(newLevel && Mod(ctxLevel, 5) = 0, 1, 0),
                level2: ctxLevel + If(newLevel, 1, 0),
                bays2: If(newLevel, "00000", bays1)
              },
              {
                nextMode: nextMode,
                score: If(swap, ctxScoreP2, score1),
                lives: If(swap, ctxLivesP2, lives2),
                level: If(swap, ctxLevelP2, level2),
                bays: If(swap, ctxBaysP2, bays2),
                scoreP2: If(swap, score1, ctxScoreP2),
                livesP2: If(swap, lives2, ctxLivesP2),
                levelP2: If(swap, level2, ctxLevelP2),
                baysP2: If(swap, bays2, ctxBaysP2),
                respawn: nextMode = "Jingle" && ctxMode <> "Jingle",
                newLevel: newLevel,
                swap: swap,
                relayout: newLevel || swap
              }
            )
          )
        )
      )
    )
  )
});
// ---- Step D: commit ----
UpdateContext({
  ctxTick: sA.tick,
  ctxFrame: If(Mod(sA.tick, 5) = 0, Mod(ctxFrame + 1, 2), ctxFrame),
  ctxRacerPhase: sA.racerPhase,
  ctxMode: sC.nextMode,
  ctxModeTicks: If(sC.nextMode = ctxMode, sA.modeTicks0,
    Switch(sC.nextMode, "Jingle", 30, "Dying", 50, "Home", 20, "LevelClear", 60, "GameOver", 200, 0)),
  ctxScore: sC.score,
  ctxHigh: Max(ctxHigh, Max(sC.score, sC.scoreP2)),
  ctxLives: sC.lives,
  ctxLevel: sC.level,
  ctxBays: sC.bays,
  ctxPlayer: If(sC.swap, 3 - ctxPlayer, ctxPlayer),
  ctxScoreP2: sC.scoreP2,
  ctxLivesP2: sC.livesP2,
  ctxLevelP2: sC.levelP2,
  ctxBaysP2: sC.baysP2,
  ctxFrogX: If(sC.respawn, nfFrogStartX, sF.fx),
  ctxFrogRow: If(sC.respawn, nfStartRow, sF.row),
  ctxFrogDir: If(sC.respawn, "U", sA.frogDir),
  ctxHopTicks: If(sC.respawn, 0, sA.hopTicks),
  ctxHopQueued: If(sC.respawn || sC.nextMode <> "Playing", "", sA.hopQueued),
  ctxLockTicks: If(sC.respawn, 10, sA.lockTicks),
  ctxBestRow: If(sC.respawn, nfStartRow, Min(ctxBestRow, sF.row)),
  ctxTime: If(sC.respawn, nfTimeTicks, sA.time),
  ctxDeathKind: If(sC.nextMode = "Dying" && ctxMode <> "Dying", sF.event, ctxDeathKind),
  ctxSndJingle: If(sC.nextMode = "Jingle" && ctxMode <> "Jingle", If(ctxSndJingle > 0, -34, 34), If(ctxSndJingle < 0, -ctxSndJingle, Max(0, ctxSndJingle - 1))),
  ctxSndHop: If(sA.hopped, If(ctxSndHop > 0, -3, 3), If(ctxSndHop < 0, -ctxSndHop, Max(0, ctxSndHop - 1))),
  ctxSndSquash: If(sC.nextMode = "Dying" && ctxMode <> "Dying" && sF.event = "Squash", If(ctxSndSquash > 0, -9, 9), If(ctxSndSquash < 0, -ctxSndSquash, Max(0, ctxSndSquash - 1))),
  ctxSndDrown: If(sC.nextMode = "Dying" && ctxMode <> "Dying" && sF.event <> "Squash", If(ctxSndDrown > 0, -22, 22), If(ctxSndDrown < 0, -ctxSndDrown, Max(0, ctxSndDrown - 1))),
  ctxSndWarn: If(sA.playing && sA.time <= 100 && sA.time > 0 && Mod(sA.time, 20) = 0, If(ctxSndWarn > 0, -4, 4), If(ctxSndWarn < 0, -ctxSndWarn, Max(0, ctxSndWarn - 1))),
  ctxSndHome: If(sF.event = "Home" && !(sF.flyHit || ctxHasLady) && sC.nextMode <> "LevelClear", If(ctxSndHome > 0, -10, 10), If(ctxSndHome < 0, -ctxSndHome, Max(0, ctxSndHome - 1))),
  ctxSndBonus: If(sF.event = "Home" && (sF.flyHit || ctxHasLady) && sC.nextMode <> "LevelClear", If(ctxSndBonus > 0, -10, 10), If(ctxSndBonus < 0, -ctxSndBonus, Max(0, ctxSndBonus - 1))),
  ctxSndFanfare: If(sC.nextMode = "LevelClear" && ctxMode <> "LevelClear", If(ctxSndFanfare > 0, -43, 43), If(ctxSndFanfare < 0, -ctxSndFanfare, Max(0, ctxSndFanfare - 1))),
  ctxSndPickup: If(sF.pickLady, If(ctxSndPickup > 0, -6, 6), If(ctxSndPickup < 0, -ctxSndPickup, Max(0, ctxSndPickup - 1))),
  ctxSndExtra: If(sC.lives > ctxLives, If(ctxSndExtra > 0, -15, 15), If(ctxSndExtra < 0, -ctxSndExtra, Max(0, ctxSndExtra - 1))),
  ctxSndOver: If(sC.nextMode = "GameOver" && ctxMode <> "GameOver", If(ctxSndOver > 0, -50, 50), If(ctxSndOver < 0, -ctxSndOver, Max(0, ctxSndOver - 1))),
  ctxHasLady: If(sC.respawn, false, If(sF.pickLady, true, ctxHasLady)),
  ctxLadyOn: If(sC.respawn, sC.level >= 2, If(sF.pickLady, false, ctxLadyOn)),
  ctxDivePair: sA.divePair,
  ctxDiveTrio: sA.diveTrio,
  ctxBayTimer: If(sC.respawn, 84, sA.bayTimer),
  ctxBayCursor: If(sA.bayTimer = 0 || sC.relayout,
    With({nextBay: LookUp(Sequence(5), Value > ctxBayCursor && Mid(sC.bays, Value, 1) = "0")},
      If(IsBlank(nextBay), Coalesce(LookUp(Sequence(5), Mid(sC.bays, Value, 1) = "0").Value, 1), nextBay.Value)),
    ctxBayCursor),
  ctxSnakeX: sA.snakeX,
  ctxSnakeDir: sA.snakeDir,
  ctxGatorOn: If(sC.relayout, sC.level >= 5, sA.gatorOn),
  """ + ",\n  ".join(f"ctxOff{L}: sA.off{L}" for L, *_ in LANES) + r""",
  """ + ",\n  ".join(f"ctxN{L}: If(sC.relayout, Value(Mid(nfTiers, Mod(sC.level - 1, 5) * 9 + {L}, 1)), ctxN{L})" for L, *_ in LANES) + r"""
})
"""
