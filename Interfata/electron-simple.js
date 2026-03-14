const { app, BrowserWindow } = require('electron');
const path = require('path');

let mainWindow = null;

console.log('\n--- Electron Start ---');
console.log(`Platform: ${process.platform}`);
console.log(`Electron: ${process.versions.electron}`);
console.log(`Node: ${process.versions.node}`);
console.log('');

function createWindow() {
  console.log('[*] Creating window...');
  
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    show: false,
    icon: path.join(__dirname, 'icon.png'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    }
  });

  console.log('[✓] Window created');

  // Show when ready
  mainWindow.once('ready-to-show', () => {
    console.log('[✓] Ready to show');
    mainWindow.show();
    mainWindow.focus();
  });

  // Track close
  mainWindow.on('closed', () => {
    console.log('[*] Window closed by user');
    mainWindow = null;
  });

  // Track crashes
  mainWindow.webContents.on('crashed', () => {
    console.error('[✗] CRASHED!');
  });

  // Track loading errors
  mainWindow.webContents.on('did-fail-load', (event, code, desc, url) => {
    console.error(`[✗] Failed to load: ${desc} (${code})`);
    console.log('[*] Retiring in 3s...');
    setTimeout(() => {
      if (mainWindow) mainWindow.reload();
    }, 3000);
  });

  const url = 'http://127.0.0.1:8000';
  console.log(`[*] Loading ${url}...`);
  
  mainWindow.loadURL(url).catch((err) => {
    console.error(`[✗] loadURL error: ${err.message}`);
  });
}

app.on('ready', () => {
  console.log('[*] App ready');
});

app.whenReady().then(() => {
  console.log('[*] Creating window...');
  try {
    createWindow();
  } catch (err) {
    console.error(`[✗] Error: ${err.message}`);
    console.error(err.stack);
    process.exit(1);
  }
});

app.on('window-all-closed', () => {
  console.log('[*] All windows closed');
  if (process.platform !== 'darwin') {
    console.log('[*] Staying open (Windows/Linux mode)');
  } else {
    console.log('[*] Quitting (macOS)');
    app.quit();
  }
});

app.on('quit', () => {
  console.log('[*] App quit\n');
});

process.on('uncaughtException', (err) => {
  console.error('[✗] UNCAUGHT:', err.message);
  console.error(err.stack);
});

// Keyboard shortcuts
if (mainWindow) {
  mainWindow.webContents.on('before-input-event', (event, input) => {
    if (input.alt && input.key.toLowerCase() === 'f4') {
      console.log('[*] Alt+F4');
      app.quit();
    }
    if (input.alt && input.key.toLowerCase() === 'd') {
      console.log('[*] Alt+D - DevTools');
      mainWindow.webContents.toggleDevTools();
    }
  });
}
