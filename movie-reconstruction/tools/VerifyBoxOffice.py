import hashlib, json, pathlib, struct, subprocess, zipfile, zlib
root=pathlib.Path(__file__).resolve().parent.parent
apk=root/'boxoffice/build/BoxOffice.apk'
expected={'classes5.dex','classes6.dex','classes7.dex','classes8.dex','classes10.dex','classes11.dex'}
changed=[]; unchanged=[]; native=[]
with zipfile.ZipFile(root.parent/'Movie.apk') as before,zipfile.ZipFile(apk) as after:
    for entry in before.infolist():
        name=entry.filename
        if name.endswith('/') or name.startswith(('res/','META-INF/')) or name in ('AndroidManifest.xml','resources.arsc'):continue
        original=before.read(entry); updated=after.read(name)
        if original!=updated:
            if name not in expected:raise RuntimeError('Unexpected payload modification: '+name)
            if original[:8]!=updated[:8]:raise RuntimeError('DEX format changed: '+name)
            if hashlib.sha1(updated[32:]).digest()!=updated[12:32] or zlib.adler32(updated[12:]) & 0xffffffff != struct.unpack_from('<I',updated,8)[0]:raise RuntimeError('DEX checksum invalid')
            if struct.unpack_from('<I',original,96)[0]!=struct.unpack_from('<I',updated,96)[0]:raise RuntimeError('DEX class count changed')
            changed.append(name)
        else:unchanged.append(name)
        if name.startswith('lib/'):native.append({'entry':name,'sha256':hashlib.sha256(updated).hexdigest()})
    if set(changed)!=expected:raise RuntimeError('Unexpected changed DEX set')
    if after.read('classes10.dex')!=(root/'boxoffice/patched/classes10.dex').read_bytes():raise RuntimeError('Ad getter patch differs from audited output')
    if after.read('classes6.dex')!=(root/'boxoffice/patched/classes6.dex').read_bytes():raise RuntimeError('Center animation patch differs from audited output')
    if after.read('classes11.dex')!=(root/'tools/native-tracing/sdk-dex/classes11.dex').read_bytes():raise RuntimeError('Playback helper DEX changed unexpectedly')
bt=pathlib.Path(r'C:\Users\AlphaDell-60\AppData\Local\Android\Sdk\build-tools\36.1.0')
badging=subprocess.check_output([str(bt/'aapt2.exe'),'dump','badging',str(apk)],text=True,encoding='utf-8')
if "application-label:'BoxOffice'" not in badging or "package: name='com.fvvcl.flickverse'" not in badging:raise RuntimeError('Brand/package verification failed')
(root/'reports/boxoffice-badging.txt').write_text(badging,encoding='utf-8')
report={'apk':str(apk),'sha256':hashlib.file_digest(apk.open('rb'),'sha256').hexdigest(),'label':'BoxOffice','package':'com.fvvcl.flickverse','changed_dex':changed,'unchanged_non_resource_payloads':len(unchanged),'unchanged_native_libraries':native,'ad_placement_getters_disabled':25,'runtime_verified':False}
(root/'reports/boxoffice-verification.json').write_text(json.dumps(report,indent=2))
print('Verified BoxOffice label, package, original DEX formats/class counts/checksums,',len(unchanged),'unchanged payloads and',len(native),'unchanged native libraries')
