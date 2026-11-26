# Baseline audit — 2026-11-26

## Evidence and scope

The connected GitHub account exposed one repository, VaultPanel, already public. The GitHub API returned one branch, `main`, at `e571586de4f22db19f8119357914b03e776b2929`. Its root commit has no parents. The recursive tree contains only `README.md` (50 bytes), with the heading VaultPanel and a short infrastructure-dashboard description. The refs endpoint returned only `refs/heads/main`; no tags were listed there. The pull-request collection was empty.

The dedicated local project directory was empty. A bounded search in its parent project directory found no additional RPI/VaultPanel source checkout. This is not a search of every disk, cloud account or inaccessible repository. The owner confirmed that no project source repository is available yet. No device connection was attempted.

The local system Git executable could not run because developer tools were absent. Repository inspection used the connected GitHub API. No local clone or independent Git object traversal was possible. The API tree was not truncated, and the only reachable baseline commit and its file were reviewed.

## Separate checks

| Check | Result | Remaining work |
| --- | --- | --- |
| Connection and visibility | One accessible repository, already public | Recheck scope if more repositories are connected |
| Branches and reachable history | One branch, one root commit, README only | Repeat for all newly imported refs and objects |
| Source secrets | No credentials, private URLs or device IPs in baseline README | Scan and manually review incoming files and assets |
| Personal data in history | Personal author email in existing commit metadata | Owner decision on retaining public identity or separately approved migration; value intentionally omitted |
| Licensing | No license or dependency manifests | Verify provenance, choose license for owned code, preserve third-party notices |
| Runtime/security behavior | No application code available | Authentication, authorization, privilege boundaries and deployment review |
| Storage/hardware | No configuration or test evidence available | Disposable-device testing and recovery validation |

GitHub's public commit signature is not a private signing key. The audit does not cover unreachable objects, deleted refs, caches, device files or third-party copies. No repository visibility, default branch, existing history or account profile was changed.

## Changes prepared after the baseline

English documentation with a Polish entry point; source and license intake requirements; a review-only environment example; ignore rules; a heuristic sensitive-data scanner; an explicit-file-list export helper; and tests for sensitive values, unsafe paths and export behavior. These are newly authored preparation tools, not recovered VaultPanel code.

## Release blockers

1. Obtain actual frontend, backend, static assets, build manifests and lockfiles.
2. Obtain selected service configuration templates and custom scripts, with secrets removed in a review copy.
3. Establish source ownership and dependency/license inventory.
4. Resolve personal metadata policy before any new history import; use a verified GitHub no-reply identity for future commits if desired.
5. Implement and test installation, authentication, least privilege, updates, backup and recovery against the recovered source.
6. Review screenshots, logs, filenames, commit messages, authors, tags, releases and CI artifacts before publication.

Do not mark this project production-ready or publish a release while these blockers remain.
