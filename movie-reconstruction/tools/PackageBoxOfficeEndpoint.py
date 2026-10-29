import pathlib,zipfile,hashlib,json,re,sys
root=pathlib.Path(__file__).resolve().parent.parent;base=root/'boxoffice/build/BoxOffice.apk';work=root/'boxoffice/endpoint-variant'
diagnostic='--diagnostic' in sys.argv
assert hashlib.sha256(base.read_bytes()).hexdigest()=='262cafd73263e8d03a306763a020824f6f597a2bec58df1bd0c657970d2b7a14'
with zipfile.ZipFile(base) as a,zipfile.ZipFile(work/('diagnostic-unsigned.apk' if diagnostic else 'unsigned.apk'),'w') as b:
 for e in a.infolist():
  if re.fullmatch(r'META-INF/(?:MANIFEST\.MF|[^/]+\.(?:SF|RSA|DSA|EC))',e.filename,re.I):continue
  p=work/('diagnostic-patched' if diagnostic else 'patched')/e.filename
  b.writestr(e,p.read_bytes() if e.filename.endswith('.dex') and p.is_file() else a.read(e))
(work/'build-intent.json').write_text(json.dumps({'base_apk_sha256':hashlib.sha256(base.read_bytes()).hexdigest(),'base_url':'https://deepcineph.7nkznc.com/','app_language':'hi','package':'com.fvvcl.flickverse','app_id':'moviein','native_channel':'63','session_note':'New endpoint uses a separate token preference key; old Movie token is retained only for rollback and not sent to the new service.','unchanged':'UI, branding, existing ads removal, player controls, native libraries, native signing configuration','compatibility_verified':False},indent=2),encoding='utf-8')
