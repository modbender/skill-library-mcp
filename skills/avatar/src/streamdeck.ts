/**
 * Stream Deck integration for OpenClaw Avatar
 *
 * This module is optional - if Stream Deck hardware is not available
 * or the dependencies are not installed, it gracefully disables itself.
 */

import { loadConfig } from './config/index.js';
import type { StreamDeckColors, StreamDeckButtonPrompt } from './config/schema.js';
import { DEFAULT_STREAMDECK_COLORS, DEFAULT_BUTTON_PROMPTS } from './config/defaults.js';

// Load configuration
const config = loadConfig();

// Types for dynamic imports
type StreamDeckInstance = {
  ICON_SIZE?: number;
  NUM_KEYS?: number;
  clearPanel(): Promise<void>;
  fillKeyBuffer(keyIndex: number, buffer: Buffer): Promise<void>;
  on(event: string, callback: (data: unknown) => void): void;
};

type Canvas = {
  getContext(type: '2d'): CanvasRenderingContext2D;
  toBuffer(type: 'raw'): Buffer;
};

type CanvasRenderingContext2D = {
  fillStyle: string;
  strokeStyle: string;
  lineWidth: number;
  lineCap: string;
  lineJoin: string;
  globalAlpha: number;
  font: string;
  textAlign: string;
  textBaseline: string;
  shadowColor: string;
  shadowBlur: number;
  save(): void;
  restore(): void;
  beginPath(): void;
  closePath(): void;
  moveTo(x: number, y: number): void;
  lineTo(x: number, y: number): void;
  arc(x: number, y: number, r: number, start: number, end: number, ccw?: boolean): void;
  fill(): void;
  stroke(): void;
  fillRect(x: number, y: number, w: number, h: number): void;
  fillText(text: string, x: number, y: number): void;
  roundRect(x: number, y: number, w: number, h: number, r: number): void;
  scale(x: number, y: number): void;
  translate(x: number, y: number): void;
  drawImage(image: Canvas, sx: number, sy: number, sw: number, sh: number, dx: number, dy: number, dw: number, dh: number): void;
  measureText(text: string): { width: number };
  createRadialGradient(x0: number, y0: number, r0: number, x1: number, y1: number, r1: number): { addColorStop(offset: number, color: string): void };
};

type CreateCanvasFn = (w: number, h: number) => Canvas;
type ButtonCallback = (action: string | null) => void | Promise<void>;

// Dynamic imports - using any for optional dependencies
// eslint-disable-next-line @typescript-eslint/no-explicit-any
let listStreamDecks: (() => Promise<Array<{ path: string; model: string }>>) | null = null;
// eslint-disable-next-line @typescript-eslint/no-explicit-any
let openStreamDeck: ((path: string, options?: unknown) => Promise<StreamDeckInstance>) | null = null;
let createCanvas: CreateCanvasFn | null = null;

// State
let deck: StreamDeckInstance | null = null;
let onButtonPress: ButtonCallback | null = null;
let iconSize = 72;
let currentPage = 'main';
let talkActive = false;
let muteActive = false;
let hasDetail = false;
let alertActive = false;
let isSpeaking = false;
let alertMessageId: string | null = null;

// Get colors from config or defaults
const COLORS: StreamDeckColors = {
  ...DEFAULT_STREAMDECK_COLORS,
  ...(config.integrations.streamDeck.colors || {}),
};

// Icon drawing functions
type IconDrawFn = (ctx: CanvasRenderingContext2D, s: number) => void;

