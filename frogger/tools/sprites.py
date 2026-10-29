"""Pixel art -> SVG data-URI named formulas for the Frogger canvas app.

Art is drawn at hi-res pixel width: ONE character = half a logical column (one Atari hi-res pixel) wide and one
scanline tall, so a sprite that occupies W columns x 16 lines is a bitmap 2W wide x 16 tall. "." is
transparent; other characters are palette keys. "0" is always the black outline.

Sprite sizes (bitmap px): frog 16x16, vehicles 24x16, turtle 24x16 (pair 48, trio 72), logs 62/78/142 x 16,
snake 32x16, alligator 78x16, life icon 8x8. The playfield background (160x240 columns x lines) is explicit SVG.

Run:  python tools/sprites.py   (prints the Power Fx lines gen_app.py appends to App.Formulas)
"""

PX_W, PX_H = 1, 1

C = {
    "black": "#000000", "white": "#F4F4F4",
    "frog": "#3CC23C", "frogLight": "#9BE36A", "frogDark": "#1E7A1E", "belly": "#E8F080",
    "pink": "#FF80C0", "pinkLight": "#FFC0E0",
    "homeGreen": "#58D858", "cyan": "#60E0F0",
    "dead": "#F0E040", "deadRed": "#D83030",
    "purple": "#A81DE3", "purpleLight": "#D080FF", "blue": "#5141FF", "blueLight": "#9AA0FF",
    "racer": "#FF60C0", "racerLight": "#FFB0E0", "orange": "#FF8900", "orangeLight": "#FFC060",
    "grey": "#B8B8B8", "greyDark": "#606060", "glass": "#B0E8FF",
    "logTop": "#E85020", "logLight": "#FF9060", "logUnder": "#A02810", "logCap": "#FFD0A0",
    "turtle": "#4C9A20", "turtleLight": "#8CD040", "turtleDark": "#2A5A10", "turtleYellow": "#FFC500",
    "snake": "#D8B860", "snakeDark": "#8A6A20", "gator": "#6A8A2A", "gatorDark": "#3A5A10", "yellow": "#FFE040",
    "water": "#321FFF", "bankYellow": "#FFC500", "bankRed": "#FF0000",
    "brickRed": "#660D00", "brickTan": "#C8A060", "brickGrey": "#8C8C8C",
}

