// ── Orb 環繞訊息（CSS 3D + DOM） ──

import { renderMarkdown } from './markdown.js';

const messages = [];
const MAX_MESSAGES = 5;
const LIFETIME = 12;        // 秒
const ORBIT_RADIUS = 240;   // px
const FLOAT_AMP = 15;       // px 上下浮動

let container = null;
let getOrbScreenPos = null;  // 回呼：取得 Orb 在螢幕上的 2D 座標

// 建立容器
function createContainer() {
  container = document.createElement('div');
  container.id = 'orb-messages';
  container.style.cssText = `
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    pointer-events: none;
    z-index: 5;
    overflow: hidden;
  `;
  document.body.appendChild(container);
}

// 建立訊息 DOM
function createMessageEl(text) {
  const el = document.createElement('div');
  el.className = 'orb-msg markdown-rendered';
  el.innerHTML = renderMarkdown(text);
  el.style.cssText = `
    position: absolute;
    width: 280px;
    word-wrap: break-word;
    white-space: normal;
    font-family: "TheGoodMonolith", monospace;
    font-size: 13px;
    letter-spacing: 1.5px;
    color: var(--accent-primary);
    background: rgba(10, 14, 23, 0.75);
    border: 1px solid rgba(var(--accent-rgb), 0.35);
    padding: 6px 14px;
    border-radius: 4px;
    text-shadow: 0 0 6px rgba(var(--accent-rgb), 0.6);
    box-shadow: 0 0 8px rgba(var(--accent-rgb), 0.15);
    opacity: 0;
    transform: scale(0.7);
    pointer-events: none;
  `;
  return el;
}

// 新增訊息
export function addOrbMessage(text) {
  if (!container) return;

  // 超過上限移除最舊
  if (messages.length >= MAX_MESSAGES) {
    destroyMessage(messages[0]);
  }

  const el = createMessageEl(text);
  container.appendChild(el);

  // 平均分佈角度，避免重疊
  let angle = Math.random() * Math.PI * 2;
  if (messages.length > 0) {
    // 找最大間隔插入
    const angles = messages.map(m => m.angle % (Math.PI * 2)).sort((a, b) => a - b);
    let maxGap = 0, bestAngle = angle;
    for (let i = 0; i < angles.length; i++) {
      const next = i < angles.length - 1 ? angles[i + 1] : angles[0] + Math.PI * 2;
      const gap = next - angles[i];
      if (gap > maxGap) {
        maxGap = gap;
        bestAngle = angles[i] + gap / 2;
      }
    }
    angle = bestAngle;
  }

  const msg = {
    el,
    angle,
    speed: 0.25 + Math.random() * 0.15,
    floatPhase: Math.random() * Math.PI * 2,
    tiltY: (Math.random() - 0.5) * 0.4,
    age: 0,
    state: 'entering',
    enterDur: 0.5,
    leaveDur: 0.8,
  };

  messages.push(msg);
}

function destroyMessage(msg) {
  const idx = messages.indexOf(msg);
  if (idx !== -1) messages.splice(idx, 1);
  if (msg.el.parentNode) msg.el.parentNode.removeChild(msg.el);
}

// 動畫循環
let lastTime = 0;
let animId = null;

function tick(timestamp) {
  animId = requestAnimationFrame(tick);
  if (!lastTime) { lastTime = timestamp; return; }
  const dt = Math.min((timestamp - lastTime) / 1000, 0.1);
  lastTime = timestamp;

  // 取得 Orb 螢幕座標
  const center = getOrbScreenPos ? getOrbScreenPos() : { x: window.innerWidth / 2, y: window.innerHeight / 2 };

  for (let i = messages.length - 1; i >= 0; i--) {
    const msg = messages[i];
    msg.age += dt;
    msg.angle += msg.speed * dt;

    // 狀態轉換
    if (msg.state === 'entering' && msg.age > msg.enterDur) msg.state = 'orbiting';
    if (msg.state === 'orbiting' && msg.age > LIFETIME - msg.leaveDur) msg.state = 'leaving';
    if (msg.age >= LIFETIME) { destroyMessage(msg); continue; }

    // 透明度 + 縮放
    let opacity, scale;
    if (msg.state === 'entering') {
      const t = msg.age / msg.enterDur;
      opacity = t;
      scale = 0.7 + t * 0.3;
    } else if (msg.state === 'leaving') {
      const t = (msg.age - (LIFETIME - msg.leaveDur)) / msg.leaveDur;
      opacity = 1 - t;
      scale = 1 - t * 0.2;
    } else {
      opacity = 0.85 + Math.sin(msg.age * 1.5) * 0.15;
      scale = 1;
    }

    // 橢圓軌道位置
    const radius = msg.state === 'entering'
      ? ORBIT_RADIUS * (0.3 + 0.7 * (msg.age / msg.enterDur))
      : msg.state === 'leaving'
        ? ORBIT_RADIUS + ((msg.age - (LIFETIME - msg.leaveDur)) / msg.leaveDur) * 60
        : ORBIT_RADIUS;

    const x = center.x + Math.cos(msg.angle) * radius;
    const floatY = Math.sin(msg.age * 0.8 + msg.floatPhase) * FLOAT_AMP;
    const y = center.y + Math.sin(msg.angle) * radius * 0.45 * (1 + msg.tiltY) + floatY;

    // 深度感：後方的更小更暗
    const depthFactor = 0.85 + 0.15 * ((Math.sin(msg.angle) + 1) / 2);

    msg.el.style.opacity = Math.max(0, opacity * depthFactor);
    msg.el.style.transform = `translate(-50%, -50%) scale(${scale * depthFactor})`;
    msg.el.style.left = x + 'px';
    msg.el.style.top = y + 'px';
    // 後方的排在更低 z-index
    msg.el.style.zIndex = Math.round(depthFactor * 10);
  }
}

// 初始化
export function initOrbMessages(screenPosFn) {
  getOrbScreenPos = screenPosFn;
  createContainer();
  lastTime = 0;
  animId = requestAnimationFrame(tick);
}

// Demo
const demoMessages = [
  'HEARTBEAT OK',
  '爸，早安 ☀️',
  'MEMORY.MD UPDATED',
  'NEW EMAIL: 3 UNREAD',
  'CALENDAR: 會議 14:00',
  'CPU: 12% | MEM: 5.2GB',
  'SKILL: WHISPER READY',
  'CRON JOB EXECUTED',
];

let demoTimer = null;

export function startDemo() {
  let idx = 0;
  function next() {
    addOrbMessage(demoMessages[idx % demoMessages.length]);
    idx++;
    demoTimer = setTimeout(next, 3000 + Math.random() * 4000);
  }
  demoTimer = setTimeout(next, 1500);
}

export function stopDemo() {
  if (demoTimer) clearTimeout(demoTimer);
  if (animId) cancelAnimationFrame(animId);
}
