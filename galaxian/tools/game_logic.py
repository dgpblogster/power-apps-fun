"""Power Fx game logic for the Galaxian canvas app (M1-M5).

Exports three formula strings used by gen_app.py:
  ON_VISIBLE   - Screen1.OnVisible: initial state
  START_GAME   - START button: reset state and enter Ready
  TICK         - tmrGame.OnTimerEnd: one simulation tick
Coordinates: 160 columns x 240 lines (see docs/01-game-spec.md). Diver X/Y are sprite centres.

Performance note: the tick is a SEQUENCE of UpdateContext steps. Each intermediate table (divers after
launch, after motion, after escort sync, after kills) is materialised once into a context variable and
later steps read the stored value. A single nested With chain re-evaluated those tables on every
reference and ran at about 0.5 ticks per second instead of 20.
"""

# Named formulas that live in App.Formulas (appended by gen_app.py)
APP_FORMULAS = """
nfDiversEmpty = ForAll(Sequence(7) As n, {Slot: n.Value, Active: false, Kind: "", Home: 0, Col: 0, Row: 0, X: 0, Y: 0, Stage: "", StageTick: 0, Dir: 1, StartX: 0, StartY: 0, Pivot: 0, Amp: 0, SignDX: 1, Phase: 0, EscLaunched: 0, EscKilled: 0});
nfBombsEmpty = ForAll(Sequence(7) As n, {Slot: n.Value, Active: false, X: 0, Y: 0, DX: 0});
nfShipSpeed = 6;
nfMissileSpeed = 16;
"""

_RESET_FIELDS = """
  ctxShipX: 80, ctxFire: false, ctxMisActive: false, ctxMisX: 80, ctxMisY: 201,
  ctxConvoyX: 0, ctxConvoyDir: 1, ctxAlive: nfAliveAll, ctxMinCol: 1, ctxMaxCol: 10,
  ctxDivers: nfDiversEmpty, ctxBombs: nfBombsEmpty,
  ctxLaunchTimer: 78, ctxConvoyTimer: 180, ctxMourn: 0, ctxDiffBase: 0, ctxDiffExtra: 0, ctxWaveTicks: 0,
  ctxExplTicks: 0, ctxExplX: 0, ctxExplY: 0, ctxFrame: 0,
  ctxPopupTicks: 0, ctxPopupX: 0, ctxPopupY: 0, ctxPopupText: "",
  ctxPaused: false
"""

ON_VISIBLE = """
UpdateContext({
  ctxMode: "Attract", ctxTick: 0, ctxModeTicks: 0, ctxStartTime: Now(),
  ctxScore: 0, ctxHigh: 0, ctxLives: 3, ctxWave: 1, ctxLevel: 0, ctxBonus: false,
""" + _RESET_FIELDS + """
})
"""

START_GAME = """
UpdateContext({
  ctxMode: "Ready", ctxModeTicks: 40, ctxStartTime: Now(), ctxTick: 0,
  ctxScore: 0, ctxLives: 3, ctxWave: 1, ctxBonus: false,
""" + _RESET_FIELDS + """
});
Reset(sldMove)
"""

