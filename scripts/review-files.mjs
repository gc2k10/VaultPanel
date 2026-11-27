import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

// Heuristics only. Values are deliberately never included in findings.
export function inspect(text) {
  const rules = [
    ['private-key', /-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----/],
    ['token', /(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[A-Z0-9]{16})/],
    ['credential-url', /https?:\/\/[^\s/@:]+:[^\s/@]+@/],
    ['email', /\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b/i],
    ['ipv4', /\b(?:\d{1,3}\.){3}\d{1,3}\b/g],
    ['ipv6', /(?:[a-f0-9]{1,4}:){2,}[a-f0-9:]+/i],
    ['home-path', /\/(?:home|Users)\/[^\s/]+/],
    ['url-review', /https?:\/\/[^\s)"'<>]+/g],
    ['credential-assignment', /\b(?:[a-z0-9]+_)*(?:password|passwd|token|secret|api_key|session_secret)\b\s*[=:]\s*["']?([^\s"'#;,]+)/i],
  ];
  const findings = [];
  text.split(/\r?\n/).forEach((line, i) => {
    for (const [rule, regex] of rules) {
      for (const match of line.matchAll(new RegExp(regex.source, regex.flags.includes('g') ? regex.flags : regex.flags + 'g'))) {
        const value = match[1] ?? match[0];
        if (rule === 'ipv4' && ['127.0.0.1', '0.0.0.0'].includes(value)) continue;
        if (rule === 'url-review') {
          try { if (new URL(value).hostname.endsWith('.invalid')) continue; } catch { /* review malformed URLs */ }
        }
        if (rule === 'credential-assignment' && /^(?:REPLACE_ME|CHANGEME|\$\{[A-Z_]+\})$/.test(value)) continue;
        findings.push({ line: i + 1, rule });
      }
    }
  });
  return findings;
}

export function scan(root) {
  const findings = [];
  function walk(file) {
    const relative = path.relative(root, file) || '.';
    const stat = fs.lstatSync(file);
    if (stat.isSymbolicLink()) { findings.push({ file: relative, rule: 'symlink-not-inspected' }); return; }
    if (stat.isDirectory()) {
      for (const name of fs.readdirSync(file).sort()) {
        if (name !== '.git') walk(path.join(file, name));
      }
    } else if (stat.isFile()) {
      if (/^(?:\.env(?:\..+)?|id_rsa.*|id_ed25519.*)$/.test(path.basename(file)) && path.basename(file) !== '.env.example') findings.push({ file: relative, rule: 'sensitive-filename' });
      if (/\.(?:pem|key|p12|pfx|db|sqlite\d*|sql|dump|log|zip|gz|tar)$/i.test(file)) findings.push({ file: relative, rule: 'sensitive-file-type' });
      if (stat.size > 2 * 1024 * 1024) { findings.push({ file: relative, rule: 'oversize-not-inspected' }); return; }
      const data = fs.readFileSync(file);
      let text;
      try { text = new TextDecoder('utf-8', { fatal: true }).decode(data); }
      catch { findings.push({ file: relative, rule: 'binary-not-inspected' }); return; }
      if (data.includes(0)) { findings.push({ file: relative, rule: 'binary-not-inspected' }); return; }
      findings.push(...inspect(text).map(f => ({ file: relative, ...f })));
    } else findings.push({ file: relative, rule: 'special-file-not-inspected' });
  }
  walk(path.resolve(root));
  return findings;
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  try {
    const findings = scan(path.resolve(process.argv[2] || '.'));
    for (const finding of findings) console.log(JSON.stringify(finding));
    console.log(`Review findings: ${findings.length}. Git history and manual privacy review are separate.`);
    process.exitCode = findings.length ? 1 : 0;
  } catch { console.error('Scan failed; no clearance to publish. Check path and permissions.'); process.exitCode = 2; }
}
