"""Power Fx game logic for the Galaxian canvas app (M1-M5).

Exports three formula strings used by gen_app.py:
  ON_VISIBLE   - Screen1.OnVisible: initial state
  START_GAME   - START button: reset state and enter Ready
  TICK         - tmrGame.OnTimerEnd: one simulation tick
Coordinates: 160 columns x 240 lines (see docs/01-game-spec.md). Diver X/Y are sprite centres.
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
  ctxExplTicks: 0, ctxExplX: 0, ctxExplY: 0,
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
With(
  {
    tick: ctxTick + 1,
    playing: ctxMode = "Playing",
    convoyMoves: ctxMode = "Playing" || ctxMode = "Attract" || ctxMode = "Ready" || ctxMode = "GameOver",
    beginner: ctxLevel = 10,
    levelBoost: If(ctxLevel = 10, 0, ctxLevel)
  },
  With(
    {
      shipX: If(playing, Min(154, Max(6, ctxShipX + Max(-nfShipSpeed, Min(nfShipSpeed, sldMove.Value - ctxShipX)))), ctxShipX),
      convoyMin: -18 - (ctxMinCol - 1) * 12,
      convoyMax: 126 - (ctxMaxCol - 1) * 12,
      convoyXTry: ctxConvoyX + If(convoyMoves && Mod(tick, 2) = 0, ctxConvoyDir, 0)
    },
    With(
      {
        convoyX: Min(convoyMax, Max(convoyMin, convoyXTry)),
        convoyDir: If(convoyXTry > convoyMax, -1, If(convoyXTry < convoyMin, 1, ctxConvoyDir)),
        misLaunch: playing && ctxFire && !ctxMisActive,
        misMovedY: ctxMisY - nfMissileSpeed
      },
      With(
        {
          misActive0: misLaunch || (ctxMisActive && misMovedY >= 26),
          misX: If(ctxMisActive, ctxMisX, shipX),
          misY: If(misLaunch, 192 - nfMissileSpeed, If(ctxMisActive, misMovedY, 201)),
          // ---- difficulty and swarm state ----
          nDiff: Min(14, ctxDiffBase + ctxDiffExtra + levelBoost),
          aliveCount: Len(Substitute(ctxAlive, "0", "")),
          noCyanPurple: IsBlank(Find("1", Mid(ctxAlive, 10, 28))),
          anyCommander: !IsBlank(Find("1", Left(ctxAlive, 3))),
          emptyRow5: IsBlank(Find("1", Mid(ctxAlive, 28, 10))),
          emptyRow4: IsBlank(Find("1", Mid(ctxAlive, 18, 10)))
        },
        With(
          {
            endPhase: aliveCount <= 3 || noCyanPurple,
            nMaxSingles: Min(Int(nDiff / 2), 3) + 1,
            launchInterval: Max(12, Int(78 / (1 + nDiff / 2))),
            convoyInterval: If(noCyanPurple, 40, Max(40, (9 - Min(3, Int(nDiff / 4))) * 20)),
            nBombChecks: Min(3, 1 + Int(levelBoost / 4) + If(emptyRow5, 1, 0) + If(emptyRow5 && emptyRow4, 1, 0)),
            canAttack: playing && ctxMourn = 0,
            flank: If(ctxConvoyX - convoyMin < 10, -1, If(convoyMax - ctxConvoyX < 10, 1, If(Rand() < 0.5, -1, 1)))
          },
          With(
            {
              launchTimer0: If(canAttack, ctxLaunchTimer - 1, ctxLaunchTimer),
              convoyTimer0: If(canAttack, ctxConvoyTimer - 1, ctxConvoyTimer),
              freeSingle: LookUp(ctxDivers, Slot >= 4 && Slot <= 3 + nMaxSingles && !Active, Slot),
              convoyFree: !LookUp(ctxDivers, Slot = 1, Active),
              flankCol: If(flank = -1, ctxMinCol, ctxMaxCol)
            },
            With(
              {
                singleSlot: If(canAttack && launchTimer0 <= 0 && !IsBlank(freeSingle),
                  LookUp(
                    Table(
                      {s: If(!anyCommander && flankCol >= 3 && flankCol <= 8, flankCol + 1, 0)},
                      {s: If(flankCol >= 2 && flankCol <= 9, flankCol + 8, 0)},
                      {s: flankCol + 17},
                      {s: flankCol + 27}
                    ),
                    s > 0 && Mid(ctxAlive, s, 1) = "1", s),
                  Blank()),
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
                    escCands: Filter(Table({s: cmdCol}, {s: cmdCol + 1}, {s: cmdCol + 2}), cmdSlot > 0 && Mid(ctxAlive, s, 1) = "1")
                  },
                  With(
                    {
                      esc1: If(CountRows(escCands) >= 1, First(escCands).s, 0),
                      esc2: If(CountRows(escCands) >= 2, Index(escCands, 2).s, 0)
                    },
                    With(
                      {
                        launches: Filter(
                          Table(
                            {k: Coalesce(freeSingle, 0), h: Coalesce(singleSlot, 0), esc: 0},
                            {k: 1, h: cmdSlot, esc: If(esc1 > 0, 1, 0) + If(esc2 > 0, 1, 0)},
                            {k: 2, h: esc1, esc: 0},
                            {k: 3, h: esc2, esc: 0}
                          ), h > 0 && k > 0)
                      },
                      With(
                        {
                          // alive string after this tick's launches
                          aliveL: Concat(ForAll(Sequence(37) As n,
                            {v: If(!IsBlank(LookUp(launches, h = n.Value)), "0", Mid(ctxAlive, n.Value, 1))}), v),
                          // new diver records for launched slots
                          diversL: ForAll(ctxDivers As d,
                            With({L: LookUp(launches, k = d.Slot)},
                              If(IsBlank(L), d,
                                With({h: L.h},
                                  With(
                                    {
                                      hc: If(h <= 3, Switch(h, 1, 4, 2, 6, 7), If(h <= 9, h - 1, If(h <= 17, h - 8, If(h <= 27, h - 17, h - 27)))),
                                      hr: If(h <= 3, 1, If(h <= 9, 2, If(h <= 17, 3, If(h <= 27, 4, 5)))),
                                      hk: If(h <= 3, "Commander", If(h <= 9, "Hornet", If(h <= 17, "Emissary", "Drone")))
                                    },
                                    With({x0: 22 + (hc - 1) * 12 + 4 + convoyX, y0: 28 + (hr - 1) * 10 + 4},
                                      {Slot: d.Slot, Active: true, Kind: hk, Home: h, Col: hc, Row: hr, X: x0, Y: y0,
                                       Stage: "Arc", StageTick: 0, Dir: flank, StartX: x0, StartY: y0,
                                       Pivot: x0, Amp: 0, SignDX: 1, Phase: 0, EscLaunched: L.esc, EscKilled: 0}))))))
                        },
                        With(
                          {
                            // ---- diver motion ----
                            diversM: ForAll(diversL As d,
                              If(!d.Active || !playing, d,
                                If(d.Stage = "Arc",
                                  With({t: d.StageTick + 1},
                                    With({nx: d.StartX + d.Dir * 10 * (1 - Cos(t * Pi() / 16)), ny: d.StartY - 10 * Sin(t * Pi() / 16)},
                                      If(t < 8,
                                        Patch(d, {X: nx, Y: ny, StageTick: t}),
                                        With({tdx: Max(30, Min(80, Abs(shipX - nx))), sgn: If(shipX >= nx, 1, -1)},
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
                                            If(endPhase || d.Stage = "Charge",
                                              With({rx: 20 + Rand() * 120},
                                                Patch(d, {Stage: "Charge", X: rx, Y: -10, Pivot: rx, Amp: 30, Phase: 0,
                                                          SignDX: If(shipX >= rx, 1, -1), StageTick: 0})),
                                              Patch(d, {Stage: "Return", Y: -10, X: 22 + (d.Col - 1) * 12 + 4 + convoyX, StageTick: 0}))))))),
                                If(d.Stage = "Return",
                                  With({hx: 22 + (d.Col - 1) * 12 + 4 + convoyX, hy: 28 + (d.Row - 1) * 10 + 4},
                                    Patch(d, {X: hx, Y: Min(hy, d.Y + 3)})),
                                  d)))))
                          },
                          With(
                            {
                              // ---- escorts follow their Commander ----
                              diversS: With({c: LookUp(diversM, Slot = 1)},
                                ForAll(diversM As d,
                                  If((d.Slot = 2 || d.Slot = 3) && d.Active && c.Active && c.Stage <> "Return",
                                    Patch(d, {X: c.X + If(d.Slot = 2, -6, 6), Y: c.Y + 10, Stage: c.Stage,
                                              Pivot: c.Pivot + If(d.Slot = 2, -6, 6), Amp: c.Amp, SignDX: c.SignDX, Phase: c.Phase}),
                                    d))),
                              // ---- bombs move ----
                              bombsM: ForAll(ctxBombs As b,
                                If(b.Active && playing,
                                  With({ny: b.Y + 6, nx: b.X + b.DX}, Patch(b, {X: nx, Y: ny, Active: ny <= 240 && nx >= 0 && nx <= 160})),
                                  If(playing, b, Patch(b, {Active: false}))))
                            },
                            With(
                              {
                                shooter: If(canAttack && !(beginner && ctxWave <= 16),
                                  LookUp(diversS, Active && (Stage = "Dive" || (Stage = "Charge" && Y > 40)) &&
                                    ((Y - If(Stage = "Charge" || Y > 144, 4, 3) < 130 && Y >= 130) ||
                                     (nBombChecks >= 2 && Y - If(Stage = "Charge" || Y > 144, 4, 3) < 155 && Y >= 155) ||
                                     (nBombChecks >= 3 && Y - If(Stage = "Charge" || Y > 144, 4, 3) < 180 && Y >= 180))),
                                  Blank()),
                                firstFree: LookUp(bombsM, !Active, Slot),
                                retSlot: LookUp(diversS, Active && Stage = "Return" && Y >= 28 + (Row - 1) * 10 + 4, Slot)
                              },
                              With(
                                {
                                  bombs2: If(IsBlank(shooter) || IsBlank(firstFree), bombsM,
                                    ForAll(bombsM As b,
                                      If(b.Slot = firstFree,
                                        {Slot: b.Slot, Active: true, X: shooter.X, Y: shooter.Y + 6,
                                         DX: Max(-2, Min(2, (shipX - shooter.X) / 40 + (Rand() - 0.5) * If(levelBoost >= 5, 1.6, 0.8)))},
                                        b))),
                                  // ---- missile vs formation ----
                                  relX: misX - 22 - convoyX,
                                  relY: misY - 28
                                },
                                With(
                                  {
                                    col: If(relX >= 0 && Mod(relX, 12) < 8, Int(relX / 12) + 1, 0),
                                    // swept test: the lowest alive row whose 8-line band intersects the segment the missile covered this tick
                                    row: If(misActive0 && playing && relX >= 0 && Mod(relX, 12) < 8,
                                      Coalesce(
                                        Max(
                                          Filter(Sequence(5) As r,
                                            misY < 28 + (r.Value - 1) * 10 + 8 && misY + nfMissileSpeed + 4 > 28 + (r.Value - 1) * 10 &&
                                            With({c: Int(relX / 12) + 1},
                                              With({s: Switch(r.Value,
                                                      1, Switch(c, 4, 1, 6, 2, 7, 3, 0),
                                                      2, If(c >= 3 && c <= 8, c + 1, 0),
                                                      3, If(c >= 2 && c <= 9, c + 8, 0),
                                                      4, 17 + c,
                                                      5, 27 + c,
                                                      0)},
                                                s > 0 && Mid(aliveL, s, 1) = "1"))),
                                          Value),
                                        0),
                                      0),
                                    // ---- missile / nose vs divers ----
                                    hitDiver: If(playing && misActive0,
                                      LookUp(diversS, Active && Abs(X - misX) < 5 && misY < Y + 4 && misY + nfMissileSpeed + 4 > Y - 4), Blank()),
                                    noseDiver: If(playing && !misActive0,
                                      LookUp(diversS, Active && Abs(X - shipX) < 5 && Y + 4 >= 201 && Y - 4 <= 205), Blank())
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
                                        0),
                                      killed: If(IsBlank(hitDiver), noseDiver, hitDiver)
                                    },
                                    With(
                                      {
                                        hit: slot > 0 && Mid(aliveL, slot, 1) = "1",
                                        pts: Switch(row, 1, 60, 2, 50, 3, 40, 30),
                                        dPts: If(IsBlank(killed), 0,
                                          Switch(killed.Kind, "Drone", 60, "Emissary", 80, "Hornet", 100,
                                            If(killed.EscLaunched = 0, 150, If(killed.EscLaunched = 1, 200, If(killed.EscKilled = 2, 800, 300))))),
                                        cmdKilled: !IsBlank(killed) && killed.Kind = "Commander"
                                      },
                                      With(
                                        {
                                          // ---- apply kills and returns to divers ----
                                          diversK: ForAll(diversS As d,
                                            If(!IsBlank(killed) && d.Slot = killed.Slot, Patch(d, {Active: false}),
                                            If(!IsBlank(killed) && (killed.Slot = 2 || killed.Slot = 3) && d.Slot = 1, Patch(d, {EscKilled: d.EscKilled + 1}),
                                            If(!IsBlank(retSlot) && d.Slot = retSlot, Patch(d, {Active: false}),
                                            d)))),
                                          aliveH: If(hit, Left(aliveL, slot - 1) & "0" & Mid(aliveL, slot + 1, 37), aliveL),
                                          retHome: If(IsBlank(retSlot), 0, LookUp(diversS, Slot = retSlot, Home))
                                        },
                                        With(
                                          {
                                            aliveR: If(retHome > 0, Left(aliveH, retHome - 1) & "1" & Mid(aliveH, retHome + 1, 37), aliveH),
                                            score: Min(999990, ctxScore + If(hit, pts, 0) + dPts),
                                            // ---- player death ----
                                            shipHit: playing && (
                                              !IsBlank(LookUp(bombs2, Active && Abs(X - shipX) < 5 && Y + 4 >= 205 && Y <= 213)) ||
                                              !IsBlank(LookUp(diversK, Active && Abs(X - shipX) < 8 && Y + 4 >= 205 && Y - 4 <= 213)))
                                          },
                                          With(
                                            {
                                              // on death every diver goes home instantly
                                              aliveD: If(shipHit,
                                                Concat(ForAll(Sequence(37) As n,
                                                  {v: If(Mid(aliveR, n.Value, 1) = "1" || !IsBlank(LookUp(diversK, Active && Home = n.Value)), "1", "0")}), v),
                                                aliveR),
                                              diversD: If(shipHit, nfDiversEmpty, diversK),
                                              bombsD: If(shipHit, nfBombsEmpty, bombs2)
                                            },
                                            With(
                                              {
                                                cols: Filter(Sequence(10) As c,
                                                  Mid(aliveD, 17 + c.Value, 1) = "1" || Mid(aliveD, 27 + c.Value, 1) = "1" ||
                                                  (c.Value >= 2 && c.Value <= 9 && Mid(aliveD, c.Value + 8, 1) = "1") ||
                                                  (c.Value >= 3 && c.Value <= 8 && Mid(aliveD, c.Value + 1, 1) = "1") ||
                                                  (c.Value = 4 && Mid(aliveD, 1, 1) = "1") || (c.Value = 6 && Mid(aliveD, 2, 1) = "1") || (c.Value = 7 && Mid(aliveD, 3, 1) = "1")),
                                                cleared: IsBlank(Find("1", aliveD)) && CountIf(diversD, Active) = 0,
                                                modeTicks0: Max(0, ctxModeTicks - 1)
                                              },
                                              With(
                                                {
                                                  nextMode:
                                                    If(shipHit, "Dying",
                                                    If(playing && cleared, "WaveClear",
                                                    If(ctxMode = "Ready" && modeTicks0 = 0, "Playing",
                                                    If(ctxMode = "Dying" && modeTicks0 = 0, If(ctxLives > 1, "Ready", "GameOver"),
                                                    If(ctxMode = "WaveClear" && modeTicks0 = 0, "Ready",
                                                    If(ctxMode = "GameOver" && modeTicks0 = 0, "Attract",
                                                    ctxMode)))))),
                                                  bonusNow: playing && !ctxBonus && score >= 5000,
                                                  waveTick: If(playing && ctxMourn = 0, ctxWaveTicks + 1, ctxWaveTicks)
                                                },
                                                With(
                                                  {
                                                    newWave: nextMode = "Ready" && ctxMode = "WaveClear",
                                                    respawn: nextMode = "Ready" && ctxMode = "Dying",
                                                    lostLife: ctxMode = "Dying" && modeTicks0 = 0,
                                                    aggStep: waveTick >= 400
                                                  },
                                                  UpdateContext({
                                                    ctxTick: tick,
                                                    ctxMode: nextMode,
                                                    ctxModeTicks:
                                                      If(nextMode = ctxMode, modeTicks0,
                                                      Switch(nextMode, "Dying", 13, "WaveClear", 85, "Ready", 40, "GameOver", 200, 0)),
                                                    ctxShipX: If(respawn, 80, shipX),
                                                    ctxConvoyX: If(newWave, 0, convoyX),
                                                    ctxConvoyDir: convoyDir,
                                                    ctxFire: false,
                                                    ctxMisActive: misActive0 && !hit && IsBlank(hitDiver) && !shipHit,
                                                    ctxMisX: misX,
                                                    ctxMisY: If(misActive0 && !hit && IsBlank(hitDiver) && !shipHit, misY, 201),
                                                    ctxAlive: If(newWave, nfAliveAll, aliveD),
                                                    ctxMinCol: If(newWave || CountRows(cols) = 0, 1, Min(cols, Value)),
                                                    ctxMaxCol: If(newWave || CountRows(cols) = 0, 10, Max(cols, Value)),
                                                    ctxDivers: If(newWave, nfDiversEmpty, diversD),
                                                    ctxBombs: If(newWave, nfBombsEmpty, bombsD),
                                                    ctxWave: If(newWave, ctxWave + 1, ctxWave),
                                                    ctxScore: score,
                                                    ctxHigh: If(nextMode = "GameOver" && ctxMode = "Dying", Max(ctxHigh, score), ctxHigh),
                                                    ctxLives: If(lostLife, ctxLives - 1, If(bonusNow, Min(5, ctxLives + 1), ctxLives)),
                                                    ctxBonus: ctxBonus || bonusNow,
                                                    ctxLaunchTimer: If(newWave || respawn, launchInterval,
                                                      If(!IsBlank(singleSlot), launchInterval, If(canAttack && launchTimer0 <= 0, 6, launchTimer0))),
                                                    ctxConvoyTimer: If(newWave || respawn, convoyInterval,
                                                      If(cmdSlot > 0, convoyInterval, If(canAttack && convoyTimer0 <= 0, 20, convoyTimer0))),
                                                    ctxMourn: If(cmdKilled, 80, Max(0, ctxMourn - 1)),
                                                    ctxDiffBase: If(newWave, Min(7, ctxDiffBase + 1), ctxDiffBase),
                                                    ctxDiffExtra: If(newWave, 0, If(shipHit, Max(0, ctxDiffExtra - 1), If(aggStep, Min(7, ctxDiffExtra + 1), ctxDiffExtra))),
                                                    ctxWaveTicks: If(newWave || aggStep, 0, waveTick),
                                                    ctxExplTicks: If(hit || !IsBlank(killed), 8, Max(0, ctxExplTicks - 1)),
                                                    ctxExplX: If(!IsBlank(killed), killed.X, If(hit, 22 + (col - 1) * 12 + 4 + convoyX, ctxExplX)),
                                                    ctxExplY: If(!IsBlank(killed), killed.Y, If(hit, 28 + (row - 1) * 10 + 4, ctxExplY)),
                                                    ctxPopupTicks: If(cmdKilled || (hit && row = 1), 17, Max(0, ctxPopupTicks - 1)),
                                                    ctxPopupX: If(cmdKilled, killed.X, If(hit && row = 1, misX, ctxPopupX)),
                                                    ctxPopupY: If(cmdKilled, killed.Y, If(hit && row = 1, 28, ctxPopupY)),
                                                    ctxPopupText: If(cmdKilled, Text(dPts), If(hit && row = 1, Text(pts), ctxPopupText))
                                                  })
                                                )
                                              )
                                            )
                                          )
                                        )
                                      )
                                    )
                                  )
                                )
                              )
                            )
                          )
                        )
                      )
                    )
                  )
                )
              )
            )
          )
        )
      )
    )
  )
)
"""
