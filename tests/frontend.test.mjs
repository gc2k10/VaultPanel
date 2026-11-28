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
  }, AbortController, clearTimeout() {}, setInterval() {}, setTimeout() {}, fetch: () => new Promise(() => {})});
  vm.runInContext(fs.readFileSync('static/js/safe-html.js', 'utf8'), context);
  vm.runInContext(fs.readFileSync('static/js/' + script, 'utf8'), context);
  return {context, elements};
}

for (const script of ['app.js', 'app_retro.js']) {
  test(`${script}: unavailable service is labelled UNKNOWN`, () => {
    const {context, elements} = harness(script);
    vm.runInContext(`renderServices({services: [{name: 'Example', active: null, active_text: 'unknown'}]})`, context);
    const html = elements.map(el => el.innerHTML).join('\n');
    assert.match(html, /UNKNOWN/);
    assert.doesNotMatch(html, /OFFLINE|FAILED/);
  });
  test(`${script}: hostile telemetry is escaped at every rendered HTML sink`, () => {
    const {context, elements} = harness(script);
    context.evil = '<img src=x onerror="attack()">';
    vm.runInContext(`
      renderServices({services: [{name: evil, description: evil, active: false, active_text: evil, port: evil, since: evil, since_short: evil}]});
      renderCooling({fans: [{label: evil, rpm: evil}], led: {}});
      renderStorage({root: {}, btrfs: {}, devices: [{name: evil, model: evil, size: evil, smart_health: evil, temperature_c: evil}]});
      renderAlerts({alerts: [{source: evil, message: evil, level: evil}], history: [{timestamp: evil, message: evil}]});
    `, context);
    const html = elements.map(el => el.innerHTML).join('\n');
    assert.ok(html.includes('&lt;'));
    assert.doesNotMatch(html, /<img/i);
  });
}

for (const script of ['app.js', 'app_retro.js']) {
  test(`${script}: RAID membership is independent of a successful BTRFS scrub`, () => {
    const {context} = harness(script);
    for (const [mdraid, expected] of [
      [undefined, 'UNKNOWN'], [{available: false, arrays: []}, 'UNKNOWN'],
      [{available: true, arrays: []}, 'UNKNOWN'],
      [{available: true, arrays: [{status: 'degraded', healthy: false}]}, 'DEGRADED'],
      [{available: true, arrays: [{status: 'busy', healthy: null}]}, 'BUSY'],
      [{available: true, arrays: [{status: 'ok', healthy: true}]}, 'MEMBERS PRESENT'],
      [{available: true, arrays: [{status: 'ok', healthy: true}, {status: 'unknown', healthy: null}]}, 'UNKNOWN'],
    ]) {
      context.storage = {root: {}, devices: [], btrfs: {healthy: true}, mdraid};
      vm.runInContext('renderStorage(storage)', context);
      assert.equal(vm.runInContext("document.getElementById('raidStatus').textContent", context), expected);
    }
  });
}
