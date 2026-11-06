// Original procedural sprites for Deep Station (machines of a mining station, pickups, the player's weapon).
// Drawn once with the 2D canvas API, then stored column-major with 16 shade copies, like the textures.

import { Pixels, SHADES, TEX, shadeCopies } from "./textures";

export const KIND = {
    drone: 1,
    crawler: 2,
    welder: 3,
    brute: 4,
    warden: 5,
    bolt: 10,       // enemy plasma bolt
    charge: 11,     // player's mining charge
    medVial: 20,
    medkit: 21,
    rivets: 22,
    shells: 23,
    cells: 24,
    charges: 25,
    vest: 26,
    chipAmber: 27,
    chipCyan: 28,
    chipViolet: 29,
    lamp: 40,
    barrel: 41,
} as const;

/** Pose index: 0,1 walk; 2 attack; 3 pain; 4 dead. */
export interface SpriteArt {
    poses: Pixels[][];   // [pose][shade]
    size: number;        // world height in cells
    lift: number;        // bottom elevation in cells (0 = on the floor)
    fullbright: boolean; // ignores light (bolts, lamps)
}

type Draw = (g: CanvasRenderingContext2D, pose: number) => void;

function makeArt(draw: Draw, poses: number, size: number, lift: number, fullbright = false): SpriteArt {
    const out: Pixels[][] = [];
    const cv = document.createElement("canvas");
    cv.width = TEX;
    cv.height = TEX;
    const g = cv.getContext("2d", { willReadFrequently: true }) as CanvasRenderingContext2D;
    for (let p = 0; p < poses; p++) {
        g.clearRect(0, 0, TEX, TEX);
        g.save();
        draw(g, p);
        g.restore();
        const data = g.getImageData(0, 0, TEX, TEX).data;
        const col = new Uint32Array(TEX * TEX);
        for (let y = 0; y < TEX; y++) {
            for (let x = 0; x < TEX; x++) {
                const i = (y * TEX + x) * 4;
                const a = data[i + 3] > 128 ? 255 : 0; // hard edges: pixel-art look, cheap transparency test
                col[x * TEX + y] = a ? ((255 << 24) | (data[i + 2] << 16) | (data[i + 1] << 8) | data[i]) >>> 0 : 0;
            }
        }
        out.push(fullbright ? Array(SHADES).fill(col) : shadeCopies(col));
    }
    return { poses: out, size, lift, fullbright };
}

function circle(g: CanvasRenderingContext2D, x: number, y: number, r: number, fill: string) {
    g.fillStyle = fill;
    g.beginPath();
    g.arc(x, y, r, 0, Math.PI * 2);
    g.fill();
}

// Drone: a floating survey sphere with one sensor eye and two thruster pods.
const drone: Draw = (g, pose) => {
    if (pose === 4) { // wreck on the floor
        g.fillStyle = "#3a3d44"; g.fillRect(12, 50, 40, 10);
        g.fillStyle = "#5c616b"; g.fillRect(18, 46, 22, 6);
        circle(g, 30, 52, 3, "#401010");
        return;
    }
    const bob = pose === 1 ? 2 : 0;
    const cy = 30 + bob;
    g.fillStyle = "#2c2f35"; g.fillRect(6, cy - 4, 10, 10); g.fillRect(48, cy - 4, 10, 10);
    const grad = g.createRadialGradient(26, cy - 8, 3, 32, cy, 20);
    grad.addColorStop(0, "#c9ced8"); grad.addColorStop(1, "#4a4f59");
    circle(g, 32, cy, 18, "#000");
    g.fillStyle = grad; g.beginPath(); g.arc(32, cy, 17, 0, Math.PI * 2); g.fill();
    g.fillStyle = "#23262c"; g.fillRect(16, cy + 1, 32, 3);
    const eye = pose === 3 ? "#ffffff" : pose === 2 ? "#ffd040" : "#ff3020";
    circle(g, 32, cy - 2, 6, "#120808");
    circle(g, 32, cy - 2, 4, eye);
    g.fillStyle = "#ff8040"; g.fillRect(9, cy + 6, 4, 3 + bob); g.fillRect(51, cy + 6, 4, 3 + bob);
};

