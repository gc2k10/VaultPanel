const state = { overview: null, cooling: null, storage: null, services: null, network: null, alerts: null };
let ledEditing = false;
let retroBootDone = false;

function $(id) { return document.getElementById(id); }

function badgeClass(text) {
  const t = String(text || '').toUpperCase();
  if (['OK', 'ONLINE', 'ACTIVE', 'PASSED', 'NOMINAL', 'INFO'].includes(t)) return 'ok';
  if (['WARNING', 'WARN', 'CHECK'].includes(t)) return 'warn';
  return 'crit';
}

function setClock() {
  const now = new Date().toLocaleString('pl-PL');
  if ($('clock')) $('clock').textContent = now;
  if ($('clockMirror')) $('clockMirror').textContent = now;
}
setInterval(setClock, 1000);
setClock();

async function retroBootSequence() {
  if (retroBootDone) return;
  retroBootDone = true;

  if ($('hostname')) $('hostname').textContent = 'VAULTPANEL';
  if ($('globalStatus')) $('globalStatus').textContent = 'BOOT';

  if ($('clockMirror')) $('clockMirror').textContent = 'INITIALIZING...';
  await new Promise(r => setTimeout(r, 350));
  if ($('clockMirror')) $('clockMirror').textContent = 'CHECKING STORAGE ARRAY...';
  await new Promise(r => setTimeout(r, 350));
  if ($('clockMirror')) $('clockMirror').textContent = 'LOADING NETWORK STACK...';
  await new Promise(r => setTimeout(r, 350));
  setClock();
}

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
  document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.toggle('active', btn.dataset.tab === name));
  document.querySelectorAll('.tab').forEach(tab => tab.classList.toggle('active', tab.id === `tab-${name}`));
}

document.querySelectorAll('.nav-btn').forEach(btn => btn.addEventListener('click', () => activateTab(btn.dataset.tab)));

function kvRow(label, value, badgeCls = '') {
  return safeHtml`<div class="row"><span>${label}</span><span class="dots"></span><strong class="${badgeCls}">${value}</strong></div>`;
}

function renderOverview(data) {
  state.overview = data || {};

  if ($('hostname')) $('hostname').textContent = data.hostname || 'VAULTPANEL';
  if ($('platform')) $('platform').textContent = data.platform || '--';
  if ($('platformTop')) $('platformTop').textContent = data.platform || '--';

  if ($('globalStatus')) {
    $('globalStatus').textContent = data.global_status || '--';
    $('globalStatus').className = `status-pill ${(data.global_status || 'nominal').toLowerCase()}`;
  }

  if ($('cpuUsage')) $('cpuUsage').textContent = data.cpu_usage_pct != null ? `${data.cpu_usage_pct}%` : '--';
  if ($('cpuTemp')) $('cpuTemp').textContent = data.cpu_temp_c != null ? `${data.cpu_temp_c}°C` : '--';
  if ($('ramUsage')) $('ramUsage').textContent = data.memory?.used_pct != null ? `${data.memory.used_pct}%` : '--';
  if ($('storageUsage')) $('storageUsage').textContent = data.storage?.used_pct != null ? `${data.storage.used_pct}%` : '--';
  if ($('internetStatus')) $('internetStatus').textContent = data.internet_ok == null ? 'UNKNOWN' : data.internet_ok ? 'ONLINE' : 'OFFLINE';
  if ($('servicesStatus')) $('servicesStatus').textContent = `${data.services_online}/${data.services_total}`;
  if ($('generatedAt')) $('generatedAt').textContent = data.generated_at || '--';
  if ($('uptime')) $('uptime').textContent = data.uptime || '--';
  if ($('loadAvg')) $('loadAvg').textContent = data.loadavg ? `${data.loadavg['1m']} / ${data.loadavg['5m']} / ${data.loadavg['15m']}` : '--';
  if ($('lanIp')) $('lanIp').textContent = data.ips?.lan_ip || '--';
  if ($('tsIp')) $('tsIp').textContent = data.ips?.tailscale_ip || '--';
  if ($('lastBackup')) $('lastBackup').textContent = formatDateShort(data.last_backup) || '--';
  if ($('lastScrub')) $('lastScrub').textContent = formatDateShort(data.last_scrub) || '--';
  if ($('vaultpanelBackup')) $('vaultpanelBackup').textContent = formatDateShort(data.vaultpanel_backup) || '--';
  if ($('lastSmart')) {
    const smart = String(data.last_smart_test || '--').toUpperCase();
    $('lastSmart').textContent = smart;
    $('lastSmart').classList.remove('ok', 'warn', 'crit');

    if (['OK', 'PASS', 'PASSED'].includes(smart)) {
      $('lastSmart').classList.add('ok');
    } else if (['NO DATA', 'UNKNOWN', '--'].includes(smart)) {
      $('lastSmart').classList.add('warn');
    } else {
      $('lastSmart').classList.add('crit');
    }
  }

  if ($('storageLastBackup')) $('storageLastBackup').textContent = formatDateShort(data.last_backup) || '--';
  if ($('storageLastScrub')) $('storageLastScrub').textContent = formatDateShort(data.last_scrub) || '--';
}

