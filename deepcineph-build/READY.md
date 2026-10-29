# DeepCine India profile build

Artifact: `output/DeepCine-India.apk`. Rebuild with `./BuildReady.ps1` using the preserved audio-menu baseline and the existing local toolchain. This project reassembles compiled DEX and resources; it does not claim successful compilation of all recovered Java.

## Behavior

- API interceptor always sends `app_language: hi` for the existing DeepCine service. Package, app ID, channel, own session and native SDK identity remain unchanged.
- The user's saved display language remains independent. An unset display preference initializes to English; later language-setting changes remain available.
- The fixed India catalog profile supplies the observed Indian recommendations, channels and seasons independently of the interface language. API validation found Season 20; it did not establish availability of the user's requested Season 21.
- Display-only model and binding transformations map 26 observed Hindi menu/filter/audio labels to English when English UI is selected. Filter selections retain their original raw values, and content titles are not indiscriminately translated.
- 33 nullable ad-placement getters are disabled. Existing no-ad player continuations are retained; no rewarded-ad completion or paid membership is fabricated.
- Three ad initialization/preload methods are disabled, 12 ad auto-initializing providers removed, and 22 static ad/subscribe views collapsed.
- The audio/subtitle menu remains accessible. Its tracks still depend on the selected source; a Hindi catalog profile is not proof that every movie has Hindi audio.

## Verification

Signing and 16 KiB native-library alignment passed. All 32 native binaries and all non-DEX non-resource payloads match the baseline. Canonical DEX verification checked 68,817 existing classes, allowing changes only in nine intended classes/43 methods, plus one new display-label helper. No diagnostic observer is included. See `reports/ready-verification.json`, `ready-method-changes.tsv`, `ready-resource-changes.json` and `ready-canonical-verification.log`.

Device verification is recorded separately after installation. Static checks do not by themselves establish long-session playback, every ad path, downloads, casting or all language choices. Backups remain under `../backups/`; original extraction is untouched in `../deepcineph-reconstruction/`. The earlier known-working audio-menu APK is retained for rollback.

## Startup regression correction

The first India build read the display preference before `VCUtils.e(context)` and crashed during Application creation. The corrected build changes the original first-run device-locale default to `en` after context initialization; it adds no pre-initialization preference reads. Saved explicit language choices still use the original branch. See `reports/ready-startup-fix.json` and `startup-crash-before-fix.txt`. The corrected APK SHA-256 is `36425131ccb410320fbbe5b180cec1aa552285ad7f9528693549271fc6c28733`. The failed artifact is retained only under reports/failed-builds for diagnosis.

Corrected build installed and cold-started successfully on SM-G998B (607 ms observed launch). PID 22740 remained alive; no crash-buffer entries were observed for that PID. The Paradise was visible playing fullscreen at a seeked sample position of 2:11:47, with English player controls and no Subscribe button or watch-ad prompt in that capture. This is a sample check, not full-film/all-title/all-ad-path validation. See reports/ready-runtime-check.json.
