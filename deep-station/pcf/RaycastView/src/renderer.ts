// Grid raycaster for Deep Station (docs/01-game-spec.md section 11).
// World: x east, y south, 1 unit per cell, walls 1 unit high. Yaw in degrees: 0 east, 90 south.
// Writes into a 320x200 Uint32 buffer; the caller blits it to the visible canvas.

import { GameMap, Sprite, isWallChar } from "./frame";
import { SHADES, TEX, TextureSet, textureFor, rgba } from "./textures";
import { SpriteArt, poseOf } from "./sprites";

export const VIEW_W = 320;
export const VIEW_H = 200;
const FOV_DEG = 66;
const PLANE = Math.tan((FOV_DEG / 2) * Math.PI / 180);
const FOG = 14;          // distance at which everything is black
const MAX_STEPS = 96;    // DDA cell steps per ray

export interface Camera {
    x: number;
    y: number;
    yaw: number;   // degrees
    bob: number;   // vertical offset in pixels, small
}

export class Renderer {
    readonly buf = new Uint32Array(VIEW_W * VIEW_H);
    readonly depth = new Float32Array(VIEW_W);
    private ceil = new Uint32Array(VIEW_H);
    private floor = new Uint32Array(VIEW_H);

    constructor(private tex: TextureSet, private art: Map<number, SpriteArt>) {
        for (let y = 0; y < VIEW_H; y++) {
            const d = Math.abs(y - VIEW_H / 2) / (VIEW_H / 2); // 0 at horizon, 1 at edge
            const k = 0.12 + 0.88 * d * d;
            this.ceil[y] = rgba(40 * k, 42 * k, 48 * k);
            this.floor[y] = rgba(70 * k, 60 * k, 50 * k);
        }
    }

    /** Shade index from light (0-9) and distance. */
    private shade(light: number, dist: number, side: number): number {
        const fog = Math.max(0, 1 - dist / FOG);
        let s = Math.round((light / 9) * fog * (SHADES - 1)) - side;
        if (s < 0) s = 0;
        if (s > SHADES - 1) s = SHADES - 1;
        return s;
    }

    render(map: GameMap, cam: Camera, doors: string, sprites: Sprite[]) {
        const { buf, depth } = this;
        const w = map.w, h = map.h, cells = map.cells;
        const rad = cam.yaw * Math.PI / 180;
        const dirX = Math.cos(rad), dirY = Math.sin(rad);
        const planeX = -dirY * PLANE, planeY = dirX * PLANE;
        const horizon = (VIEW_H >> 1) + (cam.bob | 0);

        // floor and ceiling
        for (let y = 0; y < VIEW_H; y++) {
            const c = y < horizon ? this.ceil[Math.min(VIEW_H - 1, Math.max(0, y - (cam.bob | 0)))] : this.floor[Math.min(VIEW_H - 1, Math.max(0, y - (cam.bob | 0)))];
            buf.fill(c, y * VIEW_W, (y + 1) * VIEW_W);
        }

        for (let col = 0; col < VIEW_W; col++) {
            const camX = (2 * col) / VIEW_W - 1;
            const rdx = dirX + planeX * camX;
            const rdy = dirY + planeY * camX;
            let mx = Math.floor(cam.x), my = Math.floor(cam.y);
            const ddx = rdx === 0 ? 1e30 : Math.abs(1 / rdx);
            const ddy = rdy === 0 ? 1e30 : Math.abs(1 / rdy);
            const stepX = rdx < 0 ? -1 : 1, stepY = rdy < 0 ? -1 : 1;
            let sdx = rdx < 0 ? (cam.x - mx) * ddx : (mx + 1 - cam.x) * ddx;
            let sdy = rdy < 0 ? (cam.y - my) * ddy : (my + 1 - cam.y) * ddy;
            let side = 0, dist = FOG, texIdx = 0, u = 0, lastOpen = my * w + mx, hit = false;

            for (let step = 0; step < MAX_STEPS; step++) {
                if (sdx < sdy) { sdx += ddx; mx += stepX; side = 0; } else { sdy += ddy; my += stepY; side = 1; }
                if (mx < 0 || my < 0 || mx >= w || my >= h) break;
                const i = my * w + mx;
                const c = cells[i];
                const did = map.doorId[i];
                if (did >= 0) {
                    // door panel through the middle of its cell, sliding sideways as it opens
                    const open = (doors.charCodeAt(did) - 48) / 9;
                    if (open >= 1) { lastOpen = i; continue; }
                    let t: number, along: number;
                    if (map.doorAcross[i]) { // panel on y = my + 0.5
                        if (rdy === 0) { lastOpen = i; continue; }
                        t = (my + 0.5 - cam.y) / rdy;
                        along = cam.x + t * rdx - mx;
                    } else {                 // panel on x = mx + 0.5
                        if (rdx === 0) { lastOpen = i; continue; }
                        t = (mx + 0.5 - cam.x) / rdx;
                        along = cam.y + t * rdy - my;
                    }
                    if (t > 0 && along >= open && along < 1) {
                        dist = t; texIdx = textureFor(c); u = along - open; hit = true; side = 0;
                        break;
                    }
                    lastOpen = i;
                    continue;
                }
                if (isWallChar(c)) {
                    dist = side === 0 ? sdx - ddx : sdy - ddy;
                    texIdx = textureFor(c);
                    const wx = side === 0 ? cam.y + dist * rdy : cam.x + dist * rdx;
                    u = wx - Math.floor(wx);
                    if ((side === 0 && rdx > 0) || (side === 1 && rdy < 0)) u = 1 - u;
                    hit = true;
                    break;
                }
                lastOpen = i;
            }
            if (dist < 0.05) dist = 0.05;
            depth[col] = hit ? dist : FOG;
            if (!hit) continue;

            const lineH = VIEW_H / dist;
            const top = horizon - lineH / 2;
            const y0 = Math.max(0, Math.ceil(top));
            const y1 = Math.min(VIEW_H, Math.floor(top + lineH));
            const tx = Math.min(TEX - 1, (u * TEX) | 0);
            const s = this.shade(map.light[lastOpen] ?? 7, dist, side === 1 ? 2 : 0);
            const texCol = this.tex.shaded[texIdx][s];
            const base = tx * TEX;
            const vStep = TEX / lineH;
            let v = (y0 - top) * vStep;
            for (let y = y0; y < y1; y++) {
                buf[y * VIEW_W + col] = texCol[base + (Math.min(TEX - 1, v | 0))];
                v += vStep;
            }
        }

        this.drawSprites(map, cam, sprites, dirX, dirY, planeX, planeY, horizon);
    }

