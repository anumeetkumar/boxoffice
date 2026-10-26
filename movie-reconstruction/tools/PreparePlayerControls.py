"""Reproducible player-only changes; retain original single-tap and playback wiring."""
import pathlib, re, json, xml.etree.ElementTree as ET
root=pathlib.Path(__file__).resolve().parent.parent
work=root/'boxoffice'
file=work/'smali8/com/google/android/exoplayer2/ui/ExoPlayerView.smali'
text=file.read_text()
if 'boxOfficeSeek' not in text:
    method=re.search(r'\.method public onTouchEvent\(Landroid/view/MotionEvent;\)Z.*?\.end method',text,re.S)[0]
    start=method.index('    invoke-interface {v0}, Lk3/n0;->getPlayWhenReady()Z')
    end=method.index('    :cond_9',start)
    method=method[:start]+'    invoke-direct {p0, p1}, Lcom/google/android/exoplayer2/ui/ExoPlayerView;->boxOfficeSeek(Landroid/view/MotionEvent;)V\n\n'+method[end:]
    text=re.sub(r'\.method public onTouchEvent\(Landroid/view/MotionEvent;\)Z.*?\.end method',lambda _:method,text,flags=re.S)
    text+='''
.method private boxOfficeSeek(Landroid/view/MotionEvent;)V
    .locals 8
    iget-object v0, p0, Lcom/google/android/exoplayer2/ui/PlayerView;->j:Lk3/n0;
    if-eqz v0, :done
    invoke-interface {v0}, Lk3/n0;->isPlayingAd()Z
    move-result v1
    if-nez v1, :done
    invoke-interface {v0}, Lk3/n0;->getDuration()J
    move-result-wide v4
    const-wide/16 v6, 0x0
    cmp-long v1, v4, v6
    if-lez v1, :done
    invoke-interface {v0}, Lk3/n0;->getCurrentPosition()J
    move-result-wide v2
    invoke-virtual {p1}, Landroid/view/MotionEvent;->getX()F
    move-result v1
    invoke-virtual {p0}, Landroid/view/View;->getWidth()I
    move-result v7
    int-to-float v7, v7
    const/high16 v6, 0x40000000
    div-float/2addr v7, v6
    cmpg-float v1, v1, v7
    const-wide/16 v6, 0x2710
    if-gez v1, :forward
    sub-long/2addr v2, v6
    goto :clamp
    :forward
    add-long/2addr v2, v6
    :clamp
    const-wide/16 v6, 0x0
    invoke-static {v2, v3, v6, v7}, Ljava/lang/Math;->max(JJ)J
    move-result-wide v2
    invoke-static {v2, v3, v4, v5}, Ljava/lang/Math;->min(JJ)J
    move-result-wide v2
    invoke-interface {v0}, Lk3/n0;->getCurrentWindowIndex()I
    move-result v1
    invoke-interface {v0, v1, v2, v3}, Lk3/n0;->seekTo(IJ)V
    :done
    return-void
.end method
'''
    file.write_text(text)

# Remove FLAG_PLAY_SOUND (4), retaining music stream and volume calculations.
for rel,reg in [('smali8/t/b.smali','v3'),('smali7/com/mgs/carparking/widgets/dialog/f$a.smali','v0')]:
    file=work/rel; text=file.read_text()
    method_name='R' if rel.startswith('smali8') else 'onProgressChanged'
    pattern=r'(\.method[^\n]* '+method_name+r'\([^\n]*\n).*?\.end method'
    match=re.search(pattern,text,re.S)
    if not match or 'setStreamVolume(III)V' not in match[0]:raise RuntimeError('Volume method missing: '+rel)
    body=match[0]
    if f'const/4 {reg}, 0x4' in body:body=body.replace(f'const/4 {reg}, 0x4',f'const/4 {reg}, 0x0')
    elif f'const/4 {reg}, 0x0' not in body:raise RuntimeError('Unexpected sound flag')
    file.write_text(text[:match.start()]+body+text[match.end():])

A='{http://schemas.android.com/apk/res/android}'
ET.register_namespace('android',A[1:-1])
file=work/'apktool/res/layout/exo_playback_top_my_new.xml'
tree=ET.parse(file); top=tree.getroot()
nodes={e.get(A+'id','').split('/')[-1]:e for e in top.iter() if e.get(A+'id')}
vip=nodes['tv_openvip_horizontal']
for k,v in [('visibility','gone'),('layout_width','0dp'),('layout_height','0dp'),('paddingLeft','0dp'),('paddingRight','0dp'),('clickable','false')]:vip.set(A+k,v)
center=nodes['exo_controller_center_view']; center.set(A+'gravity','center')
if not any(e.get(A+'tag')=='boxoffice_center_play' for e in center):
    parents={e:p for p in top.iter() for e in p}
    frame=ET.Element('FrameLayout',{A+'tag':'boxoffice_center_play',A+'layout_width':'56dp',A+'layout_height':'56dp'})
    for id_ in ['exo_play','exo_pause']:
        button=nodes[id_]; parents[button].remove(button)
        for k,v in [('layout_width','56dp'),('layout_height','56dp'),('layout_gravity','center'),('padding','8dp'),('soundEffectsEnabled','false')]:button.set(A+k,v)
        frame.append(button)
    center.insert(1,frame)
    # Retain the fullscreen binding IDs inside a zero-size wrapper; the shared
    # center pair already follows the same PlayerControlView state callbacks.
    hidden=ET.Element('FrameLayout',{A+'layout_width':'0dp',A+'layout_height':'0dp',A+'visibility':'gone'})
    for id_ in ['exo_play1','exo_pause1']:
        button=nodes[id_]; parents[button].remove(button); hidden.append(button)
    nodes['exo_controller_bottom'].append(hidden)
for id_,margin,desc in [('icRetreat','layout_marginRight','Rewind 10 seconds'),('icFast','layout_marginLeft','Forward 10 seconds')]:
    nodes[id_].set(A+margin,'24dp'); nodes[id_].set(A+'contentDescription',desc)
for id_,desc in [('exo_play','Play'),('exo_pause','Pause')]:nodes[id_].set(A+'contentDescription',desc)
tree.write(file,encoding='utf-8',xml_declaration=True)
(root/'reports/boxoffice-player-controls.json').write_text(json.dumps({'single_tap':'original show/hide code preserved','double_tap':'left -10000ms, right +10000ms; clamped to [0,duration]; play state unchanged','center_controls':'existing exo_play/exo_pause IDs and state callbacks','fullscreen_subscribe':'collapsed, binding ID retained','volume_feedback':'FLAG_PLAY_SOUND cleared in gesture and player sliders','runtime_verified':False},indent=2))
print('Prepared centered controls, fullscreen upsell removal, silent volume and directional double-tap seeking')
