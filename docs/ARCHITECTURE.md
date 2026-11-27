# Architecture and evidence

## Recovered implementation

Browser → Flask (`vaultpanel/app.py`) → Python collectors → Linux commands, proc/sys files and local service state.

Classic and retro HTML templates share collector API routes, with separate CSS and JavaScript. The source intake adds a Basic-auth and loopback-host boundary, read-only HTTP policy, escaped dynamic HTML and restrictive browser headers. No proxy headers are trusted. This does not establish a production security model.

| Module | Evidence in recovered source | Still missing |
| --- | --- | --- |
| Frontend | Both templates, CSS and JS | Browser/device QA; seven assets reviewed, personal OLED logo excluded |
| Backend | Flask routes, collectors, alert history logic | Production authentication, concurrency and deployment |
| Storage | Operator-confirmed mdraid RAID1 with BTRFS single/DUP on top; diagnostic readers | SMART trends, provisioning, repair and failure tests |
| Backup/snapshots | Seven operator-confirmed read-only snapshots; directory readers; backup entry point disabled | Consistent backup/restore and safe retention implementation |
| Samba | smbd status entry | Share configuration and permission model |
| Nextcloud | Named Docker container status | Deployment, PostgreSQL/Redis configuration and version inventory |
| Pi-hole | pihole-FTL service status | Resolver settings and Unbound integration |
| Netdata | Service status | Access control and deployment |
| Tailscale | Status/IP collection | Access policy and deployment |
| UPS | Operator reports disconnected; testing explicitly excluded | No shutdown/power-return validation or protection claim |
| OLED/RGB/fans | Python/shell adapters plus service/timer references | Vendor version, pin mapping, safe privilege model and hardware tests |

No imported module configures Samba, Nextcloud, DNS, RAID or UPS. Hardware adapters remain disabled by default. Even after manual opt-in, they must be reviewed against the exact hardware revision. The app must never be given unrestricted root, shell or Docker-socket access.

See [service audit](SERVICE_AUDIT.md) for the 14 supplied unit definitions and their compatibility limitations. The operator also listed Unbound as installed/enabled, but its configuration was not supplied.

The [configuration audit](CONFIGURATION_AUDIT.md) documents recovered snapshot/cleanup schedules, broad host privileges and HTTP proxy behavior. These are evidence of the existing installation, not supported defaults.

See [storage evidence](STORAGE_AUDIT.md) for the observed topology and the boot/root partitions outside the data mirror.
