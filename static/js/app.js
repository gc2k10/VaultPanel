const state = { overview: null, cooling: null, storage: null, services: null, network: null, alerts: null };
let ledEditing = false;
function $(id) { return document.getElementById(id); }
function badgeClass(text) {
  const t = String(text || '').toUpperCase();
  if (['OK', 'ONLINE', 'ACTIVE', 'PASSED', 'NOMINAL', 'INFO'].includes(t)) return 'ok';
  if (['WARNING', 'WARN', 'CHECK'].includes(t)) return 'warn';
  return 'crit';
}
function setClock() { $('clock').textContent = new Date().toLocaleString('pl-PL'); }
setInterval(setClock, 1000); setClock();

async function fetchJson(url, options) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 8000);
  try {
    const res = await fetch(url, {...options, signal: controller.signal});
    if (!res.ok) throw new Error(`Request failed: ${res.status}`);
    return await res.json();
  } finally {
    clearTimeout(timer);
  }
}

function activateTab(name) {
  document.querySelectorAll('.nav-btn').forEach(btn => {
    const selected = btn.dataset.tab === name;
    btn.classList.toggle('active', selected);
    btn.setAttribute('aria-pressed', String(selected));
  });
  document.querySelectorAll('.tab').forEach(tab => tab.classList.toggle('active', tab.id === `tab-${name}`));
}
document.querySelectorAll('.nav-btn').forEach(btn => btn.addEventListener('click', () => activateTab(btn.dataset.tab)));

function renderOverview(data) {
  state.overview = data;
  if ($('lastBackup')) $('lastBackup').textContent = data.last_backup || '--';
  if ($('lastScrub')) $('lastScrub').textContent = data.last_scrub || '--';
  if ($('lastSmart')) $('lastSmart').textContent = data.last_smart_test || '--';
  $('hostname').textContent = `${data.hostname} // VAULTPANEL`;
  $('platform').textContent = data.platform;
  $('globalStatus').textContent = data.global_status;
  $('globalStatus').className = `status-pill ${data.global_status.toLowerCase()}`;
  $('cpuUsage').textContent = data.cpu_usage_pct != null ? `${data.cpu_usage_pct}%` : '--';
  $('cpuTemp').textContent = data.cpu_temp_c != null ? `${data.cpu_temp_c}°C` : '--';
  $('ramUsage').textContent = data.memory.used_pct != null ? `${data.memory.used_pct}%` : '--';
  $('storageUsage').textContent = data.storage.used_pct != null ? `${data.storage.used_pct}%` : '--';
  $('internetStatus').textContent = data.internet_ok == null ? 'UNKNOWN' : data.internet_ok ? 'ONLINE' : 'OFFLINE';
  $('servicesStatus').textContent = `${data.services_online}/${data.services_total}`;
  $('generatedAt').textContent = data.generated_at;
  $('uptime').textContent = data.uptime;
  $('loadAvg').textContent = `${data.loadavg['1m']} / ${data.loadavg['5m']} / ${data.loadavg['15m']}`;
  $('lanIp').textContent = data.ips.lan_ip || '--';
  $('tsIp').textContent = data.ips.tailscale_ip || '--';
}

function renderServicesHealth(data) {
  const el = $('quickHealth');
  el.innerHTML = '';
  data.services.forEach(item => {
    const div = document.createElement('div');
    div.className = 'row';
    div.innerHTML = safeHtml`<span>${item.name}</span><strong class="badge ${item.active == null ? 'warn' : item.active ? 'ok' : 'crit'}">${item.active == null ? 'UNKNOWN' : item.active ? 'ONLINE' : 'OFFLINE'}</strong>`;
    el.appendChild(div);
  });
}

