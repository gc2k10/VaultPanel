# Work continued from the NAS publication review

## Carried into the alpha

The parallel intake supplied owner-approved graphics, sanitized non-installable service references, and source/service/host-configuration/storage audits. These are retained alongside the hardened root-level application and the separate synthetic frontend demo. The earlier duplicate runtime and executable hardware scripts are excluded from the release tree. Historical audit references describe recovered evidence, not active release paths.

Confirmed operator evidence: mdraid RAID1 below BTRFS; boot/root outside the data mirror; seven read-only snapshots at collection time; controller-reported SMART health. None of this is a recovery guarantee. UPS is disconnected and work on it is excluded by the owner.

## Unreleased follow-up implementation

The follow-up implementation connects the bounded mdstat parser to `/api/storage` through an independent opt-in read adapter. Both layouts distinguish array membership from BTRFS scrub results. Reads default to disabled; the adapter never invokes commands or writes. Synthetic tests cover disabled access, read failures, API separation, both layouts and a single-member array that cannot establish redundancy. This work is not part of the published v0.1.0-alpha. Physical sensor and storage topology validation remains outstanding.

The original Classic and Retro static previews use the same templates and scripts. Their missing RAID evidence stays UNKNOWN. Browser tests cover this contract without a backend or hardware reads. The published alpha archive remains unchanged.

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
