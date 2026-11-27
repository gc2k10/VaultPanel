// Template substitutions are always text, never trusted HTML.
function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, character => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  })[character]);
}

function safeHtml(parts, ...values) {
  return parts.reduce((result, part, index) =>
    result + part + (index < values.length ? escapeHtml(values[index]) : ''), '');
}
