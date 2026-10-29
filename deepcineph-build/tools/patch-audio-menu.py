import pathlib,zipfile,json,re,hashlib,zlib,struct
root=pathlib.Path(__file__).resolve().parents[1]
base=root/'output/DeepCine-test.apk';expected='6c3c451e07a91c39c14d7412db777954b5432d7f7a68f5c4ce68a75da2ba03cf'
assert hashlib.sha256(base.read_bytes()).hexdigest()==expected,'Baseline changed'
lines=(root/'reports/player-inspection.txt').read_text().splitlines();hits=[]
for i,line in enumerate(lines):
    if 'INVOKE_STATIC Ljava/util/Objects;->equals' in line and 'CONST_STRING hi' in lines[i-1] and 'MOVE_RESULT ' in lines[i+1] and 'IF_EQZ ' in lines[i+2]:hits.append(int(lines[i+2].split()[0]))
assert len(hits)==1,hits
offset=hits[0]
with zipfile.ZipFile(base) as z:data=bytearray(z.read('classes5.dex'))
assert data[offset]==0x38, data[offset:offset+4].hex()
old=bytes(data[offset:offset+4]);data[offset:offset+4]=b'\0'*4
# Keep instruction addresses and all DEX tables unchanged; repair standard DEX integrity fields.
data[12:32]=hashlib.sha1(data[32:]).digest();struct.pack_into('<I',data,8,zlib.adler32(data[12:])&0xffffffff)
out=root/'output/DeepCine-audio-menu-unsigned.apk'
with zipfile.ZipFile(base) as before,zipfile.ZipFile(out,'w') as after:
    for e in before.infolist():
        if e.filename.startswith('META-INF/'):continue
        after.writestr(e,bytes(data) if e.filename=='classes5.dex' else before.read(e))
report={'baseline_sha256':expected,'changed_dex':'classes5.dex','method':'com.mgs.carparking.ui.VideoPlayDetailActivity.onConfigurationChanged','offset':offset,'before':old.hex(),'after':'00000000','change':'Remove only the conditional branch hiding the fullscreen audio/subtitle control for non-Hindi metadata','request_and_backend_changes':False,'hindi_label_faked':False}
(root/'reports/audio-menu-patch.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
