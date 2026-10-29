import pathlib,json,zipfile
root=pathlib.Path(__file__).resolve().parents[1];base=root.parent
pairs={}
def row(name,case):
 for line in (base/'api-workbench/reports'/name).read_text(encoding='utf-8-sig').splitlines():
  p=json.loads(line).get('payload',{})
  if p.get('case_id')==case:return {x['path']:x['value'] for x in p['response']['values'] if 'value'in x}
 return{}
en=row('live-deepcine.jsonl','filters');hi=row('live-deepcine-hi-discovery.jsonl','hi-filters-confirm')
for p,v in hi.items():
 if p in en and isinstance(v,str) and isinstance(en[p],str) and v!=en[p]:pairs[v]=en[p]
pairs.update({'अनुशंसा करना':'Recommend','चलचित्र':'Movies','टीवी श्रृंखला':'TV Shows','टीवी शृंखला':'TV Shows','एनीमे':'Anime','एनिमे':'Anime','मूल ध्वनि':'Original'})
def quote(x):return json.dumps(x,ensure_ascii=False)
s='''.class public final Lcom/mgs/carparking/util/IndiaDisplayLabels;
.super Ljava/lang/Object;
.method public static map(Ljava/lang/String;)Ljava/lang/String;
    .locals 3
    if-eqz p0, :original
    invoke-static {}, Lcom/mgs/carparking/util/UserUtils;->n()Ljava/lang/String;
    move-result-object v0
    const-string v1, "en"
    invoke-virtual {v0, v1}, Ljava/lang/String;->startsWith(Ljava/lang/String;)Z
    move-result v0
    if-eqz v0, :original
'''
for i,(h,e) in enumerate(sorted(pairs.items())):
 s+=f'''    const-string v1, {quote(h)}
    invoke-virtual {{p0, v1}}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v2
    if-eqz v2, :label_{i}
    const-string p0, {quote(e)}
    return-object p0
    :label_{i}
'''
s+='''    :original
    return-object p0
.end method
.method public static mapText(Ljava/lang/CharSequence;)Ljava/lang/CharSequence;
    .locals 1
    if-eqz p0, :original_text
    invoke-interface {p0}, Ljava/lang/CharSequence;->toString()Ljava/lang/String;
    move-result-object v0
    invoke-static {v0}, Lcom/mgs/carparking/util/IndiaDisplayLabels;->map(Ljava/lang/String;)Ljava/lang/String;
    move-result-object v0
    return-object v0
    :original_text
    return-object p0
.end method
'''
(root/'ready/IndiaDisplayLabels.smali').write_text(s,encoding='utf-8');(root/'reports/english-label-mapping.json').write_text(json.dumps(pairs,indent=2,ensure_ascii=False),encoding='utf-8')
with zipfile.ZipFile(root/'ready/base-with-default.apk') as a,zipfile.ZipFile(root/'ready/prelocalize.apk','w') as b:
 for e in a.infolist():
  p=root/'ready/patched'/e.filename
  b.writestr(e,p.read_bytes() if e.filename.endswith('.dex') and p.is_file() else a.read(e))
print('Prepared',len(pairs),'display-only translations; original request filter values remain unchanged')
