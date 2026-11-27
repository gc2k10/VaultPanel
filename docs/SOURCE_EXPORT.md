# Safe source export from an existing device

No server access is assumed. Run these steps yourself on the device or on an offline source backup. Never grant broad server access just to gather files.

## 1. Identify source, without copying runtime data

Locate the actual frontend/backend source and custom scripts. Use your existing service definitions or deployment notes to identify paths; do not guess that the application is under a particular home directory. Record language/runtime versions, build commands and service entry points separately. Inspect service definitions locally because environment values and arguments may contain secrets.

Select source files, package manifests, lockfiles, original license notices, custom service units and configuration templates. Do not select NAS contents, home directories, database dumps, backups, private keys, live `.env` files, authentication databases, DNS logs, Tailscale state or Nextcloud user data. Do not copy whole `/etc`, `/var`, `/home` or a whole disk image.

## 2. Create a private review copy

The optional helper requires Node.js 22+ on the device or offline review machine. If unavailable, manually copy the same explicit selection to a private directory; installing a runtime on a production NAS is not required.

Create a plain-text manifest outside the source root, one relative filename per line, with actual filenames you have inspected. No directory entries, wildcards, absolute paths or parent traversal are accepted. For example, **only if those files actually exist**:

```text
frontend/package.json
frontend/src/main.js
backend/package.json
backend/src/server.js
```

Choose an existing private parent directory outside the application root. The output directory must not already exist. Run without sudo, substituting your own local paths (do not paste private paths into public issues):

```sh
node scripts/export-source.mjs /path/to/source /path/to/selected-files.txt /path/to/private-parent/review-copy
node scripts/review-files.mjs /path/to/private-parent/review-copy
```

The helper creates owner-only directories/files, refuses symlinks and known sensitive file types, and copies only explicit UTF-8 text files up to 2 MiB each. It does not upload, sanitize or execute source. Stop writes to the selected source while copying: this is not a race-resistant backup tool for an untrusted changing filesystem. If an I/O failure leaves partial output, keep it private and inspect it; the helper does not delete anything. Binary assets and larger files need separate manual review and provenance checks.

## 3. Sanitize the copy, never the working installation

Read every selected file. Replace private domains with `example.invalid`, usernames with descriptive placeholders, network addresses with documented placeholders and secrets with `REPLACE_ME`. Build `.env.example` from variable names, never from a blind copy of a live environment file. Check HTML, JavaScript bundles, CSS, comments, fixtures and embedded source maps too. Do not remove required third-party attribution without reviewing its license.

The scanner exits 0 for no heuristic findings, 1 for findings and 2 for failure. It flags URLs for human review, even legitimate public upstream URLs. It skips `.git` contents and does not inspect history. It may miss secrets, especially custom token formats, encoded values, usernames and hostnames without URLs. Review filenames and image metadata manually. Reports contain paths and must also remain private until reviewed.

## 4. Handle Git history separately

Do not copy `.git` into the public project. If a source repository exists later, inspect all branches/tags, every reachable commit/blob, commit messages, author/committer identities, annotated tag metadata and Git LFS/submodules. Check whether a clone is shallow or partial before claiming a full audit. Use an independently verified secret scanner in addition to manual review, retain its version and scope privately, and review its redacted findings. Never print found secrets into CI logs.

A clean working tree does not imply clean history. Revoke exposed credentials before considering history remediation. Import only reviewed files into the preparation branch; obtain explicit approval before publishing private history or changing repository visibility. The current public baseline already contains personal commit-author metadata; changing files will not remove that metadata.

## 5. Transfer only after review

Transfer the sanitized selection through a private channel to the local project workspace, then repeat review before pushing. Include the selected file list, a provenance/license inventory, module mapping and exact tested versions. Add screenshots only after inspecting every visible value and metadata. Keep unsanitized exports and original data outside any public repository.
