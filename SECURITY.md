# Security

There is no deployed or supported VaultPanel application release yet.

Never put credentials, personal data or raw device exports in public issues or pull requests. No private vulnerability-reporting channel has been verified for this repository. Establish a private channel with the maintainer before sending sensitive details; a public issue may request a private contact without including the finding.

If a credential has been exposed, revoke or rotate it at its issuer first. Deleting a file or rewriting history does not revoke a credential and cannot remove all existing copies. History changes require owner approval and a recovery plan.

Review files, filenames, Git authors/commit messages, all refs, screenshots, build artifacts and logs. Replace deployment-specific values in review copies with explicit placeholders. Keep real secrets in local environment files or a suitable secret store, not source code. `.gitignore` does not remove already tracked material.

The included scanner is heuristic, not a secret detection or privacy guarantee. It does not inspect Git history, decode binary assets or certify licenses. Its output includes filenames and line numbers; treat reports as private until filenames have also been reviewed.

## Review build boundary

All mutation endpoints and direct hardware adapters are disabled. Requests are limited to loopback clients and trusted local Host values, with optional local Basic authentication. No forwarded headers are trusted. Do not expose this development build through a proxy, tunnel or public interface. Read-only telemetry can still contain sensitive host information. See [configuration](docs/CONFIGURATION.md) and [validation limits](docs/VALIDATION.md).
