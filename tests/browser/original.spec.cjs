const {test, expect} = require('@playwright/test');
for (const layout of ['index', 'retro']) {
  test(`original ${layout}: real layout, synthetic data, no backend`, async ({page}) => {
    const errors = [], forbidden = [];
    page.on('pageerror', e => errors.push(e.message));
    page.on('request', r => {
      const url = new URL(r.url());
      if (url.origin !== 'http://127.0.0.1:8000' || url.pathname.includes('/api/') || r.method() !== 'GET') forbidden.push(r.url());
    });
    await page.goto(`/original/${layout}.html`);
    await expect(page.getByText('DEMO — SYNTHETIC DATA ONLY', {exact:true})).toBeVisible();
    await expect(page.locator('#hostname')).toContainText('DEMO-NAS');
    for (const tab of ['overview', 'cooling', 'storage', 'services', 'network', 'alerts']) {
      await page.locator(`[data-tab="${tab}"]`).click();
      await expect(page.locator(`#tab-${tab}`)).toBeVisible();
      if (tab === 'overview' || tab === 'services') {
        const list = page.locator(tab === 'overview' ? '#quickHealth' : '#servicesTable');
        for (const name of ['Samba', 'Tailscale', 'Pi-hole', 'Netdata', 'Nginx', 'SSH', 'Nextcloud']) {
          await expect(list).toContainText(new RegExp(name + ' [(]demo[)]', 'i'));
        }
        if (tab === 'services') await expect(list).toContainText('Share files with computers on your network.');
      }
      if (tab === 'storage') await expect(page.locator('#raidStatus')).toHaveText('UNKNOWN');
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBe(true);
    }
    expect(await page.locator('button.action-btn:not([disabled]),button.preset-btn:not([disabled])').count()).toBe(0);
    const denied = await page.evaluate(async () => (await fetch('/api/backup', {method:'POST'})).status);
    expect(denied).toBe(403);
    expect(errors).toEqual([]);
    expect(forbidden).toEqual([]);
    await page.getByRole('link', {name: layout === 'index' ? 'Retro' : 'Classic', exact:true}).click();
    await expect(page.locator('#hostname')).toContainText('DEMO-NAS');
  });
}
