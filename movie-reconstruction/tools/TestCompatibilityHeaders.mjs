import * as frida from '../../rea/node_modules/frida/build/src/frida.js';
import {readFile,writeFile,appendFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
const key=(await readFile(new URL('native-tracing/capture-redaction-key.private',import.meta.url),'utf8')).trim();
const bundle=await new frida.Compiler().build(fileURLToPath(new URL('native-tracing/test-compatibility-headers.js',import.meta.url)));
const manager=frida.getDeviceManager(),device=await manager.addRemoteDevice('127.0.0.1:27044');
const out=new URL('../reports/phone-header-compatibility-test.jsonl',import.meta.url);await writeFile(out,'');
let session,script,writes=Promise.resolve(),waiter;
try{
 session=await device.attach('Gadget',{realm:frida.Realm.Native});script=await session.createScript(bundle);
 script.message.connect(m=>{
  writes=writes.then(()=>appendFile(out,JSON.stringify(m)+'\n'));
  if(m.type==='send'&&m.payload.event==='api.exchange'){
   const p=m.payload;
   console.log(JSON.stringify({event:p.event,profile:p.test_profile,model:p.request_headers.mobmodel,os:p.request_headers.sysrelease,status:p.status,title:p.response_summary.find(x=>x.key==='vod_name')?.value}));
   if(waiter&&p.test_profile===waiter.profile){clearTimeout(waiter.timer);waiter.resolve(p);waiter=null;}
  }else if(m.type==='send')console.log(JSON.stringify({event:m.payload.event}));
 });
 await script.load();await script.exports.configure(key);
 console.log('Waiting for normal player navigation on the phone');
 let available=false;
 for(let i=0;i<20;i++){await script.exports.setprofile('baseline');if(await script.exports.refresh()){available=true;break;}await new Promise(r=>setTimeout(r,2000));}
 if(!available)throw Error('No resumed player');
 await new Promise(r=>setTimeout(r,2500));
 for(const profile of ['baseline','model-only','os-only','model-and-os','baseline']){
  await script.exports.setprofile(profile);
  const response=new Promise((resolve,reject)=>{const timer=setTimeout(()=>{waiter=null;reject(Error('No response for '+profile));},15000);waiter={profile,resolve,timer};});
  if(!await script.exports.refresh())throw Error('Player no longer resumed');
  await response;await new Promise(r=>setTimeout(r,1000));
 }
}finally{
 if(waiter)clearTimeout(waiter.timer);
 if(script){await script.exports.setprofile('baseline').catch(()=>{});await script.unload().catch(()=>{});}
 if(session)await session.detach().catch(()=>{});await writes;await manager.removeRemoteDevice('127.0.0.1:27044');
}
