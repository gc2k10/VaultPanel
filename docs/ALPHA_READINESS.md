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

The Python 3.13 Linux CI job passed, but that does not establish compatibility with this exact Debian/ARM64/kernel combination or real sensors. Case/controller model remains unknown; it is useful for future sensor integration, not required for the generic monitoring scope. A second physical server is not required for further mock or virtual-machine tests.

Only these non-identifying platform facts are retained. Do not publish terminal transcripts, network addresses, host/user names, login history, passwords, keys, serial numbers, production configuration or NAS data. No production access is needed for further offline work.

## Validation still required

- Continue Linux virtual-machine and synthetic-fixture checks without production access. Mocked Linux CI does not validate real sensors, permissions or vendor output; clearly disclose this limitation for the read-only alpha. Hardware-specific validation must not be claimed without evidence.
- Manually assess unresolved contrast checks and screen-reader use; automated accessibility tests are not WCAG certification.
- Review the candidate and choose an explicit version/tag only after agreed release gates pass. No release tag or GitHub Release exists as a result of this work.
- Before future hardware controls: validate failure-safe behavior, permissions, thermal limits and controller ownership on disposable hardware. Before any backup claim: implement and test restoration. These features must not be advertised as working in the proposed read-only alpha.

The production NAS must remain unchanged. No deployment or production connection is part of these checks.
