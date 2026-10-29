$ErrorActionPreference='Stop'
$root=$PSScriptRoot
$base=Split-Path $root -Parent
$java='C:\Program Files\Java\jdk-17\bin\java.exe'
$python='C:\Users\AlphaDell-60\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$apktool=Join-Path $base 'movie-reconstruction/tools/apktool.jar'
$androidTools='C:\Users\AlphaDell-60\AppData\Local\Android\Sdk\build-tools\36.1.0'
$env:JAVA_HOME='C:\Program Files\Java\jdk-17'
function Run([string]$exe,[string[]]$argv){& $exe @argv;if($LASTEXITCODE -ne 0){throw "Command failed: $exe"}}
$baseline=Join-Path $root 'output/DeepCine-audio-menu.apk'
if((Get-FileHash $baseline -Algorithm SHA256).Hash.ToLowerInvariant() -ne '43d84fbbea013308315b1d426216dbbd546ddc733080e7409982d8a88dfa691b'){throw 'Baseline differs from verified input'}
Run $python @((Join-Path $root 'tools/prepare-ready.py'))
Run $java @('-Xmx1536m','-cp',$apktool,(Join-Path $root 'tools/AssembleVariantDex.java'),(Join-Path $root 'working/sdk-dex/classes3.dex-smali'),(Join-Path $root 'ready/default-classes3.dex'),(Join-Path $root 'ready/AppApplication.smali'))
Run $python @((Join-Path $root 'tools/package-default.py'))
Run $java @('-Xmx1024m','-cp',$apktool,(Join-Path $root 'tools/PatchReadyDex.java'),(Join-Path $root 'ready/base-with-default.apk'),(Join-Path $root 'ready/patched'))
Run $python @((Join-Path $root 'tools/prepare-labels.py'))
Run $java @('-Xmx3072m','-cp',$apktool,(Join-Path $root 'tools/LocalizeReadyDex.java'),(Join-Path $root 'ready/prelocalize.apk'),(Join-Path $root 'ready/localized'),(Join-Path $root 'ready/IndiaDisplayLabels.smali'))
Run $python @((Join-Path $root 'tools/ready-resources.py'))
Run $python @((Join-Path $root 'tools/stage-ready.py'))
Run $java @('-Xmx1024m','-jar',$apktool,'b',(Join-Path $root 'ready/apktool'),'-j','2','-p',(Join-Path $base 'deepcineph-reconstruction/framework'),'-o',(Join-Path $root 'ready/unsigned.apk'))
Run (Join-Path $androidTools 'zipalign.exe') @('-P','16','-f','4',(Join-Path $root 'ready/unsigned.apk'),(Join-Path $root 'ready/aligned.apk'))
Run (Join-Path $androidTools 'apksigner.bat') @('sign','--ks',(Join-Path $base 'movie-reconstruction/tools/debug.keystore'),'--ks-pass','pass:android','--key-pass','pass:android','--ks-key-alias','androiddebugkey','--v1-signing-enabled','false','--out',(Join-Path $root 'output/DeepCine-India.apk'),(Join-Path $root 'ready/aligned.apk'))
Run (Join-Path $androidTools 'apksigner.bat') @('verify','--verbose',(Join-Path $root 'output/DeepCine-India.apk'))
Run (Join-Path $androidTools 'zipalign.exe') @('-c','-P','16','4',(Join-Path $root 'output/DeepCine-India.apk'))
Run $java @('-Xmx2048m','-cp',$apktool,(Join-Path $root 'tools/VerifyReadyDex.java'),$baseline,(Join-Path $root 'output/DeepCine-India.apk'),(Join-Path $root 'reports/ready-method-changes.tsv'))
Run $python @((Join-Path $root 'tools/verify-ready.py'))
