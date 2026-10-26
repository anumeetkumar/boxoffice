import * as frida from '../../rea/node_modules/frida/build/src/frida.js';
import {writeFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
const bundle=await new frida.Compiler().build(fileURLToPath(new URL('native-tracing/test-player-controls.js',import.meta.url)));
const manager=frida.getDeviceManager(),device=await manager.addRemoteDevice('127.0.0.1:27043');
let session,script,timer;
try {
 session=await device.attach(Number(process.argv[2]),{realm:frida.Realm.Native});
 script=await session.createScript(bundle);
 const result= new Promise((resolve,reject)=>{script.message.connect(message=>{console.log(JSON.stringify(message));if(message.type==='send')resolve(message.payload);else if(message.type==='error')reject(Error(message.description));});timer=setTimeout(()=>reject(Error('Test timed out')),25000);});
 await script.load();const report=await result;
 await writeFile(new URL('../reports/boxoffice-player-runtime-test.json',import.meta.url),JSON.stringify(report,null,2));
 if(report.result!=='pass')process.exitCode=1;
}finally{clearTimeout(timer);if(script)await script.unload();if(session)await session.detach();await manager.removeRemoteDevice('127.0.0.1:27043');}
