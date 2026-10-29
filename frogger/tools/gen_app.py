"""Generate the canvas app YAML (App.pa.yaml, Screen1.pa.yaml, _EditorState.pa.yaml) for Frogger.

Run from the project root:  python tools/gen_app.py
Writes to canvas/Src (override with FROGGER_SRC).

Geometry (docs/01-game-spec.md section 2): 160 columns x 240 lines, nfScale screen px per line, a column is
2 * nfScale px. Rows 0..11 from the home bank to the start row, 16 lines each, starting at line 24.
"""
import os, sys, textwrap, re
sys.path.insert(0, os.path.dirname(__file__))
import sprites       # noqa: E402
import game_logic    # noqa: E402
import sounds        # noqa: E402

_HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("FROGGER_SRC") or os.path.join(_HERE, "..", "canvas", "Src")

# ---------- helpers (validated against the Canvas Authoring service) ----------
def ind(text, n):
    pad = " " * n
    return "\n".join(pad + line if line.strip() else line for line in text.splitlines())

def block(prop, formula, level):
    """Multi-line formula as a block scalar; '=' goes on the first content line."""
    body = textwrap.dedent(formula).strip("\n")
    return f"{' ' * level}{prop}: |-\n{ind('=' + body, level + 2)}\n"

def props(level, **kv):
    return "".join(f"{' ' * level}{k}: {v}\n" for k, v in kv.items())

def _a11y_label(name):
    base = re.sub(r"^(img|rec|lbl|btn|sld|tmr|aud)", "", name)
    base = re.sub(r"([a-z])([A-Z0-9])", r"\1 \2", base)
    return base.strip() or name

def control(name, ctype, level, properties, extra_lines=""):
    """Control name at `level`, Control:/Properties: at level+4, property values at level+6."""
    out = f"{' ' * level}- {name}:\n{' ' * (level + 4)}Control: {ctype}\n{' ' * (level + 4)}Properties:\n"
    out += properties
    plevel = level + 6
    if "AccessibleLabel" not in properties:
        if ctype.startswith("Image"):
            out += f"{' ' * plevel}AccessibleLabel: =\"{_a11y_label(name)}\"\n{' ' * plevel}TabIndex: =-1\n"
        elif ctype.startswith("Classic/Slider") or ctype.startswith("Audio"):
            out += f"{' ' * plevel}AccessibleLabel: =\"{_a11y_label(name)}\"\n"
    out += extra_lines
    return out

P = 12  # property indent for a top-level screen child (name at 6, Properties: at 10)

BORDER = "RGBA(0, 67, 1, 1)"      # dark green #004301
WATER = "RGBA(50, 31, 255, 1)"    # #321FFF
RED = "RGBA(255, 0, 0, 1)"
ORANGE = "RGBA(255, 137, 0, 1)"
TEXT_GREEN = "RGBA(64, 192, 64, 1)"
TEXT_BLUE = "RGBA(128, 192, 255, 1)"
MONO = "Font.'Courier New'"

# ---------- named formulas ----------
formulas = """
nfScale = 2.5;
nfCol = 2 * nfScale;
nfLine = nfScale;
nfLeft = (1366 - 160 * nfCol) / 2;
nfTop = 24;
nfRowY = 24;
// ---- sprites and strips ----
""" + "\n".join(sprites.formula_lines()) + "\n" + "\n".join(sounds.formula_lines()) + "\n" + game_logic.APP_FORMULAS

app_yaml = "App:\n  Properties:\n    BackEnabled: =false\n    StartScreen: =Screen1\n"
app_yaml += "    Formulas: |-\n" + ind("=" + formulas.strip("\n"), 6) + "\n"

def col(x):      # logical column -> screen X formula
    return f"nfLeft + ({x}) * nfCol"

def line(y):     # logical line -> screen Y formula
    return f"nfTop + ({y}) * nfLine"

def label(name, text, color, size, x, y, w, h, align="Align.Left", visible="true", extra=None):
    kv = dict(Text=text, Color=f"={color}", Align=f"={align}", Font=f"={MONO}", FontWeight="=FontWeight.Bold",
              Size=f"={str(size).lstrip('=')}", X=f"={x}", Y=f"={y}", Width=f"={w}", Height=f"={h}",
              PaddingTop="=0", PaddingBottom="=0", PaddingLeft="=0", PaddingRight="=0", Wrap="=false",
              Visible=f"={visible}")
    if extra:
        kv.update(extra)
    return control(name, "Label@2.5.1", 6, props(P, **kv))

