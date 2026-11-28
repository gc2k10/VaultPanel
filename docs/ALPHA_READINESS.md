# v0.1.0-alpha readiness

Status on 2026-11-28: [v0.1.0-alpha was published as a prerelease](https://github.com/gc2k10/VaultPanel/releases/tag/v0.1.0-alpha) from `eecca724e84825bb37e4e7c141c990a48b8de1da`. [Final publication checks passed](https://github.com/gc2k10/VaultPanel/actions/runs/46084341766); the release includes the source archive, source commit and checksums. PRs #1, #3 and #5 were merged before publication.

Mainline follow-up work, including original-interface previews and optional mdraid membership, is separate from that fixed release archive. No subsequent release is claimed here. The live NAS has not been accessed or modified.

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

### Completed publication gates

The approved read-only scope and MIT license were applied. The final candidate passed dependency, source-ZIP, Linux x64/ARM64, JavaScript, browser and automated accessibility checks. The owner authorized merge and publication; sanitized source integration was completed. The release archive was checked against the selected commit before publication. See the release and workflow links above for the fixed historical evidence.

### Gates for a future release

Choose an explicit version and final commit; validate that combined tree; review the changed behavior and limitations; regenerate and verify its archive/checksums. Passing tests or merging a follow-up PR does not itself publish a new version or validate physical sensors.

### Completed preparation

Owner-approved read-only scope and MIT; portable configuration; disabled mutation boundaries; dependency inventory and privacy review; Linux x64/ARM64 tests; three-browser fixture checks; automated accessibility and gradient-bound contrast checks; reviewed narrow-screen screenshots; a source-ZIP test outside the checkout; local evaluation/removal instructions; draft release notes. See VALIDATION.md and the PR for commit-specific results.

### Known limitations, not silently waived claims

- Actual Debian 13/Raspberry Pi 5/Pironman sensor integration is unvalidated. Unavailable telemetry stays unknown.
- Manual screen-reader use and full accessibility conformance remain unverified.
- Remote access, production deployment, automated NAS installation/upgrades, hardware controls and backup/restore are outside this release scope.

No additional NAS data, credentials or production access is required to complete these publication steps. The production NAS must remain unchanged.

## Publication authorization — 2026-11-28

The owner explicitly authorized merging PR #1/#3 and publishing v0.1.0-alpha as a prerelease after final tests. Integration also reconciles the pre-existing standalone demo on main. Publication is automated only for the main branch after application and demo checks; no NAS deployment is included. GitHub Releases and its linked validation run are authoritative for publication status.
