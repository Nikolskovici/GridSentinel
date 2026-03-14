const electronModule = require('electron');
const path = require('path');

if (!electronModule || !electronModule.app) {
  console.error('[FATAL] electron module not available');
  console.error('[INFO] This script must be run with: npx electron .');
  console.error('[INFO] Not with: node electron.js');
  process.exit(1);
}

const { app, BrowserWindow } = electronModule;

console.log('[START] Electron app starting');

let mainWindow = null;

function createWindow() {
  console.log('[*] Creating window');
  
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
  
  console.log('[OK] Window created');
  
  mainWindow.on('closed', () => {
    console.log('[*] Window closed');
    mainWindow = null;
  });
  
  mainWindow.webContents.on('did-fail-load', (event, code, desc) => {
    console.log('[WARN] Load failed: ' + desc);
  });
  
  console.log('[*] Loading http://127.0.0.1:8000');
  mainWindow.loadURL('http://127.0.0.1:8000');
  
  mainWindow.once('ready-to-show', () => {
    console.log('[OK] Ready to show - displaying window');
    mainWindow.show();
  });
}

app.whenReady().then(() => {
  console.log('[*] app.whenReady fired');
  createWindow();
});

app.on('window-all-closed', () => {
  console.log('[*] All windows closed');
});

console.log('[END] Script loaded, waiting for app ready...');


 