# Work continued from the NAS publication review

## Carried into the alpha

The parallel intake supplied owner-approved graphics, sanitized non-installable service references, and source/service/host-configuration/storage audits. These are retained alongside the hardened root-level application and the separate synthetic frontend demo. The earlier duplicate runtime and executable hardware scripts are excluded from the release tree. Historical audit references describe recovered evidence, not active release paths.

Confirmed operator evidence: mdraid RAID1 below BTRFS; boot/root outside the data mirror; seven read-only snapshots at collection time; controller-reported SMART health. None of this is a recovery guarantee. UPS is disconnected and work on it is excluded by the owner.

## Follow-up implementation in review

The follow-up `mdraid.py` module parses supplied mdstat text with synthetic fixtures for healthy membership, degraded arrays, maintenance, malformed and unavailable states. Seven tests cover these cases, multiple/duplicate arrays, input size and invalid encoding/counts. It performs no reads or commands and is not yet wired into the application API. Keep mdraid membership separate from BTRFS scrub status. No repair, assembly, resync or topology changes. New optional reads must stay disabled until explicitly configured, and absence must never produce a healthy result.

## Later work and evidence needed

| Area | Safe work available now | Still unverified |
| --- | --- | --- |
| Samba | Document least-privilege share requirements | Actual sanitized share/auth policy |
| Nextcloud/database/cache | Document isolation and recovery boundaries | Versioned topology and backup consistency |
| Pi-hole/Unbound | Document resolver ownership and port conflicts | Sanitized effective configuration |
| Netdata/Tailscale | Document read-only display boundaries | Access policy; never request tokens |
| Host privilege/proxy | Preserve audit findings and design safer examples | Effective runtime rules and full proxy includes |
| Backups | Specify restoration acceptance tests | Off-device restore on disposable storage |
| Cooling/OLED/RGB | Specify isolated adapter contracts | Hardware behavior, thermal failure modes, ownership |

Do not request another broad export or access to the NAS to perform these offline tasks. If real configuration becomes necessary, request only a minimal individually reviewed snippet with identities and secrets removed. Never apply sudo/cron/proxy/storage changes to the live NAS as part of publication.
