// ── 時間戳更新 ──

export function initTimestamp() {
  function updateTimestamp() {
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    const el = document.getElementById('timestamp');
    if (el) el.textContent = `${hours}:${minutes}:${seconds}`;
  }
  setInterval(updateTimestamp, 1000);
  updateTimestamp();
}
