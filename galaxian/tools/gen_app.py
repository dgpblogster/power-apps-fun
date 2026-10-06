"""Generate the Galaxian canvas app YAML (App.pa.yaml, Screen1.pa.yaml, _EditorState.pa.yaml).

Run from the repo root:  python tools/gen_app.py
Writes into app/Src/. Repetitive controls (37 aliens, stars, flags, ship icons) are generated here.
Logical coordinates follow docs/01-game-spec.md: 160 columns x 240 lines; a column is 2 units wide.
"""
import os, sys, textwrap
sys.path.insert(0, os.path.dirname(__file__))
import sprites  # noqa: E402
import game_logic  # noqa: E402

_HERE = os.path.dirname(os.path.abspath(__file__))
# Output: canvas/Src in the published repo layout, app/Src in the local working layout.
OUT = os.environ.get("GALAXIAN_SRC") or next(
    (p for p in (os.path.join(_HERE, "..", "canvas", "Src"), os.path.join(_HERE, "..", "app", "Src")) if os.path.isdir(p)),
    os.path.join(_HERE, "..", "canvas", "Src"))

# ---------- formation slots: (slot, kind, col, row) ----------
SLOTS = []
for s, c in zip((1, 2, 3), (4, 6, 7)):
    SLOTS.append((s, "Commander", c, 1))
for i, c in enumerate(range(3, 9)):
    SLOTS.append((4 + i, "Hornet", c, 2))
for i, c in enumerate(range(2, 10)):
    SLOTS.append((10 + i, "Emissary", c, 3))
for i, c in enumerate(range(1, 11)):
    SLOTS.append((18 + i, "Drone", c, 4))
for i, c in enumerate(range(1, 11)):
    SLOTS.append((28 + i, "Drone", c, 5))
assert len(SLOTS) == 37
ALIVE_ALL = "1" * 37

# ---------- helpers ----------
def ind(text, n):
    pad = " " * n
    return "\n".join(pad + line if line.strip() else line for line in text.splitlines())

def block(prop, formula, level):
    """Multi-line formula as a block scalar. '=' goes on the first content line."""
    body = textwrap.dedent(formula).strip("\n")
    return f"{' ' * level}{prop}: |-\n{ind('=' + body, level + 2)}\n"

def props(level, **kv):
    out = ""
    for k, v in kv.items():
        out += f"{' ' * level}{k}: {v}\n"
    return out

def _a11y_label(name):
    """Human-readable accessible label derived from the control name (imgDiver3 -> 'Diver 3')."""
    import re as _re
    base = _re.sub(r"^(img|rec|lbl|btn|sld|tmr|star)", "", name)
    base = _re.sub(r"([a-z])([A-Z0-9])", r"\1 \2", base)
    return base.strip() or name

def control(name, ctype, level, properties, extra_lines=""):
    out = f"{' ' * level}- {name}:\n{' ' * (level + 4)}Control: {ctype}\n{' ' * (level + 4)}Properties:\n"
    out += properties
    # Accessibility: images are decorative game sprites (no tab stop); buttons and sliders get a label.
    plevel = level + 6
    if "AccessibleLabel" not in properties:
        if ctype.startswith("Image"):
            out += f"{' ' * plevel}AccessibleLabel: =\"{_a11y_label(name)}\"\n{' ' * plevel}TabIndex: =-1\n"
        elif ctype.startswith("Classic/Slider"):
            out += f"{' ' * plevel}AccessibleLabel: =\"{_a11y_label(name)}\"\n"
    out += extra_lines
    return out

P = 12  # property indent inside a top-level screen child

# ---------- App.pa.yaml ----------
sprite_lines = []
for name, (bmp, pal) in sprites.SPRITES.items():
    s = sprites.svg(bmp, sprites.PALETTES[pal])
    sprite_lines.append(f'{name} = "data:image/svg+xml;utf8," & EncodeUrl({sprites.powerfx_string(s)});')

formulas = """
// ---- geometry (logical 160 columns x 240 lines; see docs/01-game-spec.md) ----
nfScale = 2.5;
nfColW = nfScale * 2;
nfLeft = 283;
nfTop = 40;
nfAliveAll = "%s";
// ---- sprites (SVG data URIs, 8x8 logical pixels drawn 2:1) ----
%s
""" % (ALIVE_ALL, "\n".join(sprite_lines)) + game_logic.APP_FORMULAS

