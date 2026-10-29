import pathlib,re,shutil,json
root=pathlib.Path(__file__).resolve().parents[1]
source=root/'working/sdk-dex/classes3.dex-smali/com/mgs/carparking/app/AppApplication.smali'
s=source.read_text(encoding='utf-8')
# Change the existing first-run default branch, after VCUtils.e(context). Never read prefs before initialization.
pattern=r'    invoke-static \{\}, Lme/goldze/mvvmhabit/utils/VCUtils;->d\(\)Ljava/lang/String;\s+\.line 13\s+    move-result-object v0'
s,n=re.subn(pattern,'    const-string v0, "en"',s);assert n==1,'Default-language anchor mismatch'
method=s[s.index('.method public static safedk_AppApplication_onCreate_'):]
assert method.index('Lme/goldze/mvvmhabit/utils/VCUtils;->e(Landroid/content/Context;)V')<method.index('const-string v0, "en"')
assert '# Default only an unset' not in s
(root/'ready/AppApplication.smali').write_text(s,encoding='utf-8')
source=root/'working/apktool';dest=root/'ready/apktool'
if not dest.exists():shutil.copytree(source,dest,ignore=shutil.ignore_patterns('build','dist'))
(root/'reports/ready-startup-fix.json').write_text(json.dumps({'cause':'English-default preference read ran before VCUtils context initialization','fix':'Replace device-locale default in the existing first-run branch after VCUtils.e(context); preserve saved-language branch','context_before_default_verified':True,'extra_early_preference_reads':False},indent=2),encoding='utf-8')
print('Prepared lifecycle-safe English default using original first-run branch')
