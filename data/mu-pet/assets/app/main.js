const { app, BrowserWindow, screen, ipcMain } = require('electron');
const express = require('express');

let win;
let apiServer;

function startAPI() {
  const api = express();
  api.use(express.json());
  
  api.get('/state', (req, res) => {
    if (win && !win.isDestroyed()) {
      win.webContents.executeJavaScript('window.getState()')
        .then(s => res.json(s))
        .catch(() => res.json({ state: 'unknown' }));
    } else {
      res.json({ state: 'unknown' });
    }
  });
  
  api.post('/state', (req, res) => {
    const { state, status, bubble, duration } = req.body || {};
    if (win && !win.isDestroyed() && state) {
      const text = (bubble || status || '').replace(/"/g, '\\"').replace(/\n/g, ' ');
      const dur = duration || 0;
      win.webContents.executeJavaScript(`window.setState("${state}", "${text}", ${dur})`);
      res.json({ ok: true, state, bubble: text });
    } else {
      res.status(400).json({ error: 'need state' });
    }
  });
  
  apiServer = api.listen(18891, '127.0.0.1', () => {
    console.log('Mu API: http://127.0.0.1:18891');
  });
}

app.whenReady().then(() => {
  const display = screen.getPrimaryDisplay();
  const { width: screenW, height: screenH } = display.workAreaSize;
  
  const WIN_W = 200;
  const WIN_H = 200;
  
  win = new BrowserWindow({
    x: Math.floor(screenW / 2 - WIN_W / 2),
    y: screenH - WIN_H,
    width: WIN_W,
    height: WIN_H,
    transparent: true,
    frame: false,
    alwaysOnTop: true,
    skipTaskbar: true,
    hasShadow: false,
    resizable: false,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    }
  });
  
  win.setIgnoreMouseEvents(true, { forward: true });
  
  ipcMain.on('set-ignore-mouse', (e, ignore) => {
    win.setIgnoreMouseEvents(ignore, { forward: true });
  });
  
  // Move the window around the screen (x, y)
  ipcMain.on('move-window', (e, dx, dy) => {
    const [wx, wy] = win.getPosition();
    let newX = wx + dx;
    let newY = wy + (dy || 0);
    if (newX < -WIN_W/2) newX = -WIN_W/2;
    if (newX > screenW - WIN_W/2) newX = screenW - WIN_W/2;
    if (newY < 0) newY = 0;
    if (newY > screenH - 20) newY = screenH - 20;
    win.setPosition(Math.round(newX), Math.round(newY));
  });
  
  ipcMain.on('get-screen-size', (e) => {
    e.returnValue = { width: screenW, height: screenH };
  });
  
  ipcMain.on('get-position', (e) => {
    const [x, y] = win.getPosition();
    const cursor = screen.getCursorScreenPoint();
    e.returnValue = { x, y, screenW, screenH, cursorX: cursor.x, cursorY: cursor.y };
  });
  
  // Get frontmost window bounds via AppleScript (cached, polled)
  let frontWindowBounds = null;
  const { execSync } = require('child_process');
  
  function updateFrontWindow() {
    try {
      const script = `
        tell application "System Events"
          set fp to first application process whose frontmost is true
          set fn to name of fp
          if fn is "Electron" then return "self"
          tell fp
            set w to first window
            set {x, y} to position of w
            set {ww, wh} to size of w
            return (x as text) & "," & (y as text) & "," & (ww as text) & "," & (wh as text)
          end tell
        end tell`;
      const result = execSync(`osascript -e '${script.replace(/'/g, "'\\''")}'`, { timeout: 1000 }).toString().trim();
      if (result === 'self') {
        frontWindowBounds = null;
      } else {
        const [fx, fy, fw, fh] = result.split(',').map(Number);
        frontWindowBounds = { x: fx, y: fy, w: fw, h: fh };
      }
    } catch (e) {
      frontWindowBounds = null;
    }
  }
  
  setInterval(updateFrontWindow, 2000);
  updateFrontWindow();
  
  ipcMain.on('get-avoidance', (e) => {
    const cursor = screen.getCursorScreenPoint();
    e.returnValue = { cursor, frontWindow: frontWindowBounds };
  });
  
  ipcMain.on('quit-app', () => {
    if (apiServer) apiServer.close();
    app.quit();
  });
  
  win.loadFile('index.html');
  win.setVisibleOnAllWorkspaces(true, { visibleOnFullScreen: true });
  
  startAPI();
});

app.on('window-all-closed', () => {
  if (apiServer) apiServer.close();
  app.quit();
});
