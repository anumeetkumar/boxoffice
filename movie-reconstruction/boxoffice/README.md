# BoxOffice Android APK

Build from the parent recovery workspace with:

```powershell
.\Build.ps1 -Action BoxOffice
```

Output: `boxoffice/build/BoxOffice.apk`. The user delivery copy is `../BoxOffice.apk` relative to the recovery workspace.

This is a recovered-bytecode/resource build, not React Native or a restored compilation of the decompiled Java. The original REA evidence, Movie.apk, and previous playback build are retained separately. The existing package ID and local test signing key are preserved so this installs as an update over the previous rebuilt APK and retains its data. The tested native playback certificate-derived configuration remains present.

## Changes

- Generated BoxOffice icon stored in `assets/boxoffice-icon.png`, integrated in launcher icons for all densities, adaptive foregrounds, splash and initial player loading UI. Application label and localized branding strings are BoxOffice.
- All 25 `AdInfoEntry.getAd_position_*` getters return `Collections.EMPTY_LIST`. The original DEX already referenced this standard empty-list field, allowing equal-size instruction patches in classes10.dex with original indexes, code sizes and class counts preserved. Header checksums are recomputed.
- Both `AppApplication.loadAdConf` overloads and the main activity ad preload path are disabled. Twelve ad-related manifest provider initializers are removed. Bundled unused SDK code remains in the APK; this is not a removal of every analytics library.
- Join VIP/Subscribe banner and profile VIP upsell are collapsed while preserving binding view IDs. The player ad-overlay strip and promotional game account row are collapsed.
- Promotion is removed from the navigation model. Tabs are Home, Streaming, Categories and Me. Account navigation indexes and the obsolete promotion-name event are adjusted.
- Player update (26 October 2026): fullscreen Subscribe is collapsed, existing state-aware play/pause buttons are centered between the ten-second seek buttons, and the center row participates in show/hide animations in both orientations. Single tap retains its original show/hide behavior. Double tap now seeks ten seconds backward on the left half and forward on the right half, clamps at the media boundaries and preserves play/pause state. Unknown-duration media and ads are ignored by this seek handler. Volume gestures and both player volume sliders use flags 0 instead of FLAG_PLAY_SOUND.

The resource variant is prepared by `tools/PrepareBoxOffice.py` and `tools/PreparePlayerControls.py`; separate smali working copies are `boxoffice/smali5`, `smali7` and `smali8`. `tools/AssembleBoxOfficeDex.java` assembles these using the original DEX 037 format. Equal-size patches in DEX 6 and 10 retain the original indexes and code sizes. The main decompiled Java restoration module remains separate and does not yet compile.

## Verification

APK signature/alignment and label/package checks pass. Original class counts and DEX format are preserved. All 20 native libraries and 162 non-resource payloads outside the six intentionally changed DEX files match the original. The previously verified playback helper DEX 11 is unchanged from the working playback build.

Emulator checks covered startup, four-tab navigation, the account screen with no VIP/game promotion, and a player detail screen with no Join VIP banner. The emulator still encounters the previously investigated source/network failures for some titles; those are not claimed fixed here.

The previous ad-free APK was installed on the user's SM-G998B using `adb install -r --user 0`, with no uninstall or data clearing. Existing history, including Epic - First Semester, remained accessible. Reopening Epic showed the ad-free player layout, and the player emitted its playback-start event. No screenshot was taken when BoxOffice was not the focused phone app. No ad SDK log entries appeared in the observed phone process window; this is an observation, not an exhaustive network/privacy audit. The October 26 player update was built and tested on the isolated emulator; the phone was not connected and has not received this update.

`tools/TestPlayerControls.mjs` with `native-tracing/test-player-controls.js` is an emulator-only harness using an in-memory Java proxy player. It exercises the compiled APK's touch handler and actual play/pause button listeners without media/network dependency. Results are in `reports/boxoffice-player-runtime-test.json`; this does not substitute for a physical-phone streaming and audible-volume check.

## Request-flow equivalence audit

`tools/AuditRequestFlow.java` compares canonical disassembly from both compiled APKs, without debug information or DEX-index artifacts. All 156 selected request/playback flow classes match, including the API interface, interceptors, device-ID helper, certificate helper, native SDK Java interface, video detail activity and its callbacks, playback view model, and network wrappers. The native libraries also remain byte-identical. `BuildBoxOffice.ps1` runs the audit and verification fails if any selected class differs.

The three native SDK initialization call sites retain the previously verified local-signer configuration instead of the original-signer configuration. These intentionally changed initialization call sites are outside the 156 matching classes.

This confirms that request fields and generation algorithms were retained; it does not claim identical dynamic values. Installed certificate, device identity, session token, timestamp and native verification output can differ. BoxOffice's replacement notice on the phone remains unresolved. The emulator returned correct Paradise metadata even for a request that reported the rebuilt certificate, so certificate reporting alone is not established as the cause. A fresh phone install and API-host comparison did not resolve the notice. See `reports/boxoffice-permanent-fix-investigation.json` and `reports/request-flow-audit/comparison.tsv`.

See `reports/boxoffice-status.json`, `reports/boxoffice-verification.json`, `reports/boxoffice-ad-placement-patch.json`, `reports/boxoffice-preparation.json` and the saved app UI/log captures.
