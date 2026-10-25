"""Update the certificate-derived SDK configuration, preserving original DEX code."""
import hashlib, json, pathlib, zipfile

root = pathlib.Path(__file__).resolve().parent.parent
original = root.parent / 'Movie.apk'
expected = 'cdc0d88ebcd6ad10d04e9e09f8b75fdeabd91369b9a524827cabfcbb9e7ad4f9'
if hashlib.file_digest(original.open('rb'), 'sha256').hexdigest() != expected:
    raise RuntimeError('Original APK hash mismatch')
package, channel = 'com.fvvcl.flickverse', '63'
original_cert_md5 = '099656628B5CF75B43B04EECE0E62FA4'
candidate_cert_md5 = '66DDA37731D61DB6C753CD950AA7E82C'
old_key = hashlib.md5(f'{original_cert_md5}+{package}+{channel}'.encode()).hexdigest()
new_key = hashlib.md5(f'{candidate_cert_md5}+{package}+{channel}'.encode()).hexdigest()
if old_key != '918ef3452da2728168006719d78815a6':
    raise RuntimeError('SDK configuration derivation mismatch')
output = root / 'bytecode-app/build/outputs/apk/playback-candidate'
output.mkdir(parents=True, exist_ok=True)
unsigned = output / 'movie-playback-unsigned.apk'
changes = []
with zipfile.ZipFile(original) as before, zipfile.ZipFile(unsigned, 'w') as after:
    for entry in before.infolist():
        data = before.read(entry)
        if entry.filename.endswith('.dex') and data.startswith(b'dex\n'):
            # Only replace the fixed-length UTF-8 string data item; no code/offset changes.
            needle = b'\x20' + old_key.encode() + b'\x00'
            count = data.count(needle)
            if count:
                # Use the assembler output: direct string replacement would leave
                # the DEX string table in the wrong sort order.
                rebuilt = root / 'tools/native-tracing/sdk-dex' / entry.filename
                if not rebuilt.exists():
                    raise RuntimeError('Reassemble the SDK DEX files first with RebuildSdkDex.java')
                updated = rebuilt.read_bytes()
                if updated[:8] != data[:8]:
                    raise RuntimeError('Reassembled DEX format differs from the original version')
                if old_key.encode() in updated or new_key.encode() not in updated:
                    raise RuntimeError('Reassembled DEX SDK configuration mismatch')
                changes.append({'entry': entry.filename, 'string_items_updated': count, 'before_sha256': hashlib.sha256(data).hexdigest(), 'after_sha256': hashlib.sha256(updated).hexdigest()})
                data = bytes(updated)
        after.writestr(entry, data)
if not changes:
    raise RuntimeError('No matching SDK configuration string found')
(root / 'reports/playback-candidate-build.json').write_text(json.dumps({'original_sha256': expected, 'original_cert_md5': original_cert_md5, 'candidate_cert_md5': candidate_cert_md5, 'derivation': 'MD5(uppercase certificate MD5 + "+" + package + "+" + channel)', 'old_sdk_configuration': old_key, 'new_sdk_configuration': new_key, 'changes': changes, 'playback_verified': False}, indent=2))
print(json.dumps({'unsigned_apk': str(unsigned), 'changes': changes, 'new_sdk_configuration': new_key}, indent=2))
