const { app, BrowserWindow, screen, desktopCapturer, session, ipcMain, globalShortcut } = require('electron');
const path = require('path');
const fs = require('fs');

app.commandLine.appendSwitch('disable-gpu-shader-disk-cache');

// Load config
let config = {};
try {
  config = JSON.parse(fs.readFileSync(path.join(__dirname, 'config.json'), 'utf8'));
} catch (e) {
  console.log('No config.json found, using defaults');
}

const AUDIO_MODE = config.audioMode || 'tts';
const MONITOR = config.monitor || 'primary';

let win;
let currentDisplayIdx = 0;

function getAllDisplays() {
  return screen.getAllDisplays();
}

function getDisplay() {
  const displays = getAllDisplays();
  const primary = screen.getPrimaryDisplay();

  if (MONITOR === 'primary') return primary;
  if (MONITOR === 'secondary') return displays.find(d => d.id !== primary.id) || primary;

  // Monitor by index (0-based)
  const idx = parseInt(MONITOR);
  if (!isNaN(idx) && displays[idx]) return displays[idx];

  // Monitor by position keyword
  if (MONITOR === 'left') return displays.reduce((a, b) => a.bounds.x < b.bounds.x ? a : b);
  if (MONITOR === 'right') return displays.reduce((a, b) => a.bounds.x > b.bounds.x ? a : b);

  return primary;
}

function createWindow() {
  const displays = getAllDisplays();
  const display = getDisplay();
  currentDisplayIdx = Math.max(0, displays.findIndex(d => d.id === display.id));

  win = new BrowserWindow({
    width: display.bounds.width,
    height: display.bounds.height,
    x: display.bounds.x,
    y: display.bounds.y,
    frame: false,
    transparent: true,
    alwaysOnTop: config.alwaysOnTop !== false,
    resizable: false,
    skipTaskbar: false,
    hasShadow: false,
    focusable: true,
    show: false,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  win.once('ready-to-show', () => {
    win.show();
    win.setAlwaysOnTop(true, 'screen-saver');
    win.moveTop();
  });

  // System audio mode: approve only media capture permissions and wire up loopback
  // TTS mode: no media capture needed — lobster polls a local HTTP envelope endpoint only
  if (AUDIO_MODE === 'system') {
    const MEDIA_PERMISSIONS = ['media', 'display-capture', 'audioCapture', 'videoCapture'];
    session.defaultSession.setPermissionRequestHandler((webContents, permission, callback) => {
      callback(MEDIA_PERMISSIONS.includes(permission));
    });

    session.defaultSession.setDisplayMediaRequestHandler((request, callback) => {
      desktopCapturer.getSources({ types: ['screen'] }).then((sources) => {
        callback({ video: sources[0], audio: 'loopback' });
      });
    });
  }

  // Pass config to renderer via URL params
  const params = new URLSearchParams({
    audioMode: AUDIO_MODE,
    ttsUrl: config.ttsUrl || 'http://127.0.0.1:8787',
    ttsEnvelopePath: config.ttsEnvelopePath || '/audio/envelope',
    ttsPollIdleMs: config.ttsPollIdleMs || 500,
    ttsPollActiveMs: config.ttsPollActiveMs || 45,
    ttsPlayStartOffsetMs: config.ttsPlayStartOffsetMs || 1100,
    lobsterScale: config.lobsterScale || 4,
    swimEnabled: config.swimEnabled !== false,
    swimSpeed: config.swimSpeed || 1.0,
  });

  win.loadFile(path.join(__dirname, 'lobster.html'), { query: Object.fromEntries(params) });

  // Click-through: start per config, F9 toggles, IPC from renderer also works
  let clickThrough = config.clickThrough || false;
  win.setIgnoreMouseEvents(clickThrough, { forward: true });

  ipcMain.on('set-click-through', (event, enabled) => {
    if (win) win.setIgnoreMouseEvents(enabled, { forward: true });
  });

  globalShortcut.register('F9', () => {
    clickThrough = !clickThrough;
    if (win) {
      win.setIgnoreMouseEvents(clickThrough, { forward: true });
      console.log('Click-through:', clickThrough);
    }
  });

  // F8 — move the entire window to the next display
  globalShortcut.register('F8', () => {
    if (!win) return;
    const displays = getAllDisplays();
    currentDisplayIdx = (currentDisplayIdx + 1) % displays.length;
    const next = displays[currentDisplayIdx];
    win.setBounds({
      x:      next.bounds.x,
      y:      next.bounds.y,
      width:  next.bounds.width,
      height: next.bounds.height,
    });
    win.setAlwaysOnTop(true, 'screen-saver');
    win.moveTop();
    // Small delay so the window finishes resizing before notifying renderer
    setTimeout(() => {
      if (win) win.webContents.send('display-changed', {});
    }, 150);
  });

  globalShortcut.register('F12', () => {
    if (win) win.webContents.toggleDevTools();
  });

  win.on('closed', () => { win = null; });
}

app.whenReady().then(createWindow);
app.on('window-all-closed', () => app.quit());
