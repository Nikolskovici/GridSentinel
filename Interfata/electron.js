const { app, BrowserWindow } = require('electron');
const path = require('path');
const http = require('http');

let mainWindow = null;

function checkServer() {
  return new Promise((resolve) => {
    let attempts = 0;
    const maxAttempts = 20;
    
    const check = () => {
      attempts++;
      console.log('[*] Check server attempt ' + attempts + '/' + maxAttempts);
      
      const req = http.get('http://127.0.0.1:8000/api/status', { timeout: 2000 }, (res) => {
        res.resume();
        if (res.statusCode === 200) {
          console.log('[OK] Server responsive');
          resolve(true);
        } else {
          if (attempts < maxAttempts) {
            setTimeout(check, 500);
          } else {
            console.log('[WARN] Server not responding after 10s');
            resolve(false);
          }
        }
      }).on('error', () => {
        if (attempts < maxAttempts) {
          setTimeout(check, 500);
        } else {
          console.log('[WARN] Server unavailable after 10s');
          resolve(false);
        }
      });
    };
    
    setTimeout(check, 500);
  });
}

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

  console.log('[OK] BrowserWindow created');

  mainWindow.once('ready-to-show', () => {
    console.log('[OK] ready-to-show');
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.show();
      mainWindow.focus();
    }
  });

  mainWindow.on('closed', () => {
    console.log('[*] Window closed');
    mainWindow = null;
  });

  mainWindow.webContents.on('crashed', () => {
    console.error('[ERROR] Renderer crashed');
  });

  mainWindow.webContents.on('did-fail-load', (event, code, desc) => {
    console.error('[ERROR] did-fail-load code=' + code + ' desc=' + desc);
  });

  mainWindow.webContents.on('before-input-event', (event, input) => {
    if (input.alt && input.key === 'F4') {
      app.quit();
    }
  });

  const url = 'http://127.0.0.1:8000';
  console.log('[*] Loading ' + url);
  
  mainWindow.loadURL(url).catch((err) => {
    console.error('[ERROR] loadURL: ' + err.message);
  });
}

console.log('\n========================================');
console.log('GridSentinel Electron Starting');
console.log('========================================\n');

app.on('ready', () => {
  console.log('[*] App ready event');
});

app.whenReady().then(async () => {
  console.log('[*] app.whenReady');
  console.log('[*] Checking server...');
  
  const serverOk = await checkServer();
  console.log(serverOk ? '[OK] Server OK' : '[WARN] Server not ready');
  
  try {
    createWindow();
    console.log('[OK] Window created successfully\n');
  } catch (err) {
    console.error('[ERROR] createWindow failed: ' + err.message);
    console.error(err.stack);
    process.exit(1);
  }
});

app.on('window-all-closed', () => {
  console.log('[*] window-all-closed');
  if (process.platform !== 'darwin') {
    console.log('[*] Staying open (Windows)');
  } else {
    app.quit();
  }
});

app.on('quit', () => {
  console.log('[*] App quit\n');
});

process.on('uncaughtException', (err) => {
  console.error('[ERROR] Uncaught: ' + err.message);
  console.error(err.stack);
});

 