children = ""

# ---------- playfield background: one image (bank, water, sidewalk, road) ----------
children += control("imgField", "Image@2.2.3", 6, props(P,
    Image="=Switch(Mod(ctxLevel - 1, 3), 0, nfImgField1, 1, nfImgField2, nfImgField3)", ImagePosition="=ImagePosition.Fill",
    X="=nfLeft", Y="=nfTop", Width="=160 * nfCol", Height="=240 * nfLine"))

# ---------- time band ----------
children += label("lblTime", '="TIME"', RED, "=18", col(2), line(202), "16 * nfCol", "12 * nfLine")
children += control("recTimeBand", "Rectangle@2.3.0", 6, props(P,
    Fill=f"=If(ctxTime <= 100, {RED}, {ORANGE})",
    X=f"={col(44)}", Y=f"={line(204)}", Width="=Max(0, 97 * ctxTime / nfTimeTicks) * nfCol", Height="=8 * nfLine",
    BorderThickness="=0"))

# ---------- HUD ----------
children += label("lblSpeed", '=If(ctxFast, "FAST", "SLOW")', TEXT_GREEN, "=18", col(4), line(6), "40 * nfCol", "12 * nfLine")
children += label("lblScore", '="1UP " & If(ctxPlayer = 1, ctxScore, ctxScoreP2)', TEXT_BLUE, "=18", col(4), line(222), "60 * nfCol", "12 * nfLine")
children += label("lblScore2", '="2UP " & If(ctxPlayer = 2, ctxScore, ctxScoreP2)', TEXT_BLUE, "=18", col(96), line(222), "60 * nfCol", "12 * nfLine",
                  align="Align.Right", visible='ctxTwoPlayer && ctxMode <> "Attract"')
children += label("lblTurn", '=If(ctxMode = "Attract", If(ctxTwoPlayer, "2 PLAYERS", "1 PLAYER"), ctxPlayer & " UP")', TEXT_GREEN, "=18",
                  col(60), line(222), "40 * nfCol", "12 * nfLine", align="Align.Center",
                  visible='ctxMode = "Attract" || (ctxTwoPlayer && (ctxMode = "Jingle" || ctxMode = "GameOver"))')
children += label("lblHigh", '="HI " & ctxHigh', TEXT_BLUE, "=18", col(96), line(222), "60 * nfCol", "12 * nfLine",
                  align="Align.Right", visible='ctxMode = "Attract" || (ctxMode = "GameOver" && !ctxTwoPlayer)')
for n in range(1, 9):
    children += control(f"imgLife{n}", "Image@2.2.3", 6, props(P,
        Image="=nfSprLife", ImagePosition="=ImagePosition.Fit",
        X=f"={col(156 - 6 * n)}", Y=f"={line(8)}", Width="=4 * nfCol", Height="=8 * nfLine",
        Visible=f"=ctxLives - 1 >= {n}"))

# ---------- lane objects: 45 fixed Image controls, scalar formulas over ctxOff{L} and ctxN{L} ----------
KIND_IMAGE = {
    "Log": "nfSprLogM", "LogL": "nfSprLogL", "LogS": "nfSprLogS",
    "Pair": "If(ctxFrame = 0, nfSprPairA, nfSprPairB)", "Trio": "If(ctxFrame = 0, nfSprTrioA, nfSprTrioB)",
    "Car": "nfSprCar", "Car2": "nfSprCar2", "Racer": "nfSprRacer", "Dozer": "nfSprDozer",
}
# dive phases (ticks): pairs 85-tick cycle, trios 43-tick cycle; "gone" hides the group (spec section 6)
PAIR_DIVE = ("If(ctxDivePair < 27, {up}, If(ctxDivePair < 43, nfSprPairHalf, If(ctxDivePair < 59, nfSprPairDeep, "
             "If(ctxDivePair < 69, nfSprPairDeep, nfSprPairHalf))))")
