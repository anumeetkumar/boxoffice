import hashlib,json,pathlib,zipfile
base=pathlib.Path(__file__).resolve().parents[2]
old='9d0ed3d8efd5204654f4e6ca4a0e52fd'
package='com.velvetreel.shorttv';channel='65'
assert hashlib.md5(f'048F0D2737E3C7528ECAAD3D43B67E70+{package}+{channel}'.encode()).hexdigest()==old
new=hashlib.md5(f'66DDA37731D61DB6C753CD950AA7E82C+{package}+{channel}'.encode()).hexdigest()
with zipfile.ZipFile(base/'deepcineph.apk') as z:
    dex=[e.filename for e in z.infolist() if e.filename.endswith('.dex') and old.encode() in z.read(e)]
with zipfile.ZipFile(base/'Movie.apk') as a,zipfile.ZipFile(base/'deepcineph.apk') as b:
    native=[]
    for name in b.namelist():
        if name.startswith('lib/') and name.endswith('.so'):
            native.append({'path':name,'same_as_movie':name in a.namelist() and a.read(name)==b.read(name)})
report={'old_sdk_configuration':old,'new_sdk_configuration':new,'dex_to_reassemble':dex,'native_comparison':native,'movie_backend':'https://moviein.ajfysu.com/','deepcine_backend':'https://velvetreel.7nkznc.com/','deepcine_app_id':'deepcineph','package':package,'native_channel':channel,'playback_flow':'Same verify control request pattern, device ID plus vod ID plus timestamp; response proof forwarded to /api/vod/info_new','conclusion':'Different service identity; no verified fix for the Movie backend device-specific replacement response. Rebuilt DeepCine requires independent runtime validation.'}
(base/'deepcineph-build/reports/comparison.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='native_comparison'},indent=2))
