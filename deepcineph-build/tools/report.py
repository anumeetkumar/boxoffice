import pathlib,json
root=pathlib.Path(__file__).resolve().parents[1]
r=json.loads((root/'reports/comparison.json').read_text())
rows=r['native_comparison']
text='''# DeepCine comparison and rebuild decision

The extracted DeepCine code does not establish a fix for the device-specific replacement response from Movie/BoxOffice. Both request paths use `/control?msg=verify` with a device identity, movie ID and timestamp, then forward the generated proof into `/api/vod/info_new`. Matching the proof-generation pattern does not prove backend acceptance.

DeepCine has a separate default backend (`https://velvetreel.7nkznc.com/`), package (`com.velvetreel.shorttv`), app ID (`deepcineph`) and SDK channel (`65`). Its API version header is still `40000`. It cannot be treated as a new version of the Movie service solely because its classes have clearer names. Runtime API-domain configuration can change the literal default.

The chosen fallback is a separate DeepCine Test APK. It preserves DeepCine's identity and request flow, original native binaries and assets. The display label and local certificate-derived SDK initialization setting are updated for a genuine local test certificate. No original certificate, session token, device identity or backend authorization is impersonated.

The APK uses extracted compiled DEX; the decompiled Java is retained for review, not represented as a successfully compiled original project. The initial test build retains DeepCine's original advertising and player behavior. Prior BoxOffice ad removal, branding and control changes are not yet ported.

No phone was attached when ADB was checked. A signed/aligned APK passing static checks is not proof that its backend will allow playback. Device playback remains unverified.

Source evidence:
- `deepcineph-reconstruction/jadx-export/sources/com/mgs/carparking/util/RetrofitClient.java`: app headers and identity.
- `.../app/HttpsUtils.java`: default API host.
- `.../ui/VideoPlayDetailActivity.java`: native verify control request.
- `.../model/VIDEOPLAYDETAILVIEWMODEL.java`: playback request form.
- `.../app/AppApplication.java`: native SDK initialization.

'''
text+=f"Of {len(rows)} DeepCine native-library paths, {sum(x['same_as_movie'] for x in rows)} are byte-identical to the same path in Movie.apk. See comparison.json for each path. This comparison does not establish identical backend behavior.\n"
(root/'reports/comparison.md').write_text(text)
print(text.splitlines()[-1])
