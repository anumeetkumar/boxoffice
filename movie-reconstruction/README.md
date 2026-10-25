# Movie recovery workspace

## Current branded build: BoxOffice

The latest variant removes ad placements, VIP upsell banners and the Promotion navigation tab, and adds generated BoxOffice branding. Build it with `.\Build.ps1 -Action BoxOffice`; output is `boxoffice/build/BoxOffice.apk`, with a delivery copy at `../BoxOffice.apk`. It has been installed as a same-signature update on the phone, retaining history/data. See [BoxOffice build notes](boxoffice/README.md) for changes and verification. The older build paths below are retained as earlier recovery and diagnostic profiles.

## Playback fix verified

**Additional title-specific streaming issue remains open:** Bigg Boss Season 20 Episode 1 buffers and produces an HTTP connection/EOF error in both the rebuilt APK and the untouched original, including a fresh original installation on the same phone. The prior sample playback checks below remain valid for the tested titles. See `reports/streaming-investigation.md` and `reports/streaming-comparison.json`. No changed buffer/download setting has been identified, and no speculative streaming patch has been released.

Use `./Build.ps1 -Action Playback` for the corrected APK. The older `Build`/Gradle `assembleDebug` path below is retained as the original diagnostic resource rebuild; it does not include this playback configuration fix.

The native playback SDK's initialization value is `MD5(uppercase signing-certificate MD5 + "+" + package + "+" + channel)`. The original value matched the original certificate, so resigning without updating it caused initialization to return -1. The playback build changes this configuration to match the local test keystore at all three recovered call sites: AppApplication, MainActivity and ShortTkActivity. It reassembles only classes5.dex and classes11.dex using the original DEX 037 format, and preserves all 3,597 remaining original archive payloads, including manifest, resources, native libraries and assets. It does not patch native verification or pretend that initialization succeeded.

Output: `bytecode-app/build/outputs/apk/playback-candidate/movie-playback-candidate.apk`. A verified delivery copy is at `../Movie-playback-fixed.apk`.

Executed checks: APK signature/alignment, original DEX format and class counts, unchanged non-target archive payloads, SDK port 7000, actual movie playback (Mandaadi), and series playback (Bigg Boss Season 13 Episode 1), including rendered frames on the isolated API 35 ARM-translating emulator. The entire catalog, downloads, purchases, and ShortTk playback were not tested. See `reports/playback-fixed-status.json`, `reports/movie-playback.png`, `reports/series-playback.png` and `reports/playback-candidate-verification.json`.

The recovered Java working copies reflect the same three configuration edits, but still do not compile; the tested APK is built from recovered DEX/smali. The original REA evidence and Movie.apk remain unchanged. The original app is still installed on the phone. Because the package ID is the same and signing certificates differ, this APK cannot be installed alongside or over that original without a separate replacement decision; no phone uninstall or data clearing was performed.

Open this folder in Android Studio:

`C:\Users\AlphaDell-60\Documents\code\personal\rea-test\movie-reconstruction`

This workspace contains a tested APK rebuild and an Android Gradle source-restoration module. They are separate build paths. **The runnable rebuilt APK preserves the original compiled DEX. It is not a successful compilation of the decompiled Java. Editing the Java working copy does not change the bytecode-preserving APK.**

## Project layout

| Location | Purpose |
| --- | --- |
| `bytecode-app/apktool/` | Editable manifest/resources and original DEX/native/asset payloads, decoded with Apktool 3.0.3 using `--no-src` |
| `source-app/src/main/java/` | Independent working copy of all 42,344 recovered Java files; the REA evidence tree stays untouched |
| `source-app/src/main/AndroidManifest.xml` | Manifest prepared for the Android Gradle Plugin; original package/version declarations move to Gradle |
| `source-app/build.gradle` | Conventional Android application module for source restoration and compilation diagnostics |
| `bytecode-app/build.gradle` | Gradle tasks for rebuilding, signing, verifying and installing the preserved-bytecode APK |
| `reports/` | Build logs, source diagnostics, package/signature/alignment reports and payload verification |
| `tools/debug.keystore` | Generated local test signing key; not the original publisher key |

## Configured tools and dependencies

- Gradle 8.13 wrapper, with its official distribution SHA-256 pinned.
- Android Gradle Plugin 8.8.2 and its build dependencies resolved into `.gradle-user-home/`.
- Android Studio's existing JBR 21.0.9 for Gradle; source language/bytecode target Java 17.
- Existing Android SDK: compile API 35, target API 33, minimum API 24.
- Source module build tools 35.0.0; installed SDK 36.1.0 signing/alignment tools for the APK rebuild.
- Apktool 3.0.3, verified against the upstream release asset SHA-256. The rebuild uses its bundled resource compiler because the SDK compiler rejects this APK's generated `$` resource names.
- Existing JDK 17 for Apktool/keytool and existing ADB 36.0.2.

The recovered source tree already contains the bundled AndroidX, Kotlin, Retrofit, OkHttp, advertising SDK and application classes. Their original Maven coordinates/version graph is not recoverable just by installing current versions. No duplicate Maven copies of these recovered classes were added. Missing classes or invalid source constructs must be restored from the original project metadata or bytecode evidence.

