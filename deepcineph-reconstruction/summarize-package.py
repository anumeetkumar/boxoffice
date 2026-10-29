import json,pathlib,hashlib
root=pathlib.Path(__file__).parent
pkg=json.loads((root/'package-evidence-retry.json').read_text(encoding='utf-8-sig'))
r=pkg['normalized_result']
(root/'package-summary.json').write_text(json.dumps({k:v for k,v in r.items() if k not in ['manifest','manifest_xml']},indent=2))
print(list(r.keys()))
