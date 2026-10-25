$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$javaHome = 'C:\Program Files\Java\jdk-17'
$env:JAVA_HOME = $javaHome
$python = 'C:\Users\AlphaDell-60\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$bt = 'C:\Users\AlphaDell-60\AppData\Local\Android\Sdk\build-tools\36.1.0'
$work = Join-Path $PSScriptRoot 'native-tracing'
$out = Join-Path $root 'bytecode-app\build\outputs\apk\playback-candidate'
function Checked([string]$exe, [string[]]$arguments) {
    & $exe @arguments
    if ($LASTEXITCODE -ne 0) { throw "Failed: $exe" }
}
Push-Location $root
try {
    $publicCert = Join-Path $work 'signing-cert.der'
    Checked "$javaHome\bin\keytool.exe" @('-exportcert','-keystore','tools\debug.keystore','-storepass','android','-alias','androiddebugkey','-file',$publicCert)
    if ((Get-FileHash $publicCert -Algorithm MD5).Hash -ne '66DDA37731D61DB6C753CD950AA7E82C') { throw 'Unexpected local signing identity; derive the SDK configuration again before building.' }
    if (!(Test-Path (Join-Path $work 'sdk-dex\classes5.dex')) -or !(Test-Path (Join-Path $work 'sdk-dex\classes11.dex'))) {
        Checked "$javaHome\bin\javac.exe" @('-cp','tools\apktool.jar','-d',$work,'tools\RebuildSdkDex.java')
        Checked "$javaHome\bin\java.exe" @('-Xmx2048m','-cp',"tools\apktool.jar;$work",'RebuildSdkDex','..\Movie.apk',"$work\sdk-dex",'918ef3452da2728168006719d78815a6','dd2f0a94b46aad429d3989bc3c615f88')
    }
    Checked $python @('tools\BuildPlaybackCandidate.py')
    Checked "$bt\zipalign.exe" @('-P','16','-f','4',"$out\movie-playback-unsigned.apk","$out\movie-playback-aligned.apk")
    Checked "$bt\apksigner.bat" @('sign','--ks','tools\debug.keystore','--ks-pass','pass:android','--key-pass','pass:android','--ks-key-alias','androiddebugkey','--v1-signing-enabled','false','--out',"$out\movie-playback-candidate.apk","$out\movie-playback-aligned.apk")
    Checked "$bt\apksigner.bat" @('verify','--verbose','--print-certs',"$out\movie-playback-candidate.apk")
    Checked "$bt\zipalign.exe" @('-c','-P','16','4',"$out\movie-playback-candidate.apk")
    Checked $python @('tools\VerifyPlaybackCandidate.py')
    Write-Output "Playback candidate: $out\movie-playback-candidate.apk"
} finally { Pop-Location }
