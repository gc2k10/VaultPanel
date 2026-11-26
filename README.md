# VaultPanel

Preparation workspace for a Raspberry Pi 5 home server and infrastructure dashboard.

**Status: source collection and documentation. There is no runnable dashboard or NAS installer in this repository yet.** The existing repository contained only a short README. Frontend, backend, device configuration and hardware integrations have not been supplied or verified.

The intended scope includes storage, file sharing, private cloud, DNS, monitoring, remote access and hardware controls. Inclusion in this scope does not mean an integration exists or works.

## Start here

- [Audit and missing sources](docs/AUDIT.md)
- [Architecture and module evidence](docs/ARCHITECTURE.md)
- [Safe source export](docs/SOURCE_EXPORT.md)
- [Installation readiness](docs/INSTALLATION.md)
- [Licensing and dependency inventory](docs/LICENSING.md)
- [Security](SECURITY.md) and [contributing](CONTRIBUTING.md)
- [Polski](docs/README.pl.md)

## Repository tools

The newly written review tools use Node.js 22 or newer, with built-in modules only. They do not install services, modify disks or connect to a server.

```sh
node --test tests/*.test.mjs
node scripts/review-files.mjs .
```

The scanner reports potential sensitive data without printing matched values. A successful scan is only a heuristic check, not clearance to publish. See the manual review and history requirements in [SOURCE_EXPORT.md](docs/SOURCE_EXPORT.md).

## Scope and licensing

No frontend/backend source, package manifests, lockfiles, service units, device screenshots or deployment configurations were present at the baseline audit. A production installation guide cannot be validated until these are recovered.

No project license has been selected. Public visibility is not a grant of an open-source license. Ownership and third-party notices must be reviewed before an open-source release; see [LICENSING.md](docs/LICENSING.md).
