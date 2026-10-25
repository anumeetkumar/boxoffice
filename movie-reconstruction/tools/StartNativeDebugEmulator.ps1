$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$work = Join-Path $PSScriptRoot 'native-tracing'
$image = Join-Path $work 'image\x86_64'
if (!(Test-Path (Join-Path $image 'system.img'))) { throw 'Verified debug image is not ready' }
$avdHome = Join-Path $work 'avd'
$avd = Join-Path $avdHome 'codex_native_debug.avd'
New-Item -ItemType Directory -Force $avd | Out-Null
$config = @"
AvdId=codex_native_debug
avd.ini.displayname=Codex Native SDK Debug
avd.ini.encoding=UTF-8
PlayStore.enabled=false
abi.type=x86_64
hw.cpu.arch=x86_64
hw.cpu.ncore=2
hw.ramSize=3072
hw.lcd.width=720
hw.lcd.height=1280
hw.lcd.density=320
hw.gpu.enabled=yes
hw.gpu.mode=swiftshader
hw.keyboard=yes
hw.mainKeys=no
hw.sdCard=no
hw.camera.back=none
hw.camera.front=none
hw.audioInput=no
hw.battery=yes
disk.dataPartition.size=3G
image.sysdir.1=$image\
tag.id=google_apis
tag.display=Google APIs
target=android-35
runtime.network.latency=none
runtime.network.speed=full
vm.heapSize=256
"@
$config | Set-Content (Join-Path $avd 'config.ini') -Encoding ascii
"avd.ini.encoding=UTF-8`npath=$avd`ntarget=android-35" | Set-Content (Join-Path $avdHome 'codex_native_debug.ini') -Encoding ascii
$env:ANDROID_AVD_HOME = $avdHome
$env:ANDROID_SDK_ROOT = 'C:\Users\AlphaDell-60\AppData\Local\Android\Sdk'
$emulator = Join-Path $env:ANDROID_SDK_ROOT 'emulator\emulator.exe'
Start-Process -FilePath $emulator -ArgumentList @('-avd','codex_native_debug','-no-window','-no-audio','-no-snapshot','-no-boot-anim','-port','5558') -WindowStyle Hidden -RedirectStandardOutput (Join-Path $root 'reports\native-debug-emulator.stdout.log') -RedirectStandardError (Join-Path $root 'reports\native-debug-emulator.stderr.log')
Write-Output 'Started workspace-owned isolated emulator on port 5558.'
