import json, pathlib, re, shutil, xml.etree.ElementTree as ET
from PIL import Image

root = pathlib.Path(__file__).resolve().parent.parent
work = root / 'boxoffice'
decoded = work / 'apktool'
source = root / 'bytecode-app/apktool'
if not decoded.exists():
    shutil.copytree(source, decoded, ignore=shutil.ignore_patterns('build', 'dist'))
smali = work / 'smali5'
if not smali.exists():
    shutil.copytree(root / 'tools/native-tracing/sdk-dex/classes5.dex-smali', smali)
assets = work / 'assets'
assets.mkdir(exist_ok=True)
generated = pathlib.Path(r'C:\Users\AlphaDell-60\.codex\generated_images\01a166e7-4545-79a1-8e40-009a501a75c7\exec-973c52ed-3487-4220-9f3c-16ffd397db15.png')
if not (assets / 'boxoffice-icon.png').exists(): shutil.copy2(generated, assets / 'boxoffice-icon.png')
icon = Image.open(assets / 'boxoffice-icon.png').convert('RGB')

def replace_method(text, name, body):
    pattern = re.compile(r'(^\.method[^\n]*\s' + re.escape(name) + r'\([^\n]*\n).*?^\.end method', re.M | re.S)
    text, count = pattern.subn(lambda m: m[1] + body + '\n.end method', text)
    if count < 1: raise RuntimeError('Expected method missing: ' + name)
    return text, count

app_file = smali / 'com/mgs/carparking/app/AppApplication.smali'
app = app_file.read_text()
app, init_count = replace_method(app, 'loadAdConf', '    .locals 0\n    return-void')
app_file.write_text(app)
main_file = smali / 'com/mgs/carparking/ui/MainActivity.smali'
main = main_file.read_text()
main, _ = replace_method(main, 'E', '    .locals 0\n    return-void')
main, _ = replace_method(main, 'P', '    .locals 0\n    return-void')
main, _ = replace_method(main, 'H', '''    .locals 2
    invoke-virtual {p1}, Lx9/b0;->a()I
    move-result v0
    add-int/lit8 v0, v0, -0x65
    const/4 v1, 0x3
    if-eq v0, v1, :boxoffice_done
    const/4 v1, 0x4
    if-ne v0, v1, :boxoffice_navigate
    const/4 v0, 0x3
    :boxoffice_navigate
    iget-object p1, p0, Lcom/mgs/carparking/app/BaseActivity;->c:Landroidx/databinding/ViewDataBinding;
    check-cast p1, Lcom/mgs/carparking/databinding/ActivityMainBinding;
    iget-object p1, p1, Lcom/mgs/carparking/databinding/ActivityMainBinding;->d:Lcom/mgs/carparking/widgets/tab/TabLayout;
    invoke-virtual {p1, v0}, Lcom/mgs/carparking/widgets/tab/TabLayout;->setCurrentTab(I)V
    :boxoffice_done
    return-void''')
main = re.sub(r'^    invoke-virtual \{p1, p0\}, Lcom/yk/e/MainSDK;->initAdCache\(Landroid/app/Activity;\)V$', '    # BoxOffice: ad cache initialization disabled', main, flags=re.M)
marker = '    # BoxOffice: remove Promotion from the navigation model'
anchor = '    invoke-virtual {v2, v1, v0}, Lcom/mgs/carparking/widgets/tab/TabLayout;->b(Ljava/util/ArrayList;Lcom/mgs/carparking/widgets/tab/TabLayout$a;)V'
if marker not in main:
    if main.count(anchor) != 1: raise RuntimeError('Navigation initialization anchor mismatch')
    main = main.replace(anchor, marker + '\n    const/4 v4, 0x3\n    invoke-virtual {v1, v4}, Ljava/util/ArrayList;->remove(I)Ljava/lang/Object;\n' + anchor)
mine = re.compile(r'(const-class v8, Lcom/mgs/carparking/ui/mine/MineFragment;.*?const/4 v9, )0x4', re.S)
main, mine_changes = mine.subn(r'\g<1>0x3', main)
if mine_changes == 0 and not re.search(r'const-class v8, Lcom/mgs/carparking/ui/mine/MineFragment;.*?const/4 v9, 0x3', main, re.S): raise RuntimeError('Me navigation index anchor missing')
initial = '    invoke-virtual {v3, v1}, Lcom/mgs/carparking/widgets/tab/TabLayout;->setCurrentTab(I)V'
if ':boxoffice_initial_nav' not in main:
    if main.count(initial) != 1: raise RuntimeError('Initial navigation anchor mismatch')
    main = main.replace(initial, '    const/4 v4, 0x4\n    if-ne v1, v4, :boxoffice_initial_nav\n    const/4 v1, 0x3\n    :boxoffice_initial_nav\n' + initial)
main_file.write_text(main)

