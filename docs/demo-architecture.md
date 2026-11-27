# Target architecture

Status: proposed; public implementation not verified.

- backend/: Flask API and read-only system collectors.
- frontend/: responsive infrastructure dashboard.
- scripts/: reproducible installation and diagnostics.
- config/: sanitized example configuration.
- services/: systemd templates.
- tests/: automated tests and isolated integration tests.

Administrative operations must be explicitly authorized, narrowly scoped and disabled by default. Never use production infrastructure as a public demonstration.
