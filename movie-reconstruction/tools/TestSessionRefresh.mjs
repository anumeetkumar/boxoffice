import * as frida from '../../rea/node_modules/frida/build/src/frida.js';
import {readFile,writeFile,appendFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
const key=(await readFile(new URL('native-tracing/capture-redaction-key.private',import.meta.url),'utf8')).trim();
const bundle=await new frida.Compiler().build(fileURLToPath(new URL('native-tracing/test-session-refresh.js',import.meta.url)));
const manager=frida.getDeviceManager(),targets=[];let writes=Promise.resolve();
const record=(target,message)=>{writes=writes.then(()=>appendFile(target.output,JSON.stringify(message)+'\n'));};
async function request(target,path,action){
 const response=new Promise((resolve,reject)=>{target.pending={path,resolve,timer:setTimeout(()=>{target.pending=null;reject(Error('No '+path+' response from '+target.phone));},20000)};});
 await action();return await response;
}
try{
 for(const[phone,port]of[['s21',27044],['m53',27045]]){
  const address=`127.0.0.1:${port}`,device=await manager.addRemoteDevice(address),session=await device.attach('Gadget',{realm:frida.Realm.Native}),script=await session.createScript(bundle);
  const output=new URL(`../reports/session-refresh-${phone}.jsonl`,import.meta.url);await writeFile(output,'');const target={phone,address,device,session,script,output,pending:null};targets.push(target);
  script.message.connect(m=>{
   record(target,m);
   if(m.type==='send'&&m.payload.event==='api.exchange'){
    const p=m.payload;console.log(JSON.stringify({phone,path:p.path,status:p.status,title:p.response_summary.find(v=>v.key==='vod_name')?.value}));
    if(target.pending&&p.path===target.pending.path){clearTimeout(target.pending.timer);target.pending.resolve(p);target.pending=null;}
   }
  });
  await script.load();await script.exports.configure(key);await script.exports.setroute('direct');
 }
 for(const t of targets){
  const before=await t.script.exports.sessionstate();record(t,{event:'session.state.before',...before});
  console.log(JSON.stringify({phone:t.phone,stage:'before',format:before.format,expired:before.expired,installation_marker:before.installation_marker_visible_to_app,claim_names:Object.keys(before.claims??{})}));
  await request(t,'/api/public/init',()=>t.script.exports.refreshsession());await new Promise(r=>setTimeout(r,1500));
  const after=await t.script.exports.sessionstate();record(t,{event:'session.state.after',...after});
  await t.script.exports.openplayer();await new Promise(r=>setTimeout(r,2000));
  await request(t,'/api/vod/info_new',()=>t.script.exports.refreshplayer());
 }
}finally{
 for(const t of targets){if(t.pending)clearTimeout(t.pending.timer);await t.script.unload().catch(()=>{});await t.session.detach().catch(()=>{});await manager.removeRemoteDevice(t.address).catch(()=>{});}await writes;
}
