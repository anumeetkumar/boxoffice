# Movie detail failure

## Resolved: certificate-derived SDK initialization configuration

Further static investigation found the exact derivation of the first hls.load argument: MD5("099656628B5CF75B43B04EECE0E62FA4+com.fvvcl.flickverse+63") equals the original hard-coded value 918ef3452da2728168006719d78815a6. This is the original signing certificate's uppercase MD5, package ID, and channel, separated by plus signs.

The local signing certificate's uppercase MD5 is 66DDA37731D61DB6C753CD950AA7E82C. Its corresponding SDK initialization configuration is dd2f0a94b46aad429d3989bc3c615f88. Updating this value at AppApplication, MainActivity, and ShortTkActivity restores native initialization to port 7000. No SDK/native protection check was modified. The protected SDK implementation itself was not recovered.

The successful build reassembles classes5.dex and classes11.dex with their original DEX 037 format. This addresses validation failures in earlier local candidates: direct string replacement leaves out-of-order string IDs, while using the APK tool's API 35 writer emits DEX 041 with an incompatible header size. These rejected diagnostic candidates are superseded by the verified DEX 037 build.

On the isolated API 35 emulator, the corrected build launched, loaded the catalog and details, and played Mandaadi and Bigg Boss Season 13 Episode 1. Both emitted playback-start events, and rendered video frames were captured and visually inspected. Signature/alignment checks pass; exactly two DEX files differ while all 3,597 other original ZIP entry payloads match. Class counts are preserved (6,287 and 8,061). This verifies the sampled flows, not every catalog title or ancillary feature.

Current artifact: ../bytecode-app/build/outputs/apk/playback-candidate/movie-playback-candidate.apk; delivery copy: ../../Movie-playback-fixed.apk. Reproduce with ../Build.ps1 -Action Playback. Source working copies reflect the same configuration edits, but Java compilation is still unresolved. The phone's original app was not changed.

The historical findings below describe the earlier failure and are superseded where they say a fix has not been implemented or the exact configuration cause remains unknown.

## Signature-only isolation test

Tested on the existing Pixel_9_Pro emulator (emulator-5556, API 36, x86_64 with ARM64 translation). The original APK was installed on an emulator where the package was absent, launched, and recorded native port 7000. This test installation was removed, and an APK produced by apksigner directly from Movie.apk using the local debug key was installed and launched. It recorded port -1. Both reached the same phone permission prompt; no phone permissions were granted during this test.

The signature-only candidate was not passed through Apktool. VerifySignatureIsolation.ps1 verifies all 3,599 original ZIP entry payloads, including the original binary manifest and resources.arsc, are unchanged. Signature verification passes. This establishes that changing signing data alone is sufficient to reproduce the native initialization failure. It does not identify the exact native validation code.

Evidence: emulator-original-startup.txt (PID 3290, 7000), emulator-resigned-startup.txt (PID 5955, -1), signature-isolation-verification.json, native-jni-onload.txt. JNI_OnLoad delegates into interpreter_wrap_int64_t; the inspected native entry uses protected/interpreted code, not a recovered readable load implementation.

Recovered SDK load parameters and public certificate identity are saved in recovered-playback-sdk-config.json. Parameter six is a runtime cached public-system-configuration string (KEY_PREF_PUBLICSYSCONF_STRING), not a static private signing key. The original private key is not included in the APK. User confirms only the APK is available.

The signature-only APK is a diagnostic build, not a working playback fix. No native validation bypass or successful replacement SDK integration has been implemented. Restoring the original signing identity requires its private key; alternatively, SDK reauthorization/replacement or further native reverse engineering is required. The phone's working original was left untouched throughout the comparison.

## Original APK comparison confirmed

The user installed the original APK. Read-only ADB comparison confirms the installed base APK SHA-256 exactly matches Movie.apk (`cdc0d88ebcd6ad10d04e9e09f8b75fdeabd91369b9a524827cabfcbb9e7ad4f9`), with original signing certificate SHA-256 `e751b8dcb7f58058b063b6c4aac0ab0977187797923e81858aa6803ab1eb832e`.

Original app UID 10648, PID 25006: native port initialization succeeds with port 7000 at 11:03:54.469, followed by a playback-start message at 11:04:12.994. The user supplied screenshots of video playing. Logs are preserved in original-playback-uid-logcat.txt. In contrast, the rebuilt app repeatedly returned port -1 on the same phone.

This narrows the problem to a difference introduced by the APK rebuild/signing process, rather than a missing Node package or a generally unavailable playback backend. Certificate-dependent SDK validation or APK integrity checks are plausible, but the specific native rejection mechanism has not been proven. A successful startup smoke test did not establish functioning playback; the rebuilt APK is currently not playback-functional. No original app changes or replacements were made during this comparison.

Observed on connected Samsung SM-G998B, package com.fvvcl.flickverse, UID 10647.

The UID-filtered log capture in network-app-logcat.txt repeatedly records `wangyi: 端口号为：-1`, including immediately before movie detail opens at 10:58:58 and 10:59:40 on October 23 (device clock).

AppApplication.loadP2pSdk and MainActivity.loadP2pSdk assign the result of native hls.load to AppApplication.port. The recorded result is invalid; the native playback service did not supply a usable port.

VideoPlayDetailActivity.getSignInfo (source line 1356) checks port <= 0 and directly sets the detail error observable x=true and loading observable D=false, returning before the local /control?msg=verify request. The detail layout displays text_load_empty: “No network or server exception, please try again later”. Thus this message does not establish that the phone has no Internet or that the remote API is down.

Initialization failure cause remains unconfirmed. The rebuilt APK uses a different signing certificate; SDK licensing/signature validation is a possible cause, along with SDK configuration, native compatibility, or initialization requirements. There is no evidence yet proving any one of these causes. The native library and original DEX were preserved by the rebuild.

Next useful comparison is the untouched original APK on an isolated emulator or separate test device, followed by comparing native startup logs. Do not replace the installed package automatically: signing certificates differ and replacement can require uninstalling and losing app data. No protection checks were patched, no permissions changed, and no app data cleared during this diagnosis.

This is a runtime SDK initialization issue; adding Node/npm packages cannot supply the missing native playback port. The recovered Java project remains non-compiling, and the installed rebuild runs the original DEX.
