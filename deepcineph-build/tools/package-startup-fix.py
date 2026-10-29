import pathlib,zipfile,shutil
root=pathlib.Path(__file__).resolve().parents[1];out=root/'output/DeepCine-India.apk';failed=root/'reports/failed-builds/DeepCine-India-before-startup-fix.apk';failed.parent.mkdir(exist_ok=True)
if not failed.exists():shutil.copy2(out,failed)
with zipfile.ZipFile(out) as a,zipfile.ZipFile(root/'ready/startup-fixed-unsigned.apk','w') as b:
 for e in a.infolist():
  if e.filename.startswith('META-INF/'):continue
  b.writestr(e,(root/'ready/patched/classes3.dex').read_bytes() if e.filename=='classes3.dex' else a.read(e))
(root/'ready/apktool/classes3.dex').write_bytes((root/'ready/patched/classes3.dex').read_bytes())
