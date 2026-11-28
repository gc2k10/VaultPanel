#!/usr/bin/env python3
"""Render the reviewed UI with synthetic data; never import app/collectors."""
import json
from pathlib import Path
import shutil
import sys
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ('css/style_retro.css', 'js/safe-html.js',
          'js/app_retro.js', 'favicon.ico', 'apple-touch-icon.png')


def build(destination):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=False)
    env = Environment(loader=FileSystemLoader(ROOT / 'templates'), autoescape=select_autoescape(['html']))
    def asset_url(endpoint, filename):
        if endpoint != 'static' or filename not in (*ASSETS, 'site.webmanifest'):
            raise ValueError('Unreviewed template asset')
        return 'static/' + filename
    banner = '''<aside class="demo-notice" aria-label="Demonstration notice"><strong>DEMO — SYNTHETIC DATA ONLY</strong><span>Original VaultPanel interface. No NAS connection. Controls disabled.</span><nav aria-label="Project information"><a href="../about.html">About the project</a></nav></aside>'''
    for source, target, title in [('index_retro.html', 'retro.html', 'VaultPanel — Retro demo')]:
        html = env.get_template(source).render(title=title, url_for=asset_url)
        html = html.replace('<link rel="manifest" href="static/site.webmanifest">', '')
        html = html.replace('</head>', '<meta name="referrer" content="no-referrer"><meta http-equiv="Content-Security-Policy" content="default-src \'self\'; connect-src \'none\'; script-src \'self\'; style-src \'self\' \'unsafe-inline\'; object-src \'none\'; base-uri \'none\'"><link rel="stylesheet" href="preview.css"></head>')
        html = html.replace('<body>', '<body>' + banner).replace('href="/"', 'href="index.html"')
        html = html.replace('<script src="static/js/safe-html.js">', '<script src="preview-data.js"></script><script src="preview.js"></script><script src="static/js/safe-html.js">')
        (destination / target).write_text(html)
    (destination / 'index.html').write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=retro.html"><title>VaultPanel Retro</title></head><body><a href="retro.html">Open VaultPanel Retro</a></body></html>')
    for name in ASSETS:
        source = ROOT / 'static' / name
        if source.is_symlink():
            raise ValueError('Symlink asset rejected')
        target = destination / 'static' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    fixture = json.loads((ROOT / 'frontend/preview/telemetry.json').read_text())
    (destination / 'preview-data.js').write_text('window.VAULTPANEL_DEMO_DATA = ' + json.dumps(fixture) + ';\n')
    for name in ['preview.js', 'preview.css']:
        shutil.copyfile(ROOT / 'frontend/preview' / name, destination / name)
    print('Built original layouts with synthetic data only:', destination)


if __name__ == '__main__':
    build(sys.argv[1] if len(sys.argv) > 1 else ROOT / 'frontend/original')
