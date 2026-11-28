# Original VaultPanel interface preview

Retro is the only dashboard layout. Open https://gc2k10.github.io/VaultPanel/ or https://gc2k10.github.io/VaultPanel/original/retro.html without installing on a NAS. The former Classic URL redirects to Retro. The layout switcher and Classic template/assets have been removed.

The Retro preview is rendered from the reviewed application templates and uses the same CSS and JavaScript. A permanent banner distinguishes the preview from live telemetry. Every reading is fictional. Controls remain disabled. The browser serves telemetry from bundled synthetic data, never from a server; Content Security Policy additionally blocks network connections for telemetry. Opening the page downloads public assets from GitHub Pages, not from a NAS.

The Services examples include Samba (file sharing), Tailscale (private device networking), Pi-hole (DNS filtering), Netdata (performance metrics), Nginx (web serving/proxy), SSH (encrypted terminal access), and Nextcloud (file sync, calendars and contacts). Names and online states are explicitly simulated; they are not detected installations or a promise of dedicated integration. Nothing is installed or enabled by viewing the demo.

This is the sanitized read-only application layout. Personal configuration and private graphics are not reproduced. Project information remains available at `/about.html`; the website root opens Retro. The preview does not install anything, validate hardware, or change the published alpha release.

## Build a local static preview

From the source checkout, using the isolated development environment described in INSTALLATION.md:

```sh
python scripts/build-original-demo.py
python -m http.server 8000 --bind 127.0.0.1 --directory frontend
```

Open http://127.0.0.1:8000/ or /original/retro.html. Stop with Ctrl+C. The builder refuses to overwrite an existing output directory; for another build, provide a new empty destination path as its argument. It imports the template engine only, never the application, collectors or hardware adapter. Only explicitly listed public assets are copied.

CI builds the preview and checks Retro across Chromium, Firefox and WebKit at four widths, including tab navigation, disabled writes, synthetic readings, no backend requests and legacy-link forwarding.
