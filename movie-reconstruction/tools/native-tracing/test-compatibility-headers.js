// Bounded, explicitly requested compatibility test. Authentication remains genuine.
import './capture-phone-traffic.js';
import Java from 'frida-java-bridge';
globalThis.boxOfficeHeaderTestProfile='baseline';
rpc.exports.setprofile=name=>{
 if(!['baseline','model-only','os-only','model-and-os'].includes(name))throw Error('Unsupported compatibility profile');
 globalThis.boxOfficeHeaderTestProfile=name;return true;
};
rpc.exports.refresh=()=>new Promise((resolve,reject)=>Java.perform(()=>Java.scheduleOnMainThread(()=>{
 try{
  const records=Java.use('android.app.ActivityThread').currentActivityThread().mActivities.value.values().toArray();
  for(const item of records){
   const record=Java.cast(item,Java.use('android.app.ActivityThread$ActivityClientRecord'));
   const activity=record.activity.value;
   if(!record.paused.value&&String(activity.getClass().getName())==='com.mgs.carparking.ui.homecontent.videodetail.VideoPlayDetailActivity'){
    Java.cast(activity,Java.use('com.mgs.carparking.ui.homecontent.videodetail.VideoPlayDetailActivity')).getSignInfo();resolve(true);return;
   }
  }resolve(false);
 }catch(e){reject(String(e));}
})));
Java.perform(()=>{
 const active=new Map();
 globalThis.boxOfficeHeaderTestProfiles=active;
 const add=Java.use('okhttp3.Request$Builder').addHeader.overload('java.lang.String','java.lang.String');
 add.implementation=function(name,value){
  const profile=active.get(Process.getCurrentThreadId());
  if(String(name)==='mobmodel'&&(profile==='model-only'||profile==='model-and-os'))value='SM-M536B';
  if(String(name)==='sysrelease'&&(profile==='os-only'||profile==='model-and-os'))value='16';
  return add.call(this,name,value);
 };
 send({event:'compatibility.ready',fields_allowed:['mobmodel','sysrelease'],authentication_override:false});
});
