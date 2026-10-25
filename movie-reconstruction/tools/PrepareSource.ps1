$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$source = Join-Path $root '..\rea\_reference\movie-review\jadx-export\sources'
$destination = Join-Path $root 'source-app\src\main\java'
if (Test-Path -LiteralPath $destination) { throw 'Source working copy already exists; preserve local edits before refreshing.' }
New-Item -ItemType Directory -Path $destination | Out-Null
& robocopy.exe $source $destination '*.java' /E /COPY:DAT /DCOPY:T /R:1 /W:1 /MT:8 /NFL /NDL /NJH /NJS /NP
if ($LASTEXITCODE -gt 7) { throw "Source copy failed: robocopy exit $LASTEXITCODE" }
[xml]$manifest = Get-Content -LiteralPath (Join-Path $root 'bytecode-app\apktool\AndroidManifest.xml') -Raw
$android = 'http://schemas.android.com/apk/res/android'
$manifest.manifest.RemoveAttribute('package')
foreach ($name in @('versionCode','versionName','compileSdkVersion','compileSdkVersionCodename')) { $manifest.manifest.RemoveAttribute($name,$android) }
foreach ($name in @('platformBuildVersionCode','platformBuildVersionName')) { $manifest.manifest.RemoveAttribute($name) }
foreach ($node in @($manifest.manifest.SelectNodes('uses-sdk'))) { [void]$manifest.manifest.RemoveChild($node) }
$manifest.Save((Join-Path $root 'source-app\src\main\AndroidManifest.xml'))
Write-Output 'Copied recovered Java into an editable working tree and prepared the AGP manifest.'
$global:LASTEXITCODE = 0
