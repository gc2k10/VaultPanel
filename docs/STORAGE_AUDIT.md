# Storage evidence — 2026-11-28

## Observed topology

Operator-provided lsblk, findmnt and mdstat output establishes this stack:

```text
NVMe A partition 1 ─┐
                   ├─ Linux mdraid RAID1 (/dev/md0) ─ BTRFS ─ /data
NVMe B partition 3 ─┘
NVMe B partition 1: boot filesystem (outside this mirror)
NVMe B partition 2: ext4 operating-system root (outside this mirror)
```

At collection time mdstat reported two configured and two active members, `[UU]`, with no recovery progress displayed. BTRFS sees one logical md device. Its profiles are Data/single, Metadata/DUP and System/DUP; this is not native multi-device BTRFS RAID1. Device labels above are explanatory, not instructions for identifying disks during installation or repair. Filesystem UUIDs are intentionally omitted.

## Filesystem observations

The operator's BTRFS device counters were all zero: write, read, flush, corruption and generation errors. The last reported scrub started on 2026-11-01, finished in 6 minutes 42 seconds and reported no errors. These are historical/runtime observations, not a guarantee of current disk health or recovery capability. A subsequent SMART health reading is summarized below; member failure handling and restore tests remain outstanding.

The high percentage shown on the Data/single line refers to use of already allocated data block groups, not the whole device. The same report showed substantial unallocated device space and estimated free space. That percentage alone does not establish a full filesystem or justify balance/repair. See [BTRFS space accounting](https://btrfs.readthedocs.io/en/stable/btrfs-filesystem.html) and [device statistics](https://btrfs.readthedocs.io/en/latest/btrfs-device.html).

## Implications for VaultPanel

- Present mdraid membership and BTRFS integrity as separate observations, with unknown/error states when collection fails. A BTRFS healthy flag must not stand in for mdraid status.
- Do not advertise boot/root redundancy: those partitions are outside the observed data mirror. Loss of their physical disk may prevent boot even if mirrored data remains available.
- Do not infer physical drive health from zero counters on the logical md device.
- Local snapshots and RAID membership do not establish an independent backup. Snapshot consistency, off-device copies and restoration still need validation.
- The public preview remains conservative about health and does not create, repair, rebalance or reconfigure storage. No live maintenance was started by this review.

Further evidence needed: mdraid detailed state without UUIDs, mount configuration and a verified backup/restore procedure. UPS testing is excluded at the owner's request because the unit is disconnected.

## Subsequent physical-drive SMART reading

The operator supplied smartctl 7.4 health/attribute output for both NVMe controllers. Both reported PASSED, Critical Warning 0x00, available spare 100%, Percentage Used 0%, zero media/data integrity errors, zero error-log entries and zero warning/critical composite-temperature time. These are controller-reported readings, not a newly executed extended self-test or a guarantee against failure. Percentage Used is a reported estimate, not a statement that the drives have never been used.

Both drives have nonzero historical unsafe-shutdown counters. A single reading cannot establish when those events occurred, whether counters are increasing, or whether the cause was external power loss, a reset or another interruption. Do not infer UPS failure solely from these counters. UPS inspection was subsequently excluded by the owner because the unit is disconnected. Later counter readings could establish a trend without interrupting the live NAS; no shutdown-protection claim is made. Detailed usage volumes, device serials and identifiers are not reproduced here.

## Subvolumes and snapshot flags

The operator supplied a full subvolume listing and a separate read-only-filtered listing. The first contains the working `files` subvolume and seven dated `files-*` entries under `.snapshots`. All seven snapshot entries also occur in the read-only-filtered output; the working subvolume does not. This confirms the reported read-only flags at collection time. Numeric subvolume identifiers and generation counters are omitted from this public summary.

The observed count is consistent with the recovered seven-entry retention policy, but does not prove that every scheduled creation or deletion succeeded. Date-bearing names are not independent evidence of exact creation time. Read-only flags do not establish application consistency, protect against privileged deletion, or substitute for an off-device backup. No snapshot was mounted for inspection, restored, deleted or changed during this audit.

A restore test remains a future, separately scoped operation on disposable storage. The current project must not advertise recovery as verified.
