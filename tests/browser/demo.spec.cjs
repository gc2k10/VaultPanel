const { test, expect } = require('@playwright/test');
const brand = require('./brand.json');

for (const route of ['/about.html']) {
  test(route + ' loads safely without overflow or broken assets', async ({ page, request }, testInfo) => {
    const errors = [];
    const unexpectedRequests = [];
    page.on('pageerror', e => errors.push(e.message));
    page.on('request', r => {
      if (new URL(r.url()).origin !== 'http://127.0.0.1:8000') unexpectedRequests.push(r.url());
    });
    await page.goto(route);
    await expect(page.getByRole('heading', { name: brand.name, exact: true })).toBeVisible();
    const logo = page.getByRole('img', { name: brand.name, exact: true });
    await expect(logo).toBeVisible();
    await expect.poll(() => logo.evaluate(i => i.complete && i.naturalWidth > 0)).toBe(true);
    const size = await logo.evaluate(i => ({
      naturalWidth: i.naturalWidth, naturalHeight: i.naturalHeight,
      width: i.getBoundingClientRect().width, height: i.getBoundingClientRect().height
    }));
    expect([size.naturalWidth, size.naturalHeight]).toEqual(brand.dimensions);
    expect(Math.abs(size.width / size.height - size.naturalWidth / size.naturalHeight)).toBeLessThan(0.02);
    const widths = await page.evaluate(() => ({viewport: innerWidth, content: document.documentElement.scrollWidth}));
    expect(widths.viewport).toBe(testInfo.project.use.viewport.width);
    expect(widths.content).toBeLessThanOrEqual(widths.viewport);
    const targets = await page.locator('a, img, script[src], link[href]').evaluateAll(nodes =>
      nodes.map(n => n.getAttribute('href') || n.getAttribute('src')).filter(Boolean));
    for (const target of [...new Set(targets)]) {
      if (/^https?:/.test(target)) continue;
      const response = await request.get(new URL(target, page.url()).href);
      expect(response.ok(), target).toBe(true);
    }
    expect(await page.locator('link[rel="icon"]').count()).toBe(2);
    expect(await page.locator('link[rel="apple-touch-icon"]').count()).toBe(1);
    expect(errors).toEqual([]);
    expect(unexpectedRequests).toEqual([]);
    await page.screenshot({ path: testInfo.outputPath(route === '/' ? 'dashboard.png' : 'about.png'), fullPage: true });
  });
}

test('site root opens Retro and project navigation returns to Retro', async ({page}) => {
  await page.goto('/');
  await expect(page).toHaveURL(/original\/retro\.html$/);
  await expect(page.locator('#hostname')).toContainText('DEMO-NAS');
  await page.getByRole('link', {name: 'About the project', exact:true}).click();
  await expect(page.getByRole('heading', {name:'Project status',exact:true})).toBeVisible();
  await page.getByRole('link', {name:'Explore interactive demo',exact:true}).click();
  await expect(page).toHaveURL(/original\/retro\.html$/);
  await expect(page.locator('#hostname')).toContainText('DEMO-NAS');
});
