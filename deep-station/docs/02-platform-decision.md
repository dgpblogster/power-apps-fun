# Platform Decision: Power Fx Game, Code-Component View (Option C)

Decided 2026-11-06 (draft, confirmed at the end of spike M0). Environment: **Workbench**
(`e57d0c49-8edb-e5a5-af15-8a62479e341a`), solution **DeepStation**.

## Decision

**Build Deep Station as a canvas Power App whose game logic is Power Fx on one Timer, with a single PCF code
component (`RaycastView`) that draws the 3D view, plays sound, and captures keyboard and mouse.** Everything the
player can lose, collect, or change lives in Power Fx context variables; the code component only shows it.

This breaks the series' "standard controls only" rule once, on purpose, and only for the three things canvas
can't do for a first-person shooter.

## Options considered

| | A. Pure Power Fx raycaster | B. Port a real engine in a code component | **C. Power Fx game + code-component view** |
|---|---|---|---|
| Rendering | One SVG data URI per tick from `Concat(Sequence(...))`; fixed-step ray marching because Power Fx has no early-exit loop | Full engine in TypeScript or WebAssembly | Raycaster in TypeScript on an HTML canvas |
| Expected frame rate | Unmeasured; likely single digits to low teens at 64–128 columns, flat-shaded | 35+ | 50–60 fps, interpolated from a 20 Hz tick |
| Input | Buttons and a Slider; no held keys, no mouse look | Full | Full keyboard, pointer lock, touch |
| Where the game is | Power Fx | TypeScript; Power Apps is a frame around it | Power Fx |
| Textures, sprites clipped by walls | Not realistic | Yes | Yes |
| Licensing | Original content | GPL engine obligations; must use free game data | Original engine and content |
| Fit with the series | Best | Worst | Good: the game is still Power Fx |

Option A stays a good stretch experiment and could reuse this project's level format and Power Fx tick. Option
B was rejected because it isn't a Power Apps project any more.

## What Option C costs

1. **An environment setting.** *Power Apps component framework for canvas apps* must be turned on in
   Workbench (Admin center > Environments > Settings > Product > Features).
2. **A TypeScript toolchain.** Node, `pac pcf init`, `npm run build`, and the control packaged into the
   solution by `build.ps1`.
3. **A frozen contract.** Properties can't be removed from an imported code component, only added as optional,
   so the property list in the spec (section 3) is signed off after M0.
4. **Event discipline.** Calling `notifyOutputChanged` on every keypress or mouse move floods the host, so
   outputs are throttled to 30 per second and read by the tick instead of `OnChange`.
5. **Unknowns inside the player frame:** pointer lock, focus, and `requestAnimationFrame` behavior; M0 tests
   them and the spec defines fallbacks.

## Sources

- Code components for canvas apps (enabling the feature): https://learn.microsoft.com/power-apps/developer/component-framework/component-framework-for-canvas-apps
- Code component lifecycle (`init`, `updateView`, `getOutputs`): https://learn.microsoft.com/power-apps/developer/component-framework/custom-controls-overview
- Best practices (`notifyOutputChanged` frequency, null values in `updateView`): https://learn.microsoft.com/power-apps/developer/component-framework/code-components-best-practices
- Limitations: https://learn.microsoft.com/power-apps/developer/component-framework/limitations
- FAQ (properties can't be removed after import; Window object): https://learn.microsoft.com/power-apps/developer/component-framework/faq
- `trackContainerResize` and allocated size in canvas apps: https://learn.microsoft.com/power-apps/developer/component-framework/reference/mode/trackcontainerresize
- Timer control: https://learn.microsoft.com/power-apps/maker/canvas-apps/controls/control-timer
- Doom engine background (BSP, 35 Hz logic, fixed point) used only to choose what to simplify:
  https://www.doomwiki.org/wiki/Rendering_engine
