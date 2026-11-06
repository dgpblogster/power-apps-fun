// Bundles the harness and writes the level JSON from levels/*.txt via tools/levels.py.
import { build } from "esbuild";
import { execFileSync } from "node:child_process";
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const dist = join(here, "dist");
mkdirSync(dist, { recursive: true });
const level = process.argv[2] || "m0-test";
const py = `import sys, json; sys.path.insert(0, ${JSON.stringify(join(here, "..", "..", "tools"))}); import levels
lv = levels.load(${JSON.stringify(level)})
pick = lambda ts: [{"kind": t["kind"], "x": t["x"], "y": t["y"]} for t in ts]
print(json.dumps({"w": lv.w, "h": lv.h, "cells": lv.cells, "light": lv.light, "start": lv.start,
  "enemies": pick(lv.enemies), "items": pick(lv.items), "decor": pick(lv.decor)}))`;
writeFileSync(join(dist, "level.json"), execFileSync("python3", ["-I", "-c", py]).toString());
await build({ entryPoints: [join(here, "harness.ts")], bundle: true, outfile: join(dist, "harness.js"), format: "iife", target: "es2020", logLevel: "warning" });
writeFileSync(join(dist, "index.html"), `<!doctype html><meta charset="utf-8"><title>RaycastView harness</title>
<style>body{margin:0;background:#111}#host{width:960px;height:600px}</style><div id="host"></div><script src="harness.js"></script>`);
console.log("harness built:", join(dist, "index.html"));
