// 크래시 방지를 위한 초기 설정 - require 전에 설정
process.env.ELECTRON_DISABLE_SANDBOX = '1';
process.env.ELECTRON_DISABLE_GPU = '1';
process.env.ELECTRON_DISABLE_SECURITY_WARNINGS = 'true';
process.env.NODE_OPTIONS = '--max-old-space-size=4096';

const fs = require('fs');
const { app, BrowserWindow, Menu } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

// 부팅 로그 함수 - 간단하게
function bootLog(msg) {
  const logMsg = `[${new Date().toISOString()}] ${msg}`;
  console.log(logMsg);

  try {
    // 패키지 앱에서는 userData가 없을 수 있으므로 안전하게
    const userDataPath = app.getPath ? app.getPath('userData') : process.env.HOME;
    const logPath = path.join(userDataPath, 'boot.log');
    fs.appendFileSync(logPath, logMsg + '\n');
  } catch (e) {
    // 로그 실패는 무시
  }
}

bootLog('BOOT 0: Starting application');

// 전역 에러 핸들러
process.on('uncaughtException', (error) => {
  bootLog(`UNCAUGHT EXCEPTION: ${error.message}\nStack: ${error.stack}`);
  fs.writeFileSync(path.join(app.getPath('userData'), 'crash.log'),
    `${new Date().toISOString()} UNCAUGHT: ${error.message}\n${error.stack}\n`);
});

process.on('unhandledRejection', (reason, promise) => {
  bootLog(`UNHANDLED REJECTION: ${reason}`);
  fs.writeFileSync(path.join(app.getPath('userData'), 'crash.log'),
    `${new Date().toISOString()} UNHANDLED: ${reason}\n`);
});

bootLog('BOOT 1: Error handlers installed');

// V8 메모리 및 초기화 설정 (크래시 방지)
app.commandLine.appendSwitch('js-flags', '--max-old-space-size=4096 --no-expose-wasm --no-wasm-async-compilation');
app.commandLine.appendSwitch('disable-features', 'CalculateNativeWinOcclusion,WasmStreaming');
app.commandLine.appendSwitch('enable-features', 'SharedArrayBuffer');
bootLog('BOOT 2: Memory and V8 flags configured');

// V8 캐시 비활성화
app.commandLine.appendSwitch('v8-cache-options', 'none');
app.commandLine.appendSwitch('disable-v8-idle-tasks', 'true');
bootLog('BOOT 3: V8 cache and idle tasks disabled');

// GPU 및 렌더링 완전 비활성화 (안정성 향상)
app.disableHardwareAcceleration();
app.commandLine.appendSwitch('disable-gpu');
app.commandLine.appendSwitch('disable-gpu-compositing');
app.commandLine.appendSwitch('disable-software-rasterizer');
app.commandLine.appendSwitch('disable-dev-shm-usage');
app.commandLine.appendSwitch('no-sandbox');
app.commandLine.appendSwitch('disable-setuid-sandbox');
app.commandLine.appendSwitch('disable-gpu-sandbox');
bootLog('BOOT 4: GPU and rendering disabled completely');

let mainWindow;
let pythonProcess;

// Python 서버 시작
function startPythonServer() {
  bootLog('PYTHON 0: Starting Python server function');
  try {
    // 개발 모드와 배포 모드 구분
    const isDev = !app.isPackaged;
    bootLog(`PYTHON 1: isDev=${isDev}, isPackaged=${app.isPackaged}`);

    // 배포 모드에서는 app 폴더 내에서 실행
    const appPath = isDev ? __dirname : path.join(process.resourcesPath, 'app');
    const script = path.join(appPath, 'server.py');
    bootLog(`PYTHON 2: appPath=${appPath}, script=${script}`);

    // Python 가상환경 경로 설정 - Resources 폴더 직접 참조
    const venvPath = isDev ? path.join(appPath, 'venv') : path.join(process.resourcesPath, 'venv');
    const pythonPath = path.join(venvPath, 'bin', 'python');
    bootLog(`PYTHON 3: venvPath=${venvPath}, pythonPath=${pythonPath}`);

    // Python 서버 실행 (가상환경 직접 사용)
    bootLog('PYTHON 4: Spawning Python process');
    pythonProcess = spawn(pythonPath, [script], {
      cwd: appPath,
      stdio: ['ignore', 'pipe', 'pipe'],
      env: {
        ...process.env,
        PYTHONPATH: appPath
      }
    });

    pythonProcess.stdout.on('data', (data) => {
      console.log(`Python Server: ${data}`);
    });

    pythonProcess.stderr.on('data', (data) => {
      console.error(`Python Server Error: ${data}`);
    });

    pythonProcess.on('close', (code) => {
      console.log(`Python server exited with code ${code}`);
    });

    pythonProcess.on('error', (err) => {
      console.error('Failed to start Python server:', err);
      // Python 서버 없이도 앱은 실행되도록 함
    });
  } catch (error) {
    console.error('Error starting Python server:', error);
    // Python 서버 없이도 앱은 실행되도록 함
  }
}