// Crawler: a low, six-legged maintenance unit with cutting mandibles.
const crawler: Draw = (g, pose) => {
    if (pose === 4) { g.fillStyle = "#4a3b2a"; g.fillRect(8, 54, 48, 8); return; }
    const s = pose === 1 ? 3 : 0;
    g.strokeStyle = "#2a2a2a"; g.lineWidth = 3;
    for (let i = 0; i < 3; i++) {
        g.beginPath(); g.moveTo(22, 46); g.lineTo(6 + i * 4, 62 - (i === 1 ? s : 0)); g.stroke();
        g.beginPath(); g.moveTo(42, 46); g.lineTo(58 - i * 4, 62 - (i === 1 ? 0 : s)); g.stroke();
    }
    g.fillStyle = "#8a6a30"; g.fillRect(16, 38, 32, 14);
    g.fillStyle = "#c09040"; g.fillRect(18, 36, 28, 4);
    g.fillStyle = pose === 3 ? "#fff" : "#40ff70"; g.fillRect(24, 42, 4, 3); g.fillRect(36, 42, 4, 3);
    g.fillStyle = "#ccc"; const m = pose === 2 ? 4 : 0;
    g.fillRect(24 - m, 50, 4, 8); g.fillRect(36 + m, 50, 4, 8);
};

// Generic stand-in for kinds that arrive in later milestones: a hooded welding robot silhouette.
const welder: Draw = (g, pose) => {
    if (pose === 4) { g.fillStyle = "#2b3a3a"; g.fillRect(10, 54, 44, 8); return; }
    g.fillStyle = "#355"; g.fillRect(22, 18, 20, 32);
    g.fillStyle = "#466"; g.fillRect(18, 10, 28, 12);
    g.fillStyle = pose === 3 ? "#fff" : "#60e0ff"; g.fillRect(24, 14, 16, 4);
    g.fillStyle = "#233"; g.fillRect(22 + (pose === 1 ? 2 : 0), 50, 6, 12); g.fillRect(36 - (pose === 1 ? 2 : 0), 50, 6, 12);
    g.fillStyle = pose === 2 ? "#a0f0ff" : "#567"; g.fillRect(42, 28, 14, 5);
};

const pickup = (body: string, mark: string, label: (g: CanvasRenderingContext2D) => void): Draw => (g) => {
    g.fillStyle = "#111"; g.fillRect(18, 44, 28, 18);
    g.fillStyle = body; g.fillRect(19, 45, 26, 16);
    g.fillStyle = mark;
    label(g);
};
const medkit = pickup("#e8e8e8", "#d02020", (g) => { g.fillRect(29, 47, 6, 12); g.fillRect(26, 50, 12, 6); });
const medVial: Draw = (g) => { g.fillStyle = "#222"; g.fillRect(27, 48, 10, 14); g.fillStyle = "#ff4060"; g.fillRect(28, 52, 8, 9); g.fillStyle = "#ddd"; g.fillRect(28, 49, 8, 3); };
const rivets = pickup("#806030", "#d0d0d0", (g) => { for (let i = 0; i < 4; i++) g.fillRect(22 + i * 6, 49, 3, 8); });
const chip = (c: string): Draw => (g) => { g.fillStyle = "#111"; g.fillRect(24, 46, 16, 14); g.fillStyle = c; g.fillRect(25, 47, 14, 12); g.fillStyle = "#222"; g.fillRect(28, 50, 8, 2); };
const bolt: Draw = (g) => { circle(g, 32, 32, 9, "#2080ff"); circle(g, 32, 32, 5, "#c0f0ff"); };
const lamp: Draw = (g) => { g.fillStyle = "#333"; g.fillRect(30, 20, 4, 44); circle(g, 32, 16, 8, "#ffe8a0"); };
const barrel: Draw = (g) => { g.fillStyle = "#2a4d2a"; g.fillRect(20, 30, 24, 34); g.fillStyle = "#3d6b3d"; g.fillRect(22, 30, 6, 34); g.fillStyle = "#d0c030"; g.fillRect(20, 40, 24, 3); };

