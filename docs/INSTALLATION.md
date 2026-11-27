> Intake-stage record. A sanitized read-only application is now present; see [SOURCE_REVIEW.md](SOURCE_REVIEW.md), [CONFIGURATION.md](CONFIGURATION.md) and [VALIDATION.md](VALIDATION.md) for the current evidence. Earlier statements about missing application source describe the original baseline. Licensing and release gates remain open.

# Installation readiness

## What can run today

Only the repository review/export tools. They require Node.js 22+ and no downloaded dependencies. Run from the repository root:

```sh
node --test tests/*.test.mjs
node scripts/review-files.mjs .
```

There is no VaultPanel application to build or start, and `.env.example` is a planning template, not a runtime contract. Do not run guessed installer commands or format existing disks to follow this documentation.

## Before an installation guide can be accepted

- Confirm device model, RAM, storage controller, disks, UPS and display hardware.
- Establish supported operating system, architecture, package versions and upstream sources from the recovered implementation.
- Record required ports and privileges. Default administrative services to loopback or a deliberately restricted management network; authentication is still required.
- Provide module-by-module installation, preflight checks, rollback and uninstall behavior that preserves user data.
- Identify disks by stable identifiers; require a verified backup and explicit device selection for any destructive operation. Never assume a device name.
- Validate storage degradation/recovery, backup restore, DNS failure, UPS shutdown and power return on a disposable test system.
- Test a fresh installation and an upgrade from each supported version. Document exact tested versions and outcomes.

Until then, deployment, performance and data durability are unverified. No default password, public bind address or automatic disk initialization is provided.
