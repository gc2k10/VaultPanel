import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { inspect, scan } from '../scripts/review-files.mjs';
import { exportSource } from '../scripts/export-source.mjs';

test('flags synthetic sensitive values without returning them', () => {
  const input = ['password=' + 'synthetic-value', '-----BEGIN ' + 'PRIVATE KEY-----', 'ghp_' + 'a'.repeat(30), ['person', 'example.org'].join('@'), ['192','168','1','5'].join('.')].join('\n');
  const findings = inspect(input);
  for (const rule of ['credential-assignment','private-key','token','email','ipv4']) assert.ok(findings.some(f => f.rule === rule));
  assert.ok(!JSON.stringify(findings).includes('synthetic-value'));
});

test('review placeholders are accepted; real-looking URLs are flagged', () => {
  assert.deepEqual(inspect(['SECRET=REPLACE_ME', '127.0.0.1', 'https://vaultpanel.example.invalid'].join('\n')), []);
  assert.ok(inspect('https://' + 'private.example.org').some(f => f.rule === 'url-review'));
});

function fixture(t) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'vaultpanel-test-'));
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  const root = path.join(dir, 'source'); fs.mkdirSync(root);
  return { dir, root, manifest: path.join(dir, 'manifest'), dest: path.join(dir, 'review') };
}

test('export copies only listed files and refuses overwrite', t => {
  const { root, manifest, dest } = fixture(t);
  fs.writeFileSync(path.join(root, 'app.js'), 'original');
  fs.writeFileSync(path.join(root, 'unlisted.js'), 'private');
  fs.writeFileSync(manifest, 'app.js\n');
  assert.equal(exportSource(root, manifest, dest), 1);
  assert.deepEqual(fs.readdirSync(dest), ['app.js']);
  assert.equal(fs.readFileSync(path.join(root, 'app.js'), 'utf8'), 'original');
  assert.equal(fs.statSync(path.join(dest, 'app.js')).mode & 0o777, 0o600);
  assert.throws(() => exportSource(root, manifest, dest));
});

test('export refuses traversal, secrets, directories, symlinks and partial validation', t => {
  const { root, manifest, dest } = fixture(t);
  fs.writeFileSync(path.join(root, 'safe.js'), 'safe');
  fs.writeFileSync(path.join(root, '.env'), 'sensitive');
  fs.mkdirSync(path.join(root, 'folder'));
  fs.symlinkSync(path.join(root, 'safe.js'), path.join(root, 'link.js'));
  for (const entry of ['../manifest', '/etc/passwd', '.env', 'folder', 'link.js', 'missing.js']) {
    fs.writeFileSync(manifest, 'safe.js\n' + entry);
    assert.throws(() => exportSource(root, manifest, dest));
    assert.equal(fs.existsSync(dest), false);
  }
  fs.writeFileSync(manifest, 'safe.js');
  assert.throws(() => exportSource(root, manifest, path.join(root, 'nested')));
});

test('scanner flags uninspected binaries and symlinks', t => {
  const { root } = fixture(t);
  fs.writeFileSync(path.join(root, 'asset'), Buffer.from([0, 255]));
  fs.symlinkSync(path.join(root, 'asset'), path.join(root, 'link'));
  const rules = scan(root).map(f => f.rule);
  assert.ok(rules.includes('binary-not-inspected'));
  assert.ok(rules.includes('symlink-not-inspected'));
});

test('scanner catches prefixed environment secrets and credential URLs', () => {
  assert.ok(inspect('VAULTPANEL_SESSION_SECRET=' + 'synthetic-value').some(f => f.rule === 'credential-assignment'));
  const url = 'https://' + 'test-user:test-value@' + 'example.invalid';
  assert.ok(inspect(url).some(f => f.rule === 'credential-url'));
});

test('export rejects binary, oversized and duplicate selections before writing', t => {
  const { root, manifest, dest } = fixture(t);
  fs.writeFileSync(path.join(root, 'binary.js'), Buffer.from([0, 255]));
  fs.writeFileSync(path.join(root, 'large.js'), 'a'.repeat(2 * 1024 * 1024 + 1));
  fs.writeFileSync(path.join(root, 'safe.js'), 'safe');
  for (const entry of ['binary.js', 'large.js', 'safe.js\nsafe.js']) {
    fs.writeFileSync(manifest, entry);
    assert.throws(() => exportSource(root, manifest, dest));
    assert.equal(fs.existsSync(dest), false);
  }
});
