"""Power Fx game logic for Deep Station M0 (docs/01-game-spec.md sections 4, 5, 7-9).

The tick is a short sequence of UpdateContext steps (sIn, sPl, sWp, sEn, sC), each reading the previous
step's record once. Enemies are fixed scalar slots ctxE{n}K/X/Y/S/H/T/V/F generated for n = 1..MAX_SLOTS;
no table is patched in the tick (the Frogger rule).

Enemy slots are configurable twice:
  * build time: MAX_SLOTS (env DEEPSTATION_ENEMY_SLOTS, default 12) decides how many slots exist;
  * run time:   ctxSlots (button "SLOTS" on the status bar) caps how many of them are active, so the spike
                can compare 4 / 8 / 12 without regenerating the app.

Enemy states: 0 empty, 1 idle, 2 chase, 3 pain, 4 dead.
Sound event ids match pcf/RaycastView/src/audio.ts (SND).
"""
import os

MAX_SLOTS = int(os.environ.get("DEEPSTATION_ENEMY_SLOTS", "12"))
if not 1 <= MAX_SLOTS <= 24:
    raise SystemExit("DEEPSTATION_ENEMY_SLOTS must be 1..24")

SND = {"shot": 1, "enemyHit": 2, "enemyDeath": 3, "door": 4, "hurt": 5, "pickup": 6, "wake": 7,
       "enemyAttack": 8, "empty": 9, "playerDeath": 10}

ENEMY_HEALTH = {1: 20, 2: 40, 3: 60, 4: 150, 5: 1000}

SLOTS = range(1, MAX_SLOTS + 1)


def num(v):
    """Python float -> Power Fx literal."""
    return f"{v:.4f}".rstrip("0").rstrip(".") if isinstance(v, float) else str(v)


def pfx_text(s):
    return '"' + s.replace('"', '""') + '"'


# ---------------------------------------------------------------- named formulas and functions

def app_formulas(level):
    sx, sy, syaw = level.start
    items = level.items
    decor = "".join(f"{200 + i},{t['kind']},0,{t['x']:.2f},{t['y']:.2f},1;" for i, t in enumerate(level.decor))
    return f"""
// ---- level: {level.name} ----
nfMapW = {level.w};
nfMapH = {level.h};
nfMap = {pfx_text(level.cells)};
nfMapData = {pfx_text(level.map_data)};
nfLight = {pfx_text(level.light)};
nfDoorMap = {pfx_text(level.door_map)};
nfDoorIds = "ABCDEFGHIJKLMNOP";
nfStartX = {num(sx)};
nfStartY = {num(sy)};
nfStartYaw = {num(float(syaw))};
nfItemCount = {len(items)};
nfDecorSprites = {pfx_text(decor)};
nfEnemyTotal = {len(level.enemies)};
// ---- tuning (cells per tick at 20 ticks per second) ----
nfTickMs = 50;
nfWalk = 0.15;
nfRun = 0.25;
nfRadius = 0.25;
nfEnemyRadius = 0.3;
nfEnemySpeed = 0.06;
nfSightRange = 12;
nfMaxSlots = {MAX_SLOTS};
""" + _HELPERS


