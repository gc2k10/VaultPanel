// No fallback to native fetch: all telemetry stays in this browser.
(() => {
  const data = window.VAULTPANEL_DEMO_DATA;
  delete window.VAULTPANEL_DEMO_DATA;
  window.fetch = async (input, options = {}) => {
    const path = typeof input === 'string' ? input : input.url;
    const method = String(options.method || input.method || 'GET').toUpperCase();
    if (method !== 'GET') return new Response(JSON.stringify({ok: false, error: 'Demo controls disabled'}), {status: 403});
    const key = /^\/api\/(overview|cooling|storage|services|network|alerts)$/.exec(path)?.[1];
    if (!key) throw new Error('Demo has no network backend');
    return new Response(JSON.stringify(data[key]), {status: 200, headers: {'Content-Type': 'application/json'}});
  };
})();
