# Two-phone playback comparison — 2026-10-26

No permanent playback fix was verified.

Both phones ran the same temporary diagnostic BoxOffice APK. This was not a direct instrumented capture of the untouched original APK.

| Test | SM-G998B (S21) | SM-M536B (M53) |
| --- | --- | --- |
| Genuine playback metadata | Replacement title `-` | The Paradise |
| Common PC API network route | Replacement title `-` | The Paradise |
| Normal original-client session bootstrap | HTTP 200; playback unchanged | HTTP 200; playback unchanged |
| Session token before/after bootstrap | Unchanged (redacted comparison) | Unchanged (redacted comparison) |
| Native configuration | Same configuration on both phones; unchanged after refresh | Same configuration on both phones; unchanged after refresh |
| Native SDK with identical synthetic local input and timestamp | Identical output on both phones | Identical output on both phones |

Synthetic native test outputs were not submitted to the backend. Real device identities and sessions were retained for API tests; no token or identifier was transplanted. The common network tunnel preserved end-to-end TLS.

Prior model/OS header overrides also failed. Correct forwarding of native proof does not establish that the backend accepts that proof for a particular identity. These results reduce support for missing fields, model/OS text, network egress alone, or a different native algorithm as the sole cause. Backend identity/session validation remains unresolved; provider-side decision logs are required to establish the actual reason.

Evidence: `two-phone-native-controlled-input.json`, `common-route-s21.jsonl`, `common-route-m53.jsonl`, `session-refresh-s21.jsonl`, `session-refresh-m53.jsonl`, and `two-phone-request-comparison.md`. Private values are redacted.
