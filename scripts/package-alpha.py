"""Export a versioned candidate from Git objects; never execute packaged code."""
import argparse
import hashlib
from pathlib import Path, PurePosixPath
import re
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
VERSION = re.compile(r'v(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)-(?:alpha|beta|rc)(?:\.(?:0|[1-9][0-9]*))?')


def build(version, root=ROOT, output=None):
    if not isinstance(version, str) or not VERSION.fullmatch(version):
        raise ValueError('Use an explicit prerelease version, for example v0.2.0-alpha')
    root = Path(root)
    def git(*args):
        return subprocess.check_output(['git', *args], cwd=root)
    commit = git('rev-parse', 'HEAD').decode().strip()
    if git('status', '--porcelain', '--untracked-files=no'):
        raise ValueError('Tracked worktree must match the candidate commit')
    entries = []
    for record in git('ls-tree', '-rz', commit).split(b'\0'):
        if not record:
            continue
        metadata, raw_name = record.split(b'\t', 1)
        mode, kind, sha = metadata.decode().split()
        name = raw_name.decode('utf-8')
        path = PurePosixPath(name)
        if mode not in {'100644', '100755'} or kind != 'blob' or path.is_absolute() or '..' in path.parts:
            raise ValueError('Unsafe source entry')
        if any(part in {'.git', 'private-intake', 'private-source', 'node_modules', '.venv', 'state', '__pycache__'} for part in path.parts):
            raise ValueError('Forbidden runtime/private path')
        if (path.name.startswith('.env') and path.name != '.env.example') or path.suffix.lower() in {'.key', '.pem', '.p12', '.pfx', '.db', '.log', '.zip', '.gz', '.tar', '.sql', '.dump'}:
            raise ValueError('Forbidden sensitive/archive filename')
        entries.append((name, int(mode, 8), git('cat-file', 'blob', sha)))
    output = Path(output) if output is not None else root / 'dist' / 'candidates' / version
    output.mkdir(parents=True, exist_ok=False)
    archive = output / f'VaultPanel-{version}.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as bundle:
        for name, mode, content in sorted(entries):
            entry = zipfile.ZipInfo('VaultPanel/' + name, (1980, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.create_system = 3
            entry.external_attr = mode << 16
            bundle.writestr(entry, content)
    with zipfile.ZipFile(archive) as bundle:
        assert bundle.testzip() is None
        assert len(bundle.namelist()) == len(entries)
        for name, mode, content in entries:
            assert bundle.read('VaultPanel/' + name) == content
            assert bundle.getinfo('VaultPanel/' + name).external_attr >> 16 == mode
    source = output / 'SOURCE_COMMIT.txt'
    source.write_text(commit + '\n')
    (output / 'SHA256SUMS.txt').write_text(''.join(
        hashlib.sha256(path.read_bytes()).hexdigest() + '  ' + path.name + '\n'
        for path in [archive, source]))
    return {'commit': commit, 'files': len(entries), 'archive': str(archive)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = build(args.version, output=args.output)
    print(f"Verified {result['files']} source files at {result['commit']}: {result['archive']}")
    print('Candidate only: no tag, release or deployment has been created.')
