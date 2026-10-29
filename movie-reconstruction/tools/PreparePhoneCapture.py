import pathlib,shutil,json,re
root=pathlib.Path(__file__).resolve().parent.parent
work=root/'boxoffice/phone-capture';work.mkdir(exist_ok=True)
smali=work/'smali5'
if not smali.exists():shutil.copytree(root/'boxoffice/smali5',smali)
file=smali/'com/mgs/carparking/app/AppApplication.smali'
text=file.read_text()
marker='    # Temporary user-requested network observer'
if marker not in text:
    pattern=r'(\.method public static safedk_AppApplication_onCreate_bbdf4c402a780e2be10909c2ace6b7a9\(Lcom/mgs/carparking/app/AppApplication;\)V\s+\.locals 6)'
    addition='\n'+marker+'\n    const-string v0, "boxoffice_observer"\n    invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V\n'
    text,count=re.subn(pattern,lambda m:m[1]+addition,text)
    if count!=1:raise RuntimeError('Observer initialization anchor mismatch')
    file.write_text(text)
(work/'libboxoffice_observer.config.so').write_text(json.dumps({'interaction':{'type':'listen','address':'127.0.0.1','port':27042,'on_load':'resume'}}))
print('Prepared temporary same-signer phone diagnostic variant')
