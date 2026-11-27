# v0.1.0-alpha readiness

Status on 2026-11-27: draft review candidate, not released.

## Approved scope — 2026-11-27

A local monitoring dashboard with classic and retro layouts. CPU, memory, storage, services and available sensor readings can be displayed. Missing readings remain unknown. Optional command diagnostics require explicit configuration. Fan, LED, OLED and backup controls stay unavailable: all four write endpoints deny requests. This is a first monitoring milestone, not a commitment to remove those features from future versions.

## Owner decisions and target platform

The owner approved a monitoring-only first alpha and selected MIT on 2026-11-27. See the repository LICENSE. Authorship and redistribution rights were confirmed by the owner.

Owner-reported platform facts (not independently tested):

| Component | Reported value |
| --- | --- |
| Board | Raspberry Pi 5 Model B Rev 1.1 |
| OS | Debian GNU/Linux 13 |
| Architecture | aarch64 (ARM64) |
| Kernel | 6.12.47+rpt-rpi-2712 |
| Python | 3.13.5 |
| Case | Pironman 5-MAX; additional SSD heatsink |

The Python 3.13 Linux CI job passed, but that does not establish compatibility with this exact Debian/ARM64/kernel combination or real sensors. The owner identified a Pironman 5-MAX case with an added SSD heatsink. Its product description mentions dual NVMe, PWM/RGB fans and a 0.96-inch OLED; installed SSD count, RAID topology, Hailo accelerator presence and controller interfaces are not inferred from that description. No vendor driver is installed or invoked. A second physical server is not required for further mock or virtual-machine tests.

Only these non-identifying platform facts are retained. Do not publish terminal transcripts, network addresses, host/user names, login history, passwords, keys, serial numbers, production configuration or NAS data. No production access is needed for further offline work.

## Release decision: experimental read-only alpha

Physical fan/LED/OLED tests and backup restoration are prerequisites for future enabled features, not blockers for the approved alpha in which those operations are unavailable. Likewise, unverified sensor integration and manual screen-reader coverage must be disclosed; this alpha must not claim certified hardware support, production readiness or full accessibility conformance.

### Required before publication

1. The final candidate must pass all five CI jobs, including pinned dependency installation, `pip check`, the source-ZIP smoke test and the ARM64/Python 3.13.5 suite. Record the exact commit and run in the PR and external validation report.
2. Maintainer review/acceptance of the complete sanitized candidate and draft release notes must be completed. PR #3 is still a draft stacked on intake PR #1; neither has been merged. Complete the reviewed branch integration before tagging a mainline release. Branch API mergeability alone is not evidence of a content conflict; the inspected intake comparison is directly ahead of main.
3. Select the exact approved release commit, regenerate/check the source archive and checksums for that commit, and explicitly authorize publication as a prerelease. A preparation request is not treated as an instruction to merge or publish.

### Completed preparation

Owner-approved read-only scope and MIT; portable configuration; disabled mutation boundaries; dependency inventory and privacy review; Linux x64/ARM64 tests; three-browser fixture checks; automated accessibility and gradient-bound contrast checks; reviewed narrow-screen screenshots; a source-ZIP test outside the checkout; local evaluation/removal instructions; draft release notes. See VALIDATION.md and the PR for commit-specific results.

### Known limitations, not silently waived claims

- Actual Debian 13/Raspberry Pi 5/Pironman sensor integration is unvalidated. Unavailable telemetry stays unknown.
- Manual screen-reader use and full accessibility conformance remain unverified.
- Remote access, production deployment, automated NAS installation/upgrades, hardware controls and backup/restore are outside this release scope.

No additional NAS data, credentials or production access is required to complete these publication steps. The production NAS must remain unchanged.