TRIO_DIVE = ("If(ctxDiveTrio < 8, nfSprTrioHalf, If(ctxDiveTrio < 19, nfSprTrioDeep, If(ctxDiveTrio < 27, nfSprTrioHalf, {up})))")

def lane_image(L, i, kind):
    base = KIND_IMAGE[kind]
    if L == 1 and i == 1:
        return f"If(ctxGatorOn, nfSprGator, {base})"
    if L == 3 and i == 1:
        return f"If(ctxLevel >= 3, If(ctxFrame = 0, nfSprLogSnakeA, nfSprLogSnakeB), {base})"
    if L == 4 and i == 1:
        return f"If(ctxLadyOn, nfSprLogLady, {base})"
    if kind == "Pair":
        return f"If(ctxN2 = {i}, {PAIR_DIVE.format(up=base)}, {base})"
    if kind == "Trio":
        return f"If(ctxN5 = {i}, {TRIO_DIVE.format(up=base)}, {base})"
    return base

def lane_visible(L, i, kind):
    if kind == "Pair":
        return f"ctxN2 >= {i} && !(ctxN2 = {i} && ctxDivePair >= 53 && ctxDivePair <= 58)"
    if kind == "Trio":
        return f"ctxN5 >= {i} && !(ctxN5 = {i} && ctxDiveTrio >= 13 && ctxDiveTrio <= 15)"
    return f"ctxN{L} >= {i}"

s_no = 0
for L, row, d, spd, w, kind in game_logic.LANES:
    loop = game_logic.loop_of(w)
    for i in range(1, 6):
        s_no += 1
        children += control(f"imgLane{s_no:02d}", "Image@2.2.3", 6, props(P,
            ImagePosition="=ImagePosition.Fit",
            X=f"=nfLeft + (Mod({i - 1} * {loop} / Max(1, ctxN{L}) + ctxOff{L}, {loop}) - {w}) * nfCol",
            Y=f"={line(24 + 16 * row)}",
            Width=f"={w} * nfCol", Height="=16 * nfLine",
            Visible=f"={lane_visible(L, i, kind)}") + block("Image", lane_image(L, i, kind), P))

# ---------- sidewalk snake (level 3+) ----------
children += control("imgSnake", "Image@2.2.3", 6, props(P,
    Image="=If(ctxSnakeDir > 0, If(ctxFrame = 0, nfSprSnakeRA, nfSprSnakeRB), If(ctxFrame = 0, nfSprSnakeLA, nfSprSnakeLB))",
    ImagePosition="=ImagePosition.Fit",
    X="=nfLeft + ctxSnakeX * nfCol", Y=f"={line(120)}", Width="=16 * nfCol", Height="=16 * nfLine",
    Visible="=ctxLevel >= 3"))

# ---------- bay creature: fly on odd levels, alligator on even ----------
children += control("imgBayFly", "Image@2.2.3", 6, props(P,
    Image="=nfSprFly", ImagePosition="=ImagePosition.Fit",
    X="=nfLeft + (16 + (ctxBayCursor - 1) * 32 - 4) * nfCol", Y=f"={line(24)}", Width="=8 * nfCol", Height="=16 * nfLine",
    Visible='=(ctxMode = "Playing" || ctxMode = "Jingle") && Mod(ctxLevel, 2) = 1 && ctxBayTimer <= 36 && Mid(ctxBays, ctxBayCursor, 1) = "0"'))
children += control("imgBayGator", "Image@2.2.3", 6, props(P,
    Image="=If(ctxBayTimer < 27, nfSprBaySnout, nfSprBayJaws)", ImagePosition="=ImagePosition.Fit",
    X="=nfLeft + (16 + (ctxBayCursor - 1) * 32 - 6) * nfCol", Y=f"={line(24)}", Width="=12 * nfCol", Height="=16 * nfLine",
    Visible='=(ctxMode = "Playing" || ctxMode = "Jingle") && Mod(ctxLevel, 2) = 0 && ctxBayTimer <= 58 && Mid(ctxBays, ctxBayCursor, 1) = "0"'))

# ---------- edge masks: hide lane objects outside the playfield ----------
children += control("recMaskL", "Rectangle@2.3.0", 6, props(P,
    Fill=f"={BORDER}", X="=0", Y="=nfTop", Width="=nfLeft", Height="=240 * nfLine", BorderThickness="=0"))
