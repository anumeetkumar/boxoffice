// Emulator-only isolated control harness. Uses an in-memory player, no media URLs.
import Java from 'frida-java-bridge';
Java.perform(()=>Java.scheduleOnMainThread(()=>{
 try {
  const ActivityThread=Java.use('android.app.ActivityThread');
  const records=ActivityThread.currentActivityThread().mActivities.value.values().toArray();
  let activity;
  for(const r of records){const record=Java.cast(r,Java.use('android.app.ActivityThread$ActivityClientRecord'));if(!record.paused.value)activity=record.activity.value;}
  if(!activity)throw Error('No resumed test activity');
  const context=activity, resources=context.getResources();
  const id=name=>resources.getIdentifier(name,'id','com.fvvcl.flickverse');
  const layout=resources.getIdentifier('activity_video_play_detail','layout','com.fvvcl.flickverse');
  const root=Java.use('android.view.LayoutInflater').from(context).inflate(layout,null);
  const widget=Java.cast(root.findViewById(id('exo_play_context_id')),Java.use('chuangyuan.ycj.videolibrary.widget.VideoPlayerView'));
  const view=Java.cast(widget.getPlayerView(),Java.use('com.google.android.exoplayer2.ui.ExoPlayerView'));
  const controller=widget.getPlaybackControlView();
  let position=30000,duration=90000,playing=true,seeks=[],playChanges=[];
  const Long=Java.use('java.lang.Long'),Integer=Java.use('java.lang.Integer'),Boolean=Java.use('java.lang.Boolean');
  const Handler=Java.registerClass({name:'com.boxoffice.test.MemoryPlayerHandler',implements:[Java.use('java.lang.reflect.InvocationHandler')],methods:{invoke:function(proxy,method,args){
   const name=String(method.getName());
   if(name==='getCurrentPosition'||name==='getContentPosition'||name==='getBufferedPosition')return Long.valueOf(position);
   if(name==='getDuration')return Long.valueOf(duration);
   if(name==='getCurrentWindowIndex'||name==='getPlaybackState')return Integer.valueOf(name==='getPlaybackState'?3:0);
   if(name==='getPlayWhenReady')return Boolean.valueOf(playing);
   if(name==='isPlayingAd')return Boolean.valueOf(false);
   if(name==='seekTo'){position=Number(Java.cast(args[1],Long).longValue());seeks.push(position);return null;}
   if(name==='setPlayWhenReady'){playing=Java.cast(args[0],Boolean).booleanValue();playChanges.push(playing);return null;}
   if(name==='getCurrentTimeline')return Java.use('k3.v0').a.value;
   if(String(method.getReturnType().getName())==='boolean')return Boolean.valueOf(false);
   if(String(method.getReturnType().getName())==='int')return Integer.valueOf(0);
   if(String(method.getReturnType().getName())==='long')return Long.valueOf(0);
   return null;
  }}});
  const iface=Java.use('k3.n0');
  const proxy=Java.use('java.lang.reflect.Proxy').newProxyInstance(iface.class.getClassLoader(),Java.array('java.lang.Class',[iface.class]),Handler.$new());
  const player=Java.cast(proxy,iface);
  view._j.value=player;controller._P.value=player;
  const View=Java.use('android.view.View');
  const spec=Java.use('android.view.View$MeasureSpec');
  root.measure(spec.makeMeasureSpec(1280,1073741824),spec.makeMeasureSpec(720,1073741824));root.layout(0,0,1280,720);
  view.layout(0,0,1280,720);
  const Motion=Java.use('android.view.MotionEvent');
  let clock=10000;
  const event=(action,x)=>Motion.obtain(clock,clock,action,x,200,0);
  const tap=x=>{const down=event(0,x);view.onTouchEvent(down);down.recycle();clock+=30;const up=event(1,x);view.onTouchEvent(up);up.recycle();clock+=50;};
  const check=(condition,message)=>{if(!condition)throw Error(message);};
  tap(100);tap(100);check(position===20000&&playing,'left double tap');
  clock+=1000;tap(1100);tap(1100);check(position===30000&&playing,'right double tap');
  playing=false;clock+=1000;tap(1100);tap(1100);check(position===40000&&!playing,'paused seek preserves state');
  position=3000;clock+=1000;tap(100);tap(100);check(position===0,'start clamp');
  position=88000;clock+=1000;tap(1100);tap(1100);check(position===90000,'end clamp');
  duration=-9223372036854775807;const count=seeks.length;clock+=1000;tap(1100);tap(1100);check(seeks.length===count,'unknown duration guard');
  duration=90000;
  const play=Java.cast(root.findViewById(id('exo_play')),View),pause=Java.cast(root.findViewById(id('exo_pause')),View);
  check(String(Java.cast(Java.cast(play,View).getParent(),View).getTag())==='boxoffice_center_play','center play parent');
  check(String(Java.cast(Java.cast(pause,View).getParent(),View).getTag())==='boxoffice_center_play','center pause parent');
  const vip=Java.cast(root.findViewById(id('tv_openvip_horizontal')),View);
  check(vip.getLayoutParams().width.value===0&&vip.getLayoutParams().height.value===0,'subscribe collapsed');
  check(playChanges.length===0,'double tap never changes play state');
  playing=true;pause.performClick();check(!playing,'center pause click');
  play.performClick();check(playing,'center play click');
  let showed=0,hid=0;
  const Control=Java.use('com.google.android.exoplayer2.ui.PlayerControlView');
  Control.S.implementation=function(){showed++;return this.S();};
  Control.T.implementation=function(){hid++;return this.T();};
  controller.E();clock+=1000;tap(600);check(showed===1,'single tap shows controls');
  clock+=1000;tap(600);check(hid===1,'single tap hides controls');
  Control.S.implementation=null;Control.T.implementation=null;
  controller.setFull(false);
  const center=Java.cast(root.findViewById(id('exo_controller_center_view')),View);
  center.setVisibility(0);center.setAlpha(0);controller.S();
  const report={result:'pass',seeks,playChanges,centerButtons:true,subscribeCollapsed:true,singleTapShowHide:true,volumeFeedback:'patched flags verified statically; audible phone check pending'};
  setTimeout(()=>Java.scheduleOnMainThread(()=>{
   try{check(center.getVisibility()===0&&center.getAlpha()>0.95,'portrait center row is shown');report.portraitCenterRow=true;send(report);}
   catch(e){send({result:'fail',error:String(e),stack:e.stack});}
  }),500);
 }catch(e){send({result:'fail',error:String(e),stack:e.stack});}
}));
