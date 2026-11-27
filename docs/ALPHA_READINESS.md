# v0.1.0-alpha readiness

Status on 2026-11-27: draft review candidate, not released.

## Proposed scope awaiting owner agreement

A local monitoring dashboard with classic and retro layouts. CPU, memory, storage, services and available sensor readings can be displayed. Missing readings remain unknown. Optional command diagnostics require explicit configuration. Fan, LED, OLED and backup controls stay unavailable: all four write endpoints deny requests. This is a first monitoring milestone, not a commitment to remove those features from future versions.

## Information needed from the owner

1. Confirm whether this monitoring-only scope is suitable for the first alpha.
2. Select a license for the team's original code. The owner confirmed authorship and rights on 2026-11-27; no license was assigned automatically.
3. Confirm the target OS/version, Python version, Raspberry Pi model and case/controller model. Provide a disposable test system or sanitized diagnostic fixtures to validate the expected telemetry. Do not send passwords, keys, serial numbers, production configuration or NAS data.

## Validation still required

- Verify real target-platform telemetry in a disposable environment; mocked Linux CI does not validate sensors, permissions or vendor output.
- Manually assess unresolved contrast checks and screen-reader use; automated accessibility tests are not WCAG certification.
- Review the candidate and choose an explicit version/tag only after agreed release gates pass. No release tag or GitHub Release exists as a result of this work.
- Before future hardware controls: validate failure-safe behavior, permissions, thermal limits and controller ownership on disposable hardware. Before any backup claim: implement and test restoration. These features must not be advertised as working in the proposed read-only alpha.

The production NAS must remain unchanged. No deployment or production connection is part of these checks.
