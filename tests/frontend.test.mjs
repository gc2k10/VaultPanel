import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

function harness(script) {
  const elements = [];
  function element() {
    const el = {innerHTML: '', textContent: '', value: '', style: {}, dataset: {},
      classList: {add() {}, remove() {}, toggle() {}}, addEventListener() {},
      appendChild(child) {this.children.push(child);}, children: []};
    elements.push(el);
    return el;
  }
  const ids = new Map();
  const context = vm.createContext({document: {
    getElementById(id) {if (!ids.has(id)) ids.set(id, element()); return ids.get(id);},
    createElement: element, querySelectorAll: () => [], addEventListener() {},
  }, setInterval() {}, setTimeout() {}, fetch: () => new Promise(() => {})});
  vm.runInContext(fs.readFileSync('static/js/safe-html.js', 'utf8'), context);
  vm.runInContext(fs.readFileSync('static/js/' + script, 'utf8'), context);
  return {context, elements};
}

for (const script of ['app.js', 'app_retro.js']) {
  test(`${script}: hostile telemetry is escaped at every rendered HTML sink`, () => {
    const {context, elements} = harness(script);
    context.evil = '<img src=x onerror="attack()">';
    vm.runInContext(`
      renderServices({services: [{name: evil, active: false, active_text: evil, port: evil, since: evil, since_short: evil}]});
      renderCooling({fans: [{label: evil, rpm: evil}], led: {}});
      renderStorage({root: {}, btrfs: {}, devices: [{name: evil, model: evil, size: evil, smart_health: evil, temperature_c: evil}]});
      renderAlerts({alerts: [{source: evil, message: evil, level: evil}], history: [{timestamp: evil, message: evil}]});
    `, context);
    const html = elements.map(el => el.innerHTML).join('\n');
    assert.ok(html.includes('&lt;'));
    assert.doesNotMatch(html, /<img/i);
  });
}
