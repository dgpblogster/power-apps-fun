// Original procedural art for Deep Station, built once at load. No external files, no network calls.
// Textures are 64x64, stored as ABGR Uint32 (little-endian canvas ImageData order), with 16 pre-shaded copies.

export const TEX = 64;
export const SHADES = 16;

export type Pixels = Uint32Array;

export function rgba(r: number, g: number, b: number, a = 255): number {
    return ((a & 255) << 24 | (b & 255) << 16 | (g & 255) << 8 | (r & 255)) >>> 0;
}

// Small deterministic PRNG so the art is identical on every device.
function rng(seed: number): () => number {
    let s = seed >>> 0;
    return () => {
        s = (s + 0x6d2b79f5) >>> 0;
        let t = s;
        t = Math.imul(t ^ (t >>> 15), t | 1);
        t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
        return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
}

type Painter = (x: number, y: number, r: () => number) => [number, number, number];

function paint(seed: number, fn: Painter): Pixels {
    const r = rng(seed);
    const px = new Uint32Array(TEX * TEX);
    for (let y = 0; y < TEX; y++) {
        for (let x = 0; x < TEX; x++) {
            const [cr, cg, cb] = fn(x, y, r);
            px[y * TEX + x] = rgba(cr, cg, cb);
        }
    }
    return px;
}

const clamp = (v: number) => (v < 0 ? 0 : v > 255 ? 255 : v | 0);
const n = (r: () => number, amp: number) => (r() - 0.5) * amp;

// 1 steel panel with rivets
const steel: Painter = (x, y, r) => {
    const seam = x % 32 === 0 || y % 32 === 0;
    const rivet = (x % 32 === 4 || x % 32 === 28) && (y % 32 === 4 || y % 32 === 28);
    const base = 96 + n(r, 14) - (y % 32) * 0.4;
    if (seam) return [40, 44, 50];
    if (rivet) return [170, 175, 185];
    return [clamp(base), clamp(base + 4), clamp(base + 12)];
};
// 2 raw rock face
const rock: Painter = (x, y, r) => {
    const v = 70 + 30 * Math.sin(x * 0.31 + Math.sin(y * 0.17) * 3) + n(r, 30);
    return [clamp(v * 0.95), clamp(v * 0.8), clamp(v * 0.65)];
};
// 3 coolant pipes
const pipes: Painter = (x, y, r) => {
    const p = x % 16;
    const round = Math.cos(((p - 7.5) / 8) * Math.PI / 2);
    const band = y % 24 < 3;
    if (p === 0 || p === 15) return [25, 28, 30];
    const v = 60 + 120 * round + n(r, 8);
    return band ? [clamp(v * 0.7), clamp(v * 0.7), clamp(v * 0.75)] : [clamp(v * 0.45), clamp(v * 0.75), clamp(v * 0.8)];
};
// 4 hazard stripes
const hazard: Painter = (x, y, r) => {
    const s = Math.floor((x + y) / 8) % 2 === 0;
    const wear = n(r, 30);
    return s ? [clamp(210 + wear), clamp(170 + wear), 30] : [clamp(30 + wear / 2), clamp(30 + wear / 2), 30];
};
// 5 poured concrete
const concrete: Painter = (x, y, r) => {
    const v = 120 + n(r, 26) + (y % 16 === 0 ? -30 : 0);
    return [clamp(v), clamp(v - 2), clamp(v - 6)];
};
// 6 grate over darkness
const grate: Painter = (x, y, r) => {
    const bar = x % 8 < 2 || y % 8 < 2;
    if (bar) { const v = 110 + n(r, 20); return [clamp(v), clamp(v), clamp(v + 6)]; }
    return [12, 14, 16];
};
// 7 control bank with status lights
const bank: Painter = (x, y, r) => {
    const cellX = Math.floor(x / 8), cellY = Math.floor(y / 6);
    const inLight = x % 8 >= 2 && x % 8 <= 5 && y % 6 >= 2 && y % 6 <= 3 && cellY < 6;
    if (inLight) {
        const k = (cellX * 7 + cellY * 13) % 5;
        return k === 0 ? [240, 60, 50] : k === 1 ? [60, 230, 90] : k === 2 ? [240, 200, 60] : [30, 60, 40];
    }
    if (y >= 40) { const v = 50 + n(r, 10); return [clamp(v), clamp(v + 6), clamp(v + 4)]; }
    return [38, 48, 46];
};
// 8 rusted plate
const rust: Painter = (x, y, r) => {
    const v = r();
    const blotch = Math.sin(x * 0.2) * Math.cos(y * 0.23) > 0.3;
    return blotch ? [clamp(140 + v * 40), clamp(70 + v * 20), 30] : [clamp(90 + v * 20), clamp(85 + v * 20), clamp(80 + v * 20)];
};
// 9 rock with a glowing crystal vein (from below)
const vein: Painter = (x, y, r) => {
    const d = Math.abs(y - 32 - 12 * Math.sin(x * 0.12));
    if (d < 2.5) return [clamp(120 + n(r, 40)), 255, clamp(220 + n(r, 30))];
    if (d < 5) return [40, clamp(140 - d * 10), 130];
    return rock(x, y, r);
};
// door: heavy blast slab with a lit slit
const door: Painter = (x, y, r) => {
    if (x < 3 || x > 60) return [50, 50, 54];
    if (x >= 30 && x <= 33) return y % 8 < 4 ? [240, 180, 40] : [120, 80, 20];
    const v = 130 + n(r, 12);
    const stripe = y > 50 && Math.floor((x + y) / 6) % 2 === 0;
    return stripe ? [200, 160, 30] : [clamp(v), clamp(v - 6), clamp(v - 20)];
};
// exit switch panel
const exitSw: Painter = (x, y, r) => {
    const inPlate = x > 18 && x < 46 && y > 14 && y < 50;
    const lever = x > 28 && x < 36 && y > 20 && y < 40;
    if (lever) return [220, 40, 40];
    if (inPlate) return [70, 70, 76];
    return steel(x, y, r);
};
// secret wall: steel with a faint scuff (fair hint)
const secret: Painter = (x, y, r) => {
    const [a, b, c] = steel(x, y, r);
    return x > 40 && x < 52 && y > 44 && y < 50 ? [a - 20, b - 20, c - 20] : [a, b, c];
};

export interface TextureSet {
    /** [texture index][shade 0..15] -> 64x64 pixels, column-major for fast vertical strips */
    shaded: Pixels[][];
}

/** Map cell character to texture index. */
export function textureFor(c: string): number {
    if (c >= "1" && c <= "9") return c.charCodeAt(0) - 49; // 0..8
    switch (c) {
        case "D": case "a": case "c": case "v": return 9;
        case "X": return 10;
        case "S": return 11;
        default: return 0;
    }
}

export function buildTextures(): TextureSet {
    const painters = [steel, rock, pipes, hazard, concrete, grate, bank, rust, vein, door, exitSw, secret];
    const shaded: Pixels[][] = painters.map((p, i) => {
        const base = paint(1000 + i * 77, p);
        // transpose to column-major: column x is contiguous, so a wall strip reads sequentially
        const col = new Uint32Array(TEX * TEX);
        for (let y = 0; y < TEX; y++) for (let x = 0; x < TEX; x++) col[x * TEX + y] = base[y * TEX + x];
        return shadeCopies(col);
    });
    return { shaded };
}

export function shadeCopies(px: Pixels): Pixels[] {
    const out: Pixels[] = [];
    for (let s = 0; s < SHADES; s++) {
        const k = (s + 1) / SHADES;
        const c = new Uint32Array(px.length);
        for (let i = 0; i < px.length; i++) {
            const v = px[i];
            const a = v >>> 24;
            if (a === 0) { c[i] = 0; continue; }
            c[i] = rgba((v & 255) * k, ((v >>> 8) & 255) * k, ((v >>> 16) & 255) * k, a);
        }
        out.push(c);
    }
    return out;
}
