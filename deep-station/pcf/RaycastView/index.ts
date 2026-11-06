// Deep Station RaycastView: the 3D view for a game whose state lives in Power Fx.
// It may predict (interpolate positions, turn the camera) but never decides anything (docs/01-game-spec.md section 2).

import { IInputs, IOutputs } from "./generated/ManifestTypes";
import { Frame, GameMap, Sprite, parseFrame, parseMap } from "./src/frame";
import { Renderer, VIEW_H, VIEW_W } from "./src/renderer";
import { buildTextures } from "./src/textures";
import { buildSprites, drawWeapon } from "./src/sprites";
import { Input } from "./src/input";
import { Sound } from "./src/audio";

const NOTIFY_MS = 33;          // at most 30 output notifications per second
const DIAG_WINDOW = 60;

interface Stamped { f: Frame; at: number }

export class RaycastView implements ComponentFramework.StandardControl<IInputs, IOutputs> {
    private notify!: () => void;
    private root!: HTMLDivElement;
    private canvas!: HTMLCanvasElement;
    private g!: CanvasRenderingContext2D;
    private off!: HTMLCanvasElement;
    private og!: CanvasRenderingContext2D;
    private img!: ImageData;
    private renderer!: Renderer;
    private input!: Input;
    private sound = new Sound();

    private map: GameMap | null = null;
    private prev: Stamped | null = null;
    private cur: Stamped | null = null;
    private frameText = "";
    private spawnSeq = "";
    private paused = false;
    private showDiag = false;
    private tickMs = 50;

    private raf = 0;
    private lastT = 0;
    private lastNotify = 0;
    private ready = false;
    private fps = 0;
    private fpsCount = 0;
    private fpsAt = 0;
    private intervals: number[] = [];
    private latencies: number[] = [];
    private lastEcho = 0;
    private walkPhase = 0;
    // cosmetic feedback the view may show before the tick confirms it (it never changes game state)
    private flashUntil = 0;
    private kickUntil = 0;
    private nextLocalShot = 0;
    private hitUntil = 0;
    private killUntil = 0;
    private emptyUntil = 0;
    private lastWFrame = 0;
    private lastPos = { x: 0, y: 0 };

    public init(context: ComponentFramework.Context<IInputs>, notifyOutputChanged: () => void, _state: ComponentFramework.Dictionary, container: HTMLDivElement): void {
        this.notify = notifyOutputChanged;
        context.mode.trackContainerResize(true);

        this.root = document.createElement("div");
        this.root.style.cssText = "position:relative;width:100%;height:100%;outline:none;background:#000;overflow:hidden;";
        this.canvas = document.createElement("canvas");
        this.canvas.style.cssText = "width:100%;height:100%;display:block;image-rendering:pixelated;cursor:crosshair;";
        this.root.appendChild(this.canvas);
        container.appendChild(this.root);
        this.g = this.canvas.getContext("2d") as CanvasRenderingContext2D;

        this.off = document.createElement("canvas");
        this.off.width = VIEW_W;
        this.off.height = VIEW_H;
        this.og = this.off.getContext("2d") as CanvasRenderingContext2D;
        this.img = this.og.createImageData(VIEW_W, VIEW_H);

        this.renderer = new Renderer(buildTextures(), buildSprites());
        this.input = new Input(this.root, this.canvas, () => this.sound.unlock());

        this.lastT = performance.now();
        this.fpsAt = this.lastT;
        const loop = (t: number) => { this.raf = requestAnimationFrame(loop); this.step(t); };
        this.raf = requestAnimationFrame(loop);
    }

    public updateView(context: ComponentFramework.Context<IInputs>): void {
        const p = context.parameters;
        const w = context.mode.allocatedWidth, h = context.mode.allocatedHeight;
        if (w > 0 && h > 0 && (this.canvas.width !== w || this.canvas.height !== h)) {
            this.canvas.width = w;
            this.canvas.height = h;
        }
        const mapData = p.MapData?.raw ?? null, lightData = p.LightData?.raw ?? null;
        const key = (mapData ?? "") + "\u0000" + (lightData ?? "");
        if (!this.map || this.map.key !== key) this.map = parseMap(mapData, lightData);

        this.paused = p.Paused?.raw === true;
        this.input.setEnabled(!this.paused);
        this.showDiag = p.ShowDiag?.raw === true;
        this.input.touchForced = p.ShowTouch?.raw === true;
        if (this.input.touchForced) this.input.touchOn = true;
        this.sound.muted = p.Muted?.raw === true;
        const tm = p.TickMs?.raw;
        if (tm && tm > 0) this.tickMs = tm;

        const text = p.Frame?.raw ?? "";
        if (text && text !== this.frameText) {
            this.frameText = text;
            const f = parseFrame(text);
            if (f) this.accept(f, text);
        }
    }

