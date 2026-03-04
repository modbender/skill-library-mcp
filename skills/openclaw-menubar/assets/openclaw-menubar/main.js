const { menubar } = require('menubar');
const path = require('path');
const { app, protocol, BrowserView } = require('electron');
const fs = require('fs');
const os = require('os');

// Create menu bar app
const mb = menubar({
  index: `file://${path.join(__dirname, 'index-webchat.html')}`,
  icon: path.join(__dirname, 'icons', 'icon.png'),
  tooltip: 'CLAW - Quick Chat',
  browserWindow: {
    width: 480,
    height: 680,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      enableRemoteModule: true
    },
    resizable: true,
    movable: true,
    alwaysOnTop: false,
    skipTaskbar: true,
    frame: false,
    transparent: false,
    hasShadow: true,
    vibrancy: 'sidebar',
    visualEffectState: 'active'
  },
  preloadWindow: true,
  showDockIcon: false
});

// Register custom protocol for OAuth callback
if (process.defaultApp) {
  if (process.argv.length >= 2) {
    app.setAsDefaultProtocolClient('openclawmenubar', process.execPath, [path.resolve(process.argv[1])]);
  }
} else {
  app.setAsDefaultProtocolClient('openclawmenubar');
}

// Handle OAuth callback URL
app.on('open-url', (event, url) => {
  event.preventDefault();
  console.log('OAuth callback:', url);
  
  // Extract token from URL
  const match = url.match(/openclawmenubar:\/\/callback\?token=([^&]+)/);
  if (match && mb.window) {
    const token = match[1];
    console.log('Received token:', token);
    
    // Send token to renderer process
    mb.window.webContents.send('oauth-token', token);
    mb.showWindow();
  }
});

mb.on('ready', () => {
  console.log('OpenClaw menu bar app is ready!');
  
  // Global shortcut to show/hide (Cmd+Shift+O)
  const { globalShortcut } = require('electron');
  globalShortcut.register('CommandOrControl+Shift+O', () => {
    if (mb.window.isVisible()) {
      mb.hideWindow();
    } else {
      mb.showWindow();
    }
  });
});

mb.on('after-create-window', () => {
  // Create BrowserView for webchat
  setupWebchatView();
  
  // Open DevTools in development
  if (process.env.NODE_ENV === 'development') {
    mb.window.webContents.openDevTools({ mode: 'detach' });
  }
});

function getGatewayConfig() {
  try {
    const configPath = path.join(os.homedir(), '.openclaw', 'openclaw.json');
    if (fs.existsSync(configPath)) {
      const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
      const port = config.gateway?.port || 18789;
      const token = config.gateway?.auth?.token || config.gateway?.token || '';
      const url = `http://localhost:${port}`;
      
      console.log('Gateway config:', { url, hasToken: !!token, tokenLength: token.length });
      
      return { url, token };
    }
  } catch (error) {
    console.error('Failed to read config:', error);
  }
  return { url: 'http://localhost:18789', token: '' };
}

function setupWebchatView() {
  const view = new BrowserView({
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false
    }
  });
  
  mb.window.setBrowserView(view);
  
  // Set bounds (leave space for header)
  const bounds = mb.window.getContentBounds();
  view.setBounds({ 
    x: 0, 
    y: 50, // Header height
    width: bounds.width, 
    height: bounds.height - 50 
  });
  
  // Auto-resize
  mb.window.on('resize', () => {
    const bounds = mb.window.getContentBounds();
    view.setBounds({ 
      x: 0, 
      y: 50,
      width: bounds.width, 
      height: bounds.height - 50 
    });
  });
  
  // Load webchat with token in URL hash
  const { url: gatewayUrl, token } = getGatewayConfig();
  
  // Build authenticated URL (same format as openclaw dashboard)
  const authenticatedUrl = token 
    ? `${gatewayUrl}/#token=${token}`
    : gatewayUrl;
  
  console.log('Loading webchat from:', authenticatedUrl.replace(token, '***'));
  
  view.webContents.loadURL(authenticatedUrl).catch(err => {
    console.error('Failed to load webchat:', err);
    // Show error in main window
    mb.window.webContents.executeJavaScript(`
      document.body.innerHTML = '<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100vh;color:#e0e0e0;font-family:sans-serif;text-align:center;padding:40px;"><div style="font-size:64px;margin-bottom:20px;">⚠️</div><div style="font-size:18px;font-weight:600;margin-bottom:12px;">OpenClaw Not Running</div><div style="font-size:14px;color:#888;margin-bottom:24px;">Start OpenClaw Gateway to use the menu bar app.</div><button onclick="location.reload()" style="background:linear-gradient(135deg,#667eea,#764ba2);border:none;border-radius:8px;padding:12px 24px;color:white;font-weight:600;cursor:pointer;">Retry</button></div>';
    `);
  });
  
  // Handle navigation
  view.webContents.setWindowOpenHandler(({ url }) => {
    require('electron').shell.openExternal(url);
    return { action: 'deny' };
  });
}

// Quit when all windows are closed
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Clean up on quit
app.on('will-quit', () => {
  const { globalShortcut } = require('electron');
  globalShortcut.unregisterAll();
});
