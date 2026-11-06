#!/usr/bin/env bash
# Deep Station - offline build of the importable solution (Linux / cloud session; no Power Platform access needed).
#   ./build.sh                 -> release/DeepStation_unmanaged.zip  (RaycastView code component + the canvas app)
#   ENEMY_SLOTS=8 ./build.sh   -> same with 8 enemy slots
#   LEVEL=m0-test ./build.sh   -> level file from levels/
# Needs: node 18+, python 3, .NET SDK 10, pac (dotnet tool install --global Microsoft.PowerApps.CLI.Tool).
set -euo pipefail
cd "$(dirname "$0")"
export PATH="$PATH:$HOME/.dotnet/tools"
APP=wrk_deepstation_m0
DIST=dist
rm -rf "$DIST" && mkdir -p "$DIST" release

# 1. code component (dotnet build of the solution runs it again in production mode)
(cd pcf && { [ -d node_modules ] || npm ci --no-audit --no-fund; } && npm run build)

# 2. canvas YAML
DEEPSTATION_ENEMY_SLOTS="${ENEMY_SLOTS:-12}" python3 tools/gen_app.py "${LEVEL:-m0-test}"

# 3. msapp: base scaffolding + generated Src
mkdir -p "$DIST/pack"
(cd canvas/base && zip -qr "../../$DIST/pack/DeepStation.msapr" .)
cp -r canvas/Src "$DIST/pack/"
pac canvas pack --sources "$DIST/pack" --msapp "$DIST/DeepStation.msapp" --layout SourceCode
cp "$DIST/DeepStation.msapp" "solution/src/CanvasApps/${APP}_DocumentUri.msapp"

# 4. solution: canvas app + RaycastView (project reference), unmanaged
(cd solution && dotnet build -c Release -nologo -v q)
cp solution/bin/Release/DeepStation.zip release/DeepStation_unmanaged.zip
unzip -l release/DeepStation_unmanaged.zip
