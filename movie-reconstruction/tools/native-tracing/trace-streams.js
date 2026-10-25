import Java from 'frida-java-bridge';
Java.perform(() => {
    const Uri = Java.use('android.net.Uri');
    const Base64 = Java.use('android.util.Base64');
    const JString = Java.use('java.lang.String');
    const describe = value => {
        const uri = Uri.parse(String(value));
        const info = {scheme: String(uri.getScheme()), host: String(uri.getHost()), path: String(uri.getPath())};
        const encoded = uri.getQueryParameter('src');
        if (encoded !== null) {
            try {
                const upstream = Uri.parse(JString.$new(Base64.decode(encoded, 0)).toString());
                info.upstream = {scheme: String(upstream.getScheme()), host: String(upstream.getHost()), path: String(upstream.getPath()), has_query: upstream.getQuery() !== null};
            } catch (_) { info.upstream = 'opaque resource identifier'; }
        }
        return info;
    };
    const Source = Java.use('com.google.android.exoplayer2.upstream.d');
    const open = Source.a.overload('e5.h');
    open.implementation = function(spec) {
        const start = Date.now();
        let location;
        try {
            for(const field of spec.getClass().getDeclaredFields()) {
                if(field.getType().getName().toString()==='android.net.Uri') {
                    field.setAccessible(true);
                    location=describe(field.get(spec).toString());
                    break;
                }
            }
        } catch (e) { location = {error: String(e)}; }
        send({event:'source.open', location});
        try {
            const length = open.call(this, spec);
            send({event:'source.opened', location, elapsed_ms: Date.now()-start, length: String(length)});
            return length;
        } catch (e) {
            send({event:'source.error', location, elapsed_ms: Date.now()-start, error:String(e)});
            throw e;
        }
    };
    const read = Source.read.overload('[B','int','int');
    let bytes=0, last=Date.now();
    read.implementation=function(...args) {
        const count=read.call(this,...args);
        if(count>0)bytes+=count;
        if(Date.now()-last>5000){send({event:'source.bytes',bytes_read:bytes});last=Date.now();}
        return count;
    };
    send({event:'trace.ready',mode:'observation only; original results preserved; query values omitted'});
});
