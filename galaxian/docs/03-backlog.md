# Galaxian Arcade — Improvement Backlog

Candidate improvements beyond the shipped build, grouped by theme. Nothing here is committed work; each item
becomes its own pull request when picked up. Status: **Idea**, **Planned**, **In progress**, **Done**.

## Input: better than the slider

The slider is the only canvas control that reports a continuous pointer position during a drag, which is why it
shipped first. All three alternatives feed the same target-X variable the tick already reads, so they can coexist
behind a settings toggle.

| # | Item | Why | Notes | Status |
|---|---|---|---|---|
| I1 | **Full-width invisible touch strip** | Drag anywhere under the ship instead of hunting for the handle | Keep the slider; make it span the lower playfield with a transparent rail and invisible handle. Styling only | Idea |
| I2 | **Keyboard via the text-input trick** | Proper keyboard play on desktop (A/D move, Space fires) | A focused Text Input receives keystrokes; the modern control exposes `TriggerOutput.Keypress`. Read the last character, act, reset the box. Must `SetFocus` the box at START and after any button press; held keys auto-repeat | Idea |
| I3 | **Tilt via the accelerometer** | Analog steering on phones and tablets | `Acceleration.X` times a gain each tick. Mobile player and most mobile browsers only; needs a fallback toggle | Idea |

Rejected: tap-to-move zones. With no press-and-hold event the ship either steps once per tap or runs until a
second tap, and both feel wrong.

## AI: where it fits a 50 ms tick

No AI call can run inside the tick. The game's natural pauses (wave clear, death, game over, attract) tolerate a
one- to three-second call. Candidates use an **AI Builder prompt** (a Dataverse AI prompt callable from Power Fx,
returning text or JSON) or a **Copilot Studio agent** through the Copilot control. Both are premium; check AI
Builder credits and the DLP policy in Workbench first.

| # | Item | Why | Notes | Status |
|---|---|---|---|---|
| A1 | **Mission debrief at game over** | Proves the AI Builder plumbing with one call and no new game logic | Prompt turns the run's numbers into three lines of Atari-manual-flavoured narration | Idea (recommended first) |
| A2 | **AI Commander that plans each wave** | The enemy learns the player; the headline feature | At wave start send level, wave, accuracy, death positions, edge-camping time; receive a JSON plan (flank bias, dive cadence curve, escort count, bomb aggression, end-phase trigger). `ParseJSON` feeds the variables the tick already reads (`nDiff`, `launchInterval`, `nBombChecks`). One call per wave | Idea |
| A3 | **Adaptive level suggestion** | Sessions that last about five minutes for each player | Log runs to the Dataverse high-score table (M8); a prompt or, with enough data, an AI Builder prediction model recommends a level. SELECT shows the recommendation | Idea |
| A4 | **Coach in the attract screen** | Demo value for a blog post | Copilot Studio agent grounded on the spec and the Atari manual via the Copilot control: "How do I get 800 points?" | Idea |
| A5 | **Classic game AI autopilot** | Fills the attract-mode demo gap; zero latency, no licensing | Power Fx autopilot that dodges bombs and lines up shots. Later: let the AI Commander (A2) play against it in attract mode | Idea |

## Remaining spec items (from docs/01-game-spec.md, section 19)

| # | Item | Notes | Status |
|---|---|---|---|
| S1 | Wave-10 surprise symbols | Chomper disc from wave 10, app logo mark from 12, player initials from 14 (originals replaced) | Planned |
| S2 | Flags past wave 16 | Wide "10" marker per ten waves plus small flags | Planned |
| S3 | Attract-mode demo divers | Pairs with A5 | Planned |
| S4 | Two-player alternating mode (OPTION) | Swap score, lives, wave, and convoy state between players | Planned |
| S5 | Sound | Needs a Studio media upload or externally hosted HTTPS clips; cannot be added through YAML | Planned |
| S6 | Dataverse high-score table (M8) | `wrk_galaxianscore` in the Galaxian solution; prerequisite for A3 | Planned |
| S7 | Publish the latest save | The play link still serves the save before the sequential-tick build | Planned |

## Done since the first build

| Item | PR |
|---|---|
| Ship speed cap 6 columns per tick, instant fire, missile 16 lines per tick, tps readout | in initial commit |
| Sequential tick (0.5 to ~20 tps), frame-counter wing flap, swept missile collision | #3 |