app_yaml = "App:\n  Properties:\n    BackEnabled: =false\n    StartScreen: =Screen1\n"
app_yaml += "    Formulas: |-\n" + ind("=" + formulas.strip("\n"), 6) + "\n"

# ---------- Screen1.pa.yaml ----------
on_visible = """
UpdateContext({
  ctxMode: "Attract", ctxTick: 0, ctxModeTicks: 0,
  ctxScore: 0, ctxHigh: 0, ctxLives: 3, ctxWave: 1, ctxLevel: 0, ctxBonus: false,
  ctxShipX: 80, ctxFire: false, ctxMisActive: false, ctxMisX: 80, ctxMisY: 201,
  ctxConvoyX: 0, ctxConvoyDir: 1, ctxAlive: nfAliveAll, ctxMinCol: 1, ctxMaxCol: 10,
  ctxPopupTicks: 0, ctxPopupX: 0, ctxPopupY: 0, ctxPopupText: "",
  ctxPaused: false
})
"""

tick = """
With(
  {
    tick: ctxTick + 1,
    playing: ctxMode = "Playing",
    convoyMoves: ctxMode = "Playing" || ctxMode = "Attract" || ctxMode = "Ready" || ctxMode = "GameOver"
  },
  With(
    {
      shipX: If(playing, Min(154, Max(6, ctxShipX + Max(-2, Min(2, sldMove.Value - ctxShipX)))), ctxShipX),
      convoyMin: -18 - (ctxMinCol - 1) * 12,
      convoyMax: 126 - (ctxMaxCol - 1) * 12,
      convoyXTry: ctxConvoyX + If(convoyMoves && Mod(tick, 2) = 0, ctxConvoyDir, 0)
    },
    With(
      {
        convoyX: Min(convoyMax, Max(convoyMin, convoyXTry)),
        convoyDir: If(convoyXTry > convoyMax, -1, If(convoyXTry < convoyMin, 1, ctxConvoyDir)),
        misLaunch: playing && ctxFire && !ctxMisActive,
        misMovedY: ctxMisY - 11
      },
      With(
        {
          misActive0: misLaunch || (ctxMisActive && misMovedY >= 26),
          misX: If(ctxMisActive, ctxMisX, shipX),
          misY: If(misLaunch, 192, If(ctxMisActive, misMovedY, 201))
        },
        With(
          {
            relX: misX - 22 - convoyX,
            relY: misY - 28
          },
          With(
            {
              col: If(relX >= 0 && Mod(relX, 12) < 8, Int(relX / 12) + 1, 0),
              row: If(misActive0 && playing && relY >= 0 && relY < 50 && Mod(relY, 10) < 8, Int(relY / 10) + 1, 0)
            },
            With(
              {
                slot: If(col >= 1 && col <= 10 && row >= 1,
                  Switch(row,
                    1, Switch(col, 4, 1, 6, 2, 7, 3, 0),
                    2, If(col >= 3 && col <= 8, 3 + (col - 2), 0),
                    3, If(col >= 2 && col <= 9, 9 + (col - 1), 0),
                    4, 17 + col,
                    5, 27 + col,
                    0),
                  0)
              },
              With(
                {
                  hit: slot > 0 && Mid(ctxAlive, slot, 1) = "1",
                  pts: Switch(row, 1, 60, 2, 50, 3, 40, 30)
                },
                With(
                  {
                    alive: If(hit, Left(ctxAlive, slot - 1) & "0" & Mid(ctxAlive, slot + 1, 37), ctxAlive),
                    score: Min(999990, ctxScore + If(hit, pts, 0))
                  },
                  With(
                    {
                      cols: Filter(Sequence(10),
                        Mid(alive, 17 + Value, 1) = "1" || Mid(alive, 27 + Value, 1) = "1" ||
                        (Value >= 2 && Value <= 9 && Mid(alive, 9 + Value - 1, 1) = "1") ||
                        (Value >= 3 && Value <= 8 && Mid(alive, 3 + Value - 2, 1) = "1") ||
                        (Value = 4 && Mid(alive, 1, 1) = "1") || (Value = 6 && Mid(alive, 2, 1) = "1") || (Value = 7 && Mid(alive, 3, 1) = "1")),
                      cleared: IsBlank(Find("1", alive)),
                      modeTicks0: Max(0, ctxModeTicks - 1)
                    },
                    With(
                      {
                        nextMode:
                          If(playing && cleared, "WaveClear",
                          If(ctxMode = "Ready" && modeTicks0 = 0, "Playing",
                          If(ctxMode = "WaveClear" && modeTicks0 = 0, "Ready",
                          If(ctxMode = "GameOver" && modeTicks0 = 0, "Attract",
                          ctxMode)))),
                        bonusNow: playing && !ctxBonus && score >= 5000
                      },
                      UpdateContext({
                        ctxTick: tick,
                        ctxMode: nextMode,
                        ctxModeTicks:
                          If(nextMode = ctxMode, modeTicks0,
                          Switch(nextMode, "WaveClear", 85, "Ready", 40, "Attract", 0, 0)),
                        ctxShipX: shipX,
                        ctxConvoyX: If(nextMode = "Ready" && ctxMode = "WaveClear", 0, convoyX),
                        ctxConvoyDir: convoyDir,
                        ctxFire: false,
                        ctxMisActive: misActive0 && !hit,
                        ctxMisX: misX,
                        ctxMisY: If(misActive0 && !hit, misY, 201),
                        ctxAlive: If(nextMode = "Ready" && ctxMode = "WaveClear", nfAliveAll, alive),
                        ctxMinCol: If(nextMode = "Ready" && ctxMode = "WaveClear", 1, If(hit && !cleared, Min(cols, Value), ctxMinCol)),
                        ctxMaxCol: If(nextMode = "Ready" && ctxMode = "WaveClear", 10, If(hit && !cleared, Max(cols, Value), ctxMaxCol)),
                        ctxWave: If(nextMode = "Ready" && ctxMode = "WaveClear", ctxWave + 1, ctxWave),
                        ctxScore: score,
                        ctxLives: If(bonusNow, Min(5, ctxLives + 1), ctxLives),
                        ctxBonus: ctxBonus || bonusNow,
                        ctxPopupTicks: If(hit && row = 1, 17, Max(0, ctxPopupTicks - 1)),
                        ctxPopupX: If(hit && row = 1, misX, ctxPopupX),
                        ctxPopupY: If(hit && row = 1, 28, ctxPopupY),
                        ctxPopupText: If(hit && row = 1, Text(pts), ctxPopupText)
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
"""

