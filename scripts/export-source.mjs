import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

export function exportSource(rootArg, manifestArg, destinationArg) {
  const root = fs.realpathSync(rootArg);
  const destination = path.resolve(destinationArg);
  const parent = fs.realpathSync(path.dirname(destination));
  const resolvedDestination = path.join(parent, path.basename(destination));
  if (resolvedDestination === root || resolvedDestination.startsWith(root + path.sep)) throw new Error('Destination must be outside the source root');
  if (fs.existsSync(destination)) throw new Error('Destination must not exist');
  const entries = fs.readFileSync(manifestArg, 'utf8').split(/\r?\n/).map(s => s.trim()).filter(s => s && !s.startsWith('#'));
  if (!entries.length || new Set(entries).size !== entries.length) throw new Error('Use a nonempty, unique explicit file list');
  const selected = entries.map(relative => {
    const parts = relative.split('/');
    if (path.isAbsolute(relative) || parts.some(p => !p || p === '..' || p === '.') || relative.includes('\\')) throw new Error('Unsafe manifest path');
    let file = root;
    for (const part of parts) {
      if (['.git', '.ssh', 'node_modules', 'private-intake'].includes(part)) throw new Error('Excluded directory');
      file = path.join(file, part);
      if (fs.lstatSync(file).isSymbolicLink()) throw new Error('Symlinks are not allowed');
    }
    const name = parts.at(-1);
    if ((name.startsWith('.env') && name !== '.env.example') || /^id_(?:rsa|ed25519)/.test(name) || /\.(?:pem|key|p12|pfx|db|sqlite\d*|sql|dump|log|zip|gz|tar)$/i.test(name)) throw new Error('Sensitive file type excluded');
    const stat = fs.statSync(file);
    if (!stat.isFile() || stat.size > 2 * 1024 * 1024) throw new Error('Only regular source files up to 2 MiB are allowed');
    const data = fs.readFileSync(file);
    new TextDecoder('utf-8', { fatal: true }).decode(data);
    if (data.includes(0)) throw new Error('Binary files require separate manual review');
    return { relative, data };
  });
  // Validate and read the complete list before creating any output.
  fs.mkdirSync(destination, { mode: 0o700 });
  for (const { relative, data } of selected) {
    const out = path.join(destination, relative);
    fs.mkdirSync(path.dirname(out), { recursive: true, mode: 0o700 });
    fs.writeFileSync(out, data, { flag: 'wx', mode: 0o600 });
  }
  return selected.length;
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  if (process.argv.length !== 5) { console.error('Usage: node scripts/export-source.mjs SOURCE_ROOT MANIFEST NEW_PRIVATE_DESTINATION'); process.exitCode = 2; }
  else {
    try { console.log(`Copied ${exportSource(...process.argv.slice(2))} files to PRIVATE review staging. Nothing was uploaded or sanitized.`); }
    catch { console.error('Export refused or failed. Check the manifest, file types, paths and permissions. Any partial destination remains private; no files were removed.'); process.exitCode = 2; }
  }
}
