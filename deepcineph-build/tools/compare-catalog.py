import pathlib,json
base=pathlib.Path(__file__).resolve().parents[2];root=base/'deepcineph-build'
load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
old=load(base/'rea/_reference/movie-review/api-routes.json');new=load(base/'deepcineph-reconstruction/api-routes.json')
a={(x['verb'],x['route']) for x in old};b={(x['verb'],x['route']) for x in new}
report={'comparison_scope':'Static extracted code plus observed DeepCine search and sample playback on S21; no API credentials or identities transplanted','movie':{'host':'https://moviein.ajfysu.com/','app_id':'moviein','channel':'moviein_1001','package':'com.fvvcl.flickverse'},'deepcine':{'host':'https://velvetreel.7nkznc.com/','app_id':'deepcineph','channel':'deepcineph_1002','package':'com.velvetreel.shorttv'},'shared_route_declarations':sorted([{'verb':v,'route':r} for v,r in a&b],key=lambda x:x['route']),'audio_support':{'movie':'Consumes audio_type_option; submits audio_type','deepcine':'Consumes audio_type_option into language item models; submits audio_type; already implemented','ui_language_is_audio_selection':False},'deepcine_filters':{'category':'type_id,type,area,year,sort,pn','audio_category':'type_id,type,audio_lang,year,sort,pn','search':'kw,optional type_pid,pn,occasional sr; no explicit India/Philippines area filter in this request construction'},'observed_search':{'query':'Bigg Boss','visible_results':['Bigg Boss OTT - Season 3','Bigg Boss Marathi - Season 5'],'latest_season_in_visible_results':False,'exhaustive_catalog_inventory':False},'verified_new_build_movie_sample':{'title':'The Paradise','different_frames_observed':True,'progress':'approximately one minute','replacement_notice_seen':False,'entire_film_or_all_titles_verified':False},'decision':'India-oriented navigation and response-backed language controls are client work. Exact Movie catalog/latest seasons/audio assets require an available authorized content backend; a player/UI patch alone cannot supply absent streams. Switching host/app identity is not a verified solution and may reproduce the unresolved Movie validation response.'}
(root/'reports/india-catalog-comparison.json').write_text(json.dumps(report,indent=2))
text='''# Movie vs DeepCine: Indian catalog and audio languages

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
'''
(root/'reports/india-catalog-comparison.md').write_text(text)
p=root/'reports/s21-runtime-check.json';r=load(p);r['movie_sample_playback_verified']=True;r['verified_sample']=report['verified_new_build_movie_sample'];r['limitation']='Limited movie sample only; newest series and alternate audio are not verified. Separate Movie backend failure remains unresolved.';p.write_text(json.dumps(r,indent=2))
p=root/'README.md';t=p.read_text();t+='\nFollow-up: the Paradise movie sample was subsequently observed playing on the S21 with changing frames and approximately one minute of progress. See reports/india-catalog-comparison.md for catalog/audio limitations and feasible client changes.\n';p.write_text(t)
print('Saved catalog/audio comparison and updated runtime evidence.')
