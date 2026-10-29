# Live catalog and Hindi-source checks

The S21 tests used DeepCine's own Retrofit client, session and native proof generation. The actual configured host was deepcineph.7nkznc.com, rather than merely the APK's literal default host. Credentials and video URLs were redacted inside the app; no Movie token or identity was copied.

| Test | Observed result |
| --- | --- |
| Bigg Boss search page 1 | OTT Season 3 and Marathi Season 5 |
| Bigg Boss search page 2 | Empty |
| Bigg Boss 20 / Bigg Boss 21 searches | Empty |
| Alternate Big Boss query | OTT Season 3 |
| Hindi-script title query | Empty |
| OTT Season 3 detail series_info | Only Season 3 |
| Street Fighter audio_type 0, 1, 2 | Only Original advertised; vod_lang en |
| Fullscreen actual stream tracks | User confirmed only English |
| Advertised category filters | Genre/type, year, sort; no region or audio-language group |
| Latest baseline vs audio_lang hi | Identical 20 titles, all labelled en |
| audio_lang Hindi | Empty list |
| area India | Call failed; exact status/reason not retained by the first observer |

These results cover the tested queries, title, and filter values. They do not prove that every DeepCine title lacks Hindi or that no other catalog alias exists. The area failure is not described as a specific backend rejection because that detail was not captured.

## Movie comparison

Movie's detail model reads audio_type_option and uses the returned type_name values for its language controls. Its request sends audio_type. DeepCine already supports these fields and a separate in-stream track selector. The fullscreen control was hidden unless vod_lang was hi; that client issue is fixed in the clean DeepCine-audio-menu.apk, and the user confirmed the menu now appears.

The three Street Fighter audio-source requests did not expose a separate Hindi source. Showing a Hindi label would not create that audio track. Likewise, adding a fake season or unsupported India filter would not supply playable episodes.

Movie and DeepCine have different hosts, app IDs, channels and SDK configuration. No verified setting or endpoint was found that makes DeepCine supply Movie's India catalog while retaining DeepCine's working playback service. Repointing to Movie has not resolved the previously observed device-specific replacement response. Backend catalog policy remains unknown, and a backend acceptance fix is not claimed.

## Build state and evidence

The clean audio-menu build is restored after diagnostics. It preserves the existing app data and removes the temporary observer. No catalog/API identity modification is shipped as a supposed fix.

Evidence: live-catalog-findings.json, catalog-api-capture.jsonl, catalog-filter-probes.jsonl, catalog-api-check.log, catalog-filter-probes.log. The intact extraction backup and baseline APK remain preserved.

**Follow-up correction:** The broader two-provider matrix tested the `app_language: hi` header, which was not the same as the earlier `audio_lang` body-filter probes. That header did return DeepCine's broader Indian catalog. Matching Hindi-profile playback details are now being checked in the API workbench; earlier negative region/body-filter findings do not rule out this header-based catalog profile.