function renderServicesHealth(data) {
  const el = $('quickHealth');
  if (!el) return;

  el.innerHTML = '';

  (data.services || []).forEach(item => {
    const div = document.createElement('div');
    div.className = 'row';
    div.innerHTML = safeHtml`
      <span>${(item.name || '--').toUpperCase()}</span>
      <span class="dots"></span>
      <strong class="${item.active == null ? 'warn' : item.active ? 'ok' : 'crit'}">${item.active == null ? 'UNKNOWN' : item.active ? 'ONLINE' : 'OFFLINE'}</strong>
    `;
    el.appendChild(div);
  });
}

function asciiColor(hex) {
  const c = /^#[0-9a-f]{6}$/i.test(hex) ? hex.toUpperCase() : '#7CFC00';
  return safeHtml`
    <span class="color-hex">${c}</span>
    <span class="dots"></span>
    <span class="color-bar">[ <span style="color:${c}">█</span> ]</span>
  `;
}

function refreshCoolingAsciiControls() {
  if ($('brightnessAscii') && $('brightnessInput')) {
    $('brightnessAscii').textContent = `${Number($('brightnessInput').value || 0)}%`;
  }

  if ($('speedAscii') && $('speedInput')) {
    $('speedAscii').textContent = `${Number($('speedInput').value || 0)}%`;
  }
  if ($('colorAscii') && $('colorInput')) {
    $('colorAscii').innerHTML = asciiColor($('colorInput').value);
  }
}

function refreshCoolingAsciiSelects() {
  if ($('modeAsciiValue') && $('modeSelect')) {
    $('modeAsciiValue').textContent = $('modeSelect').value || 'STATIC';
  }

  if ($('fanLedAsciiValue') && $('fanLedSelect')) {
    $('fanLedAsciiValue').textContent = $('fanLedSelect').value || 'FOLLOW';
  }

  if ($('oledModeAsciiValue') && $('oledModeSelect')) {
    $('oledModeAsciiValue').textContent = $('oledModeSelect').value || 'AUTO';
  }
}

