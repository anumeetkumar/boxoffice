import json,pathlib,hashlib
root=pathlib.Path(__file__).parent
load=lambda name:json.loads((root/name).read_text(encoding='utf-8-sig'))
raw=load('raw-verification.json'); pkg=load('package-summary.json'); bulk=load('jadx-export/export-result.json'); index=load('source-index.json'); limits=load('decompilation-limitations.json'); routes=load('api-routes.json'); native=load('native-inventory.json')
summary={'apk':'deepcineph.apk','sha256':raw['apk_sha256'],'package':pkg['package_name'],'version':pkg['version_name'],'min_sdk':pkg['min_sdk'],'target_sdk':pkg['target_sdk'],'java_files':len(index),'java_bytes':sum(x['bytes'] for x in index),'application_java_files':sum(x['application'] for x in index),'files_with_error_markers':len(limits),'method_not_decompiled_stubs':sum(x['method_not_decompiled_stubs'] for x in index),'raw_verification':raw,'native_libraries':len(native),'api_route_declarations':len(routes),'bulk_export':bulk,'runtime_tested':False,'source_build_verified':False}
(root/'summary.json').write_text(json.dumps(summary,indent=2))
readme=f'''# DeepCine APK extraction

Original APK: `../deepcineph.apk` (unchanged).
SHA-256: `{raw['apk_sha256']}`.

Package `{pkg['package_name']}`, version {pkg['version_name']} ({pkg['version_code']}); minimum API {pkg['min_sdk']}, target API {pkg['target_sdk']}.

## Extracted output

- `jadx-export/sources/`: {len(index):,} decompiled Java files, including {summary['application_java_files']:,} files in the application namespaces.
- `apktool/`: decoded manifest, resources, assets, original DEX and native libraries; Apktool 3.0.3, no source disassembly.
- `raw-apk/`: all {raw['files_verified']:,} original archive files, verified byte-for-byte. {raw['case_collision_remaps']} Windows case collisions were preserved under remapped paths documented in `raw-file-map.json`.
- `source-index.json`: generated source file sizes, hashes and error markers.
- `decompilation-limitations.json`: {len(limits)} files containing explicit error/stub markers; {summary['method_not_decompiled_stubs']} unsupported-method stubs. Unmarked code can still be inaccurate.
- `api-routes.json`, `api-interface-candidates.json`, `url-candidates.json`: static network declarations and literal URL candidates, not tested endpoints.
- `native-inventory.json`: {len(native)} retained native libraries, ELF metadata, dependencies and exported symbols. Native implementations have not been recovered as C/C++ source.
- `package-evidence-retry.json`: successful REA inspect_android_package Evidence. The first attempt failed on temporary-directory permissions; its output is retained separately.
- `signature-verification.txt`: executed APK signature verification.
- `summary.json`, `raw-verification.json`: counts, provenance and integrity results.

## Start reviewing

- `jadx-export/sources/com/mgs/carparking/app/AppApplication.java`
- `jadx-export/sources/com/mgs/carparking/app/BrowserApiService.java`
- `jadx-export/sources/com/mgs/carparking/app/HttpsUtils.java`
- `jadx-export/sources/com/mgs/carparking/ui/MainActivity.java`
- `jadx-export/sources/com/mgs/carparking/ui/VideoPlayDetailActivity.java`

The app label is DeepCine. It uses Android views and application classes under `com.mgs.carparking`; this is a source observation, not proof of identical behavior to Movie. The static default API URL in HttpsUtils is `https://velvetreel.7nkznc.com/`; runtime configuration may replace it. No request was sent to that server during extraction.

## Limits and reproducibility

This is recovered decompiled code, not the original project source. Original comments, exact variable names, Gradle dependency graph, private signing key, server source and native C/C++ source are not recovered. No source build, APK modification, installation, or runtime verification was performed.

REA used its configured JADX headless 0.7.1 engine for package Evidence. Supplemental `BulkExport.java` used the same JAR, one worker, automatic deobfuscation off, inconsistent code retained, and class unloading between exports. Logs and the helper scripts are included. The exporter reports suppressed/empty generated classes separately; inner/synthetic classes mean class inventory counts and Java file counts differ. Raw DEX remains available for every unrecovered method.
'''
(root/'README.md').write_text(readme)
print(json.dumps(summary,indent=2))
