import hashlib, json, pathlib, urllib.request, zipfile, lzma, time

root = pathlib.Path(__file__).resolve().parent.parent
work = root / 'tools' / 'native-tracing'
work.mkdir(exist_ok=True)

def download(url, dest, algorithm, expected):
    if dest.exists() and hashlib.file_digest(dest.open('rb'), algorithm).hexdigest() == expected:
        print('Already verified:', dest.name, flush=True)
        return
    partial = dest.with_suffix(dest.suffix + '.partial')
    digest = hashlib.new(algorithm)
    total = 0
    last = time.monotonic()
    with urllib.request.urlopen(url, timeout=90) as response, partial.open('wb') as output:
        while chunk := response.read(4 * 1024 * 1024):
            output.write(chunk)
            digest.update(chunk)
            total += len(chunk)
            if time.monotonic() - last > 20:
                print(dest.name, total // 1048576, 'MiB', flush=True)
                last = time.monotonic()
    if digest.hexdigest() != expected:
        raise RuntimeError('Download checksum mismatch: ' + dest.name)
    partial.replace(dest)
    print('Verified:', dest.name, flush=True)

image = work / 'x86_64-35_r09.zip'
download('https://dl.google.com/android/repository/sys-img/google_apis/x86_64-35_r09.zip', image, 'sha1', '0103e6dab21290c4b9d16550a3ce99476f884eef')
target = work / 'image'
if not (target / 'x86_64' / 'system.img').exists():
    target.mkdir(exist_ok=True)
    with zipfile.ZipFile(image) as archive:
        for entry in archive.infolist():
            path = (target / entry.filename).resolve()
            if not path.is_relative_to(target.resolve()):
                raise RuntimeError('Unsafe archive path')
        archive.extractall(target)
    print('Debug system image extracted', flush=True)
release_url = 'https://api.github.com/repos/frida/frida/releases/tags/17.23.2'
request = urllib.request.Request(release_url, headers={'User-Agent': 'MovieRecovery-local-diagnostics'})
with urllib.request.urlopen(request, timeout=60) as response:
    release = json.load(response)
asset = next(a for a in release['assets'] if a['name'] == 'frida-server-17.23.2-android-x86_64.xz')
digest = asset['digest']
if not digest or not digest.startswith('sha256:'):
    raise RuntimeError('No upstream SHA256 available')
compressed = work / asset['name']
download(asset['browser_download_url'], compressed, 'sha256', digest.split(':', 1)[1])
with lzma.open(compressed) as source, (work / 'frida-server').open('wb') as output:
    while chunk := source.read(4 * 1024 * 1024):
        output.write(chunk)
(work / 'provenance.json').write_text(json.dumps({'image_url': 'https://dl.google.com/android/repository/sys-img/google_apis/x86_64-35_r09.zip', 'image_sha1': '0103e6dab21290c4b9d16550a3ce99476f884eef', 'frida_asset': asset['browser_download_url'], 'frida_sha256': digest, 'phone_modified': False}, indent=2))
print('Native tracing dependencies ready', flush=True)
