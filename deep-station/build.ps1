# Deep Station - build the code component, generate the canvas YAML, push to Studio.
#
# Usage (from this folder):
#   .\build.ps1                          -> build pcf\ (npm) and regenerate canvas\Src from tools\
#   .\build.ps1 -PushPcf                 -> ... and import the RaycastView code component into the DeepStation solution
#   .\build.ps1 -Push -AppId <guid>      -> ... and compile the YAML into the live Studio coauthoring session
#   .\build.ps1 -EnemySlots 8            -> generate with 8 enemy slots instead of 12 (1-24)
#   .\build.ps1 -Level m0-test           -> level file in levels\ to build into the app
#   .\build.ps1 -SkipPcf / -SkipGenerate -> skip a step
#
# First time: run -PushPcf, then in Studio add the component once (Insert > Get more components > Code >
# RaycastView) so the app knows it, then -Push. See README.md.
param(
    [switch]$Push,
    [switch]$PushPcf,
    [switch]$SkipPcf,
    [switch]$SkipGenerate,
    [int]$EnemySlots = 12,
    [string]$Level = "m0-test",
    [string]$AppId = $env:DEEPSTATION_APP_ID,
    [string]$EnvId = "e57d0c49-8edb-e5a5-af15-8a62479e341a",
    [string]$LoginHint = $env:DEEPSTATION_LOGIN_HINT,
    [string]$Solution = "DeepStation",
    [string]$PublisherPrefix = "wrk"
)

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$pcf = Join-Path $root "pcf"
$dist = Join-Path $root "dist"

if (-not $SkipPcf) {
    Push-Location $pcf
    try {
        if (-not (Test-Path "node_modules")) { npm ci; if ($LASTEXITCODE) { throw "npm ci failed" } }
        npm run build
        if ($LASTEXITCODE) { throw "PCF build failed" }
    } finally { Pop-Location }
}

if (-not $SkipGenerate) {
    $env:DEEPSTATION_SRC = Join-Path $root "canvas\Src"
    $env:DEEPSTATION_ENEMY_SLOTS = "$EnemySlots"
    $env:DEEPSTATION_PCF_NAME = "${PublisherPrefix}_DeepStation.RaycastView"
    python (Join-Path $root "tools\gen_app.py") $Level
    if ($LASTEXITCODE) { throw "gen_app.py failed" }
    Remove-Item Env:DEEPSTATION_SRC, Env:DEEPSTATION_ENEMY_SLOTS, Env:DEEPSTATION_PCF_NAME
}

if ($PushPcf) {
    # pac pcf push needs an MSBuild project file. pac creates one with `pac pcf init`; we keep our own sources
    # and borrow only the .pcfproj from a throwaway init the first time.
    if (-not (Get-ChildItem $pcf -Filter *.pcfproj -ErrorAction SilentlyContinue)) {
        $tmp = Join-Path ([IO.Path]::GetTempPath()) ("ds-pcfinit-" + [guid]::NewGuid())
        $initDir = Join-Path $tmp "pcf"
        pac pcf init --namespace DeepStation --name RaycastView --template field --framework none --outputDirectory $initDir
        Copy-Item (Join-Path $initDir "pcf.pcfproj") (Join-Path $pcf "RaycastView.pcfproj")
        Remove-Item $tmp -Recurse -Force
        Write-Host "Created pcf\RaycastView.pcfproj (commit it)."
    }
    Push-Location $pcf
    try {
        pac pcf push --publisher-prefix $PublisherPrefix --solution-unique-name $Solution
        if ($LASTEXITCODE) { throw "pac pcf push failed" }
    } finally { Pop-Location }
}

if ($Push) {
    if (-not $AppId) { throw "Pass -AppId <guid> (from the Studio URL) or set DEEPSTATION_APP_ID." }
    New-Item -ItemType Directory -Force $dist | Out-Null
    $calls = Join-Path $dist "push-calls.json"
    $src = (Join-Path $root "canvas\Src").Replace("\", "/")
    $hint = if ($LoginHint) { ", `"login_hint`": `"$LoginHint`"" } else { "" }
    @"
[
  { "tool": "connect", "args": { "environment_id": "$EnvId", "app_id": "$AppId", "environment_category": "prod"$hint } },
  { "tool": "compile_canvas", "args": { "directoryPath": "$src" } },
  { "tool": "get_appchecker_errors", "args": {} }
]
"@ | Set-Content $calls -Encoding UTF8
    $env:MCP_TIMEOUT_MS = "300000"
    node (Join-Path $root "tools\mcp-canvas.js") $calls
}
