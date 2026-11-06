// Touch test: landscape phone emulation; synthetic touch pointer events for stick, look, and FIRE.
import { createRequire } from "node:module";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
const { chromium, devices } = createRequire(import.meta.url)("playwright");

const here = dirname(fileURLToPath(import.meta.url));
const browser = await chromium.launch();
const ctx = await browser.newContext({ ...devices["Pixel 7 landscape"] });
const page = await ctx.newPage();
const errors = [];
page.on("pageerror", e => errors.push(e.message));
await page.goto("file://" + join(here, "dist", "index.html"));
await page.waitForTimeout(600);
const touch = (type, id, x, y) => page.evaluate(([type, id, x, y]) => {
  const c = document.querySelector("canvas"), r = c.getBoundingClientRect();
  c.dispatchEvent(new PointerEvent(type, { pointerId: id, pointerType: "touch", clientX: r.left + x, clientY: r.top + y, bubbles: true, cancelable: true, isPrimary: id === 1 }));
}, [type, id, x, y]);
const state = () => page.evaluate(() => window.script.state);
const s0 = await state();
// left thumb: push the stick up (forward) and hold
await touch("pointerdown", 1, 150, 400); await touch("pointermove", 1, 150, 330);
await page.waitForTimeout(1000);
const s1 = await state();
await touch("pointerup", 1, 150, 330);
// right thumb: swipe left to turn
await touch("pointerdown", 2, 700, 300);
for (let i = 1; i <= 10; i++) { await touch("pointermove", 2, 700 - i * 15, 300); await page.waitForTimeout(16); }
await touch("pointerup", 2, 550, 300);
const s2 = await state();
// FIRE button (bottom right) held while the stick is held
const L = await page.evaluate(() => { const c = document.querySelector("canvas"); return { w: c.clientWidth, h: c.clientHeight }; });
const r = Math.max(34, Math.min(L.w, L.h) * 0.085);
await touch("pointerdown", 3, 150, 400); await touch("pointermove", 3, 150, 340);
await touch("pointerdown", 4, L.w - r * 1.6, L.h - r * 1.6);
await page.waitForTimeout(150);
const s3 = await state();
await page.screenshot({ path: join(here, "dist", "m0-touch.png") });
await touch("pointerup", 4, 0, 0); await touch("pointerup", 3, 0, 0);
await browser.close();
console.log(JSON.stringify({
  view: L,
  start: { px: s0.px, py: s0.py, yaw: s0.outputs.Yaw },
  afterStick: { px: s1.px, py: s1.py, keys: s1.outputs.Keys },
  afterSwipe: { yaw: s2.outputs.Yaw, keys: s2.outputs.Keys },
  fireWithStick: { keys: s3.outputs.Keys },
  errors,
}, null, 1));
