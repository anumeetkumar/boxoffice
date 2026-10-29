# Movie vs DeepCine: Indian catalog and audio languages

DeepCine Test plays the tested Paradise movie sample on the S21, including changing frames and progress of approximately one minute. This validates that sample in the new build; it does not fix the independent Movie/BoxOffice backend rejection, validate the entire film, or establish all-title playback.

| Area | Movie / BoxOffice | DeepCine Test |
| --- | --- | --- |
| Default backend | moviein.ajfysu.com | velvetreel.7nkznc.com |
| App identity | moviein; moviein_1001 | deepcineph; deepcineph_1002 |
| Package | com.fvvcl.flickverse | com.velvetreel.shorttv |
| Search API | /api/search/result | /api/search/result |
| Player detail API | /api/vod/info_new | /api/vod/info_new |
| Language choices | Reads audio_type_option | Already reads audio_type_option into a selectable list |
| Chosen audio request | audio_type | audio_type |
| Backend acceptance on S21 | Unresolved replacement response | Tested Paradise movie sample played |

## Observations and limits

The current DeepCine search for Bigg Boss visibly returned Bigg Boss OTT Season 3 and Bigg Boss Marathi Season 5. The requested latest season was not in those visible results. This is not an exhaustive inventory of every server page or title alias. DeepCine is not wholly missing Indian titles: The Paradise was found and played.

The ordinary search request includes kw, optional type_pid, page pn, and an occasional certificate field. No explicit India/Philippines area filter was found in that request construction. Its results are mapped into movie/TV/variety/anime rows by type_pid. This provides no evidence that a simple local regional toggle is hiding the latest season; backend catalog or configuration is the leading remaining explanation, not a proven internal server rule.

The language selector is not missing from DeepCine's implementation. Its detail response model declares audio_type and audio_type_option. The player model displays the returned choices, selects a type, and submits audio_type on the next detail request. A title exposing only Original can therefore lack alternate sources in the response. Actual per-title response values still need capture before attributing every missing-language case to the server. The app's Settings language controls interface/request language and is distinct from movie audio.

## What can be built

1. India-focused navigation and rows for Indian movies, TV, Hindi and regional languages, using catalog filter values actually supported by the service. CHANNELVIEWMODEL sends area; LOOKCHANNELVIEWMODEL sends audio_lang. Backend-supported values must be verified before hardcoding defaults.
2. A clear audio selector that lists actual available streams, preserves the selected type when episodes change, and distinguishes interface language, audio, and subtitles. Verify using a title whose response supplies multiple audio_type_option entries.
3. Port BoxOffice branding, ad removal and player controls separately after preserving this working baseline. None of these UI changes supplies additional titles or audio files.
4. To match Movie's exact newer seasons and catalog, obtain a working, authorized India catalog/playback service or provider configuration. Catalog records, episode sources and alternate audio must be available there. Merely adding Netflix/Amazon labels does not add their content or establish an official platform integration. No official Netflix/Amazon catalog integration has been verified from these artifacts.

Do not transplant Movie tokens, spoof its signing identity or assume IDs are interchangeable. A direct switch back to Movie's backend may restore its catalog responses while reintroducing its unresolved device validation issue. Combining that catalog with the new player is a hypothesis, not a verified fix.

## Source evidence

- DeepCine util/RetrofitClient.java:72-95: app/package/channel/version headers.
- DeepCine app/HttpsUtils.java:67: default host.
- Both APK manifests: UMENG_CHANNEL values.
- DeepCine model/HOMECONTENTSEARCHLISTVIEWMODEL.java:269 onward: search request and result mapping.
- DeepCine model/CHANNELVIEWMODEL.java:491 onward: area filter.
- DeepCine model/LOOKCHANNELVIEWMODEL.java:530 onward: audio_lang filter.
- DeepCine model/VIDEOPLAYDETAILVIEWMODEL.java:314,1046,1327,1362: available audio options, selection, request form, language list.
- Movie model/VIDEOPLAYDETAILVIEWMODEL.java:510,1125: available audio options and request audio_type.

Full source roots are ../deepcineph-reconstruction/jadx-export/sources/ and ../rea/_reference/movie-review/jadx-export/sources/.