ANDROID = '{http://schemas.android.com/apk/res/android}'
ET.register_namespace('android', 'http://schemas.android.com/apk/res/android')
ET.register_namespace('app', 'http://schemas.android.com/apk/res-auto')
changed_names = []
for file in (decoded / 'res').glob('values*/strings.xml'):
    tree = ET.parse(file); changed = False
    for item in tree.getroot():
        if item.get('name') in ('app_name', 'text_App_name'):
            item.text = 'BoxOffice'; changed = True
    if changed:
        tree.write(file, encoding='utf-8', xml_declaration=True)
        changed_names.append(str(file.relative_to(decoded)))
for folder, size in [('mdpi',48),('hdpi',72),('xhdpi',96),('xxhdpi',144),('xxxhdpi',192)]:
    for file in (decoded / 'res' / ('mipmap-' + folder)).glob('ic_launcher*'):
        pixels = round(size * 2.25) if 'foreground' in file.name else size
        icon.resize((pixels, pixels), Image.Resampling.LANCZOS).save(file, format='WEBP', lossless=True)
for file in (decoded / 'res').glob('values*/colors.xml'):
    tree = ET.parse(file); changed = False
    for item in tree.getroot():
        if item.get('name') in ('ic_launcher_background', 'ic_splash_color'):
            item.text = '#ff06111b'; changed = True
    if changed: tree.write(file, encoding='utf-8', xml_declaration=True)
for name in ('ic_splash_window_temp.png', 'ic_video_load_first_icon.png'):
    matches = list((decoded / 'res').glob('drawable*/' + name))
    if len(matches) != 1: raise RuntimeError('Unexpected brand image variants: ' + name)
    icon.resize((512,512), Image.Resampling.LANCZOS).save(matches[0], format='PNG')

collapsed = []
for file in (decoded / 'res').glob('layout*/*.xml'):
    tree = ET.parse(file); changed = False
    parents = {child:parent for parent in tree.getroot().iter() for child in parent}
    for item in tree.getroot().iter():
        id_ = item.get(ANDROID + 'id', '').split('/')[-1]
        if id_ in ('vpLayout', 'vipBg', 'video_top_ad'):
            for key,value in [('visibility','gone'),('layout_height','0dp'),('minHeight','0dp'),('padding','0dp'),('paddingTop','0dp'),('paddingBottom','0dp'),('layout_marginTop','0dp'),('layout_marginBottom','0dp')]: item.set(ANDROID+key,value)
            changed = True; collapsed.append(str(file.relative_to(decoded)) + ':' + id_)
        if item.get(ANDROID+'background') == '@drawable/ic_splash_window_temp':
            item.set(ANDROID+'layout_width','144dp'); item.set(ANDROID+'layout_height','144dp'); changed=True
        if item.get(ANDROID+'src') == '@drawable/ic_video_load_first_icon':
            item.set(ANDROID+'layout_width','72dp'); item.set(ANDROID+'layout_height','72dp'); changed=True
        if file.name == 'fragment_mine.xml' and item.get(ANDROID+'text') in ('@string/text_mine_game','@string/str_mine_extension'):
            row=parents[item]
            for key,value in [('visibility','gone'),('layout_height','0dp'),('minHeight','0dp'),('layout_marginTop','0dp'),('layout_marginBottom','0dp')]:row.set(ANDROID+key,value)
            changed=True;collapsed.append(str(file.relative_to(decoded))+':promotional-row')
    if changed: tree.write(file, encoding='utf-8', xml_declaration=True)
manifest_file = decoded / 'AndroidManifest.xml'
tree = ET.parse(manifest_file)
application = tree.getroot().find('application')
removed = []
prefixes = ('com.yk.e.provider.', 'com.yandex.mobile.ads.', 'io.bidmachine.', 'com.google.android.gms.ads.', 'com.ironsource.', 'com.applovin.', 'com.facebook.ads.', 'com.vungle.ads.', 'com.mbridge.msdk.', 'sg.bigo.ads.')
for provider in list(application.findall('provider')):
    name = provider.get(ANDROID+'name', '')
    if name.startswith(prefixes):
        application.remove(provider); removed.append(name)
tree.write(manifest_file, encoding='utf-8', xml_declaration=True)
baseline_application = ET.parse(source / 'AndroidManifest.xml').getroot().find('application')
current_provider_names = {p.get(ANDROID+'name','') for p in application.findall('provider')}
removed = sorted(p.get(ANDROID+'name','') for p in baseline_application.findall('provider') if p.get(ANDROID+'name','').startswith(prefixes) and p.get(ANDROID+'name','') not in current_provider_names)
(root / 'reports/boxoffice-preparation.json').write_text(json.dumps({'brand':'BoxOffice','package_unchanged':'com.fvvcl.flickverse','navigation':['Home','Streaming','Categories','Me'],'ad_init_methods_disabled':init_count,'ad_providers_removed':removed,'collapsed_promotional_views':collapsed,'renamed_string_resources':changed_names,'generated_icon':str(assets/'boxoffice-icon.png')},indent=2))
print('BoxOffice resources and ad-free navigation prepared; removed',len(removed),'ad auto-initializers')