children += control("recMaskR", "Rectangle@2.3.0", 6, props(P,
    Fill=f"={BORDER}", X="=nfLeft + 160 * nfCol", Y="=nfTop", Width="=1366 - nfLeft - 160 * nfCol", Height="=240 * nfLine", BorderThickness="=0"))

# ---------- home bay stamps ----------
for b, cx in enumerate((16, 48, 80, 112, 144), start=1):
    children += control(f"imgBay{b}", "Image@2.2.3", 6, props(P,
        Image="=nfSprFrogHome", ImagePosition="=ImagePosition.Fit",
        X=f"={col(cx - 4)}", Y=f"={line(24)}", Width="=8 * nfCol", Height="=16 * nfLine",
        Visible=f'=Mid(ctxBays, {b}, 1) = "1"'))

# ---------- frog ----------
FROG_IMAGE = """
If(ctxMode = "Dying", If(ctxDeathKind = "Squash", nfSprSquash, nfSprDrown),
  Switch(ctxFrogDir,
    "U", If(ctxHopTicks > 0, nfSprFrogUHop, nfSprFrogU),
    "D", If(ctxHopTicks > 0, nfSprFrogDHop, nfSprFrogD),
    "L", If(ctxHopTicks > 0, nfSprFrogLHop, nfSprFrogL),
    If(ctxHopTicks > 0, nfSprFrogRHop, nfSprFrogR)))
"""
children += control("imgFrog", "Image@2.2.3", 6, props(P,
    ImagePosition="=ImagePosition.Fit",
    X="=nfLeft + Round(ctxFrogX, 0) * nfCol", Y="=nfTop + (nfRowY + 16 * ctxFrogRow) * nfLine",
    Width="=8 * nfCol", Height="=16 * nfLine",
    Visible='=ctxMode = "Playing" || ctxMode = "Jingle" || (ctxMode = "Dying" && ctxModeTicks > 20)') + block("Image", FROG_IMAGE, P))

# ---------- lady frog riding on the frog ----------
children += control("imgLady", "Image@2.2.3", 6, props(P,
    Image="=nfSprLady", ImagePosition="=ImagePosition.Fit",
    X="=nfLeft + Round(ctxFrogX, 0) * nfCol", Y="=nfTop + (nfRowY + 16 * ctxFrogRow) * nfLine - 4 * nfLine",
    Width="=8 * nfCol", Height="=16 * nfLine",
    Visible='=ctxHasLady && (ctxMode = "Playing" || ctxMode = "Jingle")'))

# ---------- messages ----------
children += label("lblMessage",
    '=Switch(ctxMode, "Attract", "PRESS START", "GameOver", "GAME OVER", "Dying", If(ctxDeathKind = "TimeOut", "TIME OUT", ""), "")',
    "RGBA(255, 255, 255, 1)", "=26", "nfLeft", line(121), "160 * nfCol", "14 * nfLine", align="Align.Center",
    visible='ctxMode <> "Playing" && ctxMode <> "Jingle"')
children += label("lblCredit", '="A homage built in Power Fx. Not affiliated with Konami, Sega, Parker Brothers or Atari."',
    "RGBA(120, 140, 120, 1)", "=10", "nfLeft", "nfTop + 240 * nfLine + 4", "160 * nfCol - 130", "20")
children += label("lblTps",
    '="L" & ctxLevel & If(ctxTick > 20, "  " & Text(Round(ctxTick / Max(1, DateDiff(ctxStartTime, Now(), TimeUnit.Milliseconds) / 1000), 1)) & " tps", "")',
    "RGBA(120, 140, 120, 1)", "=10", "nfLeft + 160 * nfCol - 130", "nfTop + 240 * nfLine + 4", "130", "20", align="Align.Right")

# ---------- input: tap zones around the frog (transparent) ----------
def zone(name, hop, x, y, w, h):
    return control(name, "Classic/Button@2.2.0", 6, props(P,
        Text='=""', Fill="=RGBA(0, 0, 0, 0)", HoverFill="=RGBA(255, 255, 255, 0.04)", PressedFill="=RGBA(255, 255, 255, 0.12)",
        BorderThickness="=0", FocusedBorderThickness="=0", RadiusTopLeft="=0", RadiusTopRight="=0",
        RadiusBottomLeft="=0", RadiusBottomRight="=0",
        X=f"={x}", Y=f"={y}", Width=f"={w}", Height=f"={h}",
        Visible='=ctxMode = "Playing"') + block("OnSelect", f'UpdateContext({{ctxHopQueued: "{hop}"}})', P))