_HELPERS = """// ---- geometry helpers (pure functions; doors are passed in because named formulas can't read context variables) ----
CellIdx(x: Number, y: Number): Number = RoundDown(y, 0) * nfMapW + RoundDown(x, 0) + 1;
CellAt(x: Number, y: Number): Text = If(x < 0 || y < 0 || x >= nfMapW || y >= nfMapH, "1", Mid(nfMap, CellIdx(x, y), 1));
DoorOpen(i: Number, doors: Text): Number = Value(Mid(doors, Find(Mid(nfDoorMap, i, 1), nfDoorIds), 1));
Solid(x: Number, y: Number, doors: Text): Boolean =
    With({c: CellAt(x, y)},
        If(c = "." || c = "~" || c = "T", false,
           c = "D" || c = "a" || c = "c" || c = "v", DoorOpen(CellIdx(x, y), doors) < 7,
           true));
Blocked(x: Number, y: Number, r: Number, doors: Text): Boolean =
    Solid(x - r, y - r, doors) || Solid(x + r, y - r, doors) || Solid(x - r, y + r, doors) || Solid(x + r, y + r, doors);
Clear(ax: Number, ay: Number, bx: Number, by: Number, doors: Text): Boolean =
    With({n: Max(1, Min(24, RoundUp(Sqrt((bx - ax) ^ 2 + (by - ay) ^ 2) * 2, 0)))},
        CountIf(Sequence(n) As s, Solid(ax + (bx - ax) * s.Value / (n + 1), ay + (by - ay) * s.Value / (n + 1), doors)) = 0);
AngDiff(a: Number, b: Number): Number = Mod(a - b + 540, 360) - 180;
Bit(k: Number, b: Number): Boolean = Mod(RoundDown(k / b, 0), 2) = 1;
B2N(b: Boolean): Number = If(b, 1, 0);
Num(v: Number): Text = Text(v, "0.00", "en-US");
"""


# ---------------------------------------------------------------- start / restart

def start_game(level):
    enemies = level.enemies
    parts = []
    for n in SLOTS:
        if n <= len(enemies):
            e = enemies[n - 1]
            parts.append(f"ctxE{n}K: {e['kind']}, ctxE{n}X: {num(e['x'])}, ctxE{n}Y: {num(e['y'])}, "
                         f"ctxE{n}S: If({n} <= ctxSlots, 1, 0), ctxE{n}H: {ENEMY_HEALTH[e['kind']]}, "
                         f"ctxE{n}T: 0, ctxE{n}V: false, ctxE{n}F: 0")
        else:
            parts.append(f"ctxE{n}K: 0, ctxE{n}X: 0, ctxE{n}Y: 0, ctxE{n}S: 0, ctxE{n}H: 0, ctxE{n}T: 0, "
                         f"ctxE{n}V: false, ctxE{n}F: 0")
    item_flags = "0" * len(level.items)
    return ("UpdateContext({\n"
            "  ctxMode: \"Playing\", ctxTick: 0, ctxStartTime: Now(), ctxPaused: false, ctxSpawn: ctxSpawn + 1,\n"
            "  ctxPX: nfStartX, ctxPY: nfStartY, ctxYaw: nfStartYaw, ctxHealth: 100, ctxArmor: 0,\n"
            "  ctxWeapon: 2, ctxAmmoRivet: 50, ctxCooldown: 0, ctxWFrame: 0, ctxFlash: 0, ctxHurtTicks: 0,\n"
            "  ctxDoors: \"0000000000000000\", ctxDoorAnimId: 0, ctxDoorAnimStep: 0, ctxChips: \"000\",\n"
            f"  ctxTaken: \"{item_flags}\", ctxKills: 0, ctxEvents: \"\", ctxMsg: \"\", ctxMsgTicks: 0, ctxHazardTicks: 0,\n"
            "  ctxUseSeen: Coalesce(pcfView.UseSeq, 0), ctxWeaponSeen: Coalesce(pcfView.WeaponSeq, 0), ctxEcho: 0,\n  "
            + ",\n  ".join(parts) + "\n})")


def on_visible(level):
    """First visit: session settings, then the same start as the RESTART button (inlined, no Select)."""
    return ("UpdateContext({ctxSlots: nfMaxSlots, ctxSpawn: 0, ctxDiag: true, ctxMuted: false, "
            "ctxMenuSeen: Coalesce(pcfView.MenuSeq, 0)});\n" + start_game(level))


# ---------------------------------------------------------------- the tick

