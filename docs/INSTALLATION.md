# Local read-only preview

## Requirements

Use an isolated checkout on a test machine. The intended runtime is Python 3.11+ on Linux; the intake tests were also run with the available Python 3.9.6 on macOS. A supported Raspberry Pi OS/Python combination and production deployment have not yet been validated. Node.js 22+ is needed only for repository tooling/frontend tests.

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r vaultpanel/requirements.txt
python -m unittest discover -s tests -p 'test_*.py'
node --test tests/*.test.mjs
```

Generate a fresh session password locally, without placing it in shell history:

```sh
export VAULTPANEL_PASSWORD="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
printf '%s\n' "$VAULTPANEL_PASSWORD"
python vaultpanel/app.py
```

Open `http://127.0.0.1:8090` or `http://127.0.0.1:8090/retro`. The browser requests username `vaultpanel` and the generated password. Keep the password local; do not paste it into issues, screenshots or logs. The application does not automatically load `.env` files.

The development server binds only to loopback. For a remote test host, use an SSH tunnel such as `ssh -N -L 8090:127.0.0.1:8090 USER@HOST`, replacing USER and HOST locally. HTTP Basic authentication must stay inside loopback/SSH; this is not a public HTTPS deployment. Do not expose the port, run as root, grant blanket sudo or add the process to the Docker group to make diagnostics work.

## Expected limitations

- All write methods are blocked after authentication, including backup, OLED, LED and fan endpoints. No environment switch enables web writes.
- Missing Linux tools or privileges yield missing/unknown data. Collectors may probe external connectivity; review `check_internet` and `check_dns` before use.
- Storage paths and device names reflect recovered assumptions and require operator review. No formatting, RAID creation or service installation is performed.
- The diagnostic script assumes mdraid, while other collectors assume BTRFS. Confirm actual topology before trusting storage indicators.
- Hardware dependencies are listed separately in `vaultpanel/requirements-hardware.txt`; do not install or execute these adapters for a browser preview. Their opt-in gate is not a validation certificate.
- Original images, service units, timers, sudo rules and OLED state files are not included. The frontends use a text title instead of missing logos.
- The development server, synchronous collectors and Basic authentication are not a production architecture. Rate limiting, managed authentication, privilege separation, recovery and device testing remain release blockers.

Stop with Ctrl-C and unset the password with `unset VAULTPANEL_PASSWORD`. The preview does not install a system service or alter the existing Raspberry Pi deployment.
