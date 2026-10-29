# Current build

`output/DeepCine-India.apk` is the current corrected build, installed on the S21. It keeps the API profile Hindi independently of the saved UI language and disables ad placements/upsells. The startup-order regression was fixed and a fullscreen Paradise playback sample was observed with English controls. See [READY.md](READY.md) and `reports/ready-runtime-check.json`. The previous audio-menu baseline remains available for rollback.
# DeepCine Test build

Run `./Build.ps1` from this directory. Output: `output/DeepCine-test.apk`.

This is a separate fallback experiment for the unresolved BoxOffice playback issue. See `reports/comparison.md`. A different default backend and app identity do not establish a playback fix.

The build uses a working copy of extracted resources and original compiled DEX, not compilation of the recovered Java. It retains package `com.velvetreel.shorttv`, app ID `deepcineph`, SDK channel 65 and all original native libraries. The display label is DeepCine Test. The local certificate-derived SDK configuration changes to match the actual test signer; the original publisher identity is not spoofed. Ads, logo and playback controls remain as shipped by DeepCine in this baseline build.

The script requires a verified extraction backup under `../backups/` before assembling the APK. The original extraction under `../deepcineph-reconstruction/` is kept unchanged. The backup contains the original APK and extracted code, resources, original payloads, indexes and logs; temporary REA engine/session cache is excluded. Its embedded BACKUP-MANIFEST.json lists per-file hashes, and the adjacent JSON records archive verification and SHA-256.

Verification checks signing, APK alignment, original non-resource payload hashes and canonical disassembly of every class in the two reassembled DEX files. Only the two native SDK initialization constants are allowed to differ in that disassembly comparison. Native binaries are preserved unchanged.

No original private signing key or source build metadata was recovered. The S21 was subsequently connected. The separate test app installed and launched successfully; the home catalog loaded and Matchbox the Movie showed a player position of 00:05 with a 2:06:07 duration. Sustained playback remains unverified. See reports/s21-runtime-check.json. BoxOffice was not replaced, and no app was uninstalled.

Follow-up: the Paradise movie sample was subsequently observed playing on the S21 with changing frames and approximately one minute of progress. See reports/india-catalog-comparison.md for catalog/audio limitations and feasible client changes.

## Audio-menu update

Current manual-test artifact: `output/DeepCine-audio-menu.apk`, installed as a data-preserving update on the S21. The verified baseline `output/DeepCine-test.apk` is retained. Run `./BuildAudioMenu.ps1` against that exact baseline to regenerate this update.

The original fullscreen code showed `ll_audio_subtitle` only when title metadata `vod_lang` equals `hi`. The update removes only that branch, showing the existing real track-selection popup for other title languages. Portrait visibility, selection callbacks, requests, playback URLs and native SDK code are unchanged. The patch does not relabel original audio as Hindi or create unavailable tracks. Signed APK SHA-256: `43d84fbbea013308315b1d426216dbbd546ddc733080e7409982d8a88dfa691b`.

Static verification passed: signature, alignment, 3,616 archive payload entries, unchanged DEX size, and an exact byte-difference allowlist limited to the branch plus standard DEX integrity fields. Manual verification of menu visibility and actual language switching is pending. See `reports/audio-menu-verification.json`.

Bigg Boss follow-up: the detail model includes a `series_info` field whose entries contain `series` and `vod_id`. A missing season in top-level search could be grouped in a detail response. The season dropdown needs checking before concluding the requested season is unavailable across the service.

## Live API follow-up

The live host is `deepcineph.7nkznc.com`. Requests using the original client did not reveal the requested newer Bigg Boss seasons or a Hindi Street Fighter source. Genre/year/sort were advertised; region/language probes did not supply the missing content. See `reports/live-catalog-findings.md` and its redacted evidence. The normal audio-menu APK is restored after this diagnostic pass.

