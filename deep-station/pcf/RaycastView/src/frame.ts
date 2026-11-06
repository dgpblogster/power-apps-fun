// Parsing of the three text inputs that Power Fx sends (docs/01-game-spec.md section 3).
// The view never invents state: everything here is a copy of what the tick decided.

export const DOOR_CHARS = "Dacv";
const OPEN_CHARS = ".~T";

export interface GameMap {
    w: number;
    h: number;
    cells: string;          // w*h characters, row-major, y down
    light: Uint8Array;      // 0-9 per cell
    doorId: Int16Array;     // door index 0-15 per cell, -1 where there is no door
    doorAcross: Uint8Array; // 1 if the door panel runs along X (walls left and right of it), else along Y
    key: string;            // the raw inputs, to skip re-parsing identical values
}

export function parseMap(mapData: string | null, lightData: string | null): GameMap | null {
    if (!mapData) return null;
    const semi = mapData.indexOf(";");
    if (semi < 0) return null;
    const [ws, hs] = mapData.slice(0, semi).split(",");
    const w = parseInt(ws, 10);
    const h = parseInt(hs, 10);
    const cells = mapData.slice(semi + 1);
    if (!(w > 0 && h > 0) || cells.length < w * h) return null;

    const light = new Uint8Array(w * h).fill(7);
    if (lightData && lightData.length >= w * h) {
        for (let i = 0; i < w * h; i++) {
            const d = lightData.charCodeAt(i) - 48;
            light[i] = d >= 0 && d <= 9 ? d : 7;
        }
    }

    const doorId = new Int16Array(w * h).fill(-1);
    const doorAcross = new Uint8Array(w * h);
    let next = 0;
    for (let i = 0; i < w * h; i++) {
        if (DOOR_CHARS.indexOf(cells[i]) >= 0) {
            doorId[i] = next < 16 ? next++ : 15;
            const x = i % w;
            const leftWall = x > 0 && isWallChar(cells[i - 1]);
            const rightWall = x < w - 1 && isWallChar(cells[i + 1]);
            doorAcross[i] = leftWall && rightWall ? 1 : 0;
        }
    }
    return { w, h, cells: cells.slice(0, w * h), light, doorId, doorAcross, key: mapData + "\u0000" + (lightData ?? "") };
}

export function isWallChar(c: string): boolean {
    return OPEN_CHARS.indexOf(c) < 0 && DOOR_CHARS.indexOf(c) < 0;
}

export interface Sprite {
    id: number;      // stable id (enemy slot, pickup index) used to interpolate between ticks
    kind: number;
    frame: number;
    x: number;
    y: number;
    state: number;
}

export interface Frame {
    tick: number;
    px: number;
    py: number;
    weapon: number;
    wframe: number;
    flash: number;
    doors: string;   // 16 digits 0-9
    sprites: Sprite[];
    events: number[];
    echo: number;
}

/** tick|px|py|weapon|wframe|flash|doors|sprites|events|echo */
export function parseFrame(text: string | null): Frame | null {
    if (!text) return null;
    const f = text.split("|");
    if (f.length < 3) return null;
    const num = (s: string | undefined, d = 0) => {
        const v = parseFloat(s ?? "");
        return isFinite(v) ? v : d;
    };
    const sprites: Sprite[] = [];
    if (f[7]) {
        for (const rec of f[7].split(";")) {
            if (!rec) continue;
            const p = rec.split(",");
            if (p.length < 6) continue;
            sprites.push({ id: num(p[0]), kind: num(p[1]), frame: num(p[2]), x: num(p[3]), y: num(p[4]), state: num(p[5]) });
        }
    }
    const events: number[] = [];
    if (f[8]) {
        for (const e of f[8].split(";")) {
            const v = parseInt(e, 10);
            if (v > 0) events.push(v);
        }
    }
    return {
        tick: num(f[0]),
        px: num(f[1]),
        py: num(f[2]),
        weapon: num(f[3], 2),
        wframe: num(f[4]),
        flash: num(f[5]),
        doors: (f[6] ?? "").padEnd(16, "0"),
        sprites,
        events,
        echo: num(f[9]),
    };
}
