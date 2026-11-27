"""Build an exact tracked-source alpha ZIP; never include untracked host data."""
import hashlib
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
if subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=no'], cwd=ROOT):
    raise SystemExit('Tracked worktree must match the release commit')
files = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')[:-1]
for name in files:
    path = ROOT / name
    if path.is_symlink() or not path.is_file() or Path(name).is_absolute() or '..' in Path(name).parts:
        raise SystemExit('Unsafe source entry')
    if any(part in {'.git', 'private-intake', 'private-source', 'node_modules', '.venv', 'state', '__pycache__'} for part in Path(name).parts):
        raise SystemExit('Forbidden runtime/private path')
    if (path.name.startswith('.env') and path.name != '.env.example') or path.suffix in {'.key', '.pem', '.db', '.log', '.zip', '.gz'}:
        raise SystemExit('Forbidden sensitive/archive filename')
output = ROOT / 'dist' / 'alpha'
output.mkdir(parents=True, exist_ok=True)
archive = output / 'VaultPanel-v0.1.0-alpha.zip'
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as bundle:
    for name in sorted(files):
        entry = zipfile.ZipInfo('VaultPanel/' + name, (1980, 1, 1, 0, 0, 0))
        entry.compress_type = zipfile.ZIP_DEFLATED
        entry.external_attr = 0o100644 << 16
        bundle.writestr(entry, (ROOT / name).read_bytes())
with zipfile.ZipFile(archive) as bundle:
    assert bundle.testzip() is None
    assert len(bundle.namelist()) == len(files)
    for name in files:
        assert bundle.read('VaultPanel/' + name) == (ROOT / name).read_bytes()
source = output / 'SOURCE_COMMIT.txt'
source.write_text(commit + '\n')
(output / 'SHA256SUMS.txt').write_text(''.join(
    hashlib.sha256(path.read_bytes()).hexdigest() + '  ' + path.name + '\n'
    for path in [archive, source]))
print(f'Verified {len(files)} source files at {commit}')
