# BoxOffice: two-phone request capture

The same diagnostic APK and signing certificate were used on both phones. The observer preserved original requests and responses and redacted private values inside the app.

| Item | SM-M536B (working) | SM-G998B (failing) |
|---|---|---|
| The Paradise | HTTP 200, correct title and media metadata | HTTP 200, title `-`, year `2000`, placeholder media |
| Bigg Boss Season 20 | HTTP 200, correct title and episode metadata; 1080p playback logged | HTTP 200, same placeholder media as Paradise |
| API host, channel, version, catalog IDs, request fields | Match | Match |
| Native timestamp/signature forwarded unchanged | Yes | Yes |

Different actual header values: `androidid`, `device_id`, `gaid`, `token`, `mobmodel`, `sysrelease`, and the expected time-dependent `cur_time` and `sign`. These differences do not by themselves identify the rejection rule.

The certificate is the same on both phones, so the rebuilt certificate alone is not a sufficient explanation. The original non-debuggable APK was not intercepted on the phone; this is a working-versus-failing BoxOffice comparison.

The server returns success status/code while substituting metadata and media. Backend decision logs are still needed to identify why. No permanent playback fix is claimed.

Redacted raw captures: `phone-capture-working-m53.jsonl` and `phone-capture-failing-s21.jsonl`. Machine-readable comparison: `two-phone-request-comparison.json`.
