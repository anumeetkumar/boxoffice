// Observe actual values, never alter requests, responses, certificate or verification.
import Java from 'frida-java-bridge';
let key=null;
rpc.exports={configure(value){key=value;return true;}};
Java.perform(()=>{
 const JString=Java.use('java.lang.String');
 const hmac=value=>{
  if(!key)return {redacted:true,length:String(value).length};
  const mac=Java.use('javax.crypto.Mac').getInstance('HmacSHA256');
  mac.init(Java.use('javax.crypto.spec.SecretKeySpec').$new(JString.$new(key).getBytes('UTF-8'),'HmacSHA256'));
  return {redacted:true,length:String(value).length,hmac_sha256:Array.from(mac.doFinal(JString.$new(String(value)).getBytes('UTF-8')),b=>(b&255).toString(16).padStart(2,'0')).join('')};
 };
 const safeHeaders=new Set(['app_id','package_name','version','sys_platform','mob_mfr','mobmodel','sysrelease','channel_code','is_vvv','is_language','is_display','app_language','en_al','user-agent','content-type','accept','cur_time']);
 const safeFields=new Set(['vod_id','audio_type','channel_id','pn','psize','vi','sr','cgi','cur_time']);
 safeFields.add('conf_key');
 safeFields.add('is_install');
 globalThis.boxOfficePrivateRedact=hmac;
 const summarize=data=>{
  const out=[];
  function walk(v,depth){
   if(v===null||typeof v!=='object'||depth>9||out.length>80)return;
   for(const[k,x]of Object.entries(v)){
    if(['vod_name','vod_year','vod_id','audio_type','code'].includes(k)&&typeof x!=='object')out.push({key:k,value:x});
    else if(['vod_url','orginal_url'].includes(k)&&typeof x==='string')out.push({key:k,...hmac(x)});
    else if(k==='api_url2'&&typeof x==='string'){
     try{const uri=Java.use('android.net.Uri').parse(x);out.push({key:k,scheme:String(uri.getScheme()),host:String(uri.getHost())});}catch(_){}
    }else if(typeof x==='object')walk(x,depth+1);
   }
  }walk(data,0);return out;
 };
 const Interceptor=Java.use('sa.b0$a'),intercept=Interceptor.intercept.overload('okhttp3.Interceptor$Chain');
 const Form=Java.use('okhttp3.FormBody');
 intercept.implementation=function(chain){
  const tid=Process.getCurrentThreadId(),profiles=globalThis.boxOfficeHeaderTestProfiles;
  const scoped=profiles&&String(chain.request().url().encodedPath())==='/api/vod/info_new';
  if(scoped)profiles.set(tid,globalThis.boxOfficeHeaderTestProfile);
  let response;
  try{response=intercept.call(this,chain);}catch(e){if(scoped)profiles.delete(tid);throw e;}
  try{
   const request=response.request(),path=String(request.url().encodedPath());
   if(!['/api/vod/info_new','/api/public/init','/api/public/get_sys_conf'].includes(path))return response;
   const headers={},form={};
   const hs=request.headers();
   for(let i=0;i<hs.size();i++){const name=String(hs.name(i)).toLowerCase(),value=String(hs.value(i));headers[name]=safeHeaders.has(name)?value:hmac(value);}
   try{const body=Java.cast(request.body(),Form);for(let i=0;i<body.size();i++){const name=String(body.name(i)),value=String(body.value(i));form[name]=safeFields.has(name)?value:hmac(value);}}catch(_){}
   let summary=[];try{summary=summarize(JSON.parse(String(response.peekBody(524288).string())));}catch(_){summary=[{parse_error:true}];}
   send({event:'api.exchange',route_test:globalThis.boxOfficeRouteTest??'direct',test_profile:globalThis.boxOfficeHeaderTestProfiles?.get(Process.getCurrentThreadId())??globalThis.boxOfficeHeaderTestProfile??'unmodified',time:new Date().toISOString(),host:String(request.url().host()),path,status:response.code(),request_headers:headers,request_form:form,response_summary:summary});
  }catch(_){send({event:'capture.error',detail:'Could not summarize exchange; original result preserved'});}
  if(scoped)profiles.delete(tid);
  return response;
 };
 const Model=Java.use('com.mgs.carparking.model.VIDEOPLAYDETAILVIEWMODEL');
 const submit=Model.S0.overload('int','java.lang.String','java.lang.String','int');
 submit.implementation=function(id,timestamp,signature,audio){
  try{send({event:'native.verify.consumed',vod_id:id,timestamp:String(timestamp),native_signature:hmac(String(signature)),audio_type:audio});}catch(_){}
  return submit.call(this,id,timestamp,signature,audio);
 };
 let certificate=null,host=null;
 try{certificate=String(Java.use('sa.e').l());host=String(Java.use('sa.o0').p());}catch(_){}
 send({event:'capture.ready',certificate_sha1:certificate,saved_api_host:host,mode:'observation only; private values HMAC-redacted before leaving the process'});
});
