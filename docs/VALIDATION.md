# Validation of the read-only review build

Date: 2026-11-27. Status: review candidate toward v0.1.0-alpha; **not released**.

For current release decisions, use `ALPHA_READINESS.md` and the latest verification section below. Earlier sections retain historical results.

## Executed checks

- Static/manual review of every one of the 24 original source files; archived code was never executed.
- 17 Python unittest cases passed against the refactored application, with subprocess and mutation boundaries mocked. Covered all four denied admin routes, direct disabled adapters, read routes, no GET history writes, authentication/Host/client checks, import safety, portable storage, psutil memory data, exact container matching, SMART parsing and errors, subprocess timeout/allowlist and configuration rejection.
- 9 Node tests passed: 7 inherited intake-tool tests and 2 frontend tests exercising both layouts with hostile telemetry. Dynamic HTML values are escaped, including attribute contexts. These are mocked DOM tests, not a browser visual acceptance test.
- Both application JavaScript files passed `node --check`.
- Bandit 1.8.6 scanned `app.py`, `collectors.py`, `config.py`, `hardware.py`: 0 high, 0 medium, 10 low findings. Eight B110/B112 findings concern inherited exception/pass/continue handling; B404/B603 flag the deliberately isolated subprocess boundary. No findings were suppressed. Commands are disabled by default, allowlisted, shell-free and timeout-limited; PATH trust/output limits remain review topics.
- The heuristic privacy scanner was run on original and sanitized trees. Original: 18 findings, manually reviewed. Sanitized code findings include date patterns, references to runtime authentication settings, and a documentation-range address in tests. No real credential values were found; this is not a certification.

Local runtime: macOS ARM64, Python 3.9.6, Node.js 24.22.3, Flask 3.1.3, psutil 7.2.2. Exact application dependency versions from this environment are recorded in `requirements-tested.txt`; they are evidence of one local environment, not a cross-platform lockfile or a security certification.

## Release gates still open

- Validate supported Python 3.10+ runtimes on Linux and Raspberry Pi in a disposable environment; the available local interpreter was older.
- Browser visual and interaction acceptance for both layouts, including accessibility, slow/unavailable APIs and long values.
- Full dependency vulnerability/license inventory and source/asset redistribution rights.
- Stronger telemetry failure reporting, bounded command/state-file reads, request cost limits and caching.
- Any remote deployment needs an independently reviewed authentication/TLS/proxy model; current build is local-only.
- Hardware control and backup adapters remain unavailable. Validate thermal safety, failure/timeout handling, ownership and least privilege before implementing them. A restore test is mandatory before claiming backups work.
- No release tag, release object, NAS installation, service restart or live hardware test was performed.

## Follow-up validation — 2026-11-27

This section supersedes the original counts above for the current tree.

- Python 3.12.14: 25 tests passed. Eight additional cases cover bounded state-file reads (including symlinks/FIFOs), state schemas, unknown hardware data, snapshot/backup separation, Btrfs completion/error evidence, invalid configuration, and subprocess output limits/timeouts/reaping. Only newly authored harmless Python snippets execute in subprocess integration tests; hardware commands remain mocked or disabled.
- Node.js 24.22.3: all 9 tests passed after polling changes.
- Playwright 1.62.1 with Chrome 158.0.8127.88: 8 scenarios passed using only synthetic fixture data. Both classic and retro layouts were tested at 390 and 1280 pixels, all six tabs, disabled controls, no POST requests, no page errors, HTTP 503 recovery and hostile telemetry displayed as text. All four overview screenshots were visually inspected. A mobile classic header overlap found during visual review was corrected and a geometry assertion added.
- pip-audit 2.10.1 checked the exact eight-package Python 3.12 application closure against its default public vulnerability service: no known vulnerabilities found. See `docs/dependency-audit.json` and `requirements-tested-py312.txt`. This is a dated known-advisory check, not proof of security. Tooling dependencies, OS packages and the older Python 3.9 closure are outside this result.
- Installed wheel license metadata and license-file hashes are recorded in `dependency-inventory.json`. This records evidence for dependencies; it does not establish ownership or redistribution rights for the recovered application and assets.
- Bandit 1.9.4 over the five runtime modules: 0 high, 0 medium, 6 low findings (four inherited exception/pass/continue cases, subprocess import and isolated Popen). No suppressions.
- Final source-only export privacy scan: 19 heuristic findings reviewed (date expressions, authentication code references, two loopback test URLs and a synthetic documentation-range IP). Generated bytecode is excluded from the published tree.
- Added a read-only GitHub Actions workflow for Linux on Python 3.10/3.12/3.13 and Node.js 24. Action revisions are pinned to verified upstream commit SHAs. Remote results are recorded separately after the run completes.

Remaining validation includes real Linux/Raspberry Pi telemetry, hardware failure modes, backup/restore design, additional browsers, accessibility and slow/hung request behavior. Browser fixture tests do not validate a NAS deployment.

### Reproduce browser checks

