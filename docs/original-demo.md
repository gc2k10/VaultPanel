# Original VaultPanel interface preview

The original application's classic and retro layouts can be viewed without installing on a NAS:

- Classic: https://gc2k10.github.io/VaultPanel/original/index.html
- Retro: https://gc2k10.github.io/VaultPanel/original/retro.html

These pages are rendered from the reviewed application templates and use the same CSS and JavaScript. A permanent banner distinguishes the preview from live telemetry. Every reading is fictional. Controls remain disabled. The browser serves telemetry from bundled synthetic data, never from a server; Content Security Policy additionally blocks network connections for telemetry. Opening the page downloads public assets from GitHub Pages, not from a NAS.

This is the sanitized read-only application layout. Personal configuration and private graphics are not reproduced. The separate project presentation remains available at the website root. The preview does not install anything, validate hardware, or change the published alpha release.

## Build a local static preview

From the source checkout, using the isolated development environment described in INSTALLATION.md:

```sh
python scripts/build-original-demo.py
python -m http.server 8000 --bind 127.0.0.1 --directory frontend
```

Open http://127.0.0.1:8000/original/index.html or /original/retro.html. Stop with Ctrl+C. The builder refuses to overwrite an existing output directory; for another build, provide a new empty destination path as its argument. It imports the template engine only, never the application, collectors or hardware adapter. Only explicitly listed public assets are copied.

CI builds the preview and checks both layouts across Chromium, Firefox and WebKit at four widths, including tab navigation, disabled writes, synthetic readings, no backend requests and layout switching.
