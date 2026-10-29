import pathlib,zipfile,hashlib,json,subprocess
root=pathlib.Path(__file__).resolve().parents[1];base=root.parent
apk=root/'output/DeepCine-test.apk'; changed={'classes.dex','classes3.dex'}; checked=[]
with zipfile.ZipFile(base/'deepcineph.apk') as before,zipfile.ZipFile(apk) as after:
    for info in before.infolist():
        name=info.filename
        if name.endswith('/') or name.startswith(('res/','META-INF/')) or name in {'resources.arsc','AndroidManifest.xml'}:continue
        old=before.read(info);new=after.read(name)
        if name not in changed and old!=new:raise RuntimeError('Payload changed: '+name)
        checked.append({'path':name,'unchanged':old==new,'sha256':hashlib.sha256(new).hexdigest()})
    for name in changed:
        data=after.read(name)
        if b'9d0ed3d8efd5204654f4e6ca4a0e52fd' in data or b'691c5f5ff7b2d3054de60e744c53c242' not in data:raise RuntimeError('SDK config mismatch')
result={'apk':str(apk),'sha256':hashlib.sha256(apk.read_bytes()).hexdigest(),'payload_files_checked':len(checked),'modified_dex':sorted(changed),'payloads':checked,'source_java_compiled':False,'runtime_playback_verified':False,'signing_identity':'Local debug certificate; original publisher certificate is not impersonated'}
(root/'reports/build-verification.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='payloads'},indent=2))
