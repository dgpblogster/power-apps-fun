# Parametric Motions — Power Apps canvas app

A canvas app that explores four parametric equations with a small animated circle that
traces its motion across the screen, inspired by
[PowerApps Motion Patterns (The Workbench blog)](https://www.theworkbench.blog/2019/02/powerapps-motion-patterns-with.html).

Deployed to the **Workbench** environment (`e57d0c49-8edb-e5a5-af15-8a62479e341a`) inside the
unmanaged solution **ParametricMotions** (publisher **Workbench**, prefix `wrk`).

## Screens

| Screen | Curve | Equations | Parameters |
|---|---|---|---|
| `Screen1` | Home | — | Navigation cards + hamburger menu |
| `Lissajous` | Lissajous curve | x = A·sin(a·t + δ), y = B·sin(b·t) | a, b (1–9), δ (0–180°) |
| `Rose` | Rose curve | r = A·cos(k·θ) | k (1–10), A (100–290 px) |
| `Spiral` | Archimedean spiral | r = a·θ | turns (2–10) |
| `Hypotrochoid` | Hypotrochoid (spirograph) | x = (R−r)·cos t + d·cos(((R−r)/r)·t), y = (R−r)·sin t − d·sin(((R−r)/r)·t) | R (8–12), r (1–7), d (1–12) |

Every screen has a ☰ hamburger menu (scrim + slide-over panel) for navigation, parameter
sliders (changing one restarts the trace), a tracer-speed slider, Pause/Resume and Restart.

## How the animation works

- A hidden classic `Timer` (80 ms, repeating) increments a screen context variable
  `ctx<Prefix>N` (0…600) by the speed slider value on each tick.
- The trail is an `Image` control whose `Image` property builds an inline **SVG polyline**:
  `Concat(Sequence(ctxN), …)` evaluates the parametric equations at 600 samples of t and
  emits `x,y` points, URL-encoded into a `data:image/svg+xml` URI.
- The moving dot is a classic `Circle` whose X/Y evaluate the same equations at the current t.
- Because everything derives from `ctxN` + slider values, Restart is just `ctxN = 0`.

## Project layout

```
canvas/Src/*.pa.yaml     Authored app source (Power Apps YAML v3 schema) — source of truth
canvas/base/             Non-YAML msapp scaffolding (Header, Properties, References, themes)
solution/src/            SolutionPackager-format solution (Other/*.xml + CanvasApps metadata)
tools/add-menu.ps1       Generator that appends the hamburger menu block to a screen
build.ps1                Build (and optionally import) — see below
dist/                    Build output (msapp + solution zip)
```

## Build & deploy

Requires Power Platform CLI (pac) ≥ 2.11 and an auth profile for the target environment
(profile `PckWorkbench` was used).

```powershell
.\build.ps1           # dist\ParametricMotions.msapp + dist\ParametricMotions_unmanaged.zip
.\build.ps1 -Import   # ... plus `pac solution import --publish-changes`
```

The build zips `canvas/base` into a `.msapr`, stages it with `canvas/Src`, runs
`pac canvas pack --layout SourceCode` (the packed msapp carries `LoadFromYaml: true`, so
Studio rebuilds the app from the YAML on open), then packs everything into the solution zip
with `pac solution pack`.

## After importing

Per `pac canvas pack` guidance, an app packed from YAML source should be **opened for edit
in Power Apps Studio once** to validate it, then saved/published:

1. Open the app in Studio: make.powerapps.com → Workbench environment → Apps →
   *Parametric Motions* → Edit.
2. Confirm the app loads (Studio rebuilds the controls from the YAML source).
3. Save and Publish.

## Editing the app

Edit `canvas/Src/*.pa.yaml` and re-run `.\build.ps1 -Import`. Notes that bite:

- Every property value is a Power Fx formula starting with `=`.
- Any single-line value containing `: ` (including `{record: literals}`) must be wrapped
  in single quotes, or written as a `|-` block scalar.
- Control names are unique across the whole app (screen-prefixed names are used here).
- Multi-line formulas use `|-` with the `=` on the first content line.