function renderCooling(data) {
  state.cooling = data || {};

  const fans = $('fans');
  if (fans) {
    fans.innerHTML = '';
    (data.fans || []).forEach((fan, idx) => {
      const div = document.createElement('div');
      div.className = 'row';
      const label = fan.label || (idx === 0 ? 'SYSTEM FAN' : `FAN ${idx + 1}`);
      const rpm = fan.rpm ?? '--';
      div.innerHTML = safeHtml`<span>${label}</span><span class="dots"></span><strong>${rpm} RPM</strong>`;
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
  if ($('oledModeView')) $('oledModeView').textContent = led.oled_mode || 'AUTO';
  if ($('ledNote')) $('ledNote').textContent = led.note || '';
  if ($('rearFansView')) $('rearFansView').textContent = data.rear_fans || '--';
  if (!ledEditing) {
    if ($('modeSelect')) $('modeSelect').value = led.mode || 'STATIC';
    if ($('colorInput')) $('colorInput').value = led.color || '#7cfc00';
    if ($('brightnessInput')) $('brightnessInput').value = led.brightness ?? 62;
    if ($('speedInput')) $('speedInput').value = led.speed ?? 50;
    if ($('fanLedSelect')) $('fanLedSelect').value = led.fan_led || 'FOLLOW';
    if ($('oledModeSelect')) $('oledModeSelect').value = led.oled_mode || 'AUTO';
  }

  refreshCoolingAsciiControls();
}

['brightnessInput', 'speedInput', 'colorInput'].forEach(id => {
  const el = $(id);
  if (el) {
    el.addEventListener('input', refreshCoolingAsciiControls);
    el.addEventListener('change', refreshCoolingAsciiControls);
  }
});

function renderStorage(data) {
  state.storage = data || {};

  const root = data.root || {};
  const btrfs = data.btrfs || {};
  const devicesData = data.devices || [];
  if ($('btrfsStatus')) {
    $('btrfsStatus').textContent = btrfs.scrub_status || btrfs.filesystem_show || 'No data';
  }
  if ($('rootUsed')) {
    $('rootUsed').textContent =
      root.used_gb != null && root.used_pct != null
        ? `${root.used_gb} GB (${root.used_pct}%)`
        : '--';
  }

  if ($('rootFree')) {
    $('rootFree').textContent = root.free_gb != null ? `${root.free_gb} GB` : '--';
  }

  if ($('rootTotal')) {
    $('rootTotal').textContent = root.total_gb != null ? `${root.total_gb} GB` : '--';
  }

  if ($('rootBar')) {
    $('rootBar').style.width = `${root.used_pct || 0}%`;
  }
  const nvme0 = devicesData[0];
  const nvme1 = devicesData[1];

  if ($('raidStatus')) {
    let raid = '--';
    if (btrfs.degraded === true) raid = 'DEGRADED';
    else if (btrfs.healthy === true) raid = 'HEALTHY';
    $('raidStatus').textContent = raid;
    $('raidStatus').classList.remove('ok', 'warn', 'crit');
    if (raid === 'HEALTHY') $('raidStatus').classList.add('ok');
    else if (raid === 'DEGRADED') $('raidStatus').classList.add('crit');
  }

  if ($('filesystemType')) {
    $('filesystemType').textContent = btrfs.filesystem_show ? 'BTRFS' : '--';
  }

  if ($('storageMountpoint')) {
    $('storageMountpoint').textContent = data.mountpoint || root.path || '--';
  }

  if ($('storageTotalSize')) {
    $('storageTotalSize').textContent = root.total_gb != null ? `${root.total_gb} GB` : '--';
  }

  if ($('storageUsedSpace')) {
    $('storageUsedSpace').textContent =
      root.used_gb != null && root.used_pct != null
        ? `${root.used_gb} GB (${root.used_pct}%)`
        : '--';
  }

  if ($('storageFreeSpace')) {
    $('storageFreeSpace').textContent = root.free_gb != null ? `${root.free_gb} GB` : '--';
  }

  if ($('snapshotCount')) {
    $('snapshotCount').textContent = data.snapshot_count != null ? String(data.snapshot_count) : '--';
  }

  if ($('newestSnapshot')) {
    $('newestSnapshot').textContent = data.newest_snapshot
      ? formatDateShort(data.newest_snapshot)
      : '--';
  }

  if ($('storageLastBackup')) {
    $('storageLastBackup').textContent = formatDateShort(state.overview?.last_backup) || '--';
  }

  if ($('storageLastScrub')) {
    $('storageLastScrub').textContent = formatDateShort(state.overview?.last_scrub) || '--';
  }

  if ($('nvme0Smart')) {
    const v = (nvme0?.smart_health || '--').toUpperCase();
    $('nvme0Smart').textContent = v;
    $('nvme0Smart').classList.remove('ok', 'warn', 'crit');
    if (['OK', 'PASSED'].includes(v)) $('nvme0Smart').classList.add('ok');
    else if (['CHECK', 'UNKNOWN'].includes(v)) $('nvme0Smart').classList.add('warn');
    else $('nvme0Smart').classList.add('crit');
  }

  if ($('nvme1Smart')) {
    const v = (nvme1?.smart_health || '--').toUpperCase();
    $('nvme1Smart').textContent = v;
    $('nvme1Smart').classList.remove('ok', 'warn', 'crit');
    if (['OK', 'PASSED'].includes(v)) $('nvme1Smart').classList.add('ok');
    else if (['CHECK', 'UNKNOWN'].includes(v)) $('nvme1Smart').classList.add('warn');
    else $('nvme1Smart').classList.add('crit');
  }

  const devices = $('devices');
  if (devices) {
    devices.innerHTML = '';
    devicesData.forEach(dev => {
      const smart = String(dev.smart_health || '--').toUpperCase();
      const smartCls =
        ['OK', 'PASSED'].includes(smart) ? 'ok' :
        ['CHECK', 'UNKNOWN'].includes(smart) ? 'warn' : 'crit';

      const tempText = dev.temperature_c != null ? `${dev.temperature_c}°C` : '--';

      const row = document.createElement('div');
      row.className = 'device-card';
      row.innerHTML = safeHtml`
        <div class="device-top">
          <div class="device-path">/dev/${dev.name || '--'}</div>
          <div class="device-col-head">TEMP</div>
          <div class="device-col-head">SMART</div>
        </div>
        <div class="device-bottom">
          <div class="device-meta">
            <div class="device-model">${dev.model || '--'}</div>
            <div class="device-size">${dev.size || '--'}</div>
          </div>
          <div class="device-temp">${tempText}</div>
          <div class="device-smart ${smartCls}">${smart}</div>
        </div>
      `;
      devices.appendChild(row);
    });
  }

}

function renderServices(data) {
  state.services = data;
  renderServicesHealth(data);

  const el = $('servicesTable');
  if (!el) return;

  el.innerHTML = '';

  (data.services || []).forEach(item => {
    const name = (item.name || '--').toUpperCase();
    const status = item.active == null ? 'UNKNOWN' : item.active ? 'ONLINE' : (item.active_text || 'FAILED').toUpperCase();
    const statusCls = item.active == null ? 'warn' : item.active ? 'ok' : 'crit';

    const port = item.port ? `port: ${item.port}` : 'port: --';
    const since = item.since_short ? `since: ${item.since_short}` : 'since: --';

    const card = document.createElement('div');
    card.className = 'service-card';
    card.innerHTML = safeHtml`
      <div class="row">
        <span>${name}</span>
        <span class="dots"></span>
        <strong class="${statusCls}">${status}</strong>
      </div>
      <div class="row subtle">
        <span>${port}</span>
        <span></span>
        <span>${since}</span>
      </div>
    `;
    el.appendChild(card);
  });
}

function renderNetwork(data) {
  state.network = data;
  if ($('netLan')) $('netLan').textContent = data.ips?.lan_ip || '--';
  if ($('netTs')) $('netTs').textContent = data.ips?.tailscale_ip || '--';
  if ($('gateway')) $('gateway').textContent = data.gateway || '--';
  if ($('netInternet')) $('netInternet').textContent = data.internet_ok == null ? 'UNKNOWN' : data.internet_ok ? 'ONLINE' : 'OFFLINE';
  if ($('dnsStatus')) $('dnsStatus').textContent = data.dns_ok == null ? 'UNKNOWN' : data.dns_ok ? 'OK' : 'FAIL';
  if ($('tsStatus')) $('tsStatus').textContent = data.tailscale_status || 'No tailscale output';
  if ($('resolvConf')) $('resolvConf').textContent = data.resolv_conf || 'No resolv.conf';
}

function renderAlerts(data) {
  state.alerts = data;
  state.alertHistory = data?.history || [];

  const el = $('alertsList');
  if (!el) return;

  const alerts = data?.alerts || [];
  el.innerHTML = '';

  alerts.forEach(item => {
    const source = (item.source || item.category || 'SYSTEM').toUpperCase();
    const message = (item.message || item.text || item.detail || 'NO DETAILS').toUpperCase();

    const row = document.createElement('div');
    row.className = 'row';
    row.innerHTML = safeHtml`
      <span>${source}</span>
      <span class="dots"></span>
      <strong class="value">${message}</strong>
    `;
    el.appendChild(row);
  });

  if (!alerts.length) {
    el.innerHTML = safeHtml`
      <div class="row">
        <span>ALERTS</span>
        <span class="dots"></span>
        <strong class="value">NO ALERTS</strong>
      </div>
    `;
  }

  renderPreviousAlerts();
}

function formatDateShort(dateStr) {
  if (!dateStr || dateStr === 'NO DATA' || dateStr === '--') return '--';

  const s = String(dateStr).trim();

  // Thu Mar 12 23:53:02 2026
  let m = s.match(/^[A-Z][a-z]{2}\s+([A-Z][a-z]{2})\s+(\d{1,2})\s+(\d{2}):(\d{2})/);
  if (m) {
    const [, mon, dd, hh, min] = m;
    const months = {
      Jan: '01', Feb: '02', Mar: '03', Apr: '04',
      May: '05', Jun: '06', Jul: '07', Aug: '08',
      Sep: '09', Oct: '10', Nov: '11', Dec: '12'
    };
    const mm = months[mon] || mon;
    return `${String(dd).padStart(2, '0')}.${mm} ${hh}:${min}`;
  }

  // Tue 17 Mar 14:06:34 CET 2026
  m = s.match(/^[A-Z][a-z]{2}\s+(\d{1,2})\s+([A-Z][a-z]{2})\s+(\d{2}):(\d{2})/);
  if (m) {
    const [, dd, mon, hh, min] = m;
    const months = {
      Jan: '01', Feb: '02', Mar: '03', Apr: '04',
      May: '05', Jun: '06', Jul: '07', Aug: '08',
      Sep: '09', Oct: '10', Nov: '11', Dec: '12'
    };
    const mm = months[mon] || mon;
    return `${String(dd).padStart(2, '0')}.${mm} ${hh}:${min}`;
  }

  // 2026-03-18 00:00:00
  m = s.match(/^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2})/);
  if (m) {
    const [, , mm, dd, hh, min] = m;
    return `${dd}.${mm} ${hh}:${min}`;
  }

  // 2026-03-17.15:25:45
  m = s.match(/^(\d{4})-(\d{2})-(\d{2})[.\-_](\d{2}):(\d{2})/);
  if (m) {
    const [, , mm, dd, hh, min] = m;
    return `${dd}.${mm} ${hh}:${min}`;
  }

  return s;
}

/*function formatAlertDate(ts) {
  if (!ts) return '--.--';
  const m = String(ts).match(/^(\d{4})-(\d{2})-(\d{2})/);
  if (!m) return ts;
  return `${m[3]}.${m[2]}`;*/

function formatAlertDate(ts) {
  if (!ts) return '--.-- --:--';

  const s = String(ts).trim();

  // 2026-03-18 23:53:52
  let m = s.match(/^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2})/);
  if (m) {
    const [, , mm, dd, hh, min] = m;
    return `${dd}.${mm} ${hh}:${min}`;
  }

  // Thu Mar 12 23:53:02 2026
  m = s.match(/^[A-Z][a-z]{2}\s+([A-Z][a-z]{2})\s+(\d{1,2})\s+(\d{2}):(\d{2})/);
  if (m) {
    const [, mon, dd, hh, min] = m;
    const months = {
      Jan: '01', Feb: '02', Mar: '03', Apr: '04',
      May: '05', Jun: '06', Jul: '07', Aug: '08',
      Sep: '09', Oct: '10', Nov: '11', Dec: '12'
    };
    const mm = months[mon] || mon;
    return `${String(dd).padStart(2, '0')}.${mm} ${hh}:${min}`;
  }

  // fallback: samo YYYY-MM-DD
  m = s.match(/^(\d{4})-(\d{2})-(\d{2})/);
  if (m) {
    return `${m[3]}.${m[2]}`;
  }

  return s;
}

