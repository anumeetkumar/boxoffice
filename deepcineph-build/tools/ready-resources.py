import pathlib,json,xml.etree.ElementTree as E
root=pathlib.Path(__file__).resolve().parents[1];decoded=root/'ready/apktool';A='{http://schemas.android.com/apk/res/android}'
E.register_namespace('android',A[1:-1]);E.register_namespace('app','http://schemas.android.com/apk/res-auto')
rules=json.loads((root/'ready/resource-rules.json').read_text());ids=set(rules['hidden_ids']);refs=set(rules['hidden_text_refs']);changed=[]
for p in (decoded/'res').glob('layout*/*.xml'):
 try:tree=E.parse(p)
 except E.ParseError:continue
 edited=False
 for x in tree.getroot().iter():
  ident=x.get(A+'id','').split('/')[-1];text=x.get(A+'text','')
  if ident in ids or text in refs:
   for k,v in {'visibility':'gone','layout_height':'0dp','minHeight':'0dp','padding':'0dp','paddingTop':'0dp','paddingBottom':'0dp','layout_marginTop':'0dp','layout_marginBottom':'0dp'}.items():x.set(A+k,v)
   if ident in {'tv_openvip_horizontal','tvRightJoin','joinSkipAd','iv_ad_click_player','iv_ad_share_click_player'}:x.set(A+'layout_width','0dp')
   x.set(A+'clickable','false');edited=True;changed.append({'file':str(p.relative_to(decoded)),'id':ident,'text':text})
 if edited:tree.write(p,encoding='utf-8',xml_declaration=True)
removed=[];p=decoded/'AndroidManifest.xml';tree=E.parse(p);app=tree.getroot().find('application')
prefixes=('com.yk.e.provider.','com.google.android.gms.ads.','com.applovin.sdk.AppLovinInitProvider','com.vungle.ads.','com.facebook.ads.','com.ironsource.lifecycle.','sg.bigo.ads.','com.mbridge.msdk.config.component.status.','com.secmtp.sdk.core.api.ATInitializationProvider','com.smartdigimkt.sdk.api.SDMInitializationProvider','com.tramini.plugin.api.TraminiContentProvider')
for x in list(app.findall('provider')):
 name=x.get(A+'name','')
 if name.startswith(prefixes):app.remove(x);removed.append(name)
tree.write(p,encoding='utf-8',xml_declaration=True)
for p in (decoded/'res').glob('values*/strings.xml'):
 tree=E.parse(p);edited=False
 for x in tree.getroot():
  if x.get('name')=='app_name':x.text='DeepCine';edited=True
 if edited:tree.write(p,encoding='utf-8',xml_declaration=True)
(root/'reports/ready-resource-changes.json').write_text(json.dumps({'collapsed_views':changed,'removed_ad_initializers':removed,'package':'com.velvetreel.shorttv','brand':'DeepCine'},indent=2),encoding='utf-8')
print('Collapsed',len(changed),'upsell/ad views; removed',len(removed),'ad auto-initializers')