    public getOutputs(): IOutputs {
        const i = this.input;
        return {
            Keys: i.keys,
            Yaw: Math.round(i.yaw * 10) / 10,
            UseSeq: i.useSeq,
            WeaponReq: i.weaponReq,
            WeaponSeq: i.weaponSeq,
            MenuSeq: i.menuSeq,
            MapSeq: i.mapSeq,
            Stamp: i.stamp,
            Fps: this.fps,
            Ready: this.ready,
        };
    }

    public destroy(): void {
        cancelAnimationFrame(this.raf);
        this.input.destroy();
        this.sound.destroy();
    }

    // ---- frames from Power Fx ----

    private accept(f: Frame, text: string) {
        const now = performance.now();
        if (this.cur && f.tick <= this.cur.f.tick && f.tick > 0) return; // stale or repeated tick
        if (this.cur) {
            const gap = now - this.cur.at;
            this.intervals.push(gap);
            if (this.intervals.length > DIAG_WINDOW) this.intervals.shift();
        }
        this.prev = this.cur;
        this.cur = { f, at: now };

        // spawn: "seq:yaw" lets Power Fx set the camera at level start; the view owns yaw afterwards
        const spawn = text.split("|")[10] ?? "";
        if (spawn && spawn !== this.spawnSeq) {
            this.spawnSeq = spawn;
            const yaw = parseFloat(spawn.split(":")[1] ?? "");
            if (isFinite(yaw)) { this.input.yaw = 0; this.input.turn(yaw); }
            this.prev = null; // no interpolation across a teleport
        }

        if (f.echo && f.echo !== this.lastEcho) {
            this.lastEcho = f.echo;
            const lat = (Math.floor(now) % 1000000000) - f.echo;
            if (lat >= 0 && lat < 5000) {
                this.latencies.push(lat);
                if (this.latencies.length > 20) this.latencies.shift();
            }
        }
        for (const e of f.events) {
            this.sound.play(e);
            if (e === 2) this.hitUntil = now + 220;
            if (e === 3) this.killUntil = now + 400;
            if (e === 9) this.emptyUntil = now + 500;
        }
        // the tick confirmed a shot: show the flash if the local press didn't already
        if (f.wframe === 1 && this.lastWFrame !== 1 && now > this.flashUntil + 150) { this.flashUntil = now + 100; this.kickUntil = now + 150; }
        this.lastWFrame = f.wframe;
    }

    // ---- animation frame ----

    private step(t: number) {
        const dt = Math.min(0.1, (t - this.lastT) / 1000);
        this.lastT = t;
        this.input.update(dt);

        this.fpsCount++;
        if (t - this.fpsAt >= 1000) {
            const f = Math.round((this.fpsCount * 1000) / (t - this.fpsAt));
            if (f !== this.fps) { this.fps = f; this.input.dirty = true; }
            this.fpsCount = 0;
            this.fpsAt = t;
        }

        this.draw(t);

        if (this.input.dirty && t - this.lastNotify >= NOTIFY_MS) {
            this.input.dirty = false;
            this.lastNotify = t;
            this.notify();
        }
    }

    private interpolated(t: number): { x: number; y: number; sprites: Sprite[] } | null {
        const cur = this.cur;
        if (!cur) return null;
        const prev = this.prev;
        if (!prev) return { x: cur.f.px, y: cur.f.py, sprites: cur.f.sprites };
        const a = Math.max(0, Math.min(1, (t - cur.at) / this.tickMs));
        const lerp = (p: number, c: number) => (Math.abs(c - p) > 2 ? c : p + (c - p) * a);
        const byId = new Map<number, Sprite>();
        for (const s of prev.f.sprites) byId.set(s.id, s);
        const sprites = cur.f.sprites.map(s => {
            const o = byId.get(s.id);
            return o && o.kind === s.kind ? { ...s, x: lerp(o.x, s.x), y: lerp(o.y, s.y) } : s;
        });
        return { x: lerp(prev.f.px, cur.f.px), y: lerp(prev.f.py, cur.f.py), sprites };
    }

