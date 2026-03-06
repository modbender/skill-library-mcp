// ── 載入畫面（展開圓圈動畫） ──

import { getAccentRGB } from '../config/theme.js';

function getThemeRgbaValue(alpha) {
  return `rgba(${getAccentRGB()}, ${alpha})`;
}

export function setupPreloader() {
  const canvas = document.getElementById('preloader-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const centerX = canvas.width / 2;
  const centerY = canvas.height / 2;
  let time = 0;
  let lastTime = 0;
  const maxRadius = 80;
  const circleCount = 5;
  const dotCount = 24;

  function animate(timestamp) {
    if (!lastTime) lastTime = timestamp;
    const deltaTime = timestamp - lastTime;
    lastTime = timestamp;
    time += deltaTime * 0.001;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const accentRGB = getAccentRGB();

    ctx.beginPath();
    ctx.arc(centerX, centerY, 3, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(${accentRGB}, 0.9)`;
    ctx.fill();

    for (let c = 0; c < circleCount; c++) {
      const circlePhase = (time * 0.3 + c / circleCount) % 1;
      const radius = circlePhase * maxRadius;
      const opacity = 1 - circlePhase;

      ctx.beginPath();
      ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
      ctx.strokeStyle = `rgba(${accentRGB}, ${opacity * 0.2})`;
      ctx.lineWidth = 1;
      ctx.stroke();

      for (let i = 0; i < dotCount; i++) {
        const angle = (i / dotCount) * Math.PI * 2;
        const x = centerX + Math.cos(angle) * radius;
        const y = centerY + Math.sin(angle) * radius;
        const size = 2 * (1 - circlePhase * 0.5);

        ctx.beginPath();
        ctx.moveTo(centerX, centerY);
        ctx.lineTo(x, y);
        ctx.strokeStyle = `rgba(${accentRGB}, ${opacity * 0.1})`;
        ctx.lineWidth = 1;
        ctx.stroke();

        ctx.beginPath();
        ctx.arc(x, y, size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${accentRGB}, ${opacity * 0.9})`;
        ctx.fill();
      }
    }

    if (document.getElementById('loading-overlay').style.display !== 'none') {
      requestAnimationFrame(animate);
    }
  }
  requestAnimationFrame(animate);
}