# ---------------------------------------------------------------- frog 16 x 16, facing up (top-down view)
# 0 outline, 1 body green, 2 belly, 3 eye white, 4 light green highlight
FROG_U = [
    "....00....00....",
    "...0330..0330...",
    "...0300..0030...",
    "....00111100....",
    "...0144114410...",
    "..011112211110..",
    "0.01112222111 0.".replace(" ", "0"),
    "0001112222111000",
    "0111112222111110",
    "0110112222110110",
    ".00.0112211.0.0.",
    "....01111110....",
    "...0110..0110...",
    "..011.0..0.110..",
    ".0110......0110.",
    ".000........000.",
]
FROG_U_HOP = [
    "...000....000...",
    "..03300..00330..",
    "..03000..00030..",
    "...0011111100...",
    "0..014422110..0.",
    "00.011222211.00.",
    ".001122222211000",
    "..011222222110..",
    "..011222222110..",
    "...0112222110...",
    "...0111111110...",
    "....01100110....",
    "....010..010....",
    "...010....010...",
    "..010......010..",
    "..00........00..",
]
FROG_SQUASH = [  # road death: flattened, red smear
    "................",
    "................",
    "................",
    "................",
    "0..0........0..0",
    "0001100000011000",
    ".011122222211110",
    "0111122222211110",
    "0111122222211110",
    ".011112222111110",
    "0001100000011000",
    "0..0........0..0",
    "................",
    "................",
    "................",
    "................",
]
FROG_DROWN = [  # river death: ripple rings around a sinking frog
    "................",
    "......5555......",
    "....55....55....",
    "...5..0000..5...",
    "..5..011110..5..",
    "..5.01122110.5..",
    "..5.01122110.5..",
    "..5..011110..5..",
    "...5..0000..5...",
    "....55....55....",
    "......5555......",
    "................",
    "....5......5....",
    "..5..........5..",
    "................",
    "................",
]
FROG_LIFE = [  # 8 x 8 reserve icon
    "00....00",
    "0300.030",
    ".011110.",
    "01122110",
    "01122110",
    ".011110.",
    "01.00.10",
    "00....00",
]
# ---------------------------------------------------------------- vehicles 24 x 16 (top-down)
# 0 outline, 1 body, 2 body light, 3 glass, 4 wheel grey
CAR_LEFT = [  # sedan facing left
    "........................",
    "...0000.........0000....",
    "...044400000000044400...",
    "..00111111111111111100..",
    ".0111112233333221111110.",
    ".0111112333333321111110.",
    "011111123333333211111110",
    "011111123333333211111110",
    ".0111112333333321111110.",
    ".0111112233333221111110.",
    "..00111111111111111100..",
    "...044400000000044400...",
    "...0000.........0000....",
    "........................",
    "........................",
    "........................",
]
RACER_RIGHT = [  # open-wheel racer, nose to the right
    "........................",
    "....0000.......0000.....",
    "....044400000000444 0...".replace(" ", "0"),
    "...001111100000011100...",
    "..011111111100011111110.",
    "001111113331011111111110",
    "011111113333311111122220",
    "011111113333311111122220",
    "001111113331011111111110",
    "..011111111100011111110.",
    "...001111100000011100...",
    "....044400000000444 0...".replace(" ", "0"),
    "....0000.......0000.....",
    "........................",
    "........................",
    "........................",
]
DOZER_RIGHT = [  # bulldozer, blade to the right
    "........................",
    ".0000000000000....0000..",
    ".0444444444440....0220..",
    ".0404040404040...02220..",
    ".0444444444440..022220..",
    ".000111111 0000.0222220.".replace(" ", "1"),
    ".0111331111 000 0222220.".replace(" ", "1"),
    ".0113333111110002222220.",
    ".0113333111110002222220.",
    ".0111331111110000222220.",
    ".000111111110000.022220.",
    ".0444444444440...02220..",
    ".0404040404040....0220..",
    ".0444444444440....0000..",
    ".0000000000000..........",
    "........................",
]
# ---------------------------------------------------------------- turtle 24 x 16, head to the left
# 0 outline, 1 shell green, 2 shell light, 3 shell dark pattern, 4 head/legs yellow-green, 5 eye
TURTLE_A = [
    "........................",
    "........00......00......",
    ".......0440....0440.....",
    "......00044000004400....",
    "....0001111111111100....",
    "..00441122332223311100..",
    ".045441123232323111110..",
    "044444112332223221111110",
    "044444112332223221111110",
    ".044441123232323111110..",
    "..00441122332223311100..",
    "....0001111111111100....",
    "......00044000004400....",
    ".......0440....0440.....",
    "........00......00......",
    "........................",
]
TURTLE_B = [
    "........................",
    "......00......00........",
    ".....0440....0440.......",
    "......00044000004400....",
    "....0001111111111100....",
    "..00441122332223311100..",
    ".045441123232323111110..",
    "044444112332223221111110",
    "044444112332223221111110",
    ".044441123232323111110..",
    "..00441122332223311100..",
    "....0001111111111100....",
    "......00044000004400....",
    ".....0440....0440.......",
    "......00......00........",
    "........................",
]
TURTLE_HALF = [  # sinking: shell only, no legs or head
    "........................",
    "........................",
    "........................",
    "........................",
    "........................",
    "......0001111111100.....",
    ".....011122332231110....",
    "....01111232323211110...",
    "....01111232323211110...",
    ".....011122332231110....",
    "......0001111111100.....",
    "........................",
    "........................",
    "........................",
    "........................",
    "........................",
]
TURTLE_DEEP = [  # ripple only
    "........................",
    "........................",
    "........................",
    "........................",
    "........................",
    ".........6666...........",
    "......666....666........",
    ".....6..........6.......",
    ".....6..........6.......",
    "......666....666........",
    ".........6666...........",
    "........................",
    "........................",
    "........................",
    "........................",
    "........................",
]
# ---------------------------------------------------------------- snake 32 x 16, head right (1 body, 2 dark, 3 tongue)
SNAKE_R_A = [
    "................................",
    "................................",
    "................................",
    "................................",
    "......0000............0000000...",
    ".....011110..........01111110...",
    "0...01122110........0112011130..",
    "00.011100111000000.0111111110.3.",
    ".0001100..0111111100011111110...",
    "..000.....00111110...0000000....",
    "...........00000................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
]
SNAKE_R_B = [
    "................................",
    "................................",
    "................................",
    "................................",
    "................0000..0000000...",
    "...............011110.01111110..",
    "0.....0000....0112211011120113..",
    "00...011110..01110011111111110.3",
    ".000011221100110...00111111110..",
    "..00111100011110.....0000000....",
    "...0000...00000.................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
]
# ---------------------------------------------------------------- fly 16 x 16 (1 body, 2 wing, 0 outline)
FLY = [
    "................",
    "................",
    "................",
    "..00........00..",
    ".0220..00..0220.",
    "0222200110022220",
    "0222201111022220",
    ".022001111000220",
    "..00.011110.00..",
    ".....011110.....",
    "....0.0110.0....",
    "...0...00...0...",
    "................",
    "................",
    "................",
    "................",
]
# ---------------------------------------------------------------- bay alligator 24 x 16 (1 body, 2 dark, 3 teeth, 4 eye)
GATOR_SNOUT = [
    "........................",
    "........................",
    "........................",
    "........................",
    "........................",
    "........................",
    "........................",
    "........................",
    "........................",
    "..........0000..........",
    ".......0001111000.......",
    ".....00111111111100.....",
    "....0111211111121110....",
    "....0111111111111110....",
    "....0313131313131310....",
    "....0000000000000000....",
]
GATOR_JAWS = [
    "........................",
    "........................",
    "....0000000000000000....",
    "...011111111111111110...",
    "..01114011111111401110..",
    "..01111111111111111110..",
    "...031313131313131310...",
    "....000000000000000.....",
    "........................",
    "....000000000000000.....",
    "...031313131313131310...",
    "..01111111111111111110..",
    "..01112211111111221110..",
    "...011111111111111110...",
    "....0000000000000000....",
    "........................",
]

