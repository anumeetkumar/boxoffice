$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem
$outputRoot = Join-Path $PSScriptRoot 'raw-apk'
if (Test-Path -LiteralPath $outputRoot) { throw 'Raw extraction output already exists' }
New-Item -ItemType Directory -Path $outputRoot | Out-Null
$rootPrefix = [IO.Path]::GetFullPath($outputRoot) + [IO.Path]::DirectorySeparatorChar
$seen = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
$records = [Collections.Generic.List[object]]::new()
$apkPath = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\deepcineph.apk'))
$archive = [IO.Compression.ZipFile]::OpenRead($apkPath)
try {
  $index = 0
  foreach ($entry in $archive.Entries) {
    $index++
    if ($entry.FullName.EndsWith('/')) { continue }
    $relative = $entry.FullName.Replace('/',[IO.Path]::DirectorySeparatorChar)
    $reason = $null
    $destination = [IO.Path]::GetFullPath((Join-Path $outputRoot $relative))
    if (!$destination.StartsWith($rootPrefix,[StringComparison]::OrdinalIgnoreCase)) { throw "Unsafe ZIP path: $($entry.FullName)" }
    if (!$seen.Add($destination)) {
      $relative = '__case_collisions\' + $index + '.bin'
      $destination = Join-Path $outputRoot $relative
      $reason = 'case-insensitive path collision; original ZIP name retained in map'
    }
    New-Item -ItemType Directory -Force -Path ([IO.Path]::GetDirectoryName($destination)) | Out-Null
    $source = $entry.Open()
    $target = [IO.File]::Open($destination,[IO.FileMode]::CreateNew)
    try { $source.CopyTo($target) } finally { $target.Dispose(); $source.Dispose() }
    $digest = (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLowerInvariant()
    $records.Add([pscustomobject]@{zip_index=$index;original_name=$entry.FullName;output_path=$relative;bytes=$entry.Length;sha256=$digest;remapping_reason=$reason})
  }
} finally { $archive.Dispose() }
$records | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'raw-file-map.json') -Encoding utf8
Write-Output "Extracted $($records.Count) files; remapped $(($records | Where-Object remapping_reason).Count) collisions."

