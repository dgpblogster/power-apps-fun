// Local test harness: hosts RaycastView with a mock PCF context and a small JavaScript stand-in for the
// Power Fx tick (movement, doors, idle enemies). It tests the view and the contract, not the Power Fx.
import { RaycastView } from "../RaycastView/index";
import level from "./dist/level.json";

type Lv = { w: number; h: number; cells: string; light: string; start: [number, number, number];
            enemies: { kind: number; x: number; y: number }[]; items: { kind: number; x: number; y: number }[];
            decor: { kind: number; x: number; y: number }[] };
const L = level as unknown as Lv;

const host = document.getElementById("host") as HTMLDivElement;
const W = 960, H = 600;
const params: Record<string, { raw: unknown }> = {
    MapData: { raw: `${L.w},${L.h};${L.cells}` }, LightData: { raw: L.light }, Frame: { raw: "" },
    Paused: { raw: false }, ShowTouch: { raw: false }, ShowDiag: { raw: true }, Muted: { raw: true }, TickMs: { raw: 50 },
};
let outputs: Record<string, number | boolean> = {};
const ctx = { parameters: params, mode: { allocatedWidth: W, allocatedHeight: H, trackContainerResize: () => undefined } };
const view = new RaycastView();
(window as unknown as { view: unknown }).view = view;
let notifies = 0;
view.init(ctx as never, () => { notifies++; outputs = view.getOutputs() as never; }, {} as never, host);
view.updateView(ctx as never);

// ---- stand-in tick ----
const solid = (x: number, y: number, doors: string) => {
    if (x < 0 || y < 0 || x >= L.w || y >= L.h) return true;
    const i = Math.floor(y) * L.w + Math.floor(x), c = L.cells[i];
    if (".~T".includes(c)) return false;
    if ("Dacv".includes(c)) { const id = [...L.cells.slice(0, i)].filter(ch => "Dacv".includes(ch)).length; return +doors[id] < 7; }
    return true;
};
const blocked = (x: number, y: number, r: number, d: string) => solid(x - r, y - r, d) || solid(x + r, y - r, d) || solid(x - r, y + r, d) || solid(x + r, y + r, d);
let spawn = 1;
const st = { tick: 0, px: L.start[0], py: L.start[1], doors: "0".repeat(16), useSeen: 0, events: "", anim: -1, step: 0 };
const script: { [k: string]: unknown } = (window as unknown as { script: { [k: string]: unknown } }).script = {};
setInterval(() => {
    const k = (outputs.Keys as number) ?? 0, yaw = ((outputs.Yaw as number) ?? 0) * Math.PI / 180;
    const fwd = (k & 1 ? 1 : 0) - (k & 2 ? 1 : 0), str = (k & 8 ? 1 : 0) - (k & 4 ? 1 : 0), spd = k & 16 ? 0.25 : 0.15;
    const dx = (Math.cos(yaw) * fwd - Math.sin(yaw) * str) * spd, dy = (Math.sin(yaw) * fwd + Math.cos(yaw) * str) * spd;
    if (!blocked(st.px + dx, st.py, 0.25, st.doors)) st.px += dx;
    if (!blocked(st.px, st.py + dy, 0.25, st.doors)) st.py += dy;
    st.events = "";
    if (st.anim >= 0) { st.step++; st.doors = st.doors.slice(0, st.anim) + Math.min(9, st.step) + st.doors.slice(st.anim + 1); if (st.step >= 9) st.anim = -1; }
    if (((outputs.UseSeq as number) ?? 0) !== st.useSeen) {
        st.useSeen = outputs.UseSeq as number;
        const fx = st.px + Math.cos(yaw), fy = st.py + Math.sin(yaw), i = Math.floor(fy) * L.w + Math.floor(fx);
        if ("Dacv".includes(L.cells[i])) { st.anim = [...L.cells.slice(0, i)].filter(ch => "Dacv".includes(ch)).length; st.step = 0; st.events = "4"; }
    }
    st.tick++;
    const sprites = L.enemies.map((e, n) => `${n + 1},${e.kind},${Math.floor(st.tick / 5) % 2},${e.x.toFixed(2)},${(e.y + 0.15 * Math.sin(st.tick / 8 + n)).toFixed(2)},1;`).join("")
        + L.items.map((e, n) => `${101 + n},${e.kind},0,${e.x},${e.y},1;`).join("")
        + L.decor.map((e, n) => `${200 + n},${e.kind},0,${e.x},${e.y},1;`).join("");
    params.Frame.raw = [st.tick, st.px.toFixed(2), st.py.toFixed(2), 2, k & 32 ? 1 + (st.tick % 3) : 0, 0, st.doors, sprites, st.events,
                        (outputs.Stamp as number) ?? 0, `${spawn}:${L.start[2]}`].join("|");
    view.updateView(ctx as never);
    script.state = { ...st, outputs, notifies };
}, 50);
script.teleport = (x: number, y: number, yaw: number, doors?: string) => {
    st.px = x; st.py = y; if (doors) st.doors = doors; L.start[2] = yaw; spawn++;
};
setInterval(() => {
}, 50);