start_game = """
UpdateContext({
  ctxMode: "Ready", ctxModeTicks: 40,
  ctxScore: 0, ctxLives: 3, ctxWave: 1, ctxBonus: false,
  ctxShipX: 80, ctxFire: false, ctxMisActive: false, ctxMisX: 80, ctxMisY: 201,
  ctxConvoyX: 0, ctxConvoyDir: 1, ctxAlive: nfAliveAll, ctxMinCol: 1, ctxMaxCol: 10,
  ctxPopupTicks: 0, ctxPaused: false
});
Reset(sldMove)
"""

on_visible = game_logic.ON_VISIBLE
tick = game_logic.TICK
start_game = game_logic.START_GAME

children = ""

# --- playfield background ---
children += control("recPlayfield", "Rectangle@2.3.0", 6, props(P,
    Fill="=RGBA(0, 0, 0, 1)", X="=nfLeft", Y="=nfTop", Width="=160 * nfColW", Height="=240 * nfScale",
    BorderThickness="=0"))

# --- starfield: 32 single-pixel stars in colour columns, scrolling down 1 line per tick ---
star_colours = ["RGBA(96, 128, 240, 1)", "RGBA(64, 192, 160, 1)", "RGBA(240, 144, 96, 1)", "RGBA(224, 224, 224, 1)"]
import random
rnd = random.Random(1979)
for i in range(1, 33):
    colx = rnd.randrange(0, 160)
    y0 = rnd.randrange(0, 240)
    colour = star_colours[i % 4]
    children += control(f"star{i:02d}", "Rectangle@2.3.0", 6, props(P,
        Fill=f"={colour}",
        X=f"=nfLeft + {colx} * nfColW",
        Y=f"=nfTop + Mod({y0} + ctxTick, 240) * nfScale",
        Width="=nfColW", Height="=nfScale", BorderThickness="=0",
        Visible=f"=Mod(ctxTick + {i}, 9) <> 0"))

