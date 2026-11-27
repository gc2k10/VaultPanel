# Asset review — 2026-11-28

The owner supplied eight graphics and confirmed ownership. They explicitly excluded one personal OLED logo and authorized public/MIT distribution for the remaining seven. The excluded image is not present in the repository or its new commits; the private original intake is preserved. Both OLED scripts display generic VaultPanel text when the optional logo file is absent. Hardware execution remains gated.

## Included images

| Repository path under vaultpanel/ | Dimensions | Use |
| --- | --- | --- |
| static/img/vplogo.png | 1099 × 565 | Optional retro header logo; existing ASCII header remains the default |
| static/android-chrome-192x192.png | 192 × 192 | Web manifest icon |
| static/android-chrome-512x512.png | 512 × 512 | Web manifest icon |
| static/apple-touch-icon.png | 180 × 180 | Touch icon |
| static/favicon-16x16.png | 16 × 16 | Browser icon |
| static/favicon-32x32.png | 32 × 32 | Browser icon |
| static/favicon.ico | 16, 32, 48 pixel frames | Multi-size browser icon |

All included images were visually inspected, with ICO also converted privately for inspection. No visible host addresses, credentials or personal contact details were identified. This is a review based on the owner's provenance statement, not an independent trademark clearance.

The large PNG contained EXIF and international text chunks. These were removed by filtering PNG chunks, without regenerating pixels or recompressing IDAT data. Remaining PNGs contained only structural/image chunks. PNG CRCs and source-to-publication IDAT equality were checked. ICO headers, frame bounds and trailing zero padding were checked; the ICO was not modified. Private hash inventories record the original and prepared files.

The manifest now has a VaultPanel name and icon paths relative to its `/static/` location. Both templates reference icons via Flask static URLs. Authentication still applies to static assets, so installed-app icon fetching by an operating system may vary; no offline/PWA support is claimed. No service worker was added.

The repository MIT license applies to these seven images as authorized by their owner. Do not reintroduce the withheld personal OLED image or raw private metadata in a later import.
