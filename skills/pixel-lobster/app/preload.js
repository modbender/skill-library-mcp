const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('lobsterAPI', {
  // Config from URL params (passed by main.js at load time)
  getConfig: () => {
    const params = new URLSearchParams(window.location.search);
    return Object.fromEntries(params);
  },

  // IPC: toggle click-through from renderer
  setClickThrough: (enabled) => ipcRenderer.send('set-click-through', enabled),

  // IPC: fired when F8 moves window to next display — re-center the lobster
  onDisplayChanged: (cb) => ipcRenderer.on('display-changed', () => cb()),

  // System audio capture (for audioMode: "system")
  getSources: () => require('electron').desktopCapturer.getSources({
    types: ['screen'],
    thumbnailSize: { width: 0, height: 0 },
  }),

  platform: process.platform,
});
