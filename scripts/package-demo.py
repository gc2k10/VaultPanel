#!/usr/bin/env python3
"""Build a demo-only archive from an explicit public-file allowlist."""
import argparse
import importlib.util
from tempfile import TemporaryDirectory
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

parser = argparse.ArgumentParser()
parser.add_argument("--source-commit", required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
brand = json.loads((root / "tests/browser/brand.json").read_text())
slug = brand["repository"].rsplit("/", 1)[1]
logo = "chilifarm-original.png" if slug == "chili-farm" else "vaultpanel.png"
files = {
    "frontend/index.html": "index.html",
    "frontend/about.html": "about.html",
    "frontend/style.css": "style.css",
    "docs/demo-start.md": "README.md",
    "docs/releases/v0.1.0-demo.md": "RELEASE-NOTES.md",
    "docs/demo-validation.md": "VALIDATION.md",
    "LICENSE": "LICENSE",
}
for name in [logo, "favicon.ico", "favicon-32.png", "apple-touch-icon.png"]:
    files["frontend/assets/brand/" + name] = "assets/brand/" + name
# Include only the renderer's explicit, synthetic Retro export.
spec = importlib.util.spec_from_file_location('original_demo', root / 'scripts/build-original-demo.py')
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)
preview_temp = TemporaryDirectory(prefix='vaultpanel-demo-')
preview = Path(preview_temp.name) / 'original'
renderer.build(preview)
for name in ['index.html', 'retro.html', 'preview.js', 'preview-data.js', 'preview.css'] + ['static/' + a for a in renderer.ASSETS]:
    files[str(preview / name)] = 'original/' + name

manifest = {
    "project": brand["name"], "version": "0.1.0-demo",
    "source_commit": args.source_commit, "synthetic_data_only": True,
    "sha256": {},
}
out = root / "dist"
out.mkdir(exist_ok=True)
archive = out / (slug + "-v0.1.0-demo.zip")
with ZipFile(archive, "w", ZIP_DEFLATED) as bundle:
    for source, destination in files.items():
        data = (root / source).read_bytes()
        if not data:
            raise ValueError("Empty release file: " + source)
        manifest["sha256"][destination] = hashlib.sha256(data).hexdigest()
        bundle.writestr(destination, data)
    bundle.writestr("manifest.json", json.dumps(manifest, indent=2) + "\n")
print(archive)

preview_temp.cleanup()
