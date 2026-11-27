// Start tests/browser_server.py first. Requires Playwright and a Chrome installation.
const playwright = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const fixture = JSON.parse(fs.readFileSync(path.join(__dirname, 'telemetry.json'), 'utf8'));

(async () => {
  const engine = process.env.VAULTPANEL_BROWSER || 'chromium';
  assert.ok(['chromium', 'firefox', 'webkit'].includes(engine));
  const browser = await playwright[engine].launch({...(engine === 'chromium' ? {channel: 'chrome'} : {}), headless: true});
  let passed = 0;
  try {
    for (const route of ['/', '/retro']) {
      for (const width of [390, 1280]) {
        const page = await browser.newPage({viewport: {width, height: 900}});
        const errors = [];
        const writes = [];
        page.on('pageerror', e => errors.push(e.message));
        page.on('request', r => {if (r.method() === 'POST') writes.push(r.url());});
        await page.goto('http://127.0.0.1:8091' + route);
        await page.getByText('telemetry refreshed', {exact: false}).waitFor();
        assert.equal(await page.locator('#hostname').textContent(), route === '/' ? 'example-host // VAULTPANEL' : 'example-host');
        if (route === '/' && width === 390) {
          const host = await page.locator('#hostname').boundingBox();
          const clock = await page.locator('#clock').boundingBox();
          assert.ok(clock.y >= host.y + host.height, 'Mobile clock must be below hostname');
        }
        for (const tab of ['overview', 'cooling', 'storage', 'services', 'network', 'alerts']) {
          await page.locator(`[data-tab="${tab}"]`).click();
          assert.ok(await page.locator(`#tab-${tab}`).isVisible());
          assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), `${route} ${width} ${tab}: horizontal overflow`);
        }
        assert.equal(await page.locator('button.action-btn:not([disabled]), button.preset-btn:not([disabled])').count(), 0);
        assert.deepEqual(writes, []);
        assert.deepEqual(errors, []);
        const dest = process.env.VAULTPANEL_SCREENSHOTS;
        if (dest) {
          fs.mkdirSync(dest, {recursive: true});
          await page.locator('[data-tab="overview"]').click();
          await page.screenshot({path: path.join(dest, `${route === '/' ? 'classic' : 'retro'}-${width}.png`), fullPage: true});
        }
        passed++;
        console.log(`PASS ${route} ${width}: tabs, controls, layout, console`);
        await page.close();
      }
      const page = await browser.newPage();
      await page.route('**/api/overview', r => r.fulfill({status: 503, body: '{}'}));
      await page.goto('http://127.0.0.1:8091' + route);
      await page.getByText('Telemetry unavailable.', {exact: false}).waitFor();
      assert.equal(await page.locator('#globalStatus').textContent(), 'STALE');
      await page.unroute('**/api/overview');
      await page.getByText('telemetry refreshed', {exact: false}).waitFor({timeout: 12000});
      passed++;
      console.log(`PASS ${route}: API failure and automatic recovery`);
      const hostile = JSON.parse(JSON.stringify(fixture.services));
      hostile.services[0].name = '<img src=x onerror="window.attacked=true">';
      await page.route('**/api/services', r => r.fulfill({json: hostile}));
      await page.locator('[data-tab="services"]').click();
      await page.locator('#servicesTable').getByText(/<img/i).waitFor({timeout: 12000});
      assert.equal(await page.locator('#servicesTable img').count(), 0);
      assert.equal(await page.evaluate(() => window.attacked), undefined);
      passed++;
      console.log(`PASS ${route}: hostile telemetry displayed as text`);
      await page.close();

      const longPage = await browser.newPage({viewport: {width: 390, height: 900}});
      await longPage.route('**/api/*', async r => {
        const key = r.request().url().split('/').pop();
        const data = JSON.parse(JSON.stringify(fixture[key]));
        if (key === 'overview') data.hostname = 'example-'.repeat(30);
        if (key === 'services') data.services[0].name = 'example-'.repeat(30);
        if (key === 'alerts') data.alerts[0].message = 'LongMessage'.repeat(30);
        await r.fulfill({json: data});
      });
      await longPage.goto('http://127.0.0.1:8091' + route);
      await longPage.getByText('telemetry refreshed', {exact: false}).waitFor();
      for (const tab of ['overview', 'services', 'alerts']) {
        await longPage.locator(`[data-tab="${tab}"]`).click();
        assert.ok(await longPage.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), `${route}: long ${tab} overflows`);
      }
      passed++;
      console.log(`PASS ${route}: long telemetry fits mobile width`);
      await longPage.close();

      const slowPage = await browser.newPage();
      let slowRequests = 0;
      await slowPage.route('**/api/overview', r => {
        slowRequests++;
        return new Promise(resolve => setTimeout(() => r.abort().catch(() => {}).finally(resolve), 12000));
      });
      await slowPage.route('**/api/services', r => r.fulfill({status: 503, body: '{}'}));
      await slowPage.goto('http://127.0.0.1:8091' + route);
      await slowPage.waitForTimeout(6000);
      assert.equal(slowRequests, 1, 'A fast failure must not permit overlapping a slow sibling request');
      await slowPage.getByText('Telemetry unavailable.', {exact: false}).waitFor({timeout: 12000});
      assert.equal(slowRequests, 1, 'Polling must not overlap an in-flight refresh');
      await slowPage.unroute('**/api/overview');
      await slowPage.unroute('**/api/services');
      await slowPage.getByText('telemetry refreshed', {exact: false}).waitFor({timeout: 12000});
      passed++;
      console.log(`PASS ${route}: hung API timeout, no overlapping refresh, recovery`);
      await slowPage.close();
    }
    console.log(`${passed} browser scenarios passed; ${engine} ${browser.version()}`);
  } finally {
    await browser.close();
  }
})().catch(error => {console.error(error); process.exitCode = 1;});
