"""Generate the canvas app YAML for Deep Station M0 (App.pa.yaml, Screen1.pa.yaml, _EditorState.pa.yaml).

Run from the project root:  python tools/gen_app.py [level]
Writes to canvas/Src (override with DEEPSTATION_SRC). Enemy slot count: DEEPSTATION_ENEMY_SLOTS (default 12).

Layout: 1366 x 768 screen. The RaycastView code component fills the top (960 x 600, 3x the 320 x 200 view);
the status bar of standard controls sits under it.
"""
import os, re, sys, textwrap
sys.path.insert(0, os.path.dirname(__file__))
import levels        # noqa: E402
import game_logic    # noqa: E402

_HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("DEEPSTATION_SRC") or os.path.join(_HERE, "..", "canvas", "Src")
LEVEL = sys.argv[1] if len(sys.argv) > 1 else "m0-test"
# Dataverse name of the code component: <publisher prefix>_<namespace>.<constructor>
PCF_NAME = os.environ.get("DEEPSTATION_PCF_NAME", "wrk_DeepStation.RaycastView")


# ---------- formula sanity check (catches generator slips before Studio does) ----------
def check_formula(name, text):
    s = re.sub(r'"(?:[^"]|"")*"', '""', text)          # strings
    s = re.sub(r"//[^\n]*", "", s)                      # comments
    for o, c in ("()", "{}", "[]"):
        if s.count(o) != s.count(c):
            raise SystemExit(f"{name}: unbalanced {o}{c} ({s.count(o)} vs {s.count(c)})")
    return text


# ---------- YAML helpers (same conventions as frogger/tools/gen_app.py) ----------
def ind(text, n):
    pad = " " * n
    return "\n".join(pad + line if line.strip() else line for line in text.splitlines())

def block(prop, formula, level):
    body = textwrap.dedent(check_formula(prop, formula)).strip("\n")
    return f"{' ' * level}{prop}: |-\n{ind('=' + body, level + 2)}\n"

def props(level, **kv):
    """One line per property; values that YAML would misread (': ' or ' #') become block scalars."""
    out = ""
    for k, v in kv.items():
        v = str(v)
        if ": " in v or " #" in v:
            out += f"{' ' * level}{k}: |-\n{' ' * (level + 2)}{v}\n"
        else:
            out += f"{' ' * level}{k}: {v}\n"
    return out

def control(name, ctype, level, properties, extra=""):
    return (f"{' ' * level}- {name}:\n{' ' * (level + 4)}Control: {ctype}\n{extra}"
            f"{' ' * (level + 4)}Properties:\n{properties}")

P = 12
MONO = "Font.'Courier New'"
AMBER = "RGBA(232, 208, 128, 1)"
DIM = "RGBA(130, 140, 130, 1)"
BAR = "RGBA(28, 30, 34, 1)"
VIEW_X, VIEW_Y, VIEW_W, VIEW_H = 203, 10, 960, 600
BAR_Y = VIEW_Y + VIEW_H + 8

level = levels.load(LEVEL)

def label(name, text, color, size, x, y, w, h, align="Align.Left", visible="true"):
    return control(name, "Label@2.5.1", 6, props(P,
        Text=text, Color=f"={color}", Align=f"={align}", Font=f"={MONO}", FontWeight="=FontWeight.Bold",
        Size=f"={size}", X=f"={x}", Y=f"={y}", Width=f"={w}", Height=f"={h}",
        PaddingTop="=0", PaddingBottom="=0", PaddingLeft="=0", PaddingRight="=0", Wrap="=false",
        Visible=f"={visible}"))

