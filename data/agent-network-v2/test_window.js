const { app, BrowserWindow } = require('electron');

app.whenReady().then(() => {
  console.log('Creating window...');
  const win = new BrowserWindow({
    width: 400,
    height: 600,
    webPreferences: { nodeIntegration: false }
  });
  win.loadURL('data:text/html,<h1>Hello Agent Network!</h1>');
  console.log('Window created, id:', win.id);
});

app.on('window-all-closed', () => app.quit());