TICK = r"""
// ---- Step A: scalars (ship, convoy, missile, difficulty, launch decisions) ----
UpdateContext({sA:
  With(
    {
      tick: ctxTick + 1,
      playing: ctxMode = "Playing",
      convoyMoves: ctxMode = "Playing" || ctxMode = "Attract" || ctxMode = "Ready" || ctxMode = "GameOver",
      beginner: ctxLevel = 10,
      levelBoost: If(ctxLevel = 10, 0, ctxLevel),
      convoyMin: -18 - (ctxMinCol - 1) * 12,
      convoyMax: 126 - (ctxMaxCol - 1) * 12,
      aliveCount: Len(Substitute(ctxAlive, "0", "")),
      noCyanPurple: IsBlank(Find("1", Mid(ctxAlive, 10, 28))),
      anyCommander: !IsBlank(Find("1", Left(ctxAlive, 3))),
      emptyRow5: IsBlank(Find("1", Mid(ctxAlive, 28, 10))),
      emptyRow4: IsBlank(Find("1", Mid(ctxAlive, 18, 10)))
    },
    With(
      {
        shipX: If(playing, Min(154, Max(6, ctxShipX + Max(-nfShipSpeed, Min(nfShipSpeed, sldMove.Value - ctxShipX)))), ctxShipX),
        convoyXTry: ctxConvoyX + If(convoyMoves && Mod(tick, 2) = 0, ctxConvoyDir, 0),
        misLaunch: playing && ctxFire && !ctxMisActive,
        misMovedY: ctxMisY - nfMissileSpeed,
        nDiff: Min(14, ctxDiffBase + ctxDiffExtra + levelBoost),
        canAttack: playing && ctxMourn = 0,
        flank: If(ctxConvoyX - convoyMin < 10, -1, If(convoyMax - ctxConvoyX < 10, 1, If(Rand() < 0.5, -1, 1)))
      },
      With(
        {
          convoyX: Min(convoyMax, Max(convoyMin, convoyXTry)),
          convoyDir: If(convoyXTry > convoyMax, -1, If(convoyXTry < convoyMin, 1, ctxConvoyDir)),
          misActive0: misLaunch || (ctxMisActive && misMovedY >= 26),
          misX: If(ctxMisActive, ctxMisX, shipX),
          misY: If(misLaunch, 192 - nfMissileSpeed, If(ctxMisActive, misMovedY, 201)),
          endPhase: aliveCount <= 3 || noCyanPurple,
          nMaxSingles: Min(Int(nDiff / 2), 3) + 1,
          launchInterval: Max(12, Int(78 / (1 + nDiff / 2))),
          convoyInterval: If(noCyanPurple, 40, Max(40, (9 - Min(3, Int(nDiff / 4))) * 20)),
          nBombChecks: Min(3, 1 + Int(levelBoost / 4) + If(emptyRow5, 1, 0) + If(emptyRow5 && emptyRow4, 1, 0)),
          launchTimer0: If(canAttack, ctxLaunchTimer - 1, ctxLaunchTimer),
          convoyTimer0: If(canAttack, ctxConvoyTimer - 1, ctxConvoyTimer),
          flankCol: If(flank = -1, ctxMinCol, ctxMaxCol)
        },
        With(
          {
            freeSingle: Coalesce(LookUp(ctxDivers, Slot >= 4 && Slot <= 3 + nMaxSingles && !Active, Slot), 0),
            convoyFree: !LookUp(ctxDivers, Slot = 1, Active),
            singleSlot: If(canAttack && launchTimer0 <= 0,
              Coalesce(LookUp(
                Table(
                  {s: If(!anyCommander && flankCol >= 3 && flankCol <= 8, flankCol + 1, 0)},
                  {s: If(flankCol >= 2 && flankCol <= 9, flankCol + 8, 0)},
                  {s: flankCol + 17},
                  {s: flankCol + 27}
                ), s > 0 && Mid(ctxAlive, s, 1) = "1", s), 0),
              0)
          },
          With(
            {
              cmdSlot: If(canAttack && convoyTimer0 <= 0 && convoyFree && anyCommander,
                If(flank = -1,
                  If(Mid(ctxAlive, 1, 1) = "1", 1, If(Mid(ctxAlive, 2, 1) = "1", 2, 3)),
                  If(Mid(ctxAlive, 3, 1) = "1", 3, If(Mid(ctxAlive, 2, 1) = "1", 2, 1))),
                0)
            },
            With(
              {
                cmdCol: Switch(cmdSlot, 1, 4, 2, 6, 3, 7, 0)
              },
              With(
                {
                  esc1: If(cmdSlot > 0,
                    If(Mid(ctxAlive, cmdCol, 1) = "1", cmdCol,
                      If(Mid(ctxAlive, cmdCol + 1, 1) = "1", cmdCol + 1,
                        If(Mid(ctxAlive, cmdCol + 2, 1) = "1", cmdCol + 2, 0))),
                    0)
                },
                With(
                  {
                    esc2: If(cmdSlot > 0 && esc1 > 0,
                      If(esc1 < cmdCol + 1 && Mid(ctxAlive, cmdCol + 1, 1) = "1", cmdCol + 1,
                        If(esc1 < cmdCol + 2 && Mid(ctxAlive, cmdCol + 2, 1) = "1", cmdCol + 2, 0)),
                      0)
                  },
                  {
                    tick: tick, playing: playing, beginner: beginner, levelBoost: levelBoost,
                    shipX: shipX, convoyX: convoyX, convoyDir: convoyDir,
                    misActive0: misActive0, misX: misX, misY: misY,
                    endPhase: endPhase, nBombChecks: nBombChecks, canAttack: canAttack, flank: flank,
                    launchInterval: launchInterval, convoyInterval: convoyInterval,
                    launchTimer0: launchTimer0, convoyTimer0: convoyTimer0,
                    freeSingle: If(singleSlot > 0, freeSingle, 0),
                    singleSlot: If(freeSingle > 0, singleSlot, 0),
                    cmdSlot: cmdSlot, esc1: esc1, esc2: esc2,
                    nEsc: If(esc1 > 0, 1, 0) + If(esc2 > 0, 1, 0)
                  }
                )
              )
            )
          )
        )
      )
    )
  )
});
// ---- Step B: apply launches to the convoy string and the diver pool ----
UpdateContext({
  sAliveL: With({a0: ctxAlive},
    With({a1: If(sA.singleSlot > 0, Left(a0, sA.singleSlot - 1) & "0" & Mid(a0, sA.singleSlot + 1, 37), a0)},
      With({a2: If(sA.cmdSlot > 0, Left(a1, sA.cmdSlot - 1) & "0" & Mid(a1, sA.cmdSlot + 1, 37), a1)},
        With({a3: If(sA.cmdSlot > 0 && sA.esc1 > 0, Left(a2, sA.esc1 - 1) & "0" & Mid(a2, sA.esc1 + 1, 37), a2)},
          If(sA.cmdSlot > 0 && sA.esc2 > 0, Left(a3, sA.esc2 - 1) & "0" & Mid(a3, sA.esc2 + 1, 37), a3))))),
  sDivers: ForAll(ctxDivers As d,
    With(
      {
        h: If(d.Slot = sA.freeSingle && sA.singleSlot > 0, sA.singleSlot,
            If(d.Slot = 1 && sA.cmdSlot > 0, sA.cmdSlot,
            If(d.Slot = 2 && sA.cmdSlot > 0, sA.esc1,
            If(d.Slot = 3 && sA.cmdSlot > 0, sA.esc2, 0))))
      },
      If(h = 0, d,
        With(
          {
            hc: If(h <= 3, Switch(h, 1, 4, 2, 6, 7), If(h <= 9, h - 1, If(h <= 17, h - 8, If(h <= 27, h - 17, h - 27)))),
            hr: If(h <= 3, 1, If(h <= 9, 2, If(h <= 17, 3, If(h <= 27, 4, 5)))),
            hk: If(h <= 3, "Commander", If(h <= 9, "Hornet", If(h <= 17, "Emissary", "Drone")))
          },
          With({x0: 22 + (hc - 1) * 12 + 4 + sA.convoyX, y0: 28 + (hr - 1) * 10 + 4},
            {Slot: d.Slot, Active: true, Kind: hk, Home: h, Col: hc, Row: hr, X: x0, Y: y0,
             Stage: "Arc", StageTick: 0, Dir: sA.flank, StartX: x0, StartY: y0,
             Pivot: x0, Amp: 0, SignDX: 1, Phase: 0, EscLaunched: If(d.Slot = 1, sA.nEsc, 0), EscKilled: 0})))))
});
// ---- Step C: diver motion ----
UpdateContext({
  sDivers: ForAll(sDivers As d,
    If(!d.Active || !sA.playing, d,
      If(d.Stage = "Arc",
        With({t: d.StageTick + 1},
          With({nx: d.StartX + d.Dir * 10 * (1 - Cos(t * Pi() / 16)), ny: d.StartY - 10 * Sin(t * Pi() / 16)},
            If(t < 8,
              Patch(d, {X: nx, Y: ny, StageTick: t}),
              With({tdx: Max(30, Min(80, Abs(sA.shipX - nx))), sgn: If(sA.shipX >= nx, 1, -1)},
                Patch(d, {X: nx, Y: ny, StageTick: 0, Stage: "Dive", SignDX: sgn,
                          Pivot: nx + sgn * tdx / 2, Amp: tdx / 2 * (0.6 + Rand() * 0.8), Phase: 0}))))),
      If(d.Stage = "Dive" || d.Stage = "Charge",
        With({spd: If(d.Stage = "Charge" || d.Y > 140, 4, 3), ph: d.Phase + 0.35},
          With({ny: d.Y + spd, nx0: d.Pivot - d.SignDX * Cos(ph) * d.Amp + (Rand() - 0.5) * 2},
            With({nx: If(ctxWave <= 2, Min(146, Max(14, nx0)), nx0)},
              If(ny <= 240 && nx >= -8 && nx <= 168,
                Patch(d, {X: nx, Y: ny, Phase: ph, StageTick: d.StageTick + 1}),
                If(d.Kind = "Commander" && d.EscLaunched = 0,
                  Patch(d, {Active: false}),
                  If(sA.endPhase || d.Stage = "Charge",
                    With({rx: 20 + Rand() * 120},
                      Patch(d, {Stage: "Charge", X: rx, Y: -10, Pivot: rx, Amp: 30, Phase: 0,
                                SignDX: If(sA.shipX >= rx, 1, -1), StageTick: 0})),
                    Patch(d, {Stage: "Return", Y: -10, X: 22 + (d.Col - 1) * 12 + 4 + sA.convoyX, StageTick: 0}))))))),
      If(d.Stage = "Return",
        With({hx: 22 + (d.Col - 1) * 12 + 4 + sA.convoyX, hy: 28 + (d.Row - 1) * 10 + 4},
          Patch(d, {X: hx, Y: Min(hy, d.Y + 3)})),
        d)))))
});
// ---- Step D: escorts follow their Commander; bombs move ----
UpdateContext({
  sDivers: With({c: LookUp(sDivers, Slot = 1)},
    ForAll(sDivers As d,
      If((d.Slot = 2 || d.Slot = 3) && d.Active && c.Active && c.Stage <> "Return",
        Patch(d, {X: c.X + If(d.Slot = 2, -6, 6), Y: c.Y + 10, Stage: c.Stage,
                  Pivot: c.Pivot + If(d.Slot = 2, -6, 6), Amp: c.Amp, SignDX: c.SignDX, Phase: c.Phase}),
        d))),
  sBombs: ForAll(ctxBombs As b,
    If(b.Active && sA.playing,
      With({ny: b.Y + 6, nx: b.X + b.DX}, Patch(b, {X: nx, Y: ny, Active: ny <= 240 && nx >= 0 && nx <= 160})),
      If(sA.playing, b, Patch(b, {Active: false}))))
});
// ---- Step E: shooting, returns, collisions ----
UpdateContext({sE:
  With(
    {
      shooter: If(sA.canAttack && !(sA.beginner && ctxWave <= 16),
        LookUp(sDivers, Active && (Stage = "Dive" || (Stage = "Charge" && Y > 40)) &&
          ((Y - If(Stage = "Charge" || Y > 144, 4, 3) < 130 && Y >= 130) ||
           (sA.nBombChecks >= 2 && Y - If(Stage = "Charge" || Y > 144, 4, 3) < 155 && Y >= 155) ||
           (sA.nBombChecks >= 3 && Y - If(Stage = "Charge" || Y > 144, 4, 3) < 180 && Y >= 180))),
        Blank()),
      firstFree: Coalesce(LookUp(sBombs, !Active, Slot), 0),
      retSlot: Coalesce(LookUp(sDivers, Active && Stage = "Return" && Y >= 28 + (Row - 1) * 10 + 4, Slot), 0),
      relX: sA.misX - 22 - sA.convoyX,
      relY: sA.misY - 28,
      hitDiver: If(sA.playing && sA.misActive0,
        LookUp(sDivers, Active && Abs(X - sA.misX) < 5 && sA.misY < Y + 4 && sA.misY + nfMissileSpeed + 4 > Y - 4), Blank()),
      noseDiver: If(sA.playing && !sA.misActive0,
        LookUp(sDivers, Active && Abs(X - sA.shipX) < 5 && Y + 4 >= 201 && Y - 4 <= 205), Blank())
    },
    With(
      {
        col: If(relX >= 0 && Mod(relX, 12) < 8, Int(relX / 12) + 1, 0),
        killed: If(IsBlank(hitDiver), noseDiver, hitDiver)
      },
      With(
        {
          // swept test: the lowest alive row whose 8-line band intersects the segment the missile covered this tick
          row: If(sA.misActive0 && sA.playing && col >= 1 && col <= 10,
            Coalesce(Max(Filter(Sequence(5) As r,
              sA.misY < 28 + (r.Value - 1) * 10 + 8 && sA.misY + nfMissileSpeed + 4 > 28 + (r.Value - 1) * 10 &&
              With({s: Switch(r.Value,
                      1, Switch(col, 4, 1, 6, 2, 7, 3, 0),
                      2, If(col >= 3 && col <= 8, col + 1, 0),
                      3, If(col >= 2 && col <= 9, col + 8, 0),
                      4, 17 + col,
                      5, 27 + col,
                      0)},
                s > 0 && Mid(sAliveL, s, 1) = "1")), Value), 0),
            0)
        },
      With(
        {
          slot: If(col >= 1 && col <= 10 && row >= 1,
            Switch(row,
              1, Switch(col, 4, 1, 6, 2, 7, 3, 0),
              2, If(col >= 3 && col <= 8, col + 1, 0),
              3, If(col >= 2 && col <= 9, col + 8, 0),
              4, 17 + col,
              5, 27 + col,
              0),
            0)
        },
        {
          hasShooter: !IsBlank(shooter),
          shooterX: If(IsBlank(shooter), 0, shooter.X),
          shooterY: If(IsBlank(shooter), 0, shooter.Y),
          firstFree: firstFree,
          retSlot: retSlot,
          retHome: If(retSlot > 0, LookUp(sDivers, Slot = retSlot, Home), 0),
          col: col, row: row, slot: slot,
          hit: slot > 0 && Mid(sAliveL, slot, 1) = "1",
          pts: Switch(row, 1, 60, 2, 50, 3, 40, 30),
          killedSlot: If(IsBlank(killed), 0, killed.Slot),
          killedX: If(IsBlank(killed), 0, killed.X),
          killedY: If(IsBlank(killed), 0, killed.Y),
          cmdKilled: !IsBlank(killed) && killed.Kind = "Commander",
          dPts: If(IsBlank(killed), 0,
            Switch(killed.Kind, "Drone", 60, "Emissary", 80, "Hornet", 100,
              If(killed.EscLaunched = 0, 150, If(killed.EscLaunched = 1, 200, If(killed.EscKilled = 2, 800, 300)))))
        }
      ))
    )
  )
});
// ---- Step F: apply bombs, kills, and returns ----
UpdateContext({
  sBombs: If(!sE.hasShooter || sE.firstFree = 0, sBombs,
    ForAll(sBombs As b,
      If(b.Slot = sE.firstFree,
        {Slot: b.Slot, Active: true, X: sE.shooterX, Y: sE.shooterY + 6,
         DX: Max(-2, Min(2, (sA.shipX - sE.shooterX) / 40 + (Rand() - 0.5) * If(sA.levelBoost >= 5, 1.6, 0.8)))},
        b))),
  sDivers: ForAll(sDivers As d,
    If(sE.killedSlot > 0 && d.Slot = sE.killedSlot, Patch(d, {Active: false}),
    If(sE.killedSlot > 0 && (sE.killedSlot = 2 || sE.killedSlot = 3) && d.Slot = 1, Patch(d, {EscKilled: d.EscKilled + 1}),
    If(sE.retSlot > 0 && d.Slot = sE.retSlot, Patch(d, {Active: false}),
    d)))),
  sAliveL: With({aH: If(sE.hit, Left(sAliveL, sE.slot - 1) & "0" & Mid(sAliveL, sE.slot + 1, 37), sAliveL)},
    If(sE.retHome > 0, Left(aH, sE.retHome - 1) & "1" & Mid(aH, sE.retHome + 1, 37), aH))
});
// ---- Step G: player death, column bounds, mode transitions ----
UpdateContext({sG:
  With(
    {
      score: Min(999990, ctxScore + If(sE.hit, sE.pts, 0) + sE.dPts),
      shipHit: sA.playing && (
        !IsBlank(LookUp(sBombs, Active && Abs(X - sA.shipX) < 5 && Y + 4 >= 205 && Y <= 213)) ||
        !IsBlank(LookUp(sDivers, Active && Abs(X - sA.shipX) < 8 && Y + 4 >= 205 && Y - 4 <= 213)))
    },
    With(
      {
        aliveD: If(shipHit,
          Concat(ForAll(Sequence(37) As n,
            {v: If(Mid(sAliveL, n.Value, 1) = "1" || !IsBlank(LookUp(sDivers, Active && Home = n.Value)), "1", "0")}), v),
          sAliveL)
      },
      With(
        {
          aliveChanged: aliveD <> ctxAlive,
          cleared: IsBlank(Find("1", aliveD)) && (shipHit || CountIf(sDivers, Active) = 0),
          modeTicks0: Max(0, ctxModeTicks - 1)
        },
        With(
          {
            cols: If(aliveChanged,
              Filter(Sequence(10) As c,
                Mid(aliveD, 17 + c.Value, 1) = "1" || Mid(aliveD, 27 + c.Value, 1) = "1" ||
                (c.Value >= 2 && c.Value <= 9 && Mid(aliveD, c.Value + 8, 1) = "1") ||
                (c.Value >= 3 && c.Value <= 8 && Mid(aliveD, c.Value + 1, 1) = "1") ||
                (c.Value = 4 && Mid(aliveD, 1, 1) = "1") || (c.Value = 6 && Mid(aliveD, 2, 1) = "1") || (c.Value = 7 && Mid(aliveD, 3, 1) = "1")),
              Filter(Sequence(10) As c, c.Value < 0)),
            nextMode:
              If(shipHit, "Dying",
              If(sA.playing && cleared, "WaveClear",
              If(ctxMode = "Ready" && modeTicks0 = 0, "Playing",
              If(ctxMode = "Dying" && modeTicks0 = 0, If(ctxLives > 1, "Ready", "GameOver"),
              If(ctxMode = "WaveClear" && modeTicks0 = 0, "Ready",
              If(ctxMode = "GameOver" && modeTicks0 = 0, "Attract",
              ctxMode)))))),
            bonusNow: sA.playing && !ctxBonus && score >= 5000,
            waveTick: If(sA.playing && ctxMourn = 0, ctxWaveTicks + 1, ctxWaveTicks)
          },
          {
            score: score, shipHit: shipHit, aliveD: aliveD, modeTicks0: modeTicks0,
            nextMode: nextMode, bonusNow: bonusNow, waveTick: waveTick,
            minCol: If(CountRows(cols) = 0, ctxMinCol, Min(cols, Value)),
            maxCol: If(CountRows(cols) = 0, ctxMaxCol, Max(cols, Value)),
            newWave: nextMode = "Ready" && ctxMode = "WaveClear",
            respawn: nextMode = "Ready" && ctxMode = "Dying",
            lostLife: ctxMode = "Dying" && modeTicks0 = 0,
            aggStep: waveTick >= 400
          }
        )
      )
    )
  )
});
// ---- Step H: commit the new state ----
UpdateContext({
  ctxTick: sA.tick,
  ctxFrame: If(Mod(sA.tick, 5) = 0, 1 - ctxFrame, ctxFrame),
  ctxMode: sG.nextMode,
  ctxModeTicks:
    If(sG.nextMode = ctxMode, sG.modeTicks0,
    Switch(sG.nextMode, "Dying", 13, "WaveClear", 85, "Ready", 40, "GameOver", 200, 0)),
  ctxShipX: If(sG.respawn, 80, sA.shipX),
  ctxConvoyX: If(sG.newWave, 0, sA.convoyX),
  ctxConvoyDir: sA.convoyDir,
  ctxFire: false,
  ctxMisActive: sA.misActive0 && !sE.hit && sE.killedSlot = 0 && !sG.shipHit,
  ctxMisX: sA.misX,
  ctxMisY: If(sA.misActive0 && !sE.hit && sE.killedSlot = 0 && !sG.shipHit, sA.misY, 201),
  ctxAlive: If(sG.newWave, nfAliveAll, sG.aliveD),
  ctxMinCol: If(sG.newWave, 1, sG.minCol),
  ctxMaxCol: If(sG.newWave, 10, sG.maxCol),
  ctxDivers: If(sG.newWave || sG.shipHit, nfDiversEmpty, sDivers),
  ctxBombs: If(sG.newWave || sG.shipHit, nfBombsEmpty, sBombs),
  ctxWave: If(sG.newWave, ctxWave + 1, ctxWave),
  ctxScore: sG.score,
  ctxHigh: If(sG.nextMode = "GameOver" && ctxMode = "Dying", Max(ctxHigh, sG.score), ctxHigh),
  ctxLives: If(sG.lostLife, ctxLives - 1, If(sG.bonusNow, Min(5, ctxLives + 1), ctxLives)),
  ctxBonus: ctxBonus || sG.bonusNow,
  ctxLaunchTimer: If(sG.newWave || sG.respawn, sA.launchInterval,
    If(sA.singleSlot > 0, sA.launchInterval, If(sA.canAttack && sA.launchTimer0 <= 0, 6, sA.launchTimer0))),
  ctxConvoyTimer: If(sG.newWave || sG.respawn, sA.convoyInterval,
    If(sA.cmdSlot > 0, sA.convoyInterval, If(sA.canAttack && sA.convoyTimer0 <= 0, 20, sA.convoyTimer0))),
  ctxMourn: If(sE.cmdKilled, 80, Max(0, ctxMourn - 1)),
  ctxDiffBase: If(sG.newWave, Min(7, ctxDiffBase + 1), ctxDiffBase),
  ctxDiffExtra: If(sG.newWave, 0, If(sG.shipHit, Max(0, ctxDiffExtra - 1), If(sG.aggStep, Min(7, ctxDiffExtra + 1), ctxDiffExtra))),
  ctxWaveTicks: If(sG.newWave || sG.aggStep, 0, sG.waveTick),
  ctxExplTicks: If(sE.hit || sE.killedSlot > 0, 8, Max(0, ctxExplTicks - 1)),
  ctxExplX: If(sE.killedSlot > 0, sE.killedX, If(sE.hit, 22 + (sE.col - 1) * 12 + 4 + sA.convoyX, ctxExplX)),
  ctxExplY: If(sE.killedSlot > 0, sE.killedY, If(sE.hit, 28 + (sE.row - 1) * 10 + 4, ctxExplY)),
  ctxPopupTicks: If(sE.cmdKilled || (sE.hit && sE.row = 1), 17, Max(0, ctxPopupTicks - 1)),
  ctxPopupX: If(sE.cmdKilled, sE.killedX, If(sE.hit && sE.row = 1, sA.misX, ctxPopupX)),
  ctxPopupY: If(sE.cmdKilled, sE.killedY, If(sE.hit && sE.row = 1, 28, ctxPopupY)),
  ctxPopupText: If(sE.cmdKilled, Text(sE.dPts), If(sE.hit && sE.row = 1, Text(sE.pts), ctxPopupText))
})
"""
