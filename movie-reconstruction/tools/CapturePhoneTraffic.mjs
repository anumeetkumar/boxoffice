import * as frida from '../../rea/node_modules/frida/build/src/frida.js';
import {readFile,writeFile,appendFile} from 'node:fs/promises';
import {randomBytes} from 'node:crypto';
import {fileURLToPath} from 'node:url';
const [label,port,target='Gadget']=process.argv.slice(2);
if(!/^[a-z0-9-]+$/.test(label??'')||!/^\d+$/.test(port??''))throw Error('Supply label, forwarded port and optional app PID');
const keyFile=new URL('native-tracing/capture-redaction-key.private',import.meta.url);
let key;try{key=(await readFile(keyFile,'utf8')).trim();}catch{key=randomBytes(32).toString('hex');await writeFile(keyFile,key,{mode:0o600});}
const bundle=await new frida.Compiler().build(fileURLToPath(new URL('native-tracing/capture-phone-traffic.js',import.meta.url)));
const manager=frida.getDeviceManager(),device=await manager.addRemoteDevice(`127.0.0.1:${port}`);
const out=new URL(`../reports/phone-capture-${label}.jsonl`,import.meta.url);await writeFile(out,'');
let session,script,writes=Promise.resolve();
try{
 session=await device.attach(/^\d+$/.test(target)?Number(target):target,{realm:frida.Realm.Native});
 script=await session.createScript(bundle);
 script.message.connect(m=>{writes=writes.then(()=>appendFile(out,JSON.stringify(m)+'\n'));if(m.type==='send')console.log(JSON.stringify(m.payload));else console.log(JSON.stringify({type:m.type,description:'Observer diagnostic error; see redacted capture log'}));});
 await script.load();await script.exports.configure(key);
 if(target==='Gadget'){const processes=await device.enumerateProcesses();const gadget=processes.find(p=>p.name==='Gadget');if(gadget)await device.resume(gadget.pid).catch(()=>{});}
 for(let i=0;i<4;i++)await new Promise(resolve=>setTimeout(resolve,30000));
}finally{if(script)await script.unload().catch(()=>{});if(session)await session.detach().catch(()=>{});await writes;await manager.removeRemoteDevice(`127.0.0.1:${port}`);}