function renderCooling(data) {
  state.cooling = data || {};
  const fans = $('fans');
  if (fans) {
    fans.innerHTML = '';
    (data.fans || []).forEach(fan => {
      const div = document.createElement('div');
      div.className = 'row';
      if (typeof fan === 'object') {
        div.innerHTML = safeHtml`<span>${fan.label || 'COOLING SYSTEM'}</span><strong>${fan.rpm ?? '--'} RPM</strong>`;
      } else {
        div.innerHTML = safeHtml`<span>COOLING SYSTEM</span><strong>${fan ?? '--'} RPM</strong>`;
      }
      fans.appendChild(div);
    });
  }

  if ($('thermalState')) $('thermalState').textContent = data.thermal_status || '--';
  if ($('fanProfile')) $('fanProfile').textContent = data.fan_profile || '--';

  const led = data.led || {};
  if ($('ledScene')) $('ledScene').textContent = led.scene || '--';
  if ($('ledMode')) $('ledMode').textContent = led.mode || '--';
  if ($('ledBrightness')) $('ledBrightness').textContent = `${led.brightness ?? '--'}%`;
  if ($('ledSpeed')) $('ledSpeed').textContent = `${led.speed ?? '--'}%`;
  if ($('ledNote')) $('ledNote').textContent = led.note || '';
  if (!ledEditing) {
    if ($('modeSelect')) $('modeSelect').value = led.mode || 'STATIC';
    if ($('colorInput')) $('colorInput').value = led.color || '#7cfc00';
    if ($('brightnessInput')) $('brightnessInput').value = led.brightness ?? 62;
    if ($('speedInput')) $('speedInput').value = led.speed ?? 50;
    if ($('fanLedSelect')) $('fanLedSelect').value = led.fan_led || 'FOLLOW';
    if ($('oledModeSelect')) $('oledModeSelect').value = led.oled_mode || 'AUTO';
  }
}
function renderStorage(data) {
  state.storage = data;
  $('rootUsed').textContent = `${data.root.used_gb} GB (${data.root.used_pct}%)`;
  $('rootFree').textContent = `${data.root.free_gb} GB`;
  $('rootTotal').textContent = `${data.root.total_gb} GB`;
  $('rootBar').style.width = `${data.root.used_pct || 0}%`;
  $('btrfsStatus').textContent = data.btrfs.scrub_status || data.btrfs.filesystem_show || 'No data';
  const devices = $('devices');
  devices.innerHTML = '';
  data.devices.forEach(dev => {
    const div = document.createElement('div');
    div.className = 'row';
    div.innerHTML = safeHtml`<div><strong>/dev/${dev.name}</strong><div class="muted">${dev.model || 'unknown model'} · ${dev.size || '--'}</div></div>
      <div><div class="muted">TEMP</div><strong>${dev.temperature_c ?? '--'}°C</strong></div>
      <div><div class="muted">SMART</div><strong class="badge ${badgeClass(dev.smart_health)}">${dev.smart_health}</strong></div>`;
    devices.appendChild(div);
  });
}

function renderServices(data) {
  state.services = data;
  renderServicesHealth(data);
  const el = $('servicesTable');
  el.innerHTML = '<div class="table-row table-head"><span>SERVICE</span><span>STATUS</span><span>SINCE</span><span>PORT</span></div>';
  data.services.forEach(item => {
    const row = document.createElement('div');
    row.className = 'table-row row';
    row.innerHTML = safeHtml`<span>${item.name}</span>
      <strong class="badge ${item.active == null ? 'warn' : item.active ? 'ok' : 'crit'}">${item.active == null ? 'UNKNOWN' : item.active ? 'ONLINE' : item.active_text.toUpperCase()}</strong>
      <span>${item.since || '--'}</span>
      <span>${item.port || '--'}</span>`;
    el.appendChild(row);
  });
}

function renderNetwork(data) {
  state.network = data;
  $('netLan').textContent = data.ips.lan_ip || '--';
  $('netTs').textContent = data.ips.tailscale_ip || '--';
  $('gateway').textContent = data.gateway || '--';
  $('netInternet').textContent = data.internet_ok == null ? 'UNKNOWN' : data.internet_ok ? 'ONLINE' : 'OFFLINE';
  $('dnsStatus').textContent = data.dns_ok == null ? 'UNKNOWN' : data.dns_ok ? 'OK' : 'FAIL';
  $('tsStatus').textContent = data.tailscale_status || 'No tailscale output';
  $('resolvConf').textContent = data.resolv_conf || 'No resolv.conf';
}

