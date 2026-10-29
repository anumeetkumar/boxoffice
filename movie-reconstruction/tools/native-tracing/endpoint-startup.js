import Java from 'frida-java-bridge';
Java.perform(()=>{
 const I=Java.use('sa.b0$a'),m=I.intercept.overload('okhttp3.Interceptor$Chain');
 m.implementation=function(c){const r=m.call(this,c);try{const q=r.request(),j=JSON.parse(String(r.peekBody(1048576).string()));send({path:String(q.url().encodedPath()),host:String(q.url().host()),app_language:String(q.header('app_language')),http:r.code(),business_code:j.code,message:String(j.msg??j.message??'').slice(0,200),has_result:j.result!=null});}catch(_){}return r;};
 rpc.exports={check(){return new Promise(resolve=>Java.perform(()=>{const H=Java.use('java.util.HashMap'),S=Java.use('java.lang.String'),a=Java.use('p9.a'),svc=Java.cast(Java.use('sa.b0').c().a(a.class),a);let result=[];for(const [name,method,fields] of [['init','G',{invited_by:'',is_install:'0'}],['config','R',{conf_key:'conf_key1'}]]){try{const map=H.$new();for(const[k,v]of Object.entries(fields))map.put(S.$new(k),S.$new(v));const r=svc[method](map).d();result.push({name,code:r.getCode()});}catch(e){result.push({name,error:String(e).slice(0,160)});}}resolve(result);}));}};
 send({ready:true});
});
