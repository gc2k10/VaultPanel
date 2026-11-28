# VaultPanel

A read-only review build of the existing Flask dashboard, with classic and retro layouts. The production-source intake has been reviewed and sanitized. **The main branch includes unreleased follow-up changes beyond v0.1.0-alpha. Use GitHub Releases for a fixed, verified archive. Neither is production-validated.**

The dashboard reads CPU, memory, uptime and configured storage telemetry. Optional Linux command-based reads are disabled by default. All four administration endpoints return HTTP 403; backup, fan, LED and OLED operations are intentionally unavailable. The original hardware scripts are excluded from the application.

## Preview without installation

Open the original [Classic](https://gc2k10.github.io/VaultPanel/original/index.html) or [Retro](https://gc2k10.github.io/VaultPanel/original/retro.html) layout. These use the application's templates and styles with fictional data, disabled controls and no NAS connection. [Preview details](docs/original-demo.md). The site root is a separate project presentation.

## Local evaluation

Use a disposable development environment, never a live NAS for this review. Python 3.10+ is the target for further validation. Tests passed on Python 3.10/3.12/3.13 on Linux x64 and Python 3.13.5 on Linux ARM64; current results are tracked in the PR. This does not validate physical Raspberry Pi sensors.

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-alpha.txt
python app.py
```

Open the loopback address `127.0.0.1:8090`; `/retro` selects the retro layout. Do not run as root. The Flask development server is for local evaluation only. No service installer, privileged permissions, disk changes or deployment are performed by these steps.

Configuration uses environment variables documented in [.env.example](.env.example) and [CONFIGURATION.md](docs/CONFIGURATION.md). The example is not loaded automatically. No private network address, service selection, disk name or host identity is bundled.

## Review and validation

```sh
python -m unittest discover -s tests -v
node --test tests/*.test.mjs
node scripts/review-files.mjs .
```

The heuristic scanner intentionally reports some code references and synthetic test data; review its findings, do not treat an exit code as a privacy guarantee. Node.js 22+ is required for the intake tools and JavaScript tests.

- [Local evaluation and removal](docs/INSTALLATION.md)
- [Draft alpha release notes](docs/RELEASE_NOTES_ALPHA.md)
- [Source audit, all 24 original files](docs/SOURCE_REVIEW.md)
- [Validation results and release blockers](docs/VALIDATION.md)
- [Configuration and API changes](docs/CONFIGURATION.md)
- [Security](SECURITY.md), [licensing](docs/LICENSING.md), and [contributing](CONTRIBUTING.md)
- [Earlier intake audit](docs/AUDIT.md), [source export procedure](docs/SOURCE_EXPORT.md)

Licensed under [MIT](LICENSE), selected by the owner on 2026-11-27 after confirming authorship and redistribution rights. The first alpha is approved as monitoring-only. Target-device telemetry and manual accessibility validation remain open; see [alpha readiness](docs/ALPHA_READINESS.md). The live NAS was not contacted or modified.

## Existing demo and audited NAS evidence

The [standalone frontend demo](frontend/README.md) and [project site](https://gc2k10.github.io/VaultPanel/about.html) remain synthetic and independent of the local Flask panel.

Reviewed evidence from the parallel source intake is retained: [assets](docs/ASSETS.md), [services](docs/SERVICE_AUDIT.md), [host configuration](docs/CONFIGURATION_AUDIT.md), and [storage](docs/STORAGE_AUDIT.md). Historical scripts and unit references are not production installation instructions. UPS work is explicitly excluded. See [next work](docs/NEXT_WORK.md).
