# VaultPanel

A Raspberry Pi infrastructure dashboard with classic and retro web interfaces.

**Status: recovered source, authenticated read-only preview. Not a production release or a NAS installer.** The owner supplied 24 text files from an active installation. This branch preserves the available frontend, backend and hardware adapter source while disabling privileged web actions and adding a local authentication boundary.

## Start here

- [Installation and local preview](docs/INSTALLATION.md)
- [Recovered-source audit and changes](docs/SOURCE_AUDIT.md)
- [Service and schedule audit](docs/SERVICE_AUDIT.md)
- [Architecture and integration evidence](docs/ARCHITECTURE.md)
- [Safe source export](docs/SOURCE_EXPORT.md)
- [Licensing and dependencies](docs/LICENSING.md)
- [Security](SECURITY.md) and [contributing](CONTRIBUTING.md)
- [Polski](docs/README.pl.md)

## What is included

`vaultpanel/` contains the Flask backend, collectors, both HTML/CSS/JavaScript frontends and gated OLED/RGB/fan adapters. Monitoring covers host resources, storage diagnostics, service status and networking. Observing a service is not installing or managing that service.

Hardware controls and backup POST endpoints return an explicit refusal. Sanitized service/timer definitions are retained as non-installable reference files. No sudo rules, NAS data, databases, logs, private history are imported. Seven owner-authorized images are included; one personal OLED logo is deliberately excluded. See [asset review](docs/ASSETS.md).

## Validation

```sh
node --test tests/*.test.mjs
python -m unittest discover -s tests -p 'test_*.py'
node scripts/review-files.mjs .
```

Python tests require `vaultpanel/requirements.txt`; see the installation guide. The heuristic scanner also flags public URLs and synthetic security tests for manual review. It does not certify privacy or inspect Git history.

## License

Original project code and documentation are available under [MIT](LICENSE), authorized by the owner. Third-party dependencies retain their own licenses; the seven included owner-supplied graphics are also MIT. No rights are asserted over vendor components.