function renderPreviousAlerts() {
  const el = $('alertsHistory');
  if (!el) return;

  const history = state.alertHistory || [];
  el.innerHTML = '';

  if (!history.length) {
    el.innerHTML = safeHtml`
      <div class="row subtle">
        <span>--.--</span>
        <span class="dots"></span>
        <span>NO PREVIOUS ALERTS</span>
      </div>
    `;
    return;
  }

  history.forEach(item => {
    const date = formatAlertDate(item.timestamp);
    const message = (item.message || 'UNKNOWN ALERT').toUpperCase();

    const row = document.createElement('div');
    row.className = 'row subtle';
    row.innerHTML = safeHtml`
      <span>${date}</span>
      <span class="dots"></span>
      <span>${message}</span>
    `;
    el.appendChild(row);
  });
}

['modeSelect', 'colorInput', 'brightnessInput', 'speedInput', 'fanLedSelect', 'oledModeSelect'].forEach(id => {
  const el = $(id);
  if (!el) return;

  el.addEventListener('input', () => {
    ledEditing = true;
    if (id === 'brightnessInput' && $('ledBrightness')) $('ledBrightness').textContent = `${el.value}%`;
    if (id === 'speedInput' && $('ledSpeed')) $('ledSpeed').textContent = `${el.value}%`;
    if (id === 'modeSelect' && $('ledMode')) $('ledMode').textContent = el.value;
    if (id === 'oledModeSelect' && $('oledModeView')) $('oledModeView').textContent = el.value;
  });

  el.addEventListener('change', () => {
    ledEditing = true;
    if (id === 'brightnessInput' && $('ledBrightness')) $('ledBrightness').textContent = `${el.value}%`;
    if (id === 'speedInput' && $('ledSpeed')) $('ledSpeed').textContent = `${el.value}%`;
    if (id === 'modeSelect' && $('ledMode')) $('ledMode').textContent = el.value;
    if (id === 'oledModeSelect' && $('oledModeView')) $('oledModeView').textContent = el.value;
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

$('applyLed')?.addEventListener('click', async () => {
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

document.addEventListener('keydown', (e) => {
  const key = e.key.toUpperCase();
  if (key === 'F1') { e.preventDefault(); activateTab('overview'); }
  else if (key === 'F2') { e.preventDefault(); activateTab('cooling'); }
  else if (key === 'F3') { e.preventDefault(); activateTab('storage'); }
  else if (key === 'F4') { e.preventDefault(); activateTab('services'); }
  else if (key === 'F5') { e.preventDefault(); activateTab('network'); }
  else if (key === 'F6') { e.preventDefault(); activateTab('alerts'); }
});

(async () => {
  await retroBootSequence();
  await refreshAll();
  setInterval(refreshAll, 5000);
})();

if ($('colorInput')) {
  $('colorInput').addEventListener('input', () => {
    refreshCoolingAsciiControls();
    refreshCoolingAsciiSelects();
 });
}

function bindAsciiStepper(downId, valueId, upId, inputId, step = 5) {
  const down = $(downId);
  const value = $(valueId);
  const up = $(upId);
  const input = $(inputId);
  if (!down || !value || !up || !input) return;

  const applyDelta = (delta) => {
    const min = Number(input.min || 0);
    const max = Number(input.max || 100);
    let v = Number(input.value || 0);
    v = Math.max(min, Math.min(max, v + delta));
    input.value = v;
    input.dispatchEvent(new Event('input', { bubbles: true }));
    input.dispatchEvent(new Event('change', { bubbles: true }));
    refreshCoolingAsciiControls();
  };

  down.addEventListener('click', () => applyDelta(-step));
  up.addEventListener('click', () => applyDelta(step));
}

bindAsciiStepper('brightnessDown', 'brightnessAscii', 'brightnessUp', 'brightnessInput', 5);
bindAsciiStepper('speedDown', 'speedAscii', 'speedUp', 'speedInput', 5);

['modeSelect', 'fanLedSelect', 'oledModeSelect'].forEach(id => {
  const el = $(id);
  if (el) {
    el.addEventListener('change', refreshCoolingAsciiSelects);
    el.addEventListener('input', refreshCoolingAsciiSelects);
  }
});

$('manualBackupBtn')?.addEventListener('click', async () => {
  const btn = $('manualBackupBtn');
  if (!btn) return;

  btn.disabled = true;
  btn.textContent = 'BACKUP...';

  try {
    await fetchJson('/api/backup', {
      method: 'POST'
    });

    setTimeout(async () => {
      await refreshAll();
      btn.textContent = 'DONE';
      setTimeout(() => {
        btn.textContent = 'MANUAL BACKUP';
        btn.disabled = false;
      }, 2000);
    }, 2000);

  } catch (e) {
    btn.textContent = 'ERROR';
    setTimeout(() => {
      btn.textContent = 'MANUAL BACKUP';
      btn.disabled = false;
    }, 3000);
  }
});
