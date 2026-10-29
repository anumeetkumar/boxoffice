import * as frida from '../../rea/node_modules/frida/build/src/frida.js';
import {readFile,writeFile,appendFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
const [provider,port]=process.argv.slice(2);if(!['movie','deepcine'].includes(provider)||!/^\d+$/.test(port??''))throw Error('Supply provider and local forwarded port');
const base=new URL('../../',import.meta.url),report=new URL(`api-workbench/reports/live-${provider}-hi.jsonl`,base),key=(await readFile(new URL('movie-reconstruction/tools/native-tracing/capture-redaction-key.private',base),'utf8')).trim();
const bundle=await new frida.Compiler().build(fileURLToPath(new URL(`movie-reconstruction/tools/native-tracing/api-compare-${provider}.js`,base)));
await writeFile(report,'');const manager=frida.getDeviceManager(),device=await manager.addRemoteDevice(`127.0.0.1:${port}`);let session,script,writes=Promise.resolve();const exchanges=[],results=[];let readyResolve;const ready=new Promise(r=>readyResolve=r);
function groupValues(exchange){const groups=new Map();for(const v of exchange?.response?.values??[]){if(!('value'in v))continue;const cut=v.path.lastIndexOf('.'),parent=v.path.slice(0,cut),key=v.path.slice(cut+1);if(!groups.has(parent))groups.set(parent,{});groups.get(parent)[key]=v.value;}return [...groups.entries()].map(([path,value])=>({path,...value}));}
async function call(id,op,params={},lang=''){const result=await script.exports.call(op,params,id,lang);await writes;results.push(result);const responses=exchanges.filter(x=>x.case_id===id);console.log(JSON.stringify({case:id,...result,responses:responses.map(x=>({status:x.http_status,code:x.response?.business_code,json:x.response_json,count:x.response?.result_count,host:x.host,elapsed_ms:x.elapsed_ms,titles:(x.response?.values??[]).filter(v=>v.path.endsWith('.vod_name')).slice(0,8).map(v=>v.value)}))}));return responses.at(-1);}
try{
 session=await device.attach('Gadget',{realm:frida.Realm.Native});script=await session.createScript(bundle);script.message.connect(m=>{writes=writes.then(()=>appendFile(report,JSON.stringify(m)+'\n'));if(m.type==='send'){if(m.payload?.event==='observer.ready')readyResolve();if(m.payload?.event==='api.exchange')exchanges.push(m.payload);}else console.log(JSON.stringify({event:'observer.error',description:m.description}));});await script.load();await Promise.race([ready,new Promise((_,reject)=>setTimeout(()=>reject(Error('Observer readiness timeout')),20000))]);await script.exports.configure(key);
 const targets=[];
 await call('en-filters','filters');await call('hi-filters','filters',{},'hi');await call('hi-channels','channels',{},'hi');await call('hi-hot','hot',{},'hi');await call('en-p2p-config','config',{conf_key:'p2p_config'});await call('hi-p2p-config','config',{conf_key:'p2p_config'},'hi');
 await call('en-bigg-boss-control','search',{kw:'Bigg Boss',pn:1});await call('hi-bigg-boss','search',{kw:'Bigg Boss',pn:1},'hi');await call('hi-bigg-boss-page-2','search',{kw:'Bigg Boss',pn:2},'hi');
 for(const [label,kw]of [['street-fighter','Street Fighter'],['paradise','The Paradise'],['bigg-boss-20','Bigg Boss 20'],['bigg-boss-21','Bigg Boss 21']]){
  const response=await call('hi-search-'+label,'search',{kw,pn:1},'hi');const list=groupValues(response).filter(x=>typeof x.vod_name==='string'&&Number(x.id??x.vod_id)>0);list.sort((a,b)=>Number(b.vod_year??0)-Number(a.vod_year??0));if(list[0])targets.push({label,id:Number(list[0].id??list[0].vod_id),title:list[0].vod_name});
 }
 for(const target of targets)for(const audio of [0,1,2])await call(`hi-detail-${target.label}-audio-${audio}`,'details',{vod_id:target.id,audio_type:audio},'hi');
 await call('en-bigg-boss-after-control','search',{kw:'Bigg Boss',pn:1});
 await call('search-street-fighter-repeat','search',{kw:'Street Fighter',pn:1});await writes;await writeFile(new URL(`api-workbench/reports/run-${provider}-hi.json`,base),JSON.stringify({provider,targets,results,exchanges:exchanges.length,read_only:true,original_publisher_apk_instrumented:false},null,2));
}finally{if(script)await script.unload().catch(()=>{});if(session)await session.detach().catch(()=>{});await writes;await manager.removeRemoteDevice(`127.0.0.1:${port}`);}