def _items_block(level):
    """Pickup tests for each item (fixed per level, no table): returns Power Fx fields for sPl."""
    items = level.items
    if not items:
        return 'taken: ctxTaken, heal: 0, ammo: 0, picked: false'
    picks = []
    for i, t in enumerate(items, start=1):
        cond = f'Mid(ctxTaken, {i}, 1) = "0" && Abs(nx - {num(t["x"])}) < 0.6 && Abs(ny - {num(t["y"])}) < 0.6'
        if t["name"] in ("medkit", "medvial"):
            cond += " && ctxHealth < 100"
        picks.append((i, t, cond))
    taken = " & ".join(f'If({c}, "1", Mid(ctxTaken, {i}, 1))' for i, t, c in picks)
    heal = " + ".join(f'If({c}, {25 if t["name"] == "medkit" else 10}, 0)' for i, t, c in picks
                      if t["name"] in ("medkit", "medvial")) or "0"
    ammo = " + ".join(f'If({c}, 20, 0)' for i, t, c in picks if t["name"] == "rivets") or "0"
    any_ = " || ".join(f"({c})" for i, t, c in picks)
    return f"taken: {taken},\n          heal: {heal},\n          ammo: {ammo},\n          picked: {any_}"


def _hitscan():
    """Nearest live enemy inside the aim cone; LOS is checked only for the chosen one."""
    cand = []
    for n in SLOTS:
        cand.append(
            f"c{n}: If({n} <= ctxSlots && ctxE{n}S > 0 && ctxE{n}S < 4 && "
            f"Abs(AngDiff(Degrees(Atan2(ctxE{n}X - sPl.x, ctxE{n}Y - sPl.y)), sIn.yaw)) < "
            f"Degrees(Atan(0.35 / Max(0.1, Sqrt((ctxE{n}X - sPl.x) ^ 2 + (ctxE{n}Y - sPl.y) ^ 2)))) + 1.5 && "
            f"Sqrt((ctxE{n}X - sPl.x) ^ 2 + (ctxE{n}Y - sPl.y) ^ 2) < reach, "
            f"Sqrt((ctxE{n}X - sPl.x) ^ 2 + (ctxE{n}Y - sPl.y) ^ 2), 999)")
    cands = ",\n              ".join(cand)
    dmin = "Min(" + ", ".join(f"c{n}" for n in SLOTS) + ")"
    first = "".join(f"If(c{n} = dmin, {n}, " for n in SLOTS) + "0" + ")" * MAX_SLOTS
    ex = "Switch(slot, " + ", ".join(f"{n}, ctxE{n}X" for n in SLOTS) + ", 0)"
    ey = "Switch(slot, " + ", ".join(f"{n}, ctxE{n}Y" for n in SLOTS) + ", 0)"
    return cands, dmin, first, ex, ey


