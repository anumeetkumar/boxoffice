import pathlib,json,re,statistics,collections
root=pathlib.Path(__file__).resolve().parents[1]
def read(name):return json.loads((root/'reports'/name).read_text(encoding='utf-8-sig'))
def save(name,value):(root/'reports'/name).write_text(json.dumps(value,indent=2,ensure_ascii=False),encoding='utf-8')
def live(provider):
 return [p for line in (root/'reports'/f'live-{provider}.jsonl').read_text(encoding='utf-8-sig').splitlines() if (p:=json.loads(line).get('payload',{})).get('event')=='api.exchange']
def groups(row):
 out={}
 for x in (row.get('response') or {}).get('values',[]):
  if 'value' in x:
   parent,_,key=x['path'].rpartition('.');out.setdefault(parent,{})[key]=x['value']
 return out
rows={p:live(p) for p in ['movie','deepcine']};bycase={p:{r['case_id']:r for r in v if r.get('case_id')} for p,v in rows.items()}
def status(r):
 if r['http_status']!=200:return 'http_error'
 if not r['response_json']:return 'non_json_response'
 if r['response']['business_code']!=10000:return 'business_error'
 d=groups(r).get('$.result',{})
 if r['path']=='/api/vod/info_new' and d.get('vod_name')=='-' and d.get('id',d.get('vod_id'))==0:return 'replacement_detail'
 return 'normal_detail_metadata' if r['path']=='/api/vod/info_new' else 'normal_api_response'
summary={}
for p,records in rows.items():
 run=read(f'run-{p}.json');summary[p]={'cases_attempted':len(run['results']),'calls_completed':sum(x['completed'] for x in run['results']),'captured_exchanges':len(records),'distinct_routes_tested':len({r['path'] for r in records}),'host':sorted({r['host'] for r in records}),'outcomes':dict(collections.Counter(status(r) for r in records)),'http_interceptor_median_ms':statistics.median(r['elapsed_ms'] for r in records),'sample_note':'One bounded sequential run on S21; no media download, streaming benchmark or representative latency claim.'}
 assert len(run['results'])==27 and len(records)==27,'Unexpected live coverage'
 assert all(x['completed'] for x in run['results']),'A client call did not complete'
 assert len(bycase[p])==27,'Missing or duplicate case attribution'
comparison=[]
for case in bycase['movie'].keys()&bycase['deepcine'].keys():
 a=bycase['movie'][case];b=bycase['deepcine'][case];sa=(a.get('response') or {}).get('schema',{});sb=(b.get('response') or {}).get('schema',{})
 comparison.append({'case':case,'route':a['path'],'same_form_field_names':set(a['request_form'])==set(b['request_form']),'movie':{'http_status':a['http_status'],'business_code':a['response']['business_code'],'result_count':a['response']['result_count'],'classification':status(a)},'deepcine':{'http_status':b['http_status'],'business_code':b['response']['business_code'],'result_count':b['response']['result_count'],'classification':status(b)},'shared_schema_paths':sorted(set(sa)&set(sb)),'movie_only_schema_paths':sorted(set(sa)-set(sb)),'deepcine_only_schema_paths':sorted(set(sb)-set(sa)),'type_mismatches':[{ 'path':k,'movie':sa[k],'deepcine':sb[k]} for k in sa.keys()&sb.keys() if sa[k]!=sb[k]]})
comparison.sort(key=lambda x:x['case']);save('case-comparison.json',comparison)
items={}
for p,records in rows.items():
 dedup={}
 for r in records:
  if r['path']!='/api/search/result':continue
  for path,item in groups(r).items():
   if not re.fullmatch(r'\$\.result\.\d+',path) or not item.get('vod_name') or not item.get('id'):continue
   vid=int(item['id']);dedup[vid]={'provider':p,'provider_id':vid,'request_profile':{'app_language':r['request_headers'].get('app_language')},'title':item['vod_name'],'year':str(item.get('vod_year','')),'kind':item.get('type_pid'),'catalog_audio_label':item.get('audio_language_tag'),'evidence_case':r['case_id']}
 items[p]=list(dedup.values())