# --- formation: 37 alien images ---
for slot, kind, col, row in SLOTS:
    phase = (slot * 3) % 5
    children += control(f"alien{slot:02d}", "Image@2.2.3", 6, props(P,
        Image=f"=If(Mod(ctxFrame + {phase}, 2) = 0, nfSpr{kind}A, nfSpr{kind}B)",
        ImagePosition="=ImagePosition.Fit",
        X=f"=nfLeft + (22 + {(col - 1) * 12} + ctxConvoyX) * nfColW",
        Y=f"=nfTop + {28 + (row - 1) * 10} * nfScale",
        Width="=8 * nfColW", Height="=8 * nfScale",
        Visible=f'=Mid(ctxAlive, {slot}, 1) = "1" && ctxMode <> "Attract"'))

# --- player ship, missile ---
children += control("imgShip", "Image@2.2.3", 6, props(P,
    Image="=nfSprShip", ImagePosition="=ImagePosition.Fit",
    X="=nfLeft + (ctxShipX - 4) * nfColW", Y="=nfTop + 205 * nfScale",
    Width="=8 * nfColW", Height="=8 * nfScale",
    Visible='=ctxMode = "Playing" || ctxMode = "Ready" || ctxMode = "WaveClear" || ctxMode = "Attract"'))
children += control("recMissile", "Rectangle@2.3.0", 6, props(P,
    Fill="=RGBA(240, 240, 240, 1)",
    X="=nfLeft + ctxMisX * nfColW - nfColW / 2", Y="=nfTop + ctxMisY * nfScale",
    Width="=nfColW", Height="=4 * nfScale", BorderThickness="=0",
    Visible='=ctxMode = "Playing"'))

# --- HUD top row ---
children += control("lblLevel", "Label@2.5.1", 6, props(P,
    Text='=If(ctxLevel = 10, "B", Text(ctxLevel))', Color="=RGBA(80, 128, 240, 1)",
    Font="=Font.'Courier New'", FontWeight="=FontWeight.Bold", Size="=22",
    X="=nfLeft + 4 * nfColW", Y="=nfTop + 14 * nfScale", Width="=12 * nfColW", Height="=12 * nfScale",
    PaddingTop="=0", PaddingBottom="=0", PaddingLeft="=0", PaddingRight="=0", Wrap="=false"))
children += control("lblScore", "Label@2.5.1", 6, props(P,
    Text='=Text(ctxScore, "00")', Color="=RGBA(240, 224, 64, 1)",
    Font="=Font.'Courier New'", FontWeight="=FontWeight.Bold", Size="=22",
    X="=nfLeft + 24 * nfColW", Y="=nfTop + 14 * nfScale", Width="=48 * nfColW", Height="=12 * nfScale",
    PaddingTop="=0", PaddingBottom="=0", PaddingLeft="=0", PaddingRight="=0", Wrap="=false"))
for i in range(1, 5):
    children += control(f"imgLife{i}", "Image@2.2.3", 6, props(P,
        Image="=nfSprShip", ImagePosition="=ImagePosition.Fit",
        X=f"=nfLeft + ({72 + (i - 1) * 10}) * nfColW", Y="=nfTop + 16 * nfScale",
        Width="=8 * nfColW", Height="=8 * nfScale",
        Visible=f'=ctxMode <> "Attract" && ctxLives - 1 >= {i}'))
for i in range(1, 17):
    children += control(f"imgFlag{i:02d}", "Image@2.2.3", 6, props(P,
        Image="=nfSprFlag", ImagePosition="=ImagePosition.Fit",
        X=f"=nfLeft + ({150 - (i - 1) * 6}) * nfColW", Y="=nfTop + 16 * nfScale",
        Width="=8 * nfColW", Height="=8 * nfScale",
        Visible=f'=ctxMode <> "Attract" && Min(ctxWave, 16) >= {i}'))

