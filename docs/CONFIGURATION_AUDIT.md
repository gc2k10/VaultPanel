> Historical intake evidence. The alpha runtime is now at the repository root. The earlier `vaultpanel/` runtime and executable hardware scripts were removed from the release tree during integration; reference units are not installable. Current behavior is documented in CONFIGURATION.md and INSTALLATION.md.

# Privileges, cron and proxy audit — 2026-11-28

## Evidence and publication boundary

Twelve files were supplied privately: the main sudoers file, six sudoers include files, two package cron files, one enabled Nginx site and two account crontab captures. The user crontab was empty; the root crontab contained eight jobs. Hashes and original captures remain outside Git. This report omits account names, private virtual hosts and upstream addresses. Raw host policy and package-owned configuration are not redistributed as installation templates.

This is a static review, not an effective-policy or live network test. The complete Nginx include tree, firewall, group memberships, file ownership and system versions remain unknown. No host configuration has been modified.

## Privilege findings

**High priority:** the account used by the captured VaultPanel service has a passwordless ALL command rule. More specific rules do not make this broad grant restrictive. Separately, unrestricted shell and tee grants would themselves allow arbitrary privileged execution or file writes. Merely removing the ALL line would therefore not establish least privilege. See the upstream [sudoers manual](https://github.com/sudo-project/sudo/blob/main/docs/sudoers.man.in).

Other grants cover BTRFS, SMART, vendor hardware commands, specific service operations and the application backup script. BTRFS/SMART executable grants without restricted arguments include more than read-only diagnostics. Several vendor/service entries are duplicated. The backup script and its parent directories must be checked for non-root writability before any privileged execution is considered.

Do not publish or install these rules as defaults. Keep an independent administrative session and recovery access before changing live policy; validate proposed policy with visudo on the target system. A future design should run the web app under a dedicated unprivileged account and use a root-owned helper with fixed operations, validated arguments and no writable executable path. The current preview intentionally grants no sudo policy and may show unavailable diagnostics.

## Root schedule inventory

Times below are interpreted in the server's cron timezone, which has not been verified.

| Schedule | Observed job | Review requirement |
| --- | --- | --- |
| Daily 01:00 | SMART health readings for two NVMe devices | Health checks are not self-tests. Chained commands and direct output overwrite can leave incomplete status files on failure. |
| Daily 02:00 | Read-only BTRFS snapshot, then timestamp marker | A local snapshot is not an independent backup or an application-consistent database backup. |
| Daily 02:30 | Delete matching snapshots, retaining seven sorted entries | Destructive retention has no visible lock, dry-run or dependency on successful snapshot creation. |
| Daily 03:00 | Nextcloud trash cleanup | Verify application retention requirements and backup recoverability before adopting. |
| Daily 03:00 | Application/configuration archive with log redirection | Recovered backup script also deletes older archives; public entry point is disabled. No restore test was supplied. |
| Daily 03:15 | Nextcloud version cleanup | Destructive cleanup requires a documented retention policy. |
| Sunday 04:00 | Docker system prune with confirmation suppressed | Can remove stopped containers, unused networks, dangling images and build cache. No volume-pruning option was present. |
| First day of month 04:00 | Blocking BTRFS scrub, then timestamp marker | Confirm topology, runtime, monitoring and successful-completion semantics. |

The Docker cleanup scope follows the official [prune reference](https://docs.docker.com/reference/cli/docker/system/prune/). Do not generalize it to deleting all volumes or all unused images. Concurrent jobs and command failures require review; none of these jobs were executed during the audit.

Package cron files contain Pi-hole maintenance and e2fsprogs scrub fallback tasks. They are not custom VaultPanel jobs and should remain package-managed. The ext-filesystem scrub entries are not evidence of BTRFS maintenance. No backup/retention installer is provided.

## Nginx findings

The supplied site contains four HTTP virtual hosts routing to the dashboard, private cloud, monitoring and DNS administration. The captured server blocks listen on port 80, forward Host, and contain no TLS or authentication directives. This does not rule out protections elsewhere in the complete configuration or network.

The hardened preview accepts only loopback Host values, so forwarding the original private virtual host will be rejected. Do not bypass that check merely to make the old proxy work. HTTP Basic credentials must not be exposed over an unencrypted network. Continue using loopback/SSH until a reviewed TLS/authentication/proxy trust design is available. A paste-ready proxy example would be misleading without that design and the complete effective configuration.

## Remaining inputs

- Effective sudo policy, service account groups, and ownership/modes for privileged scripts and parent directories, collected without secrets.
- Actual storage topology, mount/subvolume layout and independent backup/restore evidence.
- UPS review is excluded at the owner's request: the device is disconnected. No shutdown protection has been verified.
- Selected complete proxy includes, container deployment definitions and exact software versions, privately reviewed before publication.

The original Raspberry Pi remains unchanged. No automated remediation or deletion is authorized by this report alone.
