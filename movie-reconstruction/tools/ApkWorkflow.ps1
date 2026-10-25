param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('Prepare','Assemble','Verify','Install','Launch','Devices','DecodeSmali')]
    [string]$Action,
    [string]$Serial = ''
)
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$original = [IO.Path]::GetFullPath((Join-Path $root '..\Movie.apk'))
$expectedApkHash = 'cdc0d88ebcd6ad10d04e9e09f8b75fdeabd91369b9a524827cabfcbb9e7ad4f9'
$javaHome = 'C:\Program Files\Java\jdk-17'
$java = Join-Path $javaHome 'bin\java.exe'
$sdk = 'C:\Users\AlphaDell-60\AppData\Local\Android\Sdk'
$buildTools = Join-Path $sdk 'build-tools\36.1.0'
$adb = Join-Path $sdk 'platform-tools\adb.exe'
$apktool = Join-Path $PSScriptRoot 'apktool.jar'
$framework = Join-Path $PSScriptRoot 'framework'
$decoded = Join-Path $root 'bytecode-app\apktool'
$reports = Join-Path $root 'reports'
$output = Join-Path $root 'bytecode-app\build\outputs\apk\rebuilt-debug'
$signed = Join-Path $output 'movie-rebuilt-debug.apk'
$env:JAVA_HOME = $javaHome
New-Item -ItemType Directory -Force -Path $reports | Out-Null

