# Contributing

The first milestone is verified source intake, not a runnable release.

Use a separate branch and a draft pull request. Keep changes small enough to review and describe whether code is newly authored or recovered from an existing installation. Never import device data or private Git history into a public branch.

For source imports, include provenance and redistribution permissions, sanitized configuration examples, dependency manifests/lockfiles and meaningful tests. Preserve third-party license notices. Do not include real hostnames, usernames, addresses, tokens, passwords, screenshots of personal data or generated build output without review.

Run the tests and scanner described in the README. Manually inspect every file and review the entire proposed diff. Any installer must provide safe preflight behavior and must not modify storage without explicit operator intent. Test on disposable infrastructure first.

Use a verified no-reply commit identity if you do not want a personal email in public history. Do not rewrite others' commits or change repository visibility without explicit approval.