children += zone("btnZoneUp", "U", "nfLeft", line(24), "160 * nfCol", "16 * ctxFrogRow * nfLine")
children += zone("btnZoneDown", "D", "nfLeft", "nfTop + (nfRowY + 16 * (ctxFrogRow + 1)) * nfLine",
                 "160 * nfCol", "16 * (11 - ctxFrogRow) * nfLine")
children += zone("btnZoneLeft", "L", "nfLeft", "nfTop + (nfRowY + 16 * ctxFrogRow) * nfLine",
                 "Max(0, Round(ctxFrogX, 0)) * nfCol", "16 * nfLine")
children += zone("btnZoneRight", "R", "nfLeft + (Round(ctxFrogX, 0) + 8) * nfCol", "nfTop + (nfRowY + 16 * ctxFrogRow) * nfLine",
                 "Max(0, 152 - Round(ctxFrogX, 0)) * nfCol", "16 * nfLine")

# ---------- input: hop cross to the right of the playfield ----------
def hop_button(name, text, hop, dx, dy):
    return control(name, "Classic/Button@2.2.0", 6, props(P,
        Text=f'="{text}"', Color="=RGBA(0, 0, 0, 1)", Fill="=RGBA(64, 192, 64, 1)", HoverFill="=RGBA(96, 220, 96, 1)",
        PressedFill="=RGBA(40, 150, 40, 1)", HoverColor="=RGBA(0, 0, 0, 1)", PressedColor="=RGBA(0, 0, 0, 1)",
        DisabledFill="=RGBA(40, 80, 40, 1)", DisabledColor="=RGBA(20, 40, 20, 1)",
        Font=f"={MONO}", FontWeight="=FontWeight.Bold", Size="=22", BorderThickness="=0",
        RadiusTopLeft="=10", RadiusTopRight="=10", RadiusBottomLeft="=10", RadiusBottomRight="=10",
        X=f"=nfLeft + 160 * nfCol + 30 + {dx} * 76", Y=f"=nfTop + 120 * nfLine - 38 + {dy} * 76", Width="=70", Height="=70",
        DisplayMode='=If(ctxMode = "Playing", DisplayMode.Edit, DisplayMode.Disabled)') +
        block("OnSelect", f'UpdateContext({{ctxHopQueued: "{hop}"}})', P))
children += hop_button("btnUp", "^", "U", 1, -1)
children += hop_button("btnLeft", "<", "L", 0, 0)
children += hop_button("btnRight", ">", "R", 2, 0)
children += hop_button("btnDown", "v", "D", 1, 1)