PALETTES = {
    "Frog": {"0": C["black"], "1": C["frog"], "2": C["belly"], "3": C["white"], "4": C["frogLight"]},
    "Lady": {"0": C["black"], "1": C["pink"], "2": C["pinkLight"], "3": C["white"], "4": C["pinkLight"]},
    "Home": {"0": C["black"], "1": C["homeGreen"], "2": C["cyan"], "3": C["white"], "4": C["frogLight"]},
    "Dead": {"0": C["black"], "1": C["dead"], "2": C["deadRed"], "5": C["white"]},
    "Car": {"0": C["black"], "1": C["purple"], "2": C["purpleLight"], "3": C["glass"], "4": C["greyDark"]},
    "Car2": {"0": C["black"], "1": C["blue"], "2": C["blueLight"], "3": C["glass"], "4": C["greyDark"]},
    "Racer": {"0": C["black"], "1": C["racer"], "2": C["racerLight"], "3": C["glass"], "4": C["greyDark"]},
    "Dozer": {"0": C["black"], "1": C["orange"], "2": C["grey"], "3": C["glass"], "4": C["greyDark"]},
    "Turtle": {"0": C["black"], "1": C["turtle"], "2": C["turtleLight"], "3": C["turtleDark"], "4": C["turtleYellow"], "5": C["black"], "6": C["white"]},
    "Log": {"0": C["black"], "1": C["logTop"], "2": C["logUnder"], "3": C["logCap"], "4": C["logLight"]},
    "Snake": {"0": C["black"], "1": C["snake"], "2": C["snakeDark"], "3": C["deadRed"]},
    "Fly": {"0": C["black"], "1": C["greyDark"], "2": C["cyan"]},
    "Gator": {"0": C["black"], "1": C["gator"], "2": C["gatorDark"], "3": C["white"], "4": C["yellow"]},
    "LogSnake": {"0": C["black"], "1": C["logTop"], "2": C["logUnder"], "3": C["logCap"], "4": C["logLight"], "5": C["snake"], "6": C["snakeDark"], "7": C["deadRed"]},
    "LogLady": {"0": C["black"], "1": C["logTop"], "2": C["logUnder"], "3": C["logCap"], "4": C["logLight"], "5": C["pink"], "6": C["pinkLight"], "7": C["white"]},
}


# ---------------------------------------------------------------- bitmap helpers
def mirror_h(bm):
    return [row[::-1] for row in bm]


def flip_v(bm):
    return list(reversed(bm))


def rotate_ccw(bm):
    """Square bitmap rotated 90 degrees counter-clockwise (top of the sprite ends up at the left)."""
    n = len(bm)
    return ["".join(bm[x][n - 1 - y] for x in range(n)) for y in range(n)]


def rotate_cw(bm):
    n = len(bm)
    return ["".join(bm[n - 1 - x][y] for x in range(n)) for y in range(n)]


def hconcat(*bms):
    return ["".join(parts) for parts in zip(*bms)]


def remap(bm, mapping):
    return ["".join(mapping.get(ch, ch) for ch in row) for row in bm]


def overlay(base, sprite, x, y):
    out = [list(r) for r in base]
    for dy, row in enumerate(sprite):
        for dx, ch in enumerate(row):
            if ch != "." and 0 <= y + dy < len(out) and 0 <= x + dx < len(out[0]):
                out[y + dy][x + dx] = ch
    return ["".join(r) for r in out]


