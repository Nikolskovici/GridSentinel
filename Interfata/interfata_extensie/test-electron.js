const { app, BrowserWindow } = require('electron');

app.whenReady().then(() => {
  console.log('READY');
  const w = new BrowserWindow();
  w.loadURL('data:text/html,<h1>Test</h1>');
});

app.on('window-all-closed', () => app.quit());
