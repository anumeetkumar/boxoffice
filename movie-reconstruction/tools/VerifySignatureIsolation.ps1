$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem
$root = Split-Path $PSScriptRoot -Parent
$original = [IO.Compression.ZipFile]::OpenRead((Join-Path $root '..\Movie.apk'))
$candidate = [IO.Compression.ZipFile]::OpenRead((Join-Path $root 'bytecode-app\build\outputs\apk\signature-isolation\movie-original-resigned.apk'))
$checked = 0
try {
    foreach ($entry in $original.Entries) {
        if ($entry.FullName.EndsWith('/') -or $entry.FullName -match '^META-INF/.*\.(SF|RSA|DSA|EC)$' -or $entry.FullName -eq 'META-INF/MANIFEST.MF') { continue }
        $other = $candidate.GetEntry($entry.FullName)
        if (!$other) { throw "Missing entry: $($entry.FullName)" }
        $sha = [Security.Cryptography.SHA256]::Create()
        $stream = $entry.Open()
        try { $a = [BitConverter]::ToString($sha.ComputeHash($stream)) } finally { $stream.Dispose() }
        $stream = $other.Open()
        try { $b = [BitConverter]::ToString($sha.ComputeHash($stream)) } finally { $stream.Dispose(); $sha.Dispose() }
        if ($a -ne $b -or $entry.Length -ne $other.Length) { throw "Changed payload: $($entry.FullName)" }
        $checked++
    }
    [pscustomobject]@{comparison='Original APK versus signature-only diagnostic candidate'; unchanged_entries=$checked; includes_original_manifest_resources_dex_native=$true; playback_fixed=$false; runtime_test_pending=$true} | ConvertTo-Json | Set-Content (Join-Path $root 'reports\signature-isolation-verification.json')
    Write-Output "Verified $checked unchanged entries, including original manifest and resources. This does not verify playback."
} finally { $original.Dispose(); $candidate.Dispose() }
