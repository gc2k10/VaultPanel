import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

test('HTML substitutions cannot create tags or break quoted attributes', () => {
  const context = vm.createContext({});
  vm.runInContext(fs.readFileSync(new URL('../vaultpanel/static/js/safe-html.js', import.meta.url), 'utf8'), context);
  context.payload = '<img src=x onerror=alert(1)>"\'&';
  const html = vm.runInContext('safeHtml`<span title="${payload}">${payload}</span>`', context);
  assert.ok(!html.includes('<img'));
  assert.ok(html.includes('&lt;img'));
  assert.ok(html.includes('&quot;'));
  assert.ok(html.includes('&#39;'));
});

test('recovered frontends use escaped templates for dynamic innerHTML', () => {
  for (const name of ['app.js', 'app_retro.js']) {
    const source = fs.readFileSync(new URL('../vaultpanel/static/js/' + name, import.meta.url), 'utf8');
    assert.doesNotMatch(source, /innerHTML\s*=\s*`/);
    new vm.Script(source, { filename: name });
  }
});
