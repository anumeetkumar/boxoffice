import * as frida from '../../rea/node_modules/frida/build/src/frida.js';
import {readFile,writeFile,appendFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
const key=(await readFile(new URL('native-tracing/capture-redaction-key.private',import.meta.url),'utf8')).trim();
const bundle=await new frida.Compiler().build(fileURLToPath(new URL('native-tracing/test-common-route.js',import.meta.url)));
const manager=frida.getDeviceManager(),targets=[];
let writes=Promise.resolve();
try{
 for(const [phone,port] of [['s21',27044],['m53',27045]]){
  const device=await manager.addRemoteDevice(`127.0.0.1:${port}`),session=await device.attach('Gadget',{realm:frida.Realm.Native}),script=await session.createScript(bundle);
  const output=new URL(`../reports/common-route-${phone}.jsonl`,import.meta.url);await writeFile(output,'');
  const target={phone,address:`127.0.0.1:${port}`,device,session,script,output,pending:null};targets.push(target);
  script.message.connect(m=>{
   writes=writes.then(()=>appendFile(output,JSON.stringify(m)+'\n'));
   if(m.type==='send'&&m.payload.event==='api.exchange'&&m.payload.path==='/api/vod/info_new'){
    const p=m.payload;console.log(JSON.stringify({phone,route:p.route_test,status:p.status,title:p.response_summary.find(v=>v.key==='vod_name')?.value}));
    if(target.pending&&p.route_test===target.pending.route){clearTimeout(target.pending.timer);target.pending.resolve(p);target.pending=null;}
   }
  });
  await script.load();await script.exports.configure(key);await script.exports.setroute('direct');await script.exports.openplayer();
 }
 await new Promise(r=>setTimeout(r,4000));
 for(const route of ['direct','pc-tunnel','direct']){
  for(const target of targets){
   await target.script.exports.setroute(route);
   const response=new Promise((resolve,reject)=>{target.pending={route,resolve,timer:setTimeout(()=>{target.pending=null;reject(Error('No response: '+target.phone+' '+route));},18000)};});
   if(!await target.script.exports.refreshplayer())throw Error('Player not resumed: '+target.phone);
   await response;await new Promise(r=>setTimeout(r,1000));
  }
 }
}finally{
 for(const t of targets){if(t.pending)clearTimeout(t.pending.timer);await t.script.exports.setroute('direct').catch(()=>{});await t.script.unload().catch(()=>{});await t.session.detach().catch(()=>{});await manager.removeRemoteDevice(t.address).catch(()=>{});}
 await writes;
}
