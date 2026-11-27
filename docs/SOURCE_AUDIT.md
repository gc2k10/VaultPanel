> Historical intake evidence. The alpha runtime is now at the repository root. The earlier `vaultpanel/` runtime and executable hardware scripts were removed from the release tree during integration; reference units are not installable. Current behavior is documented in CONFIGURATION.md and INSTALLATION.md.

# Recovered-source audit — 2026-11-26

## Intake evidence

The operator confirmed an active VaultPanel service with working directory `/opt/vaultpanel`, then copied an explicit selection of 24 text files into private staging. No server access was assumed or used by this audit. Two other source locations were listed by the operator but were not imported or compared. The supplied selection includes Python backend/collectors, two frontends, shell adapters and OLED code. Original files remain unchanged in private staging and on the device.

The owner confirmed original/generated-for-owner provenance and authorized MIT. No images, credentials, runtime data, backups, virtual environments, service units or private Git history were imported. A private inventory of source hashes is retained outside the repository.

## Privacy review

The 18 initial scanner findings were manually inspected. Token matches were parser variable names used to process SMART output, not access tokens. Address matches were wildcard/loopback listeners and a public connectivity probe. The README URL was an illustrative device URL. No literal credential was identified in the 24 supplied files; this is not a guarantee for missing files or the running service environment.

The public copy removes the device nickname, deployment-specific README instructions and references to unavailable frontend logos. A later [asset review](ASSETS.md) includes seven authorized images with sensitive-capable metadata removed; one personal OLED logo remains excluded. Runtime diagnostics can still contain hostnames and network information: authentication does not make screenshots or exported API responses suitable for public sharing.

The repository scanner flags expected public/loopback URLs, authentication code and date strings that resemble IPv6. These require manual classification; a zero-finding claim is not made for the imported source. The known private device addresses and local account paths were checked separately and were not found in the publication candidate.

## Changes applied to the publication copy

| Finding | Change | Verification |
| --- | --- | --- |
| Unauthenticated API and wildcard listener | Password required for every route; loopback bind and host allowlist; no forwarded-header trust | Authorized/unauthorized and rebinding-host tests |
| Privileged POST actions | Reject all write methods; no web enable switch; disable related controls in both UIs | Tests assert no helper or backup process is invoked |
| Destructive backup retention | Replace backup entry point with an explicit refusal; original retained privately | Disabled-script test |
| Raw values interpolated into HTML | Escaping template tag and validated color values; CSP | Escaping and frontend syntax tests |
| Missing psutil dependency | Declare core and separate optional hardware dependencies | Import and API tests |
| Failed command output treated as data | Noninteractive sudo and empty result on command failure | Failure-path test |
| Empty BTRFS output could look healthy | Health remains unverified rather than inferred from missing errors | Missing-output test |
| Incidental OK text in SMART output | Remove broad substring success test | Regression test |
| Duplicate fan function | Keep one identical implementation | Python import/syntax checks |
| GET requests append history indefinitely | Read-only response history, capped at 200 entries, no persistence | No-write test |
| Accidental hardware script execution | Explicit opt-in gate before shell/Python hardware work | Disabled-script tests |
| Arbitrary PWM argument interpolated into privileged shell | Require numeric range; missing temperature refuses AUTO action | Static review; hardware remains untested |
| Claimed Nextcloud success on OLED | Replace hardcoded success with UNVERIFIED | Static review |

## Outstanding release blockers

- Topology is now documented in [storage evidence](STORAGE_AUDIT.md): BTRFS on mdraid RAID1. `api/system.sh` assumes mdraid and reads external status files; its SMART/RAID summaries must not be used as authoritative health evidence.
- Service and timer definitions were subsequently reviewed; see [service audit](SERVICE_AUDIT.md). Selected cron jobs, sudo rules and proxy configuration have since been reviewed in [configuration audit](CONFIGURATION_AUDIT.md). Effective runtime policy, complete proxy includes and actual package versions are still needed. Do not publish Environment values or raw command-line secrets.
- The recovered LED alert script feeds both a heredoc and a JSON pipe into stdin; parsing needs repair. Other LED variants search history as well as current alerts. All remain gated; they are not advertised as validated automation.
- Fixed hwmon/device identifiers, mutable `/tmp` state, vendor restart behavior, privileged shell use and service failure handling need device-specific redesign before any hardware support is enabled. Gates are not a substitute for those fixes.
- Collector errors, slow synchronous probes, mount assumptions and platform-specific diagnostics need target-system tests. External network probes remain in the recovered collectors.
- No production authentication/session design, rate limiting, audited privilege broker, backup restore test, UPS implementation, NAS installer or container deployment is provided.
- OLED state configuration and several integration configurations are missing. Seven graphics have since been reviewed; the personal OLED logo remains excluded by owner request. Optional hardware dependency licenses and a target-platform dependency lock/vulnerability review remain pending.
- Historical public commit metadata remains unchanged. The new source import must use the owner's noreply identity.

## Validation scope

Automated tests exercise Flask request boundaries and templates with collectors mocked, HTML escaping, source export safety, missing diagnostic behavior and disabled adapters. Python/JavaScript/shell syntax checks do not execute the device integrations. Tests ran locally on macOS; no hardware, live NAS or production service was modified. Visual browser/device acceptance testing remains outstanding.
