import * as frida from '../../rea/node_modules/frida/build/src/frida.js';
import {fileURLToPath} from 'node:url';
import {writeFile} from 'node:fs/promises';
const bundle=await new frida.Compiler().build(fileURLToPath(new URL('native-tracing/endpoint-startup.js',import.meta.url)));
const manager=frida.getDeviceManager(),device=await manager.addRemoteDevice('127.0.0.1:27042');let session,script;const events=[];
try{session=await device.attach('Gadget',{realm:frida.Realm.Native});script=await session.createScript(bundle);let ready;const p=new Promise(r=>ready=r);script.message.connect(m=>{if(m.type==='send'){events.push(m.payload);console.log(JSON.stringify(m.payload));if(m.payload.ready)ready();}else console.log(m.description);});await script.load();await p;console.log(JSON.stringify(await script.exports.check()));await writeFile(new URL('../reports/endpoint-startup.json',import.meta.url),JSON.stringify(events,null,2));}finally{if(script)await script.unload();if(session)await session.detach();await manager.removeRemoteDevice('127.0.0.1:27042');}
