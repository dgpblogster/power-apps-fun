# power-apps-fun

A collection of fun Power Platform side projects. Each top-level folder is a
self-contained project with its own README, source, and build/deploy scripts.

## Projects

| Folder | What it is |
|---|---|
| [`parametric-motions/`](parametric-motions/) | Power Apps canvas app that animates four parametric equations — Lissajous, Rose, Spiral, and Hypotrochoid — with a small circle tracing each curve. Inspired by [The Workbench blog's "PowerApps Motion Patterns"](https://www.theworkbench.blog/2019/02/powerapps-motion-patterns-with.html). Deployed as the **ParametricMotions** solution in the Workbench Dataverse environment. |
| [`proximity-collision/`](proximity-collision/) | Power Apps canvas app in which a ball senses proximity and collisions at runtime against drifting blocks and a Breakout-style paddle: closest-point gap, swept (time-to-impact) test with relative velocity, and reactive avoidance, all as Power Fx named formulas and user-defined functions. A modern take on [The Workbench blog's "Simple Object Proximity and Collision Detection"](https://www.theworkbench.blog/2019/02/powerapps-simple-object-proximity-and.html). Deployed as the **ProximityCollision** solution in the Workbench Dataverse environment. |

## Get the code

```powershell
git clone https://github.com/dgpblogster/power-apps-fun.git
cd power-apps-fun
```

### Prerequisites

- [PowerShell 7+](https://learn.microsoft.com/powershell/scripting/install/installing-powershell)
- [Power Platform CLI (`pac`)](https://learn.microsoft.com/power-platform/developer/cli/introduction) 2.11 or later — install with
  `dotnet tool install --global Microsoft.PowerApps.CLI.Tool` or the Windows installer
- A Power Platform environment you can import solutions into (Environment Maker or System Administrator role)

### Authenticate

Create (once) and select a `pac` auth profile pointing at your target environment:

```powershell
pac auth create --name MyEnv --environment <environment-id-or-url>
pac auth select --name MyEnv
pac org who        # confirm you are connected to the right environment
```

## Deploy a project into Power Apps

Each project's `build.ps1` packs the canvas app from its YAML source and wraps it in a
Dataverse solution. From the project folder (for example `parametric-motions/`):

```powershell
cd parametric-motions
.\build.ps1            # build only: dist\*.msapp + dist\*_unmanaged.zip
.\build.ps1 -Import    # build, then import the solution into the selected environment and publish
```

Prefer manual import? Run `.\build.ps1`, then in the [maker portal](https://make.powerapps.com)
go to **Solutions → Import solution** and upload `dist\*_unmanaged.zip`.

After the first import, open the app **for edit in Power Apps Studio** once (apps packed
from YAML source are validated on first open), verify it loads, then **Save and Publish**.
From then on it runs like any other canvas app.

> Note: the solution carries a publisher named `Workbench` (prefix `wrk`); importing
> creates that publisher in your environment if it doesn't already exist.

## Inside each project

Projects follow a common shape (see each project's README for specifics):

- `canvas/Src/` — canvas app source in Power Apps YAML (v3 "Source Code" schema), the source of truth
- `canvas/base/` — non-YAML `.msapp` scaffolding used to reassemble the app package
- `solution/src/` — SolutionPackager-format Dataverse solution wrapping the app
- `tools/` — helper scripts for code generation and maintenance
- `build.ps1` — builds the `.msapp` and solution zip with the Power Platform CLI (`pac`), and imports to the environment with `-Import`
- `dist/` — build output (git-ignored; regenerate with `build.ps1`)
