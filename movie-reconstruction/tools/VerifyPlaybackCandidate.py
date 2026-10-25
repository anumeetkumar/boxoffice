import hashlib, json, pathlib, struct, zipfile, zlib

root = pathlib.Path(__file__).resolve().parent.parent
candidate = root / 'bytecode-app/build/outputs/apk/playback-candidate/movie-playback-candidate.apk'
expected_changes = {'classes5.dex', 'classes11.dex'}
unchanged, changed = [], []
with zipfile.ZipFile(root.parent / 'Movie.apk') as before, zipfile.ZipFile(candidate) as after:
    if set(before.namelist()) != set(after.namelist()):
        raise RuntimeError('Unexpected archive entry additions/removals')
    for entry in before.infolist():
        old, new = before.read(entry), after.read(entry.filename)
        if old == new:
            unchanged.append(entry.filename)
            continue
        if entry.filename not in expected_changes:
            raise RuntimeError('Unexpected modified payload: ' + entry.filename)
        if old[:8] != new[:8] or new[:8] != b'dex\n037\0':
            raise RuntimeError('DEX format version mismatch')
        if hashlib.sha1(new[32:]).digest() != new[12:32] or zlib.adler32(new[12:]) & 0xffffffff != struct.unpack_from('<I', new, 8)[0]:
            raise RuntimeError('DEX checksum mismatch')
        old_classes, new_classes = struct.unpack_from('<I', old, 96)[0], struct.unpack_from('<I', new, 96)[0]
        if old_classes != new_classes:
            raise RuntimeError('DEX class count changed')
        changed.append({'entry': entry.filename, 'classes': new_classes, 'sha256': hashlib.sha256(new).hexdigest(), 'dex_version': '037'})
if {item['entry'] for item in changed} != expected_changes:
    raise RuntimeError('Expected exactly two modified DEX files')
report = {'candidate': str(candidate), 'candidate_sha256': hashlib.file_digest(candidate.open('rb'), 'sha256').hexdigest(), 'unchanged_entries': len(unchanged), 'original_manifest_resources_native_assets_preserved': True, 'changed_entries': changed, 'archive_and_dex_checks_passed': True}
(root / 'reports/playback-candidate-verification.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
