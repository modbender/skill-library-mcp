const { app, BrowserWindow } = require('electron');

app.whenReady().then(() => {
  const win = new BrowserWindow({ width: 380, height: 600 });
  win.loadURL('https://example.com');
  console.log('Window with URL created');
});

app.onclosed', () =>('window-all- app.quit());
