# Configuration and API contract

Environment variables are read once at startup. Restart after changing them. There is no automatic `.env` loading and no configuration endpoint. Keep private values outside Git.

| Variable | Default | Meaning |
| --- | --- | --- |
| `VAULTPANEL_STORAGE_MOUNT` | `/` | Filesystem to display; use an absolute path |
| `VAULTPANEL_SNAPSHOT_DIR` | empty | Optional directory to list; disabled when empty |
| `VAULTPANEL_STATE_DIR` | `state` | Optional existing state files to read; never created or written |
| `VAULTPANEL_SMART_DEVICES` | empty | Comma-separated explicit `/dev/` device paths; SMART reads restricted to these |
| `VAULTPANEL_SERVICES` | `[]` | JSON list of service objects with `name` and exactly one of `systemd` or `docker`; optional `port` |
| `VAULTPANEL_MDRAID_READS` | `false` | Independent opt-in to read the fixed `/proc/mdstat` file; no commands or writes |
| `VAULTPANEL_COMMAND_READS` | `false` | Explicit opt-in for allowlisted diagnostic subprocesses |
| `VAULTPANEL_PING_TARGET` | empty | Optional connectivity target; no probe without a value and command opt-in |
| `VAULTPANEL_DNS_TARGET` | empty | Optional DNS target, also requires command opt-in |
| `VAULTPANEL_ACCESS_TOKEN` | empty | Optional Basic authentication password; browser username is not used |

Service example: `[{"name":"Example service","systemd":"example.service","port":null}]`. Do not include production configuration in a public PR. An empty services list is valid.

The application always limits requests to loopback clients and loopback Host values, including when loaded by another WSGI server. It does not trust forwarded headers. Authentication is optional for local evaluation; local processes can read telemetry when it is unset. Do not expose the application through a proxy or tunnel. Such deployment requires a separate authentication/TLS and proxy trust review.

Optional diagnostics invoke only enumerated read operations, with argument lists, timeouts and `shell=False`. There is no `sudo`. Output is limited to 64 KiB and stderr is discarded. Missing permissions/tools return unavailable telemetry; do not grant root, Docker socket access or broad sudo permissions to make a display green. Docker reads require high-trust access and are not enabled by default. System utilities are resolved using the operator's PATH; use a trusted PATH in any future deployment.

## Routes

- `GET /`, `/retro`: preserved layouts, disabled administration buttons, read-only notice.
- `GET /api/overview`, `/api/cooling`, `/api/storage`, `/api/services`, `/api/network`: telemetry.
- `GET /api/alerts`: current alerts and an empty history list. No persistence as a side effect of a GET.
- `GET /api/system`: now JSON overview data; the old plain-text shell-script contract is removed. Neither supplied frontend uses that old endpoint.
- `GET /api/capabilities`: explicit read-only capability flags.
- `POST /api/backup`, `/api/led`, `/api/fans`, `/api/oled`: always HTTP 403 and `ok: false`, including malformed input. No runtime switch enables writes.

Unavailable network probes and Btrfs data are reported as unknown instead of false success. SMART health is not a historical self-test result: `last_smart_test` is a retained compatibility field carrying current aggregate health. Snapshot names and legacy marker files are not evidence of a successful, restorable backup; both backup fields now stay unavailable. Hardware controls need a separately reviewed adapter, input schemas, authorization, CSRF protection, failure reporting, concurrency control and disposable-device validation before reintroduction.

Optional local state reads are restricted to regular, non-symlink files of at most 4 KiB, with a fixed schema for LED/fan JSON values. Parent directories must remain trusted. Missing LED/fan values are unknown, never synthetic success.

Btrfs is marked healthy only with recognizable filesystem output and an explicitly completed, error-free scrub; missing or ambiguous evidence stays unknown. This is a conservative display heuristic, not a filesystem integrity guarantee.

A service with unavailable diagnostics is reported as `active: null` and displayed as UNKNOWN. Recognized systemd inactive/failed states remain explicit. Empty or unavailable Docker output is treated conservatively as unknown.

## RAID membership (follow-up branch; not in v0.1.0-alpha)

`GET /api/storage` adds `mdraid: {available, arrays}`. Reads are disabled by default, independent of command diagnostics. When explicitly enabled, the adapter reads at most 64 KiB plus an overflow byte from the fixed `/proc/mdstat` path. Missing files, permissions, invalid UTF-8 or excess output remain unavailable. No device names, UUIDs or raw input are returned; no `mdadm`, sudo or repair commands are invoked.

The two layouts display UNKNOWN, DEGRADED, BUSY or MEMBERS PRESENT from this evidence alone. All recognized arrays must have consistent active RAID1 membership with at least two members for MEMBERS PRESENT. This does not establish filesystem integrity, durability, backups or which array backs the configured mount. An unsupported array keeps the combined display unknown; degraded evidence takes priority. BTRFS scrub results remain separate. No NAS configuration is necessary for offline tests or the public synthetic demo.
