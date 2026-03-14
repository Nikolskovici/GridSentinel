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
  console.log('\n[>>] Creare fereastră Electron...');
  
  mainWindow = new BrowserWindow({
    x: 0,
    y: 0,
    width: 1400,
    height: 900,
    show: false,
    skipTaskbar: false,
    icon: path.join(__dirname, 'icon.png'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    }
  });

  console.log('[✓] BrowserWindow creat');

  mainWindow.once('ready-to-show', () => {
    console.log('[✓] ready-to-show event');
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.show();
      mainWindow.focus();
      mainWindow.setVisibleOnAllWorkspaces(true);
      mainWindow.setAlwaysOnTop(true);
      setTimeout(() => {
        if (mainWindow && !mainWindow.isDestroyed()) {
          mainWindow.setAlwaysOnTop(false);
        }
      }, 1000);
    }
  });

  mainWindow.on('closed', () => {
    console.log('[*] Fereastră închisă de utilizator');
    mainWindow = null;
  });

  mainWindow.webContents.on('crashed', () => {
    console.error('[✗] Renderer crashed!');
    setTimeout(() => {
      if (mainWindow && !mainWindow.isDestroyed()) {
        console.log('[*] Reîncarcă...');
        mainWindow.reload();
      }
    }, 2000);
  });

  mainWindow.webContents.on('unresponsive', () => {
    console.warn('[⚠] Renderer unresponsive');
  });

  mainWindow.webContents.on('responsive', () => {
    console.log('[✓] Renderer responsive');
  });

  mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription, url) => {
    console.error(`[✗] Failed to load ${url}: ${errorDescription} (${errorCode})`);
    setTimeout(() => {
      if (mainWindow && !mainWindow.isDestroyed()) {
        console.log('[*] Retry încărcare...');
        mainWindow.reload();
      }
    }, 3000);
  });

  mainWindow.webContents.on('before-input-event', (event, input) => {
    if (input.alt && input.key.toLowerCase() === 'f4') {
      console.log('[*] Alt+F4 - quit');
      app.quit();
    }
    if (input.alt && input.key.toLowerCase() === 'd') {
      console.log('[*] Alt+D - DevTools');
      mainWindow.webContents.toggleDevTools();
    }
  });

  console.log('[*] LoadURL: http://127.0.0.1:8000');
  mainWindow.loadURL('http://127.0.0.1:8000').catch((err) => {
    console.error(`[✗] loadURL error: ${err.message}`);
  });
}

// Main app flow
app.on('ready', () => {
  console.log('\n╔════════════════════════════════════════╗');
  console.log('║  GridSentinel Electron Startup       ║');
  console.log('╚════════════════════════════════════════╝\n');
  console.log(`[*] Platform: ${process.platform}`);
  console.log(`[*] Electron: ${process.versions.electron}`);
  console.log(`[*] Node: ${process.versions.node}`);
  console.log(`[*] CWD: ${process.cwd()}\n`);
});

app.whenReady().then(async () => {
  console.log('[*] app.whenReady() triggered');
  
  startServer();
  console.log('[*] Verific server...');
  const ok = await checkServer();
  
  console.log(ok ? '[✓] Server OK' : '[⚠] Server timeout, continuu oricum...');
  console.log('[*] Creare window...');
  
  try {
    createWindow();
    console.log('[✓] Window created');
  } catch (err) {
    console.error(`[✗] createWindow error: ${err.message}`);
    console.error(err.stack);
  }
});

// Doar pe macOS inchide app cand toate ferestrele sunt inchise
app.on('window-all-closed', () => {
  console.log('[*] window-all-closed event');
  if (process.platform === 'darwin') {
    console.log('[✓] macOS: quit');
    app.quit();
  } else {
    console.log('[*] Windows: app stays open (Alt+F4 to quit)');
  }
});

app.on('before-quit', () => {
  console.log('[*] before-quit');
});

app.on('quit', () => {
  console.log('[*] quit event');
});

process.on('uncaughtException', (err) => {
  console.error('[✗] UNCAUGHT:', err.message);
  console.error(err.stack);
});

process.on('unhandledRejection', (reason) => {
  console.error('[✗] REJECTION:', reason);
});
 