def _enemy(n):
    """One enemy slot's step. Reads ctxE{n}*, sIn, sPl, sWp; returns a record."""
    return f"""e{n}: With(
      {{active: {n} <= ctxSlots && ctxE{n}S > 0 && ctxE{n}S < 4,
       dx: sPl.x - ctxE{n}X, dy: sPl.y - ctxE{n}Y, hit: sWp.slot = {n}}},
      With(
        {{d: Max(0.01, Sqrt(dx ^ 2 + dy ^ 2)),
         h: ctxE{n}H - If(hit, sWp.dmg, 0)}},
        With(
          {{los: If(active && Mod(sIn.tick, 4) = {n % 4}, d < nfSightRange && Clear(ctxE{n}X, ctxE{n}Y, sPl.x, sPl.y, sPl.doors), ctxE{n}V && active),
           dead: active && h <= 0}},
          With(
            {{woke: active && !dead && ctxE{n}S = 1 && (los || hit || (sWp.fired && d < 10)),
             s1: If(dead, 4, !active, ctxE{n}S,
                    ctxE{n}S = 1, If(los || hit || (sWp.fired && d < 10), 2, 1),
                    hit && Rand() < 0.5, 3,
                    ctxE{n}S = 3 && ctxE{n}T <= 0, 2,
                    ctxE{n}S)}},
            With(
              {{shoots: s1 = 2 && los && d < 8 && ctxE{n}T <= 0 && sC0.alive,
               mvx: If(s1 = 2 && d > 0.9, dx / d * nfEnemySpeed, 0),
               mvy: If(s1 = 2 && d > 0.9, dy / d * nfEnemySpeed, 0)}},
              With(
                {{x1: If(mvx <> 0 && !Blocked(ctxE{n}X + mvx, ctxE{n}Y, nfEnemyRadius, sPl.doors), ctxE{n}X + mvx, ctxE{n}X)}},
                With(
                  {{y1: If(mvy <> 0 && !Blocked(x1, ctxE{n}Y + mvy, nfEnemyRadius, sPl.doors), ctxE{n}Y + mvy, ctxE{n}Y)}},
                  {{x: x1, y: y1, s: s1, h: If(active, Max(0, h), ctxE{n}H), v: los,
                   t: If(shoots, 40 + RandBetween(0, 20), s1 = 3 && ctxE{n}S <> 3, 6, Max(0, ctxE{n}T - 1)),
                   f: If(s1 = 3, 3, shoots || (s1 = 2 && ctxE{n}T > 34), 2, Mod(RoundDown(sIn.tick / 5, 0) + {n}, 2)),
                   pd: If(shoots && Rand() < 0.75 - d / 16, RandBetween(3, 10), 0),
                   kill: dead,
                   ev: If(dead, ";{SND['enemyDeath']}", hit, ";{SND['enemyHit']}", "") & If(woke, ";{SND['wake']}", "") & If(shoots, ";{SND['enemyAttack']}", "")}}
                )))))))"""


