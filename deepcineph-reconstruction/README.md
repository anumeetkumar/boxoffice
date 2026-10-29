# DeepCine APK extraction

Original APK: `../deepcineph.apk` (unchanged).
SHA-256: `788e45abd4c315e5d2cb51319eae1ba92d8d796e24f4364314df334d636f8600`.

Package `com.velvetreel.shorttv`, version 4.0.0 (40000); minimum API 24, target API 35.

## Extracted output

- `jadx-export/sources/`: 42,365 decompiled Java files, including 1,026 files in the application namespaces.
- `apktool/`: decoded manifest, resources, assets, original DEX and native libraries; Apktool 3.0.3, no source disassembly.
- `raw-apk/`: all 3,747 original archive files, verified byte-for-byte. 848 Windows case collisions were preserved under remapped paths documented in `raw-file-map.json`.
- `source-index.json`: generated source file sizes, hashes and error markers.
- `decompilation-limitations.json`: 106 files containing explicit error/stub markers; 139 unsupported-method stubs. Unmarked code can still be inaccurate.
- `api-routes.json`, `api-interface-candidates.json`, `url-candidates.json`: static network declarations and literal URL candidates, not tested endpoints.
- `native-inventory.json`: 32 retained native libraries, ELF metadata, dependencies and exported symbols. Native implementations have not been recovered as C/C++ source.
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
