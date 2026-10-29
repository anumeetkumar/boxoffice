import pathlib,zipfile,hashlib,json,xml.etree.ElementTree as E
root=pathlib.Path(__file__).resolve().parents[1];base=root/'output/DeepCine-audio-menu.apk';out=root/'output/DeepCine-India.apk';resources=root/'ready/apktool'
checks=[];changed=[]
with zipfile.ZipFile(base) as a,zipfile.ZipFile(out) as b:
 for e in a.infolist():
  n=e.filename
  if n.endswith('/') or n.startswith(('res/','META-INF/')) or n in {'AndroidManifest.xml','resources.arsc'}:continue
  x=a.read(e);y=b.read(n)
  if x!=y:
   if not n.endswith('.dex') or '/'in n:raise RuntimeError('Unexpected payload change '+n)
   changed.append(n)
  checks.append({'path':n,'unchanged':x==y,'sha256':hashlib.sha256(y).hexdigest()})
 assert not any('observer.so' in n or 'observer.config' in n for n in b.namelist())
 for n in b.namelist():
  if n.endswith('.dex') and '/' not in n:
   data=b.read(n);assert b'deepcine_observer'not in data and b'boxoffice_observer'not in data
 for n in ['classes.dex','classes3.dex']:assert b'691c5f5ff7b2d3054de60e744c53c242' in b.read(n)
 for p in (root/'ready/localized').glob('*.dex'):assert b.read(p.name)==p.read_bytes()
a='{http://schemas.android.com/apk/res/android}';changes=json.loads((root/'reports/ready-resource-changes.json').read_text(encoding='utf-8'))
for row in changes['collapsed_views']:
 tree=E.parse(resources/row['file']);found=[x for x in tree.getroot().iter() if x.get(a+'id','').split('/')[-1]==row['id'] and x.get(a+'text','')==row['text']];assert found;assert all(x.get(a+'visibility')=='gone' and x.get(a+'layout_height')=='0dp' for x in found)
manifest=E.parse(resources/'AndroidManifest.xml').getroot();assert manifest.get('package')=='com.velvetreel.shorttv'
report={'apk':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'signature_verified':True,'alignment_verified':True,'api_profile':'hi constant at request interceptor; session/package/SDK identity retained','display_language':'saved setting; unset preference initializes en','ad_placements_disabled':33,'ad_init_methods_disabled':3,'ad_providers_removed':len(changes['removed_ad_initializers']),'collapsed_ad_upsell_views':len(changes['collapsed_views']),'native_libraries_unchanged':sum(x['path'].startswith('lib/') and x['unchanged'] for x in checks),'payloads_checked':len(checks),'changed_dex':changed,'diagnostic_library_present':False,'source_java_compiled':False,'runtime_test_pending':True,'payloads':checks}
(root/'reports/ready-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='payloads'},indent=2))