# --- bottom text ---
children += control("lblHigh", "Label@2.5.1", 6, props(P,
    Text='=Text(ctxHigh, "00")', Color="=RGBA(176, 176, 176, 1)",
    Font="=Font.'Courier New'", FontWeight="=FontWeight.Bold", Size="=18",
    X="=nfLeft + 4 * nfColW", Y="=nfTop + 218 * nfScale", Width="=40 * nfColW", Height="=12 * nfScale",
    PaddingTop="=0", PaddingBottom="=0", PaddingLeft="=0", PaddingRight="=0", Wrap="=false"))
children += control("lblFooter", "Label@2.5.1", 6, props(P,
    Text='="HOMAGE 2026  NOT AFFILIATED WITH ATARI OR BANDAI NAMCO"', Color="=RGBA(176, 176, 176, 1)",
    Font="=Font.'Courier New'", Size="=11",
    X="=nfLeft + 48 * nfColW", Y="=nfTop + 220 * nfScale", Width="=108 * nfColW", Height="=10 * nfScale",
    PaddingTop="=0", PaddingBottom="=0", PaddingLeft="=0", PaddingRight="=0", Wrap="=false",
    Visible='=ctxMode = "Attract" || ctxMode = "GameOver"'))

# --- centre messages ---
children += control("lblTitle", "Label@2.5.1", 6, props(P,
    Text='="GALAXIAN"', Color="=RGBA(176, 160, 240, 1)", Align="=Align.Center",
    Font="=Font.'Courier New'", FontWeight="=FontWeight.Bold", Size="=56",
    X="=nfLeft", Y="=nfTop + 112 * nfScale", Width="=160 * nfColW", Height="=26 * nfScale",
    PaddingTop="=0", PaddingBottom="=0", Wrap="=false",
    Visible='=ctxMode = "Attract"'))
children += control("lblMessage", "Label@2.5.1", 6, props(P,
    Text='=Switch(ctxMode, "Ready", "PLAYER ONE", "GameOver", "GAME OVER", "")',
    Color="=RGBA(176, 160, 240, 1)", Align="=Align.Center",
    Font="=Font.'Courier New'", FontWeight="=FontWeight.Bold", Size="=36",
    X="=nfLeft", Y="=nfTop + 116 * nfScale", Width="=160 * nfColW", Height="=18 * nfScale",
    PaddingTop="=0", PaddingBottom="=0", Wrap="=false",
    Visible='=ctxMode = "Ready" || ctxMode = "GameOver"'))
children += control("lblPopup", "Label@2.5.1", 6, props(P,
    Text="=ctxPopupText", Color="=RGBA(240, 224, 64, 1)", Align="=Align.Center",
    Font="=Font.'Courier New'", FontWeight="=FontWeight.Bold", Size="=14",
    X="=nfLeft + (ctxPopupX - 8) * nfColW", Y="=nfTop + ctxPopupY * nfScale", Width="=16 * nfColW", Height="=8 * nfScale",
    PaddingTop="=0", PaddingBottom="=0", PaddingLeft="=0", PaddingRight="=0", Wrap="=false",
    Visible="=ctxPopupTicks > 0"))

# --- input: tap-to-fire overlay over the upper playfield ---
children += control("btnFireZone", "Classic/Button@2.2.0", 6, props(P,
    Text='=""', Fill="=RGBA(0, 0, 0, 0)", HoverFill="=RGBA(0, 0, 0, 0)", PressedFill="=RGBA(255, 255, 255, 0.05)",
    BorderThickness="=0", FocusedBorderThickness="=0",
    X="=nfLeft", Y="=nfTop + 26 * nfScale", Width="=160 * nfColW", Height="=170 * nfScale",
    Visible='=ctxMode = "Playing"') + block("OnSelect", 'If(ctxMode = "Playing" && !ctxMisActive, UpdateContext({ctxMisActive: true, ctxMisX: ctxShipX, ctxMisY: 192}))', P))

