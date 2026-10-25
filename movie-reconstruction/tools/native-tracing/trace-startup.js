import Java from 'frida-java-bridge';

// Observation only: all hooks return the original result without changing it.
Java.perform(() => {
    const Hls = Java.use('com.pp.hls');
    const Digest = Java.use('java.security.MessageDigest');
    const Log = Java.use('android.util.Log');
    const Exception = Java.use('java.lang.Exception');
    const active = new Set();
    const hex = bytes => Array.from(bytes, b => (b & 255).toString(16).padStart(2, '0')).join('');
    const inLoad = () => active.has(Process.getCurrentThreadId());
    const emit = (event, values) => send({ event, tid: Process.getCurrentThreadId(), ...values });
    const load = Hls.load.overload(...Array(7).fill('java.lang.String'));
    load.implementation = function (...args) {
        const tid = Process.getCurrentThreadId();
        active.add(tid);
        emit('hls.load.enter', { package: String(args[1]), channel: String(args[2]), config_length: args[5] === null ? 0 : String(args[5]).length });
        try {
            const result = load.call(this, ...args);
            emit('hls.load.return', { result });
            return result;
        } catch (error) {
            emit('hls.load.exception', { error: String(error) });
            throw error;
        } finally {
            active.delete(tid);
        }
    };
    const PM = Java.use('android.app.ApplicationPackageManager');
    for (const overload of PM.getPackageInfo.overloads) {
        overload.implementation = function (...args) {
            const result = overload.call(this, ...args);
            if (inLoad()) emit('PackageManager.getPackageInfo', { package: String(args[0]), flags: String(args[1]), stack: Log.getStackTraceString(Exception.$new()).toString() });
            return result;
        };
    }
    const Signature = Java.use('android.content.pm.Signature');
    const toBytes = Signature.toByteArray.overload();
    toBytes.implementation = function () {
        const result = toBytes.call(this);
        if (inLoad()) emit('Signature.toByteArray', { certificate_sha256: hex(Digest.getInstance('SHA-256').digest(result)), bytes: result.length });
        return result;
    };
    const chars = Signature.toCharsString.overload();
    chars.implementation = function () {
        const result = chars.call(this);
        if (inLoad()) emit('Signature.toCharsString', { character_count: String(result).length });
        return result;
    };
    const table = Java.vm.getEnv().handle.readPointer();
    let nativeEvents = 0;
    for (const [name, index] of [['GetMethodID', 33], ['GetStaticMethodID', 113]]) {
        Interceptor.attach(table.add(index * Process.pointerSize).readPointer(), {
            onEnter(args) {
                if (!inLoad() || nativeEvents++ >= 120) return;
                try { emit('JNI.' + name, { method: args[2].readCString(), signature: args[3].readCString() }); }
                catch (error) { emit('trace.read-error', { error: String(error) }); }
            }
        });
    }
    const libc = Process.getModuleByName('libc.so');
    for (const name of ['open', 'openat']) {
        const address = libc.findExportByName(name);
        if (address === null) continue;
        Interceptor.attach(address, {
            onEnter(args) {
                if (!inLoad() || nativeEvents++ >= 120) return;
                try { emit('native.' + name, { path: args[name === 'openat' ? 1 : 0].readCString() }); }
                catch (error) { emit('trace.read-error', { error: String(error) }); }
            }
        });
    }
    emit('trace.ready', { arch: Process.arch, mode: 'read-only; original results preserved' });
});
