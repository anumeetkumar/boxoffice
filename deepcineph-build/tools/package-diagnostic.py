import pathlib,zipfile
root=pathlib.Path(__file__).resolve().parents[1];base=root.parent
replacements={'classes3.dex':root/'diagnostic/classes3.dex','lib/arm64-v8a/libdeepcine_observer.so':base/'movie-reconstruction/tools/native-tracing/frida-gadget-arm64.so','lib/arm64-v8a/libdeepcine_observer.config.so':root/'diagnostic/libdeepcine_observer.config.so'}
with zipfile.ZipFile(root/'output/DeepCine-audio-menu.apk') as a,zipfile.ZipFile(root/'diagnostic/unsigned.apk','w') as b:
    for e in a.infolist():
        if e.filename.startswith('META-INF/') or e.filename in replacements:continue
        b.writestr(e,a.read(e))
    for name,p in replacements.items():b.writestr(name,p.read_bytes(),compress_type=zipfile.ZIP_STORED if name.startswith('lib/') else zipfile.ZIP_DEFLATED)
