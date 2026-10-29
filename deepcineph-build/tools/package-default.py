import pathlib,zipfile
root=pathlib.Path(__file__).resolve().parents[1]
with zipfile.ZipFile(root/'output/DeepCine-audio-menu.apk') as before,zipfile.ZipFile(root/'ready/base-with-default.apk','w') as after:
 for e in before.infolist():
  if e.filename.startswith('META-INF/'):continue
  after.writestr(e,(root/'ready/default-classes3.dex').read_bytes() if e.filename=='classes3.dex' else before.read(e))
