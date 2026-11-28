# VaultPanel Retro demo — Quick start

Open https://gc2k10.github.io/VaultPanel/ for the single Retro dashboard. All readings are synthetic; no NAS connection, login or installation is needed. The original Classic URL forwards to Retro. The About page contains project information, not a second dashboard.

## Local source preview

Use the isolated Python environment described in INSTALLATION.md. From the repository root:

```sh
python scripts/build-original-demo.py
python -m http.server 8000 --bind 127.0.0.1 --directory frontend
```

Open http://127.0.0.1:8000/. Use the six tabs to explore readings and service examples. Stop with Ctrl+C. The builder refuses to overwrite existing output; specify a fresh destination when rebuilding. See [original-demo.md](original-demo.md).

## Newly built standalone demo ZIP

Extract the complete ZIP into a fresh directory and serve it with `python3 -m http.server 8000 --bind 127.0.0.1` from that directory. No Python packages are needed to serve the exported files. The index opens Retro. Keep the original/ and assets/ directories intact. manifest.json records source provenance and file hashes.

Historical release archives are immutable and may contain older layouts. These instructions describe the current source and newly generated demo package, not a replacement of an existing release. The preview has no backend or functioning hardware controls and does not validate real sensors.
