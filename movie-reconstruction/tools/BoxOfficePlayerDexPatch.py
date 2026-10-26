"""Keep the center control row in the existing show/hide animation in both orientations."""
import pathlib,struct,zipfile,hashlib,zlib,json
root=pathlib.Path(__file__).resolve().parent.parent
with zipfile.ZipFile(root.parent/'Movie.apk') as apk:data=bytearray(apk.read('classes6.dex'))
u32=lambda at:struct.unpack_from('<I',data,at)[0]
def uleb(at):
    value=shift=0
    while True:
        b=data[at];at+=1;value|=(b&127)<<shift
        if b<128:return value,at
        shift+=7
strings=[]
for i in range(u32(56)):
    _,at=uleb(u32(u32(60)+i*4));strings.append(bytes(data[at:data.index(0,at)]).decode('utf-8',errors='replace'))
types=[strings[u32(u32(68)+i*4)] for i in range(u32(64))]
methods=[]
for i in range(u32(88)):
    owner,proto,name=struct.unpack_from('<HHI',data,u32(92)+i*8);methods.append((types[owner],strings[name]))
boolean=methods.index(('Ljava/lang/Boolean;','booleanValue'))
patches=[]
for i in range(u32(96)):
    entry=u32(100)+32*i
    if types[u32(entry)]!='Lcom/google/android/exoplayer2/ui/PlayerControlView;':continue
    at=u32(entry+24)
    static,at=uleb(at);instance,at=uleb(at);direct,at=uleb(at);virtual,at=uleb(at)
    for _ in range(static+instance):_,at=uleb(at);_,at=uleb(at)
    for count in (direct,virtual):
        index=0
        for _ in range(count):
            delta,at=uleb(at);index+=delta;_,at=uleb(at);code,at=uleb(at)
            if methods[index][1]!='S':continue
            begin=code+16;end=begin+u32(code+12)*2
            for p in range(begin,end-12,2):
                if data[p]==0x6e and struct.unpack_from('<H',data,p+2)[0]==boolean and data[p+6]==0x0a and data[p+8]==0x38:
                    patches.append({'method':'PlayerControlView.S','offset':p+8,'before':bytes(data[p+8:p+12]).hex(),'after':'00000000'})
                    data[p+8:p+12]=b'\0'*4
if len(patches)!=1:raise RuntimeError('Expected one fullscreen-only center animation branch')
data[12:32]=hashlib.sha1(data[32:]).digest();struct.pack_into('<I',data,8,zlib.adler32(data[12:])&0xffffffff)
(root/'boxoffice/patched/classes6.dex').write_bytes(data)
(root/'reports/boxoffice-player-animation-patch.json').write_text(json.dumps(patches,indent=2))
print('Center controls now participate in the original show/hide animation in portrait and fullscreen')