def button(name, text, x, y, w, action, enabled="true"):
    return control(name, "Classic/Button@2.2.0", 6, props(P,
        Text=text, Color=f"={AMBER}", Fill="=RGBA(70, 58, 30, 1)", HoverFill="=RGBA(96, 78, 40, 1)",
        PressedFill="=RGBA(50, 40, 20, 1)", HoverColor="=RGBA(255, 240, 180, 1)", PressedColor=f"={AMBER}",
        DisabledFill="=RGBA(40, 36, 28, 1)", DisabledColor="=RGBA(110, 100, 80, 1)",
        Font=f"={MONO}", FontWeight="=FontWeight.Bold", Size="=11", BorderThickness="=0",
        RadiusTopLeft="=4", RadiusTopRight="=4", RadiusBottomLeft="=4", RadiusBottomRight="=4",
        X=f"={x}", Y=f"={y}", Width=f"={w}", Height="=30",
        DisplayMode=f"=If({enabled}, DisplayMode.Edit, DisplayMode.Disabled)") + block("OnSelect", action, P))

# ---------- App ----------
formulas = check_formula("Formulas", game_logic.app_formulas(level))
app_yaml = "App:\n  Properties:\n    BackEnabled: =false\n    StartScreen: =Screen1\n"
app_yaml += "    Formulas: |-\n" + ind("=" + formulas.strip("\n"), 6) + "\n"

children = ""

# ---------- the view (code component) ----------
children += control("pcfView", "CodeComponent", 6,
    props(P, X=f"={VIEW_X}", Y=f"={VIEW_Y}", Width=f"={VIEW_W}", Height=f"={VIEW_H}",
          MapData="=nfMapData", LightData="=nfLight", TickMs="=nfTickMs",
          Paused="=ctxPaused", ShowDiag="=ctxDiag", Muted="=ctxMuted", ShowTouch="=false")
    + block("Frame", game_logic.frame_formula(level), P)
    + block("OnChange", "If(Coalesce(Self.MenuSeq, 0) <> ctxMenuSeen, UpdateContext({ctxPaused: !ctxPaused, ctxMenuSeen: Coalesce(Self.MenuSeq, 0)}))", P),
    extra=f"{' ' * 10}ComponentName: {PCF_NAME}\n")

# ---------- status bar ----------
children += control("recBar", "Rectangle@2.3.0", 6, props(P,
    Fill=f"={BAR}", X=f"={VIEW_X}", Y=f"={BAR_Y}", Width=f"={VIEW_W}", Height="=104", BorderThickness="=0"))

def stat(name, caption, value, x, w, color=AMBER):
    return (label(f"lbl{name}Cap", f'="{caption}"', DIM, "10", x, BAR_Y + 8, w, 16, align="Align.Center") +
            label(f"lbl{name}", value, color, "26", x, BAR_Y + 24, w, 40, align="Align.Center"))

children += stat("Health", "HEALTH", '=ctxHealth & "%"', VIEW_X + 10, 150,
                 color='If(ctxHealth > 50, RGBA(110, 230, 120, 1), ctxHealth > 25, RGBA(240, 200, 60, 1), RGBA(255, 70, 60, 1))')
children += stat("Armor", "ARMOR", '=ctxArmor & "%"', VIEW_X + 170, 130)
children += stat("Ammo", "RIVETS", '=ctxAmmoRivet', VIEW_X + 310, 130)
children += stat("Weapon", "WEAPON", '=Switch(ctxWeapon, 1, "WRENCH", 2, "RIVET", "-")', VIEW_X + 450, 170)
children += stat("Kills", "KILLS", '=ctxKills & "/" & Min(nfEnemyTotal, ctxSlots)', VIEW_X + 630, 140)
children += label("lblMsg", "=ctxMsg", AMBER, "13", VIEW_X + 14, BAR_Y + 70, 600, 24,
                  visible='ctxMsg <> ""')

# spike diagnostics: measured tick rate and the active enemy slot count
children += label("lblTps",
    '=Text(Round(ctxTick / Max(1, DateDiff(ctxStartTime, Now(), TimeUnit.Milliseconds) / 1000), 1)) & " tps  " & '
    'Coalesce(pcfView.Fps, 0) & " fps  slots " & ctxSlots & "/" & nfMaxSlots',
    DIM, "11", VIEW_X + 780, BAR_Y + 8, 170, 18, align="Align.Right")

