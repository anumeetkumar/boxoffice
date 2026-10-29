import pathlib,zipfile,hashlib,json,datetime
base=pathlib.Path(__file__).resolve().parents[2]
source=base/'deepcineph-reconstruction'
stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
archive=base/'backups'/f'deepcineph-extraction-{stamp}.zip'
records=[]
with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as z:
    files=[base/'deepcineph.apk']+sorted(p for p in source.rglob('*') if p.is_file() and 'temp' not in p.relative_to(source).parts)
    for p in files:
        data=p.read_bytes(); name=p.relative_to(base).as_posix()
        z.writestr(name,data)
        records.append({'path':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
    z.writestr('BACKUP-MANIFEST.json',json.dumps(records,indent=2))
with zipfile.ZipFile(archive) as z:
    for r in records:
        data=z.read(r['path'])
        if len(data)!=r['bytes'] or hashlib.sha256(data).hexdigest()!=r['sha256']:raise RuntimeError(r['path'])
result={'archive':str(archive),'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'verified_files':len(records),'excluded':'temporary REA engine/session cache only','verified':True}
(archive.with_suffix('.json')).write_text(json.dumps(result,indent=2))
print(json.dumps(result))
