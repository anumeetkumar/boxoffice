import json, pathlib, statistics
root = pathlib.Path(__file__).resolve().parent.parent
def summarize(name):
    events = []
    for line in (root / 'reports' / name).read_text().splitlines():
        message = json.loads(line)
        if message.get('type') == 'send': events.append(message['payload'])
    opens = [e for e in events if e.get('event') == 'source.open']
    errors = [e for e in events if e.get('event') == 'source.error']
    return {'locations': [json.loads(s) for s in sorted({json.dumps(e['location'], sort_keys=True) for e in opens})],
            'observed_open_attempts': len(opens), 'observed_open_errors': len(errors),
            'mean_failed_open_ms': round(statistics.mean(e['elapsed_ms'] for e in errors)) if errors else None}
original = summarize('streams-original-bigg20.jsonl')
rebuilt = summarize('streams-fixed-bigg20-verified.jsonl')
report = {'tested_item': 'Bigg Boss Season 20 Episode 1', 'catalog_id': 592351,
          'environment': 'same isolated emulator and host network; sequential installations',
          'instrumentation': 'read-only Java data-source observation, original return values and exceptions preserved',
          'original': original, 'rebuilt': rebuilt,
          'same_stream_resource': original['locations'] == rebuilt['locations'],
          'both_observed_http_open_failure': original['observed_open_errors'] > 0 and rebuilt['observed_open_errors'] > 0,
          'pc_bounded_origin_http_probe_status': 403, 'pc_bounded_origin_https_probe_status': 403,
          'phone_origin_status_proven': False, 'phone_original_comparison_completed': False,
          'streaming_issue_fixed': False}
(root / 'reports/streaming-comparison.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
