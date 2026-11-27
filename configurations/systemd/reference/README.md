# Recovered service references

These 13 files document the existing installation; they are **not supported installation templates**. The `.reference` suffix prevents them from being ordinary systemd service/timer unit filenames. Do not rename, copy to system directories or enable them without resolving the [service audit](../../../docs/SERVICE_AUDIT.md).

Account names were replaced with `vaultpanel`; no account is created. Paths and timer settings describe the recovered deployment and are not a universal configuration contract. Units with no User directive preserve that evidence rather than silently hiding the root-execution finding.

No installer reads this directory. No credentials are included. The vendor pironman5 unit is not redistributed because its exact provenance and license have not been verified. Use the local preview instructions while deployment and hardware support remain under review.