AGP 8.8's documented baseline is Gradle 8.10.2 and JDK 17; this project uses compatible newer installed tools. See [Android's AGP 8.8 release notes](https://developer.android.com/build/releases/agp-8-8-0-release-notes). Apktool's [`--no-src` mode preserves DEX rather than disassembling it](https://apktool.org/docs/2.x/cli-parameters/).

## Build and inspect the rebuilt APK

Run PowerShell from this folder:

```powershell
.\Build.ps1 -Action Build
```

Output:

`bytecode-app\build\outputs\apk\rebuilt-debug\movie-rebuilt-debug.apk`

The Gradle build has passed. Verification confirms:

- The APK signature verifies with the local Android debug certificate.
- APK alignment and package ID `com.fvvcl.flickverse` are valid.
- All 168 original non-resource/non-signature archive entries match by size and SHA-256, including the 11 root DEX files, the embedded asset DEX, native libraries, assets and other preserved metadata.
- The original `Movie.apk` SHA-256 remains `cdc0d88ebcd6ad10d04e9e09f8b75fdeabd91369b9a524827cabfcbb9e7ad4f9`.

Resources and the manifest are recompiled and the signing identity changes. Native protection, publisher-signature checks and server behavior can therefore affect runtime behavior. The rebuilt APK retains the original manifest's debuggable setting; "debug" in the filename refers to the local signing key.

Use `reports/rebuild-verification.json`, `reports/rebuilt-signature.txt`, `reports/zipalign-verification.txt` and `reports/rebuilt-badging.txt` for the executed checks.

### Executed phone check

The rebuilt APK was installed successfully on the connected Samsung SM-G998B, Android API 35, with ARM64 support. The package was absent before installation, so an existing installation was not replaced. Its splash activity launched with Android status `ok`, and the main app process was alive eight seconds later. The subsequent window check found the target application in the foreground. This is an installation/startup smoke check, not validation of login, playback, downloads, networking or the reconstructed Java build. The workflow did not enter credentials. See `reports/phone-install.log`, `reports/phone-launch.log`, `reports/phone-app-logcat.txt` and `reports/device-smoke.json`.

## Connect your phone

Enable USB debugging and accept the computer authorization prompt. Then:

```powershell
.\Build.ps1 -Action Devices
.\Build.ps1 -Action Install
.\Build.ps1 -Action Launch
```

For multiple devices:

```powershell
.\Build.ps1 -Action Install -Serial YOUR_DEVICE_SERIAL
.\Build.ps1 -Action Launch -Serial YOUR_DEVICE_SERIAL
```

Installation targets the primary Android user (user 0) and refuses to replace an existing `com.fvvcl.flickverse` package automatically. A publisher-signed installation cannot be updated with this local test key. The scripts do not uninstall applications, clear data, or grant permissions. Decide separately how to preserve existing app data before replacing an installed copy. The initial test installation is now present, so repeating Install will stop at this check; use Launch to reopen it.

## Restore the Java source build

Select `source-app` in Android Studio to browse the working copy. These commands exercise source compilation, not the bytecode-preserving rebuild:

```powershell
.\Build.ps1 -Action Dependencies
.\Build.ps1 -Action DiagnoseSources
.\Build.ps1 -Action Sources
```

`DiagnoseSources` invokes javac against recovered Java and the Android boot classpath without requiring resource compilation. The executed check failed and reached its **200 reported-error limit**, starting with reconstructed static initializers in interfaces under `android/`. There may be more errors beyond that limit. `Sources` runs the normal Android application build; its executed check failed at `mergeDebugResources` because `$` is not accepted in file-based resource names.

A Java source build has not passed. The extracted code also includes a `super.onCreate()` call inside a static wrapper, erased/renamed APIs, and a failed generated binding method. The original generated R classes are retained for direct compiler diagnostics; the normal AGP module excludes the app's recovered R/BuildConfig so AGP can generate them.

The source module's resource tree is currently shared with the editable Apktool recovery. The stock AGP resource compiler requires resource-name restoration for private generated names. Such restoration must preserve resource-ID relationships and update matching Java/XML references; it is not solved by installing another SDK library.

Do not interpret the rebuilt APK as proof that this Java module compiles. Review `reports/java-compilation.log` and `reports/source-assemble.log` for the actual compiler results.

For a separate smali recovery tree, the project exposes:

```powershell
.\Build.ps1 -Action Smali
```

This optional task creates `bytecode-app/apktool-smali/` and refuses to overwrite an existing tree. It is not run automatically and its edits are not consumed by the default bytecode-preserving build.

## Android Studio and Windows Gradle setup

The included Gradle run configurations expose "Build rebuilt APK (original DEX)" and "Install rebuilt APK (authorized phone)". The ordinary Android Run configuration for `source-app` still requires source restoration before it can produce an app.

`Build.ps1` uses a project-local Gradle cache, Android user directory and a short temporary socket directory at `..\.java-tmp`. This fixes the Java NIO/Gradle loopback error observed with this environment's long temporary path. Only the launched process environment is changed. Oracle documents the [Unix-domain socket temporary directory and path-length limit](https://docs.oracle.com/en/java/javase/17/core/java-networking.html).

The Gradle wrapper remains usable directly once its distribution is downloaded. If launching it from this chat's sandbox, the Gradle daemon's loopback connection may require execution approval. A normal Android Studio or PowerShell terminal is not that sandbox.

## Evidence

The original REA results remain at `../rea/_reference/movie-review/README.md`, including 116 successful MCP calls, 95 method inspections, 49 API route declarations, source hashes, native inventories and the original byte extraction verification. The recovered HTTP client disables certificate and hostname validation; that behavior was preserved for comparison and has not been silently repaired here.
