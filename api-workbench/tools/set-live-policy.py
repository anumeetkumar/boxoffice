import pathlib,json
root=pathlib.Path(__file__).resolve().parents[1];p=root/'reports/api-contracts.json';r=json.loads(p.read_text())
allow={'/api/type/get_list','/api/channel/get_list','/api/channel/get_info','/api/search/hot_search','/api/search/suggest','/api/search/result','/api/search/screen','/api/search/recommend','/api/topic/list','/api/topic/vod_list','/api/public/get_sys_conf','/api/vod/info_new'}
for x in r:x['live_test_policy']='read-only candidate: verify required arguments first' if x['route'] in allow else 'static inspection only; not authorized for this catalog/playback live matrix'
p.write_text(json.dumps(r,indent=2),encoding='utf-8')
