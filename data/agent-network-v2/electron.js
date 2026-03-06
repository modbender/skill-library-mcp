const { app, BrowserWindow, Tray, Menu, ipcMain, nativeImage, screen } = require('electron');
const path = require('path');
const http = require('http');

let mainWindow = null;
let tray = null;

// Create the main window
function createWindow() {
  const { width, height } = screen.getPrimaryDisplay().workAreaSize;
  
  mainWindow = new BrowserWindow({
    width: 380,
    height: 600,
    x: width - 400,
    y: height - 650,
    frame: true,
    resizable: true,
    skipTaskbar: false,
    alwaysOnTop: true,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });
  
  // Load the renderer
  mainWindow.loadFile(path.join(__dirname, 'ui', 'index.html'));
  
  // Minimize to tray instead of closing
  mainWindow.on('close', (event) => {
    if (!app.isQuitting) {
      event.preventDefault();
      mainWindow.hide();
    }
  });
  
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
  
  console.log('Main window created');
}

// Create system tray
function createTray() {
  const icon = nativeImage.createEmpty();
  
  tray = new Tray(icon.resize({ width: 16, height: 16 }));
  
  const contextMenu = Menu.buildFromTemplate([
    { label: '打开 Agent Network', click: () => mainWindow && mainWindow.show() },
    { label: '状态', click: () => mainWindow && mainWindow.show() },
    { type: 'separator' },
    { label: '退出', click: () => {
      app.isQuitting = true;
      app.quit();
    }}
  ]);
  
  tray.setToolTip('Agent Network');
  tray.setContextMenu(contextMenu);
  
  tray.on('click', () => {
    if (mainWindow) {
      mainWindow.isVisible() ? mainWindow.hide() : mainWindow.show();
    }
  });
  
  console.log('Tray created');
}

// App ready
app.whenReady().then(async () => {
  console.log('Starting Agent Network UI...');
  
  // Just create window and tray - no API server needed
  // The UI will directly connect to port 18794
  createWindow();
  createTray();
  
  console.log('Agent Network UI is ready!');
});

// Handle all windows closed
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

app.on('before-quit', () => {
  app.isQuitting = true;
});
