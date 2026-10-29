import pathlib,zipfile,hashlib
root=pathlib.Path(__file__).resolve().parents[1]
with zipfile.ZipFile(root/'ready/prelocalize.apk') as z:
 for e in z.infolist():
  if e.filename.endswith('.dex') and '/'not in e.filename:
   p=root/'ready/localized'/e.filename;data=p.read_bytes() if p.exists() else z.read(e)
   (root/'ready/apktool'/e.filename).write_bytes(data)
assert not list((root/'ready/apktool/lib').rglob('*observer*'))
print('Staged final DEX payloads without any diagnostic library')