function renderAlerts(data) {
  state.alerts = data;
  const el = $('alertsList');
  if (!el) return;

  el.innerHTML = '';
  (data.alerts || []).forEach(item => {
    const div = document.createElement('div');
    div.className = 'row';
    div.innerHTML = safeHtml`<div><strong>${item.source}</strong><div class="muted">${item.message}</div></div><strong class="badge ${badgeClass(item.level)}">${item.level}</strong>`;
    el.appendChild(div);
  });
}

['modeSelect', 'colorInput', 'brightnessInput', 'speedInput', 'fanLedSelect', 'oledModeSelect'].forEach(id => {
  const el = $(id);
  if (!el) return;

  el.addEventListener('input', () => {
    ledEditing = true;
  });

  el.addEventListener('change', () => {
    ledEditing = true;
  });
});

let refreshInProgress = false;
async function refreshAll() {
  if (refreshInProgress) return;
  refreshInProgress = true;
  try {
    const results = await Promise.allSettled([
      fetchJson('/api/overview'), fetchJson('/api/cooling'), fetchJson('/api/storage'),
      fetchJson('/api/services'), fetchJson('/api/network'), fetchJson('/api/alerts')
    ]);
    if (results.some(result => result.status === 'rejected')) throw new Error('Telemetry unavailable');
    const [overview, cooling, storage, services, network, alerts] = results.map(result => result.value);
    renderOverview(overview);
    renderCooling(cooling);
    renderStorage(storage);
    renderServices(services);
    renderNetwork(network);
    renderAlerts(alerts);
    if ($('telemetryStatus')) $('telemetryStatus').textContent = 'READ-ONLY — telemetry refreshed; unavailable checks remain unknown.';
  } catch (error) {
    if ($('globalStatus')) $('globalStatus').textContent = 'STALE';
    if ($('telemetryStatus')) $('telemetryStatus').textContent = 'Telemetry unavailable. Displayed values may be outdated; retrying automatically.';
  } finally {
    refreshInProgress = false;
  }
}

$('applyLed').addEventListener('click', async () => {
  const payload = {
    scene: $('modeSelect') ? $('modeSelect').value : 'STATIC',
    mode: $('modeSelect') ? $('modeSelect').value : 'STATIC',
    color: $('colorInput') ? $('colorInput').value : '#7cfc00',
    brightness: $('brightnessInput') ? Number($('brightnessInput').value) : 62,
    speed: $('speedInput') ? Number($('speedInput').value) : 50,
    fan_led: $('fanLedSelect') ? $('fanLedSelect').value : 'FOLLOW'
  };

  await fetchJson('/api/led', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  ledEditing = false;
  await refreshAll();
});

document.querySelectorAll('.preset-btn').forEach(btn => btn.addEventListener('click', async () => {
  if ($('modeSelect')) $('modeSelect').value = btn.dataset.mode;
  if ($('colorInput')) $('colorInput').value = btn.dataset.color;
  ledEditing = true;

  await fetchJson('/api/led', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      scene: btn.dataset.scene,
      mode: btn.dataset.mode,
      color: btn.dataset.color,
      brightness: $('brightnessInput') ? Number($('brightnessInput').value) : 62,
      speed: $('speedInput') ? Number($('speedInput').value) : 50,
      fan_led: $('fanLedSelect') ? $('fanLedSelect').value : 'FOLLOW'
    })
  });

  ledEditing = false;
  await refreshAll();
}));

refreshAll();
setInterval(refreshAll, 5000);

$('applyOledMode')?.addEventListener('click', async () => {
  const payload = {
    mode: $('oledModeSelect') ? $('oledModeSelect').value : 'AUTO'
  };

  await fetchJson('/api/oled', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  await refreshAll();
});

document.addEventListener('click', async (e) => {
  const btn = e.target.closest('.action-btn[data-profile]');
  if (!btn) return;

  const profile = btn.dataset.profile;

  await fetchJson('/api/fans', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ profile })
  });

  await refreshAll();
});
