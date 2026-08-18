# Proximity & Collision

A Power Apps canvas app in which a ball moves through a field of obstacles that can move
too, senses how close it is to everything, predicts when its current heading would make
contact, and reacts. It is a modern take on the essence of The Workbench blog post
[Power Apps | Simple Object Proximity and Collision Detection](https://www.theworkbench.blog/2019/02/powerapps-simple-object-proximity-and.html)
(February 2019), not a port of its implementation.

The one rule the app is built around: **the ball carries no map.** Every tick it re-reads
whatever is in the world right now (a live collection of obstacles), measures the gap to
the nearest thing, predicts the time to impact along its heading, and acts on that.
Move the blocks, shove the paddle under it, and it simply reacts to the new situation.

## What you get

| Screen | Purpose |
|---|---|
| **Home** | What the app does, and the three ideas (sense, predict, react) at a glance. |
| **Arena** | The simulation: a 900x600 field with drifting blocks, a Breakout-style paddle you slide along the bottom, and the ball. A side panel shows the sensor readouts (status, nearest thing and gap, predicted contact in ticks and seconds, counters) and the tunables (speed, ball radius, sensor range, number of blocks, block drift), plus Play/Pause, Shuffle, Pilot manual/auto and steering buttons. |
| **Theory** | The formulas behind each step, in the app itself. |

Visual language in the arena (all drawn in **one SVG image** rebuilt every tick):

- white ball, its rim coloured by threat (green far, red touching), with a heading tick
- dashed cyan ring: sensor range
- dashed line + dot: the gap to the closest point of the nearest thing (the nearest block also lights up)
- amber ray + ghost circle: where the ball will be at the predicted contact on its current heading
- red pulse: contact this tick

## How the collision detection works

The 2019 post asked, per arrow press, "does my next step land inside the rectangle?" with
separate branches for each direction of travel and one hard-coded obstacle. This app asks
three different questions, for any number of obstacles, in any direction, every tick:

### 1. Sense: closest-point gap (circle vs. axis-aligned box)

```
px  = clamp(cx, bx, bx + bw)
py  = clamp(cy, by, by + bh)
gap = sqrt((cx - px)^2 + (cy - py)^2) - r        <= 0 means overlap
```

Clamping the ball's centre into a rectangle gives the closest point on that rectangle;
the distance minus the radius is the true gap. It is a signed, continuous number rather
than a yes/no, so it grades a threat level (`1 - clamp(gap / range, 0, 1)`), works on
diagonals and around corners, and the nearest obstacle is just the smallest gap in the
sensor table. The four walls are very large boxes outside the field, so they use the same
function.

### 2. Predict: swept test with relative velocity (slab method)

```
box' = box inflated by r                     (Minkowski sum: circle vs box -> point vs box)
rv   = v_ball - v_obstacle                    (relative velocity)
per axis:  t = (edge - c) / rv
tEnter = max(tx_near, ty_near),  tExit = min(tx_far, ty_far)
contact ahead  <=>  0 <= tEnter <= tExit      (tEnter = ticks until contact)
face hit = the axis whose slab is entered last
```

Because the ray uses the velocity of the ball *relative to* each obstacle, a drifting block
or a paddle you shove sideways is handled exactly like a wall. The game loop uses the same
prediction for the physics: if the earliest contact falls inside the current tick, the ball
advances only to the contact point and is then reflected, so a fast ball never tunnels
through a thin block. The panel and the amber ghost show the same number to you.

### 3. React

- **Manual pilot** (Breakout physics): you turn the heading in 15° steps; on contact the
  velocity component along the hit face is reflected (only if the ball was actually
  heading into that face). Slide the paddle to block it.
- **Auto pilot** (reactive avoidance): one rule, no path planning, no memory:
  `dir' = normalize(dir + k * threat * n)` where `n` is the unit vector from the closest
  point of the nearest thing to the ball's centre. Blocks and paddle can move; the ball
  just reacts.

## Where the logic lives (the modern part)

- **`App.Formulas`** (`canvas/Src/App.pa.yaml`) holds everything as **named formulas and
  user-defined functions**: `GapCircleBox`, `SlabEnter`/`SlabExit`, `ImpactTime`,
  `ImpactAxis`, and live named formulas `Sensor`, `Nearest`, `NextHit`, `Threat`, `Status`,
  `ThreatColor`... Any control, and the game loop, asks the same questions. This replaces the
  2019 pattern of hidden buttons used as methods.
- **A live collection** `colObstacles` (`Id, Name, Kind, X, Y, W, H, VX, VY`) holds walls,
  the paddle and the blocks. `Sensor` is `AddColumns` over it, so N obstacles cost nothing extra.
- **A Timer game loop** (`tmrArn.OnTimerEnd`, 50 ms) does one tick: read the paddle's
  velocity from the slider, optionally steer (auto pilot), sweep for the earliest contact,
  move/reflect, then move the world (`UpdateIf` on the collection).
- **One `Image` control** renders the whole scene as an SVG built with `Concat` over the
  collection, so there is nothing to keep in sync between "data" and "controls".
- Also used: `With`, `ForAll`/`Sequence`/`As`, `Index`, `Shuffle`, `RandBetween`, `Dec2Hex`,
  `Text(v, "0.0", "en-US")` for locale-safe SVG numbers.

Known simplifications: obstacles are axis-aligned rectangles; the swept test inflates
boxes by the radius with square (not rounded) corners, so a corner contact is predicted a
hair early; blocks pass through each other; the ball's speed is constant (no restitution).

## Layout

- `canvas/Src/*.pa.yaml`: app source (Power Apps YAML v3 "Source Code" schema), the source of truth
- `canvas/base/`: non-YAML `.msapp` scaffolding used to reassemble the package (`msapr-header.json` + `msapp/*`)
- `solution/src/`: SolutionPackager-format Dataverse solution **ProximityCollision** (publisher Workbench, `wrk`)
- `build.ps1`: builds `dist/ProximityCollision.msapp` and `dist/ProximityCollision_unmanaged.zip`; `-Import` also imports and publishes into the selected `pac` environment
- `dist/`: build output (git-ignored)

## Build and deploy

```powershell
pac auth select --name <your-profile>
cd proximity-collision
.\build.ps1 -Import
```

Then open **Proximity and Collision** in Power Apps Studio (edit mode) once, let it load
from the YAML source, Save, and Publish. See the repo root README for prerequisites.
