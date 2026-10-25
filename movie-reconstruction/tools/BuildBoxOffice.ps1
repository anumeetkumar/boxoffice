$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$python='C:\Users\AlphaDell-60\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$javaHome='C:\Program Files\Java\jdk-17'
$env:JAVA_HOME=$javaHome
$bt='C:\Users\AlphaDell-60\AppData\Local\Android\Sdk\build-tools\36.1.0'
$out=Join-Path $root 'boxoffice\build'
function Checked([string]$exe,[string[]]$arguments){ & $exe @arguments; if($LASTEXITCODE -ne 0){throw "Failed: $exe"} }
Push-Location $root
try {
    New-Item -ItemType Directory -Force (Join-Path $root 'boxoffice') | Out-Null
    Checked "$javaHome\bin\keytool.exe" @('-exportcert','-keystore','tools\debug.keystore','-storepass','android','-alias','androiddebugkey','-file','boxoffice\signing-cert.der')
    if((Get-FileHash 'boxoffice\signing-cert.der' -Algorithm MD5).Hash -ne '66DDA37731D61DB6C753CD950AA7E82C'){throw 'Signing key differs from the tested playback configuration'}
    Checked $python @('tools\BoxOfficeDexPatch.py')
    Checked $python @('tools\PrepareBoxOffice.py')
    Checked "$javaHome\bin\javac.exe" @('-cp','tools\apktool.jar','-d','tools\native-tracing','tools\AssembleBoxOfficeDex.java')
    Checked "$javaHome\bin\java.exe" @('-Xmx2048m','-cp','tools\apktool.jar;tools\native-tracing','AssembleBoxOfficeDex','boxoffice\smali5','boxoffice\patched\classes5.dex')
    Copy-Item boxoffice\patched\classes5.dex boxoffice\apktool\classes5.dex -Force
    Copy-Item boxoffice\patched\classes10.dex boxoffice\apktool\classes10.dex -Force
    Copy-Item tools\native-tracing\sdk-dex\classes11.dex boxoffice\apktool\classes11.dex -Force
    New-Item -ItemType Directory -Force $out | Out-Null
    Checked "$javaHome\bin\java.exe" @('-Xmx1024m','-jar','tools\apktool.jar','b','boxoffice\apktool','-j','2','-p','tools\framework','-o',"$out\boxoffice-unsigned.apk")
    Checked "$bt\zipalign.exe" @('-P','16','-f','4',"$out\boxoffice-unsigned.apk","$out\boxoffice-aligned.apk")
    Checked "$bt\apksigner.bat" @('sign','--ks','tools\debug.keystore','--ks-pass','pass:android','--key-pass','pass:android','--ks-key-alias','androiddebugkey','--v1-signing-enabled','false','--out',"$out\BoxOffice.apk","$out\boxoffice-aligned.apk")
    Checked "$bt\apksigner.bat" @('verify','--verbose','--print-certs',"$out\BoxOffice.apk")
    Checked "$bt\zipalign.exe" @('-c','-P','16','4',"$out\BoxOffice.apk")
    Checked $python @('tools\VerifyBoxOffice.py')
    Write-Output "BoxOffice APK: $out\BoxOffice.apk"
} finally { Pop-Location }
