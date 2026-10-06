# Galaxian Arcade - build, push, import, publish.
#
# Usage (from this folder):
#   .\build.ps1                 -> regenerate canvas\Src from tools\, build dist\GalaxianArcade.msapp and dist\Galaxian_unmanaged.zip
#   .\build.ps1 -Push           -> ... and compile the YAML into the live Power Apps Studio coauthoring session (validates + applies)
#   .\build.ps1 -Import         -> ... and import the solution zip into the selected pac environment
#   .\build.ps1 -Publish        -> publish the last saved version of the app through the Power Apps API (needs az login to the tenant)
#   .\build.ps1 -SkipGenerate   -> do not run the Python generator (use canvas\Src as it is)
#
# Requirements: pac CLI 2.12+, Python 3 (generator), Node 20+ and .NET 10 SDK (for -Push), Azure CLI (for -Publish).
param(
    [switch]$Push,
    [switch]$Import,
    [switch]$Publish,
    [switch]$SkipGenerate
)

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$dist = Join-Path $root "dist"
$appName = "wrk_galaxianarcade_13ba2"
$envId = "e57d0c49-8edb-e5a5-af15-8a62479e341a"
$appId = "d54c1069-9192-4e86-a6ec-db2d5f66ff2c"
$loginHint = "marianog@maximumglobal.biz"

# 1. Regenerate YAML from the generator (tools\game_logic.py + tools\sprites.py -> canvas\Src)
if (-not $SkipGenerate) {
    $env:GALAXIAN_SRC = Join-Path $root "canvas\Src"
    python (Join-Path $root "tools\gen_app.py")
    Remove-Item Env:GALAXIAN_SRC
}

# 2. Fresh dist
Remove-Item "$dist\*" -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force $dist | Out-Null

# 3. Build the .msapr (zip of canvas\base: msapr-header.json + msapp\<non-YAML files>)
$stage = Join-Path $dist "pack-src"
New-Item -ItemType Directory -Force $stage | Out-Null
$msaprZip = Join-Path $dist "msapr.zip"
Compress-Archive -Path (Join-Path $root "canvas\base\*") -DestinationPath $msaprZip -Force
Move-Item $msaprZip (Join-Path $stage "GalaxianArcade.msapr") -Force

# 4. Stage YAML sources and pack the msapp
Copy-Item (Join-Path $root "canvas\Src") $stage -Recurse
$msapp = Join-Path $dist "GalaxianArcade.msapp"
pac canvas pack --sources $stage --msapp $msapp --layout SourceCode
if (-not (Test-Path $msapp)) { throw "pac canvas pack did not produce $msapp" }
Write-Host "Built $msapp"

# 5. Assemble the solution and pack it
Copy-Item $msapp (Join-Path $root "solution\src\CanvasApps\${appName}_DocumentUri.msapp") -Force
$zip = Join-Path $dist "Galaxian_unmanaged.zip"
pac solution pack --zipfile $zip --folder (Join-Path $root "solution\src") --packagetype Unmanaged
if (-not (Test-Path $zip)) { throw "pac solution pack did not produce $zip" }
Write-Host "Built $zip"

# 6. Optional: compile into the live coauthoring session (the app must be open in Studio with coauthoring on)
if ($Push) {
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

# 7. Optional import
if ($Import) {
    pac solution import --path $zip --publish-changes
}

# 8. Optional publish of the last saved version through the Power Apps API
if ($Publish) {
    $tok = az account get-access-token --resource "https://service.powerapps.com/" --query accessToken -o tsv
    $uri = "https://api.powerapps.com/providers/Microsoft.PowerApps/apps/$appId/publish?api-version=2017-05-01"
    $resp = Invoke-WebRequest -Method Post -Uri $uri -Headers @{ Authorization = "Bearer $tok"; "Content-Type" = "application/json" } -Body "{}"
    Write-Host "Publish status: $($resp.StatusCode)"
}
