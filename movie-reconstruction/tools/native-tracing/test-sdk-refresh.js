// Exercise only the original client's own configuration refresh path.
import './capture-phone-traffic.js';
import Java from 'frida-java-bridge';
const onMain=fn=>new Promise((resolve,reject)=>Java.perform(()=>Java.scheduleOnMainThread(()=>{try{resolve(fn());}catch(e){reject(String(e));}})));
rpc.exports.sdkstate=()=>onMain(()=>({port:Java.use('com.mgs.carparking.app.AppApplication').port.value,configuration:globalThis.boxOfficePrivateRedact(String(Java.use('sa.o0').J()))}));
rpc.exports.refreshconfiguration=()=>onMain(()=>{Java.use('sa.c').h(true);return true;});
rpc.exports.openplayer=()=>onMain(()=>{
 const context=Java.use('me.goldze.mvvmhabit.base.BaseApplication').getInstance();
 const intent=Java.use('android.content.Intent').$new(context,Java.use('com.mgs.carparking.ui.homecontent.videodetail.VideoPlayDetailActivity').class);
 intent.putExtra.overload('java.lang.String','int').call(intent,'id',2077341734);
 intent.putExtra.overload('java.lang.String','int').call(intent,'language_type',0);
 intent.setFlags(0x10000000);context.startActivity(intent);return true;
});
rpc.exports.refreshplayer=()=>onMain(()=>{
 const records=Java.use('android.app.ActivityThread').currentActivityThread().mActivities.value.values().toArray();
 for(const item of records){const rec=Java.cast(item,Java.use('android.app.ActivityThread$ActivityClientRecord'));const a=rec.activity.value;
  if(!rec.paused.value&&String(a.getClass().getName())==='com.mgs.carparking.ui.homecontent.videodetail.VideoPlayDetailActivity'){
   Java.cast(a,Java.use('com.mgs.carparking.ui.homecontent.videodetail.VideoPlayDetailActivity')).getSignInfo();return true;
  }
 }return false;
});
Java.perform(()=>{
 const load=Java.use('com.pp.hls').load.overload(...Array(7).fill('java.lang.String'));
 load.implementation=function(...args){
  const result=load.call(this,...args);
  send({event:'native.sdk.loaded',package:String(args[1]),channel:String(args[2]),configuration:globalThis.boxOfficePrivateRedact(String(args[5])),mode:String(args[6]),returned_port:result});
  return result;
 };
 send({event:'sdk.refresh.test.ready'});
});
