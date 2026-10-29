import pathlib,zipfile,sys
root=pathlib.Path(__file__).resolve().parent.parent
work=root/'boxoffice/phone-capture'
replacements={'classes5.dex':work/'classes5.dex','lib/arm64-v8a/libboxoffice_observer.so':root/'tools/native-tracing/frida-gadget-arm64.so','lib/arm64-v8a/libboxoffice_observer.config.so':work/'libboxoffice_observer.config.so'}
base=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else root/'boxoffice/build/BoxOffice.apk'
with zipfile.ZipFile(base) as before,zipfile.ZipFile(work/'unsigned.apk','w') as after:
    for e in before.infolist():
        if e.filename.startswith('META-INF/'):continue
        if e.filename in replacements:continue
        after.writestr(e,before.read(e))
    for name,file in replacements.items():after.writestr(name,file.read_bytes(),compress_type=zipfile.ZIP_STORED if name.startswith('lib/') else zipfile.ZIP_DEFLATED)
print('Packaged diagnostic APK; original request algorithms and signing configuration preserved')