def log_bitmap(width):
    """Procedural log: outlined cylinder with a light highlight stripe, dark underside, rounded light end caps,
    bark knots. width in hi-res px (2 x columns)."""
    rows = []
    for y in range(16):
        row = []
        for x in range(width):
            edge = min(x, width - 1 - x)
            if y < 3 or y > 12:
                row.append("."); continue
            if (y in (3, 12) and edge < 2) or (y in (4, 11) and edge < 1):
                row.append("."); continue
            if y in (3, 12) or edge == 0 or (y in (4, 11) and edge < 2):
                row.append("0")
            elif edge < 5:
                row.append("3")
            elif y == 4:
                row.append("4")
            elif y >= 10:
                row.append("2")
            elif y in (6, 8) and (x * 7 + y * 3) % 23 in (0, 1, 2):
                row.append("2")
            else:
                row.append("1")
        rows.append("".join(row))
    return rows


def gator_bitmap():
    """78 x 16: scaly body, head with open jaws at the right (leading) end, 20 px head zone."""
    rows = []
    for y in range(16):
        row = []
        for x in range(78):
            head = x >= 58
            if y < 3 or y > 12:
                row.append("."); continue
            if head:
                if y in (3, 12):
                    row.append("0" if x < 72 else ".")
                elif y in (4, 11):
                    row.append("0" if x >= 74 else "1")
                elif y == 5 and x in (61, 62):
                    row.append("4")
                elif y in (6, 10) and x >= 64 and x % 2 == 0:
                    row.append("3")
                elif y in (7, 9) and x >= 64:
                    row.append("0")
                elif y == 8 and x >= 64:
                    row.append("2")
                else:
                    row.append("1" if x < 76 else "0")
            else:
                if y in (3, 12) or x == 0:
                    row.append("0")
                elif y >= 10:
                    row.append("2")
                elif (x + y) % 6 == 0 and 4 < y < 10:
                    row.append("2")
                else:
                    row.append("1")
        rows.append("".join(row))
    return rows


LOG_S, LOG_M, LOG_L = log_bitmap(62), log_bitmap(78), log_bitmap(142)
_SNAKE_ON_LOG = {"1": "5", "2": "6", "3": "7"}
LOG_SNAKE_A = overlay(LOG_L, remap(SNAKE_R_A, _SNAKE_ON_LOG), 106, -2)
LOG_SNAKE_B = overlay(LOG_L, remap(SNAKE_R_B, _SNAKE_ON_LOG), 106, -2)
LADY_ON_LOG = {"1": "5", "2": "6", "3": "7", "4": "6"}
LOG_LADY = overlay(LOG_S, remap(FROG_U, LADY_ON_LOG), 23, 0)

SPRITES = {
    "nfSprFrogU": (FROG_U, "Frog"), "nfSprFrogUHop": (FROG_U_HOP, "Frog"),
    "nfSprFrogD": (flip_v(FROG_U), "Frog"), "nfSprFrogDHop": (flip_v(FROG_U_HOP), "Frog"),
    "nfSprFrogL": (rotate_ccw(FROG_U), "Frog"), "nfSprFrogLHop": (rotate_ccw(FROG_U_HOP), "Frog"),
    "nfSprFrogR": (rotate_cw(FROG_U), "Frog"), "nfSprFrogRHop": (rotate_cw(FROG_U_HOP), "Frog"),
    "nfSprFrogHome": (FROG_U, "Home"),
    "nfSprSquash": (FROG_SQUASH, "Dead"), "nfSprDrown": (FROG_DROWN, "Dead"),
    "nfSprLife": (FROG_LIFE, "Frog"),
    "nfSprLady": (FROG_U, "Lady"),
    "nfSprCar": (CAR_LEFT, "Car"), "nfSprCar2": (CAR_LEFT, "Car2"),
    "nfSprRacer": (RACER_RIGHT, "Racer"), "nfSprDozer": (DOZER_RIGHT, "Dozer"),
    "nfSprPairA": (hconcat(TURTLE_A, TURTLE_A), "Turtle"), "nfSprPairB": (hconcat(TURTLE_B, TURTLE_B), "Turtle"),
    "nfSprPairHalf": (hconcat(TURTLE_HALF, TURTLE_HALF), "Turtle"), "nfSprPairDeep": (hconcat(TURTLE_DEEP, TURTLE_DEEP), "Turtle"),
    "nfSprTrioA": (hconcat(TURTLE_A, TURTLE_A, TURTLE_A), "Turtle"), "nfSprTrioB": (hconcat(TURTLE_B, TURTLE_B, TURTLE_B), "Turtle"),
    "nfSprTrioHalf": (hconcat(TURTLE_HALF, TURTLE_HALF, TURTLE_HALF), "Turtle"), "nfSprTrioDeep": (hconcat(TURTLE_DEEP, TURTLE_DEEP, TURTLE_DEEP), "Turtle"),
    "nfSprLogS": (LOG_S, "Log"), "nfSprLogM": (LOG_M, "Log"), "nfSprLogL": (LOG_L, "Log"),
    "nfSprSnakeRA": (SNAKE_R_A, "Snake"), "nfSprSnakeRB": (SNAKE_R_B, "Snake"),
    "nfSprSnakeLA": (mirror_h(SNAKE_R_A), "Snake"), "nfSprSnakeLB": (mirror_h(SNAKE_R_B), "Snake"),
    "nfSprFly": (FLY, "Fly"),
    "nfSprGator": (gator_bitmap(), "Gator"),
    "nfSprBaySnout": (GATOR_SNOUT, "Gator"), "nfSprBayJaws": (GATOR_JAWS, "Gator"),
    "nfSprLogSnakeA": (LOG_SNAKE_A, "LogSnake"), "nfSprLogSnakeB": (LOG_SNAKE_B, "LogSnake"),
    "nfSprLogLady": (LOG_LADY, "LogLady"),
}


