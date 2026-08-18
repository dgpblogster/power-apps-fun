# power-apps-fun

A collection of fun Power Platform side projects. Each top-level folder is a
self-contained project with its own README, source, and build/deploy scripts.

## Projects

| Folder | What it is |
|---|---|
| [`parametric-motions/`](parametric-motions/) | Power Apps canvas app that animates four parametric equations — Lissajous, Rose, Spiral, and Hypotrochoid — with a small circle tracing each curve. Inspired by [The Workbench blog's "PowerApps Motion Patterns"](https://www.theworkbench.blog/2019/02/powerapps-motion-patterns-with.html). Deployed as the **ParametricMotions** solution in the Workbench Dataverse environment. |

## Inside each project

Projects follow a common shape (see each project's README for specifics):

- `canvas/Src/` — canvas app source in Power Apps YAML (v3 "Source Code" schema), the source of truth
- `canvas/base/` — non-YAML `.msapp` scaffolding used to reassemble the app package
- `solution/src/` — SolutionPackager-format Dataverse solution wrapping the app
- `tools/` — helper scripts for code generation and maintenance
- `build.ps1` — builds the `.msapp` and solution zip with the Power Platform CLI (`pac`), and imports to the environment with `-Import`
- `dist/` — build output (git-ignored; regenerate with `build.ps1`)