function Invoke-Checked([string]$Executable, [string[]]$Arguments) {
    & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Command failed ($LASTEXITCODE): $Executable" }
}
function Assert-Inputs {
    if ((Get-FileHash -LiteralPath $original -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expectedApkHash) { throw 'Original APK differs from the analyzed input; refusing to mix recoveries.' }
    if ((Get-FileHash -LiteralPath $apktool -Algorithm SHA256).Hash.ToLowerInvariant() -ne 'dbf930b076c6b9be08d57c449cacefc3bdd6b71ebd59b3066fc0e1f5b14f9423') { throw 'Apktool checksum mismatch.' }
}
function Prepare-Recovery {
    Assert-Inputs
    if (!(Test-Path -LiteralPath (Join-Path $decoded 'apktool.yml'))) {
        if (Test-Path -LiteralPath $decoded) { throw 'Incomplete recovery directory exists. Preserve it and choose a new directory before decoding again.' }
        Invoke-Checked $java @('-Xmx1024m','-jar',$apktool,'d',$original,'-s','-j','2','-p',$framework,'-o',$decoded)
    }
}
function Verify-Payload {
    Assert-Inputs
    if (!(Test-Path -LiteralPath $signed)) { throw 'No rebuilt APK; run Build first.' }
    $verification = & (Join-Path $buildTools 'apksigner.bat') verify --verbose --print-certs $signed 2>&1
    $verification | Set-Content -LiteralPath (Join-Path $reports 'rebuilt-signature.txt') -Encoding utf8
    if ($LASTEXITCODE -ne 0) { throw 'Rebuilt APK signature verification failed.' }
    Invoke-Checked (Join-Path $buildTools 'zipalign.exe') @('-c','-P','16','-v','4',$signed) | Set-Content -LiteralPath (Join-Path $reports 'zipalign-verification.txt')
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $before = [IO.Compression.ZipFile]::OpenRead($original)
    $after = [IO.Compression.ZipFile]::OpenRead($signed)
    $rows = [Collections.Generic.List[object]]::new()
    try {
        foreach ($entry in $before.Entries) {
            $name = $entry.FullName
            if ($name.EndsWith('/') -or $name.StartsWith('res/') -or $name.StartsWith('META-INF/') -or $name -in @('resources.arsc','AndroidManifest.xml')) { continue }
            $newEntry = $after.GetEntry($name)
            if (!$newEntry) { throw "Missing preserved payload: $name" }
            $hash = [Security.Cryptography.SHA256]::Create()
            $stream = $entry.Open()
            try { $digestBefore = [BitConverter]::ToString($hash.ComputeHash($stream)).Replace('-','').ToLowerInvariant() } finally { $stream.Dispose() }
            $stream = $newEntry.Open()
            try { $digestAfter = [BitConverter]::ToString($hash.ComputeHash($stream)).Replace('-','').ToLowerInvariant() } finally { $stream.Dispose(); $hash.Dispose() }
            if ($digestBefore -ne $digestAfter -or $entry.Length -ne $newEntry.Length) { throw "Preserved payload changed: $name" }
            $rows.Add([pscustomobject]@{path=$name;bytes=$entry.Length;sha256=$digestAfter})
        }
    } finally { $before.Dispose(); $after.Dispose() }
    $badging = & (Join-Path $buildTools 'aapt2.exe') dump badging $signed 2>&1
    $badging | Set-Content -LiteralPath (Join-Path $reports 'rebuilt-badging.txt') -Encoding utf8
    if ($LASTEXITCODE -ne 0 -or !($badging -match "package: name='com.fvvcl.flickverse'")) { throw 'Rebuilt manifest/package validation failed.' }
    [pscustomobject]@{
        original_apk_sha256=$expectedApkHash
        rebuilt_apk=$signed
        rebuilt_apk_sha256=(Get-FileHash -LiteralPath $signed -Algorithm SHA256).Hash.ToLowerInvariant()
        signature_verified=$true
        zip_alignment_verified=$true
        preserved_payload_files=$rows.Count
        compared_payloads=$rows
        source_java_compiled=$false
        signing_identity='Local Android debug key; differs from the original publisher key'
        runtime_verified=$false
    } | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $reports 'rebuild-verification.json') -Encoding utf8
    Write-Output "Verified signature, alignment, package identity and $($rows.Count) unchanged non-resource payloads."
}
function Selected-Device {
    if ($Serial) {
        $state = & $adb -s $Serial get-state 2>&1
        if ($LASTEXITCODE -ne 0 -or ($state -join '').Trim() -ne 'device') { throw "Device $Serial is unavailable or unauthorized." }
        return $Serial
    }
    $listing = & $adb devices
    if ($LASTEXITCODE -ne 0) { throw 'ADB device discovery failed.' }
    $ready = @($listing | ForEach-Object { if ($_ -match '^(\S+)\s+device(?:\s|$)') { $Matches[1] } })
    if ($ready.Count -ne 1) { throw 'Connect and authorize exactly one device, or pass -Serial explicitly.' }
    return $ready[0]
}
switch ($Action) {
    'Prepare' { Prepare-Recovery }
    'Assemble' {
        Prepare-Recovery
        New-Item -ItemType Directory -Force -Path $output | Out-Null
        $unsigned = Join-Path $output 'movie-unsigned.apk'
        $aligned = Join-Path $output 'movie-aligned.apk'
        Invoke-Checked $java @('-Xmx1024m','-jar',$apktool,'b',$decoded,'-j','2','-p',$framework,'-o',$unsigned)
        Invoke-Checked (Join-Path $buildTools 'zipalign.exe') @('-P','16','-f','4',$unsigned,$aligned)
        $key = Join-Path $PSScriptRoot 'debug.keystore'
        if (!(Test-Path -LiteralPath $key)) {
            Invoke-Checked (Join-Path $javaHome 'bin\keytool.exe') @('-genkeypair','-keystore',$key,'-storetype','JKS','-storepass','android','-keypass','android','-alias','androiddebugkey','-keyalg','RSA','-keysize','2048','-validity','10000','-dname','CN=Android Debug,O=Android,C=US')
        }
        Invoke-Checked (Join-Path $buildTools 'apksigner.bat') @('sign','--ks',$key,'--ks-pass','pass:android','--key-pass','pass:android','--ks-key-alias','androiddebugkey','--v1-signing-enabled','false','--out',$signed,$aligned)
        Verify-Payload
        Write-Output "Built: $signed"
    }
    'Verify' { Verify-Payload }
    'Devices' { Invoke-Checked $adb @('devices','-l') }
    'Install' {
        Verify-Payload
        $device = Selected-Device
        $installed = & $adb -s $device shell pm path --user 0 com.fvvcl.flickverse 2>&1
        if ($installed -match '^package:') { throw 'This package is already installed. The rebuilt APK uses a different signing key; no replacement or uninstall was attempted.' }
        Invoke-Checked $adb @('-s',$device,'install','--user','0',$signed)
    }
    'Launch' {
        $device = Selected-Device
        $resolved = & $adb -s $device shell cmd package resolve-activity --user 0 --brief -a android.intent.action.MAIN -c android.intent.category.LAUNCHER com.fvvcl.flickverse
        if ($LASTEXITCODE -ne 0) { throw 'Launcher activity resolution failed.' }
        $component = @($resolved | Where-Object { $_ -match '^[A-Za-z0-9_.]+/[A-Za-z0-9_.$]+$' }) | Select-Object -Last 1
        if (!$component) { throw 'No installed launcher activity was resolved.' }
        Invoke-Checked $adb @('-s',$device,'shell','am','start','--user','0','-W','-n',$component)
    }
    'DecodeSmali' {
        Assert-Inputs
        $smali = Join-Path $root 'bytecode-app\apktool-smali'
        if (Test-Path -LiteralPath $smali) { throw 'Smali recovery already exists; refusing to replace edits.' }
        Invoke-Checked $java @('-Xmx2048m','-jar',$apktool,'d',$original,'--all-src','-j','2','-p',$framework,'-o',$smali)
    }
}
