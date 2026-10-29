# Re-review of the extracted original code

## Findings

1. The native verification algorithm is not implemented in recovered Java. `com.pp.hls.load` and `exec` are native declarations, with a protected native library resolved by `pp_hlsProtected`. Java request equivalence and successful localhost port initialization do not prove backend validity of a generated proof.

2. Native initialization consumes a cached, server-supplied `p2p_config`: `sa.o0.J()` reads `KEY_PREF_PUBLICSYSCONF_STRING`; `sa.c.h(true)` fetches the configuration and reloads the SDK. HomePageViewModel normally fetches it only when empty. This provided a legitimate client-side hypothesis to test.

3. The original client forwards the localhost verification response without validating its semantic correctness. It treats a backend success code and a non-null detail result as playable metadata; the substitution therefore appears inside the ordinary player. Payload validation could improve reporting but would not recover the requested video.

4. Registration uses cached device identity plus `is_install`, derived from an external DCIM `isSimple.txt` marker. Such a marker can survive uninstall, so uninstall is not a proof that every installation input resets. The marker was not found (or not accessible) during the read-only ADB check on S21; no marker or identifier was changed.

## Test performed

The S21 fetched genuine server P2P configuration through the original `sa.c.h(true)` method. Native SDK reload returned port 7000. Subsequent timestamp/native-proof requests still received title `-` and year `2000`. No identity, credential, model, OS or certificate override was used in this test.

See `phone-sdk-refresh-summary.json` and the HMAC-redacted `phone-sdk-refresh-test.jsonl`.

## Limits

No permanent playback fix is verified. The remaining native proof-generation behavior and server-side validation/decision are not established by the Java code. The earlier claim that all meaningful behavior was covered by matching Java classes was too broad; it covered request-generation code, not native proof validity or server acceptance.