// Electron 윈도우 생성
function createWindow() {
  bootLog('WINDOW 0: Starting createWindow function');
  try {
    bootLog('WINDOW 1: Creating BrowserWindow');
    mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    webPreferences: {
      // 크래시 방지를 위한 설정
      nodeIntegration: false,
      contextIsolation: false, // 크래시 방지를 위해 임시로 false
      webSecurity: false, // 크래시 방지를 위해 임시로 false
      sandbox: false, // 샌드박스 비활성화
      webgl: false, // WebGL 비활성화
      experimentalFeatures: false
    },
    titleBarStyle: 'hiddenInset',
    backgroundColor: '#0f0f0f',
    trafficLightPosition: { x: 20, y: 20 },
    icon: path.join(__dirname, 'assets/icon.png')
  });

  // 메뉴바 설정
  const template = [
    {
      label: '크로노X 스크립트 변환기',
      submenu: [
        {
          label: '크로노X 스크립트 변환기에 대하여',
          click: () => {
            const { dialog } = require('electron');
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: '크로노X 스크립트 변환기',
              message: '크로노X 스크립트 변환기',
              detail: '영상 스크립트 변환기\n유니콘하우스, 크로노엑스 전용 내부프로그램\n\nVersion 1.0.0\n© 2024 ChronoX',
              buttons: ['확인']
            });
          }
        },
        { type: 'separator' },
        {
          label: '크로노X 스크립트 변환기 종료',
          accelerator: 'Cmd+Q',
          click: () => {
            app.quit();
          }
        }
      ]
    },
    {
      label: '편집',
      submenu: [
        { label: '실행 취소', accelerator: 'Cmd+Z', role: 'undo' },
        { label: '다시 실행', accelerator: 'Shift+Cmd+Z', role: 'redo' },
        { type: 'separator' },
        { label: '잘라내기', accelerator: 'Cmd+X', role: 'cut' },
        { label: '복사', accelerator: 'Cmd+C', role: 'copy' },
        { label: '붙여넣기', accelerator: 'Cmd+V', role: 'paste' },
        { label: '모두 선택', accelerator: 'Cmd+A', role: 'selectAll' }
      ]
    },
    {
      label: '보기',
      submenu: [
        { label: '새로고침', accelerator: 'Cmd+R', role: 'reload' },
        { label: '개발자 도구', accelerator: 'Alt+Cmd+I', role: 'toggleDevTools' },
        { type: 'separator' },
        { label: '확대', accelerator: 'Cmd+Plus', role: 'zoomIn' },
        { label: '축소', accelerator: 'Cmd+-', role: 'zoomOut' },
        { label: '실제 크기', accelerator: 'Cmd+0', role: 'resetZoom' }
      ]
    },
    {
      label: '윈도우',
      submenu: [
        { label: '최소화', accelerator: 'Cmd+M', role: 'minimize' },
        { label: '닫기', accelerator: 'Cmd+W', role: 'close' }
      ]
    }
  ];

  bootLog('WINDOW 2: Building menu');
  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
  bootLog('WINDOW 3: Menu set');

  // 서버가 시작될 때까지 잠시 대기 후 로드
  bootLog('WINDOW 4: Setting timeout for HTML load');
  setTimeout(() => {
    try {
      bootLog('WINDOW 5: Loading index.html');
      const isDev = !app.isPackaged;
      const htmlPath = isDev
        ? path.join(__dirname, 'index.html')
        : path.join(process.resourcesPath, 'app', 'index.html');

      bootLog(`WINDOW 6: HTML path=${htmlPath}, exists=${fs.existsSync(htmlPath)}`);

      // loadFile 대신 loadURL 사용 (더 안정적)
      mainWindow.loadURL(`file://${htmlPath}`);
      bootLog('WINDOW 7: index.html loaded');
    } catch (error) {
      bootLog(`WINDOW ERROR loading HTML: ${error.message}`);
      // 폴백 - 단순 HTML 로드
      mainWindow.loadURL('data:text/html,<h1>Loading...</h1>');
    }
  }, 3000);

  mainWindow.on('closed', () => {
    bootLog('WINDOW 8: Window closed');
    mainWindow = null;
  });

  bootLog('WINDOW 9: createWindow completed');
  } catch (error) {
    bootLog(`WINDOW ERROR: ${error.message}\nStack: ${error.stack}`);
    throw error;
  }
}

// 앱 준비 완료
bootLog('BOOT 5: Setting up app.whenReady handler');
app.whenReady().then(() => {
  bootLog('BOOT 6: App is ready');
  try {
    // Python 서버는 나중에 시작 (앱이 먼저 열리도록)
    bootLog('BOOT 7: Calling createWindow');
    createWindow();
    bootLog('BOOT 8: Window created, setting Python server timeout');
    setTimeout(() => {
      bootLog('BOOT 9: Starting Python server');
      startPythonServer();
    }, 1000);
  } catch (error) {
    bootLog(`BOOT ERROR in whenReady: ${error.message}\nStack: ${error.stack}`);
  }
}).catch((error) => {
  bootLog(`BOOT ERROR - whenReady failed: ${error.message}`);
});

// 모든 윈도우가 닫혔을 때
app.on('window-all-closed', () => {
  if (pythonProcess) {
    pythonProcess.kill();
  }
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// 앱 재활성화 (맥)
app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});

// 앱 종료시 Python 서버도 종료
app.on('will-quit', () => {
  if (pythonProcess) {
    pythonProcess.kill();
  }
});