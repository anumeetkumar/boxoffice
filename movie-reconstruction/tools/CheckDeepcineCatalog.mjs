import * as frida from '../../rea/node_modules/frida/build/src/frida.js';
import {readFile,writeFile,appendFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
const root=new URL('../../deepcineph-build/',import.meta.url),out=new URL('reports/catalog-api-capture.jsonl',root);
await writeFile(out,'');const key=(await readFile(new URL('native-tracing/capture-redaction-key.private',import.meta.url),'utf8')).trim();
const bundle=await new frida.Compiler().build(fileURLToPath(new URL('native-tracing/deepcine-catalog.js',import.meta.url)));
const manager=frida.getDeviceManager(),device=await manager.addRemoteDevice('127.0.0.1:27046');let session,script,writes=Promise.resolve(),streetId=null;
try{
 session=await device.attach('Gadget',{realm:frida.Realm.Native});script=await session.createScript(bundle);
 script.message.connect(m=>{writes=writes.then(()=>appendFile(out,JSON.stringify(m)+'\n'));if(m.type==='error'){console.log(JSON.stringify({event:'observer.error',description:m.description}));return;}const p=m.payload;if(!p)return;if(p.event==='catalog.exchange'){const titles=p.response.filter(x=>x.path.endsWith('.vod_name')).map(x=>x.value);console.log(JSON.stringify({path:p.path,form:p.request_form,titles,options:p.response.filter(x=>/audio_type_option|series_info|vod_lang/.test(x.path))}));if(p.request_form.kw==='Street Fighter'){const id=p.response.find(x=>(x.path.endsWith('.vod_id')||x.path.endsWith('.id'))&&x.value>0);if(id)streetId=Number(id.value);}}else console.log(JSON.stringify(p));});
 await script.load();await new Promise(r=>setTimeout(r,2000));await script.exports.configure(key);
 for(const [name,args]of [['filters',[]],['search',['Street Fighter',1]],['search',['Bigg Boss',1]],['search',['Bigg Boss',2]],['search',['Bigg Boss 21',1]],['search',['Bigg Boss 20',1]]]){try{console.log('RPC',name,JSON.stringify(args),JSON.stringify(await script.exports[name](...args)));}catch(e){console.log('RPC_FAILED',name,String(e.message));}}
 if(streetId)for(const audio of [0,1,2]){try{console.log('DETAILS',streetId,audio,JSON.stringify(await script.exports.details(streetId,audio)));}catch(e){console.log('DETAIL_FAILED',audio,String(e.message));}}
 await writes;
}finally{if(script)await script.unload().catch(()=>{});if(session)await session.detach().catch(()=>{});await writes;await manager.removeRemoteDevice('127.0.0.1:27046');}

