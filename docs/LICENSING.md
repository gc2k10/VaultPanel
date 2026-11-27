# Licensing and dependencies

The owner confirmed that the supplied VaultPanel source is original or generated for them and explicitly authorized MIT on 2026-11-26. The repository LICENSE applies to original project code, documentation and preparation tools. On 2026-11-28 the owner also authorized MIT/public distribution for seven supplied graphics; one personal OLED logo was explicitly excluded. See [asset review](ASSETS.md). No vendor driver source is bundled.

## Tested dependency inventory

The following versions were installed from PyPI in an isolated macOS/Python 3.9.6 test environment. License information was inspected from the installed distribution metadata and license files. This is a test inventory, not a vulnerability scan or a portable lockfile.

| Distribution | Tested version | License |
| --- | --- | --- |
| Flask | 3.1.3 | BSD-3-Clause |
| psutil | 7.2.2 | BSD-3-Clause |
| Werkzeug | 3.1.9 | BSD-3-Clause |
| Jinja2 | 3.1.6 | BSD-3-Clause |
| MarkupSafe | 3.0.4 | BSD-3-Clause |
| itsdangerous | 2.2.0 | BSD-3-Clause |
| click | 8.1.8 | BSD-3-Clause |
| blinker | 1.9.0 | MIT |
| importlib-metadata | 8.7.1 | Apache-2.0 |
| zipp | 3.23.1 | MIT |

The application requirements declare Flask and the previously missing psutil dependency. Dependency distributions are installed separately, not copied into this repository. Preserve their licenses if distributing a bundled environment. Versions and transitive dependencies may differ on a supported target Python version; create and audit a target-specific lockfile before a release.

## Hardware and external services

The supplied OLED scripts import Pillow and luma.oled/luma.core; these are listed as optional hardware dependencies but were not installed, license-audited at a pinned version or exercised on hardware. The scripts also invoke a vendor pironman5 executable that was not supplied. Review exact versions, licenses and hardware compatibility before enabling them.

Samba, Nextcloud, Pi-hole, Unbound, Netdata, Tailscale, BTRFS tools and UPS software are not bundled or installed by this project. Service names and command invocations do not grant redistribution rights. Fonts, logos, screenshots and other assets require a separate source and rights record.

## Service-definition intake

Thirteen owner-supplied VaultPanel service/timer definitions are retained as sanitized references. The separately supplied vendor pironman5 service is summarized in the service audit rather than redistributed: its package version and upstream license have not been verified.