export function buildSprites(): Map<number, SpriteArt> {
    const m = new Map<number, SpriteArt>();
    m.set(KIND.drone, makeArt(drone, 5, 0.75, 0.25));
    m.set(KIND.crawler, makeArt(crawler, 5, 0.6, 0));
    m.set(KIND.welder, makeArt(welder, 5, 0.9, 0));
    m.set(KIND.brute, makeArt(welder, 5, 1.0, 0));
    m.set(KIND.warden, makeArt(welder, 5, 1.2, 0));
    m.set(KIND.bolt, makeArt(bolt, 1, 0.3, 0.35, true));
    m.set(KIND.charge, makeArt(bolt, 1, 0.25, 0.35, true));
    m.set(KIND.medVial, makeArt(medVial, 1, 0.5, 0));
    m.set(KIND.medkit, makeArt(medkit, 1, 0.5, 0));
    m.set(KIND.rivets, makeArt(rivets, 1, 0.5, 0));
    m.set(KIND.chipAmber, makeArt(chip("#ffb020"), 1, 0.5, 0));
    m.set(KIND.chipCyan, makeArt(chip("#20e0e0"), 1, 0.5, 0));
    m.set(KIND.chipViolet, makeArt(chip("#b050ff"), 1, 0.5, 0));
    m.set(KIND.lamp, makeArt(lamp, 1, 1.0, 0, true));
    m.set(KIND.barrel, makeArt(barrel, 1, 0.7, 0));
    return m;
}

/** Pose for a sprite record: state 4 is dead; frame 2 attack, 3 pain, else walk frames 0/1. */
export function poseOf(art: SpriteArt, frame: number, state: number): number {
    if (art.poses.length === 1) return 0;
    if (state === 4) return 4;
    if (frame === 2 || frame === 3) return frame;
    return frame & 1;
}

/** Player weapons drawn on a 2D canvas at view resolution (320 wide). Frame 0 idle, 1-3 firing. */
/** flash: draw the muzzle flash (the view shows it at once on a local press, then as the tick confirms). */
export function drawWeapon(g: CanvasRenderingContext2D, weapon: number, wframe: number, flash: boolean, bobX: number, bobY: number, w: number, h: number) {
    const cx = w / 2 + bobX;
    const by = h + bobY;
    const fire = wframe > 0;
    g.save();
    if (weapon === 1) { // pipe wrench
        const swing = fire ? (wframe === 1 ? -30 : wframe === 2 ? -10 : 0) : 0;
        g.fillStyle = "#6a6f78"; g.fillRect(cx + 20 + swing, by - 70, 12, 70);
        g.fillStyle = "#8a8f98"; g.fillRect(cx + 10 + swing, by - 82, 32, 16);
        g.fillStyle = "#c08850"; g.fillRect(cx + 30, by - 30, 26, 30);
    } else { // rivet pistol (default for M0 and any later weapon without art)
        if (flash) {
            g.fillStyle = "#ffe080"; g.beginPath(); g.arc(cx, by - 74, 12, 0, Math.PI * 2); g.fill();
            g.fillStyle = "#fff8d0"; g.beginPath(); g.arc(cx, by - 74, 6, 0, Math.PI * 2); g.fill();
        }
        const kick = fire ? (wframe === 1 ? 6 : wframe === 2 ? 3 : 1) : 0;
        g.fillStyle = "#2b2e33"; g.fillRect(cx - 9, by - 66 + kick, 18, 40);
        g.fillStyle = "#4a4f57"; g.fillRect(cx - 7, by - 64 + kick, 6, 36);
        g.fillStyle = "#c06020"; g.fillRect(cx - 9, by - 46 + kick, 18, 4);
        g.fillStyle = "#b08060"; g.fillRect(cx - 16, by - 26 + kick, 32, 26);
        g.fillStyle = "#906040"; g.fillRect(cx - 16, by - 26 + kick, 6, 26);
    }
    g.restore();
}
