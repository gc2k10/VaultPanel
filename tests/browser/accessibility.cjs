const {chromium} = require('playwright');
const axe = require('axe-core');
const assert = require('node:assert/strict');
const fs = require('node:fs');

(async () => {
  const browser = await chromium.launch({channel: 'chrome', headless: true});
  const results = [];
  try {
    for (const route of ['/', '/retro']) {
      for (const width of [320, 1280]) {
      const page = await browser.newPage({viewport: {width, height: 900}, reducedMotion: 'reduce'});
      await page.goto('http://127.0.0.1:8091' + route);
      await page.getByText('telemetry refreshed', {exact: false}).waitFor();
      await page.keyboard.press('Tab');
      assert.equal(await page.locator(':focus').getAttribute('class'), 'skip-link');
      await page.keyboard.press('Enter');
      assert.equal(await page.locator(':focus').getAttribute('id'), 'dashboard-content');
      assert.equal(await page.locator('main').evaluate(e => getComputedStyle(e).animationName), 'none');
      if (route === '/retro') assert.equal(await page.locator('.terminal-title').evaluate(e => getComputedStyle(e, '::after').animationName), 'none');
      await page.evaluate(axe.source);
      for (const tab of ['overview', 'cooling', 'storage', 'services', 'network', 'alerts']) {
        const button = page.locator(`[data-tab="${tab}"]`);
        await button.focus();
        await page.keyboard.press('Enter');
        assert.ok(await page.locator(`#tab-${tab}`).isVisible());
        assert.equal(await button.getAttribute('aria-pressed'), 'true');
        assert.equal(await page.locator('[data-tab][aria-pressed="true"]').count(), 1);
        assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), `${route} ${width} ${tab}: overflow`);
        const report = await page.evaluate(async () => {
          const result = await axe.run(document);
          return {violations: result.violations.map(v => ({id:v.id, impact:v.impact, nodes:v.nodes.map(n => ({target:n.target, summary:n.failureSummary}))})), incomplete: result.incomplete.map(v => v.id)};
        });
        const contrastBounds = [];
        if (route === '/') {
          // Bound the monotonic body gradient, retaining real nested backgrounds.
          for (const background of ['#08110a', '#102312']) {
            const style = await page.addStyleTag({content: `body { background: ${background} !important; }`});
            const contrast = await page.evaluate(async () => {
              const result = await axe.run(document, {runOnly: ['color-contrast']});
              return {violations: result.violations.map(v => ({id:v.id, nodes:v.nodes.map(n=>n.target)})), incomplete: result.incomplete.map(v=>({id:v.id,nodes:v.nodes.map(n=>({target:n.target,summary:n.failureSummary}))}))};
            });
            await style.evaluate(e => e.remove());
            assert.deepEqual(contrast.violations, [], `${tab}: contrast on ${background}`);
            assert.deepEqual(contrast.incomplete, [], `${tab}: unresolved contrast on ${background}`);
            contrastBounds.push({background, ...contrast});
          }
        }
        results.push({route, width, tab, ...report, contrastBounds});
        console.log(route, width, tab, JSON.stringify(report));
      }
      await page.close();
      }
    }
  } finally {
    await browser.close();
  }
  if (process.env.VAULTPANEL_A11Y_REPORT) fs.writeFileSync(process.env.VAULTPANEL_A11Y_REPORT, JSON.stringify({axeVersion:axe.version, results}, null, 2));
  assert.equal(results.reduce((count, result) => count + result.violations.length, 0), 0, 'Automated accessibility violations remain');
  console.log(`24 accessibility/keyboard views passed; axe-core ${axe.version}`);
})().catch(error => {console.error(error); process.exitCode = 1;});
