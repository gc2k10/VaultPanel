# Validation of the read-only review build

Date: 2026-11-27. Status: review candidate toward v0.1.0-alpha; **not released**.

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
