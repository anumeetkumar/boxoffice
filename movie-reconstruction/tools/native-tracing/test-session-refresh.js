import './test-common-route.js';
import Java from 'frida-java-bridge';
const onMain=fn=>new Promise((resolve,reject)=>Java.perform(()=>Java.scheduleOnMainThread(()=>{try{resolve(fn());}catch(e){reject(String(e));}})));
rpc.exports.refreshsession=()=>onMain(()=>{Java.use('sa.c').f('');return true;});
rpc.exports.sessionstate=()=>onMain(()=>{
 const token=String(Java.use('sa.o0').R()),now=Date.now()/1000;
 const result={token:globalThis.boxOfficePrivateRedact(token),native_configuration:globalThis.boxOfficePrivateRedact(String(Java.use('sa.o0').J())),installation_marker_visible_to_app:Java.use('sa.e').p(),now_epoch_seconds:Math.floor(now)};
 try{
  const parts=token.split('.');if(parts.length!==3){result.format='opaque';return result;}
  const decoded=Java.use('java.lang.String').$new(Java.use('android.util.Base64').decode(parts[1],10),'UTF-8');
  const claims=JSON.parse(String(decoded)),masked={};
  for(const[k,v]of Object.entries(claims)){
   if(['iat','exp','nbf'].includes(k)&&typeof v==='number')masked[k]=v;
   else masked[k]=globalThis.boxOfficePrivateRedact(JSON.stringify(v));
  }
  result.format='jwt';result.claims=masked;
  if(typeof claims.exp==='number')result.expired=now>=claims.exp;
  if(typeof claims.nbf==='number')result.not_yet_valid=now<claims.nbf;
 }catch(_){result.format='opaque-or-unparseable';}
 return result;
});
