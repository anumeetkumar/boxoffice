import * as frida from '../../rea/node_modules/frida/build/src/frida.js';
import {writeFile,appendFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
const [label,pid]=process.argv.slice(2);
if(!/^[a-z0-9-]+$/.test(label??'')||!/^\d+$/.test(pid??''))throw Error('Supply label and emulator app PID');
const bundle=await new frida.Compiler().build(fileURLToPath(new URL('native-tracing/observe-catalog.js',import.meta.url)));
const manager=frida.getDeviceManager(),device=await manager.addRemoteDevice('127.0.0.1:27043');
const output=new URL(`../reports/catalog-${label}.jsonl`,import.meta.url);await writeFile(output,'');
let session,script,writes=Promise.resolve();
try{
 session=await device.attach(Number(pid),{realm:frida.Realm.Native});script=await session.createScript(bundle);
 script.message.connect(m=>{console.log(JSON.stringify(m));writes=writes.then(()=>appendFile(output,JSON.stringify(m)+'\n'));});
 await script.load();
 if(process.argv.includes('--refresh')){
  for(let i=0;i<12;i++){await new Promise(resolve=>setTimeout(resolve,3000));if(!await script.exports.refresh())throw Error('No resumed player for refresh test');}
  await new Promise(resolve=>setTimeout(resolve,5000));
 }else await new Promise(resolve=>setTimeout(resolve,55000));
}finally{if(script)await script.unload();if(session)await session.detach();await writes;await manager.removeRemoteDevice('127.0.0.1:27043');}