def paths(bitmap, palette):
    """Horizontal-run SVG paths per colour (compact)."""
    out = {}
    for y, row in enumerate(bitmap):
        x = 0
        while x < len(row):
            c = row[x]
            if c == ".":
                x += 1
                continue
            run = 1
            while x + run < len(row) and row[x + run] == c:
                run += 1
            out.setdefault(c, []).append(f"M{x*PX_W} {y*PX_H}h{run*PX_W}v{PX_H}h-{run*PX_W}z")
            x += run
    return [(palette[c], "".join(segs)) for c, segs in out.items()]


def svg(bitmap, palette):
    w = len(bitmap[0]) * PX_W
    h = len(bitmap) * PX_H
    parts = "".join(f'<path fill="{col}" d="{d}"/>' for col, d in paths(bitmap, palette))
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" shape-rendering="crispEdges">{parts}</svg>'


# ---------------------------------------------------------------- playfield background (viewBox 320 x 240)
def field_rects(brick):
    """(x_cols, y_lines, w_cols, h_lines, colour) for the whole field: border, bank with arches, water,
    sidewalk bricks, road. Grass and HUD rows stay border green."""
    r = [(0, 0, 160, 240, "#004301"), (0, 24, 160, 16, C["bankYellow"])]
    for y in range(25, 40, 3):
        for x in range(((y - 25) // 3) % 2 * 3, 160, 8):
            r.append((x, y, 2, 1, C["bankRed"]))
    for cx in (16, 48, 80, 112, 144):
        r += [(cx - 6, 27, 12, 13, C["black"]), (cx - 4, 26, 8, 1, C["black"]), (cx - 2, 25, 4, 1, C["black"])]
    r.append((0, 40, 160, 80, C["water"]))
    r.append((0, 120, 160, 16, brick))
    for y0, off in ((120, 0), (128, 8)):
        r.append((0, y0, 160, 1, C["black"]))
        for x in range(off, 160, 16):
            r.append((x, y0, 1, 8, C["black"]))
    r.append((0, 136, 160, 64, C["black"]))
    return r


def field_svg(brick):
    body = "".join(f'<rect x="{x*2}" y="{y}" width="{w*2}" height="{h}" fill="{c}"/>' for x, y, w, h, c in field_rects(brick))
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 240" shape-rendering="crispEdges">{body}</svg>'


STRIPS = {
    "nfImgField1": field_svg(C["brickRed"]),
    "nfImgField2": field_svg(C["brickTan"]),
    "nfImgField3": field_svg(C["brickGrey"]),
}


def powerfx_string(s):
    return '"' + s.replace('"', '""') + '"'


def formula_lines():
    lines = [f'{name} = "data:image/svg+xml;utf8," & EncodeUrl({powerfx_string(svg(bmp, PALETTES[pal]))});'
             for name, (bmp, pal) in SPRITES.items()]
    lines += [f'{name} = "data:image/svg+xml;utf8," & EncodeUrl({powerfx_string(s)});' for name, s in STRIPS.items()]
    return lines


if __name__ == "__main__":
    print("\n".join(formula_lines()))
