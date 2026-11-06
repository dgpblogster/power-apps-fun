"""Level text files -> data for the Power Fx generator and the view (docs/01-game-spec.md section 6).

Format:
    name: <title>
    light-default: <0-9>
    ---grid---
    rows of cell characters (all the same width; 'P' marks the player start and becomes floor)
    ---things---
    kind x y angle skillmask
    ---lights---            (optional)
    rows of digits 0-9, same size as the grid
"""
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
LEVEL_DIR = os.path.join(_HERE, "..", "levels")

DOOR_CHARS = "Dacv"
OPEN_CHARS = ".~T"
WALL_CHARS = "123456789XS"
DOOR_IDS = "ABCDEFGHIJKLMNOP"    # door index 0-15 as a letter in the door map
MAX_SIZE = 48
MAX_DOORS = 16

# Sprite kinds shared with pcf/RaycastView/src/sprites.ts (KIND)
ENEMY_KINDS = {"drone": 1, "crawler": 2, "welder": 3, "brute": 4, "warden": 5}
ITEM_KINDS = {"medvial": 20, "medkit": 21, "rivets": 22, "shells": 23, "cells": 24, "charges": 25, "vest": 26,
              "chipamber": 27, "chipcyan": 28, "chipviolet": 29}
DECOR_KINDS = {"lamp": 40, "barrel": 41}


class Level:
    def __init__(self, name, w, h, cells, light, things, start):
        self.name, self.w, self.h, self.cells, self.light, self.things = name, w, h, cells, light, things
        self.start = start                     # (x, y, yaw)
        self.door_map = "".join(self._door_letter(i) for i in range(w * h))

    def _door_letter(self, i):
        if self.cells[i] not in DOOR_CHARS:
            return "-"
        return DOOR_IDS[min(MAX_DOORS - 1, sum(1 for c in self.cells[:i] if c in DOOR_CHARS))]

    @property
    def map_data(self):
        return f"{self.w},{self.h};{self.cells}"

    @property
    def enemies(self):
        return [t for t in self.things if t["kind"] in ENEMY_KINDS.values()]

    @property
    def items(self):
        return [t for t in self.things if t["kind"] in ITEM_KINDS.values()]

    @property
    def decor(self):
        return [t for t in self.things if t["kind"] in DECOR_KINDS.values()]


def load(name):
    path = os.path.join(LEVEL_DIR, name if name.endswith(".txt") else name + ".txt")
    meta, grid, things, lights, section = {}, [], [], [], "meta"
    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\n").rstrip()
            if line.startswith("---") and line.endswith("---"):
                section = line.strip("-")
                continue
            if section == "meta" and ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
            elif section == "grid" and line:
                grid.append(line)
            elif section == "things" and line and not line.startswith("#"):
                things.append(line.split())
            elif section == "lights" and line and not line.startswith("("):
                lights.append(line)

    h, w = len(grid), max(len(r) for r in grid)
    if any(len(r) != w for r in grid):
        raise ValueError(f"{path}: grid rows differ in width")
    if w > MAX_SIZE or h > MAX_SIZE:
        raise ValueError(f"{path}: grid {w}x{h} exceeds {MAX_SIZE}x{MAX_SIZE}")

    start = None
    cells = []
    for y, row in enumerate(grid):
        for x, c in enumerate(row):
            if c == "P":
                start = (x + 0.5, y + 0.5, 0)
                c = "."
            if c not in OPEN_CHARS + DOOR_CHARS + WALL_CHARS:
                raise ValueError(f"{path}: unknown cell {c!r} at {x},{y}")
            if (x in (0, w - 1) or y in (0, h - 1)) and c not in WALL_CHARS:
                raise ValueError(f"{path}: border cell {x},{y} must be a wall")
            cells.append(c)
    cells = "".join(cells)
    if sum(1 for c in cells if c in DOOR_CHARS) > MAX_DOORS:
        raise ValueError(f"{path}: more than {MAX_DOORS} doors")

    default_light = meta.get("light-default", "7")
    light = "".join(lights) if lights else default_light * (w * h)
    if len(light) != w * h or not light.isdigit():
        raise ValueError(f"{path}: lights must be {w}x{h} digits")

    parsed = []
    all_kinds = {**ENEMY_KINDS, **ITEM_KINDS, **DECOR_KINDS}
    for t in things:
        kind = t[0].lower()
        x, y, ang = float(t[1]), float(t[2]), float(t[3]) if len(t) > 3 else 0.0
        mask = int(t[4]) if len(t) > 4 else 7
        if kind == "player":
            start = (x, y, ang)
            continue
        if kind not in all_kinds:
            raise ValueError(f"{path}: unknown thing {kind!r}")
        if cells[int(y) * w + int(x)] not in OPEN_CHARS:
            raise ValueError(f"{path}: {kind} at {x},{y} is not on a floor cell")
        parsed.append({"kind": all_kinds[kind], "name": kind, "x": x, "y": y, "angle": ang, "mask": mask})
    if start is None:
        raise ValueError(f"{path}: no player start")
    return Level(meta.get("name", name), w, h, cells, light, parsed, start)


if __name__ == "__main__":
    import sys
    lv = load(sys.argv[1] if len(sys.argv) > 1 else "m0-test")
    print(f"{lv.name}: {lv.w}x{lv.h}, {len(lv.enemies)} enemies, {len(lv.items)} items, "
          f"{lv.cells.count('D') + sum(lv.cells.count(c) for c in 'acv')} doors, start {lv.start}")
