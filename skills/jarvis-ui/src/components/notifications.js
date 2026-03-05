// ── 通知系統 ──

const notification = document.getElementById('notification');

export function showNotification(message) {
  if (!notification) return;
  notification.textContent = message;
  notification.style.opacity = 1;
  setTimeout(() => {
    notification.style.opacity = 0;
  }, 3000);
}
