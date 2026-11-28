# Public Retro demo

The website root forwards to `original/retro.html`, built from the single application template. `original/index.html` forwards to the same page for old links. Classic and the earlier presentation dashboard have been removed. `about.html` remains a project information page.

Run `python scripts/build-original-demo.py` in the prepared development environment before serving this directory locally. The export contains only allowlisted public assets and synthetic telemetry. See [demo instructions](../docs/demo-start.md). Do not copy NAS configuration into the fixtures.