    private draw(t: number) {
        const W = this.canvas.width, H = this.canvas.height;
        const g = this.g;
        const pos = this.interpolated(t);
        if (!this.map || !pos || !this.cur) {
            g.fillStyle = "#000";
            g.fillRect(0, 0, W, H);
            g.fillStyle = "#6c8";
            g.font = "16px monospace";
            g.fillText(this.map ? "waiting for the first tick..." : "waiting for MapData...", 16, 28);
            return;
        }
        const f = this.cur.f;

        // weapon bob from actual movement
        const moved = Math.hypot(pos.x - this.lastPos.x, pos.y - this.lastPos.y);
        this.lastPos = { x: pos.x, y: pos.y };
        this.walkPhase += Math.min(moved, 0.2) * 9;

        this.renderer.render(this.map, { x: pos.x, y: pos.y, yaw: this.input.yaw, bob: 0 }, f.doors, pos.sprites);
        this.img.data.set(new Uint8ClampedArray(this.renderer.buf.buffer));
        this.og.putImageData(this.img, 0, 0);

        // local fire feedback: flash and recoil on the press itself, repeating at the pistol's 8-tick cadence
        if (this.input.keys & 32) {
            if (t >= this.nextLocalShot && !this.paused) {
                this.flashUntil = t + 100;
                this.kickUntil = t + 150;
                this.nextLocalShot = t + (f.weapon === 1 ? 500 : 400);
            }
        } else if (this.nextLocalShot > t + 50) {
            this.nextLocalShot = t + 50; // allow tapping faster than the hold cadence, but not faster than the tick
        }
        const kick = t < this.kickUntil ? Math.max(1, Math.ceil(((this.kickUntil - t) / 150) * 3)) : 0;
        drawWeapon(this.og, f.weapon, Math.max(f.wframe, kick), t < this.flashUntil, Math.sin(this.walkPhase) * 6, Math.abs(Math.cos(this.walkPhase)) * 5 + 4, VIEW_W, VIEW_H);
        this.og.fillStyle = "rgba(255,255,255,0.7)";
        this.og.fillRect(VIEW_W / 2 - 3, VIEW_H / 2, 2, 1); this.og.fillRect(VIEW_W / 2 + 2, VIEW_H / 2, 2, 1);
        this.og.fillRect(VIEW_W / 2, VIEW_H / 2 - 3, 1, 2); this.og.fillRect(VIEW_W / 2, VIEW_H / 2 + 2, 1, 2);
        if (t < this.flashUntil) { // light the scene a little with the muzzle flash
            this.og.fillStyle = "rgba(255,220,140,0.10)";
            this.og.fillRect(0, 0, VIEW_W, VIEW_H);
        }
        if (t < this.hitUntil || t < this.killUntil) { // hit marker around the crosshair
            const kill = t < this.killUntil, r = kill ? 7 : 5;
            this.og.strokeStyle = kill ? "rgba(255,60,40,0.95)" : "rgba(255,240,200,0.95)";
            this.og.lineWidth = 1;
            const cx = VIEW_W / 2 + 0.5, cy = VIEW_H / 2 + 0.5;
            this.og.beginPath();
            for (const [sx, sy] of [[-1, -1], [1, -1], [-1, 1], [1, 1]]) { this.og.moveTo(cx + sx * 3, cy + sy * 3); this.og.lineTo(cx + sx * r, cy + sy * r); }
            this.og.stroke();
        }
        if (t < this.emptyUntil) {
            this.og.fillStyle = "rgba(255,200,80,0.9)";
            this.og.font = "bold 10px monospace";
            this.og.textAlign = "center";
            this.og.fillText("NO RIVETS", VIEW_W / 2, VIEW_H / 2 + 22);
            this.og.textAlign = "left";
        }
        if (f.flash) {
            this.og.fillStyle = f.flash === 1 ? "rgba(255,0,0,0.30)" : f.flash === 2 ? "rgba(255,210,60,0.22)" : "rgba(40,255,90,0.22)";
            this.og.fillRect(0, 0, VIEW_W, VIEW_H);
        }

        g.imageSmoothingEnabled = false;
        g.drawImage(this.off, 0, 0, W, H);

        if (this.paused) {
            g.fillStyle = "rgba(0,0,0,0.55)";
            g.fillRect(0, 0, W, H);
            g.fillStyle = "#e8d080";
            g.font = "bold 28px monospace";
            g.textAlign = "center";
            g.fillText("PAUSED", W / 2, H / 2);
            g.textAlign = "left";
        } else if (this.input.touchOn) {
            this.drawTouch();
        } else if (!this.input.locked && document.activeElement !== this.root) {
            g.fillStyle = "rgba(0,0,0,0.5)";
            g.fillRect(0, H - 34, W, 34);
            g.fillStyle = "#e8d080";
            g.font = "14px monospace";
            g.fillText("Click the view to play: WASD move, mouse turn, click fire, E use, Esc pause", 12, H - 12);
        }
        if (this.showDiag) this.drawDiag(W);

        if (!this.ready) { this.ready = true; this.input.dirty = true; }
    }

