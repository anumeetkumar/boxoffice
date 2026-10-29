import './test-sdk-refresh.js';
import Java from 'frida-java-bridge';
let route='direct';
rpc.exports.setroute=value=>{if(!['direct','pc-tunnel'].includes(value))throw Error('Unsupported route');route=value;globalThis.boxOfficeRouteTest=value;return true;};
Java.perform(()=>{
 const Client=Java.use('okhttp3.OkHttpClient'),call=Client.newCall.overload('okhttp3.Request');
 const Proxy=Java.use('java.net.Proxy'),Type=Java.use('java.net.Proxy$Type'),Address=Java.use('java.net.InetSocketAddress');
 call.implementation=function(request){
  if(route==='pc-tunnel'&&String(request.url().host())==='moviein.ajfysu.com'&&String(request.url().encodedPath()).startsWith('/api/')){
   const client=this.newBuilder().proxy(Proxy.$new(Type.HTTP.value,Address.$new('127.0.0.1',18080))).build();
   return call.call(client,request);
  }
  return call.call(this,request);
 };
 send({event:'route.test.ready',authentication_override:false,tls_decryption:false});
});