    private drawSprites(map: GameMap, cam: Camera, sprites: Sprite[], dirX: number, dirY: number, planeX: number, planeY: number, horizon: number) {
        const invDet = 1 / (planeX * dirY - dirX * planeY);
        const list = sprites
            .map(s => ({ s, dx: s.x - cam.x, dy: s.y - cam.y }))
            .map(o => ({ ...o, d2: o.dx * o.dx + o.dy * o.dy }))
            .sort((a, b) => b.d2 - a.d2);
        for (const { s, dx, dy } of list) {
            const art = this.art.get(s.kind);
            if (!art) continue;
            const tX = invDet * (dirY * dx - dirX * dy);
            const tY = invDet * (-planeY * dx + planeX * dy);
            if (tY <= 0.1) continue;
            const screenX = (VIEW_W / 2) * (1 + tX / tY);
            const scale = VIEW_H / tY;
            const size = (s.state === 4 ? Math.min(art.size, 0.5) : art.size) * scale;
            const lift = s.state === 4 ? 0 : art.lift;
            const bottom = horizon + (0.5 - lift) * scale;
            const top = bottom - size;
            const left = screenX - size / 2;
            const x0 = Math.max(0, Math.ceil(left)), x1 = Math.min(VIEW_W, Math.floor(left + size));
            const y0 = Math.max(0, Math.ceil(top)), y1 = Math.min(VIEW_H, Math.floor(bottom));
            if (x0 >= x1 || y0 >= y1) continue;
            const cx = Math.max(0, Math.min(map.w - 1, Math.floor(s.x))), cy = Math.max(0, Math.min(map.h - 1, Math.floor(s.y)));
            const sh = art.fullbright ? SHADES - 1 : this.shade(map.light[cy * map.w + cx], tY, 0);
            const px = art.poses[poseOf(art, s.frame, s.state)][sh];
            const step = TEX / size;
            for (let x = x0; x < x1; x++) {
                if (tY >= this.depth[x]) continue;
                const tx = Math.min(TEX - 1, ((x - left) * step) | 0) * TEX;
                let v = (y0 - top) * step;
                for (let y = y0; y < y1; y++) {
                    const c = px[tx + Math.min(TEX - 1, v | 0)];
                    if (c >>> 24) this.buf[y * VIEW_W + x] = c;
                    v += step;
                }
            }
        }
    }
}
