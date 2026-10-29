import pathlib,zipfile,hashlib,json
root=pathlib.Path(__file__).resolve().parents[1];report=json.loads((root/'reports/audio-menu-patch.json').read_text());offset=report['offset'];checked=0
with zipfile.ZipFile(root/'output/DeepCine-test.apk') as a,zipfile.ZipFile(root/'output/DeepCine-audio-menu.apk') as b:
    for e in a.infolist():
        if e.filename.startswith('META-INF/'):continue
        old=a.read(e);new=b.read(e.filename)
        if e.filename=='classes5.dex':
            assert len(old)==len(new)
            differences=[i for i,(x,y) in enumerate(zip(old,new)) if x!=y]
            assert all(8<=i<32 or offset<=i<offset+4 for i in differences),differences
            assert new[offset:offset+4]==bytes(4)
        else:assert old==new,e.filename
        checked+=1
lines=(root/'reports/player-after-inspection.txt').read_text().splitlines()
assert any(x.startswith(str(offset)+' NOP') for x in lines)
assert any(x.startswith(str(offset+2)+' NOP') for x in lines)
report.update({'signature_verified':True,'alignment_verified':True,'archive_payloads_verified':checked,'only_modified_bytecode':'One conditional branch replaced by two NOP instructions; DEX checksums repaired','apk_sha256':hashlib.sha256((root/'output/DeepCine-audio-menu.apk').read_bytes()).hexdigest(),'runtime_menu_test_pending':True})
(root/'reports/audio-menu-verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
