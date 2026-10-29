import json,hashlib,pathlib,zipfile
root=pathlib.Path(__file__).parent
apk=root.parent/'deepcineph.apk'
records=json.loads((root/'raw-file-map.json').read_text(encoding='utf-8-sig'))
errors=[]
with zipfile.ZipFile(apk) as z:
    for r in records:
        p=root/'raw-apk'/r['output_path'].replace('\\','/')
        data=p.read_bytes()
        if len(data)!=r['bytes'] or hashlib.sha256(data).hexdigest()!=r['sha256'] or data!=z.read(z.infolist()[r['zip_index']-1]): errors.append(r['original_name'])
report={'apk_sha256':hashlib.sha256(apk.read_bytes()).hexdigest(),'files_verified':len(records),'mismatches':errors,'case_collision_remaps':sum(bool(r['remapping_reason']) for r in records)}
(root/'raw-verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))