def match_key(item):return (re.sub(r'\s+',' ',item['title'].casefold()).strip(),item['year'],item['kind'])
index=collections.defaultdict(list)
for x in items['deepcine']:index[match_key(x)].append(x)
candidates=[]
for m in items['movie']:
 ds=index.get(match_key(m),[])
 if ds:candidates.append({'title':m['title'],'year':m['year'],'movie':m,'deepcine_candidates':ds,'confidence':'title/year/kind candidate only; confirm actual content before automatic fallback','ids_interchangeable':False,'audio_availability_interchangeable':False})
save('catalog-items.json',items);save('candidate-mappings.json',candidates)
# Validate the semantic boundary on real captured failure/success records.
assert all(status(r)=='replacement_detail' for r in rows['movie'] if r['path']=='/api/vod/info_new')
assert all(status(r)=='normal_detail_metadata' for r in rows['deepcine'] if r['path']=='/api/vod/info_new')
lang={}
for p in rows:
 a=bycase[p]['search-bigg-boss'];b=bycase[p]['search-bigg-boss-hindi-interface'];assert b['request_headers']['app_language']=='hi','Language profile was not applied'
 key=lambda r:sorted((x['value'] for x in r['response']['values'] if x['path'].endswith('.vod_name')))
 lang[p]={'wire_language_header':'hi','same_returned_title_set':key(a)==key(b),'request_identity_changed':False}
save('language-profile-comparison.json',lang)
contracts=read('api-contracts.json');matrix=read('route-matrix.json')
coverage=[]
for route in matrix:
 entry=dict(route);entry['live_cases']={p:sum(r['path']==route['route'] for r in rows[p]) for p in route['providers']};entry['coverage']='live read-only cases' if any(entry['live_cases'].values()) else 'static contract only';coverage.append(entry)
save('route-coverage.json',coverage)
report={'declared_requests':len(contracts),'unique_routes':len(matrix),'shared_routes':sum(x['shared'] for x in matrix),'providers':summary,'live_tested_distinct_routes':len(set(r['path'] for v in rows.values() for r in v)),'candidate_title_matches':len(candidates),'language_profiles':lang,'restoration':read('phone-restoration.json'),'conclusion':'A provider-neutral catalog client is feasible. Hindi app_language changes DeepCine catalog selection; validate its matching detail responses before declaring fallback playable. Keep provider/profile-specific IDs, sessions and native proof.'}
save('comparison-summary.json',report)
text=f'''# API comparison results

The workbench inventories {len(contracts)} declared requests across {len(matrix)} distinct routes; {sum(x['shared'] for x in matrix)} routes occur in both APKs. It inspected request encodings, interface methods, response model fields, and ran 27 controlled read-only cases per provider on the same S21. The live Movie transport is the Movie-derived BoxOffice build with its genuine local signing/session identity, not instrumentation of the untouched publisher-signed Movie.apk.

## Executed requests

The live matrix covered filters, home channels, hot search, search suggestions, search/pagination, interface-language variation, movie/TV listing, recommendations, topics, one provider-owned channel and native-verified detail requests with audio_type 0/1/2. It captured {report['live_tested_distinct_routes']} distinct endpoint paths per provider. Account changes, payments, uploads, deletion and unknown operations were not executed. Topic-content lookup was skipped because this topic response did not yield a usable topic ID. Static-only routes remain explicitly unverified in route-coverage.json.

| Provider | HTTP/API exchanges | Normal API responses | Normal detail metadata | Replacement details | Median API time |
| --- | --- | --- | --- | --- | --- |
'''
for p in rows:
 s=summary[p];o=s['outcomes'];text+=f"| {p} | {s['captured_exchanges']} | {o.get('normal_api_response',0)} | {o.get('normal_detail_metadata',0)} | {o.get('replacement_detail',0)} | {s['http_interceptor_median_ms']} ms |\n"
