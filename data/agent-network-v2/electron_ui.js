const { app, BrowserWindow } = require('electron');
const path = require('path');
const fs = require('fs');

app.whenReady().then(() => {
  const win = new BrowserWindow({
    width: 380,
    height: 600,
    webPreferences: { 
      nodeIntegration: false,
      contextIsolation: true 
    }
  });
  
  // 读取 HTML 文件
  const htmlPath = path.join(__dirname, 'ui', 'index.html');
  win.loadFile(htmlPath).then(() => {
    console.log('HTML loaded');
  }).catch(e => console.error('Load error:', e));
});

app.on('window-all-closed', () => app.quit());
