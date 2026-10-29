param()
$ErrorActionPreference='Stop'
$root=$PSScriptRoot
$base=Split-Path $root -Parent
$python='C:\Users\AlphaDell-60\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$java='C:\Program Files\Java\jdk-17\bin\java.exe'
$tools=Join-Path $base 'movie-reconstruction/tools'
$apktool=Join-Path $tools 'apktool.jar'
$sdk='C:\Users\AlphaDell-60\AppData\Local\Android\Sdk\build-tools\36.1.0'
$env:JAVA_HOME='C:\Program Files\Java\jdk-17'
function Run([string]$exe,[string[]]$argv){ & $exe @argv; if($LASTEXITCODE -ne 0){throw "Failed: $exe ($LASTEXITCODE)"} }
$backups=@(Get-ChildItem (Join-Path $base 'backups') -Filter 'deepcineph-extraction-*.json' | Sort-Object LastWriteTime -Descending)
if(!$backups.Count){throw 'Verified extraction backup required before building'}
$backup=Get-Content $backups[0].FullName -Raw | ConvertFrom-Json
if(!$backup.verified -or (Get-FileHash $backup.archive -Algorithm SHA256).Hash.ToLowerInvariant() -ne $backup.sha256){throw 'Backup verification failed'}
$original=Join-Path $base 'deepcineph.apk'
if((Get-FileHash $original -Algorithm SHA256).Hash.ToLowerInvariant() -ne '788e45abd4c315e5d2cb51319eae1ba92d8d796e24f4364314df334d636f8600'){throw 'Input APK changed'}
$decoded=Join-Path $root 'working/apktool'
if(!(Test-Path $decoded)){New-Item -ItemType Directory -Force (Split-Path $decoded -Parent) | Out-Null; Copy-Item (Join-Path $base 'deepcineph-reconstruction/apktool') $decoded -Recurse}
$strings=Join-Path $decoded 'res/values/strings.xml'
$text=Get-Content $strings -Raw
$text.Replace('<string name="app_name">DeepCine</string>','<string name="app_name">DeepCine Test</string>') | Set-Content $strings -Encoding utf8
if(!(Test-Path (Join-Path $root 'working/sdk-dex/classes.dex')) -or !(Test-Path (Join-Path $root 'working/sdk-dex/classes3.dex'))){
Run $java @('-Xmx2048m','-cp',$apktool,(Join-Path $root 'tools/RebuildSdkDex.java'),$original,(Join-Path $root 'working/sdk-dex'),'9d0ed3d8efd5204654f4e6ca4a0e52fd','691c5f5ff7b2d3054de60e744c53c242')
}
Copy-Item (Join-Path $root 'working/sdk-dex/classes.dex') (Join-Path $decoded 'classes.dex') -Force
Copy-Item (Join-Path $root 'working/sdk-dex/classes3.dex') (Join-Path $decoded 'classes3.dex') -Force
$out=Join-Path $root 'output'
New-Item -ItemType Directory -Force $out | Out-Null
Run $java @('-Xmx1024m','-jar',$apktool,'b',$decoded,'-j','2','-p',(Join-Path $base 'deepcineph-reconstruction/framework'),'-o',(Join-Path $out 'unsigned.apk'))
Run (Join-Path $sdk 'zipalign.exe') @('-P','16','-f','4',(Join-Path $out 'unsigned.apk'),(Join-Path $out 'aligned.apk'))
Run (Join-Path $sdk 'apksigner.bat') @('sign','--ks',(Join-Path $tools 'debug.keystore'),'--ks-pass','pass:android','--key-pass','pass:android','--ks-key-alias','androiddebugkey','--v1-signing-enabled','false','--out',(Join-Path $out 'DeepCine-test.apk'),(Join-Path $out 'aligned.apk'))
Run (Join-Path $sdk 'apksigner.bat') @('verify','--verbose','--print-certs',(Join-Path $out 'DeepCine-test.apk'))
Run (Join-Path $sdk 'zipalign.exe') @('-c','-P','16','4',(Join-Path $out 'DeepCine-test.apk'))
Run $java @('-Xmx1536m','-cp',$apktool,(Join-Path $root 'tools/VerifyDex.java'),$original,(Join-Path $out 'DeepCine-test.apk'))
Run $python @((Join-Path $root 'tools/verify-build.py'))