# --- controls strip under the playfield ---
children += control("sldMove", "Classic/Slider@2.1.0", 6, props(P,
    Min="=6", Max="=154", Default="=80", ShowValue="=false",
    HandleFill="=RGBA(240, 80, 160, 1)", RailFill="=RGBA(48, 48, 64, 1)", ValueFill="=RGBA(48, 48, 64, 1)",
    HandleActiveFill="=RGBA(240, 160, 200, 1)", RailHoverFill="=RGBA(64, 64, 80, 1)", ValueHoverFill="=RGBA(64, 64, 80, 1)",
    X="=nfLeft + 8 * nfColW", Y="=nfTop + 240 * nfScale + 12", Width="=104 * nfColW", Height="=40"))
children += control("btnFire", "Classic/Button@2.2.0", 6, props(P,
    Text='="FIRE"', Color="=RGBA(0, 0, 0, 1)", Fill="=RGBA(240, 80, 160, 1)", HoverFill="=RGBA(250, 120, 180, 1)",
    PressedFill="=RGBA(200, 60, 130, 1)", HoverColor="=RGBA(0, 0, 0, 1)", PressedColor="=RGBA(0, 0, 0, 1)",
    Font="=Font.'Courier New'", FontWeight="=FontWeight.Bold", Size="=20", BorderThickness="=0",
    RadiusTopLeft="=24", RadiusTopRight="=24", RadiusBottomLeft="=24", RadiusBottomRight="=24",
    X="=nfLeft + 120 * nfColW", Y="=nfTop + 240 * nfScale + 8", Width="=40 * nfColW", Height="=48") + block("OnSelect", 'If(ctxMode = "Playing" && !ctxMisActive, UpdateContext({ctxMisActive: true, ctxMisX: ctxShipX, ctxMisY: 192}))', P))

console_keys = [
    ("btnStart", "START", 'ctxMode = "Attract" || ctxMode = "GameOver"', start_game),
    ("btnSelect", "SELECT", 'ctxMode = "Attract" || ctxMode = "GameOver"', 'UpdateContext({ctxLevel: Mod(ctxLevel + 1, 11)})'),
    ("btnOption", "OPTION", 'false', 'false'),
    ("btnPause", "PAUSE", 'ctxMode = "Playing"', 'UpdateContext({ctxPaused: !ctxPaused})'),
    ("btnReset", "RESET", 'true', 'UpdateContext({ctxMode: "Attract", ctxModeTicks: 0, ctxLevel: 0, ctxPaused: false, ctxAlive: nfAliveAll, ctxMinCol: 1, ctxMaxCol: 10, ctxConvoyX: 0})'),
]
for i, (name, text, enabled, action) in enumerate(console_keys):
    children += control(name, "Classic/Button@2.2.0", 6, props(P,
        Text=f'="{text}"', Color="=RGBA(220, 200, 120, 1)", Fill="=RGBA(96, 72, 32, 1)", HoverFill="=RGBA(120, 92, 44, 1)",
        PressedFill="=RGBA(72, 54, 24, 1)", HoverColor="=RGBA(255, 240, 180, 1)", PressedColor="=RGBA(220, 200, 120, 1)",
        DisabledFill="=RGBA(48, 40, 28, 1)", DisabledColor="=RGBA(120, 110, 90, 1)",
        Font="=Font.'Courier New'", FontWeight="=FontWeight.Bold", Size="=12", BorderThickness="=0",
        RadiusTopLeft="=4", RadiusTopRight="=4", RadiusBottomLeft="=4", RadiusBottomRight="=4",
        X=f"=nfLeft + {8 + i * 30} * nfColW", Y="=nfTop + 240 * nfScale + 64", Width="=26 * nfColW", Height="=36",
        DisplayMode=f"=If({enabled}, DisplayMode.Edit, DisplayMode.Disabled)") + block("OnSelect", action, P))

