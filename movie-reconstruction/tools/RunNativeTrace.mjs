import * as frida from '../../rea/node_modules/frida/build/src/frida.js';
import { writeFile, appendFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';

const root = new URL('../', import.meta.url);
const entry = fileURLToPath(new URL('native-tracing/trace-startup.js', import.meta.url));
const label = process.argv[2];
if (!/^[a-z0-9-]+$/.test(label ?? '')) throw new Error('Supply a simple trace label');
const output = new URL(`reports/native-trace-${label}.jsonl`, root);
const compiler = new frida.Compiler();
compiler.diagnostics.connect(diagnostic => console.error(JSON.stringify(diagnostic)));
const source = await compiler.build(entry);
await writeFile(new URL('native-tracing/trace-startup.bundle.js', import.meta.url), source);
if (process.argv.includes('--compile-only')) { console.log('Trace compiled'); process.exit(0); }
await writeFile(output, '');
const manager = frida.getDeviceManager();
const device = await manager.addRemoteDevice('127.0.0.1:27043');
let session;
let script;
let pid;
let resumed = false;
let writes = Promise.resolve();
try {
    pid = await device.spawn('com.fvvcl.flickverse');
    console.log('Spawned emulator app PID', pid);
    session = await device.attach(pid, { realm: frida.Realm.Native });
    script = await session.createScript(source, { name: 'read-only-sdk-startup' });
    script.message.connect(message => {
        const line = JSON.stringify({ time: new Date().toISOString(), pid, message });
        console.log(line);
        writes = writes.then(() => appendFile(output, line + '\n'));
    });
    await script.load();
    await device.resume(pid);
    resumed = true;
    await new Promise(resolve => setTimeout(resolve, 45000));
} finally {
    if (script) await script.unload().catch(error => console.error('Script cleanup:', error.message));
    if (session) await session.detach().catch(error => console.error('Session cleanup:', error.message));
    if (pid && !resumed) await device.resume(pid).catch(error => console.error('Resume cleanup:', error.message));
    await writes;
    await manager.removeRemoteDevice('127.0.0.1:27043');
}
