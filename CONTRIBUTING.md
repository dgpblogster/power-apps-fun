# Contributing

All changes to this repository land through a pull request. The `main` branch is protected: direct pushes,
force pushes, and branch deletion are blocked for everyone, including the repository owner.

## Workflow

1. Fork the repository (or create a branch if you are a collaborator).
2. Make your change in a branch named for the work, for example `galaxian/two-player-mode`.
3. Build the project you touched from its folder, for example `cd galaxian; .\build.ps1`, and confirm it
   packs cleanly. For canvas apps, open the result in Power Apps Studio once to validate the YAML.
4. Open a pull request against `main`. Describe what changed and how you tested it. Resolve every review
   conversation before merging.

## Project conventions

- Each top-level folder is a self-contained project with its own `README.md`, source, and `build.ps1`.
- Canvas app source lives in `canvas/Src/*.pa.yaml`. In `galaxian/` that YAML is **generated** by
  `tools/gen_app.py`; edit `tools/game_logic.py`, `tools/sprites.py`, or `tools/gen_app.py` and regenerate
  rather than editing the YAML by hand.
- Keep art, sound, and text original. These projects are homages and are not affiliated with the rights
  holders of the games that inspired them.
