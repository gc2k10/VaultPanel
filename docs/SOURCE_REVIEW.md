# Production-source review

Reviewed 24 UTF-8 source files from the private archive, without executing any archived code. Archive entries were validated before copying: regular files/directories only, no links or special files, no absolute/traversal paths or duplicate normalized paths, bounded file count and total size. Ownership, executable bits and timestamps were not restored. Raw material remains outside the repository.

No explicit password, API key or private key was found in this bounded manual review. This is not proof that all possible secrets are absent. The intake heuristic scanner produced 18 findings in the original: local/example URLs, public probe addresses, and timestamp expressions misclassified as IPv6. SMART `token` variables are parsing variables, not credentials. A deployment hostname, service inventory, storage/device assumptions and installation paths were removed or made configurable. No original Git history or binary assets were supplied.

## File-by-file disposition

| Original file | Review and disposition |
| --- | --- |
| `app.py` | Four unauthenticated mutation routes, broad bind, exception detail exposure, GET history writes, unbounded script call. Replaced route wiring with loopback-only read routes, optional authentication, security headers and disabled writes. |
| `collectors.py` | Generic shell runner, sudo, hardcoded deployment details, ambiguous health parsing, duplicate fan implementation. Retained/refactored telemetry, portable settings, strict command boundary, no writable adapters. |
| `requirements.txt` | Imported psutil missing. Added explicit Flask and psutil dependency ranges. |
| `README.md` | Stale port and hardware adapter claims, installation-specific service example. Replaced with English review instructions and limits. |
| `backup.sh` | Archives application and system configuration, deletes old backups, writes success marker without robust success handling. Excluded; backup endpoint disabled. |
| `api/system.sh` | Deployment-specific storage paths, fixed two-disk parsing, missing data reported as failure. Excluded; endpoint now JSON telemetry. |
| `scripts/oled_mode.sh` | Starts/stops service with sudo; AUTO stop failures ignored. Excluded. |
| `scripts/pironman_fans.sh` | Fixed hwmon/PWM paths, sudo shell writes, missing temperatures treated as zero, unchecked direct MANUAL argument. Excluded. |
| `scripts/pironman_led.sh` | Privileged vendor CLI and daemon restart, no independent range validation. Excluded. |
| `scripts/pironman_oled_mode.sh` | Conflicting pair of services, errors suppressed. Excluded. |
| `scripts/vaultpanel_auto_fans.sh` | Temporary state file and fixed script path, errors suppressed. Excluded. |
| `scripts/vaultpanel_led_alert.sh` | Shell heredoc consumes Python stdin instead of piped JSON; fixed state and privileged adapter. Excluded. |
| `scripts/vaultpanel_led_alert_hourly.sh` | Text matching can react to historical alerts; fixed adapter path. Excluded. |
| `scripts/vaultpanel_led_auto.sh` | Deployment schedule and broad alert matching; direct vendor command. Excluded. |
| `scripts/vaultpanel_led_schedule.sh` | Deployment-specific time/color schedule. Excluded. |
| `scripts/vaultpanel_oled.py` | Initializes I2C at import, fixed storage/config/logo paths, synthetic service OK text. Excluded. |
| `scripts/vaultpanel_oled_custom.py` | Initializes I2C at import, fixed paths and shell commands. Excluded. |
| `static/css/style.css` | Read completely; no credentials, external URLs or admin code. Retained styling. |
| `static/css/style_retro.css` | Read completely; no credentials, external URLs or admin code. Retained styling. |
| `static/js/app.js` | Unescaped HTML interpolation, mutation controls and ignored HTTP failures. Escaped dynamic HTML, disabled controls, HTTP error handling, unknown network state. |
| `static/js/app_retro.js` | Same HTML risk, hardcoded host and two device identifiers, optimistic backup success. Sanitized identifiers and device selection, escaped dynamic HTML, disabled controls, HTTP failures rejected. |
| `static/site.webmanifest` | Referenced missing icons. Replaced with generic manifest without absent assets. |
| `templates/index.html` | Read completely; controls exposed without capability gating. Preserved layout, added disabled controls/read-only notice and escaping helper. |
| `templates/index_retro.html` | Same controls, fixed disk/storage labels and missing icons/logo references. Generic labels, disabled controls, absent asset references removed. |

## Fan semantics

The two original `apply_fan_profile` definitions have identical ASTs; the second overrides the first without changing behavior. Both accepted AUTO/SILENT/BALANCED/PERFORMANCE/MANUAL, wrote requested state before execution, ignored script failure, and could claim success when no script existed. Neither passed a manual PWM value. The shell adapter mapped SILENT/BALANCED/PERFORMANCE to 90/140/220, AUTO to disk-temperature thresholds and MANUAL to a default of 140. Unknown disk temperature selected the lowest AUTO tier. Simply deleting the duplicate would preserve these safety defects.

There is now one function delegating to a disabled operation result. No fan curve or hardware behavior is claimed validated. Reintroducing fan writes requires verified sensor-loss behavior and a thermal safety design on disposable hardware.

## Remaining risks

Broad exception handling in inherited collectors can conceal diagnostics; missing values are generally shown as unknown. Follow-up work caps subprocess output at 64 KiB and optional state files at 4 KiB, rejects non-regular/symlink state files and validates known fields. Reads are not cached; diagnostic cost and rate limits remain open. The loopback guard is not a multi-user security boundary; use the optional password for local confidentiality. A dated dependency vulnerability check and installed wheel license inventory are now available in VALIDATION.md. Independent source scanning has been performed (see VALIDATION.md); no private Git history was imported or audited. The owner attested to application/design rights; the owner selected MIT on 2026-11-27; see LICENSING.md. No original hardware scripts or personal deployment settings are published by this change.
