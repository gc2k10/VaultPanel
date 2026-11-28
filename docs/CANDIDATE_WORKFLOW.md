# Source candidates without publication

The next working version is `v0.2.0-alpha`. A candidate is an exact source snapshot for review; it is not a release or installation plan.

On a clean tracked checkout, run:

```sh
python3 scripts/package-alpha.py --version v0.2.0-alpha
```

The new directory `dist/candidates/v0.2.0-alpha/` contains the ZIP, SOURCE_COMMIT.txt and SHA256SUMS.txt. Existing output is never overwritten; use `--output /path/to/a/new-directory` for a separate review build. Versions must be explicit prerelease identifiers. The exporter reads Git objects without executing packaged files and checks every ZIP member. Untracked files are never included; sensitive paths and symlinks are rejected. This is not a substitute for a source/secret review.

The read-only review workflow uploads the same three files as a 14-day artifact after Python, JavaScript and application browser checks pass. Demo checks run separately and must also pass before release. A PR build can record GitHub's temporary merge commit; use the exact final mainline commit for publication. Do not treat a branch name or artifact label as evidence of a published version.

The historical v0.1.0-alpha publisher is now manual-only and refuses to replace the existing release. It does not publish this new version. No tag or release is created by candidate jobs. Future publication must select its version, commit and notes explicitly.

See [candidate notes](releases/v0.2.0-alpha.md) for scope and [installation](INSTALLATION.md) for an isolated local evaluation. No NAS access is needed.
