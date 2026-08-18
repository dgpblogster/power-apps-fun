# Builds the Parametric Motions canvas app (.msapp) and solution zip, and optionally imports it.
# Usage:
#   .\build.ps1            -> builds dist\ParametricMotions.msapp and dist\ParametricMotions_unmanaged.zip
#   .\build.ps1 -Import    -> also imports the solution into the currently selected pac auth profile's environment
param(
    [switch]$Import
)

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$dist = Join-Path $root "dist"
$appName = "wrk_parametricmotions_b1e07"

# 1. Fresh dist
Remove-Item "$dist\*" -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force $dist | Out-Null

# 2. Build the .msapr (zip of canvas\base: msapr-header.json + msapp\<non-YAML files>)
$stage = Join-Path $dist "pack-src"
New-Item -ItemType Directory -Force $stage | Out-Null
$msaprZip = Join-Path $dist "msapr.zip"
Compress-Archive -Path (Join-Path $root "canvas\base\*") -DestinationPath $msaprZip -Force
Move-Item $msaprZip (Join-Path $stage "ParametricMotions.msapr") -Force

# 3. Stage YAML sources and pack the msapp
Copy-Item (Join-Path $root "canvas\Src") $stage -Recurse
$msapp = Join-Path $dist "ParametricMotions.msapp"
pac canvas pack --sources $stage --msapp $msapp --layout SourceCode
if (-not (Test-Path $msapp)) { throw "pac canvas pack did not produce $msapp" }
Write-Host "Built $msapp"

# 4. Assemble the solution and pack it
Copy-Item $msapp (Join-Path $root "solution\src\CanvasApps\${appName}_DocumentUri.msapp") -Force
$zip = Join-Path $dist "ParametricMotions_unmanaged.zip"
pac solution pack --zipfile $zip --folder (Join-Path $root "solution\src") --packagetype Unmanaged
if (-not (Test-Path $zip)) { throw "pac solution pack did not produce $zip" }
Write-Host "Built $zip"

# 5. Optional import
if ($Import) {
    pac solution import --path $zip --publish-changes
}