children += button("btnPause", '=If(ctxPaused, "RESUME", "PAUSE")', VIEW_X + VIEW_W - 300, BAR_Y + 68, 70,
                   "UpdateContext({ctxPaused: !ctxPaused})")
children += button("btnSlots", '="SLOTS " & ctxSlots', VIEW_X + VIEW_W - 225, BAR_Y + 68, 80,
                   "UpdateContext({ctxSlots: If(ctxSlots >= nfMaxSlots, Min(4, nfMaxSlots), Min(nfMaxSlots, ctxSlots + 4))}); Select(btnRestart)")
children += button("btnDiag", '=If(ctxDiag, "DIAG ON", "DIAG")', VIEW_X + VIEW_W - 140, BAR_Y + 68, 70,
                   "UpdateContext({ctxDiag: !ctxDiag})")
children += button("btnMute", '=If(ctxMuted, "UNMUTE", "MUTE")', VIEW_X + VIEW_W - 65, BAR_Y + 68, 60,
                   "UpdateContext({ctxMuted: !ctxMuted})")
children += button("btnRestart", '="RESTART"', VIEW_X + 780, BAR_Y + 34, 170, game_logic.start_game(level))

children += label("lblCredit",
    '="Deep Station: an original game built in Power Fx. Not affiliated with id Software, ZeniMax, or Bethesda."',
    DIM, "9", VIEW_X, BAR_Y + 108, VIEW_W, 16)

# ---------- the tick ----------
children += control("tmrGame", "Timer@2.1.0", 6, props(P,
    AutoStart="=true", Repeat="=true", AutoPause="=false", Duration="=nfTickMs",
    Start="=!ctxPaused", Visible="=false", X="=0", Y="=0", Width="=120", Height="=24")
    + block("OnTimerEnd", game_logic.tick(level), P))

screen_yaml = "Screens:\n  Screen1:\n    Properties:\n"
screen_yaml += "      Fill: =RGBA(12, 13, 15, 1)\n      LoadingSpinnerColor: =RGBA(232, 208, 128, 1)\n"
screen_yaml += block("OnVisible", game_logic.on_visible(level), 6)
screen_yaml += "    Children:\n" + children

editor_yaml = "EditorState:\n  ScreensOrder:\n    - Screen1\n"

if os.environ.get("DEEPSTATION_BOOTSTRAP") == "1":
    # Bootstrap app: no code component, so Studio can open it. The maker adds RaycastView once in Studio
    # (Insert > Get more components > Code), saves, and exports; the export teaches the build how Studio
    # records the component. See README "Bootstrap".
    app_yaml = "App:\n  Properties:\n    BackEnabled: =false\n    StartScreen: =Screen1\n"
    steps = ("Deep Station bootstrap\n\n"
             "1. Insert > Get more components > Code tab > RaycastView > Import.\n"
             "2. Insert > Code components > RaycastView (drop one anywhere).\n"
             "3. Save. Then export the DeepStation solution (unmanaged) and send the zip to the Claude session.")
    screen_yaml = ("Screens:\n  Screen1:\n    Properties:\n      Fill: =RGBA(12, 13, 15, 1)\n    Children:\n" +
        control("lblBootstrap", "Label@2.5.1", 6, props(P,
            Color=f"={AMBER}", Font=f"={MONO}", Size="=16", X="=60", Y="=60", Width="=1246", Height="=400",
            VerticalAlign="=VerticalAlign.Top") + block("Text", '"' + steps.replace('"', '""') + '"', P)))
    print("bootstrap app (no code component)")

os.makedirs(OUT, exist_ok=True)
for fname, content in (("App.pa.yaml", app_yaml), ("Screen1.pa.yaml", screen_yaml), ("_EditorState.pa.yaml", editor_yaml)):
    with open(os.path.join(OUT, fname), "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print(f"wrote {fname} ({len(content)} chars)")
print(f"level {level.name}: {level.w}x{level.h}, {len(level.enemies)} enemies in {game_logic.MAX_SLOTS} slots")
