$ErrorActionPreference='Stop'
$root=$PSScriptRoot
$java='C:\Program Files\Java\jdk-17\bin\java.exe'
$python='C:\Users\AlphaDell-60\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$apktool=Join-Path $root '../movie-reconstruction/tools/apktool.jar'
$androidTools='C:\Users\AlphaDell-60\AppData\Local\Android\Sdk\build-tools\36.1.0'
$env:JAVA_HOME='C:\Program Files\Java\jdk-17'
function Run([string]$exe,[string[]]$argv){& $exe @argv;if($LASTEXITCODE -ne 0){throw "Command failed: $exe"}}
# Keep the verified baseline APK; this update is separately named and never overwrites it.
Run $java @('-cp',$apktool,(Join-Path $root 'tools/InspectPlayer.java'),(Join-Path $root 'output/DeepCine-test.apk'),(Join-Path $root 'reports/player-before.smali')) | Set-Content (Join-Path $root 'reports/player-inspection.txt')
Run $python @((Join-Path $root 'tools/patch-audio-menu.py'))
Run (Join-Path $androidTools 'zipalign.exe') @('-P','16','-f','4',(Join-Path $root 'output/DeepCine-audio-menu-unsigned.apk'),(Join-Path $root 'output/DeepCine-audio-menu-aligned.apk'))
Run (Join-Path $androidTools 'apksigner.bat') @('sign','--ks',(Join-Path $root '../movie-reconstruction/tools/debug.keystore'),'--ks-pass','pass:android','--key-pass','pass:android','--ks-key-alias','androiddebugkey','--v1-signing-enabled','false','--out',(Join-Path $root 'output/DeepCine-audio-menu.apk'),(Join-Path $root 'output/DeepCine-audio-menu-aligned.apk'))
Run (Join-Path $androidTools 'apksigner.bat') @('verify','--verbose',(Join-Path $root 'output/DeepCine-audio-menu.apk'))
Run (Join-Path $androidTools 'zipalign.exe') @('-c','-P','16','4',(Join-Path $root 'output/DeepCine-audio-menu.apk'))
Run $java @('-cp',$apktool,(Join-Path $root 'tools/InspectPlayer.java'),(Join-Path $root 'output/DeepCine-audio-menu.apk'),(Join-Path $root 'reports/player-after.smali')) | Set-Content (Join-Path $root 'reports/player-after-inspection.txt')
Run $python @((Join-Path $root 'tools/verify-audio-menu.py'))
