# Architecture and evidence

## Recovered implementation

Browser → Flask (`vaultpanel/app.py`) → Python collectors → Linux commands, proc/sys files and local service state.

Classic and retro HTML templates share collector API routes, with separate CSS and JavaScript. The source intake adds a Basic-auth and loopback-host boundary, read-only HTTP policy, escaped dynamic HTML and restrictive browser headers. No proxy headers are trusted. This does not establish a production security model.

| Module | Evidence in recovered source | Still missing |
| --- | --- | --- |
| Frontend | Both templates, CSS and JS | Original image rights/review, browser/device QA |
| Backend | Flask routes, collectors, alert history logic | Production authentication, concurrency and deployment |
| Storage | lsblk, SMART, BTRFS and mdstat readers | Actual RAID topology, provisioning, repair and failure tests |
| Backup/snapshots | Snapshot directory readers; backup entry point disabled | Consistent backup/restore and safe retention implementation |
| Samba | smbd status entry | Share configuration and permission model |
| Nextcloud | Named Docker container status | Deployment, PostgreSQL/Redis configuration and version inventory |
| Pi-hole | pihole-FTL service status | Resolver settings and Unbound integration |
| Netdata | Service status | Access control and deployment |
| Tailscale | Status/IP collection | Access policy and deployment |
| UPS | No supplied implementation | Model, daemon, shutdown and power-return tests |
| OLED/RGB/fans | Python display code and shell adapters | Service units, timers, vendor version, pin mapping, safe privilege model |

No imported module configures Samba, Nextcloud, DNS, RAID or UPS. Hardware adapters remain disabled by default. Even after manual opt-in, they must be reviewed against the exact hardware revision. The app must never be given unrestricted root, shell or Docker-socket access.
