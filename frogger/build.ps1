# Frogger - generate, push, pack, import, publish. Carried over from galaxian/build.ps1.
#
# Usage (from this folder):
#   .\build.ps1                 -> regenerate canvas\Src from tools\ (and pack if canvas\base and solution\src exist)
#   .\build.ps1 -Push           -> ... and compile the YAML into the live Power Apps Studio coauthoring session
#   .\build.ps1 -Import         -> ... and import the solution zip into the selected pac environment
#   .\build.ps1 -Publish        -> publish the last saved version through the Power Apps API (az login to the tenant first)
#   .\build.ps1 -SkipGenerate   -> use canvas\Src as it is
#
param(
    [switch]$Push,
    [switch]$Import,
    [switch]$Publish,
    [switch]$SkipGenerate
)

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$dist = Join-Path $root "dist"
$appName = "wrk_frogger_103d1"
$envId = "e57d0c49-8edb-e5a5-af15-8a62479e341a"
$appId = "80f9c4ce-e9a8-4dd1-a8d2-a9bb969fc958"
$loginHint = "marianog@maximumglobal.biz"

if (-not $SkipGenerate) {
    $env:FROGGER_SRC = Join-Path $root "canvas\Src"
    python (Join-Path $root "tools\gen_app.py")
    Remove-Item Env:FROGGER_SRC
}

$havePack = (Test-Path (Join-Path $root "canvas\base")) -and (Test-Path (Join-Path $root "solution\src"))
if ($havePack) {
    Remove-Item "$dist\*" -Recurse -Force -ErrorAction SilentlyContinue
    New-Item -ItemType Directory -Force $dist | Out-Null
    $stage = Join-Path $dist "pack-src"
    New-Item -ItemType Directory -Force $stage | Out-Null
    $msaprZip = Join-Path $dist "msapr.zip"
    Compress-Archive -Path (Join-Path $root "canvas\base\*") -DestinationPath $msaprZip -Force
    Move-Item $msaprZip (Join-Path $stage "Frogger.msapr") -Force
    Copy-Item (Join-Path $root "canvas\Src") $stage -Recurse
    $msapp = Join-Path $dist "Frogger.msapp"
    pac canvas pack --sources $stage --msapp $msapp --layout SourceCode
    if (-not (Test-Path $msapp)) { throw "pac canvas pack did not produce $msapp" }
    Copy-Item $msapp (Join-Path $root "solution\src\CanvasApps\${appName}_DocumentUri.msapp") -Force
    $zip = Join-Path $dist "Frogger_unmanaged.zip"
    pac solution pack --zipfile $zip --folder (Join-Path $root "solution\src") --packagetype Unmanaged
    if (-not (Test-Path $zip)) { throw "pac solution pack did not produce $zip" }
    Write-Host "Built $msapp and $zip"
    if ($Import) { pac solution import --path $zip --publish-changes }
} elseif ($Import) {
    Write-Warning "No canvas\base or solution\src yet; export the solution first (see CLAUDE.md). Skipping pack/import."
}

if ($Push) {
    New-Item -ItemType Directory -Force $dist | Out-Null
    $calls = Join-Path $dist "push-calls.json"
    $src = (Join-Path $root "canvas\Src").Replace("\", "/")
    @"
[
  { "tool": "connect", "args": { "environment_id": "$envId", "app_id": "$appId", "environment_category": "prod", "login_hint": "$loginHint" } },
  { "tool": "compile_canvas", "args": { "directoryPath": "$src" } }
]
"@ | Set-Content $calls -Encoding UTF8
    $env:MCP_TIMEOUT_MS = "300000"
    node (Join-Path $root "tools\mcp-canvas.js") $calls
}

if ($Publish) {
    $tok = az account get-access-token --resource "https://service.powerapps.com/" --query accessToken -o tsv
    $uri = "https://api.powerapps.com/providers/Microsoft.PowerApps/apps/$appId/publish?api-version=2017-05-01"
    $resp = Invoke-WebRequest -Method Post -Uri $uri -Headers @{ Authorization = "Bearer $tok"; "Content-Type" = "application/json" } -Body "{}"
    Write-Host "Publish status: $($resp.StatusCode)"
}
