// Escape each dynamic value at HTML sinks; static markup stays unchanged.
function safeHtml(parts, ...values) {
  const escape = value => String(value ?? '').replace(/[&<>"']/g, char =>
    ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[char]));
  return parts.reduce((result, part, i) => result + part + (i < values.length ? escape(values[i]) : ''), '');
}


// Membership evidence only; a filesystem scrub cannot establish RAID status.
function mdraidLabel(data) {
  if (data?.available !== true || !Array.isArray(data.arrays) || !data.arrays.length) return 'UNKNOWN';
  if (data.arrays.some(a => a.status === 'degraded' && a.healthy === false)) return 'DEGRADED';
  if (data.arrays.some(a => a.status === 'busy')) return 'BUSY';
  if (data.arrays.every(a => a.status === 'ok' && a.healthy === true)) return 'MEMBERS PRESENT';
  return 'UNKNOWN';
}
