# Licensing and dependency intake

The baseline repository has no license. This preparation does not assign a license to missing, vendor or third-party code. MIT is a candidate for original project code only after ownership is confirmed; no license grant is asserted here.

Before importing a component, record:

| Field | Required information |
| --- | --- |
| Component and location | Exact files and module |
| Provenance | Author, upstream URL, version/commit, acquisition method |
| Permission | Applicable license and evidence of redistribution rights |
| Obligations | Notices, attribution, source availability and modifications |
| Dependencies | Direct/transitive versions, lockfile and license inventory |
| Assets | Separate rights for icons, fonts, photos, logos and screenshots |

Current inventory: original baseline README; newly authored preparation documents and Node.js tools; no application dependencies or vendored assets. The tools import only Node.js built-ins and require no package installation. This is not an SBOM for the missing application or Raspberry Pi operating system.

Do not infer licenses of Samba, Nextcloud, Pi-hole, Unbound, Netdata, Tailscale, display drivers or vendor software from their names. Check the exact versions and files actually imported. Prefer referencing upstream installation instructions over copying vendor code until rights are established. Preserve existing notices when importing permitted material.
