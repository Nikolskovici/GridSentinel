const { app, BrowserWindow } = require('electron');
const path = require('path');
const fs = require('fs');
const http = require('http');
const { spawn, execSync } = require('child_process');

let mainWindow = null;
let serverProcess = null;

function startServer() {
  console.log('[*] Electron nu porneste server - verific doar daca ruleaza deja');
  // Serverul trebuie pornit separat (cu launch.bat sau manual)
  // Electron doar se conecteaza la el
}

function checkServer() {
  return new Promise((resolve) => {
    let attempts = 0;
    const check = () => {
      attempts++;
      const req = http.get('http://127.0.0.1:8000/api/status', { timeout: 1500 }, (res) => {
        if (res.statusCode === 200) {
          console.log('✓ Server conectat');
          res.resume();
          resolve(true);
        } else if (attempts < 60) {
          setTimeout(check, 500);
        } else {
          resolve(false);
        }
      }).on('error', () => {
        if (attempts < 60) {
          setTimeout(check, 500);
        } else {
          resolve(false);
        }
      });
    };
    setTimeout(check, 1000);
  });
}

function createWindow() {
  console.log('✓ Creare fereastră');
  
  mainWindow = new BrowserWindow({
    x: 0,
    y: 0,
    width: 1400,
    height: 900,
    show: true,
    skipTaskbar: false,
    icon: path.join(__dirname, 'icon.png'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    }
  });

  // Asigura ca fereastra e vizibila
  mainWindow.show();
  mainWindow.focus();
  mainWindow.setVisibleOnAllWorkspaces(true);
  mainWindow.setAlwaysOnTop(true);
  setTimeout(() => mainWindow?.setAlwaysOnTop(false), 1000);

  mainWindow.once('ready-to-show', () => {
    console.log('✓ Fereastră visible');
    if (mainWindow) {
      mainWindow.show();
      mainWindow.focus();
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  console.log('✓ Loading URL...');
  mainWindow.loadURL('http://127.0.0.1:8000');
  
  // Apare DevTools daca e eroare
  mainWindow.webContents.on('crashed', () => {
    console.error('✗ Renderer crashed');
  });
}

// Main app flow
app.whenReady().then(async () => {
  console.log('=== GridSentinel Starting ===');
  
  startServer();
  const ok = await checkServer();
  
  // Deschide fereastra indiferent daca serverul e ready
  // WebSocket-ul din browser se va reconecta automat
  console.log(ok ? '✓ Server conectat' : '⚠ Server nu e ready, deschidere in orice caz...');
  createWindow();
});

app.on('window-all-closed', () => {
  console.log('✓ Ferestre închise - Curățare');
  try {
    execSync('taskkill /F /IM python.exe', { stdio: 'ignore' });
  } catch (e) {}
  app.quit();
});

process.on('uncaughtException', (err) => {
  console.error('ERROR:', err);
});
