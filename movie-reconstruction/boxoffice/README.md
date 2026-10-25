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

The resource variant is prepared by `tools/PrepareBoxOffice.py`; its separate smali working copy is `boxoffice/smali5`. `tools/AssembleBoxOfficeDex.java` assembles this variant using the original DEX 037 format. The main decompiled Java restoration module remains separate and does not yet compile.

## Verification

APK signature/alignment and label/package checks pass. Original class counts and DEX format are preserved. All 20 native libraries and 165 non-resource payloads outside the three intentionally changed DEX files match the original. The previously verified playback helper DEX is unchanged.

Emulator checks covered startup, four-tab navigation, the account screen with no VIP/game promotion, and a player detail screen with no Join VIP banner. The emulator still encounters the previously investigated source/network failures for some titles; those are not claimed fixed here.

The final APK was installed on the user's SM-G998B using `adb install -r --user 0`, with no uninstall or data clearing. Existing history, including Epic - First Semester, remained accessible. Reopening Epic showed the ad-free player layout, and the player emitted its playback-start event. No screenshot was taken when BoxOffice was not the focused phone app. No ad SDK log entries appeared in the observed phone process window; this is an observation, not an exhaustive network/privacy audit.

See `reports/boxoffice-status.json`, `reports/boxoffice-verification.json`, `reports/boxoffice-ad-placement-patch.json`, `reports/boxoffice-preparation.json` and the saved app UI/log captures.