text+='''
API times are from one bounded run, not a streaming benchmark. HTTP 200 and business code 10000 alone do not establish usable playback: Movie returned a replacement object with title `-` and ID 0 for all nine tested detail calls. DeepCine returned normal metadata for the three titles it supplied. Media URLs were not fetched in this phase.

## Findings that change the design

- The search/detail contracts are similar enough to share catalog UI and normalization code. Provider IDs and authentication/proof remain separate.
- Movie search returned Bigg Boss Season 20 and a much broader Indian series catalog. Its tested Season 21 query returned no matching entry. DeepCine returned OTT Season 3 and Marathi Season 5. The workbench reports what the services returned, not a claim about the actual current broadcast season.
- Movie's Paradise catalog entry was labelled Multilingual; DeepCine's detail response advertised Original/English for the tested source. Movie's Street Fighter catalog entry itself was labelled English. A blanket Hindi label would be inaccurate.
- Hindi interface-language requests were verified on the wire. Movie kept the same title set, while DeepCine changed from two Bigg Boss entries to the broader Indian catalog. This corrects the earlier preliminary summary; matching Hindi-profile detail requests require follow-up validation.
- Both filter responses advertised genre, year and sort. No verified provider/region switch was discovered. Earlier area/audio_lang probes are retained under deepcineph-build/reports/live-catalog-findings.md.
- Playback timestamps/proofs were freshly generated by each app's own native SDK for an ID discovered in that same provider's catalog. Sessions, IDs and signatures were never transplanted between services. Apps were run one at a time to avoid a collision between their local native HTTP services.

## Feasible shared-client approach

Represent a selected item using a canonical title plus separate provider references. Resolve details through the provider that owns each reference; validate the detail body rather than trusting HTTP success. If the preferred provider returns a replacement/error, search the other service for the same work, validate title/year/type and content identity, then resolve using that service's own ID and session. Show the languages supplied by the selected playback source.

'''
text+=f"The bounded search sample produced {len(candidates)} title/year/type matching candidates in candidate-mappings.json. These are candidates, not proof of identical editions, audio tracks or stream availability. For example:\n\n"
for x in candidates:
 if x['title'] in ['The Paradise','Street Fighter']:
  text+=f"- {x['title']} ({x['year']}): Movie ID {x['movie']['provider_id']}; DeepCine ID(s) {', '.join(str(y['provider_id']) for y in x['deepcine_candidates'])}.\n"
text+='''
This fallback can help titles genuinely available on both services. It cannot make a Movie-only season or unavailable Hindi dub appear in DeepCine. Matching Movie's full inventory still depends on resolving Movie's detail-response failure or another usable source supplying that content. No compatibility claim is made for sending one provider's credentials or IDs to another.

## Deliverables and limits

- api-contracts.json and route-matrix.md: every extracted route declaration, method, encoding and source location.
- response-models.json and response-model-comparison.json: 77 same-named model comparisons; literal serialization annotations are distinguished from inferred default field names. Runtime schemas remain stronger evidence.
- live-movie.jsonl / live-deepcine.jsonl: in-process-redacted request headers, request fields, JSON field/type shapes, selected catalog values and HTTP/business status.
- run-movie.json / run-deepcine.json: case execution and per-request timings.
- case-comparison.json: matching case comparisons and response-shape differences.
- candidate-mappings.json: namespace-preserving content-match candidates.
- route-coverage.json: live versus static-only status for every route.
- phone-restoration.json: both exact original installed APK hashes restored; temporary USB observer routes removed. No app data was cleared.

The workbench currently uses each app's native Android client as its signed transport. It is not a claim that standalone curl/Node can recreate all native proofs, or that recovered Java compiles. No application feature changes were made in this API phase.
'''
(root/'reports/comparison.md').write_text(text,encoding='utf-8')
print(json.dumps({'declared_requests':report['declared_requests'],'unique_routes':report['unique_routes'],'shared_routes':report['shared_routes'],'live_paths':report['live_tested_distinct_routes'],'candidate_matches':len(candidates),'providers':summary},indent=2))

