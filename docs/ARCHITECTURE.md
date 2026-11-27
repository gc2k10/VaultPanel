> Intake-stage record. A sanitized read-only application is now present; see [SOURCE_REVIEW.md](SOURCE_REVIEW.md), [CONFIGURATION.md](CONFIGURATION.md) and [VALIDATION.md](VALIDATION.md) for the current evidence. Earlier statements about missing application source describe the original baseline. Licensing and release gates remain open.

# Architecture and module evidence

This document describes an intended boundary, not an implemented system. No service topology, programming language, API contract, ports or hardware wiring has been verified.

## Proposed boundaries for review after source recovery

Browser → authenticated VaultPanel API → narrowly scoped service adapters → host services.

The browser should never receive system credentials. The API should run without root privileges. Any privileged helper needs a fixed operation allowlist, explicit authorization, validation and an audit trail; user input must not become a shell command. Destructive storage actions require a separate design and explicit operator confirmation. Avoid exposing the Docker socket to the dashboard.

| Requested module | Available implementation | Evidence needed |
| --- | --- | --- |
| VaultPanel frontend | None supplied | Full source, assets, build manifest, lockfile, sanitized screenshots |
| Backend/API | None supplied | Routes, auth/session handling, manifests, service definitions, tests |
| NVMe / RAID1 / BTRFS | None supplied | Actual topology, mount and maintenance scripts; determine BTRFS RAID1 vs block-layer RAID |
| Snapshots / backup | None supplied | Retention, scheduling, off-device backup and tested restore procedures |
| Samba | None supplied | Share templates, account/group and permission model; no account databases |
| Nextcloud / PostgreSQL / Redis | None supplied | Deployment files and version constraints; no databases or live config secrets |
| Pi-hole / Unbound | None supplied | Resolver templates and network bindings; no query logs |
| Netdata | None supplied | Deployment and access-control configuration; no cloud claim tokens |
| Tailscale | None supplied | Integration approach; no auth keys or machine state |
| UPS | None supplied | Model/protocol, daemon choice and tested shutdown behavior |
| OLED / RGB / fans | None supplied | Hardware revision, pin mapping, controller source and vendor license |
| Pironman 5 MAX | Mentioned in prior planning only | Confirm actual hardware and redistribution rights for vendor assets |

RAID and snapshots must not be presented as independent backups. Document recovery and failure behavior for each integration before supporting it. Integration names do not imply bundled third-party software.