const ICONS: Record<string, IconDrawFn> = {
  mic: (ctx, s) => {
    const cx = s / 2, cy = s * 0.36, w = s * 0.12, h = s * 0.18;
    ctx.beginPath();
    ctx.roundRect(cx - w, cy - h, w * 2, h * 2, w);
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(cx, cy + h * 0.3, w * 1.5, 0, Math.PI);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(cx, cy + h * 0.3 + w * 1.5);
    ctx.lineTo(cx, cy + h * 0.3 + w * 2.2);
    ctx.moveTo(cx - w, cy + h * 0.3 + w * 2.2);
    ctx.lineTo(cx + w, cy + h * 0.3 + w * 2.2);
    ctx.stroke();
  },
  stop: (ctx, s) => {
    const sz = s * 0.26;
    ctx.fillRect(s / 2 - sz / 2, s * 0.36 - sz / 2, sz, sz);
  },
  mute: (ctx, s) => {
    const cx = s * 0.38, cy = s * 0.36;
    ctx.beginPath();
    ctx.moveTo(cx - s * 0.08, cy - s * 0.06);
    ctx.lineTo(cx + s * 0.02, cy - s * 0.06);
    ctx.lineTo(cx + s * 0.1, cy - s * 0.14);
    ctx.lineTo(cx + s * 0.1, cy + s * 0.14);
    ctx.lineTo(cx + s * 0.02, cy + s * 0.06);
    ctx.lineTo(cx - s * 0.08, cy + s * 0.06);
    ctx.closePath();
    ctx.stroke();
    const xx = s * 0.58;
    ctx.beginPath();
    ctx.moveTo(xx, cy - s * 0.08);
    ctx.lineTo(xx + s * 0.12, cy + s * 0.08);
    ctx.moveTo(xx + s * 0.12, cy - s * 0.08);
    ctx.lineTo(xx, cy + s * 0.08);
    ctx.stroke();
  },
  unmute: (ctx, s) => {
    const cx = s * 0.35, cy = s * 0.36;
    ctx.beginPath();
    ctx.moveTo(cx - s * 0.08, cy - s * 0.06);
    ctx.lineTo(cx + s * 0.02, cy - s * 0.06);
    ctx.lineTo(cx + s * 0.1, cy - s * 0.14);
    ctx.lineTo(cx + s * 0.1, cy + s * 0.14);
    ctx.lineTo(cx + s * 0.02, cy + s * 0.06);
    ctx.lineTo(cx - s * 0.08, cy + s * 0.06);
    ctx.closePath();
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(cx + s * 0.12, cy, s * 0.08, -0.6, 0.6);
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(cx + s * 0.12, cy, s * 0.14, -0.6, 0.6);
    ctx.stroke();
  },
  status: (ctx, s) => {
    const x = s * 0.22, y = s * 0.2, w = s * 0.56, h = s * 0.42;
    const gap = s * 0.04;
    const bw = (w - gap) / 2, bh = (h - gap) / 2;
    ctx.fillRect(x, y, bw, bh);
    ctx.fillRect(x + bw + gap, y, bw, bh);
    ctx.fillRect(x, y + bh + gap, bw, bh);
    ctx.fillRect(x + bw + gap, y + bh + gap, bw, bh);
  },
  back: (ctx, s) => {
    const cx = s / 2, cy = s * 0.36;
    ctx.beginPath();
    ctx.moveTo(cx + s * 0.12, cy - s * 0.12);
    ctx.lineTo(cx - s * 0.06, cy);
    ctx.lineTo(cx + s * 0.12, cy + s * 0.12);
    ctx.stroke();
  },
  email: (ctx, s) => {
    const x = s * 0.2, y = s * 0.22, w = s * 0.6, h = s * 0.36;
    ctx.beginPath();
    ctx.roundRect(x, y, w, h, 3);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(s / 2, y + h * 0.5);
    ctx.lineTo(x + w, y);
    ctx.stroke();
  },
  calendar: (ctx, s) => {
    const x = s * 0.2, y = s * 0.2, w = s * 0.6, h = s * 0.44;
    ctx.beginPath();
    ctx.roundRect(x, y + h * 0.15, w, h * 0.85, 3);
    ctx.stroke();
    ctx.fillRect(x, y + h * 0.15, w, h * 0.22);
    ctx.beginPath();
    ctx.moveTo(s * 0.35, y); ctx.lineTo(s * 0.35, y + h * 0.25);
    ctx.moveTo(s * 0.65, y); ctx.lineTo(s * 0.65, y + h * 0.25);
    ctx.stroke();
    const dotR = 1.5;
    for (let r = 0; r < 2; r++) {
      for (let c = 0; c < 3; c++) {
        ctx.beginPath();
        ctx.arc(x + w * 0.25 + c * w * 0.25, y + h * 0.55 + r * h * 0.2, dotR, 0, Math.PI * 2);
        ctx.fill();
      }
    }
  },
  hubspot: (ctx, s) => {
    const cx = s / 2, cy = s * 0.36, r = s * 0.16;
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(cx, cy, r * 0.45, 0, Math.PI * 2);
    ctx.fill();
    for (let i = 0; i < 6; i++) {
      const a = (i * Math.PI) / 3;
      ctx.beginPath();
      ctx.moveTo(cx + Math.cos(a) * r * 0.8, cy + Math.sin(a) * r * 0.8);
      ctx.lineTo(cx + Math.cos(a) * r * 1.3, cy + Math.sin(a) * r * 1.3);
      ctx.stroke();
    }
  },
  notion: (ctx, s) => {
    const x = s * 0.25, y = s * 0.18, w = s * 0.5, h = s * 0.46;
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(x + w * 0.65, y);
    ctx.lineTo(x + w, y + h * 0.2);
    ctx.lineTo(x + w, y + h);
    ctx.lineTo(x, y + h);
    ctx.closePath();
    ctx.stroke();
    for (let i = 0; i < 3; i++) {
      ctx.beginPath();
      ctx.moveTo(x + w * 0.15, y + h * 0.4 + i * h * 0.17);
      ctx.lineTo(x + w * 0.75, y + h * 0.4 + i * h * 0.17);
      ctx.stroke();
    }
  },
  slack: (ctx, s) => {
    const cx = s / 2, cy = s * 0.34, w = s * 0.28, h = s * 0.22;
    ctx.beginPath();
    ctx.roundRect(cx - w, cy - h, w * 2, h * 2, 6);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(cx - w * 0.3, cy + h);
    ctx.lineTo(cx - w * 0.6, cy + h * 1.5);
    ctx.lineTo(cx + w * 0.1, cy + h);
    ctx.stroke();
    for (let i = 0; i < 3; i++) {
      ctx.beginPath();
      ctx.arc(cx - w * 0.5 + i * w * 0.5, cy, 2, 0, Math.PI * 2);
      ctx.fill();
    }
  },
  customers: (ctx, s) => {
    const cx = s / 2;
    ctx.beginPath();
    ctx.arc(cx, s * 0.26, s * 0.08, 0, Math.PI * 2);
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(cx, s * 0.56, s * 0.16, Math.PI, 0);
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(cx - s * 0.16, s * 0.29, s * 0.06, 0, Math.PI * 2);
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(cx - s * 0.16, s * 0.52, s * 0.12, Math.PI, 0);
    ctx.stroke();
  },
  meetings: (ctx, s) => {
    const cx = s / 2, cy = s * 0.36, r = s * 0.18;
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.lineTo(cx, cy - r * 0.65);
    ctx.moveTo(cx, cy);
    ctx.lineTo(cx + r * 0.5, cy + r * 0.2);
    ctx.stroke();
  },
  pipeline: (ctx, s) => {
    const x = s * 0.2, bw = s * 0.12, gap = s * 0.05, base = s * 0.6;
    const heights = [0.25, 0.4, 0.55, 0.35];
    for (let i = 0; i < 4; i++) {
      const bx = x + i * (bw + gap);
      const bh = s * heights[i];
      ctx.fillRect(bx, base - bh, bw, bh);
    }
  },
  brief: (ctx, s) => {
    const x = s * 0.25, y = s * 0.18, w = s * 0.5, h = s * 0.46;
    ctx.beginPath();
    ctx.roundRect(x, y + h * 0.1, w, h * 0.9, 3);
    ctx.stroke();
    ctx.beginPath();
    ctx.roundRect(x + w * 0.25, y, w * 0.5, h * 0.2, 2);
    ctx.stroke();
    for (let i = 0; i < 3; i++) {
      ctx.beginPath();
      ctx.moveTo(x + w * 0.15, y + h * 0.4 + i * h * 0.18);
      ctx.lineTo(x + w * 0.85, y + h * 0.4 + i * h * 0.18);
      ctx.stroke();
    }
  },
  followups: (ctx, s) => {
    const cx = s / 2, cy = s * 0.36;
    ctx.beginPath();
    ctx.arc(cx, cy, s * 0.14, Math.PI, 0, true);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(cx + s * 0.14 - s * 0.06, cy - s * 0.06);
    ctx.lineTo(cx + s * 0.14, cy);
    ctx.lineTo(cx + s * 0.14 + s * 0.06, cy - s * 0.06);
    ctx.stroke();
  },
  churn: (ctx, s) => {
    const cx = s / 2, top = s * 0.2, bot = s * 0.56, hw = s * 0.2;
    ctx.beginPath();
    ctx.moveTo(cx, top);
    ctx.lineTo(cx + hw, bot);
    ctx.lineTo(cx - hw, bot);
    ctx.closePath();
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(cx, top + (bot - top) * 0.35);
    ctx.lineTo(cx, top + (bot - top) * 0.65);
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(cx, top + (bot - top) * 0.8, 1.5, 0, Math.PI * 2);
    ctx.fill();
  },
  alert: (ctx, s) => {
    const cx = s / 2, cy = s * 0.34;
    ctx.lineWidth = 2;
    ctx.globalAlpha = 0.5;
    const rays: [number, number, number, number][] = [
      [-0.28, -0.12, -0.20, -0.06],
      [0.28, -0.12, 0.20, -0.06],
      [-0.24, 0.02, -0.17, 0.04],
      [0.24, 0.02, 0.17, 0.04],
    ];
    for (const [x1, y1, x2, y2] of rays) {
      ctx.beginPath();
      ctx.moveTo(cx + s * x1, cy + s * y1);
      ctx.lineTo(cx + s * x2, cy + s * y2);
      ctx.stroke();
    }
    ctx.globalAlpha = 1.0;
    ctx.lineWidth = 2.5;
    const r = s * 0.18;
    ctx.beginPath();
    ctx.arc(cx, cy - r * 0.15, r, Math.PI * 0.82, Math.PI * 0.18, true);
    ctx.lineTo(cx + r * 1.4, cy + r * 1.1);
    ctx.lineTo(cx - r * 1.4, cy + r * 1.1);
    ctx.closePath();
    ctx.fill();
    ctx.fillRect(cx - r * 1.6, cy + r * 1.1, r * 3.2, s * 0.04);
    ctx.beginPath();
    ctx.arc(cx, cy + r * 1.45, r * 0.28, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#dc2626';
    ctx.beginPath();
    ctx.roundRect(cx - 1.5, cy - r * 0.55, 3, r * 0.7, 1);
    ctx.fill();
    ctx.beginPath();
    ctx.arc(cx, cy + r * 0.4, 1.8, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#ffffff';
  },
  alertDone: (ctx, s) => {
    const cx = s / 2, cy = s * 0.36, r = s * 0.18;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.stroke();
    ctx.lineWidth = 3.5;
    ctx.beginPath();
    ctx.moveTo(cx - r * 0.5, cy);
    ctx.lineTo(cx - r * 0.1, cy + r * 0.45);
    ctx.lineTo(cx + r * 0.55, cy - r * 0.35);
    ctx.stroke();
  },
  clear: (ctx, s) => {
    const cx = s / 2, cy = s * 0.36, r = s * 0.14;
    ctx.beginPath();
    ctx.moveTo(cx - r, cy - r);
    ctx.lineTo(cx + r, cy + r);
    ctx.moveTo(cx + r, cy - r);
    ctx.lineTo(cx - r, cy + r);
    ctx.stroke();
  },
  interrupt: (ctx, s) => {
    const cx = s / 2, cy = s * 0.36, r = s * 0.15;
    ctx.beginPath();
    ctx.roundRect(cx - r, cy - r, r * 2, r * 2, 3);
    ctx.fill();
  },
  prepMtg: (ctx, s) => {
    const cx = s / 2, cy = s * 0.32, r = s * 0.12;
    ctx.beginPath();
    ctx.arc(cx, cy, r, Math.PI * 0.8, Math.PI * 0.2, true);
    ctx.lineTo(cx + r * 0.5, cy + r * 1.5);
    ctx.lineTo(cx - r * 0.5, cy + r * 1.5);
    ctx.closePath();
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(cx - r * 0.35, cy + r * 1.7);
    ctx.lineTo(cx + r * 0.35, cy + r * 1.7);
    ctx.moveTo(cx - r * 0.25, cy + r * 1.95);
    ctx.lineTo(cx + r * 0.25, cy + r * 1.95);
    ctx.stroke();
  },
};

async function drawButton(keyIndex: number, iconFn: IconDrawFn, label: string, bgColor: string): Promise<void> {
  if (!deck || !createCanvas) return;
  try {
    const canvas = createCanvas(iconSize, iconSize);
    const ctx = canvas.getContext('2d');
    const s = iconSize;

    ctx.fillStyle = bgColor;
    ctx.beginPath();
    ctx.roundRect(0, 0, s, s, 8);
    ctx.fill();

    ctx.save();
    ctx.strokeStyle = '#ffffff';
    ctx.fillStyle = '#ffffff';
    ctx.lineWidth = 2.5;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    iconFn(ctx, s);
    ctx.restore();

    ctx.fillStyle = '#ffffff';
    ctx.font = `bold ${Math.floor(s * 0.15)}px sans-serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(label, s / 2, s * 0.82);

    const rgba = canvas.toBuffer('raw');
    const rgb = Buffer.alloc(s * s * 3);
    for (let i = 0, j = 0; i < rgba.length; i += 4, j += 3) {
      rgb[j] = rgba[i];
      rgb[j + 1] = rgba[i + 1];
      rgb[j + 2] = rgba[i + 2];
    }
    await deck.fillKeyBuffer(keyIndex, rgb);
  } catch (err) {
    console.error(`Failed to draw button ${keyIndex}:`, (err as Error).message);
  }
}

async function drawLabel(keyIndex: number, text: string, bgColor: string): Promise<void> {
  if (!deck || !createCanvas) return;
  try {
    const canvas = createCanvas(iconSize, iconSize);
    const ctx = canvas.getContext('2d');
    const s = iconSize;
    ctx.fillStyle = bgColor;
    ctx.beginPath();
    ctx.roundRect(0, 0, s, s, 8);
    ctx.fill();
    ctx.fillStyle = '#94a3b8';
    ctx.font = `${Math.floor(s * 0.18)}px sans-serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, s / 2, s / 2);
    const rgba = canvas.toBuffer('raw');
    const rgb = Buffer.alloc(s * s * 3);
    for (let i = 0, j = 0; i < rgba.length; i += 4, j += 3) {
      rgb[j] = rgba[i];
      rgb[j + 1] = rgba[i + 1];
      rgb[j + 2] = rgba[i + 2];
    }
    await deck.fillKeyBuffer(keyIndex, rgb);
  } catch {
    // Ignore errors
  }
}

async function drawMainPage(): Promise<void> {
  currentPage = 'main';
  if (!deck) return;
  await deck.clearPanel();
  await drawButton(2, ICONS.status, 'Check...', COLORS.indigo);
  if (isSpeaking) {
    await drawButton(7, ICONS.interrupt, 'Stop', COLORS.red);
  } else {
    await drawButton(7, talkActive ? ICONS.stop : ICONS.mic, talkActive ? 'Stop' : 'Talk', talkActive ? COLORS.red : COLORS.purple);
  }
  await drawButton(10, muteActive ? ICONS.unmute : ICONS.mute, muteActive ? 'Unmute' : 'Mute', muteActive ? COLORS.red : COLORS.slate);

  if (alertActive) {
    await drawButton(4, ICONS.alertDone, 'Resolved', COLORS.green);
  } else {
    await drawButton(4, ICONS.alert, 'HELP', COLORS.orange);
  }

  if (hasDetail) {
    await drawButton(0, ICONS.followups, 'Follow up', COLORS.teal);
    await drawButton(1, ICONS.brief, 'Draft', COLORS.green);
    await drawButton(9, ICONS.clear, 'Clear', COLORS.slate);
    await drawLabel(11, 'Send to...', COLORS.dark);
    await drawButton(12, ICONS.slack, 'Slack', COLORS.slack);
    await drawButton(13, ICONS.email, 'Email', COLORS.blue);
  }
}

async function drawStatusPage(): Promise<void> {
  currentPage = 'status';
  if (!deck) return;
  await deck.clearPanel();
  await drawButton(0, ICONS.email, 'Email', COLORS.blue);
  await drawButton(1, ICONS.calendar, 'Calendar', COLORS.green);
  await drawButton(2, ICONS.hubspot, 'HubSpot', COLORS.orange);
  await drawButton(3, ICONS.notion, 'Notion', COLORS.slate);
  await drawButton(4, ICONS.slack, 'Slack', COLORS.blue);
  await drawButton(5, ICONS.customers, 'Customers', COLORS.teal);
  await drawButton(6, ICONS.meetings, 'Meetings', COLORS.green);
  await drawButton(7, ICONS.pipeline, 'Pipeline', COLORS.orange);
  await drawButton(8, ICONS.brief, 'Brief', COLORS.indigo);
  await drawButton(9, ICONS.followups, 'Follow-ups', COLORS.teal);
  await drawButton(10, ICONS.churn, 'Churn Risk', COLORS.orange);
  await drawButton(11, ICONS.prepMtg, 'Prep Mtg', COLORS.green);
  await drawButton(14, ICONS.back, 'Back', COLORS.slate);
}

function handleButton(keyIndex: number): string | null {
  if (currentPage === 'main') {
    if (keyIndex === 2) {
      drawStatusPage();
      return null;
    }
    if (keyIndex === 7) {
      if (isSpeaking) {
        isSpeaking = false;
        drawButton(7, talkActive ? ICONS.stop : ICONS.mic, talkActive ? 'Stop' : 'Talk', talkActive ? COLORS.red : COLORS.purple);
        return 'interrupt';
      }
      talkActive = !talkActive;
      drawButton(7, talkActive ? ICONS.stop : ICONS.mic, talkActive ? 'Stop' : 'Talk', talkActive ? COLORS.red : COLORS.purple);
      return talkActive ? 'push_to_talk' : 'stop';
    }
    if (keyIndex === 4) {
      alertActive = !alertActive;
      if (alertActive) {
        playAlertAnimation();
      } else {
        drawMainPage();
      }
      return alertActive ? 'alert_send' : 'alert_resolved';
    }
    if (keyIndex === 10) {
      muteActive = !muteActive;
      drawButton(10, muteActive ? ICONS.unmute : ICONS.mute, muteActive ? 'Unmute' : 'Mute', muteActive ? COLORS.red : COLORS.slate);
      return muteActive ? 'mute' : 'unmute';
    }
    if (!hasDetail) return null;
    if (keyIndex === 0) return 'followup_detail';
    if (keyIndex === 1) return 'draft_detail';
    if (keyIndex === 9) return 'clear';
    if (keyIndex === 12) return 'send_slack';
    if (keyIndex === 13) return 'send_email';
    return null;
  }

  if (currentPage === 'status') {
    if (keyIndex === 14) {
      drawMainPage();
      return null;
    }
    const statusActions: Record<number, string> = {
      0: 'check_email',
      1: 'check_calendar',
      2: 'check_hubspot',
      3: 'search_notion',
      4: 'check_slack',
      5: 'customer_health',
      6: 'todays_meetings',
      7: 'deal_pipeline',
      8: 'morning_brief',
      9: 'followups',
      10: 'churn_risk',
      11: 'prep_meeting',
    };
    const action = statusActions[keyIndex];
    if (action) {
      setTimeout(() => drawMainPage(), 500);
    }
    return action || null;
  }

  return null;
}

// Animation state
let alertInterval: ReturnType<typeof setInterval> | null = null;
let alertFrame = 0;
let loadingInterval: ReturnType<typeof setInterval> | null = null;
let loadingFrame = 0;

const FULL_W = 5;
const FULL_H = 3;

async function playAlertAnimation(): Promise<void> {
  if (!deck || !createCanvas) return;
  alertFrame = 0;
  const totalFrames = 40;

  return new Promise((resolve) => {
    alertInterval = setInterval(async () => {
      if (alertFrame >= totalFrames) {
        if (alertInterval) clearInterval(alertInterval);
        alertInterval = null;
        await drawMainPage();
        resolve();
        return;
      }

      const s = iconSize;
      const t = alertFrame / totalFrames;
      const fullW = s * FULL_W;
      const fullH = s * FULL_H;
      const canvas = createCanvas!(fullW, fullH);
      const ctx = canvas.getContext('2d');

      ctx.fillStyle = '#0a0a1a';
      ctx.fillRect(0, 0, fullW, fullH);

      const cx = fullW / 2;
      const cy = fullH / 2;
      const maxR = Math.sqrt(cx * cx + cy * cy);

      for (let ring = 0; ring < 4; ring++) {
        const ringT = (t * 2 + ring * 0.25) % 1;
        const r = ringT * maxR;
        const alpha = Math.max(0, 1 - ringT) * 0.6;
        ctx.strokeStyle = `rgba(249, 115, 22, ${alpha})`;
        ctx.lineWidth = 6 + (1 - ringT) * 10;
        ctx.beginPath();
        ctx.arc(cx, cy, r, 0, Math.PI * 2);
        ctx.stroke();
      }

      const bellScale = 1 + Math.sin(alertFrame * 0.5) * 0.15;
      const shake = Math.sin(alertFrame * 1.5) * 4;
      ctx.save();
      ctx.translate(cx + shake, cy);
      ctx.scale(bellScale, bellScale);
      ctx.fillStyle = '#ffffff';
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 3;
      const br = s * 0.35;
      ctx.beginPath();
      ctx.arc(0, -br * 0.15, br, Math.PI * 0.82, Math.PI * 0.18, true);
      ctx.lineTo(br * 1.4, br * 1.1);
      ctx.lineTo(-br * 1.4, br * 1.1);
      ctx.closePath();
      ctx.fill();
      ctx.fillRect(-br * 1.6, br * 1.1, br * 3.2, s * 0.06);
      ctx.beginPath();
      ctx.arc(0, br * 1.45, br * 0.28, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = '#f97316';
      ctx.beginPath();
      ctx.roundRect(-2.5, -br * 0.55, 5, br * 0.7, 2);
      ctx.fill();
      ctx.beginPath();
      ctx.arc(0, br * 0.4, 3, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();

      const textAlpha = Math.min(1, t * 3);
      ctx.fillStyle = `rgba(255, 255, 255, ${textAlpha})`;
      ctx.font = `bold ${Math.floor(s * 0.5)}px sans-serif`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText('HELP', cx, fullH - s * 0.4);

      for (let key = 0; key < 15; key++) {
        const col = key % 5;
        const row = Math.floor(key / 5);
        const tileCanvas = createCanvas!(s, s);
        const tileCtx = tileCanvas.getContext('2d');
        tileCtx.drawImage(canvas, col * s, row * s, s, s, 0, 0, s, s);
        const rgba = tileCanvas.toBuffer('raw');
        const rgb = Buffer.alloc(s * s * 3);
        for (let j = 0, k = 0; j < rgba.length; j += 4, k += 3) {
          rgb[k] = rgba[j];
          rgb[k + 1] = rgba[j + 1];
          rgb[k + 2] = rgba[j + 2];
        }
        try {
          await deck!.fillKeyBuffer(key, rgb);
        } catch {
          // Ignore
        }
      }

      alertFrame++;
    }, 50);
  });
}

async function animateLoading(): Promise<void> {
  if (!deck || !createCanvas) return;
  loadingFrame++;
  const s = iconSize;
  const t = loadingFrame * 0.04;

  const fullW = s * FULL_W;
  const fullH = s * FULL_H;
  const canvas = createCanvas(fullW, fullH);
  const ctx = canvas.getContext('2d');

  ctx.fillStyle = '#0a0a1a';
  ctx.fillRect(0, 0, fullW, fullH);

  for (let x = 0; x < fullW; x += 4) {
    for (let y = 0; y < fullH; y += 4) {
      const nx = x / fullW;
      const ny = y / fullH;
      const d = Math.sqrt((nx - 0.5) ** 2 + (ny - 0.5) ** 2);
      const wave = Math.sin(d * 10 - t * 3) * 0.5 + 0.5;
      const b = wave * 0.25;
      ctx.fillStyle = `rgb(${Math.floor(20 + b * 60)}, ${Math.floor(10 + b * 30)}, ${Math.floor(40 + b * 120)})`;
      ctx.fillRect(x, y, 4, 4);
    }
  }

  const text = config.app.name.toUpperCase();
  const fontSize = Math.floor(s * 0.7);
  ctx.font = `bold ${fontSize}px sans-serif`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';

  const centerX = fullW / 2;
  const centerY = fullH / 2;

  const floatX = Math.sin(t * 1.2) * s * 0.3;
  const floatY = Math.cos(t * 0.9) * s * 0.15;

  const metrics = ctx.measureText(text);
  const totalW = metrics.width;
  let charX = centerX - totalW / 2 + floatX;

  for (let i = 0; i < text.length; i++) {
    const char = text[i];
    const charW = ctx.measureText(char).width;
    const cx = charX + charW / 2;

    const letterFloat = Math.sin(t * 2.5 + i * 0.8) * s * 0.12;
    const letterScale = 1 + Math.sin(t * 2 + i * 0.6) * 0.08;

    const hue = (t * 30 + i * 25) % 360;
    const r = Math.floor(150 + Math.sin((hue) * Math.PI / 180) * 105);
    const g = Math.floor(120 + Math.sin((hue + 120) * Math.PI / 180) * 80);
    const b = Math.floor(200 + Math.sin((hue + 240) * Math.PI / 180) * 55);

    ctx.save();
    ctx.translate(cx, centerY + floatY + letterFloat);
    ctx.scale(letterScale, letterScale);

    ctx.shadowColor = `rgb(${r}, ${g}, ${b})`;
    ctx.shadowBlur = 20;
    ctx.fillStyle = `rgb(${r}, ${g}, ${b})`;
    ctx.fillText(char, 0, 0);

    ctx.shadowBlur = 8;
    ctx.fillStyle = `rgb(${Math.min(255, r + 60)}, ${Math.min(255, g + 60)}, ${Math.min(255, b + 30)})`;
    ctx.fillText(char, 0, 0);

    ctx.restore();
    charX += charW;
  }

  for (let p = 0; p < 8; p++) {
    const px = (Math.sin(t * 1.3 + p * 2.1) * 0.4 + 0.5) * fullW;
    const py = (Math.cos(t * 1.7 + p * 1.7) * 0.4 + 0.5) * fullH;
    const sparkle = Math.sin(t * 4 + p * 3) * 0.5 + 0.5;
    if (sparkle > 0.7) {
      const sr = 2 + sparkle * 3;
      const grad = ctx.createRadialGradient(px, py, 0, px, py, sr);
      grad.addColorStop(0, `rgba(220, 200, 255, ${sparkle})`);
      grad.addColorStop(1, 'rgba(220, 200, 255, 0)');
      ctx.fillStyle = grad as unknown as string;
      ctx.beginPath();
      ctx.arc(px, py, sr, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  for (let key = 0; key < 15; key++) {
    const col = key % 5;
    const row = Math.floor(key / 5);

    const tileCanvas = createCanvas(s, s);
    const tileCtx = tileCanvas.getContext('2d');
    tileCtx.drawImage(canvas, col * s, row * s, s, s, 0, 0, s, s);

    const rgba = tileCanvas.toBuffer('raw');
    const rgb = Buffer.alloc(s * s * 3);
    for (let j = 0, k = 0; j < rgba.length; j += 4, k += 3) {
      rgb[k] = rgba[j];
      rgb[k + 1] = rgba[j + 1];
      rgb[k + 2] = rgba[j + 2];
    }
    try {
      await deck!.fillKeyBuffer(key, rgb);
    } catch {
      // Ignore
    }
  }
}

export function setLoading(active: boolean): void {
  if (active && !loadingInterval) {
    loadingFrame = 0;
    loadingInterval = setInterval(() => animateLoading(), 50);
  } else if (!active) {
    if (loadingInterval) {
      clearInterval(loadingInterval);
      loadingInterval = null;
    }
    drawMainPage();
  }
}

export function setHasDetail(value: boolean): void {
  hasDetail = value;
  if (currentPage === 'main') {
    drawMainPage();
  }
}

export function setAlertMessageId(id: string | null): void {
  alertMessageId = id;
}

export async function setSpeaking(active: boolean): Promise<void> {
  isSpeaking = active;
  if (!deck || currentPage !== 'main') return;
  if (active) {
    await drawButton(7, ICONS.interrupt, 'Stop', COLORS.red);
  } else {
    await drawButton(7, talkActive ? ICONS.stop : ICONS.mic, talkActive ? 'Stop' : 'Talk', talkActive ? COLORS.red : COLORS.purple);
  }
}

export function getAlertMessageId(): string | null {
  return alertMessageId;
}

// Button prompts from config
export const BUTTON_PROMPTS: StreamDeckButtonPrompt = {
  ...DEFAULT_BUTTON_PROMPTS,
  ...(config.integrations.streamDeck.buttonPrompts || {}),
};

export function getButtonAction(action: string): string {
  return action;
}

/**
 * Initialize Stream Deck with graceful failure
 */
export async function initStreamDeck(callback: ButtonCallback): Promise<StreamDeckInstance | null> {
  if (!config.integrations.streamDeck.enabled) {
    console.log('Stream Deck disabled in config');
    return null;
  }

  onButtonPress = callback;

  try {
    // Dynamic import of optional dependencies
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const streamDeckModule = await import('@elgato-stream-deck/node') as any;
    listStreamDecks = streamDeckModule.listStreamDecks;
    openStreamDeck = streamDeckModule.openStreamDeck as (path: string, options?: unknown) => Promise<StreamDeckInstance>;

    const canvasModule = await import('canvas');
    createCanvas = canvasModule.createCanvas as CreateCanvasFn;
  } catch (e) {
    console.warn('Stream Deck dependencies not available:', (e as Error).message);
    console.log('Install optional dependencies with: npm install @elgato-stream-deck/node canvas');
    return null;
  }

  try {
    const devices = await listStreamDecks!();
    if (devices.length === 0) {
      console.log('No Stream Deck found');
      return null;
    }

    deck = await openStreamDeck!(devices[0].path);
    iconSize = deck.ICON_SIZE || 72;
    console.log(`Stream Deck connected: ${devices[0].model} (${deck.NUM_KEYS || 15} keys, ${iconSize}px icons)`);

    await drawMainPage();

    deck.on('down', (evt) => {
      const keyIndex = typeof evt === 'number' ? evt : (evt as { index?: number; key?: number })?.index ?? (evt as { key?: number })?.key ?? evt;
      console.log(`Stream Deck key ${keyIndex} pressed (page: ${currentPage})`);
      const action = handleButton(keyIndex as number);
      if (action && onButtonPress) onButtonPress(action);
    });

    deck.on('error', (err) => {
      console.error('Stream Deck error:', (err as Error).message);
    });

    return deck;
  } catch (e) {
    console.warn('Stream Deck init failed:', (e as Error).message);
    return null;
  }
}

export { drawButton, ICONS };
