// Escape each dynamic value at HTML sinks; static markup stays unchanged.
function safeHtml(parts, ...values) {
  const escape = value => String(value ?? '').replace(/[&<>"']/g, char =>
    ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[char]));
  return parts.reduce((result, part, i) => result + part + (i < values.length ? escape(values[i]) : ''), '');
}