def tick(level):
    cands, dmin, first, ex, ey = _hitscan()
    enemy_steps = ",\n    ".join(_enemy(n) for n in SLOTS)
    enemy_commit = ",\n  ".join(
        f"ctxE{n}X: sEn.e{n}.x, ctxE{n}Y: sEn.e{n}.y, ctxE{n}S: sEn.e{n}.s, ctxE{n}H: sEn.e{n}.h, "
        f"ctxE{n}T: sEn.e{n}.t, ctxE{n}V: sEn.e{n}.v, ctxE{n}F: sEn.e{n}.f" for n in SLOTS)
    enemy_dmg = " + ".join(f"sEn.e{n}.pd" for n in SLOTS)
    enemy_kills = " + ".join(f"B2N(sEn.e{n}.kill)" for n in SLOTS)
    enemy_ev = " & ".join(f"sEn.e{n}.ev" for n in SLOTS)
    items = _items_block(level)

    return f"""
// ---- sIn: input (outputs of the view, read once per tick) ----
UpdateContext({{sIn:
  With(
    {{k: If(ctxMode = "Playing", Coalesce(pcfView.Keys, 0), 0),
     yaw: Coalesce(pcfView.Yaw, ctxYaw),
     useNow: Coalesce(pcfView.UseSeq, 0) <> ctxUseSeen,
     wpnNow: Coalesce(pcfView.WeaponSeq, 0) <> ctxWeaponSeen}},
    With(
      {{fwd: B2N(Bit(k, 1)) - B2N(Bit(k, 2)),
       str: B2N(Bit(k, 8)) - B2N(Bit(k, 4)),
       spd: If(Bit(k, 16), nfRun, nfWalk),
       rad: Radians(yaw)}},
      With(
        {{f: If(fwd <> 0 && str <> 0, 0.7071, 1)}},
        {{tick: ctxTick + 1, k: k, yaw: yaw, rad: rad,
         fire: Bit(k, 32),
         use: useNow && ctxMode = "Playing",
         restart: useNow && ctxMode <> "Playing",
         wpn: If(wpnNow && (pcfView.WeaponReq = 1 || pcfView.WeaponReq = 2), pcfView.WeaponReq, ctxWeapon),
         dx: (Cos(rad) * fwd - Sin(rad) * str) * spd * f,
         dy: (Sin(rad) * fwd + Cos(rad) * str) * spd * f}}
      )))}});
If(sIn.restart, Select(btnRestart));
If(!sIn.restart,
// ---- sPl: player movement, pickups, use (doors, exit), hazard floor ----
UpdateContext({{sPl:
  With(
    {{nx0: If(Blocked(ctxPX + sIn.dx, ctxPY, nfRadius, ctxDoors), ctxPX, ctxPX + sIn.dx)}},
    With(
      {{nx: nx0, ny: If(Blocked(nx0, ctxPY + sIn.dy, nfRadius, ctxDoors), ctxPY, ctxPY + sIn.dy)}},
      With(
        {{front: CellIdx(nx + Cos(sIn.rad), ny + Sin(sIn.rad)),
         frontCell: CellAt(nx + Cos(sIn.rad), ny + Sin(sIn.rad)),
         onHazard: CellAt(nx, ny) = "~",
          {items}}},
        With(
          {{doorId: If(sIn.use, Find(Mid(nfDoorMap, front, 1), nfDoorIds), 0),
           locked: (frontCell = "a" && Mid(ctxChips, 1, 1) <> "1") || (frontCell = "c" && Mid(ctxChips, 2, 1) <> "1") || (frontCell = "v" && Mid(ctxChips, 3, 1) <> "1")}},
          With(
            {{opening: doorId > 0 && !locked && Mid(ctxDoors, doorId, 1) = "0" && ctxDoorAnimId = 0,
             animStep: If(ctxDoorAnimId > 0, ctxDoorAnimStep + 1, 0)}},
            {{x: nx, y: ny,
             doors: If(ctxDoorAnimId > 0, Replace(ctxDoors, ctxDoorAnimId, 1, Text(Min(9, animStep))), ctxDoors),
             animId: If(opening, doorId, ctxDoorAnimId > 0 && animStep < 9, ctxDoorAnimId, 0),
             animStep: If(opening, 0, animStep),
             exit: sIn.use && frontCell = "X",
             lockedMsg: doorId > 0 && locked,
             hazard: onHazard && Mod(ctxHazardTicks + 1, 20) = 0,
             hazardTicks: If(onHazard, ctxHazardTicks + 1, 0),
             taken: taken, heal: heal, ammo: ammo, picked: picked,
             ev: If(opening, ";{SND['door']}", "") & If(picked, ";{SND['pickup']}", "")}}
          )))))}});
// ---- sC0: is the player alive this tick (enemies stop firing at a corpse) ----
UpdateContext({{sC0: {{alive: ctxMode = "Playing"}}}});
// ---- sWp: weapon switch, cooldown, firing, hitscan ----
UpdateContext({{sWp:
  With(
    {{cool: Max(0, ctxCooldown - 1),
     reach: If(sIn.wpn = 1, 1.1, 40)}},
    With(
      {{trigger: sC0.alive && sIn.fire && cool = 0}},
      With(
        {{fired: trigger && (sIn.wpn = 1 || ctxAmmoRivet > 0),
         click: trigger && sIn.wpn = 2 && ctxAmmoRivet <= 0,
          {cands}}},
        With(
          {{dmin: {dmin}}},
          With(
            {{slot0: If(fired && dmin < 999, {first}, 0)}},
            With(
              {{slot: If(slot0 > 0 && With({{slot: slot0}}, Clear(sPl.x, sPl.y, {ex}, {ey}, sPl.doors)), slot0, 0)}},
              {{fired: fired, slot: slot,
               dmg: If(sIn.wpn = 1, RandBetween(10, 30), RandBetween(5, 15)),
               cool: If(fired || click, If(sIn.wpn = 1, 10, 8), cool),
               ammo: ctxAmmoRivet - If(fired && sIn.wpn = 2, 1, 0),
               wframe: If(fired, 1, ctxWFrame > 0 && ctxWFrame < 3, ctxWFrame + 1, 0),
               ev: If(fired, ";{SND['shot']}", click, ";{SND['empty']}", "")}}
            ))))))}});
// ---- sEn: enemies (fixed slots, no tables) ----
UpdateContext({{sEn: {{
    {enemy_steps}
  }}}});
// ---- sC: commit ----
UpdateContext({{sC:
  With(
    {{dmg: If(sC0.alive, {enemy_dmg} + If(sPl.hazard, 5, 0), 0)}},
    With(
      {{hp: Min(200, Max(0, ctxHealth + sPl.heal - dmg))}},
      {{dmg: dmg, hp: hp, died: sC0.alive && hp <= 0, kills: {enemy_kills}}}))}});
UpdateContext({{
  ctxTick: sIn.tick, ctxYaw: sIn.yaw, ctxEcho: Coalesce(pcfView.Stamp, 0),
  ctxUseSeen: Coalesce(pcfView.UseSeq, 0), ctxWeaponSeen: Coalesce(pcfView.WeaponSeq, 0), ctxWeapon: sIn.wpn,
  ctxPX: sPl.x, ctxPY: sPl.y, ctxDoors: sPl.doors, ctxDoorAnimId: sPl.animId, ctxDoorAnimStep: sPl.animStep,
  ctxTaken: sPl.taken, ctxHazardTicks: sPl.hazardTicks,
  ctxAmmoRivet: sWp.ammo + sPl.ammo, ctxCooldown: sWp.cool, ctxWFrame: sWp.wframe,
  ctxHealth: sC.hp, ctxKills: ctxKills + sC.kills,
  ctxHurtTicks: If(sC.dmg > 0, 3, Max(0, ctxHurtTicks - 1)),
  ctxFlash: If(sC.dmg > 0 || ctxHurtTicks > 1, 1, sPl.picked, 2, 0),
  ctxMode: If(sC.died, "Dead", sPl.exit, "Exit", ctxMode),
  ctxMsg: If(sC.died, "You died. Press E to restart.", sPl.exit, "Exit reached. Press E to restart.",
             sPl.lockedMsg, "You need an access chip.", sPl.picked, "Picked up supplies.", ctxMsgTicks > 0, ctxMsg, ""),
  ctxMsgTicks: If(sC.died || sPl.exit, 9999, sPl.lockedMsg || sPl.picked, 40, Max(0, ctxMsgTicks - 1)),
  ctxEvents: Mid(sPl.ev & sWp.ev & {enemy_ev} & If(sC.dmg > 0, ";{SND['hurt']}", "") & If(sC.died, ";{SND['playerDeath']}", ""), 2),
  {enemy_commit}
}})
)
"""


def frame_formula(level):
    """pcfView.Frame: tick|px|py|weapon|wframe|flash|doors|sprites|events|echo|spawn"""
    enemy = " &\n    ".join(
        f'If({n} <= ctxSlots && ctxE{n}S > 0, "{n}," & ctxE{n}K & "," & ctxE{n}F & "," & Num(ctxE{n}X) & "," & Num(ctxE{n}Y) & "," & ctxE{n}S & ";")'
        for n in SLOTS)
    items = " &\n    ".join(
        f'If(Mid(ctxTaken, {i}, 1) = "0", "{100 + i},{t["kind"]},0,{t["x"]:.2f},{t["y"]:.2f},1;")'
        for i, t in enumerate(level.items, start=1)) or '""'
    return f"""
ctxTick & "|" & Num(ctxPX) & "|" & Num(ctxPY) & "|" & ctxWeapon & "|" & ctxWFrame & "|" & ctxFlash & "|" & ctxDoors & "|" &
    {enemy} &
    {items} &
    nfDecorSprites &
    "|" & ctxEvents & "|" & Text(ctxEcho, "0") & "|" & ctxSpawn & ":" & Num(nfStartYaw)
"""
