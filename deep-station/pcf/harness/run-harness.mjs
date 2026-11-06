// Drives the harness in headless Chromium: walks, turns, opens a door, measures fps and output rate, saves screenshots.
import { createRequire } from "node:module";
const { chromium } = createRequire(import.meta.url)("playwright");
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const shots = process.argv[2] || join(here, "dist");
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 960, height: 600 } });
const errors = [];
page.on("pageerror", e => errors.push(e.message));
page.on("console", m => { if (m.type() === "error") errors.push(m.text()); });
await page.goto("file://" + join(here, "dist", "index.html"));
await page.waitForTimeout(800);
await page.click("#host", { position: { x: 480, y: 300 } });         // focus (pointer lock is refused headless)
const state = () => page.evaluate(() => window.script.state);
await page.screenshot({ path: join(shots, "m0-start.png") });

// turn right 90 degrees with the arrow key (180 deg/s), then walk forward toward the first door
await page.keyboard.down("ArrowRight"); await page.waitForTimeout(500); await page.keyboard.up("ArrowRight");
await page.keyboard.down("ArrowLeft"); await page.waitForTimeout(500); await page.keyboard.up("ArrowLeft");
await page.keyboard.down("KeyW"); await page.waitForTimeout(1200); await page.keyboard.up("KeyW");
const s1 = await state();
await page.keyboard.press("KeyE");                                    // open the door ahead
await page.waitForTimeout(700);
const s2 = await state();
await page.keyboard.down("KeyW"); await page.waitForTimeout(900); await page.keyboard.up("KeyW");
await page.keyboard.down("ControlLeft"); await page.waitForTimeout(60);
await page.screenshot({ path: join(shots, "m0-door.png") });
await page.keyboard.up("ControlLeft");
await page.waitForTimeout(2500);
const s3 = await state();
// scene: corridor east of the start room, door 2 half open, drones ahead
await page.evaluate(() => window.script.teleport(9.5, 3.0, 0, "0500000000000000"));
await page.waitForTimeout(600);
await page.screenshot({ path: join(shots, "m0-drones.png") });
await page.evaluate(() => window.script.teleport(2.5, 8.5, 40, "0000000000000000"));
await page.waitForTimeout(600);
await page.screenshot({ path: join(shots, "m0-dark-room.png") });
await browser.close();
console.log(JSON.stringify({
  afterWalk: { px: s1.px, py: s1.py, yaw: s1.outputs.Yaw },
  afterUse: { doors: s2.doors, useSeq: s2.outputs.UseSeq },
  end: { px: s3.px, py: s3.py, tick: s3.tick, fps: s3.outputs.Fps, notifies: s3.notifies, ready: s3.outputs.Ready },
  errors,
}, null, 1));