Install Playwright 1.62.1 in a separate development tools directory and make it available to Node (for example via `NODE_PATH`), with Chrome installed. In the project root, start `python tests/browser_server.py`; in another terminal run `node tests/browser/check.cjs`. Optionally set `VAULTPANEL_SCREENSHOTS` to a private output directory. The fixture server uses port 8091 and replaces all endpoint collectors with synthetic data. Do not deploy this test server.

## Extended verification — 2026-11-27

- GitHub Actions run [46034285288](https://github.com/gc2k10/VaultPanel/actions/runs/46034285288) completed successfully for commit `3874e89c5f64fc89259082f7b7c75fe2b3e65579`: Python 3.10, 3.12 and 3.13 on Linux, plus Node.js 24. All four jobs and their test steps succeeded. These are mocked/integration checks, not real NAS telemetry validation.
- detect-secrets 1.5.0 scanned all 24 original files and the source-only sanitized export with network verification disabled. Original: 0 findings. Sanitized export: 6 high-entropy findings, manually verified as SHA-256 hashes of dependency license files. No credential was confirmed. Scanner output containing hashes remains in private work files; it is not a guarantee that unknown/custom secrets are absent.
- A further service-status regression test distinguishes unavailable telemetry from a known inactive/failed service. Current local suite: 26 Python tests and 11 Node tests passed.
- Polling waits for every request to settle, so a fast error cannot start another refresh while a sibling request is still pending. Eight-second request timeouts remain in effect. Both layouts now wrap long host/service/alert values on mobile.

The final 12 Chrome/Playwright scenarios passed, including long values and a mixed fast-failure/hung-request cycle with automatic recovery. Newest Linux CI outcomes are attached to the PR validation summary. No hardware writes, production deployment, merge or release was performed.

## Accessibility and HTTP failure verification — 2026-11-27

- 32 Python tests and 11 Node tests passed locally. Six new HTTP tests cover collector exceptions, invalid authentication, method/path rejection, cross-origin response headers, forwarded-header spoofing and malformed/oversized admin bodies. Unexpected collector failures return generic JSON HTTP 503 without exception details.
- Playwright 1.62.1: 12 scenarios each in Chrome 158.0.8127.88, Firefox 153.0 and WebKit 26.5 (36 total), using only synthetic fixture telemetry. WebKit exposed native select overflow on the retro cooling page; resetting the hidden select appearance/padding fixed it. WebKit is an engine test, not a test of a physical Safari/iOS device.
- axe-core 4.14.1: no automated violations in 12 desktop views after heading and input-label corrections. Keyboard tests cover the skip link, Enter activation and selected-navigation announcements; reduced-motion styling is enabled. Seven views retain incomplete contrast checks requiring manual review. Screen readers and full WCAG conformance have not been validated.
- Bandit 1.9.4 repeated on the five runtime modules: 6 low findings, 0 medium/high.
- Final source export: 46 files; 24 heuristic findings manually reviewed (configuration references, date patterns, loopback/public CI URLs and synthetic IPs). detect-secrets 1.5.0 with network verification disabled reported only the same six dependency license-file hashes. No credential was confirmed; private history and unknown/custom secret formats remain outside this assurance.
- Owner confirmed team authorship and rights to code/design. License selection and the proposed monitoring-only alpha scope still require the owner's decision. See `ALPHA_READINESS.md`.

To reproduce the browser matrix, run `tests/browser/check.cjs` with `VAULTPANEL_BROWSER=chromium`, `firefox` or `webkit` after installing the corresponding Playwright engines. Chromium uses the installed Chrome channel. Run `tests/browser/accessibility.cjs` with axe-core 4.14.1 and Playwright available in the separate tools directory. `VAULTPANEL_A11Y_REPORT` optionally saves the detailed JSON result. All tests use the local fixture server described above; never deploy it.

## Narrow-screen and ARM64 follow-up — 2026-11-27

- Owner confirmed Pironman 5-MAX and an additional SSD heatsink. No installed RAID/SSD/AI configuration is inferred from the product name. MIT and the monitoring-only scope are approved.
- 32 Python and 11 Node tests passed again locally.
- Accessibility/keyboard checks now cover 24 views (both layouts, six sections, 320/1280 pixels). Zero automated violations. Testing found and fixed overlapping metric text at 320 pixels and retro disk-path overflow.
- The classic gradient still produces axe incomplete results in the original view. All 24 contrast-bound checks (12 classic views at each of the two gradient endpoint colors) passed without violations or incomplete results, retaining nested translucent backgrounds. This is a controlled contrast check, not full rendered-pixel or WCAG certification. The remaining retro cooling incomplete result concerns a decorative color-block glyph, with its hex value separately visible; it is hidden from the accessibility tree. Real screen-reader interaction remains untested.
- Reduced-motion testing now inspects the retro blinking pseudo-element, not only the main element. Skip-link and selected-navigation checks remain enabled.
- Added an independent GitHub-hosted Ubuntu ARM64 job with Python 3.13.5 and explicit architecture/version assertions. Its remote outcome is recorded in the PR after execution; Ubuntu CI is not validation of the exact Debian/Raspberry Pi platform.
