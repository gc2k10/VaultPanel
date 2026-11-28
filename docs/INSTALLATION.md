# Local evaluation without a NAS

The published alpha is a read-only preview, not a production NAS installer. Use a separate development machine or disposable VM. Do not install it over an existing VaultPanel or change any NAS services. No second physical NAS is required.

## Preview without installation

Open the [Retro preview](https://gc2k10.github.io/VaultPanel/) on your existing computer. It uses the application template with synthetic values, does not contact your NAS and requires no login or server address. RAID membership is UNKNOWN because the fixture contains no array evidence. Retro is the sole layout; former Classic links forward to it. A normal web visit contacts GitHub Pages; do not enter secrets or upload configuration.

For the Retro layout and local build steps, follow [original-demo.md](original-demo.md). The already published preview needs only a browser. The separate presentation has its own [quick start](demo-start.md). You can stop here: installing on a NAS is not required to review the project.

## Start from the reviewed source archive

Extract the reviewed source ZIP into a new empty directory. Use the ZIP checksum supplied with the candidate to verify the exact download before extraction. Open a terminal in the extracted VaultPanel directory. Python 3.10+ with venv support is required; Node is needed only for developer tests.

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-alpha.txt
python -m pip check
python -B app.py
```

These commands install dependencies only into the local virtual environment. Do not use sudo. Open `http://127.0.0.1:8090/` or `/retro` on that same machine. If the port is already in use, stop this evaluation attempt; do not stop an unknown service or overwrite a live installation. The Flask development server is only for local evaluation.

Start with no VAULTPANEL environment overrides. `.env.example` is documentation and is not loaded automatically. Diagnostic commands default to disabled, service/device lists are empty and missing readings remain unknown. All four write endpoints deny requests. No disks, accounts, services, firewall rules or startup tasks are configured. The displayed telemetry belongs to the evaluation machine, not the NAS.

The optional `VAULTPANEL_ACCESS_TOKEN` protects local access with Basic authentication; configure it privately if needed. Local-only binding is not isolation from other local users/processes. Do not expose this build through a proxy or tunnel. See [configuration](CONFIGURATION.md).

## Stop and remove the evaluation

Press Ctrl+C in the terminal running the server, then run `deactivate`. Remove only the new directory created for this evaluation if no longer needed. No system service is installed, so there is no service uninstall or reboot step. Do not delete an existing deployment or its data. This procedure is not an upgrade or rollback plan for a production installation.

## Checks performed and limits

A fresh local Python environment installs the pinned dependency set and passes `pip check`. The distribution smoke test creates a source ZIP from tracked files, extracts it into a temporary directory, and imports it in a new isolated Python process from a different working directory. It requests both pages, local assets, eight read APIs and four denied write APIs. Command execution and outbound socket connections are trapped; source hashes and the empty working directory must remain unchanged. API response contents are not printed or published.

CI repeats the test on Linux x64 and ARM64. This uses the Flask request test client, not a production HTTP server or the physical Raspberry Pi. Browser tests use synthetic fixtures. Never deploy `tests/browser_server.py`.

## Follow-up RAID review

The RAID changes on PR #4 are separate from the published alpha ZIP. Keep `VAULTPANEL_MDRAID_READS=false` for local evaluation. Tests inject synthetic mdstat text and mocked reads; do not copy `/proc/mdstat` or configuration from the NAS. Running the app on a laptop displays laptop telemetry, not NAS data. No remote NAS connection exists. Real hardware acceptance and any permanent installation remain later, separately planned work.
