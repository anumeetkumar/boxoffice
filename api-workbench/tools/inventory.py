import pathlib,json,re,hashlib,collections
root=pathlib.Path(__file__).resolve().parents[1];base=root.parent
providers={'movie':base/'rea/_reference/movie-review','deepcine':base/'deepcineph-reconstruction'}
records=[]
for provider,source in providers.items():
 routes=json.loads((source/'api-routes.json').read_text(encoding='utf-8-sig'))
 for item in routes:
  p=source/item['path'];lines=p.read_text(encoding='utf-8').splitlines();line=item['line']-1
  declaration=' '.join(lines[line+1:line+5]).strip().split(';')[0]+';'
  # Bound at the next method declaration; route annotations are followed by the interface method.
  for row in lines[line+1:line+9]:
   if ';' in row:declaration=row.strip();break
  prefix='\n'.join(lines[max(0,line-3):line+1])
  method=re.search(r'([\w$]+)\s*\(',declaration)
  route=item['route']; mutation=bool(re.search(r'(?:register|login|logout|remove|delete|upload|feedback|report|payment|pay|create|update|setName|collect|favorite|share|log/|/log|bind|sign_in|check_in|invite|down$|discuss/send|barrage/send)',route,re.I))
  sensitive=bool(re.search(r'/user|/order|/payment|/invited',route,re.I))
  family='catalog'
  if re.search(r'vod/info',route):family='playback-detail'
  elif re.search(r'public|sys_conf',route):family='configuration'
  elif re.search(r'search|screen|rank|topic|channel|type/',route):family='discovery'
  elif re.search(r'ad/|/ad|barrage|discuss',route):family='ads-or-comments'
  elif sensitive:family='account-or-commerce'
  records.append({'provider':provider,'verb':item['verb'],'route':route,'interface_method':method.group(1) if method else None,'declaration':declaration,'encoding':'multipart' if '@Multipart' in prefix else 'form' if '@FormUrlEncoded' in prefix else 'json-or-raw-body' if '@Body' in declaration else 'no-declared-body','family':family,'live_test_policy':'inspect-only: side effects or private account state' if mutation or sensitive else 'read-only candidate: verify required arguments first','source':str(p),'line':item['line'],'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
by=collections.defaultdict(dict)
for x in records:by[(x['verb'],x['route'])].setdefault(x['provider'],[]).append(x)
matrix=[]
for (verb,route),members in sorted(by.items()):matrix.append({'verb':verb,'route':route,'providers':sorted(members),'shared':len(members)==2,'movie_methods':[x['interface_method'] for x in members.get('movie',[])],'deepcine_methods':[x['interface_method'] for x in members.get('deepcine',[])]})
(root/'reports/api-contracts.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
(root/'reports/route-matrix.json').write_text(json.dumps(matrix,indent=2),encoding='utf-8')
text='# API route and request comparison\n\nStatic declarations from both APKs. A shared path does not establish shared IDs, media inventory, credentials, authorization or response semantics. Required fields hidden behind FieldMap/Body remain subject to call-site or runtime evidence.\n\n| Verb | Route | Providers | Movie method | DeepCine method |\n| --- | --- | --- | --- | --- |\n'
for x in matrix:text+=f"| {x['verb']} | `{x['route']}` | {', '.join(x['providers'])} | {', '.join(x['movie_methods'])} | {', '.join(x['deepcine_methods'])} |\n"
(root/'reports/route-matrix.md').write_text(text,encoding='utf-8')
print(json.dumps({'declarations':dict(collections.Counter(x['provider'] for x in records)),'unique_routes':len(matrix),'shared_routes':sum(x['shared'] for x in matrix),'source_files':{p:sorted(set(x['source'] for x in records if x['provider']==p)) for p in providers}},indent=2))
