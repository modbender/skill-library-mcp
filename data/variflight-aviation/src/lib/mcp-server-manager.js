const { spawn } = require('child_process');
const { EventEmitter } = require('events');

/**
 * MCP 服务器管理器
 * 负责启动 MCP 服务器并提供直接的 stdio 访问
 */
class MCPServerManager extends EventEmitter {
  constructor(options = {}) {
    super();
    this.env = { ...process.env, ...options.env };
    this.timeout = options.timeout || 30000;
    this.process = null;
    this.isReady = false;
    this.startTime = null;
    this.buffer = '';
  }

  /**
   * 启动 MCP 服务器
   */
  async start() {
    if (this.process) {
      return Promise.resolve();
    }

    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        this.kill();
        reject(new Error(`MCP server start timeout (${this.timeout}ms)`));
      }, this.timeout);

      // 使用绝对路径启动 npx
      const npxPath = this.env.NPX_PATH || '/Users/lixiao/.nvm/versions/node/v22.14.0/bin/npx';
      
      this.startTime = Date.now();
      
      // 启动 MCP 服务器进程
      this.process = spawn(npxPath, ['-y', '@variflight-ai/variflight-mcp'], {
        env: this.env,
        stdio: ['pipe', 'pipe', 'pipe']
      });

      let stderrBuffer = '';

      // 处理标准错误
      this.process.stderr.on('data', (data) => {
        const str = data.toString();
        stderrBuffer += str;
        this.emit('stderr', str);
      });

      // 处理标准输出（JSON-RPC 响应）
      this.process.stdout.on('data', (data) => {
        this.buffer += data.toString();
        
        // 检查是否收到初始化响应
        if (!this.isReady) {
          try {
            // 尝试解析 JSON-RPC 响应
            const lines = this.buffer.split('\n').filter(line => line.trim());
            for (const line of lines) {
              const msg = JSON.parse(line);
              if (msg.id === 0 && msg.result) {
                // 收到 initialize 响应，服务器就绪
                this.isReady = true;
                clearTimeout(timeout);
                this.emit('ready', Date.now() - this.startTime);
                resolve();
                break;
              }
            }
          } catch (e) {
            // JSON 解析失败，继续等待
          }
        }
      });

      this.process.on('error', (err) => {
        clearTimeout(timeout);
        reject(new Error(`Failed to start MCP server: ${err.message}`));
      });

      this.process.on('exit', (code, signal) => {
        this.isReady = false;
        const duration = this.startTime ? Date.now() - this.startTime : 0;
        this.process = null;
        this.emit('exit', { code, signal, duration });
        
        if (code !== 0 && code !== null) {
          this.emit('error', new Error(`MCP server exited with code ${code}`));
        }
      });

      // 发送初始化请求
      setTimeout(() => {
        this.sendInitialize();
      }, 500);
    });
  }

  /**
   * 发送 JSON-RPC initialize 请求
   */
  sendInitialize() {
    if (!this.process) return;
    
    const initMessage = {
      jsonrpc: '2.0',
      id: 0,
      method: 'initialize',
      params: {
        protocolVersion: '2024-11-05',
        capabilities: {},
        clientInfo: {
          name: 'variflight-openclaw-skill',
          version: '1.0.0'
        }
      }
    };
    
    this.process.stdin.write(JSON.stringify(initMessage) + '\n');
  }

  /**
   * 发送 JSON-RPC 消息
   */
  send(message) {
    if (!this.process) {
      throw new Error('MCP server not started');
    }
    const json = JSON.stringify(message);
    this.process.stdin.write(json + '\n');
  }

  /**
   * 获取原始 stdio 流（用于 SDK 集成）
   */
  getStreams() {
    if (!this.process) {
      throw new Error('MCP server not started');
    }
    return {
      stdin: this.process.stdin,
      stdout: this.process.stdout,
      stderr: this.process.stderr
    };
  }

  /**
   * 停止 MCP 服务器
   */
  async stop() {
    if (!this.process) {
      return;
    }

    return new Promise((resolve) => {
      const timeout = setTimeout(() => {
        this.kill();
        resolve();
      }, 5000);

      this.process.on('exit', () => {
        clearTimeout(timeout);
        resolve();
      });

      // 发送退出通知
      try {
        const exitMessage = {
          jsonrpc: '2.0',
          method: 'notifications/exit'
        };
        this.process.stdin.write(JSON.stringify(exitMessage) + '\n');
        this.process.stdin.end();
      } catch (e) {
        this.kill();
        resolve();
      }
    });
  }

  /**
   * 强制杀死进程
   */
  kill() {
    if (this.process) {
      try {
        this.process.kill('SIGKILL');
      } catch (e) {
        // 忽略错误
      }
      this.process = null;
      this.isReady = false;
    }
  }

  /**
   * 获取状态
   */
  getStatus() {
    return {
      isRunning: !!this.process,
      isReady: this.isReady,
      pid: this.process ? this.process.pid : null,
      uptime: this.startTime ? Date.now() - this.startTime : 0
    };
  }
}

module.exports = { MCPServerManager };