# ---------- console keys ----------
console_keys = [
    ("btnStart", "START", 'ctxMode = "Attract" || ctxMode = "GameOver"', game_logic.START_GAME),
    ("btnSelect", "SELECT", 'ctxMode = "Attract"', 'UpdateContext({ctxTwoPlayer: !ctxTwoPlayer})'),
    ("btnOption", "OPTION", 'true', 'UpdateContext({ctxFast: !ctxFast})'),
    ("btnPause", "PAUSE", 'ctxMode = "Playing"', 'UpdateContext({ctxPaused: !ctxPaused})'),
    ("btnReset", "RESET", 'true', 'UpdateContext({ctxMode: "Attract", ctxModeTicks: 0, ctxPaused: false, ctxFast: false, ctxTwoPlayer: false})'),
    # debug: fake a level clear so the tick advances the level through the normal path
    ("btnMute", '=If(ctxMuted, "UNMUTE", "MUTE")', 'true', 'UpdateContext({ctxMuted: !ctxMuted})'),
    ("btnKeys", '=If(ctxKeys, "KEYS ON", "KEYS")', 'true', 'UpdateContext({ctxKeys: !ctxKeys}); If(ctxKeys, SetFocus(txtKeys))'),
    ("btnLevel", "LEVEL+", 'ctxMode = "Playing" || ctxMode = "Jingle"', 'UpdateContext({ctxMode: "LevelClear", ctxModeTicks: 1, ctxBays: "11111"})'),
]
for i, (name, text, enabled, action) in enumerate(console_keys):
    children += control(name, "Classic/Button@2.2.0", 6, props(P,
        Text=(text if text.startswith("=") else f'="{text}"'), Color="=RGBA(220, 200, 120, 1)", Fill="=RGBA(96, 72, 32, 1)", HoverFill="=RGBA(120, 92, 44, 1)",
        PressedFill="=RGBA(72, 54, 24, 1)", HoverColor="=RGBA(255, 240, 180, 1)", PressedColor="=RGBA(220, 200, 120, 1)",
        DisabledFill="=RGBA(48, 40, 28, 1)", DisabledColor="=RGBA(120, 110, 90, 1)",
        Font=f"={MONO}", FontWeight="=FontWeight.Bold", Size="=12", BorderThickness="=0",
        RadiusTopLeft="=4", RadiusTopRight="=4", RadiusBottomLeft="=4", RadiusBottomRight="=4",
        X=f"=nfLeft + {i} * 116", Y="=nfTop + 240 * nfLine + 30", Width="=108", Height="=36",
        DisplayMode=f"=If({enabled}, DisplayMode.Edit, DisplayMode.Disabled)") + block("OnSelect", action, P))

# ---------- keyboard trick: a focused text input reads WASD / IJKL ----------
children += control("txtKeys", "Classic/TextInput", 6, props(P,
    Default='=""', HintText='="click, then WASD"', DelayOutput="=false", AccessibleLabel='="Keyboard hop input"', Font=f"={MONO}", Size="=11",
    Color="=RGBA(220, 200, 120, 1)", Fill="=RGBA(40, 32, 16, 1)", BorderColor="=RGBA(96, 72, 32, 1)", BorderThickness="=1",
    HoverFill="=RGBA(48, 40, 20, 1)", PressedFill="=RGBA(48, 40, 20, 1)", FocusedBorderThickness="=2",
    X="=nfLeft + 160 * nfCol + 30", Y="=nfTop + 240 * nfLine - 10", Width="=222", Height="=34", Visible="=ctxKeys") +
    block("OnChange", '''
    With({k: Lower(Right(Self.Text, 1))},
      UpdateContext({ctxHopQueued: Switch(k, "w", "U", "i", "U", "s", "D", "k", "D", "a", "L", "j", "L", "d", "R", "l", "R", ctxHopQueued)}));
    Reset(Self)
    ''', P))

# ---------- audio: one hidden control per clip, Start pulses true for one tick ----------
for name in sounds.CLIPS:
    flag = name.replace("nfSnd", "ctxSnd")
    children += control(name.replace("nfSnd", "aud"), "Audio", 6, props(P,
        Media=f"={name}", Start=f"={flag} > 0 && !ctxMuted", AutoStart="=false", Loop="=false",
        ShowControls="=false", Visible="=true", X="=0", Y="=0", Width="=1", Height="=1"))

# ---------- timer ----------
children += control("tmrGame", "Timer@2.1.0", 6, props(P,
    AutoStart="=true", Repeat="=true", AutoPause="=false", Duration="=50",
    Start="=!ctxPaused", Visible="=false",
    X="=nfLeft + 160 * nfCol + 20", Y="=nfTop", Width="=120", Height="=24") + block("OnTimerEnd", game_logic.TICK, P))

screen_yaml = "Screens:\n  Screen1:\n    Properties:\n"
screen_yaml += f"      Fill: ={BORDER}\n      LoadingSpinnerColor: =RGBA(64, 192, 64, 1)\n"
screen_yaml += block("OnVisible", game_logic.ON_VISIBLE, 6)
screen_yaml += "    Children:\n" + children

editor_yaml = "EditorState:\n  ScreensOrder:\n    - Screen1\n"

os.makedirs(OUT, exist_ok=True)
for fname, content in (("App.pa.yaml", app_yaml), ("Screen1.pa.yaml", screen_yaml), ("_EditorState.pa.yaml", editor_yaml)):
    with open(os.path.join(OUT, fname), "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print(f"wrote {fname} ({len(content)} chars)")