    private drawTouch() {
        const g = this.g, i = this.input, L = i.touchLayout();
        const sx = this.canvas.width / L.w, sy = this.canvas.height / L.h;
        g.save();
        g.scale(sx, sy);
        g.lineWidth = 3;
        const ring = (x: number, y: number, r: number, fill: string, text: string) => {
            g.fillStyle = fill; g.beginPath(); g.arc(x, y, r, 0, Math.PI * 2); g.fill();
            g.strokeStyle = "rgba(232,208,128,0.7)"; g.stroke();
            g.fillStyle = "rgba(255,240,200,0.9)"; g.font = `bold ${Math.round(r * 0.42)}px monospace`;
            g.textAlign = "center"; g.textBaseline = "middle"; g.fillText(text, x, y);
        };
        ring(L.fire.x, L.fire.y, L.r, (i.keys & 32) ? "rgba(220,80,40,0.55)" : "rgba(120,40,20,0.35)", "FIRE");
        ring(L.use.x, L.use.y, L.r * 0.8, "rgba(60,60,40,0.35)", "USE");
        if (i.stick) {
            g.strokeStyle = "rgba(232,208,128,0.5)";
            g.beginPath(); g.arc(i.stick.ox, i.stick.oy, L.stickR, 0, Math.PI * 2); g.stroke();
            g.fillStyle = "rgba(232,208,128,0.45)";
            g.beginPath(); g.arc(i.stick.x, i.stick.y, L.r * 0.55, 0, Math.PI * 2); g.fill();
        } else {
            g.fillStyle = "rgba(232,208,128,0.55)"; g.font = "13px monospace"; g.textAlign = "left"; g.textBaseline = "alphabetic";
            g.fillText("left thumb: move   right side: drag to turn", 14, L.h - 14);
        }
        g.restore();
    }

    private drawDiag(W: number) {
        const q = (a: number[], p: number) => {
            if (!a.length) return 0;
            const s = [...a].sort((x, y) => x - y);
            return Math.round(s[Math.min(s.length - 1, Math.floor(p * s.length))]);
        };
        const lines = [
            `fps ${this.fps}   keys ${this.input.keys}   weapon frame ${this.cur?.f.wframe ?? 0}`,
            `tick gap med ${q(this.intervals, 0.5)} ms  p95 ${q(this.intervals, 0.95)} ms`,
            `input->tick->view med ${q(this.latencies, 0.5)} ms  p95 ${q(this.latencies, 0.95)} ms`,
            `lock ${this.input.locked ? "on" : this.input.lockRefused ? "refused (drag mode)" : "off"}  tick ${this.cur?.f.tick ?? 0}`,
        ];
        const g = this.g;
        g.fillStyle = "rgba(0,0,0,0.6)";
        g.fillRect(W - 360, 0, 360, 18 * lines.length + 8);
        g.fillStyle = "#7fe08a";
        g.font = "13px monospace";
        lines.forEach((l, i) => g.fillText(l, W - 352, 18 + i * 18));
    }
}
