# VaultPanel

A self-hosted infrastructure dashboard for Raspberry Pi and home servers.

VaultPanel aims to bring storage, services, networking, hardware health and alerts into a single responsive interface.

## Project status

Early public repository. A local Flask prototype has been reported; public application code, installation and feature availability have not yet been verified. The following is the intended scope, not a claim of released functionality.

## Planned capabilities

| Module | Scope |
|---|---|
| Overview | System health and resource usage |
| Storage | RAID, Btrfs, capacity and snapshots |
| Services | Service status and controlled actions |
| Network | Connectivity and network service health |
| Hardware | UPS, cooling, RGB and OLED monitoring |
| Alerts | Health warnings and event history |

## Target architecture

Python / Flask backend, modular system collectors, responsive web frontend and narrowly scoped administrative actions. The public implementation will use sanitized example configurations and synthetic demonstration data.

## Installation

A tested installation guide is not yet available. Do not deploy unverified code on a production NAS. A clean Raspberry Pi OS installation, non-root service account and documented rollback procedure are release requirements.

## Security

Never expose the administration interface directly to the internet. Do not publish credentials, private network details or production logs. Administrative actions must be authenticated and explicitly authorized.

## Roadmap

1. Inventory and sanitize the existing prototype.
2. Establish a reproducible installation and read-only monitoring.
3. Build and test the responsive dashboard.
4. Add narrowly scoped controls and automated tests.
5. Publish a documented release.

## License and support

License selection and optional funding links are pending. No payment is required to view this repository.
