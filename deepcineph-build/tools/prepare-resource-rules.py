import pathlib,xml.etree.ElementTree as E,json
root=pathlib.Path(__file__).resolve().parents[1]
source=root.parent/'deepcineph-reconstruction/apktool/res'
a='{http://schemas.android.com/apk/res/android}'
# Actual application placements and upsells only; streaming-provider catalog tiles remain.
hide={'vpLayout','vipBg','vipAD','video_top_ad','tv_openvip_horizontal','tvRightJoin','joinSkipAd','tvLookAD','iv_ad_click_player','iv_ad_share_click_player','flPauseAd','fl_ad','adContainer','fl_ad_container'}
refs={'@string/str_detail_open_vip','@string/str_subscription','@string/str_join_vp','@string/str_join_vp_noad','@string/str_look_ad','@string/str_lookad_tip','@string/str_lookad_tip2','@string/text_home_detail_look_ad_lock','@string/str_vip_tip1','@string/str_viptip2'}
(root/'ready/resource-rules.json').write_text(json.dumps({'hidden_ids':sorted(hide),'hidden_text_refs':sorted(refs)},indent=2),encoding='utf-8')
print('Resource rules saved')
