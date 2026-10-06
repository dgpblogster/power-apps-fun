"""Generate SVG sprite data for the Galaxian canvas app.

Each sprite is an 8x8 (or 8x8 double-row) bitmap of palette indices. The output is a set of
Power Fx named formulas (one per sprite) whose value is a data: URI for an SVG with crisp pixels.
Logical pixels are 2 units wide and 1 unit tall to mimic the Atari's wide colour clocks.

Run:  python tools/sprites.py > app/generated-sprites.txt
"""
import json

# palette index -> colour, per sprite kind ("." = transparent)
ALIEN_SHAPE_A = [  # wings up (hanging bat-style like the original formation pose)
    "..1....1",
    "..1....1",
    ".111111.",
    "1121.121",
    "11111111",
    "1.1111.1",
    "1.1..1.1",
    "...33...",
]
ALIEN_SHAPE_B = [  # wings down
    "........",
    "1.1....1",
    "1111111.",
    ".121.121",
    "11111111",
    ".111111.",
    "..1..1..",
    "...33...",
]
COMMANDER_A = [
    "...11...",
    "..1111..",
    ".111111.",
    "11311311",
    "11111111",
    "1.2222.1",
    "1..22..1",
    "....2...",
]
COMMANDER_B = [
    "...11...",
    "..1111..",
    "1111111.",
    "11311311",
    ".111111.",
    "..2222..",
    ".2.22.2.",
    "....2...",
]
SHIP = [
    "...11...",
    "...11...",
    "..1111..",
    "..1111..",
    ".111111.",
    "11111111",
    "2.1111.2",
    "2..11..2",
]
EXPLODE_1 = [
    "........",
    "..1..1..",
    "...11...",
    ".1.22.1.",
    "...22...",
    "..1..1..",
    "........",
    "........",
]
EXPLODE_2 = [
    "1......1",
    ".1.33.1.",
    "..3113..",
    ".3.11.3.",
    "..3113..",
    ".1.33.1.",
    "1......1",
    "........",
]
EXPLODE_3 = [
    "1..1..1.",
    ".......1",
    "1..3....",
    "...3.3.1",
    "1.3....1",
    "........",
    ".1..1..1",
    "1.......",
]
FLAG = [  # 8 wide x 8 tall small red flag
    "1.......",
    "1111....",
    "1111111.",
    "1111111.",
    "1111....",
    "1.......",
    "1.......",
    "1.......",
]
CHOMPER = [  # original "surprise" symbol: a yellow chomping disc (homage, not Pac-Man art)
    "..1111..",
    ".111111.",
    "11111...",
    "1111....",
    "1111....",
    "11111...",
    ".111111.",
    "..1111..",
]

PALETTES = {
    "Drone":     {"1": "#40C0C0", "2": "#A02020", "3": "#2040A0"},
    "Emissary":  {"1": "#B080E0", "2": "#E8C840", "3": "#3040A0"},
    "Hornet":    {"1": "#E03030", "2": "#F0E040", "3": "#40B040"},
    "Commander": {"1": "#E8C840", "2": "#E05A20", "3": "#6060D0"},
    "Ship":      {"1": "#F050A0", "2": "#4060E0"},
    "Explode":   {"1": "#F0E040", "2": "#FFFFFF", "3": "#E05A20"},
    "Flag":      {"1": "#E03030"},
    "Chomper":   {"1": "#F0E040"},
}

def paths(bitmap, palette, px_w=2, px_h=1):
    """Return list of (colour, path d) using horizontal runs for compactness."""
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
            out.setdefault(c, []).append(f"M{x*px_w} {y*px_h}h{run*px_w}v{px_h}h-{run*px_w}z")
            x += run
    return [(palette[c], "".join(segs)) for c, segs in out.items()]

def svg(bitmap, palette):
    w = len(bitmap[0]) * 2
    h = len(bitmap)
    parts = "".join(f'<path fill="{col}" d="{d}"/>' for col, d in paths(bitmap, palette))
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" shape-rendering="crispEdges">{parts}</svg>'

SPRITES = {
    "nfSprDroneA": (ALIEN_SHAPE_A, "Drone"),
    "nfSprDroneB": (ALIEN_SHAPE_B, "Drone"),
    "nfSprEmissaryA": (ALIEN_SHAPE_A, "Emissary"),
    "nfSprEmissaryB": (ALIEN_SHAPE_B, "Emissary"),
    "nfSprHornetA": (ALIEN_SHAPE_A, "Hornet"),
    "nfSprHornetB": (ALIEN_SHAPE_B, "Hornet"),
    "nfSprCommanderA": (COMMANDER_A, "Commander"),
    "nfSprCommanderB": (COMMANDER_B, "Commander"),
    "nfSprShip": (SHIP, "Ship"),
    "nfSprExplode1": (EXPLODE_1, "Explode"),
    "nfSprExplode2": (EXPLODE_2, "Explode"),
    "nfSprExplode3": (EXPLODE_3, "Explode"),
    "nfSprFlag": (FLAG, "Flag"),
    "nfSprChomper": (CHOMPER, "Chomper"),
}

def powerfx_string(s):
    return '"' + s.replace('"', '""') + '"'

if __name__ == "__main__":
    lines = []
    for name, (bmp, pal) in SPRITES.items():
        s = svg(bmp, PALETTES[pal])
        lines.append(f'{name} = "data:image/svg+xml;utf8," & EncodeUrl({powerfx_string(s)});')
    print("\n".join(lines))
