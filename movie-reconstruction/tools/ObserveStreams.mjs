import * as frida from '../../rea/node_modules/frida/build/src/frida.js';
import {writeFile,appendFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
const [label,pid]=process.argv.slice(2);
if(!/^[a-z0-9-]+$/.test(label??'')||!/^\d+$/.test(pid??''))throw Error('Supply label and emulator PID');
const compiler=new frida.Compiler();
const bundle=await compiler.build(fileURLToPath(new URL('native-tracing/trace-streams.js',import.meta.url)));
const manager=frida.getDeviceManager();
const device=await manager.addRemoteDevice('127.0.0.1:27043');
const output=new URL(`../reports/streams-${label}.jsonl`,import.meta.url);
await writeFile(output,'');
let session,script,writes=Promise.resolve();
try{
    session=await device.attach(Number(pid),{realm:frida.Realm.Native});
    script=await session.createScript(bundle,{name:'read-only-stream-observer'});
    script.message.connect(message=>{const line=JSON.stringify(message);console.log(line);writes=writes.then(()=>appendFile(output,line+'\n'));});
    await script.load();
    for(let i=0;i<4;i++)await new Promise(resolve=>setTimeout(resolve,30000));
}finally{
    if(script)await script.unload().catch(e=>console.error(e.message));
    if(session)await session.detach().catch(e=>console.error(e.message));
    await writes;
    await manager.removeRemoteDevice('127.0.0.1:27043');
}
