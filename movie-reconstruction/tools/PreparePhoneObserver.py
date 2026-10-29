import pathlib,urllib.request,json,hashlib,lzma
root=pathlib.Path(__file__).resolve().parent.parent
work=root/'tools/native-tracing';name='frida-gadget-17.23.2-android-arm64.so.xz'
request=urllib.request.Request('https://api.github.com/repos/frida/frida/releases/tags/17.23.2',headers={'User-Agent':'BoxOffice-user-requested-diagnostics'})
with urllib.request.urlopen(request,timeout=60) as response:release=json.load(response)
asset=next(a for a in release['assets'] if a['name']==name)
expected=asset.get('digest','')
if not expected.startswith('sha256:'):raise RuntimeError('Official asset SHA256 missing')
dest=work/name
if not dest.exists() or hashlib.sha256(dest.read_bytes()).hexdigest()!=expected[7:]:
    with urllib.request.urlopen(asset['browser_download_url'],timeout=90) as response:payload=response.read()
    if hashlib.sha256(payload).hexdigest()!=expected[7:]:raise RuntimeError('Official asset checksum mismatch')
    dest.write_bytes(payload)
target=work/'frida-gadget-arm64.so';target.write_bytes(lzma.decompress(dest.read_bytes()))
(work/'phone-observer-provenance.json').write_text(json.dumps({'url':asset['browser_download_url'],'compressed_sha256':expected[7:],'library_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'purpose':'temporary user-authorized app request/response observation'},indent=2))
print('Verified official ARM64 diagnostic library:',expected)