# --- divers (7 pooled slots) ---
for n in range(1, 8):
    children += control(f"imgDiver{n}", "Image@2.2.3", 6, props(P,
        Image=(f'=Switch(Index(ctxDivers, {n}).Kind, '
               f'"Commander", If(ctxFrame = 0, nfSprCommanderA, nfSprCommanderB), '
               f'"Hornet", If(ctxFrame = 0, nfSprHornetA, nfSprHornetB), '
               f'"Emissary", If(ctxFrame = 0, nfSprEmissaryA, nfSprEmissaryB), '
               f'If(ctxFrame = 0, nfSprDroneA, nfSprDroneB))'),
        ImagePosition="=ImagePosition.Fit",
        X=f"=nfLeft + (Index(ctxDivers, {n}).X - 4) * nfColW",
        Y=f"=nfTop + (Index(ctxDivers, {n}).Y - 4) * nfScale",
        Width="=8 * nfColW", Height="=8 * nfScale",
        Visible=f'=Index(ctxDivers, {n}).Active && ctxMode = "Playing"'))

# --- bombs (7 pooled slots) ---
for n in range(1, 8):
    children += control(f"recBomb{n}", "Rectangle@2.3.0", 6, props(P,
        Fill="=RGBA(240, 240, 240, 1)",
        X=f"=nfLeft + Index(ctxBombs, {n}).X * nfColW - nfColW / 2",
        Y=f"=nfTop + Index(ctxBombs, {n}).Y * nfScale",
        Width="=nfColW", Height="=4 * nfScale", BorderThickness="=0",
        Visible=f'=Index(ctxBombs, {n}).Active && ctxMode = "Playing"'))

# --- explosions ---
children += control("imgExplode", "Image@2.2.3", 6, props(P,
    Image="=If(ctxExplTicks > 5, nfSprExplode1, If(ctxExplTicks > 2, nfSprExplode2, nfSprExplode3))",
    ImagePosition="=ImagePosition.Fit",
    X="=nfLeft + (ctxExplX - 4) * nfColW", Y="=nfTop + (ctxExplY - 4) * nfScale",
    Width="=8 * nfColW", Height="=8 * nfScale",
    Visible="=ctxExplTicks > 0"))
children += control("imgShipExplode", "Image@2.2.3", 6, props(P,
    Image="=If(ctxModeTicks > 9, nfSprExplode1, If(ctxModeTicks > 4, nfSprExplode2, nfSprExplode3))",
    ImagePosition="=ImagePosition.Fit",
    X="=nfLeft + (ctxShipX - 8) * nfColW", Y="=nfTop + 199 * nfScale",
    Width="=16 * nfColW", Height="=16 * nfScale",
    Visible='=ctxMode = "Dying"'))

# --- diagnostics: measured ticks per second ---
children += control("lblTps", "Label@2.5.1", 6, props(P,
    Text='=If(ctxTick > 20, Text(Round(ctxTick / Max(1, DateDiff(ctxStartTime, Now(), TimeUnit.Milliseconds) / 1000), 1)) & " tps", "")',
    Color="=RGBA(96, 96, 112, 1)", Font="=Font.'Courier New'", Size="=10", Align="=Align.Right",
    X="=nfLeft + 160 * nfColW - 120", Y="=nfTop + 240 * nfScale + 70", Width="=120", Height="=20",
    PaddingTop="=0", PaddingBottom="=0", PaddingLeft="=0", PaddingRight="=0", Wrap="=false"))

# --- game loop timer ---
children += control("tmrGame", "Timer@2.1.0", 6, props(P,
    AutoStart="=true", Repeat="=true", AutoPause="=false", Duration="=50",
    Start="=!ctxPaused", Visible="=false",
    X="=nfLeft + 160 * nfColW + 20", Y="=nfTop", Width="=120", Height="=24") + block("OnTimerEnd", tick, P))

screen_yaml = "Screens:\n  Screen1:\n    Properties:\n      Fill: =RGBA(8, 8, 12, 1)\n      LoadingSpinnerColor: =RGBA(176, 160, 240, 1)\n"
screen_yaml += block("OnVisible", on_visible, 6)
screen_yaml += "    Children:\n" + children

editor_yaml = "EditorState:\n  ScreensOrder:\n    - Screen1\n"

os.makedirs(OUT, exist_ok=True)
for fname, content in (("App.pa.yaml", app_yaml), ("Screen1.pa.yaml", screen_yaml), ("_EditorState.pa.yaml", editor_yaml)):
    with open(os.path.join(OUT, fname), "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print(f"wrote {fname} ({len(content)} chars)")
