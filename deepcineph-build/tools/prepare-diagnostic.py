import pathlib,re,json
root=pathlib.Path(__file__).resolve().parents[1]
p=root/'working/sdk-dex/classes3.dex-smali/com/mgs/carparking/app/AppApplication.smali'
s=p.read_text();pattern=r'(\.method public static safedk_AppApplication_onCreate_bbdf4c402a780e2be10909c2ace6b7a9\(Lcom/mgs/carparking/app/AppApplication;\)V\s+\.locals 4)'
s,n=re.subn(pattern,lambda m:m[1]+'\n    const-string v0, "deepcine_observer"\n    invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V\n',s)
assert n==1
(root/'diagnostic/AppApplication.smali').write_text(s)
(root/'diagnostic/libdeepcine_observer.config.so').write_text(json.dumps({'interaction':{'type':'listen','address':'127.0.0.1','port':27046,'on_load':'resume'}}))
