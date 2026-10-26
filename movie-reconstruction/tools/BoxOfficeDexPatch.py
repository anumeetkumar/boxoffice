"""Disable ad placement getters without changing DEX table indexes or layout."""
import hashlib, json, pathlib, struct, zipfile, zlib
root = pathlib.Path(__file__).resolve().parent.parent
work = root / 'boxoffice'
(work / 'patched').mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(root.parent / 'Movie.apk') as apk:
    data = bytearray(apk.read('classes10.dex'))
u32 = lambda offset: struct.unpack_from('<I', data, offset)[0]
def uleb(offset):
    value, shift = 0, 0
    while True:
        b = data[offset]; offset += 1
        value |= (b & 127) << shift
        if b < 128: return value, offset
        shift += 7
strings = []
for i in range(u32(56)):
    _, at = uleb(u32(u32(60) + i * 4))
    end = data.index(0, at)
    strings.append(bytes(data[at:end]).decode('utf-8', errors='replace'))
types = [strings[u32(u32(68) + i * 4)] for i in range(u32(64))]
empty_list_field = None
for i in range(u32(80)):
    owner, kind, name = struct.unpack_from('<HHI', data, u32(84) + i * 8)
    if types[owner] == 'Ljava/util/Collections;' and strings[name] == 'EMPTY_LIST' and types[kind] == 'Ljava/util/List;':
        empty_list_field = i
        break
if empty_list_field is None:
    raise RuntimeError('No existing Collections.EMPTY_LIST field reference; use semantic DEX assembly instead')
methods = []
for i in range(u32(88)):
    owner, proto, name = struct.unpack_from('<HHI', data, u32(92) + i * 8)
    methods.append((types[owner], strings[name]))
patched = []
volume_patched = []
for i in range(u32(96)):
    entry = u32(100) + i * 32
    if types[u32(entry)] not in ('Lcom/mgs/carparking/netbean/AdInfoEntry;', 'Lgb/l$a;'): continue
    at = u32(entry + 24)
    static, at = uleb(at); instance, at = uleb(at)
    direct, at = uleb(at); virtual, at = uleb(at)
    for _ in range(static + instance):
        _, at = uleb(at); _, at = uleb(at)
    for count in (direct, virtual):
        index = 0
        for _ in range(count):
            delta, at = uleb(at); index += delta
            _, at = uleb(at); code, at = uleb(at)
            owner, name = methods[index]
            if owner == 'Lgb/l$a;' and name == 'onProgressChanged':
                start=code+16; end=start+u32(code+12)*2
                matches=[p for p in range(start,end,2) if data[p:p+2] == b'\x12\x40']
                if len(matches)!=1: raise RuntimeError('Unexpected download-volume sound flag layout')
                at_flag=matches[0]; data[at_flag+1]=0
                volume_patched.append({'method':owner+'->'+name,'offset':at_flag,'before':'1240','after':'1200'})
                continue
            if not name.startswith('getAd_position_'): continue
            if not code or u32(code + 12) != 3:
                raise RuntimeError('Unexpected ad getter layout: ' + name)
            insns = code + 16
            original = bytes(data[insns:insns+6])
            if data[insns] != 0x54 or data[insns+4:insns+6] != b'\x11\x00':
                raise RuntimeError('Unexpected getter instructions: ' + name)
            # sget-object v0, Collections.EMPTY_LIST; return-object v0.
            struct.pack_into('<HHH', data, insns, 0x0062, empty_list_field, 0x0011)
            patched.append({'method': name, 'code_offset': code, 'original_instructions': original.hex(), 'replacement_instructions': bytes(data[insns:insns+6]).hex()})
if len(patched) != 25:
    raise RuntimeError(f'Expected 25 ad placement getters, found {len(patched)}')
if len(volume_patched)!=1:raise RuntimeError('Download-volume sound flag was not patched')
data[12:32] = hashlib.sha1(data[32:]).digest()
struct.pack_into('<I', data, 8, zlib.adler32(data[12:]) & 0xffffffff)
(work / 'patched/classes10.dex').write_bytes(data)
(root / 'reports/boxoffice-ad-placement-patch.json').write_text(json.dumps({'existing_empty_list_field': empty_list_field, 'patched_getters': patched, 'silent_volume_patch':volume_patched, 'all_indexes_and_code_sizes_preserved': True, 'sha256': hashlib.sha256(data).hexdigest()}, indent=2))
print('Disabled', len(patched), 'ad placement getters using the existing Collections.EMPTY_LIST field')
