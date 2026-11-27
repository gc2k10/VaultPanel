# Architecture and hardware boundaries

## Implemented read-only candidate

Browser (classic or retro layout) -> local Flask API -> collectors -> psutil, bounded state-file reads and optional allowlisted diagnostic commands.

The application binds to loopback and enforces loopback client/Host guards. Optional local authentication and response security headers are implemented. No proxy headers are trusted. Deployment for remote access is outside this candidate's scope.

Command diagnostics default to disabled. Configured reads use a fixed allowlist, no shell or sudo, a timeout and bounded output. State-file reads use regular files with size/schema checks. The API does not persist alert history on GET. All four write endpoints (backup, fan, LED, OLED) return HTTP 403; direct mutation adapters also deny operations. There is no switch to enable writes.

## Hardware evidence

The owner reports Raspberry Pi 5 Model B Rev 1.1, Debian 13 ARM64, Python 3.13.5 and a Pironman 5-MAX case with an extra SSD heatsink. The product description lists dual NVMe, PWM cooling, RGB fans and a 0.96-inch OLED. This does not establish installed SSD count, RAID topology, Hailo presence, GPIO wiring, vendor driver versions or verified sensor paths.

No vendor controller code, GPIO library, privileged helper, service unit or production configuration is installed by this review. All production hardware scripts were excluded. Thermal safety continues to depend on the existing independent cooling setup; VaultPanel does not replace it.

## Evidence boundaries

- Synthetic fixtures exercise the API and both layouts without contacting hardware.
- Python tests cover disabled writes, parsing, configuration, authentication and bounded reads.
- Linux ARM64 CI with Python 3.13.5 is configured separately from the x64 matrix. It tests application portability, not a Raspberry Pi kernel, Debian image or physical case.
- Real sensor integration remains unvalidated. Missing readings must remain unknown.
- Snapshot names and RAID status do not prove backups. Backup/restore and future hardware controls require separate design and validation before implementation.

Third-party services are not bundled merely because their names appear in documentation. License and configuration review must precede any new integration.
