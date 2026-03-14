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
    const maxAttempts = 120; // ~60 secunde (500ms * 120)
    const check = () => {
      attempts++;
      console.log(`[*] Incerc conectare la server... (${attempts}/${maxAttempts})`);
      
      const req = http.get('http://127.0.0.1:8000/api/status', { timeout: 2000 }, (res) => {
        if (res.statusCode === 200) {
          console.log('✓ Server conectat si responsive');
          res.resume();
          resolve(true);
        } else {
          res.resume();
          if (attempts < maxAttempts) {
            setTimeout(check, 500);
          } else {
            console.warn('⚠ Server nu raspunde dupa 60s, continuu oricum');
            resolve(false);
          }
        }
      }).on('error', (err) => {
        if (attempts < maxAttempts) {
          setTimeout(check, 500);
        } else {
          console.warn('⚠ Server nu disponibil dupa 60s, continuu oricum');
          resolve(false);
        }
      });
    };
    // Incepe verificarea dupa 2 secunde (timp de startup uvicorn)
    setTimeout(check, 2000);
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

  // Error handling pentru incarcarea paginii
  mainWindow.webContents.on('crashed', () => {
    console.error('✗ Renderer crashed - reincerc conectare...');
    setTimeout(() => {
      if (mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.reload();
      }
    }, 2000);
  });

  mainWindow.webContents.on('unresponsive', () => {
    console.warn('⚠ Renderer nu raspunde');
  });

  mainWindow.webContents.on('responsive', () => {
    console.log('✓ Renderer responsive din nou');
  });

  mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription, url) => {
    console.error(`✗ Failed to load: ${errorDescription} (${errorCode})`);
    addAlert = (msg, type) => console.log(`[${type}] ${msg}`);
    dispatch({
      type: 'ALERT_ADD',
      payload: { message: 'Eroare la încărcare', type: 'danger' }
    });
  });

  console.log('✓ Loading URL...');
  mainWindow.loadURL('http://127.0.0.1:8000');
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

// Doar pe macOS inchide app cand toate ferestrele sunt inchise
app.on('window-all-closed', () => {
  console.log('[*] Fereastră închisă');
  // Pe Windows/Linux, aplicația trebuie să rămână deschisă chiar dacă fereastra e închisă
  // Doar pe macOS este convențional să se închidă app-ul
  if (process.platform === 'darwin') {
    console.log('✓ macOS: Aplicația se va închide');
    app.quit();
  } else {
    console.log('[*] Windows/Linux: Menține app deschis (dublu-click pentru ieșire)');
  }
});

app.on('before-quit', () => {
  console.log('[*] Aplicația se inchide - cleanup...');
  try {
    // Nu omor procesele - les lasa sa ruleze in background
    // Pentru viitoare porniri, launch.bat va detecta procesul existent
    console.log('✓ Ressurse curățate');
  } catch (e) {
    console.error('Error during cleanup:', e);
  }
});

process.on('uncaughtException', (err) => {
  console.error('✗ UNCAUGHT EXCEPTION:', err);
  // Nu inchide app pe eroare
});
 