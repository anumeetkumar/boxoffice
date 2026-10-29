import * as frida from '../../rea/node_modules/frida/build/src/frida.js';
import {readFile,writeFile,appendFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
const key=(await readFile(new URL('native-tracing/capture-redaction-key.private',import.meta.url),'utf8')).trim();
const bundle=await new frida.Compiler().build(fileURLToPath(new URL('native-tracing/test-sdk-refresh.js',import.meta.url)));
const manager=frida.getDeviceManager(),device=await manager.addRemoteDevice('127.0.0.1:27044');
const output=new URL('../reports/phone-sdk-refresh-test.jsonl',import.meta.url);await writeFile(output,'');
let session,script,writes=Promise.resolve(),loadedWaiter,timer;
const record=m=>{writes=writes.then(()=>appendFile(output,JSON.stringify(m)+'\n'));};
try{
 session=await device.attach('Gadget',{realm:frida.Realm.Native});script=await session.createScript(bundle);
 script.message.connect(m=>{
  record(m);
  if(m.type==='send'){
   const p=m.payload;if(p.event==='api.exchange')console.log(JSON.stringify({event:p.event,path:p.path,conf:p.request_form.conf_key,status:p.status,title:p.response_summary.find(x=>x.key==='vod_name')?.value}));
   else console.log(JSON.stringify(p));
   if(p.event==='native.sdk.loaded'&&loadedWaiter){clearTimeout(timer);loadedWaiter(p);loadedWaiter=null;}
  }
 });
 await script.load();await script.exports.configure(key);
 await script.exports.openplayer();
 console.log('Waiting for normal player navigation');let player=false;
 for(let i=0;i<40;i++){if(await script.exports.refreshplayer()){player=true;break;}await new Promise(r=>setTimeout(r,2000));}
 if(!player)throw Error('Player not open');await new Promise(r=>setTimeout(r,2500));
 const before=await script.exports.sdkstate();record({event:'sdk.state.before',...before});console.log('Original SDK state recorded with configuration redacted');
 const loaded=new Promise((resolve,reject)=>{loadedWaiter=resolve;timer=setTimeout(()=>reject(Error('Configuration refresh did not reload SDK')),20000);});
 await script.exports.refreshconfiguration();await loaded;
 const after=await script.exports.sdkstate();record({event:'sdk.state.after',...after});
 await script.exports.refreshplayer();await new Promise(r=>setTimeout(r,3000));await script.exports.refreshplayer();await new Promise(r=>setTimeout(r,3000));
}finally{clearTimeout(timer);if(script)await script.unload().catch(()=>{});if(session)await session.detach().catch(()=>{});await writes;await manager.removeRemoteDevice('127.0.0.1:27044');}
