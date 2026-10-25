param(
    [ValidateSet('Build','Playback','BoxOffice','Verify','Install','Launch','Devices','Sources','DiagnoseSources','Dependencies','Smali','Tasks')]
    [string]$Action = 'Build',
    [string]$Serial = ''
)
$ErrorActionPreference = 'Stop'
if ($Action -eq 'BoxOffice') {
    & (Join-Path $PSScriptRoot 'tools\BuildBoxOffice.ps1')
    exit $LASTEXITCODE
}
if ($Action -eq 'Playback') {
    & (Join-Path $PSScriptRoot 'tools\BuildPlayback.ps1')
    exit $LASTEXITCODE
}
$env:JAVA_HOME = 'C:\Program Files\Android\Android Studio\jbr'
$socketTemp = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\.java-tmp'))
New-Item -ItemType Directory -Force -Path $socketTemp | Out-Null
$env:TEMP = $socketTemp
$env:TMP = $socketTemp
$env:JAVA_OPTS = "-Djava.net.preferIPv4Stack=true -Djdk.net.unixdomain.tmpdir=$socketTemp"
$env:ANDROID_HOME = 'C:\Users\AlphaDell-60\AppData\Local\Android\Sdk'
$env:ANDROID_USER_HOME = Join-Path $PSScriptRoot '.android'
$env:GRADLE_USER_HOME = Join-Path $PSScriptRoot '.gradle-user-home'
$gradle = Get-ChildItem -LiteralPath (Join-Path $env:USERPROFILE '.gradle\wrapper\dists\gradle-8.13-bin') -Recurse -Filter gradle.bat -File -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName
if (!$gradle) { $gradle = Join-Path $PSScriptRoot 'gradlew.bat' }
$task = switch ($Action) {
    'Build' { ':bytecode-app:assembleDebug' }
    'Verify' { ':bytecode-app:verifyPayload' }
    'Install' { ':bytecode-app:installDebug' }
    'Launch' { ':bytecode-app:launchApp' }
    'Devices' { ':bytecode-app:devices' }
    'Sources' { ':source-app:assembleDebug' }
    'DiagnoseSources' { ':source-app:diagnoseRecoveredJava' }
    'Dependencies' { ':source-app:dependencies' }
    'Smali' { ':bytecode-app:decodeSmali' }
    'Tasks' { 'tasks' }
}
$gradleArgs = @('--project-dir', $PSScriptRoot, '--no-daemon', '--console=plain', $task)
if ($Action -notin @('Sources','DiagnoseSources','Dependencies','Tasks')) { $gradleArgs += '-PbytecodeOnly=true' }
if ($Serial) { $gradleArgs += "-PdeviceSerial=$Serial" }
& $gradle @gradleArgs
exit $LASTEXITCODE
