# Service and schedule audit — 2026-11-28

## Evidence and privacy

The operator supplied 14 `systemctl cat` captures: nine services and five timers. Thirteen VaultPanel definitions are retained under [reference configurations](../configurations/systemd/reference/README.md); the vendor pironman5 unit is summarized only. No credentials, environment assignments or environment-file references were found in these captures. Deployment account names were replaced with the neutral `vaultpanel` account, which this repository does not create. Original captures and hashes remain in private intake, outside the Git repository.

These are configured definitions, not runtime verification. The operator's earlier unit-file listing establishes boot enablement only. Only the main VaultPanel service was separately reported active. Cron jobs, sudo rules, effective process credentials, device permissions and runtime environment have not been supplied. No unit has been installed, enabled, restarted or disabled by this audit.

## Inventory

| Unit stem | Captured service behavior | Timer definition | Operator-listed enablement |
| --- | --- | --- | --- |
| vaultpanel | Flask via `venv/bin/python`, configured non-root account, restart always | None | Service enabled |
| vaultpanel-auto-fans | Fan refresh script, non-root account | Boot +30 seconds; 30 seconds after unit activation | Timer disabled |
| vaultpanel-led-alert-hourly | Hourly alert script, non-root account | Boot +5 minutes; 1 hour after activation; Persistent=true | Timer disabled |
| vaultpanel-led-alert | Alert script; no User directive | Boot +30 seconds; 60 seconds after activation | Timer enabled |
| vaultpanel-led-auto | Automatic LED script, non-root account | Boot +30 seconds; 30 seconds after activation | Timer disabled |
| vaultpanel-led-schedule | Scheduled LED script, non-root account | Local system time 08:00, 18:00, 22:00; Persistent=true | Timer enabled |
| vaultpanel-oled-custom | Python script executed directly, non-root account, restart always | None | Service disabled |
| vaultpanel-oled | Python via `venv/bin/python`, non-root account, restart always | None | Service disabled |
| pironman5 | Vendor executable with background/forking mode; no User directive | None | Service disabled |

## Findings and adaptation requirements

1. **Root execution boundary.** The LED-alert and vendor definitions omit User. System-manager services default to root in that case. The captured definitions do not establish whether those services are currently running. Do not replicate root execution without a narrowly scoped privilege design. [systemd.exec](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec)
2. **Authentication mismatch.** The recovered LED scripts call `/api/alerts` without authentication. The hardened preview rejects those requests. The scripts also require an explicit hardware opt-in that the captured service files do not provide. Do not bypass either boundary; design a restricted read-only credential flow or a direct local collector interface before enabling automation. Never embed credentials in command arguments or published units.
3. **Preview startup mismatch.** The main service capture neither supplies the new application password nor specifies an environment file. It uses `venv`, while the documented local preview creates `.venv`. Copying the capture is not an installation method.
4. **Persistent schedule catch-up.** The schedule timer can catch up after downtime, but its script only acts when the current minute is exactly one of its three configured times. A delayed/catch-up invocation can therefore perform no action. The fix must select the desired state from a time interval and arbitrate against active alerts, rather than only matching the trigger minute. Do not change the live device until tested. [systemd.timer](https://freedesktop.org/software/systemd/man/latest/systemd.timer.html)
5. **Timer semantics.** Persistent affects calendar timers; it does not add downtime catch-up to the hourly timer's monotonic OnBootSec/OnUnitActiveSec schedule. Activation-relative periods are not guaranteed wall-clock intervals, and timer accuracy can delay invocation. The LED-auto timer implicitly targets its same-named service. [systemd.timer](https://freedesktop.org/software/systemd/man/latest/systemd.timer.html)
6. **Competing hardware writers.** Multiple LED timers and both OLED services exist. Their presence does not prove concurrent execution, but enabling them together without coordination could cause conflicting output. Select one controller per resource and implement explicit alert/schedule priority and locking.
7. **Missing privileges and deployment evidence.** User-level scripts invoke sudo and access hardware. Actual sudo rules, groups, executable permissions, GPIO/I2C mapping and driver versions remain unknown. The references contain no resource isolation or privilege restrictions. Adding NoNewPrivileges blindly would also prevent their existing sudo approach; privilege separation must be designed as a whole.
8. **OLED direct execution.** The custom OLED service executes its Python file directly. The imported text selection did not preserve executable permission, so the reference cannot launch that file as-is. A future reviewed unit should invoke a verified interpreter explicitly. Hardware libraries and state/logo files still need validation.

## Wider infrastructure evidence

The supplied unit-file listing included apcupsd, Unbound, Samba, Pi-hole, Netdata, smartmontools and Tailscale. This establishes installation/enablement evidence, not their configuration or health. The similarly matched CUPS entries are printing services and excluded from NAS scope. The generic ups-monitor unit was masked; that alone does not establish whether apcupsd shutdown protection works.

## Validation and next inputs

Reference names and timer-to-service mappings were checked locally; script targets were matched to the supplied source tree. There is no `systemd-analyze verify` or target-device execution result. File suffixes are deliberately `.reference` and no installer is provided. Selected sudo/cron and reverse-proxy configuration has subsequently been reviewed in [configuration audit](CONFIGURATION_AUDIT.md). Storage evidence is now recorded in [storage audit](STORAGE_AUDIT.md); effective privileges and restore capability remain to be verified. UPS testing is excluded because the owner reports it disconnected. Graphics are covered in [asset review](ASSETS.md).
