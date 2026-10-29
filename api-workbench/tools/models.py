import pathlib,json,re,hashlib
root=pathlib.Path(__file__).resolve().parents[1];base=root.parent
roots={'movie':base/'rea/_reference/movie-review/jadx-export/sources/com/mgs/carparking/netbean','deepcine':base/'deepcineph-reconstruction/jadx-export/sources/com/mgs/carparking/netbean'}
models={}
for provider,folder in roots.items():
 out={}
 for p in folder.glob('*.java'):
  text=p.read_text(encoding='utf-8');fields=[]
  for m in re.finditer(r'\bprivate\s+(?:final\s+)?([\w.$<>?, \[\]]+)\s+(\w+)\s*(?:=|;)',text):
   prefix=text[max(0,m.start()-550):m.start()].split(';')[-1];a=re.search(r'@SerializedName\("([^"\n]+)"\)',prefix);alias=re.search(r'renamed from: (\w+),',prefix)
   key=a[1] if a else alias[1] if alias else m[2]
   fields.append({'wire_key_candidate':key,'java_type':m[1].strip(),'field':m[2],'provenance':'literal SerializedName' if a else 'JADX original field alias; serialization unverified' if alias else 'declared field; default Gson serialization inferred'})
  if fields:out[p.stem]={'source':str(p),'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'fields':fields}
 models[provider]=out
common=sorted(set(models['movie'])&set(models['deepcine']));comparison=[]
for name in common:
 a={x['wire_key_candidate'] for x in models['movie'][name]['fields']};b={x['wire_key_candidate'] for x in models['deepcine'][name]['fields']}
 comparison.append({'model':name,'shared_key_candidates':sorted(a&b),'movie_only_key_candidates':sorted(a-b),'deepcine_only_key_candidates':sorted(b-a)})
(root/'reports/response-models.json').write_text(json.dumps(models,indent=2),encoding='utf-8');(root/'reports/response-model-comparison.json').write_text(json.dumps(comparison,indent=2),encoding='utf-8')
print(json.dumps({'models_with_declared_fields':{p:len(v) for p,v in models.items()},'common_models_compared':len(common),'limitations':'Literal annotations distinguished from inferred default field serialization; constants and custom Gson adapters may differ.'}))
