// Read-only diagnostics. No certificate/identity/request/response substitution.
import Java from 'frida-java-bridge';
rpc.exports={refresh(){return new Promise((resolve,reject)=>Java.perform(()=>Java.scheduleOnMainThread(()=>{
 try{
  const thread=Java.use('android.app.ActivityThread').currentActivityThread();
  const records=thread.mActivities.value.values().toArray();
  for(const item of records){
   const record=Java.cast(item,Java.use('android.app.ActivityThread$ActivityClientRecord'));
   const activity=record.activity.value;
   if(!record.paused.value&&String(activity.getClass().getName())==='com.mgs.carparking.ui.homecontent.videodetail.VideoPlayDetailActivity'){
    Java.cast(activity,Java.use('com.mgs.carparking.ui.homecontent.videodetail.VideoPlayDetailActivity')).getSignInfo();resolve(true);return;
   }
  }resolve(false);
 }catch(e){reject(String(e));}
})));}};
Java.perform(()=>{
 const Interceptor=Java.use('sa.b0$a');
 const intercept=Interceptor.intercept.overload('okhttp3.Interceptor$Chain');
 const Form=Java.use('okhttp3.FormBody');
 const digest=value=>{
  const MD=Java.use('java.security.MessageDigest');
  const bytes=MD.getInstance('SHA-256').digest(Java.use('java.lang.String').$new(value).getBytes('UTF-8'));
  return Array.from(bytes,b=>(b&255).toString(16).padStart(2,'0')).join('');
 };
 const summarize=(data)=>{
  const out=[];
  function visit(v,depth){
   if(depth>8||out.length>50||v===null||typeof v!=='object')return;
   for(const [k,x]of Object.entries(v)){
    if(['vod_name','vod_year','vod_id','audio_type','api_url2','code','msg','message'].includes(k)&&typeof x!=='object')out.push({key:k,value:x});
    else if(['vod_url','orginal_url'].includes(k)&&typeof x==='string')out.push({key:k,sha256:digest(x)});
    else if(typeof x==='object')visit(x,depth+1);
   }
  }visit(data,0);return out;
 };
 intercept.implementation=function(chain){
  const request=chain.request(),path=String(request.url().encodedPath());
  const relevant=path.startsWith('/api/');
  let form={};
  try{const body=Java.cast(request.body(),Form);for(let i=0;i<body.size();i++){
   const name=String(body.name(i));
   if(['vi','sr','cgi','vod_id','audio_type','channel_id'].includes(name))form[name]=String(body.value(i));
  }}catch(_){}
  const response=intercept.call(this,chain);
  if(relevant){
   let summary;
   try{summary=summarize(JSON.parse(String(response.peekBody(524288).string())));}catch(e){summary={parse_error:String(e)};}
   send({event:'api.response',host:String(request.url().host()),path,form,status:response.code(),summary});
  }
  return response;
 };
 send({event:'ready',certificate:String(Java.use('sa.e').l()),saved_api_host:String(Java.use('sa.o0').p()),mode:'observation only; tokens, IDs and signatures omitted'});
});
