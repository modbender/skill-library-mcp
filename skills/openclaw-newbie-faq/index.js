const { spawn } = require('child_process');
const path = require('path');
const os = require('os');

const PORT = process.env.OPENCLAW_SKILL_PORT || 34567;
const SKILL_DIR = path.join(os.homedir(), '.openclaw', 'workspace', 'skills', 'openclaw-newbie-faq');

let serverProcess = null;

function log(level, message, meta = {}) {
  console.log(JSON.stringify({
    timestamp: new Date().toISOString(),
    level,
    service: 'openclaw-newbie-faq',
    message,
    ...meta
  }));
}

function startServer() {
  if (serverProcess) {
    log('info', '服务器已在运行');
    return;
  }

  const serverPath = path.join(SKILL_DIR, 'server.js');
  
  serverProcess = spawn('node', [serverPath], {
    env: { ...process.env, OPENCLAW_SKILL_PORT: String(PORT) },
    detached: false,
    stdio: ['ignore', 'pipe', 'pipe']
  });

  serverProcess.stdout.on('data', (data) => {
    log('info', data.toString().trim());
  });

  serverProcess.stderr.on('data', (data) => {
    log('error', data.toString().trim());
  });

  serverProcess.on('error', (err) => {
    log('error', '启动服务器失败', { error: err.message, stack: err.stack });
    serverProcess = null;
  });

  serverProcess.on('exit', (code) => {
    log('info', `服务器退出`, { code });
    serverProcess = null;
  });

  log('info', `服务器已启动`, { pid: serverProcess.pid });
}

function stopServer() {
  if (serverProcess) {
    serverProcess.kill('SIGTERM');
    serverProcess = null;
    log('info', '服务器已停止');
  } else {
    log('info', '服务器未在运行');
  }
}

module.exports = {
  name: 'openclaw-newbie-faq',
  version: '1.0.43',
  displayName: 'openclaw新手帮帮忙',
  description: '为刚接触 OpenCLAW 的新手提供完整指南。安装后请说"启动新手帮助"来启动34567端口的Web服务',
  
  async activate() {
    log('info', '正在启动 OpenClaw 新手帮帮忙...');
    startServer();
    
    return {
      success: true,
      message: `OpenClaw 新手帮帮忙已启动，访问地址: http://localhost:${PORT}`
    };
  },
  
  async deactivate() {
    stopServer();
    
    return {
      success: true,
      message: 'OpenClaw 新手帮帮忙已停止'
    };
  },
  
  getWebUrl() {
    return `http://localhost:${PORT}`;
  }
};

if (require.main === module) {
  startServer();
}
