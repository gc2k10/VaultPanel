# v0.1.0-alpha — experimental read-only dashboard

Publication is gated on final main-branch tests; the GitHub prerelease records the exact source commit and validation run.

VaultPanel's first alpha is an experimental local monitoring dashboard with classic and retro layouts, licensed under MIT. It displays available CPU, memory, storage and configured service telemetry. Unknown or unavailable data stays explicitly unknown.

## Included

- Portable environment configuration and pinned application dependencies.
- Loopback access restrictions, optional local authentication and generic API error responses.
- Read-only defaults, bounded optional diagnostic/state reads and escaped browser content.
- Keyboard navigation, narrow-screen fixes, telemetry failure/timeout recovery and tests on Linux x64/ARM64.

## Deliberately unavailable

Fan, LED, OLED and backup controls are disabled with no runtime switch to enable them. No RAID/storage provisioning, NAS installer, vendor driver, remote access setup or production upgrade is supplied. Snapshot names are not backup evidence.

## Known limitations

- The exact Debian 13/Raspberry Pi 5/Pironman 5-MAX sensor configuration has not been tested. ARM64 CI is not physical hardware certification.
- Manual screen-reader use and full accessibility conformance remain unverified; automated accessibility and controlled gradient-contrast checks are documented separately.
- The Flask development server is for local evaluation only. Do not expose it via network proxies/tunnels.
- No production deployment, hardware safety, backup/restore or data durability claim is made.

Use the reviewed source archive and [local evaluation guide](INSTALLATION.md). Report issues without credentials, host identifiers, personal configuration or raw NAS logs.

The existing standalone synthetic demo, seven reviewed owner-approved graphics, and sanitized service/configuration/storage audit evidence are retained. Historical hardware scripts are not executable components of this alpha. UPS is excluded.
